#!/usr/bin/env python3
"""Fact-and-intent search-release eligibility audit for Winterbbang.

This gate is intentionally stricter than a lexical Jaccard comparison:
a page made from locality name plus shuffled general advice cannot be released
to search even if its character n-grams are different from adjacent pages.
No network or deployment action is performed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from scripts import build_winterbbang_national as build

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/winterbbang/search-quality.json"
PREVIEW = ROOT / "dist/winterbbang"
SCOPE = ROOT / "sites/winterbbang/search-release-scope.json"

def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def check(out: Path = PREVIEW, report: Path = REPORT):
    scope = read(SCOPE)
    spec = read(build.BASE / "site-spec.json")
    manifest = read(build.REPORT / "manifest.json")
    similarity = read(build.REPORT / "similarity.json")
    assert scope["site"] == spec["siteId"] == "winterbbang"
    assert scope["releaseType"] == "HOME_ONLY_CANARY"
    assert scope["indexablePaths"] == ["/"] and len(scope["indexablePaths"]) == 1
    assert scope["publishedPagesToRemainNoindex"] == 1803
    assert scope["domain"] == spec["domain"] == "https://winterbbang.nalmada.net"
    assert spec["domainBinding"]["status"] == "LIVE_HTTPS_NO_INDEX"
    assert spec["publishPolicy"]["customDomainBindingVerified"] is True
    assert spec["publishPolicy"]["searchReleaseAllowed"] is False
    assert manifest["count"] == 1804 and manifest["localityCount"] == 1732
    assert manifest["hubCount"] == 71
    assert similarity["passed"] and similarity["maxPair"]["value"] < .49
    assert (out/"robots.txt").read_text(encoding="utf-8") == "User-agent: *\nDisallow: /\n"
    assert not (out/"sitemap.xml").exists()
    home = (out/"index.html").read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", home, flags=re.S)
    h1 = re.search(r"<h1>(.*?)</h1>", home, flags=re.S)
    assert title and h1 and h1.group(1) in title.group(1), "Home title and H1 mismatch"
    assert '<meta name="robots" content="noindex,nofollow">' in home
    assert 'rel="canonical"' not in home
    required = ["백세푸드","031-407-0103","tel:0314070103","붕어빵","잉어빵","계란빵","십원빵",
                "샵인샵","반죽","팥소","슈크림","매출총이익률","재료비","순이익률"]
    missing = [term for term in required if term not in home]
    assert not missing, "Home missing core business fact(s): " + repr(missing)
    forbidden = re.compile(r"초도비용\s*\d|월\s*(?:최소\s*)?\d+\s*만\s*원|최소\s*구매.{0,15}\d+|무조건\s*수익")
    assert not forbidden.search(home), "Private contract/earnings promise leaked into home"
    assert len(list((out/"assets/images").glob("*.webp"))) == 5

    # A verified locality content source has NOT been supplied. A geographic
    # name or shuffled nonlocal sentence is not locally distinctive evidence.
    distinct_local_evidence = 0
    kinds = {}
    for page in manifest["pages"]:
        kinds[page["type"]] = kinds.get(page["type"],0) + 1
        path = out / ("index.html" if page["path"] == "/" else page["path"].lstrip("/"))
        assert path.exists(), page["path"]
        if page["path"] != "/":
            text = path.read_text(encoding="utf-8")
            assert '<meta name="robots" content="noindex,nofollow">' in text
    assert kinds == {"home":1,"province-hub":2,"district-hub":69,"locality":1732}, kinds
    assert not (build.BASE/"verified-local-business-facts.json").exists(), (
        "A new verified-local-business-facts ledger appeared; perform a new independent quality review"
    )
    assert distinct_local_evidence == 0
    result = {
        "site":"winterbbang", "version":1, "status":"PASS_FOR_HOME_ONLY_AND_BLOCK_ALL_REGION_URLS",
        "policyBasis":"Google Search Central doorway abuse and scaled content abuse: locality name + recombined general copy is insufficient",
        "totalSiteUrls":manifest["count"], "types":kinds,
        "localityReview":{
            "regionNameInventoryAsOf":"2026-10-12", "candidateNameCount":1732,
            "independentLocalBusinessFactRows":distinct_local_evidence,
            "regionPagesSearchEligible":0,
            "regionHubsSearchEligible":0,
            "why":"The same centrally supplied phone CTA and 160 generic text blocks are selected by hash; no verified district-specific conditions, local sales presence, original case studies, or unique search tasks."
        },
        "homeReview":{
            "searchCandidateEligible":True, "onlyAllowedPath":"/",
            "operatorBusinessFactsPresent":True,
            "phoneAndFourMenuOfferings":True,
            "ingredientSupplyAndShopInShop":True,
            "grossMarginNotNetMargin":True,
            "privateTermsAbsent":True,
            "limits":"Operator provided figures are not an independent audited income guarantee."
        },
        "lexicalSimilarity":{
            "comparisonType":"18 sampled regional narratives versus remaining full 1732 corpus",
            "maxFiveGramJaccard":similarity["maxPair"]["value"],
            "comparedPairs":similarity["comparisons"],
            "isSearchQualityProof":False
        },
        "publicCanaryUrl":"https://winterbbang.nalmada.net/",
        "excludedFromIndexNow":1803, "permittedIndexNowUrls":["https://winterbbang.nalmada.net/"],
        "technicalPrerequisites":["unique homepage index,follow on custom host","self canonical only public host home",
                                  "public host robots Allow /","1 URL sitemap","owned IndexNow key HTTP200 exact content",
                                  "workers.dev entirely noindex/robots disallow","non-home paths noindex",
                                  "existing Worker version and domain binding preservation"],
        "readyForFullSiteIndexing":False,
        "readyForHomeOnlyRelease":True,
        "hasSubmittedIndexNow":False,
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"quality":result["status"],"homeEligible":1,"regionEligible":0,
                      "deferred":result["excludedFromIndexNow"],"similarity":result["lexicalSimilarity"]},
                     ensure_ascii=False))
    return result

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--dist",type=Path,default=PREVIEW)
    parser.add_argument("--report",type=Path,default=REPORT)
    args=parser.parse_args()
    check(args.dist,args.report)
