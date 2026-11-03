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

for (const host of ['wallsky.nalmada.net','preview.workers.dev']) {
  const r=await worker.fetch(new Request('https://'+host+'/rss.xml'),{WALLSKY_PUBLIC:'1',ASSETS:{fetch:async()=>new Response('<rss/>')}});
  assert.equal(r.status,host==='wallsky.nalmada.net'?200:404);
  if(r.ok)assert.match(r.headers.get('Content-Type'),/application\/rss\+xml/);
}

{
 const env={WALLSKY_PUBLIC:'1',ASSETS:{fetch:async()=>new Response('<head><link rel="alternate" type="application/rss+xml" href="https://wallsky.nalmada.net/rss.xml"></head>',{headers:{'Content-Type':'text/html','ETag':'old','Content-Length':'200'}})}};
 const r=await worker.fetch(new Request('https://preview.workers.dev/'),env);
 assert.ok(!(await r.text()).includes('application/rss+xml'));assert.equal(r.headers.get('Content-Length'),null);assert.equal(r.headers.get('ETag'),null);
}
