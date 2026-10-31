#!/usr/bin/env python3
"""Promote the 430 fully tested Baekse city-only HTML pages to an indexable candidate.
Pure local file transformation. No DNS, auth, Cloudflare, or IndexNow actions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET
from scripts import build_baekse_cities as site

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"dist/baekse"
DEST=ROOT/"dist/baekse-public"
REPORT=ROOT/"reports/baekse/public-release.json"
HOST="https://baekse.nalmada.net"
KEYFILE=site.SITE/"indexnow-key.txt"
MENUS=site.MENUS

def render(source=SOURCE,dest=DEST,report=REPORT):
    manifest=json.loads((site.REPORT/"manifest.json").read_text(encoding="utf-8"))
    quality=json.loads((site.REPORT/"audit.json").read_text(encoding="utf-8"))
    spec=json.loads((site.SITE/"site-spec.json").read_text(encoding="utf-8"))
    assert spec["approved"] and spec["targetPageCount"]==430
    assert spec["domain"]==HOST
    assert quality["status"]=="PASS" and quality["sitePages"]==430
    assert quality["internalBrokenLinks"]==0 and quality["uniqueTitles"]==quality["uniqueDescriptions"]==430
    assert quality["similarity"]["passed"] and quality["similarity"]["max"]["value"]<0.49
    assert len(quality["imagesCopiedAndShaVerified"])==5
    assert len(manifest["pages"])==430
    if dest.resolve()==source.resolve() or dest.resolve() in (ROOT,site.SITE,ROOT/"sites"):
        raise ValueError("Unsafe output directory")
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(source,dest)
    urls=[]
    indexable=0
    for route in manifest["pages"]:
        item=dest/("index.html" if route=="/" else route.lstrip("/"))
        body=item.read_text(encoding="utf-8")
        old='<meta name="robots" content="noindex,nofollow">'
        canonical=HOST+route
        assert body.count(old)==1 and 'rel="canonical"' not in body
        meta='<meta name="robots" content="index,follow"><link rel="canonical" href="'+escape(canonical,quote=True)+'">'
        body=body.replace(old,meta,1)
        assert body.count('rel="canonical"')==1
        assert body.count('<meta name="robots" content="index,follow">')==1
        assert '<meta name="robots" content="noindex,nofollow">' not in body
        assert 'tel:0314070103' in body
        item.write_text(body,encoding="utf-8",newline="\n")
        urls.append(canonical)
        indexable+=1
    assert indexable==430 and len(set(urls))==430
    key=KEYFILE.read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"[a-f0-9]{8,128}",key)
    (dest/(key+".txt")).write_text(key+"\n",encoding="utf-8",newline="\n")
    (dest/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: "+HOST+"/sitemap.xml\n",encoding="utf-8",newline="\n")
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap+="".join("<url><loc>"+escape(url)+"</loc></url>\n" for url in urls)
    sitemap+='</urlset>\n'
    (dest/"sitemap.xml").write_text(sitemap,encoding="utf-8",newline="\n")
    seen=[x.text for x in ET.fromstring(sitemap).iter() if x.tag.endswith("loc")]
    assert seen==urls and len(seen)==430
    assert (dest/"404.html").read_text(encoding="utf-8").count("noindex,nofollow")==1
    assert len(list((dest/"assets/baekse").glob("*.webp")))==5
    assert len(list(dest.rglob("*.html")))==431
    receipt={
      "site":"baekse","domain":HOST,"status":"FULL_430_INDEXABLE_CANDIDATE_OFFLINE",
      "counts":quality["pageTypes"],"pageCount":430,"urlCount":len(urls),
      "urls":urls,"sitemapUrl":HOST+"/sitemap.xml","robots":"Allow /",
      "indexMeta": "index,follow","selfCanonicalCount":430,
      "keyUrl":HOST+"/"+key+".txt","keyFileSHA256":hashlib.sha256((key+"\n").encode()).hexdigest(),
      "webpCount":5,"unknownPageNoindex":True,
      "searchIndexConfirmed":False,"indexNowSubmitted":False,
      "previewWorkersDevMustBeNoindex":True,
      "limit":"Search engines independently determine index eligibility; lexical similarity below .49 does not guarantee ranking."
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":receipt["status"],"pages":430,"sitemap":430,"images":5,
       "regionCities":85,"keyUrl":receipt["keyUrl"],"indexNowSubmitted":False},ensure_ascii=False))
    return receipt

if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--source",type=Path,default=SOURCE)
    args.add_argument("--dest",type=Path,default=DEST)
    a=args.parse_args()
    render(a.source,a.dest)
