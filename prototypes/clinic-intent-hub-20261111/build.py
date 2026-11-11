"""Offline-only, fail-closed clinic intent-hub prototype builder.

Never modifies existing generated national sites, domains, Workers or SEO assets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
HOSTS=("clinicflower.nalmada.net","clinicopen.nalmada.net","clinicpresent.nalmada.net")
EXPECTED_SKUS={"D144","D149","C200","C206"}

def historic_sample(names):
    def rank(filename,prefix):
        return hashlib.sha256((prefix+"|"+filename).encode("utf-8")).digest()
    original=sorted(names,key=lambda n:rank(n,"clinic-editorial-20261111"))[:54]
    used=set(original)
    extra=sorted((n for n in names if n not in used and n!="00139.html"),
                 key=lambda n:rank(n,"clinic-editorial-new-20261111"))[:54]
    assert len(original)==len(extra)==54 and len(set(original+extra))==108
    return sorted(set(original+extra))

def build(output):
    if output.exists():raise RuntimeError("Refusing existing output: "+str(output))
    raw=json.loads((ROOT/"data/regions/v4_official_parent_regions_20261022.json").read_text("utf-8"))
    regions=raw["regions"]
    assert len(regions)==284
    assert raw["levels"]=={"province":16,"municipality":229,"ward":39}
    assert len({r["code"] for r in regions})==284
    assert all(r["sourceStatus"]=="존재" and r["level"] in raw["levels"] for r in regions)
    allowed={"code","name","fullName","level","parent","sourceRecord","sourceStatus"}
    region_document={
        "sourceRef":"data/regions/v4_official_parent_regions_20261022.json",
        "sourceGitBlobSHA":"13d43fc3f2492b29b1680858235fe0ac0cd10580",
        "sourceRetrievedDate":"2026-10-22",
        "sourceEffectiveDate":None,
        "currentStatusVerified":False,
        "levelCounts":raw["levels"],
        "regions":[{k:v for k,v in r.items() if k in allowed} for r in regions]
    }
    ledger=json.loads((ROOT/"sites/nalmada-shared3/clinic-retail-candidate-ledger-20261111.json").read_text("utf-8"))
    items=ledger["items"]
    assert {x["sku"] for x in items}==EXPECTED_SKUS
    for item in items:
        sku=item["sku"]
        assert item["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id="+sku
        assert item["priceKRWHistorical"]>0
        for field in ("priceCurrentKRW","stockCurrent","deliveryAreaCurrent","deliveryFeeCurrent","orderUrlCurrentHTTP"):
            assert item[field] is None,(sku,field)
    catalog={"scope":"2026-11-05 seller snapshot, not current price / delivery",
             "currentVerification":False,
             "items":[{key:item[key] for key in ("sku","name","priceKRWHistorical","priceObservedKSTDate","priceCurrentKRW","stockCurrent","deliveryAreaCurrent","deliveryFeeCurrent","orderUrl","orderUrlCurrentHTTP","sourceEvidenceUrl")} for item in items]}
    legacy=json.loads((ROOT/"data/regions/nationwide_locality_candidates_5034.json").read_text("utf-8"))
    assert legacy["counts"]["localities"]==5034
    legacy_rows=legacy["records"]
    assert len(legacy_rows)==5034
    sampled=historic_sample([f"{i:05d}.html" for i in range(1,5035)])
    old_rows=[]
    for host in HOSTS:
        for filename in sampled:
            idx=int(filename[:-5])
            name=legacy_rows[idx-1]
            old_rows.append({"host":host,"oldPath":"/r/"+filename,
                "legacyRegionRowId":idx,"legacyRecord":name,
                "migrationAction":"NONE; preserved comparison only",
                "prototypeRoute":"/index.html","notAutomaticRedirect":True})
    assert len(old_rows)==324
    manifest={
      "mode":"offline-only; never deploy",
      "legacySource":"data/regions/nationwide_locality_candidates_5034.json",
      "legacySourceBlob":"525eb4b5c9f9f046ce2bcbd96a3dcfb343be399d",
      "comparisonPopulation":"previous 54 plus fresh 54 per host, 324 unique HTML paths",
      "legacyOldURLCount":324,"legacyOldURLsPreserved":True,
      "legacyURLDeletionOrRedirect":False,
      "items":old_rows
    }
    output.mkdir(parents=True)
    for name in ("index.html","app.css","app.js"):
        shutil.copyfile(BASE/name,output/name)
    (output/"regions.json").write_text(json.dumps(region_document,ensure_ascii=False,separators=(",",":"))+"\n","utf-8")
    (output/"catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n","utf-8")
    (output/"legacy-comparison-324.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n","utf-8")
    report={"mode":"offline-only","prototypeHTML":1,"newRegionalHTML":0,"regionRecords":len(regions),
      "levels":raw["levels"],"skuCount":len(items),"legacyComparisonRecords":len(old_rows),
      "legacyURLsModified":0,"redirects":0,"sellerCurrentPricesVerified":False,
      "sourceOriginal":str(ROOT/"data/regions/v4_official_parent_regions_20261022.json")}
    (output/"build-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    generated=list(output.rglob("*.html"))
    assert len(generated)==1 and generated[0].name=="index.html"
    print("CLINIC_HUB_OFFLINE_BUILD="+json.dumps(report,ensure_ascii=False))
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    build(args.output.resolve())
