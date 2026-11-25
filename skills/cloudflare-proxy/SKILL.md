---
name: cloudflare-proxy
description: >-
  Use when building Cloudflare Workers edge reverse proxies, masking origin VPS
  IP addresses, terminating SSL certificates at the edge, rewriting request paths,
  injecting dynamic CORS headers, or caching API responses globally.
---

# Cloudflare Workers Edge Reverse Proxy Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Shielding backend origin servers (VPS IP addresses) from direct public exposure and port scans.
- Deploying **Cloudflare Workers** as lightweight, globally distributed reverse proxies.
- Terminating edge HTTPS and automatically upgrading insecure HTTP requests.
- Dynamically rewriting request URLs and sanitizing headers between clients and origins.
- Injecting CORS headers at the edge to solve browser preflight (`OPTIONS`) requirements without touching backend code.

---

## 2. Hard Architectural Rules

1. **Origin IP Cloaking**:
   Never reveal the raw VPS IP address in public DNS records, client-side JavaScript, or API documentation. All client traffic must terminate at Cloudflare Workers or Cloudflare Proxied DNS.

2. **Handle HTTP OPTIONS (Preflight) at the Edge**:
   Always handle `OPTIONS` requests directly inside the Cloudflare Worker without forwarding them to the backend VPS. This eliminates backend server load for CORS preflights and speeds up API response times.

3. **Pass-Through Header Hygiene**:
   Always forward `CF-Connecting-IP` as `X-Forwarded-For` or `X-Real-IP` so your backend application logs the actual visitor's IP address rather than Cloudflare's edge proxy IPs.

4. **Wrangler Secret Management**:
   Never hardcode origin endpoints or internal auth tokens in `wrangler.toml`. Store origin URLs in Cloudflare Worker environment variables or secrets (`wrangler secret put ORIGIN_URL`).

---

## 3. Edge Reverse Proxy Architecture

```
[ Client Browser / Mobile App ]
               │ (HTTPS to custom domain / workers.dev)
               ▼
[ Cloudflare Global Edge Network ]
   ├─ 1. Intercept OPTIONS -> Return 204 CORS immediately
   ├─ 2. Inject X-Real-IP (CF-Connecting-IP)
   ├─ 3. Terminate Edge SSL & Check Cache
               │
               ▼ (Proxied Request to Origin)
[ Origin VPS (Port 5000 / FastAPI / Express) ]
```

---

## 4. Production Code Patterns

### Pattern A: Master Cloudflare Worker Reverse Proxy (`worker.js`)
Directly sourced from your production edge architecture (`app.saidixit.workers.dev`):

```javascript
/**
 * Cloudflare Worker Edge Reverse Proxy
 * Proxies incoming edge requests to private origin backend with CORS and header rewriting.
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
  'Access-Control-Max-Age': '86400',
};

export default {
  async fetch(request, env, ctx) {
    // 1. Handle CORS Preflight at the Edge
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS,
      });
    }

    const url = new URL(request.url);
    // Origin configured via environment secret
    const originHost = env.ORIGIN_URL || 'http://origin-vps.internal:5000';
    const targetUrl = new URL(url.pathname + url.search, originHost);

    // 2. Clone and sanitize headers
    const newHeaders = new Headers(request.headers);
    newHeaders.set('X-Forwarded-Host', url.hostname);
    newHeaders.set('X-Real-IP', request.headers.get('cf-connecting-ip') || '');
    newHeaders.set('Host', targetUrl.host);

    const init = {
      method: request.method,
      headers: newHeaders,
      redirect: 'follow',
    };

    // Forward request body for non-GET/HEAD methods
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      init.body = request.body;
    }

    try {
      // 3. Fetch from origin with error fallback
      const originResponse = await fetch(targetUrl.toString(), init);
      const responseHeaders = new Headers(originResponse.headers);

      // 4. Inject CORS headers into origin response
      for (const [key, value] of Object.entries(CORS_HEADERS)) {
        responseHeaders.set(key, value);
      }

      return new Response(originResponse.body, {
        status: originResponse.status,
        statusText: originResponse.statusText,
        headers: responseHeaders,
      });
    } catch (err) {
      return new Response(
        JSON.stringify({
          error: 'EDGE_GATEWAY_TIMEOUT',
          message: 'Origin server unreachable or unresponsive.',
        }),
        {
          status: 502,
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        }
      );
    }
  },
};
```

---

### Pattern B: Wrangler Deployment Configuration (`wrangler.toml`)
```toml
name = "vps-edge-proxy"
main = "worker.js"
compatibility_date = "2024-01-01"

[vars]
ENVIRONMENT = "production"

# Deploy command: npx wrangler deploy
```

---

## 5. Anti-Patterns & Common Pitfalls

| Mistake | Fatal Impact | Edge Fix |
| :--- | :--- | :--- |
| **Forwarding OPTIONS to origin** | Multiplies origin server CPU load | Intercept and return 204 directly at the edge |
| **Missing `X-Real-IP` injection** | Origin backend sees all visitors as Cloudflare IPs | Read `cf-connecting-ip` and set `X-Real-IP` |
| **Hardcoding origin IPs in frontend code** | Attackers bypass Cloudflare and DDoS origin directly | Only expose worker URL or proxied domain |

---

## 6. Verification Command
Deploy and inspect edge logs in real-time:
```bash
npx wrangler tail
```
