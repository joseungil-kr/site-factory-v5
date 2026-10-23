/** Collects only action category and path. No names, forms, query parameters or cookies. */
(() => {
  const ALLOWED = new Set(['phone','shop','calculator']);
  async function record(action) {
    if (!ALLOWED.has(action)) return;
    const payload = JSON.stringify({event:action,page:location.pathname});
    try {
      await fetch('/__v5_event',{method:'POST',headers:{'Content-Type':'application/json'},body:payload,keepalive:true,credentials:'omit'});
    } catch (_) { /* Reporting must never block customer actions. */ }
  }
  document.addEventListener('click', (event) => {
    const link = event.target.closest('[data-track-event]');
    if (link) record(link.dataset.trackEvent);
  });
  window.v5TrackCalculator = () => record('calculator');
})();
