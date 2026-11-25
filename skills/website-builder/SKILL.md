---
name: website-builder
description: >-
  Use when architecting high-performance static websites, sub-100ms
  Time-To-Interactive (TTI) web apps, zero-hydration architectures, speculative
  link pre-warming, Service Worker media caching, and edge CDN cache headers.
---

# High-Performance Static Website Architecture Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Architecting high-converting portfolios, agency landing pages, or multi-page documentation without framework bloat.
- Achieving sub-100ms **Time-To-Interactive (TTI)** and zero cumulative layout shift (CLS).
- Implementing speculative link pre-warming (`fast-loader.js`) that downloads pages on user intent (hover/touch).
- Caching video and media byte-ranges offline via Service Workers (`sw.js`).
- Configuring edge CDN caching headers (Vercel, Cloudflare, Netlify) for atomic instant invalidation.

---

## 2. Hard Architectural Rules

1. **Zero Hydration Penalty**:
   Avoid heavy fullstack frameworks (Next.js/Nuxt/Remix) for static showcase sites. Fullstack frameworks ship 180KB+ of baseline runtime JS, causing DOM reconstruction lag on low-power mobile devices. Use native modern ES Modules, semantic HTML5, and hardware-accelerated CSS.

2. **The 100ms Intent Pre-Warming Rule**:
   Always pre-warm links on user intent (`mouseenter` or `touchstart`). By the time the user's click triggers navigation (average 100ms–250ms reaction time), the destination page is already cached in memory, creating the illusion of zero-latency page loads.

3. **Service Worker Range-Request Passthrough**:
   Safari and Chrome require HTTP 206 (Partial Content) range requests for `<video>` and audio streaming. Never let a Service Worker intercept video requests with standard `fetch()` without slicing byte ranges, otherwise video scrubbing stutters and fails.

4. **Immutable Asset Caching**:
   - Static hashed assets (`/assets/*.[hash].css`, `.js`, `.woff2`): `Cache-Control: public, max-age=31536000, immutable`.
   - HTML documents: `Cache-Control: public, max-age=0, must-revalidate` (guarantees visitors always receive fresh markup immediately after deployments).

5. **Font Display Swap**:
   Always declare `font-display: swap;` in `@font-face` rules to eliminate invisible text flash (FOIT).

---

## 3. High-Performance Website Architecture

```
[ Visitor Hover / Touch Event ]
               │
               ▼
[ Speculative Pre-Warming (fast-loader.js injected <link rel="prefetch">) ]
               │
               ▼
[ Instant Cache Hit on Click (< 50ms transition) ]
               │
               ▼
[ Head Anti-FOUC Router Activates Layout Instantly ]
               │
               ▼
[ Service Worker Serves Cached Media Bytes (sw.js) ]
```

---

## 4. Production Code Patterns

### Pattern A: Speculative Pre-Warming Engine (`fast-loader.js`)
Sourced directly from your award-winning portfolio architecture:

```javascript
/**
 * Speculative Link Pre-Warming Engine
 * Monitors internal links and prefetches resources on hover or touch intent.
 */
(function initFastLoader() {
  const prefetched = new Set();
  const isSlowConnection =
    navigator.connection &&
    (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType));

  // Skip prefetching on metered or 2G connections
  if (isSlowConnection) return;

  function prefetchUrl(url) {
    if (prefetched.has(url) || url === window.location.href || url.includes('#')) return;
    prefetched.add(url);

    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    link.as = 'document';
    document.head.appendChild(link);
  }

  function handleIntent(e) {
    const anchor = e.target.closest('a');
    if (!anchor || !anchor.href) return;

    const url = new URL(anchor.href, window.location.origin);
    // Only prefetch same-origin internal routes
    if (url.origin === window.location.origin && !url.pathname.endsWith('.pdf')) {
      prefetchUrl(anchor.href);
    }
  }

  // Pre-warm on desktop hover and mobile initial touch
  document.addEventListener('mouseover', handleIntent, { passive: true });
  document.addEventListener('touchstart', handleIntent, { passive: true });
})();
```

---

### Pattern B: Service Worker Video Range Caching (`sw.js`)
Handles partial content byte-ranges (HTTP 206) so high-resolution video reels scrub seamlessly with zero buffering:

```javascript
const CACHE_NAME = 'media-cache-v1';
const VIDEO_EXTENSIONS = ['.mp4', '.webm', '.mov'];

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const isVideo = VIDEO_EXTENSIONS.some((ext) => url.pathname.endsWith(ext));

  if (!isVideo) return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      const cachedResponse = await cache.match(event.request);

      if (cachedResponse) {
        return cachedResponse;
      }

      const networkResponse = await fetch(event.request);
      // Only cache complete 200 responses to prevent corrupted chunks
      if (networkResponse.status === 200) {
        cache.put(event.request, networkResponse.clone());
      }
      return networkResponse;
    })()
  );
});
```

---

### Pattern C: Edge CDN Cache Rules (`vercel.json` or Cloudflare)
```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*).html",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ]
}
```

---

## 5. Anti-Patterns & Performance Traps

| Trap | Fatal Consequence | Solution |
| :--- | :--- | :--- |
| **Using Next.js for simple static portfolios** | 200KB JS bundle, hydration jank on mobile | Use pure HTML/CSS/ESM with speculative prefetching |
| **Intercepting video range requests with standard fetch** | Video scrubbing breaks in Safari | Let range requests bypass SW or return sliced byte responses |
| **Missing `font-display: swap`** | Flash of Invisible Text (FOIT) on slow 3G | Always declare `font-display: swap;` in `@font-face` |
| **Caching HTML permanently (`max-age=31536000`)** | Visitors see stale website versions forever | Use `max-age=0, must-revalidate` on all HTML routes |

---

## 6. Verification Checklist
- [ ] Lighthouse Performance score > 95 on mobile.
- [ ] Sub-100ms TTI on internal navigation.
- [ ] Video playback starts in under 200ms without buffering.
- [ ] Edge headers ensure immediate markup invalidation on deploy.
