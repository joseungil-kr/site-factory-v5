import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/officeplant/worker.js';
for (const [host, mode, expected] of [['officeplant.nalmada.net','1',false],['officeplant.nalmada.net','0',true],['sfv52-officeplant.test.workers.dev','1',true],['plants.nalmada.net','1',true]]) {
  test(`${host} public=${mode}`, async () => {
    let seen;
    const env={OFFICEPLANT_PUBLIC:mode,ASSETS:{fetch:async request=>{seen=new URL(request.url).pathname;return new Response('ok')}}};
    const res=await worker.fetch(new Request(`https://${host}/`),env);
    assert.equal(seen,'/index.html');
    assert.equal(res.headers.has('X-Robots-Tag'),expected);
    const map=await worker.fetch(new Request(`https://${host}/sitemap.xml`),env);
    assert.equal(map.status,expected?404:200);
  });
}
test('404 is never indexed',async()=>{
  const response=await worker.fetch(new Request('https://officeplant.nalmada.net/missing'),{OFFICEPLANT_PUBLIC:'1',ASSETS:{fetch:async()=>new Response('missing',{status:404})}});
  assert.equal(response.status,404);assert.match(response.headers.get('X-Robots-Tag'),/noindex/);
});