"""Evidence-bound homepage editorial release gate.

The Quicksky homepage is a phone consultation overview. Owner statements are evidence
for statements made by the operator, not evidence of fleet ownership or completed jobs.
This gate only permits the EXACT homepage URL, never the region-name page collection.
"""
from __future__ import annotations
import json
from pathlib import Path
from .config import ROOT,ConfigError

EVIDENCE=ROOT/"docs/QUICKSKY_HOME_FACTS_QUALITY_EVIDENCE_20261027.json"

def validate_home_evidence(site, pages, rates):
    if site.get("id")!="quicksky" or site.get("domain")!="https://quicksky.nalmada.net":
        raise ConfigError("Home evidence for unrelated domain rejected")
    if site.get("homeIndexingScope")!="quicksky-home-1-20261027" or len(pages)!=1733:
        raise ConfigError("Quicksky home-only scope and inventory mismatch")
    if not EVIDENCE.is_file():
        raise ConfigError("Quicksky home editorial evidence document is missing")
    obj=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if (obj.get("siteId")!="quicksky" or obj.get("hostname")!="quicksky.nalmada.net"
            or obj.get("releaseScope")!=site["homeIndexingScope"]):
        raise ConfigError("Homepage quality review does not cover this exact release")
    review=obj.get("homeCopyReview",{})
    verdict=obj.get("qualityDecision",{})
    if review.get("indexablePaths")!=["/"] or review.get("regionPagesIndexable")!=0 \
            or review.get("regionalPageCountRetained")!=1732 \
            or verdict.get("homeOnly")!="APPROVED_AFTER_SCOPE_LIMITED_COPY_REVIEW" \
            or verdict.get("allRegions")!="NOT_APPROVED":
        raise ConfigError("Home evidence does not limit indexing to one URL")
    facts={x.get("fact"):x for x in obj.get("factMatrix",[])}
    for name in ("Brand","Consultation telephone","Consultation service area",
                 "Topics 1t, 3.5t, 5t","Photographs","Domain association","Pricing"):
        if name not in facts or not facts[name].get("basis") or not facts[name].get("status"):
            raise ConfigError("Quicksky home fact review incomplete: "+name)
    if (site.get("brand")!="빠른스카이" or site.get("phone")!="010-5322-1952"
            or site.get("region")!="서울·경기"
            or site.get("pricingPolicy")!="consult-only" or rates.get("plans")):
        raise ConfigError("Current home facts deviate from recorded operator statements")
    if set(site["imagePool"])!={"skycar-hero.webp","skycar-facade.webp","skycar-truck.webp"}:
        raise ConfigError("Home review did not approve changed images")
    if pages[0]["number"]!=1 or pages[0]["id"]!="quicksky-home":
        raise ConfigError("Homepage source differs from reviewed seed")
    intro=pages[0]["intro"]
    if not all(x in intro for x in ("1톤·3.5톤·5톤","전화 상담","현장 조건")):
        raise ConfigError("Homepage service/consultation description changed from evidence")
    combined=intro+" ".join(s["paragraph"] for s in pages[0]["sections"])
    if any(x in combined for x in ("전 지역 당일","전국 어디든","20~30분 이내","시공 완료","무사고","도착 보장","확정된 가격")):
        raise ConfigError("Unsupported guarantee introduced into homepage")
    if not all((ROOT/p).is_file() for p in obj["evidenceRefs"] if not p.startswith("https://")):
        raise ConfigError("Source evidence reference missing")
    return {"homeVerified":True,"indexablePaths":["/"],"regionsNoindex":1732,
            "businessEvidenceType":"owner-stated, not measured fleet/dispatch"}
