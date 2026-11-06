"""Verify all 310 official-code Skyquote pages for visitor-first copy and preserved provenance."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,re,importlib.util
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"dist/skyquote-official-preview"
m=json.loads((OUT/"national-manifest.json").read_text())
regions=json.loads((ROOT/"sites/skyquote/official-upper-regions-20261022.json").read_text())
assert len(regions["entries"])==284
assert m["totalContentPages"]==310 and m["nationalRecords"]==284 and m["ansanPreserved"]==25
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
class Visible(HTMLParser):
    def __init__(self):super().__init__();self.skip=0;self.parts=[]
    def handle_starttag(self,t,a):
        if t in ('style','script','head'):self.skip+=1
    def handle_endtag(self,t):
        if t in ('style','script','head'):self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip:self.parts.append(d)
spec=importlib.util.spec_from_file_location("skyquote_official_generator",ROOT/"scripts"/"build_skyquote_official.py")
generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
question_sets=set()
for path in m["paths"]:
    raw=(OUT/path).read_text(encoding="utf-8")
    assert 'name="robots" content="noindex,nofollow"' in raw,path
    assert raw.count("<img ")==5,path
    assert "AI 생성 설명 이미지" not in raw and "<figcaption>" not in raw,path
    if path!="national/index.html":
        for phrase in ("영진스카이 공개 이용요금","30만 원","부가세는 별도","작업 지점까지 높이(미터)","반나절 · 4시간","하루 · 8시간"):
            assert phrase in raw,(path,phrase)
        assert raw.count('loading="eager"')==1 and raw.count('loading="lazy"')==4,path
    for bad in ("업계 최저가를 주장하지 않습니다","업계 최저가 보장","무조건 최저가","전국 출동 가능합니다","즉시 배차 보장","차량 톤수만으로 안전조건을 단정하지 마세요","현장정보가 아닙니다","가격 보장 목록이 아닙니다","실제 현장의 증거가 아닙니다","실수를 피할 수 있습니다","단정하지 마세요","기재합니다","실제 시공·장비 보유 증명이 아닙니다"):
        assert bad not in raw,(path,bad)
    for a in manifest["assets"]:assert Path(a["path"]).name in raw,path
    assert 'href="//' not in raw,path
    for dest in re.findall(r'href="(/[^"#?]*)"',raw):
        target=OUT/"index.html" if dest=="/" else OUT/dest.lstrip("/")
        assert target.exists(),(path,dest)
    if path.startswith("national/") and path!="national/index.html":
        parser=Visible();parser.feed(raw)
        text=" ".join(parser.parts)
        assert "작업 지점까지 높이" in text and "작업대에 오를 인원" in text
        assert "공개 이용요금" in text
        import hashlib
        prompt_titles=[heading for heading,_body in generator.PROMPTS]
        headings=tuple(heading for heading in prompt_titles if '<h2>'+heading+'</h2>' in raw)
        assert len(headings)==4,(path,headings)
        assert len(set(headings))==4,path
        question_sets.add(headings)
assert len(question_sets)>90,len(question_sets)
print("SKYQUOTE_OFFICIAL_310_VISITOR_COPY_QA_PASS pages=310 questionSets="+str(len(question_sets))+" images=5 pricing=true links=true noindex=true")
