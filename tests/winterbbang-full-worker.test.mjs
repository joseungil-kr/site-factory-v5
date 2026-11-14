import test from "node:test";
import assert from "node:assert/strict";
import worker, { PUBLIC_HOST, PREVIEW_HOST, INDEXNOW_KEY, stripPublicSEO } from "../sites/winterbbang/worker-full-public.js";

const ORIGIN = "https://winterbbang.nalmada.net";
const baseHTML=(route,label)=>'<!doctype html><html lang="ko"><head><meta name="robots" content="index,follow"><link rel="canonical" href="'+ORIGIN+route+'"></head><body><h1>'+label+'</h1><a href="tel:0314070103">창업상담</a></body></html>';
const samples=new Map([
 ["/index.html",[200,baseHTML("/","백세푸드"),"text/html; charset=utf-8"]],
 ["/r/abc123.html",[200,baseHTML("/r/abc123.html","서울 강남구 역삼동"),"text/html; charset=utf-8"]],
 ["/d/def456.html",[200,baseHTML("/d/def456.html","강남구 지역 허브"),"text/html; charset=utf-8"]],
 ["/p/pqr789.html",[200,baseHTML("/p/pqr789.html","서울 지역 허브"),"text/html; charset=utf-8"]],
 ["/sitemap.xml",[200,'<?xml version="1.0"?><urlset><url><loc>'+ORIGIN+'/</loc></url></urlset>',"application/xml"]],
 ["/robots.txt",[200,"User-agent: *\nAllow: /\nSitemap: "+ORIGIN+"/sitemap.xml\n","text/plain"]],
 ["/"+INDEXNOW_KEY+".txt",[200,INDEXNOW_KEY+"\n","text/plain"]],
 ["/assets/images/hero.webp",[200,"fake-image-body-for-unit-test","image/webp"]],
]);
const env={ASSETS:{async fetch(req){
  const p=new URL(req.url).pathname;
  const row=samples.get(p);
  if (!row) return new Response("Not found",{status:404});
  return new Response(row[1],{status:row[0],headers:{"Content-Type":row[2]}});
}}};
const hit=(host,path="/")=>worker.fetch(new Request("https://"+host+path),env);

test("public home and all three regional hierarchies are indexable and keep exact canonical",async()=>{
  for(const path of ["/","/r/abc123.html","/d/def456.html","/p/pqr789.html"]){
    const res=await hit(PUBLIC_HOST,path),body=await res.text();
    const canonical=path==="/" ? ORIGIN+"/":ORIGIN+path;
    assert.equal(res.status,200);
    assert.equal(res.headers.get("X-Robots-Tag"),null);
    assert.ok(body.includes('<meta name="robots" content="index,follow">'));
    assert.ok(body.includes('<link rel="canonical" href="'+canonical+'">'));
    assert.ok(body.includes("tel:0314070103"));
  }
});
test("all 1804 HTML paths in workers.dev are transformed to noindex and no canonical",async()=>{
  for(const path of ["/","/r/abc123.html","/d/def456.html","/p/pqr789.html"]){
    const res=await hit(PREVIEW_HOST,path),body=await res.text();
    assert.equal(res.status,200);
    assert.match(res.headers.get("X-Robots-Tag"),/noindex/);
    assert.ok(body.includes('<meta name="robots" content="noindex,nofollow">'));
    assert.ok(!body.includes('rel="canonical"'));
  }
});
test("robots sitemap and IndexNow key exist only on exact public hostname",async()=>{
  let x=await hit(PUBLIC_HOST,"/robots.txt");
  assert.match(await x.text(),/Allow: \//);
  x=await hit(PREVIEW_HOST,"/robots.txt");
  assert.match(await x.text(),/Disallow: \//);
  assert.match(x.headers.get("X-Robots-Tag"),/noindex/);
  for(const p of ["/sitemap.xml","/"+INDEXNOW_KEY+".txt"]){
    assert.equal((await hit(PUBLIC_HOST,p)).status,200);
    const res=await hit(PREVIEW_HOST,p);
    assert.equal(res.status,404);
    assert.match(res.headers.get("X-Robots-Tag"),/noindex/);
  }
});
test("404, 405 and unknown hosts fail-closed with noindex",async()=>{
  for(const [host,path] of [[PUBLIC_HOST,"/missing.html"],[PREVIEW_HOST,"/missing.html"],["other.example.com","/"]]){
    const r=await hit(host,path);
    assert.equal(r.status,404);
    assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
  }
  const r=await worker.fetch(new Request(ORIGIN+"/",{method:"POST"}),env);
  assert.equal(r.status,405);
});
test("mismatched public SEO markup fails closed on preview instead of leaking index",async()=>{
  assert.throws(()=>stripPublicSEO("<html><meta name='robots' content='noindex'></html>"));
  const malicious='<html><head><meta name="robots" content="index,follow"><link rel="canonical" href="https://wrong.example.com/x"></head></html>';
  assert.throws(()=>stripPublicSEO(malicious));
});
test("all public routes stay on one host and references never rewrite to external site",async()=>{
  for(const p of ["/r/abc123.html","/d/def456.html","/p/pqr789.html"]){
    const data=await (await hit(PUBLIC_HOST,p)).text();
    assert.ok(!data.includes(PREVIEW_HOST));
    assert.ok(!data.includes("href=\"http://"));
  }
});
