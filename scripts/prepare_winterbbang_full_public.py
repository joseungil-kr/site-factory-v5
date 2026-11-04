#!/usr/bin/env python3
"""Create Winterbbang 1,804-URL searchable static release candidate.

Reproduces the approved responsive design and source HTML exactly, except for
searchable meta/canonical, public robots.txt, sitemap.xml and IndexNow key.
No HTTP, Cloudflare or IndexNow action. The preview worker must always remain
noindex on workers.dev using its host-aware routing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from html import escape as h

from scripts import audit_winterbbang_full_quality as qa
from scripts import build_winterbbang_national as build

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"dist/winterbbang"
DEST=ROOT/"dist/winterbbang-public-1804"
REPORT=ROOT/"reports/winterbbang/full-public-release.json"
DOMAIN="https://winterbbang.nalmada.net"
KEY_FILE=ROOT/"sites/winterbbang/indexnow-public-key.txt"

def construct(source=SOURCE,dest=DEST,report=REPORT):
    audit=qa.run(source)
    assert audit["readyForCandidateBuild"] is True and audit["totalCandidates"]==1804
    manifest=json.loads((ROOT/"reports/winterbbang/manifest.json").read_text(encoding="utf-8"))
    scope=json.loads((ROOT/"sites/winterbbang/search-release-scope-v2.json").read_text(encoding="utf-8"))
    assert scope["releaseType"]=="ALL_1804_INDEXABLE_CANDIDATE"
    assert scope["expectedIndexNowCount"]==manifest["count"]==1804
    assert scope["domain"]==DOMAIN
    assert source.resolve()!=dest.resolve()
    assert dest.resolve() not in (ROOT,ROOT/"sites",ROOT/"assets")
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(source,dest)
    assert len(list(dest.rglob("*.html")))==1805
    paths=[]
    for page in manifest["pages"]:
        route=page["path"]
        target=dest/("index.html" if route=="/" else route.lstrip("/"))
        assert target.is_file(),route
        body=target.read_text(encoding="utf-8")
        assert body.count('<meta name="robots" content="noindex,nofollow">')==1,route
        assert 'rel="canonical"' not in body,route
        url=DOMAIN+route
        canonical='<link rel="canonical" href="'+h(url,quote=True)+'">'
        body=body.replace('<meta name="robots" content="noindex,nofollow">',
                          '<meta name="robots" content="index,follow">'+canonical,1)
        assert body.count('<meta name="robots" content="index,follow">')==1,route
        assert body.count(canonical)==1,route
        assert 'noindex' not in re.search(r"<head>(.*?)</head>",body,re.S).group(1).lower(),route
        target.write_text(body,encoding="utf-8",newline="\n")
        paths.append(url)
    assert len(paths)==len(set(paths))==1804
    key=KEY_FILE.read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"[0-9a-f]{8,128}",key)
    (dest/(key+".txt")).write_text(key+"\n",encoding="utf-8",newline="\n")
    robots="User-agent: *\nAllow: /\nSitemap: "+DOMAIN+"/sitemap.xml\n"
    (dest/"robots.txt").write_text(robots,encoding="utf-8",newline="\n")
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap+='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap+="".join("<url><loc>"+h(url,quote=False)+"</loc></url>\n" for url in paths)
    sitemap+='</urlset>\n'
    (dest/"sitemap.xml").write_text(sitemap,encoding="utf-8",newline="\n")
    parsed=ET.fromstring(sitemap)
    actual=[el.text for el in parsed.iter() if el.tag.endswith("loc")]
    assert actual==paths and all(url.startswith(DOMAIN+"/") for url in actual)
    assert (dest/"404.html").read_text(encoding="utf-8").count('noindex,nofollow')==1
    assert all('<meta name="robots" content="index,follow">' in
               (dest/("index.html" if p["path"]=="/" else p["path"].lstrip("/"))).read_text(encoding="utf-8")
               for p in manifest["pages"])
    assert len(list((dest/"assets/images").glob("*.webp")))==5
    receipt={
      "site":"winterbbang","mode":"ALL_1804_INDEXABLE_RELEASE_CANDIDATE",
      "sourceNameLedger":"data/regions/seoul_gyeonggi_current_dong.json",
      "count":len(paths),"localityCount":1732,"districtCount":69,"provinceCount":2,"homeCount":1,
      "publicRoot":DOMAIN+"/","allUrls":paths,"sitemap":DOMAIN+"/sitemap.xml",
      "sitemapUrlCount":len(actual),"robotsAllow":True,"noindex404":True,
      "allPagesIndexFollow":True,"selfCanonicalCount":len(paths),
      "previewNoindexEnforcedByDedicatedWorker":True,
      "keyLocation":DOMAIN+"/"+key+".txt","keyFilename":key+".txt",
      "keySHA256":hashlib.sha256((key+"\n").encode()).hexdigest(),
      "images":5,"qualityAudit":"reports/winterbbang/search-quality-v2.json",
      "indexNowAttempted":False,"cloudflareDeployed":False,
      "risks":"IndexNow 200/202 is URL receipt, not index confirmation; Google/Naver independently determine eligibility."
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"site":receipt["site"],"mode":receipt["mode"],"urls":len(paths),
                      "sitemap":len(actual),"canonical":len(paths),"keyFile":key+".txt",
                      "noindex404":True,"indexNowAttempted":False},ensure_ascii=False))
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,default=SOURCE)
    ap.add_argument("--dest",type=Path,default=DEST)
    ap.add_argument("--report",type=Path,default=REPORT)
    args=ap.parse_args()
    construct(args.source,args.dest,args.report)
