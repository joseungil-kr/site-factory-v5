// Local release candidate derived from V5's static-assets adapter.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const indexable = url.hostname === 'wallsky.nalmada.net' && env.WALLSKY_PUBLIC === '1';
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
    if (!indexable || response.status === 404) headers.set('X-Robots-Tag','noindex, nofollow, noarchive');
    return new Response(response.body,{status:response.status,headers});
  }
};
