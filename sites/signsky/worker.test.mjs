import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './worker.mjs';
test('only exact approved host can be indexable; missing assets remain 404',async()=>{
  for(const host of ['signsky.nalmada.net','sfv52-signsky.workers.dev','other.nalmada.net']){
    const env={SIGNSKY_PUBLIC:'1',ASSETS:{fetch:async req=>new Response(new URL(req.url).pathname,{status:new URL(req.url).pathname==='/missing'?404:200})}};
    const r=await worker.fetch(new Request('https://'+host+'/'),env);
    assert.equal(r.headers.has('x-robots-tag'),host!=='signsky.nalmada.net');
    const missing=await worker.fetch(new Request('https://'+host+'/missing'),env);
    assert.equal(missing.status,404);assert.match(missing.headers.get('x-robots-tag'),/noindex/);
    const sitemap=await worker.fetch(new Request('https://'+host+'/sitemap.xml'),env);
    assert.equal(sitemap.status,host==='signsky.nalmada.net'?200:404);
  }
});
