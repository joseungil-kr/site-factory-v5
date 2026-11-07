"""Create a deterministic standalone Sites handoff ZIP from the strict V5 build.

This is a FILE PACKAGE, never an external deployment or authorization change.
It preserves each of 95 routes, 404, CSS, SVG, robots/noindex and all assets.
The hosting service MUST still enforce owner-only access before publishing.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import zipfile

from v5.config import ROOT
from scripts.verify_county_independent_html import scan_tree

ID="county-funeral-ownerprivate-test"

def sha256(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def package():
    source=ROOT/"dist"/ID
    site=ROOT/"sites"/ID
    assert source.is_dir(), "Run the strict V5 county preview build first"
    cfg=json.loads((site/"site.json").read_text(encoding="utf-8"))
    plan=json.loads((site/"site-spec.json").read_text(encoding="utf-8"))
    assert cfg["id"]==ID and cfg["domain"] is None and cfg["publishEnabled"] is False
    assert cfg["indexNow"]["enabled"] is False
    assert plan["publishPolicy"]["mode"]=="owner-private-preview-only"
    assert plan["similarityAudit"]["thresholdExclusive"]==.49
    assert not (source/"sitemap.xml").exists()
    assert not (source/"rss.xml").exists()
    assert (source/"robots.txt").read_text(encoding="utf-8")=="User-agent: *\nDisallow: /\n"
    rows=json.loads((site/"pages.json").read_text(encoding="utf-8"))
    assert len(rows)==95
    scan=scan_tree(source,{p["number"]:p["productSkus"] for p in rows})
    assert scan["failedCount"]==0
    rootfiles=sorted([p for p in source.rglob("*") if p.is_file()])
    htmls=[p for p in rootfiles if p.suffix==".html"]
    assert len(htmls)==96 and len([p for p in htmls if p.name!="404.html"])==95
    for p in htmls:
        txt=p.read_text(encoding="utf-8")
        assert '<meta name="robots" content="noindex,nofollow">' in txt
        assert 'rel="canonical"' not in txt
    assert (source/"assets/images/county-wreath.svg").is_file()
    artifacts=ROOT/"artifacts"
    artifacts.mkdir(parents=True,exist_ok=True)
    name="county-funeral-ownerprivate-95-pages"
    zipfile_path=artifacts/(name+".zip")
    with zipfile.ZipFile(zipfile_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
        for item in rootfiles:
            relative=item.relative_to(source).as_posix()
            info=zipfile.ZipInfo(relative,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644<<16)
            bundle.writestr(info,item.read_bytes())
    with zipfile.ZipFile(zipfile_path) as bundle:
        assert len(bundle.namelist())==len(rootfiles)
        for item in rootfiles:
            assert bundle.read(item.relative_to(source).as_posix())==item.read_bytes()
    report={
        "siteId":ID,
        "purpose":"owner-private ChatGPT Sites trial handoff; not deployed",
        "sourceCommit":os.getenv("GITHUB_SHA") or "LOCAL_UNVERIFIED_COMMIT",
        "status":"READY_STATIC_BYTES_NOT_OWNER_PRIVATE_DEPLOYED",
        "htmlContentPages":95,
        "errorDocument":True,
        "assetFileCount":len(rootfiles)-len(htmls)-1, # non-HTML besides robots
        "fileCount":len(rootfiles),
        "rss":False,"sitemap":False,"noindex":True,
        "robotsDisallow":True,"indexNow":False,"publicRelease":False,
        "ownerOnlyAccessVerified":False,
        "files":{p.relative_to(source).as_posix():sha256(p) for p in rootfiles},
        "zipSha256":sha256(zipfile_path),
        "zipSizeBytes":zipfile_path.stat().st_size,
        "parentOfficialEvidence":"data/regions/v4_official_parent_regions_20261022.json",
        "officialArchiveSHA256":"44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd",
        "sellerPricingEvidenceRun":42361620276,
        "fullHTMLContract":scan["failedCount"]==0,
        "separateOwnerOnlySitesActionRequired":True,
    }
    manifest_path=artifacts/(name+"-manifest.json")
    manifest_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    hashfile=artifacts/(name+".sha256")
    hashfile.write_text(report["zipSha256"]+"  "+zipfile_path.name+"\n",encoding="utf-8")
    print("V51_OWNER_PRIVATE_STATIC_PACKAGE "+json.dumps({
        "sha256":report["zipSha256"],"sourceSHA":report["sourceCommit"],
        "html":report["htmlContentPages"],"files":report["fileCount"],
        "sizeBytes":report["zipSizeBytes"],"ownerPrivateLive":False,
    },ensure_ascii=False))
    return report

if __name__=="__main__":
    package()
