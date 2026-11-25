---
name: stripe-subscriptions
description: >-
  Use when architecting Stripe billing integrations, handling webhook signatures,
  managing customer checkout sessions, preventing duplicate charges with idempotency
  keys, or configuring portal redirects.
---

# Stripe Subscriptions & Webhook Processing Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Implementing Stripe Checkout sessions for subscriptions or one-time payments.
- Verifying raw Stripe webhook signatures (`stripe.Webhook.construct_event`) to block spoofed events.
- Preventing duplicate transactions using Stripe **Idempotency Keys** (`Idempotency-Key: <UUID>`).
- Synchronizing subscription statuses (`active`, `past_due`, `canceled`) with MongoDB/PostgreSQL.
- Handling checkout cancellation, payment failure retries, and billing portal session generation.

---

## 2. Hard Architectural Rules

1. **Verify Raw Request Bodies Only**:
   Never parse request bodies into JSON before verifying Stripe webhook signatures. Stripe signature verification computes HMAC-SHA256 hashes against the **exact raw binary bytes**. Parsing JSON alters whitespace, causing signature verification to fail (`SignatureVerificationError`).

2. **Always Use Idempotency Keys on Mutations**:
   On every charge, subscription creation, or refund request, always send an `idempotency_key` (e.g. `uuid4()`). If network drops occur, retrying with the same key guarantees the customer is never charged twice.

3. **Handle Webhook Concurrency & Out-of-Order Delivery**:
   Stripe does not guarantee in-order delivery of webhooks (`customer.subscription.updated` might arrive before `customer.subscription.created`). Always check database event timestamps before updating subscription state.

4. **Sanitized Stripe Secrets**:
   Never hardcode `sk_live_...` or `whsec_...` secrets in source code. Inject via `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` environment variables.

---

## 3. Production Code Patterns

### Pattern A: Master Stripe Webhook Handler (FastAPI)
```python
import os
import stripe
from fastapi import FastAPI, Request, HTTPException, Header, status

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/api/v1/stripe/webhook", status_code=status.HTTP_200_OK)
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    # Read raw bytes directly
    raw_payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=raw_payload,
            sig_header=stripe_signature,
            secret=WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        customer_id = data_object.get("customer")
        subscription_id = data_object.get("subscription")
        print(f" Payment verified for customer {customer_id}, subscription: {subscription_id}")
    elif event_type == "customer.subscription.deleted":
        print(f" Subscription canceled for customer {data_object.get('customer')}")

    return {"status": "success"}
```

---

## 4. Verification Command
Test webhook signing verification locally via Stripe CLI:
```bash
stripe listen --forward-to localhost:5000/api/v1/stripe/webhook
```
