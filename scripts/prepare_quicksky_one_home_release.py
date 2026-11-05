"""Validate exact one-home release and write ONLY a config for existing bound Worker."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
from v5.config import read_site
from v5.quicksky_home_evidence import validate_home_evidence

def main():
    data=read_site("quicksky");site=data["site"]
    evidence=validate_home_evidence(site,data["pages"],data["rates"])
    assert site["homeIndexingApproved"] is True and site["publicIndexingApproved"] is False
    assert site["publishEnabled"] is False and site["indexNow"]=={"enabled":False,"key":None}
    assert evidence["indexablePaths"]==["/"]
    root=Path("dist/quicksky")
    report=json.loads(Path("reports/quicksky/audit.json").read_text())
    manifest=json.loads(Path("reports/quicksky/manifest.json").read_text())
    assert manifest["siteId"]=="quicksky" and manifest["mode"]=="home-indexing" and manifest["pageCount"]==1733
    assert not report["errors"]
    pages=list(root.glob("*.html"))
    assert len(pages)==1734 and (root/"1733.html").is_file()
    for page in pages:
        body=page.read_text()
        meta="index,follow" if page.name=="index.html" else "noindex,nofollow"
        assert '<meta name="robots" content="'+meta+'">' in body,page.name
        if page.name=="index.html":
            assert body.count('<link rel="canonical" href="https://quicksky.nalmada.net/">')==1
            assert "비용 상담 안내 보기" in body
            assert "실제 배차 가능 지역" in body
            assert 'tel:01053221952' in body and 'class="equip-art"' not in body
            assert 'id="regions"' not in body and 'href="/2.html"' not in body
        else:
            assert 'rel="canonical"' not in body,page.name
    assert (root/"robots.txt").read_text()=="User-agent: *\nAllow: /\nSitemap: https://quicksky.nalmada.net/sitemap.xml\n"
    tree=ET.parse(root/"sitemap.xml")
    ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls=[e.text for e in tree.findall(".//"+ns+"loc")]
    assert urls==["https://quicksky.nalmada.net/"]
    assert not list(root.glob("*indexnow*"))
    cfg={"name":"sfv5-quicksky-preview","compatibility_date":"2026-10-21",
         "main":"../../worker/index.js","workers_dev":True,"preview_urls":False,
         "keep_vars":False,
         "vars":{"V5_STAGING":"1","V5_PUBLIC_HOST":"quicksky.nalmada.net","V5_HOME_ONLY":"1"},
         "assets":{"directory":"../../dist/quicksky","binding":"ASSETS",
                   "html_handling":"none","not_found_handling":"404-page","run_worker_first":True}}
    assert not any(k in cfg for k in ("route","routes","triggers","zone_id"))
    path=Path("deploy/quicksky/staging.wrangler.json")
    path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(cfg,indent=2)+"\n")
    print("EXACT_ONE_HOME_RELEASE_REVIEW_PASS",{"indexable":["/"],
          "noindexRegionalPages":1732,"errorPageNoindex":True,
          "indexNow":False,"worker":cfg["name"],
          "otherDomainMappings":"unchanged (checked separately by provider readback)"})

if __name__=="__main__":main()
