#!/usr/bin/env python3
"""Winterbbang all-1804 search-release candidate audit.

Separates technical and factual-expression checks from search-engine ranking
eligibility. Verifies the real 9-paragraph locality revision and <0.49 fixed
sample-vs-all similarity without inventing local shop/case/price evidence.
No Cloudflare, DNS, or IndexNow calls.
"""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from html import unescape
from pathlib import Path
from scripts import build_winterbbang_national as national

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/winterbbang"
REPORT=ROOT/"reports/winterbbang/search-quality-v2.json"
SCOPE=ROOT/"sites/winterbbang/search-release-scope-v2.json"
BLOCKED_PATTERNS=[
  r"초도비용\s*[=:]?\s*(?:0|\d+)\s*(?:원|만원)",
  r"월\s*최소\s*(?:식자재)?\s*(?:구매|매입)",
  r"월\s*(?:100|백)\s*만\s*원",
  r"계약\s*종료\s*시\s*반환",
  r"수익\s*(?:확정|보장|무조건)",
  r"이\s*(?:동네|지역)에\s*(?:백세푸드\s*)?(?:직영|가맹|판매)\s*매장\s*(?:운영|존재)",
  r"이\s*지역\s*(?:판매|매출)\s*실적\s*(?:\d+|확인)",
  r"(?:준비\s*중|검수용|임시\s*페이지|실제\s*사례\s*미확인)"
]
BLOCKED=re.compile("|".join(BLOCKED_PATTERNS),re.I)
TEMPLATE_IMAGES=["hero.webp","shop-in-shop.webp","menu.webp","street.webp","ingredients.webp"]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def run(out:Path=OUT,report:Path=REPORT):
    scope=read_json(SCOPE)
    manifest=read_json(national.REPORT/"manifest.json")
    similarity=read_json(national.REPORT/"similarity.json")
    ledger=read_json(national.LEDGER)
    spec=read_json(national.BASE/"site-spec.json")
    assert scope["releaseType"]=="ALL_1804_INDEXABLE_CANDIDATE"
    assert scope["expectedIndexNowCount"]==1804
    assert scope["domain"]==spec["domain"]=="https://winterbbang.nalmada.net"
    assert len(ledger["rows"])==1732 and ledger["asOf"]=="2026-10-12"
    assert manifest["count"]==1804 and manifest["localityCount"]==1732
    assert len(manifest["pages"])==1804
    assert len({p["path"] for p in manifest["pages"]})==1804
    assert similarity["passed"] is True
    assert similarity["maxPair"]["value"]<0.49
    assert similarity["comparisons"]==31158
    assert similarity["exactDuplicateNarratives"]==0
    assert len(manifest["assets"])==5
    assert set(x["filename"] for x in manifest["assets"])==set(TEMPLATE_IMAGES)
    for a in manifest["assets"]:
        raw=(out/"assets/images"/a["filename"]).read_bytes()
        assert raw[:4]==b"RIFF" and raw[8:12]==b"WEBP"
        assert len(raw)==a["bytes"] and hashlib.sha256(raw).hexdigest()==a["sha256"]
    counts=Counter()
    titles=set()
    descriptions=set()
    all_hrefs=set()
    localParagraphs=[]
    fixtureCount=0
    failures=[]
    for entry in manifest["pages"]:
        url=entry["path"]
        html_path=out/("index.html" if url=="/" else url.lstrip("/"))
        body=html_path.read_text(encoding="utf-8")
        counts[entry["type"]]+=1
        title=re.search(r"<title>(.*?)</title>",body,re.S|re.I)
        h1=re.search(r"<h1>(.*?)</h1>",body,re.S|re.I)
        description=re.search(r'<meta name="description" content="([^"]+)"',body)
        assert title and h1 and description,(url,"missing SEO title/H1/description")
        titleTxt=unescape(title.group(1));h1Txt=unescape(h1.group(1))
        assert h1Txt in titleTxt,(url,"title/h1 intent mismatch")
        titles.add(titleTxt);descriptions.add(description.group(1))
        assert '<meta name="robots" content="noindex,nofollow">' in body
        assert 'rel="canonical"' not in body
        assert "tel:0314070103" in body and "031-407-0103" in body
        assert "매출총이익률" in body and "재료비" in body and "순이익률" in body
        assert "60~70%" in body
        assert not BLOCKED.search(body),(url,"unsupported claim, private term, or placeholder")
        for image in TEMPLATE_IMAGES:
            assert '/assets/images/'+image in body,(url,image)
        all_hrefs.update(re.findall(r'<a[^>]+\bhref="([^"]+)"',body))
        if entry["type"]=="locality":
            assert entry["region"] in titleTxt,(url,"region absent in title")
            top=re.search(r'<div class="copygrid">(.*?)</div>',body,re.S)
            lower=re.search(r'<section class="local-detail">(.*?)</section>',body,re.S)
            assert top and lower,(url,"missing original topic sections")
            upper=[unescape(x) for x in re.findall(r'<article class="copy">.*?<p>(.*?)</p>',top.group(1),re.S)]
            bottom=[unescape(x) for x in re.findall(r'<article class="copy">.*?<p>(.*?)</p>',lower.group(1),re.S)]
            assert len(upper)==3 and len(bottom)==9,(url,len(upper),len(bottom))
            assert not set(upper)&set(bottom),(url,"nine-section duplicate repeats top cards")
            assert len(set(bottom))==9,(url,"nine paragraph duplicate")
            localParagraphs.append("\n".join(bottom))
            fixtureCount+=1
    assert len(titles)==1804,("duplicate titles",len(titles))
    assert len(descriptions)==1804,("duplicate descriptions",len(descriptions))
    assert len(localParagraphs)==1732 and len(set(localParagraphs))==1732
    assert fixtureCount==1732
    assert counts==Counter({"locality":1732,"district-hub":69,"province-hub":2,"home":1}),counts
    internal={p for p in all_hrefs if p.startswith("/")}
    all_paths={p["path"] for p in manifest["pages"]}
    assert not internal-all_paths,("broken internal links",sorted(internal-all_paths)[:10])
    assert not (out/"sitemap.xml").exists()
    assert (out/"robots.txt").read_text()=="User-agent: *\nDisallow: /\n"
    quality={
        "site":"winterbbang","mode":"ALL_1804_PUBLIC_CANDIDATE","buildSource":"pinned V5 region ledger and 160 original copy blocks",
        "pass":True,"totalCandidates":1804,"pagesByType":dict(counts),
        "titleUnique":len(titles),"metaDescriptionUnique":len(descriptions),
        "verifiedLocalityNames":1732,"regionNameSourceAsOf":"2026-10-12 mixed candidate ledger, legal/administrative status not independently verified",
        "localityLowerParagraphsPerPage":9,"topCopyParagraphsPerPage":3,
        "duplicatesAcrossTopAndNineLowerParagraphs":0,
        "exactDuplicateNineParagraphLocalityNarratives":0,
        "unsupportedOrPrivatePatternsDetected":0,"missingInternalLinkTargets":0,
        "imagesVerified":5,
        "similarity":{"metric":"char-5gram-jaccard","sampleCount":18,
                      "comparisons":similarity["comparisons"],"max":similarity["maxPair"]["value"],
                      "thresholdExclusive":0.49,"violations":similarity["overlapAtOrAbove49Percent"],
                      "method":"fixed 18 regional narratives vs entire 1732 corpus, not all-pairs"},
        "searchPolicyWarning":"A <0.49 lexical similarity score is not a search-engine quality guarantee. Search platforms may still classify regional lead pages as doorway/scaled content.",
        "businessProofScope":"Four menus, ingredient supply, phone confirmed by operator; no asserted individual physical stores, prices, or local sales cases.",
        "readyForCandidateBuild":True,"livePublished":False,"indexNowSubmitted":False
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(quality,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","pages":1804,"uniqueTitles":len(titles),"uniqueDescriptions":len(descriptions),
                      "nineParagraphLocalities":fixtureCount,"sampleMax":similarity["maxPair"]["value"],
                      "sampleComparedPairs":similarity["comparisons"]},ensure_ascii=False))
    return quality

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dist",type=Path,default=OUT)
    p.add_argument("--report",type=Path,default=REPORT)
    a=p.parse_args()
    run(a.dist,a.report)
