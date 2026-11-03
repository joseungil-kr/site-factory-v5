/** New-site preview only. HTML dispatch invokes the Worker; public assets may bypass it. */
export function createSharedWorker(hosts) {
return {
  async fetch(request, env) {
    const url = new URL(request.url);
    const headers = {'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store'};
    const missing = () => new Response('Not found', {status: 404, headers});
    const site = Object.hasOwn(hosts, url.hostname) ? hosts[url.hostname] : null;
    if (!site || !['GET', 'HEAD'].includes(request.method)) return missing();
    let path;
    try { path = decodeURIComponent(url.pathname); } catch { return missing(); }
    if (path.startsWith('/_') || path.includes('\\') || path.includes('\0') || path.split('/').some(x => x === '..' || x === '.')) return missing();
    if (path === '/robots.txt') {
      return new Response(request.method === 'HEAD' ? null : 'User-agent: *\nDisallow: /\n',
        {headers: {...headers, 'Content-Type': 'text/plain; charset=utf-8'}});
    }
    if (path === '/sitemap.xml' || path === '/__v5_event') return missing();
    if (path === '/') path = '/index.html';
    const found = site.paths.includes(path);
    url.pathname = '/_sfv5/sites/' + site.id + (found ? path : '/404.html');
    url.search = '';
    const response = await env.ASSETS.fetch(new Request(url, {method: request.method}));
    const resultHeaders = new Headers(response.headers);
    for (const [key, value] of Object.entries(headers)) resultHeaders.set(key, value);
    return new Response(request.method === 'HEAD' ? null : response.body,
      {status: found ? response.status : 404, headers: resultHeaders});
  }
};
}
