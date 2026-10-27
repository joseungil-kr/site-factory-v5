/**
 * V5 Static Assets adapter.
 * Default analytics is OFF. No URL queries, IP addresses or user agents are written.
 */
const EVENTS = new Set(['phone', 'shop', 'calculator']);
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/__v5_event') {
      if (request.method !== 'POST' || !env.ANALYTICS) return new Response('Not found', {status:404});
      const origin = request.headers.get('Origin');
      if (origin !== url.origin) return new Response('Forbidden', {status:403});
      if (!request.headers.get('content-type')?.startsWith('application/json')) return new Response('Bad request',{status:400});
      const length = Number(request.headers.get('content-length') || '0');
      if (length > 256) return new Response('Too large',{status:413});
      let body;
      try {
        if (!request.body) return new Response('Missing body',{status:400});
        const reader=request.body.getReader();
        const chunks=[];let bytes=0;
        while (true) {
          const {done,value}=await reader.read();
          if (done) break;
          bytes+=value.byteLength;
          if (bytes>256) { await reader.cancel();return new Response('Too large',{status:413}); }
          chunks.push(value);
        }
        const raw=new Uint8Array(bytes);let offset=0;
        for (const chunk of chunks) {raw.set(chunk,offset);offset+=chunk.byteLength;}
        body=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
      } catch { return new Response('Invalid JSON',{status:400}); }
      const route = body?.page;
      if (!EVENTS.has(body?.event) || typeof route !== 'string' || route.length>150 || !route.startsWith('/') || route.includes('?')) {
        return new Response('Bad event',{status:400});
      }
      env.ANALYTICS.writeDataPoint({blobs:[body.event,route],doubles:[1],indexes:[url.hostname]});
      return new Response(null,{status:204,headers:{'Cache-Control':'no-store'}});
    }
    // Exact-authorized host only. workers.dev remains noindex and does not get
    // the production sitemap or dynamically indexable documents.
    const approvedHosts = new Set(['plants.nalmada.net','daysky.nalmada.net','flower.nalmada.net']);
    const indexedHost = env.V5_STAGING === '1' &&
      approvedHosts.has(env.V5_PUBLIC_HOST) &&
      url.hostname.toLowerCase() === env.V5_PUBLIC_HOST;

    // Cloudflare Asset binding has returned 404 for the uploaded sitemap.xml on
    // this specific Worker. Derive the same validated 1081 URLs from the deployed
    // 1080-hall search index instead of silently publishing a broken sitemap.
    if (indexedHost && url.hostname.toLowerCase()==='flower.nalmada.net' &&
        url.pathname==='/sitemap.xml' &&
        (request.method==='GET' || request.method==='HEAD')) {
      const indexUrl=new URL('/halls.json',url.origin);
      const hallResponse=await env.ASSETS.fetch(new Request(indexUrl,request));
      if (hallResponse.status!==200) return new Response('Hall index missing',{status:503});
      let halls;
      try { halls=await hallResponse.json(); }
      catch { return new Response('Invalid hall index',{status:503}); }
      if (!Array.isArray(halls) || halls.length!==1080) {
        return new Response('Incomplete hall index',{status:503});
      }
      const seen=new Set();
      const locs=['/'];
      for (const hall of halls) {
        if (typeof hall?.u!=='string' || !/^\/fh-[0-9a-f]{20}\.html$/.test(hall.u) ||
            seen.has(hall.u)) return new Response('Invalid hall URL',{status:503});
        seen.add(hall.u);
        locs.push(hall.u);
      }
      const xml='<?xml version="1.0" encoding="UTF-8"?>'+
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+
        locs.map(path=>'<url><loc>https://flower.nalmada.net'+path+'</loc></url>').join('')+
        '</urlset>';
      return new Response(request.method==='HEAD'?null:xml,{
        status:200,
        headers:{'Content-Type':'application/xml; charset=utf-8',
                 'Cache-Control':'public, max-age=600',
                 'X-Robots-Tag':'index, follow'}
      });
    }
    // All staging assets go through the Worker, including / and 404 responses.
    let response;
    if (url.pathname === '/') {
      url.pathname = '/index.html';
      response = await env.ASSETS.fetch(new Request(url,request));
    } else {
      response = await env.ASSETS.fetch(request);
    }

    if (env.V5_STAGING === '1' && !indexedHost) {
      const headers = new Headers(response.headers);
      headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
      headers.set('Cache-Control', 'no-store');
      headers.set('X-Content-Type-Options', 'nosniff');
      if (url.pathname === '/robots.txt') {
        headers.set('Content-Type','text/plain; charset=utf-8');
        return new Response('User-agent: *\nDisallow: /\n', {status:200,headers});
      }
      return new Response(response.body, {status:response.status, statusText:response.statusText, headers});
    }
    if (indexedHost && response.status === 404) {
      const headers=new Headers(response.headers);
      headers.set('X-Robots-Tag','noindex, nofollow');
      return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
    }
    return response;
  }
};
