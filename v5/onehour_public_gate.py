"""Onehour exact-host, 5436-page, owner facts and lexical QA release gate."""
from __future__ import annotations
import json
from .config import ROOT, ConfigError
PATH=ROOT/"sites/onehour-sky/release-evidence.json"
def verify_owner_scope(site):
    try:
        proof=json.loads(PATH.read_text(encoding="utf-8"))
    except (OSError,ValueError) as e:
        raise ConfigError("Missing owner consent evidence: "+str(e)) from e
    good=(proof.get("site")=="onehour-sky"
          and proof.get("host")=="1hrsky.nalmada.net"
          and proof.get("scope")=="onehour-5436-20261028"
          and proof.get("totalPages")==5436
          and proof.get("userApproved",{}).get("phone")==site.get("phone")
          and sorted(proof.get("userApproved",{}).get("photos",[]))==sorted(site.get("imagePool",[]))
          and proof.get("userProvided",{}).get("oneHourArrivalNotGuaranteed") is True
          and proof.get("confirmedRuns",{}).get("domainBinding")==40543796228
          and proof.get("naverHomepageToken")==site.get("naverSiteVerification")
          and proof.get("public",{}).get("worker")=="sfv5-onehour-sky-preview"
          and site.get("indexNow",{}).get("enabled") is False)
    if not good: raise ConfigError("Onehour exact-host owner/source verification failed")
    return proof

def verify_content_qa(site,pages):
    proof=verify_owner_scope(site)
    if (len(pages)!=5436 or proof["quality"]["sampleSize"]!=55
        or proof["quality"]["pairs"]!=298925
        or proof["quality"]["maxSimilarity"]>=0.49
        or proof["quality"]["exactDuplicates"]!=0
        or site.get("pricingPolicy")!="half-day-minimum-consult"):
        raise ConfigError("Onehour source quality scope mismatch")
    from .onehour_sky_quality import inspect
    fresh=inspect(pages)
    if not fresh["passed"] or fresh["wholePopulationExactBodyDuplicates"] or fresh["worstSampleToPopulationSimilarity"]>=0.49:
        raise ConfigError("Onehour current 1%-versus-all content QA failed")
    forbidden=("실제 이 지역에서 시공 완료","무조건 한 시간 이내 도착","15년 무사고")
    if any(f in p["intro"]+" "+" ".join(s["paragraph"] for s in p["sections"]) for p in pages for f in forbidden):
        raise ConfigError("Unverified service promise in content")
    return fresh
