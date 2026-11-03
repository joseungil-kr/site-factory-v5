// RSS-only adaptation of V4 todayflower-public-release.yml; original host/SEO policy preserved.
const HOST='todayflower.nalmada.net';
const DOMAIN='https://'+HOST;
const OLD='<meta name="robots" content="noindex,nofollow">';
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    const path=url.pathname;
    const publicHost=url.hostname===HOST;
    const header={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
    if(publicHost && path==='/index.html')
      return Response.redirect(DOMAIN+'/',301);
    if(path==='/robots.txt'){
      const body=publicHost
        ? 'User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n'
        : 'User-agent: *\nDisallow: /\n';
      return new Response(body,{status:200,headers:{...header,
        'Content-Type':'text/plain; charset=utf-8',
        'X-Robots-Tag':publicHost?'index, follow':'noindex, nofollow, noarchive'}});
    }
    if(['/sitemap.xml','/rss.xml'].includes(path) && !publicHost)
      return new Response('Not Found',{status:404,headers:{...header,
        'X-Robots-Tag':'noindex, nofollow, noarchive'}});
    if(path==='/404.html')
      return new Response('Not Found',{status:404,headers:{...header,
        'X-Robots-Tag':'noindex, nofollow, noarchive'}});
    const assetUrl=new URL(url);
    if(path==='/')assetUrl.pathname='/index.html';
    const response=await env.ASSETS.fetch(new Request(assetUrl,request));
    const h=new Headers(response.headers);
    h.set('Cache-Control','no-store');
    h.set('X-Content-Type-Options','nosniff');
    if(response.status!==200){
      h.set('X-Robots-Tag','noindex, nofollow, noarchive');
      return new Response(response.body,{status:response.status,headers:h});
    }
    if(publicHost && path==='/rss.xml'){h.set('Content-Type','application/rss+xml; charset=utf-8');h.set('X-Robots-Tag','index, follow');return new Response(response.body,{status:200,headers:h});}
    if(publicHost && (path==='/'||/^\/(?:[1-9]\d*)\.html$/.test(path))){
      const n=path==='/'?1:Number(path.slice(1,-5));
      if(n===404 || n>5071)return new Response('Not Found',{status:404,headers:{
        'X-Robots-Tag':'noindex, nofollow, noarchive'}});
      const original=await response.text();
      if(original.split(OLD).length!==2 || original.includes('rel="canonical"'))
        return new Response('Unexpected source SEO metadata',{status:503,headers:{
          'X-Robots-Tag':'noindex, nofollow, noarchive'}});
      const canonical=DOMAIN+path;
      const html=original.replace(OLD,'<meta name="robots" content="index,follow">'+
        '<link rel="canonical" href="'+canonical+'">'+
        (path==='/'?'<meta name="naver-site-verification" content="d970eeb70abc7b36cbcc02fadd9362c5c57fcb46" />':'')+
          '<link rel="alternate" type="application/rss+xml" title="오늘꽃" href="https://todayflower.nalmada.net/rss.xml">');
      for(const headerName of ('Content-Encoding','Content-Length','ETag'))h.delete(headerName);
      h.set('Content-Type','text/html; charset=utf-8');
      h.set('X-Robots-Tag','index, follow');
      return new Response(html,{status:200,headers:h});
    }
    h.set('X-Robots-Tag',publicHost?'index, follow':'noindex, nofollow, noarchive');
    return new Response(response.body,{status:200,headers:h});
  }
};
