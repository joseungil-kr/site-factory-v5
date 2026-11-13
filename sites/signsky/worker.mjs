// Reuse the V5 asset adapter; constrain indexing to the exact approved hostname.
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
    if(!publicHost && response.status===200 && (headers.get('content-type')||'').includes('text/html')){
      let body=await response.text();
      body=body.replace(/<meta\s+name=["']robots["']\s+content=["']index,follow["']\s*\/?>/i,
        '<meta name="robots" content="noindex,nofollow">');
      body=body.replace(/<link\s+rel=["']canonical["'][^>]*>\s*/ig,'');
      headers.delete('content-length');
      headers.delete('content-encoding');
      headers.delete('etag');
      return new Response(body,{status:response.status,headers});
    }
    return new Response(response.body,{status:response.status,headers});
  }
};
