#!/usr/bin/env python3
"""Prepare exactly one indexable Winterbbang homepage.

Copies the audited noindex 1,804-page corpus, changes only the homepage,
robots, one-URL sitemap and public IndexNow ownership key. No API submission
or Cloudflare mutation takes place here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts import audit_winterbbang_search_quality as qa

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dist/winterbbang"
DEST = ROOT / "dist/winterbbang-home-indexable"
REPORT = ROOT / "reports/winterbbang/home-release.json"
KEY_PATH = ROOT / "sites/winterbbang/indexnow-public-key.txt"
HOME_URL = "https://winterbbang.nalmada.net/"
KEY_PATTERN = re.compile(r"[0-9a-f]{8,128}")

def prepare(source: Path = SOURCE,dest: Path = DEST,report: Path = REPORT):
    quality=qa.check(source)
    assert quality["readyForHomeOnlyRelease"] and not quality["readyForFullSiteIndexing"]
    if dest.resolve() == source.resolve() or dest.resolve() in (ROOT,ROOT/"sites"):
        raise ValueError("Unsafe release output path")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source,dest)
    key=KEY_PATH.read_text(encoding="utf-8").strip()
    assert KEY_PATTERN.fullmatch(key), "Invalid IndexNow public key"
    home=(dest/"index.html").read_text(encoding="utf-8")
    assert home.count('<meta name="robots" content="noindex,nofollow">')==1
    assert 'rel="canonical"' not in home
    home=home.replace('<meta name="robots" content="noindex,nofollow">',
         '<meta name="robots" content="index,follow"><link rel="canonical" href="'+HOME_URL+'">',1)
    assert home.count('<link rel="canonical" href="'+HOME_URL+'">')==1
    assert home.count('<meta name="robots" content="index,follow">')==1
    (dest/"index.html").write_text(home,encoding="utf-8",newline="\n")
    robots="User-agent: *\nAllow: /\nSitemap: "+HOME_URL+"sitemap.xml\n"
    (dest/"robots.txt").write_text(robots,encoding="utf-8",newline="\n")
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+HOME_URL+'</loc></url></urlset>\n'
    (dest/"sitemap.xml").write_text(sitemap,encoding="utf-8",newline="\n")
    (dest/(key+".txt")).write_text(key+"\n",encoding="utf-8",newline="\n")
    urls=[x.text for x in ET.fromstring(sitemap).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert urls==[HOME_URL]
    region_paths=list((dest/"r").glob("*.html"))
    hubs=list((dest/"d").glob("*.html"))+list((dest/"p").glob("*.html"))
    assert len(region_paths)==1732 and len(hubs)==71
    for file in region_paths+hubs+[dest/"404.html"]:
        text=file.read_text(encoding="utf-8")
        assert '<meta name="robots" content="noindex,nofollow">' in text,file
        assert '<meta name="robots" content="index,follow">' not in text,file
        assert 'rel="canonical"' not in text,file
    assert all((dest/"assets/images"/p).is_file() for p in
               ("hero.webp","shop-in-shop.webp","menu.webp","street.webp","ingredients.webp"))
    result={
       "site":"winterbbang","release":"HOME_ONLY_PUBLIC_CANARY",
       "host":"winterbbang.nalmada.net","homepage":HOME_URL,
       "indexableCount":1,"noindexHtmlCount":1804,
       "noindexNonhomePages":1803,"noindex404":True,
       "sitemapCount":1,"sitemapUrls":urls,
       "keyFile":key+".txt","keyFileSha256":hashlib.sha256((key+"\n").encode()).hexdigest(),
       "publicRobots":"Allow /, Sitemap one URL",
       "indexedStatus":"NOT_KNOWN",
       "indexNowSubmissionStatus":"NOT_SUBMITTED_IN_BUILD",
       "currentSourceNeedsDeploy":True,
       "approvedDesign":True,
       "contentQualityEvidence":quality["status"],
       "qualityReport":"reports/winterbbang/search-quality.json",
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,default=SOURCE)
    a.add_argument("--dest",type=Path,default=DEST)
    a.add_argument("--report",type=Path,default=REPORT)
    args=a.parse_args()
    prepare(args.source,args.dest,args.report)
