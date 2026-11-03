import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/todayflower-nalmada/worker.public-rss.mjs';

test('existing public-host rendering adds discovery without exposing preview RSS', async()=>{
  const html='<html><head><meta name="robots" content="noindex,nofollow"></head><body><main><h1>Complete article</h1></main></body></html>';
  const env={ASSETS:{fetch:async request=>new Response(new URL(request.url).pathname==='/rss.xml'?'<rss/>':html,{headers:{'Content-Type':'text/html'}})}};
  const page=await worker.fetch(new Request('https://todayflower.nalmada.net/'),env);
  const text=await page.text();
  assert.equal(page.status,200);
  assert.ok(text.includes('rel="canonical" href="https://todayflower.nalmada.net/"'));
  assert.ok(text.includes('d970eeb70abc7b36cbcc02fadd9362c5c57fcb46'));
  assert.ok(text.includes('application/rss+xml'));
  assert.ok(text.includes('<h1>Complete article</h1>'));
  const feed=await worker.fetch(new Request('https://todayflower.nalmada.net/rss.xml'),env);
  assert.equal(feed.status,200);assert.match(feed.headers.get('Content-Type'),/application\/rss\+xml/);
  const preview=await worker.fetch(new Request('https://sfv56-todayflower-preview.joseungil.workers.dev/rss.xml'),env);
  assert.equal(preview.status,404);assert.match(preview.headers.get('X-Robots-Tag'),/noindex/);
  const previewPage=await worker.fetch(new Request('https://sfv56-todayflower-preview.joseungil.workers.dev/'),env);
  assert.equal(await previewPage.text(),html);
  assert.match(previewPage.headers.get('X-Robots-Tag'),/noindex/);
});
