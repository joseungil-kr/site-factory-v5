import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/skyquote/worker.dual-host.js';
test('RSS exact host MIME and preview discovery protection',async()=>{
 const env={SKYQUOTE_PUBLIC:'1',ASSETS:{fetch:async()=>new Response('<rss/>')}};
 const pub=await worker.fetch(new Request('https://skyquote.nalmada.net/rss.xml'),env);assert.equal(pub.status,200);assert.match(pub.headers.get('Content-Type'),/application\/rss\+xml/);
 assert.equal((await worker.fetch(new Request('https://sfv5-skyquote-preview.joseungil.workers.dev/rss.xml'),env)).status,404);
 env.ASSETS.fetch=async()=>new Response('<head><meta name="robots" content="index,follow"><link rel="alternate" type="application/rss+xml" href="https://skyquote.nalmada.net/rss.xml"></head>',{headers:{'Content-Type':'text/html'}});
 const preview=await worker.fetch(new Request('https://sfv5-skyquote-preview.joseungil.workers.dev/'),env);const html=await preview.text();assert.ok(html.includes('noindex,nofollow'));assert.ok(!html.includes('application/rss+xml'));
});
