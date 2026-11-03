// Isolated host policy; never modifies the shared V5 Worker or its host allowlist.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const indexable = env.OFFICEPLANT_PUBLIC === '1' && url.hostname === 'officeplant.nalmada.net';
    if (url.pathname === '/') url.pathname = '/index.html';
    const response = await env.ASSETS.fetch(new Request(url, request));
    const headers = new Headers(response.headers);
    headers.set('X-Content-Type-Options', 'nosniff');
    if (!indexable || response.status === 404) headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
    if (!indexable && url.pathname === '/robots.txt') return new Response('User-agent: *\nDisallow: /\n', {headers});
    if (!indexable && ['/sitemap.xml','/rss.xml'].includes(url.pathname)) return new Response('Not found', {status:404,headers});
    if(indexable && url.pathname === '/rss.xml' && response.ok)headers.set('Content-Type','application/rss+xml; charset=utf-8');
    if(!indexable && headers.get('Content-Type')?.includes('text/html')){
      const body=(await response.text()).replace(/<link rel="alternate" type="application\/rss\+xml"[^>]*>/g,'');
      headers.delete('Content-Length');headers.delete('ETag');
      return new Response(body,{status:response.status,headers});
    }
    return new Response(response.body, {status:response.status,headers});
  }
};