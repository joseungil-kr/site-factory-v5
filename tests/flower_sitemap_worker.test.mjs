import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const script=readFileSync('worker/index.js','utf8');
const {default:worker}=await import('data:text/javascript;base64,'+Buffer.from(script).toString('base64'));
const halls=Array.from({length:1080},(_,i)=>({
  n:'장례식장 '+i, r:'경기도',u:'/fh-'+i.toString(16).padStart(20,'0')+'.html'
}));
const env={
  V5_STAGING:'1',
  V5_PUBLIC_HOST:'flower.nalmada.net',
  FLOWER_INDEXNOW_KEY:'a8268664ba94ac17777f7d37683b253b',
  ASSETS:{
    fetch:async req=>{
      const path=new URL(req.url).pathname;
      if(path==='/halls.json')
        return new Response(JSON.stringify(halls),{status:200,headers:{'Content-Type':'application/json'}});
      return new Response('Not found',{status:404});
    }
  }
};
const live=await worker.fetch(new Request('https://flower.nalmada.net/sitemap.xml'),env);
assert.equal(live.status,200);
assert.match(live.headers.get('content-type'),/application\/xml/);
const xml=await live.text();
assert.equal((xml.match(/<loc>/g)||[]).length,1081);
assert.match(xml,/<loc>https:\/\/flower.nalmada.net\/<\/loc>/);
assert.match(xml,/<loc>https:\/\/flower.nalmada.net\/fh-00000000000000000000.html<\/loc>/);

const head=await worker.fetch(new Request('https://flower.nalmada.net/sitemap.xml',{method:'HEAD'}),env);
assert.equal(head.status,200);
assert.equal(await head.text(),'');

const robots=await worker.fetch(new Request('https://flower.nalmada.net/robots.txt'),env);
assert.equal(robots.status,200);
const robotsText=await robots.text();
assert.match(robotsText,/Allow: \//);
assert.match(robotsText,/Sitemap: https:\/\/flower.nalmada.net\/sitemap.xml/);
assert.doesNotMatch(robotsText,/Disallow: \//);
const proof=await worker.fetch(new Request('https://flower.nalmada.net/a8268664ba94ac17777f7d37683b253b.txt'),env);
assert.equal(proof.status,200);
assert.equal(await proof.text(),'a8268664ba94ac17777f7d37683b253b');

const preview=await worker.fetch(new Request('https://sfv5-nalmada-flower-preview.joseungil.workers.dev/sitemap.xml'),env);
assert.equal(preview.status,404);
assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);

const other=await worker.fetch(new Request('https://daysky.nalmada.net/sitemap.xml'),env);
assert.equal(other.status,404);
assert.match(other.headers.get('X-Robots-Tag'),/noindex/);

const wrongHalls=[...halls,{n:'Extra',r:'',u:'/fh-00000000000000000000.html'}];
const invalidEnv={...env,ASSETS:{fetch:async()=>new Response(JSON.stringify(wrongHalls),{status:200})}};
const malformed=await worker.fetch(new Request('https://flower.nalmada.net/sitemap.xml'),invalidEnv);
assert.equal(malformed.status,503);

console.log('FLOWER_1081_SITEMAP_WORKER_TEST_PASSED: exact host, 1080 input, 1081 XML URLs, preview noindex');
