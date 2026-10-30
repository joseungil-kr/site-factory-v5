import test from "node:test";
import assert from "node:assert/strict";
import worker, { PUBLIC_HOST, PREVIEW_HOST, OWNERSHIP_KEY } from "../sites/winterbbang/worker-home-public.js";

const publicHome = '<!doctype html><html lang="ko"><head><meta name="robots" content="index,follow"><link rel="canonical" href="https://winterbbang.nalmada.net/"></head><body><h1>백세푸드</h1><a href="tel:0314070103">전화</a></body></html>';
const region = '<!doctype html><html lang="ko"><head><meta name="robots" content="noindex,nofollow"></head><body>역삼동</body></html>';
const staticFiles = new Map([
  ["/index.html", [200, publicHome, "text/html; charset=utf-8"]],
  ["/r/example.html", [200, region, "text/html; charset=utf-8"]],
  ["/sitemap.xml", [200, '<?xml version="1.0"?><urlset><url><loc>https://winterbbang.nalmada.net/</loc></url></urlset>', "application/xml"]],
  ["/robots.txt", [200, "User-agent: *\nAllow: /\nSitemap: https://winterbbang.nalmada.net/sitemap.xml\n", "text/plain"]],
  ["/" + OWNERSHIP_KEY + ".txt", [200, OWNERSHIP_KEY + "\n", "text/plain"]],
]);
const env = {
  ASSETS: { async fetch(request) {
    const row = staticFiles.get(new URL(request.url).pathname);
    if (!row) return new Response("Missing", {status:404,headers:{"Content-Type":"text/plain"}});
    return new Response(row[1], {status:row[0],headers:{"Content-Type":row[2]}});
  }},
};
async function fetchHost(host,path="/") {
  return worker.fetch(new Request("https://" + host + path),env);
}
test("public homepage is indexable with self canonical and no noindex header",async()=>{
  const r=await fetchHost(PUBLIC_HOST);
  const body=await r.text();
  assert.equal(r.status,200);
  assert.equal(r.headers.get("X-Robots-Tag"),null);
  assert.match(body,/meta name="robots" content="index,follow"/);
  assert.match(body,/rel="canonical" href="https:\/\/winterbbang.nalmada.net\/"/);
});
test("preview homepage is noindex in header and html with no canonical",async()=>{
  const r=await fetchHost(PREVIEW_HOST);
  const body=await r.text();
  assert.equal(r.status,200);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  assert.match(body,/meta name="robots" content="noindex,nofollow"/);
  assert.doesNotMatch(body,/rel="canonical"/);
});
test("locality on custom domain remains noindex",async()=>{
  const r=await fetchHost(PUBLIC_HOST,"/r/example.html");
  assert.equal(r.status,200);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  assert.match(await r.text(),/noindex,nofollow/);
});
test("custom domain robots and sitemap are public but preview keeps them closed",async()=>{
  let r=await fetchHost(PUBLIC_HOST,"/robots.txt");
  assert.match(await r.text(),/Allow: \//);
  r=await fetchHost(PREVIEW_HOST,"/robots.txt");
  assert.match(await r.text(),/Disallow: \//);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  r=await fetchHost(PREVIEW_HOST,"/sitemap.xml");
  assert.equal(r.status,404);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  r=await fetchHost(PUBLIC_HOST,"/sitemap.xml");
  assert.equal(r.status,200);
});
test("IndexNow public key visible only on owned host",async()=>{
  let r=await fetchHost(PUBLIC_HOST,"/"+OWNERSHIP_KEY+".txt");
  assert.equal(r.status,200);
  assert.equal(await r.text(),OWNERSHIP_KEY+"\n");
  r=await fetchHost(PREVIEW_HOST,"/"+OWNERSHIP_KEY+".txt");
  assert.equal(r.status,404);
});
test("unrecognized host, missing page and wrong method fail closed",async()=>{
  let r=await fetchHost("wrong.example.com");
  assert.equal(r.status,404);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  r=await fetchHost(PUBLIC_HOST,"/does-not-exist.html");
  assert.equal(r.status,404);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  r=await worker.fetch(new Request("https://"+PUBLIC_HOST+"/",{method:"POST"}),env);
  assert.equal(r.status,405);
});
