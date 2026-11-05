import test from "node:test";
import assert from "node:assert/strict";
import worker,{PUBLIC_HOST,PREVIEW_HOST,INDEXNOW_KEY} from "../sites/baekse/worker-public.js";

const ROOT="https://baekse.nalmada.net";
const doc=(route,label)=>'<!doctype html><html lang="ko"><head><meta name="robots" content="index,follow"><link rel="canonical" href="'+ROOT+route+'"></head><body><h1>'+label+'</h1><a href="tel:0314070103">상담</a></body></html>';
const assets=new Map([
 ["/index.html",[200,doc("/","백세푸드"),"text/html"]],
 ["/c/abcdef123456.html",[200,doc("/c/abcdef123456.html","수원시"),"text/html"]],
 ["/r/abcdef123456-dakhanmari.html",[200,doc("/r/abcdef123456-dakhanmari.html","수원시 닭한마리"),"text/html"]],
 ["/m/dakhanmari.html",[200,doc("/m/dakhanmari.html","닭한마리"),"text/html"]],
 ["/robots.txt",[200,"User-agent: *\nAllow: /\nSitemap: https://baekse.nalmada.net/sitemap.xml\n","text/plain"]],
 ["/sitemap.xml",[200,'<?xml version="1.0"?><urlset><url><loc>'+ROOT+'/</loc></url></urlset>',"application/xml"]],
 ["/"+INDEXNOW_KEY+".txt",[200,INDEXNOW_KEY+"\n","text/plain"]]
]);
const env={ASSETS:{async fetch(req){
 const path=new URL(req.url).pathname;
 const found=assets.get(path);
 if(!found)return new Response("Not found",{status:404});
 return new Response(found[1],{status:found[0],headers:{"Content-Type":found[2]}});
}}};
const hit=(host,path="/")=>worker.fetch(new Request("https://"+host+path),env);

test("public host keeps each menu, city and city-menu page indexable with self canonical",async()=>{
 for(const path of ["/","/m/dakhanmari.html","/c/abcdef123456.html","/r/abcdef123456-dakhanmari.html"]){
  const response=await hit(PUBLIC_HOST,path),html=await response.text();
  assert.equal(response.status,200);
  assert.equal(response.headers.get("X-Robots-Tag"),null);
  assert.ok(html.includes('<meta name="robots" content="index,follow">'));
  assert.ok(html.includes('<link rel="canonical" href="'+ROOT+path+'">'));
  assert.ok(html.includes("tel:0314070103"));
 }
});
test("workers.dev preview transforms all page kinds to noindex and removes self canonical",async()=>{
 for(const path of ["/","/m/dakhanmari.html","/c/abcdef123456.html","/r/abcdef123456-dakhanmari.html"]){
  const response=await hit(PREVIEW_HOST,path),html=await response.text();
  assert.equal(response.status,200);
  assert.match(response.headers.get("X-Robots-Tag"),/noindex/);
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
  assert.ok(!html.includes('rel="canonical"'));
 }
});
test("preview excludes public sitemap and ownership key, with robots disallow",async()=>{
 const res=await hit(PREVIEW_HOST,"/robots.txt");
 assert.equal(res.status,200);
 assert.match(await res.text(),/Disallow: \//);
 for(const path of ["/sitemap.xml","/"+INDEXNOW_KEY+".txt"]){
  const status=await hit(PREVIEW_HOST,path);
  assert.equal(status.status,404);
  assert.match(status.headers.get("X-Robots-Tag"),/noindex/);
  assert.equal((await hit(PUBLIC_HOST,path)).status,200);
 }
 assert.match(await (await hit(PUBLIC_HOST,"/robots.txt")).text(),/Allow: \//);
});
test("unknown hosts, missing URLs and unsafe HTTP methods fail closed",async()=>{
 for(const [host,path]of [["random.example.com","/"],[PUBLIC_HOST,"/missing.html"],[PREVIEW_HOST,"/missing.html"]]){
  const r=await hit(host,path);
  assert.equal(r.status,404);
  assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
 }
 const bad=await worker.fetch(new Request(ROOT+"/",{method:"POST"}),env);
 assert.equal(bad.status,405);
});
test("preview fails closed if static HTML loses exact public index or canonical",async()=>{
 const broken='<html><head><meta name="robots" content="index,follow"><link rel="canonical" href="https://wrong.example.com/"></head></html>';
 const e={ASSETS:{async fetch(){return new Response(broken,{status:200,headers:{"Content-Type":"text/html"}})}}};
 const r=await worker.fetch(new Request("https://"+PREVIEW_HOST+"/"),e);
 assert.equal(r.status,503);
 assert.match(r.headers.get("X-Robots-Tag"),/noindex/);
});
