"""Match a strictly bounded government-primary-source subset; never infer region coverage.

No web scraping or secret keys. Input source rows are hand verified with cited government
legal-dong code table (8) and MOIS 2026-07-01 change notice (2).
Remaining ledger entries are *unknown*, not mismatches.
"""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path
from v5.config import ROOT, read_site

REF=ROOT/"data/regions/quicksky_official_government_match_sample_20261027.json"

def verify_and_export(output:Path)->dict:
    site=read_site("quicksky")
    pages=site["pages"][1:]
    assert len(pages)==1732
    official=json.loads(REF.read_text(encoding="utf-8"))
    rows=official["dataEntries"]
    assert len(rows)==10
    names=[r["fullName"] for r in rows]
    if len(names)!=len(set(names)):raise ValueError("Duplicate official sample name")
    by_name={r["fullName"]:r for r in rows}
    all_names=[p["region"] for p in pages]
    if len(all_names)!=len(set(all_names)):raise ValueError("Non-unique original region ledger")
    unmatched_official=set(by_name)-set(all_names)
    if unmatched_official:raise ValueError("Government cited names absent from original ledger: "+repr(unmatched_official))
    export=[]
    for page in pages:
        r=by_name.get(page["region"])
        export.append({
            "pageNumber":page["number"],"pageId":page["id"],
            "pagePath":"/"+str(page["number"])+".html",
            "originalRegionName":page["region"],
            "officialMatchStatus":"VERIFIED_NAME_AND_CODE" if r and r["codeVerified"]
            else "VERIFIED_NAME_ONLY" if r else "NOT_YET_CHECKED",
            "officialRegionType":r["officialCategory"] if r else "UNVERIFIED",
            "officialCode":r["officialCode"] if r and r["codeVerified"] else "",
            "primaryGovernmentSourceUrl":r["sourceUrl"] if r else "",
            "primarySourceCheckedDate":r["checkedDate"] if r else "",
            "serviceCoverageProof":"NOT_PROVIDED",
            "indexingEligibility":"NO_EVIDENCE_FOR_REGIONAL_INDEXING"
        })
    counts=Counter(x["officialMatchStatus"] for x in export)
    if counts!={"VERIFIED_NAME_AND_CODE":8,"VERIFIED_NAME_ONLY":2,"NOT_YET_CHECKED":1722}:
        raise ValueError("Official-region matching result changed; independently review evidence")
    output.mkdir(parents=True,exist_ok=True)
    with (output/"quicksky-official-region-name-match.csv").open("w",newline="",encoding="utf-8-sig") as fp:
        writer=csv.DictWriter(fp,fieldnames=tuple(export[0].keys()))
        writer.writeheader();writer.writerows(export)
    summary={"site":"quicksky","ledgerEntries":len(export),"governmentNameAndCodeMatches":8,
        "governmentNameOnlyMatches":2,"notYetChecked":1722,
        "serviceCoverageIndependentlyVerified":0,
        "indexableRegionalPagesSupportedByThisCheck":0,
        "sourceScope":[{"url":s["sourceUrl"],"description":s["description"]} for s in official["primarySources"]],
        "limitations":["Not a national code source snapshot","Official present-day names may differ from 2026-10-12 candidate records",
                       "One-to-one legal/administrative status not proven for remaining entries",
                       "No government name match indicates Quicksky actual dispatch or completed job"]}
    (output/"quicksky-official-region-match-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser();a.add_argument("--output",type=Path,default=Path("reports/quicksky/official-government-match"))
    args=a.parse_args()
    print(json.dumps(verify_and_export(args.output),ensure_ascii=False,indent=2))
