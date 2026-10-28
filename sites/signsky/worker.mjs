// Reuse the V5 asset adapter; constrain this isolated deployment to one hostname.
import adapter from '../../worker/index.js';
export default {
  async fetch(request,env){
    const url=new URL(request.url);
    const publicHost=url.hostname==='signsky.nalmada.net' && env.SIGNSKY_PUBLIC==='1';
    const response=await adapter.fetch(request,{...env,V5_STAGING:'0',ANALYTICS:undefined});
    const headers=new Headers(response.headers);
    headers.set('X-Content-Type-Options','nosniff');
    if(!publicHost || response.status===404) headers.set('X-Robots-Tag','noindex, nofollow, noarchive');
    if(!publicHost && url.pathname==='/robots.txt') return new Response('User-agent: *\nDisallow: /\n',{headers});
    if(!publicHost && url.pathname==='/sitemap.xml') return new Response('Not found',{status:404,headers});
    return new Response(response.body,{status:response.status,headers});
  }
};
