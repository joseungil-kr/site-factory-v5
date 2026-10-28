import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './worker.mjs';

test('only exact approved host is indexable; preview HTML is noindex and canonical-free',async()=>{
  for(const host of ['signsky.nalmada.net','sfv52-signsky.workers.dev','other.nalmada.net']){
    const env={
      SIGNSKY_PUBLIC:'1',
      ASSETS:{fetch:async req=>{
        const path=new URL(req.url).pathname;
        if(path==='/missing') return new Response('not found',{status:404});
        if(path==='/robots.txt') return new Response('User-agent: *\nAllow: /\n');
        if(path==='/sitemap.xml') return new Response('<urlset/>',{headers:{'content-type':'application/xml'}});
        return new Response('<html><head><meta name="robots" content="index,follow"><link rel="canonical" href="https://signsky.nalmada.net/"></head><body>Signsky</body></html>',{headers:{'content-type':'text/html; charset=utf-8'}});
      }}
    };
    const r=await worker.fetch(new Request('https://'+host+'/'),env);
    const html=await r.text();
    const isPublic=host==='signsky.nalmada.net';
    assert.equal(r.headers.has('x-robots-tag'),!isPublic);
    if(isPublic){
      assert.match(html,/<meta name="robots" content="index,follow">/);
      assert.match(html,/<link rel="canonical"/);
    }else{
      assert.match(html,/<meta name="robots" content="noindex,nofollow">/);
      assert.doesNotMatch(html,/<link rel="canonical"/);
    }
    const missing=await worker.fetch(new Request('https://'+host+'/missing'),env);
    assert.equal(missing.status,404);
    assert.match(missing.headers.get('x-robots-tag'),/noindex/);
    const sitemap=await worker.fetch(new Request('https://'+host+'/sitemap.xml'),env);
    assert.equal(sitemap.status,isPublic?200:404);
    const robots=await worker.fetch(new Request('https://'+host+'/robots.txt'),env);
    assert.match(await robots.text(),isPublic?/Allow: \///:/Disallow: \//);
  }
});
