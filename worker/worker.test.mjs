import test from 'node:test';
import assert from 'node:assert/strict';
import adapter from './index.js';

const paths = [];
const env = {
  ASSETS: {
    async fetch(req) {
      const path = new URL(req.url).pathname;
      paths.push(path);
      return new Response(path === '/404-test.html' ? '404' : path, {status:path === '/404-test.html'?404:200});
    }
  }
};
test('root rewrites to index.html and exact .html pages are untouched', async()=>{
  const first = await adapter.fetch(new Request('https://preview.invalid/'),env);
  assert.equal(await first.text(),'/index.html');
  const numbered = await adapter.fetch(new Request('https://preview.invalid/499.html'),env);
  assert.equal(await numbered.text(),'/499.html');
  const missing = await adapter.fetch(new Request('https://preview.invalid/404-test.html'),env);
  assert.equal(missing.status,404);
  assert.deepEqual(paths,['/index.html','/499.html','/404-test.html']);
});

test('opt-in aggregated event accepts only whitelisted same-origin action', async()=>{
  const logged=[];
  const tracked={...env,ANALYTICS:{writeDataPoint(x){logged.push(x);}}};
  const request=new Request('https://preview.invalid/__v5_event',{method:'POST',
    headers:{'Content-Type':'application/json','Origin':'https://preview.invalid'},
    body:JSON.stringify({event:'shop',page:'/2.html'})});
  const reply=await adapter.fetch(request,tracked);
  assert.equal(reply.status,204);
  assert.deepEqual(logged[0].blobs,['shop','/2.html']);
  assert.equal(await adapter.fetch(new Request('https://preview.invalid/__v5_event',{method:'POST',
    headers:{'Content-Type':'application/json','Origin':'https://outsider.invalid'},
    body:JSON.stringify({event:'phone',page:'/'})}),tracked).then(r=>r.status),403);
  const none=await adapter.fetch(new Request('https://preview.invalid/__v5_event',{method:'POST'}),env);
  assert.equal(none.status,404);
});

test('event receiver rejects oversized payload and missing origin', async()=>{
  const tracked={...env,ANALYTICS:{writeDataPoint(){throw new Error('should not be called');}}};
  const oversized=await adapter.fetch(new Request('https://preview.invalid/__v5_event',{
    method:'POST',headers:{'Content-Type':'application/json','Origin':'https://preview.invalid'},
    body:JSON.stringify({event:'phone',page:'/'+ 'x'.repeat(270)})}),tracked);
  assert.equal(oversized.status,413);
  const noOrigin=await adapter.fetch(new Request('https://preview.invalid/__v5_event',{
    method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({event:'phone',page:'/'})}),tracked);
  assert.equal(noOrigin.status,403);
});

test('staging applies HTTP noindex to homepage, numbered HTML and 404', async()=>{
  const staging={...env,V5_STAGING:'1'};
  for(const path of ['/','/2.html','/404-test.html']) {
    const resp=await adapter.fetch(new Request('https://preview.invalid'+path),staging);
    assert.match(resp.headers.get('X-Robots-Tag'),/noindex/);
    assert.equal(resp.headers.get('Cache-Control'),'no-store');
    if(path.includes('404')) assert.equal(resp.status,404);
    else assert.equal(resp.status,200);
  }
});


test('only plants.nalmada.net permits indexing; workers.dev stays noindex',async()=>{
  const staging={...env,V5_STAGING:'1',V5_PUBLIC_HOST:'plants.nalmada.net'};
  const publicPage=await adapter.fetch(new Request('https://plants.nalmada.net/'),staging);
  assert.equal(publicPage.status,200);
  assert.equal(publicPage.headers.get('X-Robots-Tag'),null);
  const preview=await adapter.fetch(new Request('https://sfv5-seoul-gyeonggi-plants-preview.joseungil.workers.dev/'),staging);
  assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);
  const public404=await adapter.fetch(new Request('https://plants.nalmada.net/404-test.html'),staging);
  assert.equal(public404.status,404);
  assert.match(public404.headers.get('X-Robots-Tag'),/noindex/);
  const previewRobots=await adapter.fetch(new Request('https://sfv5-seoul-gyeonggi-plants-preview.joseungil.workers.dev/robots.txt'),staging);
  assert.ok((await previewRobots.text()).includes('Disallow: /'));
});

test('only explicitly approved Daysky hostname is indexable, and preview stays blocked',async()=>{
  const staging={...env,V5_STAGING:'1',V5_PUBLIC_HOST:'daysky.nalmada.net'};
  const launched=await adapter.fetch(new Request('https://daysky.nalmada.net/'),staging);
  assert.equal(launched.status,200);
  assert.equal(launched.headers.get('X-Robots-Tag'),null);
  const preview=await adapter.fetch(new Request('https://sfv5-daysky-preview.joseungil.workers.dev/'),staging);
  assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);
  const previewRobots=await adapter.fetch(new Request('https://sfv5-daysky-preview.joseungil.workers.dev/robots.txt'),staging);
  assert.match(await previewRobots.text(),/Disallow: \//);
});

test('Quicksky home-only public host allows only /; regions and index.html cannot index',async()=>{
  const scoped={...env,V5_STAGING:'1',V5_PUBLIC_HOST:'quicksky.nalmada.net',V5_HOME_ONLY:'1'};
  const homepage=await adapter.fetch(new Request('https://quicksky.nalmada.net/'),scoped);
  assert.equal(homepage.status,200);
  assert.equal(homepage.headers.get('X-Robots-Tag'),null);
  for(const path of ['/2.html','/1733.html','/index.html','/404-test.html']) {
    const reply=await adapter.fetch(new Request('https://quicksky.nalmada.net'+path),scoped);
    assert.match(reply.headers.get('X-Robots-Tag'),/noindex/);
  }
  for(const path of ['/', '/2.html','/robots.txt']) {
    const preview=await adapter.fetch(new Request('https://sfv5-quicksky-preview.joseungil.workers.dev'+path),scoped);
    assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);
    if(path==='/robots.txt') assert.match(await preview.text(),/Disallow: \//);
  }
  const bot=await adapter.fetch(new Request('https://quicksky.nalmada.net/robots.txt'),scoped);
  assert.equal(bot.headers.get('X-Robots-Tag'),null);
  const map=await adapter.fetch(new Request('https://quicksky.nalmada.net/sitemap.xml'),scoped);
  assert.equal(map.headers.get('X-Robots-Tag'),null);
  // Unrecognized sites or mismatched public hostname never become indexable.
  const wrong=await adapter.fetch(new Request('https://daysky.nalmada.net/'),scoped);
  assert.match(wrong.headers.get('X-Robots-Tag'),/noindex/);
});
