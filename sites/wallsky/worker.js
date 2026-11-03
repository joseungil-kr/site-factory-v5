// Local release candidate derived from V5's static-assets adapter.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const indexable = url.hostname === 'wallsky.nalmada.net' && env.WALLSKY_PUBLIC === '1';
    if (url.pathname === '/rss.xml' && !indexable) return new Response('Not found', {status:404, headers:{'X-Robots-Tag':'noindex, nofollow'}});
    if (url.pathname === '/robots.txt' && !indexable) {
      return new Response('User-agent: *\nDisallow: /\n', {
        headers: {'Content-Type':'text/plain; charset=utf-8','X-Robots-Tag':'noindex, nofollow'}
      });
    }
    // Reuse the V5-proven static-assets pattern: forward non-root requests
    // unchanged; only translate "/" to the actual index.html asset path.
    let response;
    if (url.pathname === '/') {
      url.pathname = '/index.html';
      response = await env.ASSETS.fetch(new Request(url, request));
    } else {
      response = await env.ASSETS.fetch(request);
    }
    const headers = new Headers(response.headers);
    headers.set('X-Content-Type-Options','nosniff');
    if (url.pathname === '/rss.xml' && indexable && response.ok) headers.set('Content-Type','application/rss+xml; charset=utf-8');
    if (!indexable && headers.get('Content-Type')?.includes('text/html')) {
      const body=(await response.text()).replace(/<link rel="alternate" type="application\/rss\+xml"[^>]*>/g,'');
      headers.delete('Content-Length');headers.delete('ETag');
      return new Response(body,{status:response.status,headers:{...Object.fromEntries(headers),'X-Robots-Tag':'noindex, nofollow, noarchive'}});
    }
    if (!indexable || response.status === 404) headers.set('X-Robots-Tag','noindex, nofollow, noarchive');
    return new Response(response.body,{status:response.status,headers});
  }
};
