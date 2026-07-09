import os
import time
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe

from .spanner_client import SpannerClient

stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_mock")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")

app = FastAPI(title="Trench-Builder Tollbooth API", version="1.0.0")
db = SpannerClient()

class ComputeRequest(BaseModel):
    x: float
    z: float
    channels: list[str]

@app.post("/v1/gumroad/validate")
def validate_gumroad(license_key: str):
    """Validate a Gumroad customer license key in Spanner."""
    license_data = db.get_license(license_key)
    if not license_data or license_data["LicenseType"] != "sdk_download":
        raise HTTPException(status_code=403, detail="Invalid Gumroad license key.")
    
    # Log telemetry event
    db.log_telemetry("gumroad_license_validated", {"license_key": license_key})
    return {"status": "valid", "license_type": "sdk_download"}

@app.post("/v1/compute/tensor")
def compute_tensor(request: ComputeRequest, x_api_key: str = Header(...)):
    """Primary spatial compute endpoint gating calculations behind valid subscriptions."""
    license_data = db.get_license(x_api_key)
    if not license_data or license_data["Status"] != "active":
        raise HTTPException(status_code=403, detail="Unauthorized API key.")

    # Check metered usage limits
    if license_data["MaxRequests"] and license_data["AccumulatedRequests"] >= license_data["MaxRequests"]:
        raise HTTPException(status_code=429, detail="Usage limit exceeded for this billing period.")

    start_time = time.time()

    # Core logic mock - generates mock 6-channel material tensor footprint
    tensor_data = {
        "density": 1.0,
        "cohesion": 0.8,
        "velocity": [0.0, -1.0, 0.0],
        "moisture": 0.35,
        "heat": 20.0,
        "friction": 0.4
    }

    # Increment request tally atomically
    db.increment_usage(x_api_key)

    # Log telemetry event dynamically matching AGENTS.md rules
    latency = time.time() - start_time
    db.log_telemetry("compute_tensor_executed", {
        "license_key": x_api_key,
        "latency_sec": latency,
        "coords": [request.x, request.z]
    })

    return {"status": "success", "tensor": tensor_data}

@app.post("/v1/stripe/webhook")
async def stripe_webhook(request: Request):
    """Stripe webhook handling customer creation and subscription syncs."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Generate or cancel API keys based on payments
    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        new_key = f"trench_pro_{customer_id[-8:]}"
        # Provisions dynamic metered key mapping in Spanner
        db.create_license(new_key, "metered_api", max_requests=100000)
        db.log_telemetry("stripe_subscription_created", {"customer_id": customer_id, "key": new_key})

    return JSONResponse(content={"status": "success"})
