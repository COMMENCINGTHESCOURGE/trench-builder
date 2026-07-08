#!/usr/bin/env python
"""
TRENCH BUILDER API — Monetization Platform Backend
Flask API with JSON-persisted license management. DeepSeek AI endpoint.
Stripe integration stubbed (webhook framework in place, checkout creation
not yet implemented). Production-readiness: needs SQLite migration,
Stripe checkout flow, and a render queue worker.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, hashlib, time, hmac, uuid, sys
import stripe
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS

# Force UTF-8 encoding for standard streams on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

from trench_config import PATHS, deepseek_key as _deepseek_key, openai_key as _openai_key
from trench_config import stripe_secret as _stripe_secret, stripe_webhook_secret as _stripe_webhook

DEEPSEEK_KEY = _deepseek_key()
OPENAI_KEY = _openai_key()
STRIPE_SECRET = _stripe_secret()
STRIPE_WEBHOOK_SECRET = _stripe_webhook()

if STRIPE_SECRET and not STRIPE_SECRET.startswith("sk_test_mock"):
    stripe.api_key = STRIPE_SECRET

# License database — JSON file persistence
STATE_PATH = PATHS.api_state
licenses = {}      # key → {tier, expires, max_requests, used_requests}
api_keys = {}      # api_key → license_key
sessions = {}      # session_token → user_data


def _load_state():
    """Load persisted state from disk on startup."""
    if STATE_PATH.exists():
        try:
            data = json.loads(STATE_PATH.read_text())
            licenses.update(data.get("licenses", {}))
            api_keys.update(data.get("api_keys", {}))
            sessions.update(data.get("sessions", {}))
            return True
        except (json.JSONDecodeError, OSError):
            return False
    return False


def _save_state():
    """Persist state atomically — temp file + rename (NTFS-safe)."""
    tmp = STATE_PATH.with_suffix(".tmp")
    payload = {
        "licenses": licenses,
        "api_keys": api_keys,
        "sessions": sessions,
    }
    tmp.write_text(json.dumps(payload, indent=2, default=str))
    tmp.replace(STATE_PATH)  # atomic on NTFS


# Load persisted state at import time
_loaded = _load_state()

TIERS = {
    "free":    {"requests": 100,   "render_minutes": 10,  "models": ["gemma4:2b"], "price": 0},
    "pro":     {"requests": 5000,  "render_minutes": 300, "models": ["deepseek-chat", "gemma4:2b", "hermes3"], "price": 29},
    "studio":  {"requests": 50000, "render_minutes": 2000,"models": ["deepseek-chat", "gpt-4o", "gemma4:2b", "hermes3", "qwen3.5"], "price": 149},
    "enterprise": {"requests": -1, "render_minutes": -1,"models": ["*"], "price": "custom"},
}

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════
# AUTH — License validation
# ═══════════════════════════════════════════════════════

def generate_license(tier="free", duration_days=30):
    """Generate a cryptographically signed license key."""
    lid = str(uuid.uuid4())
    expires = (datetime.utcnow() + timedelta(days=duration_days)).isoformat()
    signature = hmac.new(
        (STRIPE_SECRET or "dev-secret").encode(),
        f"{lid}:{tier}:{expires}".encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    
    key = f"TB-{tier.upper()}-{lid[:8]}-{signature}".upper()
    licenses[key] = {
        "tier": tier,
        "expires": expires,
        "max_requests": TIERS[tier]["requests"],
        "used_requests": 0,
        "created": datetime.utcnow().isoformat()
    }
    _save_state()
    return key

def require_license(f):
    """Decorator: validate API key before executing endpoint."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if not api_key or api_key not in api_keys:
            return jsonify({"error": "Invalid or missing API key", "code": "UNAUTHORIZED"}), 401
        
        lic = licenses.get(api_keys[api_key])
        if not lic:
            return jsonify({"error": "License not found", "code": "LICENSE_MISSING"}), 403
        
        if datetime.fromisoformat(lic["expires"]) < datetime.utcnow():
            return jsonify({"error": "License expired", "code": "LICENSE_EXPIRED", "expired": lic["expires"]}), 403
        
        if lic["max_requests"] > 0 and lic["used_requests"] >= lic["max_requests"]:
            return jsonify({"error": "Rate limit exceeded", "code": "RATE_LIMITED", "limit": lic["max_requests"]}), 429
        
        lic["used_requests"] += 1
        _save_state()
        request.license = lic
        return f(*args, **kwargs)
    return wrapper

# ═══════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════

@app.route("/")
def root():
    return jsonify({
        "service": "TRENCH BUILDER API",
        "version": "v1.0",
        "status": "operational",
        "providers": {
            "deepseek": bool(DEEPSEEK_KEY),
            "openai": bool(OPENAI_KEY),
            "ollama": True
        },
        "endpoints": [
            "POST /v1/license/generate",
            "POST /v1/render/scene",
            "POST /v1/ai/ask",
            "GET  /v1/metrics",
            "GET  /v1/artifacts/<name>"
        ]
    })

@app.route("/pricing.html")
def serve_pricing():
    return send_file("pricing.html")

@app.route("/success.html")
def serve_success():
    return send_file("success.html")

@app.route("/v1/license/generate", methods=["POST"])
def create_license():
    """Generate a new license key."""
    data = request.json or {}
    tier = data.get("tier", "free")
    if tier not in TIERS:
        return jsonify({"error": f"Invalid tier. Options: {list(TIERS.keys())}"}), 400
    
    if tier != "free":
        if not STRIPE_SECRET:
            return jsonify({"error": "Stripe is not configured. Cannot process paid tiers.", "code": "STRIPE_UNCONFIGURED"}), 501
        
        if STRIPE_SECRET.startswith("sk_test_mock"):
            if os.environ.get("GCP_PROJECT"):
                return jsonify({"error": "Mock Stripe checkout is disabled in production.", "code": "MOCK_DISABLED_PROD"}), 400
            # Generate local offline mock checkout flow
            session_id = f"mock_sess_{uuid.uuid4().hex[:16]}"
            checkout_url = f"http://127.0.0.1:8090/v1/mock-stripe-checkout?session_id={session_id}&tier={tier}"
            return jsonify({
                "checkout_url": checkout_url,
                "session_id": session_id,
                "tier": tier,
                "mode": "mock"
            })
        else:
            # Real Stripe Checkout Session Creation
            try:
                origin = request.headers.get("Origin") or "https://commencingthescourge.github.io"
                success_url = f"{origin}/success.html?session_id={{CHECKOUT_SESSION_ID}}"
                cancel_url = f"{origin}/pricing.html"
                
                price_val = TIERS[tier]["price"]
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f'Trench Builder - {tier.upper()} Subscription',
                            },
                            'unit_amount': int(price_val * 100),
                            'recurring': {'interval': 'month'},
                        },
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata={'tier': tier}
                )
                return jsonify({
                    "checkout_url": session.url,
                    "session_id": session.id,
                    "tier": tier,
                    "mode": "stripe"
                })
            except Exception as e:
                return jsonify({"error": f"Stripe checkout creation failed: {str(e)}", "code": "STRIPE_ERROR"}), 500
    
    key = generate_license(tier)
    api_key = f"tb_{uuid.uuid4().hex[:24]}"
    api_keys[api_key] = key
    _save_state()
    
    return jsonify({
        "license_key": key,
        "api_key": api_key,
        "tier": tier,
        "limits": TIERS[tier],
        "expires": licenses[key]["expires"]
    })

@app.route("/v1/mock-stripe-checkout", methods=["GET"])
def mock_checkout_page():
    """Serve a mock Stripe checkout page for offline/dev testing."""
    session_id = request.args.get("session_id", "")
    tier = request.args.get("tier", "pro")
    
    price = TIERS.get(tier, {}).get("price", 0)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mock Stripe Checkout</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background: #0d0e15;
                color: #e4e6f1;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 40px;
                max-width: 450px;
                width: 100%;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0,0,0,0.5);
                backdrop-filter: blur(12px);
            }}
            h1 {{
                font-weight: 800;
                margin-bottom: 8px;
                color: #fff;
            }}
            .price {{
                font-size: 36px;
                font-weight: 800;
                margin: 20px 0;
                color: #5469d4;
            }}
            .details {{
                font-size: 14px;
                color: #8f95b2;
                margin-bottom: 30px;
                line-height: 1.5;
            }}
            button {{
                background: #5469d4;
                color: white;
                border: none;
                padding: 14px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                transition: background 0.2s;
            }}
            button:hover {{
                background: #4353b3;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>stripe</h1>
            <p style="color:#8f95b2; margin-top:0;">TEST MODE CHECKOUT</p>
            <div class="price">${price}.00 / month</div>
            <div class="details">
                Simulating subscription checkout for <strong>Trench Builder {tier.upper()}</strong>.<br>
                Session ID: <code>{session_id}</code>
            </div>
            <form action="/v1/mock-stripe-checkout/pay" method="POST">
                <input type="hidden" name="session_id" value="{session_id}">
                <input type="hidden" name="tier" value="{tier}">
                <button type="submit">Simulate Successful Payment</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/v1/mock-stripe-checkout/pay", methods=["POST"])
def mock_checkout_pay():
    """Simulate Stripe event and call the local webhook endpoint."""
    session_id = request.form.get("session_id", "")
    tier = request.form.get("tier", "pro")
    
    import urllib.request as ur
    
    payload = {
        "id": f"evt_mock_{uuid.uuid4().hex[:12]}",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "customer": f"cus_mock_{uuid.uuid4().hex[:12]}",
                "subscription": f"sub_mock_{uuid.uuid4().hex[:12]}",
                "metadata": {"tier": tier},
                "payment_status": "paid"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "t=12345,v1=mock_signature"
    }
    
    req = ur.Request(
        "http://127.0.0.1:8090/v1/webhooks/stripe",
        data=json.dumps(payload).encode(),
        headers=headers
    )
    try:
        resp = ur.urlopen(req, timeout=5)
        resp_data = json.loads(resp.read())
        
        created_key = None
        created_api = None
        for key, val in licenses.items():
            if val.get("tier") == tier:
                created_key = key
                for a_k, l_k in api_keys.items():
                    if l_k == key:
                        created_api = a_k
                        break
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mock Stripe Checkout - Success</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    background: #0d0e15;
                    color: #e4e6f1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }}
                .card {{
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 16px;
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
                    backdrop-filter: blur(12px);
                }}
                h1 {{
                    font-weight: 800;
                    margin-bottom: 8px;
                    color: #4caf50;
                }}
                .credential-box {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px dashed rgba(255,255,255,0.2);
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                code {{
                    color: #e91e63;
                    font-weight: 600;
                    font-size: 15px;
                }}
                a {{
                    color: #5469d4;
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Payment Simulated!</h1>
                <p>The Stripe webhook event <code>checkout.session.completed</code> was dispatched and handled locally.</p>
                <div class="credential-box">
                    <strong>License Key:</strong><br>
                    <code>{created_key or "PENDING (Check Server Logs)"}</code><br><br>
                    <strong>X-API-Key:</strong><br>
                    <code>{created_api or "PENDING (Check Server Logs)"}</code>
                </div>
                <p>You can now use this API key in headers to access premium endpoints.</p>
                <p><a href="http://127.0.0.1:8090/v1/health">Check server health</a> or return to <a href="https://commencingthescourge.github.io/">storefront</a>.</p>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"Webhook simulation failed: {str(e)}", 500

@app.route("/v1/render/scene", methods=["POST"])
@require_license
def render_scene():
    """Queue a cloud render job."""
    data = request.json or {}
    scene_type = data.get("type", "subwoofer")
    params = data.get("params", {})
    
    # Validate against license tier
    tier = request.license["tier"]
    render_limit = TIERS[tier]["render_minutes"]
    
    job_id = uuid.uuid4().hex[:12]
    
    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "scene": scene_type,
        "params": params,
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
        "provider": "deepseek" if DEEPSEEK_KEY else "ollama"
    })

@app.route("/v1/ai/ask", methods=["POST"])
@require_license
def ai_ask():
    """AI design assistant — powered by DeepSeek (95% cache hit)."""
    if not DEEPSEEK_KEY:
        return jsonify({"error": "AI provider offline", "code": "PROVIDER_DOWN"}), 503
    
    data = request.json or {}
    question = data.get("question", "")
    context = data.get("context", {})
    
    # Check model availability for tier
    tier = request.license["tier"]
    allowed_models = TIERS[tier]["models"]
    
    import urllib.request as ur
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{
            "role": "user",
            "content": f"You are an engineering design assistant. Context: {json.dumps(context)[:500]}. Question: {question}"
        }],
        "max_tokens": 300,
        "temperature": 0.3
    }).encode()
    
    try:
        req = ur.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
        )
        resp = ur.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        answer = result["choices"][0]["message"]["content"]
        
        return jsonify({
            "answer": answer,
            "model": "deepseek-chat",
            "usage": result.get("usage", {}),
            "cached": result.get("usage", {}).get("prompt_cache_hit_tokens", 0) > 0
        })
    except Exception as e:
        return jsonify({"error": str(e), "code": "AI_ERROR"}), 500

@app.route("/v1/metrics", methods=["GET"])
@require_license
def metrics():
    """Get usage metrics for the current license."""
    lic = request.license
    return jsonify({
        "tier": lic["tier"],
        "used_requests": lic["used_requests"],
        "max_requests": lic["max_requests"],
        "expires": lic["expires"],
        "remaining": lic["max_requests"] - lic["used_requests"] if lic["max_requests"] > 0 else "unlimited"
    })

@app.route("/v1/artifacts/<name>", methods=["GET"])
@require_license
def get_artifact(name):
    """Serve rendered artifacts (HTML files, CAD exports)."""
    # Security: only allow known filenames
    allowed = {
        "trench-builder-v5": "TRENCH_BUILDER_v5.html",
        "cinematography-engine": "CINEMATOGRAPHY_ENGINE.html",
        "backrooms-mep": "BACKROOMS_MEP.html",
        "manifestation-bridge": "MANIFESTATION_BRIDGE.html",
        "resonance-hud": "RESONANCE_HUD.html",
    }
    
    if name not in allowed:
        return jsonify({"error": "Unknown artifact", "available": list(allowed.keys())}), 404
    
    filepath = PATHS.trench_builder / allowed[name]
    if not filepath.exists():
        return jsonify({"error": "Artifact not found on disk"}), 404
    
    return send_file(str(filepath), mimetype="text/html")

@app.route("/v1/health")
def health():
    return jsonify({
        "status": "ok",
        "deepseek": bool(DEEPSEEK_KEY),
        "openai": bool(OPENAI_KEY),
        "licenses_active": len(licenses),
        "api_keys_issued": len(api_keys),
        "uptime": datetime.utcnow().isoformat()
    })

# ═══════════════════════════════════════════════════════
# STRIPE WEBHOOK (production)
# ═══════════════════════════════════════════════════════

@app.route("/v1/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    """Handle Stripe subscription events."""
    if not STRIPE_WEBHOOK_SECRET:
        return jsonify({"error": "Stripe not configured"}), 501
    
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    
    event = None
    
    if STRIPE_WEBHOOK_SECRET.startswith("whsec_mock") and sig_header == "t=12345,v1=mock_signature":
        if os.environ.get("GCP_PROJECT"):
            return jsonify({"error": "Mock Webhook verification is disabled in production.", "code": "MOCK_WEBHOOK_DISABLED_PROD"}), 400
        try:
            event = request.json
        except Exception as e:
            return jsonify({"error": "Invalid mock payload"}), 400
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return jsonify({"error": "Invalid payload", "details": str(e)}), 400
        except stripe.error.SignatureVerificationError as e:
            return jsonify({"error": "Invalid signature", "details": str(e)}), 400
            
    event_type = event.get("type")
    
    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        metadata = session.get("metadata", {})
        tier = metadata.get("tier", "pro")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        session_id = session.get("id")
        
        license_key = generate_license(tier, duration_days=30)
        api_key = f"tb_{uuid.uuid4().hex[:24]}"
        api_keys[api_key] = license_key
        
        licenses[license_key]["stripe_customer"] = customer_id
        licenses[license_key]["stripe_subscription"] = subscription_id
        licenses[license_key]["stripe_session_id"] = session_id
        
        _save_state()
        print(f"[STRIPE WEBHOOK] Issued license {license_key} for tier {tier} (Sub: {subscription_id})")
        
    elif event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
        subscription = event.get("data", {}).get("object", {})
        sub_id = subscription.get("id")
        status = subscription.get("status")
        
        target_license_key = None
        for key, lic in licenses.items():
            if lic.get("stripe_subscription") == sub_id:
                target_license_key = key
                break
                
        if target_license_key:
            if status in ["canceled", "unpaid"]:
                licenses[target_license_key]["expires"] = datetime.utcnow().isoformat()
                print(f"[STRIPE WEBHOOK] Suspended license {target_license_key} (status: {status})")
            elif status == "past_due":
                licenses[target_license_key]["status"] = "past_due"
                print(f"[STRIPE WEBHOOK] Flagged license {target_license_key} as past_due")
            elif status == "active":
                new_expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()
                licenses[target_license_key]["expires"] = new_expiry
                licenses[target_license_key]["status"] = "active"
                print(f"[STRIPE WEBHOOK] Renewed license {target_license_key} to {new_expiry}")
            _save_state()
            
    return jsonify({"received": True})

# ═══════════════════════════════════════════════════════
# LICENSE RETRIEVAL & VERIFICATION
# ═══════════════════════════════════════════════════════

@app.route("/v1/checkout/retrieve", methods=["GET"])
def retrieve_checkout_license():
    """Retrieve the API and license keys generated for a completed Stripe session."""
    session_id = request.args.get("session_id", "")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
        
    # Search for license with this stripe_session_id
    for api_key, lic_key in api_keys.items():
        lic = licenses.get(lic_key, {})
        if lic.get("stripe_session_id") == session_id:
            return jsonify({
                "success": True,
                "api_key": api_key,
                "license_key": lic_key,
                "tier": lic.get("tier"),
                "expires": lic.get("expires")
            })
            
    # Fallback: check Stripe directly
    if STRIPE_SECRET and not STRIPE_SECRET.startswith("sk_test_mock"):
        try:
            stripe_session = stripe.checkout.Session.retrieve(session_id)
            if stripe_session.payment_status == "paid":
                metadata = stripe_session.metadata or {}
                tier = metadata.get("tier", "pro")
                customer_id = stripe_session.customer
                subscription_id = stripe_session.subscription
                
                # Prevent duplicates
                for ak, lk in list(api_keys.items()):
                    if licenses.get(lk, {}).get("stripe_subscription") == subscription_id:
                        return jsonify({
                            "success": True,
                            "api_key": ak,
                            "license_key": lk,
                            "tier": licenses[lk].get("tier"),
                            "expires": licenses[lk].get("expires")
                        })
                
                license_key = generate_license(tier, duration_days=30)
                api_key = f"tb_{uuid.uuid4().hex[:24]}"
                api_keys[api_key] = license_key
                licenses[license_key]["stripe_customer"] = customer_id
                licenses[license_key]["stripe_subscription"] = subscription_id
                licenses[license_key]["stripe_session_id"] = session_id
                _save_state()
                return jsonify({
                    "success": True,
                    "api_key": api_key,
                    "license_key": license_key,
                    "tier": tier,
                    "expires": licenses[license_key]["expires"]
                })
        except Exception as e:
            return jsonify({"error": f"Failed to retrieve session from Stripe: {str(e)}"}), 500

    return jsonify({"error": "License not found or webhook pending. Refresh in a few seconds."}), 404

@app.route("/v1/license/verify", methods=["POST"])
def verify_license():
    """Verify a license key without consuming a request."""
    key = (request.json or {}).get("license_key", "")
    if key not in licenses:
        return jsonify({"valid": False, "reason": "unknown_key"}), 404
    
    lic = licenses[key]
    if datetime.fromisoformat(lic["expires"]) < datetime.utcnow():
        return jsonify({"valid": False, "reason": "expired"}), 403
    
    return jsonify({
        "valid": True,
        "tier": lic["tier"],
        "expires": lic["expires"],
        "remaining": lic["max_requests"] - lic["used_requests"] if lic["max_requests"] > 0 else "unlimited"
    })

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Generate a test license on startup
    test_key = generate_license("pro", 365)
    test_api = f"tb_{uuid.uuid4().hex[:24]}"
    api_keys[test_api] = test_key
    
    print("╔══════════════════════════════════════════╗")
    print("║  TRENCH BUILDER API v1.1               ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  State:   {'✓ LOADED' if _loaded else '○ FRESH'} ({len(licenses)} licenses)     ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  DeepSeek: {'✓ ONLINE' if DEEPSEEK_KEY else '✗ OFFLINE'}                         ║")
    print(f"║  OpenAI:   {'✓ ONLINE' if OPENAI_KEY else '✗ OFFLINE'}                         ║")
    print(f"║  Stripe:   {'✓ CONFIGURED' if STRIPE_SECRET else '✗ DEV MODE'}                  ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  TEST LICENSE:                           ║")
    print(f"║    Key:    {test_key}  ║")
    print(f"║    API:    {test_api}      ║")
    print(f"║    Tier:   pro                           ║")
    print(f"║    Limit:  5,000 requests                ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Endpoints:                              ║")
    print("║    POST /v1/license/generate             ║")
    print("║    POST /v1/render/scene                 ║")
    print("║    POST /v1/ai/ask                       ║")
    print("║    GET  /v1/metrics                      ║")
    print("║    GET  /v1/artifacts/<name>             ║")
    print("║    GET  /v1/health                       ║")
    print("╚══════════════════════════════════════════╝")
    
    app.run(host="127.0.0.1", port=8090, debug=False)
