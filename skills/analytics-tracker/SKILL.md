---
name: analytics-tracker
description: >-
  Use when engineering lightweight first-party telemetry tracking scripts,
  capturing click events with navigator.sendBeacon, recording session IDs,
  bypassing ad-blocker filters, or streaming raw analytics into MongoDB or PostgreSQL.
---

# First-Party Telemetry & Click Analytics Tracker Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Implementing lightweight, zero-dependency client-side tracking beacons (under 2KB).
- Replacing bloated third-party trackers (Google Analytics 50KB+) with first-party telemetry.
- Bypassing browser ad-blockers by routing tracking beacons through your own domain.
- Asynchronously dispatching click and scroll events using `navigator.sendBeacon()`.
- Ingesting and aggregating high-volume raw event batches in Express and MongoDB.

---

## 2. Hard Architectural Rules

1. **Use `navigator.sendBeacon` for Exit Resilience**:
   Never use standard asynchronous `fetch()` or `XMLHttpRequest` on link click or page unload events. Browsers cancel pending `fetch()` requests when the user leaves the page. Always use `navigator.sendBeacon(endpoint, payload)`, which guarantees delivery in the background even after page destruction.

2. **Zero DOM Performance Impact**:
   Never attach expensive individual `click` event listeners to hundreds of separate elements. Always use **event delegation** at the `document` level (`document.addEventListener('click', handleEvent, { passive: true })`).

3. **Privacy by Design**:
   Never collect PII (Personally Identifiable Information) like plaintext IP addresses or raw passwords. Hash IP addresses with daily salt or discard after geographical resolution.

4. **Payload Batching**:
   Avoid firing an HTTP request for every micro-movement. Buffer scroll depth and interaction events and flush them in batches of 5–10 events or every 5 seconds.

---

## 3. Production Code Patterns

### Pattern A: Master 1.8KB Client-Side Tracking Pixel (`v.js`)
Sourced directly from your `job-insights/v.js` telemetry engine:

```javascript
/**
 * First-Party Micro Telemetry Beacon (v.js)
 * Size: ~1.8KB. Zero dependencies. Bypasses ad-blockers.
 */
(function (window, document) {
  'use strict';

  const ENDPOINT = window.ANALYTICS_ENDPOINT || '/api/v1/telemetry';

  // 1. Session ID Generator
  function getSessionId() {
    let sid = sessionStorage.getItem('_sid');
    if (!sid) {
      sid = 's_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
      sessionStorage.setItem('_sid', sid);
    }
    return sid;
  }

  // 2. High-Reliability Event Dispatcher
  function sendEvent(eventType, metadata = {}) {
    const payload = JSON.stringify({
      event: eventType,
      url: window.location.href,
      path: window.location.pathname,
      referrer: document.referrer || '',
      session_id: getSessionId(),
      timestamp: new Date().toISOString(),
      meta: metadata
    });

    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT, payload);
    } else {
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true
      }).catch(() => {});
    }
  }

  // 3. Document-Level Click Event Delegation
  document.addEventListener('click', function (e) {
    const target = e.target.closest('a, button, [data-track]');
    if (!target) return;

    const trackName = target.getAttribute('data-track') || target.id || target.innerText.substring(0, 30).trim();
    sendEvent('click', {
      element: target.tagName.toLowerCase(),
      track_id: trackName,
      href: target.href || ''
    });
  }, { passive: true });

  // 4. Initial Pageview
  sendEvent('pageview');

  window.trackEvent = sendEvent;
})(window, document);
```

---

### Pattern B: Backend Fast Ingestion Endpoint (Express & MongoDB)
```javascript
app.post('/api/v1/telemetry', async (req, res) => {
  // Return immediate 204 No Content to free client socket
  res.status(204).end();

  try {
    const event = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    event.ip_hash = hashIp(req.ip);
    event.received_at = new Date();

    // Direct background insert into MongoDB
    await db.collection('raw_clicks').insertOne(event);
  } catch (err) {
    // Fail silently without disrupting client
  }
});
```

---

## 4. Anti-Patterns & Pitfalls

| Mistake | Fatal Impact | Solution |
| :--- | :--- | :--- |
| **Using `fetch` on outbound clicks** | 30–40% of click events lost on link redirect | Use `navigator.sendBeacon()` with `keepalive: true` |
| **Individual listeners on every button** | Memory leaks on complex dynamic apps | Use delegated `document.addEventListener` |
| **Loading from `google-analytics.com`** | Blocked by uBlock Origin and Brave | Host tracking script on your own domain (`/js/v.js`) |
