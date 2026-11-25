---
name: api-builder
description: >-
  Use when architecting unified REST API gateways with FastAPI or Express,
  implementing Pydantic v2 validation, configuring CORS middleware, managing
  async dependency injection, or structuring multi-service route modules.
---

# Unified REST API Gateway & Backend Architecture Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Architecting high-throughput REST API gateways with **FastAPI** (Python) or **Express** (Node.js).
- Designing modular route controllers across dozens of backend endpoints (clicks reports, proxy management, analytics).
- Enforcing strict request/response data contracts using **Pydantic v2** models.
- Managing asynchronous database dependency injection (`Depends`) with connection pooling.
- Securing gateways with custom CORS middleware, rate limit headers, and unified RFC 7807 error envelopes.

---

## 2. Hard Architectural Rules

1. **Zero Raw Dictionary Returns**:
   Never return unvalidated, raw Python dictionaries or Node objects from public endpoints. Always return typed Pydantic models or clean response DTOs with explicit status codes.

2. **Async Route Handlers by Default**:
   Declare route handlers with `async def` when performing I/O (database queries, external HTTP calls). Avoid blocking synchronous I/O (`time.sleep` or synchronous `requests.get`) inside FastAPI event loops.

3. **CORS Explicit Origin Whitelisting**:
   Never use `allow_origins=["*"]` when `allow_credentials=True`. This violates modern browser security specs and causes cookie authentication failures. Always whitelist explicit origins.

4. **Sanitized Error Payloads**:
   Never expose internal stack traces, database schema names, or raw connection errors to API clients. Catch internal exceptions and return normalized JSON error envelopes (`{ "error": "NOT_FOUND", "message": "...", "status_code": 404 }`).

5. **Dependency Injection for DB Sessions**:
   Never create new database connections per request. Always inject pooled connections using FastAPI `Depends(get_db)`.

---

## 3. Step-by-Step API Gateway Architecture

```
[ Incoming Request from Cloudflare / Client ]
                     │
                     ▼
[ CORS & Security Headers Middleware ]
                     │
                     ▼
[ Pydantic v2 Input Validation & Type Casting ]
                     │
                     ▼
[ Async Dependency Injection (Database / Auth) ]
                     │
                     ▼
[ Controller Execution (Business Logic) ]
                     │
                     ▼
[ Typed Response DTO Serialization (RFC 7807) ]
```

---

## 4. Production Code Patterns

### Pattern A: Master FastAPI Gateway Module (Sai Dixit Production Gateway)
Grounded directly in your 42-endpoint VPS API gateway:

```python
import os
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from pymongo import MongoClient

app = FastAPI(
    title="Unified Production Gateway",
    version="2.0.0",
    docs_url="/docs-portal"
)

# 1. Hardened CORS Configuration
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "https://saidixit.vercel.app,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Reusable Database Dependency
def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri, maxPoolSize=50, serverSelectionTimeoutMS=4000)
    try:
        yield client["production"]
    finally:
        client.close()

# 3. Pydantic v2 Request & Response Contracts
class MetricReport(BaseModel):
    domain: str
    total_clicks: int = Field(ge=0, description="Total recorded clicks")
    unique_ips: int = Field(ge=0, description="Unique IP count")
    status: str = "active"

class APIResponse(BaseModel):
    success: bool = True
    data: List[MetricReport]
    count: int

# 4. Typed Controller Endpoint
@app.get("/api/v1/metrics", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def get_metrics(
    team: Optional[str] = Query(None, description="Team filter"),
    limit: int = Query(50, le=500),
    db = Depends(get_db)
):
    try:
        query = {"team": team} if team else {}
        cursor = db["metrics"].find(query, {"_id": 0}).limit(limit)
        results = list(cursor)
        return APIResponse(data=results, count=len(results))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database query failure: {str(e)}"
        )
```

---

### Pattern B: Express.js Route Controller (Node.js Alternative)
```javascript
const express = require('express');
const router = express.Router();

router.get('/health', async (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

module.exports = router;
```

---

## 5. Anti-Patterns & Operational Pitfalls

| Mistake | Impact | Fix |
| :--- | :--- | :--- |
| **`allow_origins=["*"]` with credentials** | CORS blocked in modern Chrome/Safari | Whitelist explicit domains in CORS middleware |
| **Synchronous `time.sleep` in async route** | Freezes entire server event loop for all users | Use `await asyncio.sleep()` or run in threadpool |
| **Raw database strings returned** | Exposes private user emails or internal MongoDB `_id` | Use Pydantic response models with projection filters |
| **Opening DB client per request** | Port exhaustion (`Cannot assign requested address`) | Use persistent connection pool with `Depends()` |

---

## 6. Verification Command
Test gateway health and OpenAPI schema generation:
```bash
python3 scripts/gateway_app.py --test-schema
```
