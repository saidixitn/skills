// Speculative Link Pre-Warming Engine
// Add to public/js/fast-loader.js and load via <script src="/js/fast-loader.js" defer></script>
(function () {
  const prefetched = new Set();
  const isSlow = navigator.connection && (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType));
  if (isSlow) return;

  function prefetch(url) {
    if (prefetched.has(url) || url === window.location.href || url.includes('#')) return;
    prefetched.add(url);
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    link.as = 'document';
    document.head.appendChild(link);
  }

  document.addEventListener('mouseover', (e) => {
    const a = e.target.closest('a');
    if (a && a.origin === window.location.origin) prefetch(a.href);
  }, { passive: true });

  document.addEventListener('touchstart', (e) => {
    const a = e.target.closest('a');
    if (a && a.origin === window.location.origin) prefetch(a.href);
  }, { passive: true });
})();
