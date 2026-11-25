// First-Party Lightweight Analytics Pixel
// Embed via: <script src="/js/tracker-pixel.js" defer></script>
(function (w, d) {
  const ep = w.ANALYTICS_ENDPOINT || '/api/telemetry';
  function send(type, meta) {
    const data = JSON.stringify({
      t: type,
      u: location.pathname,
      r: d.referrer,
      m: meta || {},
      ts: Date.now()
    });
    if (navigator.sendBeacon) navigator.sendBeacon(ep, data);
    else fetch(ep, { method: 'POST', body: data, keepalive: true }).catch(() => {});
  }
  d.addEventListener('click', (e) => {
    const el = e.target.closest('a, button');
    if (el) send('click', { tag: el.tagName, text: el.innerText.slice(0, 25) });
  }, { passive: true });
  send('pv');
})(window, document);
