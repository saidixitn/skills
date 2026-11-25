---
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
    """Reads from Redis cache; falls back to database on cache miss."""
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
