// One Worker serves the approved custom domain as public and workers.dev as noindex preview.
export default {
  async fetch(request, env) {
    const u = new URL(request.url);
    const isPublicHost = u.hostname === 'wreath.nalmada.net' && env.WREATH_PUBLIC === '1';
    if (!isPublicHost && u.pathname === '/robots.txt') {
      return new Response('User-agent: *\\nDisallow: /\\n', {
        headers: {'Content-Type': 'text/plain; charset=utf-8', 'X-Robots-Tag': 'noindex,nofollow,noarchive'}
      });
    }
    if (!isPublicHost && u.pathname === '/sitemap.xml') {
      return new Response('Not found', {status: 404, headers: {'X-Robots-Tag': 'noindex,nofollow,noarchive'}});
    }
    if (u.pathname === '/') u.pathname = '/index.html';
    const response = await env.ASSETS.fetch(new Request(u, request));
    const headers = new Headers(response.headers);
    headers.set('X-Content-Type-Options', 'nosniff');
    if (!isPublicHost || response.status === 404) headers.set('X-Robots-Tag', 'noindex,nofollow,noarchive');
    if (!isPublicHost && response.status === 200 && (headers.get('content-type') || '').includes('text/html')) {
      // Public candidate HTML contains index/follow and the public canonical.
      // For workers.dev only, rewrite HTML metadata without weakening access controls.
      return new HTMLRewriter()
        .on('head link[rel="canonical"]', { element(e) { e.remove(); } })
        .on('head meta[name="robots"]', { element(e) { e.setAttribute('content', 'noindex,nofollow'); } })
        .transform(new Response(response.body, {status: response.status, headers}));
    }
    return new Response(response.body, {status: response.status, headers});
  }
};
