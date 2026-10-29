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
test('preview HTML metadata is rewritten but public HTML metadata is preserved',async()=>{
  const old=globalThis.HTMLRewriter;
  globalThis.HTMLRewriter=class {
    constructor(){this.handlers=[];}
    on(selector,handler){this.handlers.push({selector,handler});return this;}
    transform(response){
      const handlers=this.handlers;
      return response.text().then(body=>{
        let out=body;
        if(handlers.some(x=>x.selector==='head link[rel="canonical"]'))out=out.replace(/<link\s+rel="canonical"[^>]*>/gi,'');
        if(handlers.some(x=>x.selector==='head meta[name="robots"]'))out=out.replace(/(<meta\s+name="robots"\s+content=")[^"]*(")/i,'$1noindex,nofollow$2');
        return new Response(out,{status:response.status,headers:response.headers});
      });
    }
  };
  try {
    const html='<html><head><meta name="robots" content="index,follow"><link rel="canonical" href="https://wreath.nalmada.net/r/x"></head><body>ok</body></html>';
    const env={WREATH_PUBLIC:'1',ASSETS:{fetch:async()=>new Response(html,{status:200,headers:{'Content-Type':'text/html; charset=utf-8'}})}};
    const preview=await worker.fetch(new Request('https://sfv52-wreath-preview.joseungil.workers.dev/r/x'),env);
    const previewHtml=await preview.text();
    assert.match(previewHtml,/name="robots" content="noindex,nofollow"/);
    assert.doesNotMatch(previewHtml,/rel="canonical"/);
    assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);
    const publicResponse=await worker.fetch(new Request('https://wreath.nalmada.net/r/x'),env);
    const publicHtml=await publicResponse.text();
    assert.match(publicHtml,/name="robots" content="index,follow"/);
    assert.match(publicHtml,/rel="canonical" href="https:\/\/wreath.nalmada.net\/r\/x"/);
    assert.equal(publicResponse.headers.has('X-Robots-Tag'),false);
  } finally {
    if(old===undefined)delete globalThis.HTMLRewriter;else globalThis.HTMLRewriter=old;
  }
});

test('Naver ownership response is served only on exact approved host/path for GET and HEAD',async()=>{
  const host='wreath.nalmada.net';
  const path='/naverc0fb6c053d93d541062de1835c25f51c.html';
  const expected='naver-site-verification: naverc0fb6c053d541062de1835c25f51c.html';
  let assetCalls=0;
  const env={WREATH_PUBLIC:'1',ASSETS:{fetch:async()=>{assetCalls++;return new Response('asset fallback',{status:404})}}};
  const get=await worker.fetch(new Request('https://'+host+path),env);
  assert.equal(get.status,200);
  assert.equal(await get.text(),expected);
  assert.equal(get.headers.get('Content-Type'),'text/html; charset=utf-8');
  const head=await worker.fetch(new Request('https://'+host+path,{method:'HEAD'}),env);
  assert.equal(head.status,200);
  assert.equal(await head.text(),'');
  const wrongPath=await worker.fetch(new Request('https://'+host+path+'x'),env);
  assert.equal(wrongPath.status,404);
  const preview=await worker.fetch(new Request('https://sfv52-wreath-preview.joseungil.workers.dev'+path),env);
  assert.equal(preview.status,404);
  assert.equal(assetCalls,2);
});
