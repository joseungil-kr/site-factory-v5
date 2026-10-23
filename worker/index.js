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
    // All staging assets go through the Worker, including / and 404 responses.
    // This is intentionally independent of any custom-domain production headers.
    let response;
    if (url.pathname === '/') {
      url.pathname = '/index.html';
      response = await env.ASSETS.fetch(new Request(url,request));
    } else {
      response = await env.ASSETS.fetch(request);
    }
    if (env.V5_STAGING === '1') {
      const headers = new Headers(response.headers);
      headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
      headers.set('Cache-Control', 'no-store');
      headers.set('X-Content-Type-Options', 'nosniff');
      return new Response(response.body, {status:response.status, statusText:response.statusText, headers});
    }
    return response;
  }
};
