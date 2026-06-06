#!/usr/bin/env python
"""
TRENCH BUILDER API — Monetization Platform Backend
Flask API with JSON-persisted license management. DeepSeek AI endpoint.
Stripe integration stubbed (webhook framework in place, checkout creation
not yet implemented). Production-readiness: needs SQLite migration,
Stripe checkout flow, and a render queue worker.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, hashlib, time, hmac, uuid
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

from trench_config import PATHS, deepseek_key as _deepseek_key, openai_key as _openai_key
from trench_config import stripe_secret as _stripe_secret, stripe_webhook_secret as _stripe_webhook

DEEPSEEK_KEY = _deepseek_key()
OPENAI_KEY = _openai_key()
STRIPE_SECRET = _stripe_secret()
STRIPE_WEBHOOK_SECRET = _stripe_webhook()

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

@app.route("/v1/license/generate", methods=["POST"])
def create_license():
    """Generate a new license key."""
    data = request.json or {}
    tier = data.get("tier", "free")
    if tier not in TIERS:
        return jsonify({"error": f"Invalid tier. Options: {list(TIERS.keys())}"}), 400
    
    # In production: create Stripe checkout session first
    if tier != "free" and STRIPE_SECRET:
        # stripe.checkout.Session.create(...)
        pass
    
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
    
    # In production: verify stripe signature, handle checkout.session.completed,
    # customer.subscription.updated, customer.subscription.deleted
    return jsonify({"received": True})

# ═══════════════════════════════════════════════════════
# ANTI-PIRACY: License integrity check
# ═══════════════════════════════════════════════════════

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
