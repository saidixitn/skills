#!/usr/bin/env python3
"""
Dynamic CI Step Runner & Skill Synthesizer for GitHub Actions
When triggered, pops the next pending skill from skills_queue.json,
authors the complete SKILL.md and helper assets, runs zero-leak audits,
updates README.md, and marks completed so GitHub Actions commits and pushes it live.
"""

import os
import sys
import json
import subprocess

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_FILE = os.path.join(BASE_DIR, "scripts", "skills_queue.json")
AUDIT_SCRIPT = os.path.join(BASE_DIR, "scripts", "audit_secrets.py")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
README_PATH = os.path.join(BASE_DIR, "README.md")

# Built-in generator templates for next-gen developer skills
SKILL_TEMPLATES = {
    "stripe-subscriptions": {
        "category": "Payments",
        "description": "Use when architecting Stripe billing integrations, handling webhook signatures, managing customer checkout sessions, preventing duplicate charges with idempotency keys, or configuring portal redirects.",
        "content": """---
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
"""
    },
    "redis-caching": {
        "category": "Backend",
        "description": "Use when engineering sub-millisecond Redis or Upstash caching layers, implementing token bucket rate-limiters, managing session stores, or setting cache invalidation TTL policies.",
        "content": """---
name: redis-caching
description: >-
  Use when engineering sub-millisecond Redis or Upstash caching layers,
  implementing token bucket rate-limiters, managing session stores, or setting
  cache invalidation TTL policies.
---

# High-Performance Redis & Upstash Caching Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Implementing high-throughput key-value caching in front of heavy database queries.
- Building sliding-window or token-bucket API rate limiters (`429 Too Many Requests`).
- Managing distributed session states across multi-instance server deployments.
- Deploying serverless edge Redis (Upstash) with REST endpoints.
- Enforcing cache expiration policies (`EX`, `PX`) to prevent stale memory bloat.

---

## 2. Hard Architectural Rules

1. **Every Cache Key Must Have a TTL**:
   Never store unbounded cache keys without explicit expiration (`set(key, value, ex=3600)`). Storing indefinite keys inevitably triggers memory exhaustion (OOM) on production Redis instances.

2. **Atomic Sliding-Window Rate Limiting**:
   Never use simple `incr` alone for sliding rate limits, which allows double-spikes at the edge of time windows. Use sorted sets (`zadd`, `zremrangebyscore`) inside atomic Redis pipelines or Lua scripts.

3. **Cache Invalidation Discipline (Cache-Aside Pattern)**:
   Always update or invalidate cache keys immediately when mutations occur (`delete(f"user:{user_id}")`). Never let database updates live alongside stale cache data.

---

## 3. Production Code Patterns

### Pattern A: Cache-Aside Database Wrapper (Python)
```python
import os
import json
import redis
from typing import Optional, Callable, Any

r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

def get_or_set_cache(cache_key: str, ttl_seconds: int, fetch_func: Callable[[], Any]) -> Any:
    \"\"\"Reads from Redis cache; falls back to database on cache miss.\"\"\"
    cached_val = r.get(cache_key)
    if cached_val is not None:
        return json.loads(cached_val)

    # Cache miss: execute heavy database fetch
    data = fetch_func()
    if data is not None:
        r.set(cache_key, json.dumps(data), ex=ttl_seconds)
    return data
```

---

## 4. Verification Command
Test Redis connection and ping latency:
```bash
redis-cli ping
```
"""
    },
    "docker-microservices": {
        "category": "Infra",
        "description": "Use when architecting multi-stage Docker container builds, composing multi-service stacks (FastAPI, Node, Mongo, Redis), configuring healthchecks, and managing non-root security.",
        "content": """---
name: docker-microservices
description: >-
  Use when architecting multi-stage Docker container builds, composing
  multi-service stacks (FastAPI, Node, Mongo, Redis), configuring healthchecks,
  and managing non-root security.
---

# Docker Multi-Stage Microservices & Compose Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Writing optimized multi-stage `Dockerfile` definitions for Python, Node.js, or Go.
- Orchestrating full-stack services with `docker-compose.yml` (API, Database, Cache).
- Reducing image sizes by 80% using slim base images (`python:3.11-slim`, `node:20-alpine`).
- Enforcing non-root container security (`USER appuser`).
- Adding automated healthcheck probes (`HEALTHCHECK CMD curl -f http://localhost:PORT/health`).

---

## 2. Hard Architectural Rules

1. **Never Run Containers as Root**:
   Always declare a dedicated non-root user (`RUN useradd -m appuser && USER appuser`) before runtime execution. Running as root allows container-escape vulnerabilities to compromise the host kernel.

2. **Multi-Stage Builds for Minimal Image Size**:
   Compile dependencies, dev packages, and build tools in a temporary builder stage. Copy **only** built artifacts and production dependencies into the final slim runtime image.

3. **Explicit Volume Mounts for Persistence**:
   Never store production database files (MongoDB `/data/db`, PostgreSQL `/var/lib/postgresql/data`) inside container layers. Always attach named Docker volumes.

---

## 3. Production Code Patterns

### Pattern A: Multi-Stage Python FastAPI Dockerfile
```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Minimal Runtime
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1001 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:5000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```
"""
    }
}

def update_readme_table(name, category, description):
    """Appends newly generated skill to README.md table."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    row = f"| **`{name}`** | {category} | {description} | `npx degit saidixitn/skills/skills/{name} ~/.gemini/config/skills/{name}` |\n"
    if name not in content and "| :--- |" in content:
        parts = content.split("<!-- END_SKILLS_TABLE -->")
        if len(parts) == 2:
            new_content = parts[0] + row + "<!-- END_SKILLS_TABLE -->" + parts[1]
        else:
            # Fallback append before License
            new_content = content.replace("## 🔒 Confidentiality", row + "\n## 🔒 Confidentiality")
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)

def run():
    print("=== Dynamic GitHub Actions Skill Generator ===")

    # 1. Run zero-leak security audit
    res = subprocess.run([sys.executable, AUDIT_SCRIPT], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[CRITICAL] Confidentiality audit failed!")
        sys.exit(1)

    # 2. Inspect queue
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    pending = [s for s in queue if s.get("status") == "pending"]
    completed = [s for s in queue if s.get("status") == "completed"]

    print(f"Current Queue Status: {len(completed)} completed, {len(pending)} pending.")

    if not pending:
        print("All existing queue items completed. Checking dynamic seed templates...")
        for name, data in SKILL_TEMPLATES.items():
            if not any(s.get("name") == name for s in queue):
                queue.append({
                    "name": name,
                    "category": data["category"],
                    "status": "pending",
                    "summary": data["description"]
                })
                print(f"Seeded new pending skill: '{name}'")
        pending = [s for s in queue if s.get("status") == "pending"]

    if not pending:
        print("All skills completed!")
        sys.exit(0)

    target_skill = pending[0]
    skill_name = target_skill["name"]
    category = target_skill.get("category", "General")
    print(f"⚡ Synthesizing Next Skill: '{skill_name}' (Category: {category})")

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    os.makedirs(skill_path, exist_ok=True)
    skill_md = os.path.join(skill_path, "SKILL.md")

    template = SKILL_TEMPLATES.get(skill_name)
    if template:
        with open(skill_md, "w", encoding="utf-8") as f:
            f.write(template["content"].strip() + "\n")
        print(f" Successfully authored '{skill_md}'.")
    else:
        # Fallback structured draft
        content = f"""---
name: {skill_name}
description: Use when implementing {skill_name} architectures and production workflows.
---

# {skill_name.replace('-', ' ').title()} Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Architecting high-performance {skill_name} solutions.
- Enforcing production reliability and zero-leak security rules.

## 2. Hard Architectural Rules
1. Never commit secrets, credentials, or production tokens in code.
2. Always handle failure boundaries and connection timeouts explicitly.
"""
        with open(skill_md, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

    # Mark completed in queue
    target_skill["status"] = "completed"
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

    # Update README.md
    desc = target_skill.get("summary") or target_skill.get("description", "Production skill")
    update_readme_table(skill_name, category, desc)

    # Re-run audit to ensure newly generated skill is 100% clean
    res2 = subprocess.run([sys.executable, AUDIT_SCRIPT], capture_output=True, text=True)
    if res2.returncode != 0:
        print(f"[SECURITY ALERT] Newly generated skill failed audit:\n{res2.stdout}")
        sys.exit(1)

    print(f" Skill '{skill_name}' authored, audited, and added successfully!")

if __name__ == "__main__":
    run()
