import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/wreath-region/worker.js';
test('wreath preview is isolated and noindex; only exact approved production host is indexable',async()=>{
  for(const [host,flag,blocked] of [
    ['wreath.nalmada.net','0',true],
    ['wreath.nalmada.net','1',false],
    ['sfv52-wreath-preview.joseungil.workers.dev','1',true],
    ['quicksky.nalmada.net','1',true]]) {
    let requested='';
    let env={WREATH_PUBLIC:flag,ASSETS:{fetch:async r=>{requested=new URL(r.url).pathname;return new Response('ok',{status:200})}}};
    let r=await worker.fetch(new Request('https://'+host+'/'),env);
    assert.equal(requested,'/index.html');
    assert.equal(r.headers.has('X-Robots-Tag'),blocked);
    r=await worker.fetch(new Request('https://'+host+'/robots.txt'),env);
    assert.equal(r.headers.has('X-Robots-Tag'),blocked);
    r=await worker.fetch(new Request('https://'+host+'/sitemap.xml'),env);
    assert.equal(r.status,blocked?404:200);
    env.ASSETS.fetch=async()=>new Response('not found',{status:404});
    r=await worker.fetch(new Request('https://'+host+'/not-real'),env);
    assert.equal(r.status,404);
    assert.match(r.headers.get('X-Robots-Tag'),/noindex/);
  }
});
