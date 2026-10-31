"""Export only demonstrable gaps, never fabricate service or region facts.

A generated location-name page is NOT proof that an operator serves the location.
The evidence-gap CSV is an internal research worksheet, not visitor content.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from v5.config import read_site

HEADERS=(
    "pageNumber","pagePath","pageId","regionName","topic",
    "officialRegionType","officialRegionCode","officialSourceUrl",
    "officialSourceAsOf","operatorServiceStatus","operatorEvidenceSource",
    "bookingPolicy","verifiedEquipmentModels","verifiedJobEvidence",
    "publishedIndexingState","gapResolutionStatus",
)
UNKNOWN="UNVERIFIED"

def export(output: Path) -> dict:
    data=read_site("quicksky")
    pages=data["pages"]
    site=data["site"]
    if site["domain"]!="https://quicksky.nalmada.net" or len(pages)!=1733:
        raise ValueError("Unexpected Quicksky scope or requested domain")
    if site.get("publicIndexingApproved") or site.get("publishEnabled"):
        raise ValueError("Export is only safe for the current nonindexable service source")
    if [p["number"] for p in pages]!=list(range(1,1734)):
        raise ValueError("Numbered page inventory changed")
    output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for page in pages[1:]:
        number=page["number"]
        rows.append({
            "pageNumber":number,"pagePath":f"/{number}.html",
            "pageId":page["id"],"regionName":page["region"],"topic":page["topic"],
            "officialRegionType":UNKNOWN,"officialRegionCode":UNKNOWN,
            "officialSourceUrl":"","officialSourceAsOf":"",
            "operatorServiceStatus":UNKNOWN,"operatorEvidenceSource":"",
            "bookingPolicy":UNKNOWN,"verifiedEquipmentModels":UNKNOWN,
            "verifiedJobEvidence":UNKNOWN,
            "publishedIndexingState":"noindex",
            "gapResolutionStatus":"NEEDS_OFFICIAL_CLASSIFICATION_AND_OPERATOR_CONFIRMATION",
        })
    assert len(rows)==1732 and len({r["regionName"] for r in rows})==1732
    assert len({r["pageId"] for r in rows})==1732
    assert len({r["pagePath"] for r in rows})==1732
    with (output/"region-evidence-gaps.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    province=Counter("서울" if r["regionName"].startswith("서울특별시 ") else "경기" for r in rows)
    summary={
        "site":"quicksky","generatedAtUTC":datetime.now(timezone.utc).isoformat(),
        "domain":site["domain"],"sourcePageCount":len(pages),
        "regionNameEntries":len(rows),"provinceCount":dict(province),
        "officialRegionClassificationsSupportedByCurrentSource":0,
        "operatorAvailabilityEvidenceRecordsPresentInCurrentSource":0,
        "siteJobEvidenceRecordsPresentInCurrentSource":0,
        "publicIndexingEligibleEstablishedByThisEvidenceExport":0,
        "notes":[
            "Zero means no supporting source/evidence fields exist in this repository, not that service is impossible.",
            "Current source is a pinned mixed legal/administrative region-name candidate ledger.",
            "Government regional classification requires separately verified official code names and as-of dates.",
            "Operational availability, real equipment, scheduling and worksite examples require operator evidence.",
            "Do not use this CSV to overwrite site content or grant indexability.",
        ],
        "officialCandidateReferences":[
            "https://www.data.go.kr/data/15077871/openapi.do",
            "https://www.data.go.kr/data/15129688/fileData.do",
            "https://sgis.mods.go.kr/developer/html/openApi/api/data.html",
        ],
    }
    (output/"region-evidence-gaps-summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("reports/quicksky"))
    args=parser.parse_args()
    print(json.dumps(export(args.output),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
