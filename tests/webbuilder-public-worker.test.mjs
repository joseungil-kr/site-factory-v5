import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../sites/webbuilder/worker.public.js';
const env = {ASSETS: {fetch: async request => {
  const path = new URL(request.url).pathname;
  return new Response('<meta name="robots" content="index,follow"><link rel="canonical" href="https://webbuilder.nalmada.net/">page',
    {status: path === '/unknown/index.html' ? 404 : 200, headers: {'Content-Type':'text/html'}});
}}};
test('public host indexes only successful content, 404 stays actual 404', async () => {
  for (const path of ['/', '/404.html', '/unknown/']) {
    const r = await worker.fetch(new Request('https://webbuilder.nalmada.net'+path), env);
    assert.equal(r.status, path === '/' ? 200 : 404);
    assert.equal(r.headers.get('X-Robots-Tag').includes('noindex'), path !== '/');
  }
});
test('workers.dev remains blocked even with public assets', async () => {
  const r = await worker.fetch(new Request('https://test.workers.dev/'), env);
  const html = await r.text();
  assert.match(html, /noindex/);
  assert.doesNotMatch(html, /canonical/);
  assert.match(r.headers.get('X-Robots-Tag'), /noindex/);
  for (const path of ['/robots.txt','/sitemap.xml','/rss.xml']) {
    const response = await worker.fetch(new Request('https://test.workers.dev'+path), env);
    assert.equal(response.status, path === '/robots.txt' ? 200 : 404);
    assert.match(await response.text(), /Disallow: \//);
  }
});

test('RSS keeps correct MIME on the public host only', async () => {
  const r = await worker.fetch(new Request('https://webbuilder.nalmada.net/rss.xml'), env);
  assert.equal(r.status, 200);
  assert.equal(r.headers.get('Content-Type'), 'application/rss+xml; charset=utf-8');
});
