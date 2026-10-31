"""Fail-closed national public release gate: evidence-backed source freshness checks.

This is deliberately NOT a generator and does not mutate site, DNS, or Worker.
Current 242-record third-party dataset is known incomplete and deprecated for public index.
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"sites/skyquote/nationwide-district-source.json"
EVIDENCE=ROOT/"sites/skyquote/official-region-reconciliation.json"
def main():
    data=json.loads(SOURCE.read_text(encoding="utf-8"))
    check=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    rows=data["rows"]
    names={(r["region"],r["name"]) for r in rows if r["level"]==2}
    province_names={r["name"] for r in rows if r["level"]==1}
    seen=[]
    for province,district in check["requiredPresentDistricts"]:
        if (province,district) not in names:seen.append("MISSING "+province+" "+district)
    for province in check["mustNotUseFormerProvinceNames"]:
        if province in province_names:seen.append("STALE PROVINCE "+province)
    for province,district in check["mustNotUseFormerDistrictNames"]:
        if (province,district) in names:seen.append("STALE DISTRICT "+province+" "+district)
    # A full official snapshot and reconciliation, not just a patched list, is mandatory.
    verified=check.get("fullOfficialSnapshot",{})
    if not verified.get("sha256") or not verified.get("validatedRowCount") or verified.get("matchedCurrentCodeSystem") is not True:
        seen.append("OFFICIAL_SNAPSHOT_NOT_VERIFIED")
    result={"releaseReadiness":"BLOCKED" if seen else "SOURCE_CHECK_PASS",
            "candidateProvinceCount":sum(r["level"]==1 for r in rows),
            "candidateDistrictCount":sum(r["level"]==2 for r in rows),
            "checks":seen,"previewNoindexOnly":True}
    print("SKYQUOTE_PUBLIC_REGION_READINESS",json.dumps(result,ensure_ascii=False))
    if seen:raise SystemExit(2)
if __name__=="__main__":main()
