// Isolated noindex preview; no custom domains, routes or shared Worker changes.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const headers = { 'X-Robots-Tag': 'noindex, nofollow, noarchive', 'X-Content-Type-Options': 'nosniff' };
    if (url.pathname === '/robots.txt') return new Response('User-agent: *\nDisallow: /\n', { headers: {...headers, 'Content-Type': 'text/plain; charset=utf-8'} });
    if (url.pathname === '/sitemap.xml') return new Response('Not found', {status:404, headers});
    if (url.pathname === '/') url.pathname = '/index.html';
    const response = await env.ASSETS.fetch(new Request(url, request));
    const responseHeaders = new Headers(response.headers);
    for (const [name, value] of Object.entries(headers)) responseHeaders.set(name, value);
    return new Response(response.body, {status:response.status, headers:responseHeaders});
  }
};
