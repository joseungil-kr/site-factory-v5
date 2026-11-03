import test from 'node:test';
import assert from 'node:assert/strict';
import {createSharedWorker} from './shared-static.js';

const hosts = {'ansanwreath.fwith.kr': {id: 'ansan', paths: ['/index.html', '/404.html', '/2.html', '/배송.html']},
  'seoulwreath.fwith.kr': {id: 'seoul', paths: ['/index.html', '/404.html']}};
const worker = createSharedWorker(hosts);
function env() {
  const calls = [];
  return {calls, ASSETS: {fetch: async r => {
    calls.push(r.url); return new Response(new URL(r.url).pathname);
  }}};
}
test('home, numbered and unicode paths dispatch only within the requested host', async () => {
  for (const [host, id] of [['ansanwreath.fwith.kr', 'ansan'], ['seoulwreath.fwith.kr', 'seoul']]) {
    const e = env();
    const response = await worker.fetch(new Request(`https://${host}/?q=ignored`), e);
    assert.equal(await response.text(), `/_sfv5/sites/${id}/index.html`);
    assert.match(response.headers.get('X-Robots-Tag'), /noindex/);
    assert.equal(new URL(e.calls[0]).search, '');
  }
  const e = env();
  assert.equal((await worker.fetch(new Request('https://ansanwreath.fwith.kr/2.html'), e)).status, 200);
  assert.equal((await worker.fetch(new Request('https://ansanwreath.fwith.kr/%EB%B0%B0%EC%86%A1.html'), e)).status, 200);
});
test('unknown host, private paths, events, invalid paths and methods fail closed', async () => {
  for (const [host, path, method] of [
    ['wreath.fwith.kr', '/', 'GET'], ['preview.workers.dev', '/', 'GET'],
    ['ansanwreath.fwith.kr', '/_sfv5/sites/seoul/index.html', 'GET'],
    ['ansanwreath.fwith.kr', '/%5fsfv5/sites/seoul/index.html', 'GET'],
    ['ansanwreath.fwith.kr', '/%ZZ', 'GET'],
    ['ansanwreath.fwith.kr', '/__v5_event', 'POST'],
    ['ansanwreath.fwith.kr', '/sitemap.xml', 'GET'],
    ['ansanwreath.fwith.kr', '/', 'POST']]) {
    const e = env();
    assert.equal((await worker.fetch(new Request(`https://${host}${path}`, {method}), e)).status, 404);
    assert.equal(e.calls.length, 0);
  }
});
test('host-local 404, HEAD and noindex robots', async () => {
  const e = env();
  const missing = await worker.fetch(new Request('https://seoulwreath.fwith.kr/2.html'), e);
  assert.equal(missing.status, 404);
  assert.match(await missing.text(), /sites\/seoul\/404.html/);
  const head = await worker.fetch(new Request('https://ansanwreath.fwith.kr/', {method: 'HEAD'}), e);
  assert.equal(await head.text(), '');
  const robots = await worker.fetch(new Request('https://ansanwreath.fwith.kr/robots.txt'), e);
  assert.match(await robots.text(), /Disallow: \//);
});
