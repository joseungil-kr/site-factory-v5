import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './index.js';
const host='quicksky.nalmada.net';
const env={V5_STAGING:'1',V5_PUBLIC_HOST:host,V5_HOME_ONLY:'0',ASSETS:{fetch:async()=>new Response('<rss/>',{headers:{'Content-Type':'application/xml'}})}};
test('RSS is served only on exact public host with proper MIME',async()=>{
  const publicFeed=await worker.fetch(new Request('https://'+host+'/rss.xml'),env);
  assert.equal(publicFeed.status,200);
  assert.equal(publicFeed.headers.get('Content-Type'),'application/rss+xml; charset=utf-8');
  for(const other of ['test.workers.dev','unapproved.nalmada.net']){
    const feed=await worker.fetch(new Request('https://'+other+'/rss.xml'),env);
    assert.equal(feed.status,404);
    assert.match(feed.headers.get('X-Robots-Tag'),/noindex/);
  }
});