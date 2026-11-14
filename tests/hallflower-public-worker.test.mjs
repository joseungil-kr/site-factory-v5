import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/hallflower/worker.public.js';
const assetResponse=(path)=>new Response(path==='/index.html'?'<!doctype html><title>Hallflower</title>':'asset',{status:path.includes('missing')?404:200,headers:{'Content-Type':'text/plain'}});
test('preview robots.txt uses exactly two LF-terminated directives',async()=>{
  const response=await worker.fetch(new Request('https://sfv53-hallflower.joseungil.workers.dev/robots.txt'),{HALLFLOWER_PUBLIC:'0',ASSETS:{fetch:async()=>assetResponse('/robots.txt')}});
  assert.equal(response.status,200);
  const text=await response.text();
  assert.equal(text,'User-agent: *\nDisallow: /\n');
  assert.equal((text.match(/\n/g)||[]).length,2);
  assert.equal((text.match(/\r/g)||[]).length,0);
  assert.match(response.headers.get('X-Robots-Tag'),/noindex/);
});
test('preview sitemap remains 404 and noindex',async()=>{
  const response=await worker.fetch(new Request('https://sfv53-hallflower.joseungil.workers.dev/sitemap.xml'),{HALLFLOWER_PUBLIC:'0',ASSETS:{fetch:async()=>assetResponse('/sitemap.xml')}});
  assert.equal(response.status,404);
  assert.match(response.headers.get('X-Robots-Tag'),/noindex/);
});
test('indexing cannot be enabled on workers.dev hostname',async()=>{
  const response=await worker.fetch(new Request('https://sfv53-hallflower.joseungil.workers.dev/'),{HALLFLOWER_PUBLIC:'1',ASSETS:{fetch:async()=>assetResponse('/index.html')}});
  assert.equal(response.status,200);
  assert.match(response.headers.get('X-Robots-Tag'),/noindex/);
});
