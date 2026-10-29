// Isolated V5-2 wreath region Worker; default denied indexing everywhere.
export default {
  async fetch(request, env) {
    const u=new URL(request.url);
    const allowed=u.hostname==='wreath.nalmada.net' && env.WREATH_PUBLIC==='1';
    if(!allowed && u.pathname==='/robots.txt')return new Response('User-agent: *\nDisallow: /\n',
      {headers:{'Content-Type':'text/plain; charset=utf-8','X-Robots-Tag':'noindex,nofollow,noarchive'}});
    if(!allowed && u.pathname==='/sitemap.xml')return new Response('Not found',{status:404,headers:{'X-Robots-Tag':'noindex,nofollow,noarchive'}});
    if(u.pathname==='/')u.pathname='/index.html';
    const response=await env.ASSETS.fetch(new Request(u,request));
    const headers=new Headers(response.headers);
    headers.set('X-Content-Type-Options','nosniff');
    if(!allowed || response.status===404)headers.set('X-Robots-Tag','noindex,nofollow,noarchive');
    return new Response(response.body,{status:response.status,headers});
  }
};
