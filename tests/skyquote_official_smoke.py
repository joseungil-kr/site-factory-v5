"""Verify 310 informational Skyquote pages from official upper-code snapshot."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"dist/skyquote-official-preview"
m=json.loads((OUT/"national-manifest.json").read_text())
regions=json.loads((ROOT/"sites/skyquote/official-upper-regions-20261022.json").read_text())
assert len(regions["entries"])==284
assert m["totalContentPages"]==310 and m["nationalRecords"]==284
assert m["nationalInfoPages"]==284 and m["ansanPreserved"]==25
assert m["serviceCoverageConfirmed"] is False and m["noIndex"] and m["noSitemap"]
assert not (OUT/"sitemap.xml").exists()
assert (OUT/"robots.txt").read_text()=="User-agent: *\nDisallow: /\n"
assert len(set(m["paths"]))==310
manifest=json.loads((ROOT/"sites/skyquote/assets-manifest.json").read_text())
for a in manifest["assets"]:
    raw=(OUT/"assets"/Path(a["path"]).name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==a["sha256"]
names={x["fullName"] for x in regions["entries"]}
for required in ("서울특별시 강서구","인천광역시 영종구","인천광역시 제물포구","인천광역시 서해구","인천광역시 검단구","전남광주통합특별시","강원특별자치도","전북특별자치도"):
    assert required in names,required
questions=set()
for path in m["paths"]:
    p=OUT/path
    raw=p.read_text(encoding="utf-8")
    assert 'name="robots" content="noindex,nofollow"' in raw,path
    assert raw.count("<img ")==5,path
    assert "업계 최저가를 주장하지 않습니다" in raw or path=="national/index.html",path
    for bad in ("업계 최저가 보장","무조건 최저가","전국 출동 가능합니다","즉시 배차 보장"):
        assert bad not in raw,(path,bad)
    for a in manifest["assets"]:assert Path(a["path"]).name in raw,path
    assert 'href="//' not in raw,(path,'scheme-relative URL is not allowed')
    for dest in re.findall(r'href="(/[^"#?]*)"',raw):
        target=OUT/"index.html" if dest=="/" else OUT/dest.lstrip("/")
        assert target.exists(),(path,dest)
    if path.startswith("national/") and path!="national/index.html":
        titles=tuple(re.findall(r'<h2>(.*?) 비교 질문</h2>',raw))
        assert len(titles)==4 and len(set(titles))==4,path
        questions.add(titles)
assert len(questions)>150,len(questions)
print("SKYQUOTE_OFFICIAL_310_QA_PASS pages=310 upperRegions=284 ansan=25 questionSets="+str(len(questions))+" imageHashes=5 links=valid noindex=true")
