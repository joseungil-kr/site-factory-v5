import test from 'node:test';
import assert from 'node:assert/strict';
import worker,{PUBLIC_HOST,PREVIEW_HOST,stripPublicSEO} from '../sites/winterbbang/worker-full-public.js';
test('RSS exact host MIME and preview isolation',async()=>{
 const env={ASSETS:{fetch:async()=>new Response('<rss/>')}};
 const pub=await worker.fetch(new Request('https://'+PUBLIC_HOST+'/rss.xml'),env);
 assert.equal(pub.status,200);assert.match(pub.headers.get('Content-Type'),/application\/rss\+xml/);
 assert.equal((await worker.fetch(new Request('https://'+PREVIEW_HOST+'/rss.xml'),env)).status,404);
 const html='<head><meta name="robots" content="index,follow"><link rel="canonical" href="https://winterbbang.nalmada.net/"><link rel="alternate" type="application/rss+xml" href="https://winterbbang.nalmada.net/rss.xml"></head>';
 assert.ok(!stripPublicSEO(html).includes('application/rss+xml'));
});
