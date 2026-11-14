import assert from 'node:assert/strict';
import worker from '../sites/wallsky/worker.js';
for (const [host,flag,expected] of [['wallsky.nalmada.net','1',false],['wallsky.nalmada.net','0',true],['sfv52-wallsky.example.workers.dev','1',true],['daysky.nalmada.net','1',true]]) {
  let path;
  const env={WALLSKY_PUBLIC:flag,ASSETS:{fetch:async req=>{path=new URL(req.url).pathname;return new Response('asset:'+path);}}};
  let r=await worker.fetch(new Request('https://'+host+'/'),env);
  assert.equal(path,'/index.html');assert.equal(await r.text(),'asset:/index.html');assert.equal(r.headers.has('X-Robots-Tag'),expected);
  r=await worker.fetch(new Request('https://'+host+'/2.html'),env);
  assert.equal(path,'/2.html');assert.equal(await r.text(),'asset:/2.html');assert.equal(r.headers.has('X-Robots-Tag'),expected);
  r=await worker.fetch(new Request('https://'+host+'/robots.txt'),env);
  assert.equal(r.headers.has('X-Robots-Tag'),expected);
  env.ASSETS.fetch=async()=>new Response('missing',{status:404});
  r=await worker.fetch(new Request('https://'+host+'/missing'),env);
  assert.equal(r.status,404);assert.match(r.headers.get('X-Robots-Tag'),/noindex/);
}
console.log('Wallsky host isolation, root, robots and 404: passed');
