// Separate, noindex-only WreathPrice sample worker. No domain routes.
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    if(url.pathname==='/sitemap.xml')return new Response('Not found',{status:404,headers:{'X-Robots-Tag':'noindex,nofollow,noarchive'}});
    if(url.pathname==='/robots.txt')return new Response('User-agent: *\nDisallow: /\n',{headers:{'Content-Type':'text/plain; charset=utf-8','X-Robots-Tag':'noindex,nofollow,noarchive'}});
    const aliases={'/':'/ansan/index.html','/ansan/':'/ansan/index.html','/regions/':'/regions/index.html','/localities/':'/localities/index.html','/ansan/sangnok/':'/ansan/sangnok/index.html','/ansan/sangnok/bono/':'/ansan/sangnok/bono/index.html'};
    url.pathname=aliases[url.pathname]||url.pathname;
    const response=await env.ASSETS.fetch(new Request(url,request));
    const headers=new Headers(response.headers);
    headers.set('X-Robots-Tag','noindex,nofollow,noarchive');
    headers.set('X-Content-Type-Options','nosniff');
    return new Response(response.body,{status:response.status,headers});
  }
};
