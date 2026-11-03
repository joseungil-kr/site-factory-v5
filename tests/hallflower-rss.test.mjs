import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/hallflower/worker.public.js';
test('RSS MIME and preview protection',async()=>{
 const env={HALLFLOWER_PUBLIC:'1',ASSETS:{fetch:async()=>new Response('<rss/>')}};
 const pub=await worker.fetch(new Request('https://hallflower.nalmada.net/rss.xml'),env);assert.equal(pub.status,200);assert.match(pub.headers.get('Content-Type'),/application\/rss\+xml/);
 const preview=await worker.fetch(new Request('https://preview.workers.dev/rss.xml'),env);assert.equal(preview.status,404);assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);
});
