#!/usr/bin/env python3
"""Build 1,804 winterbbang HTML pages from the pinned Seoul/Gyeonggi name ledger.

Reads only V5-local files. Uses the approved sample design and five verified
WebP images. No Cloudflare, DNS, IndexNow, network, or AI API calls are made.
Generated pages are noindex previews until separate release controls pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
from collections import defaultdict
from html import escape as h
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts import winterbbang_render as sample
from v5.site_plan import require_site_plan

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sites/winterbbang"
LEDGER = ROOT / "data/regions/seoul_gyeonggi_current_dong.json"
REPORT = ROOT / "reports/winterbbang"
OUT = ROOT / "dist/winterbbang"
GROUPS = ("setting", "menu", "workflow", "supply", "equipment", "marketing", "site", "profit")
GROUP_HEADINGS = {
    "setting": "어떤 기존 매장에서 운영할까요?",
    "menu": "메뉴 구성과 시제품 준비",
    "workflow": "실제 영업 동선과 작업 시간",
    "supply": "반죽과 속재료 공급 계획",
    "equipment": "조리 기계와 설비 조건",
    "marketing": "기존 메뉴와 알리는 방법",
    "site": "판매 장소와 안전을 확인하세요",
    "profit": "매출총이익과 실제 운영비 구분",
}
REGION_SOURCE_SHA = "057679a9a6312dbb4dd284d2ca42856d40a828239b2483540a7000b630fc30eb"

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def short_id(text: str):
    return digest(text)[:12]

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def choose(items: list, key: str):
    assert items, key
    return items[int(digest(key)[:16], 16) % len(items)]

def source_data():
    source = read_json(LEDGER)
    spec = read_json(BASE / "site-spec.json")
    require_site_plan("winterbbang")
    rows = source["rows"]
    assert source["asOf"] == "2026-10-12"
    assert source["sourceSHA256"] == REGION_SOURCE_SHA == spec["serviceScope"]["sourceSHA256"]
    assert len(rows) == 1732 == spec["serviceScope"]["sourceRows"]
    assert len({tuple(row) for row in rows}) == 1732
    assert all(len(row) == 2 and row[0].startswith(("서울특별시", "경기도")) for row in rows)
    assert sum(r[1].endswith("동") for r in rows) == 1588
    assert sum(r[1].endswith("가") for r in rows) == 143
    assert sum(r[1].endswith("로") for r in rows) == 1
    assert sum(r[0].startswith("서울") for r in rows) == 807
    assert sum(r[0].startswith("경기") for r in rows) == 925
    assert len({r[0] for r in rows}) == 69
    assert spec["targetPageCount"] == 1804 and spec["approved"] is True
    assert spec["publishPolicy"]["searchReleaseAllowed"] is False
    return rows, spec

def pools():
    raw = read_json(BASE / "region-copy-pool.json")
    seed = read_json(ROOT / "docs/site-plans/winterbbang/copy-pool.seed.json")
    assert len(raw["blocks"]) == 96 and len(seed["blocks"]) == 64
    ext = defaultdict(list)
    for row in raw["blocks"]:
        assert row["family"] in GROUPS
        assert len(row["copy"].strip()) >= 60
        ext[row["family"]].append(row["copy"])
    assert all(len(ext[name]) == 12 for name in GROUPS)
    seed_by_family = defaultdict(list)
    for row in seed["blocks"]:
        seed_by_family[row["family"]].append(row)
    assert len(seed_by_family["startup-core"]) >= 5
    assert len(seed_by_family["ingredients-and-supply"]) >= 6
    return seed, ext, seed_by_family

def region_url(parent: str, dong: str):
    return "/r/" + short_id(parent + "|" + dong) + ".html"

def district_url(parent: str):
    return "/d/" + short_id(parent) + ".html"

def province_url(province: str):
    return "/p/" + short_id(province) + ".html"

def full_name(parent: str, dong: str):
    return parent + " " + dong

def province_of(parent: str):
    return "서울특별시" if parent.startswith("서울특별시") else "경기도"

def make_selection(parent: str, dong: str, ext: dict, seed_by_family: dict):
    key = parent + "|" + dong
    menu_families = ("menu-bungeoppang", "menu-ingeoppang", "menu-egg-bread", "menu-tenwon")
    shop_families = ("shop-in-shop-cafe", "shop-in-shop-unmanned", "shop-in-shop-produce",
                     "shop-in-shop-snackbar", "shop-in-shop-doughnut", "shop-in-shop-teahouse")
    start = choose(seed_by_family["startup-core"], key + "|start")
    shop_family = choose(list(shop_families), key + "|shop-family")
    shop = choose(seed_by_family[shop_family], key + "|shop")
    menu_family = choose(list(menu_families), key + "|menu-family")
    menu = choose(seed_by_family[menu_family], key + "|menu")
    supply = choose(seed_by_family["ingredients-and-supply"], key + "|supply")
    chosen = [choose(ext[family], key + "|" + family) for family in GROUPS]
    # The sample layout contains three explanatory cards; those are also
    # selected from independently authored V5 seed paragraphs.
    base_blocks = [start["decision"], shop["decision"], supply["decision"]]
    return base_blocks, [start["copy"], shop["copy"], menu["copy"], supply["copy"]] + chosen

def more_content(parent: str, dong: str, chosen: list, neighbors: list, district: str):
    # Four seed paragraphs precede eight independently authored topical blocks.
    headings = ["판매 공간과 첫 판매 준비", "기존 매장의 샵인샵 검토",
                "메뉴별 조리 방법", "식자재 공급과 보관"]
    headings += [GROUP_HEADINGS[g] for g in GROUPS]
    assert len(headings) == len(chosen) == 12
    sections = ['<section class="local-detail"><h2>' + h(full_name(parent,dong)) + ' 창업 체크리스트</h2>'
                '<p>해당 지역에서 실제 판매 장소를 정하기 전, 필요한 시설과 메뉴·원료를 점검하세요. '
                '이 안내는 지역 내 점포 운영이나 매출 실적을 의미하지 않습니다.</p>']
    for heading, paragraph in zip(headings, chosen):
        sections.append('<article class="copy"><h3>' + h(heading) + '</h3><p>' + h(paragraph) + '</p></article>')
    sections.append('</section>')
    links = [('<a href="' + district_url(parent) + '">' + h(parent) + ' 창업 안내</a>')]
    for parent2, dong2 in neighbors:
        if (parent2,dong2) != (parent,dong):
            links.append('<a href="' + region_url(parent2,dong2) + '">' + h(dong2) + ' 창업</a>')
    sections.append('<nav class="region-nav" aria-label="지역 창업 자료">' + "".join(links) + '</nav>')
    return "\n".join(sections)

EXTRA_CSS = """
.local-detail{padding-top:22px}.local-detail article{margin:12px 0;background:#fffaf2}
.local-detail h3{color:#4f2b15;font-size:1.12rem}.local-detail p{margin:8px 0}
.region-nav{display:flex;flex-wrap:wrap;gap:10px;padding:20px 0}
.region-nav a{padding:9px 12px;background:#fff4e9;border:1px solid #e7c7a8;border-radius:9px;text-decoration:none}
.directory-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:9px;list-style:none;padding:0}
.directory-list a{display:block;padding:10px 14px;border:1px solid #ead6c5;border-radius:8px;text-decoration:none;background:#fff}
@media(max-width:720px){.local-detail article{padding:15px}.directory-list{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

def extend_html(doc: str, addition: str):
    marker = '<section><div class="margin">'
    if doc.count(marker) != 1:
        raise ValueError("Approved template anchor missing or duplicated")
    doc = doc.replace(marker, addition + "\n" + marker)
    if doc.count("</style>") != 1:
        raise ValueError("Expected only one approved inline CSS style")
    return doc.replace("</style>", EXTRA_CSS + "</style>")

def directory_section(title: str, summary: str, links: list):
    parts = ['<section class="region-directory"><h2>' + h(title) + '</h2><p>' + h(summary) + '</p>',
             '<ul class="directory-list">']
    for label, path in links:
        parts.append('<li><a href="' + h(path) + '">' + h(label) + '</a></li>')
    parts.extend(['</ul>', '</section>'])
    return "".join(parts)

def robots():
    return "User-agent: *\nDisallow: /\n"

def error_page():
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex,nofollow"><title>페이지를 찾을 수 없습니다 | 백세푸드</title></head>'
            '<body><main><h1>페이지를 찾을 수 없습니다</h1><a href="/">홈으로 돌아가기</a></main></body></html>')

def render_all(out: Path, report: Path):
    rows, spec = source_data()
    seed, ext, seed_by_family = pools()
    basic = sample.load_pool(sample.POOL_DEFAULT)
    groups = defaultdict(list)
    for parent, dong in rows:
        groups[parent].append((parent, dong))
    provinces = ("서울특별시", "경기도")
    assert len(groups) == 69
    page_meta = []
    texts = {}
    written = set()
    def emit(path, doc, role, region=None):
        relative = "index.html" if path == "/" else path.lstrip("/")
        if relative in written:
            raise ValueError("Route collision: " + relative)
        if '<meta name="robots" content="noindex,nofollow">' not in doc:
            raise ValueError("Noindex preview gate failed: " + relative)
        if 'rel="canonical"' in doc:
            raise ValueError("Preview canonical not permitted")
        if "tel:0314070103" not in doc:
            raise ValueError("Telephone conversion missing")
        if "매출총이익률" not in doc or "순이익률" not in doc:
            raise ValueError("Margin disclosure missing")
        if any(term in doc for term in ("초도비용 0원", "월 100만 원", "월 최소 구매", "무조건 수익", "전 지역 매장 운영")):
            raise ValueError("Private/commercial claim leaked: " + relative)
        write(out / relative, doc)
        written.add(relative)
        page_meta.append({"path":path,"type":role,"region":region,"sha256":hashlib.sha256(doc.encode()).hexdigest()})
    home_links = [(p,province_url(p)) for p in provinces]
    home_html = sample.render(basic)
    home_html = extend_html(home_html,directory_section("서울·경기 지역별 붕어빵 창업 안내",
        "서울특별시와 경기도에서 창업 예정 지역을 선택해 메뉴와 판매 공간을 검토하세요.", home_links))
    emit("/",home_html,"home")
    for province in provinces:
        parents = sorted(p for p in groups if province_of(p) == province)
        content = directory_section(province + " 지역별 샵인샵·겨울 간식 창업",
          "하위 시·군·구별 창업 문의를 살펴보세요. 개별 동의 점포·실적을 확인했다고 뜻하지 않습니다.",
          [(p,district_url(p)) for p in parents])
        preset = {"name":province,"blocks":["initial-choice","coffee-pairing","batter-supply"]}
        emit(province_url(province), extend_html(sample.render(basic,preset),content),
             "province-hub",province)
    for parent in sorted(groups):
        children = sorted(groups[parent], key=lambda t:t[1])
        links = [(dong,region_url(par,dong)) for par,dong in children]
        content = directory_section(parent+" 지역명별 붕어빵 창업·샵인샵 안내",
           "해당 시·구 안에서 계획 중인 판매 장소를 선택하고 조리·식자재 조건을 상담해 보세요.", links)
        content += '<nav class="region-nav"><a href="' + province_url(province_of(parent)) + '">광역별 목록</a></nav>'
        preset = {"name":parent,"blocks":["initial-choice","coffee-pairing","batter-supply"]}
        emit(district_url(parent),extend_html(sample.render(basic,preset),content),"district-hub",parent)
    for parent,dong in rows:
        children=sorted(groups[parent],key=lambda t:t[1])
        index=children.index((parent,dong))
        neighbors=children[max(0,index-2):index]+children[index+1:index+3]
        base_decisions,chosen=make_selection(parent,dong,ext,seed_by_family)
        body=sample.render(basic, {"name":full_name(parent,dong),"blocks":base_decisions})
        addition=more_content(parent,dong,chosen,neighbors,parent)
        emit(region_url(parent,dong),extend_html(body,addition),"locality",full_name(parent,dong))
        texts[region_url(parent,dong)]="\n".join(chosen)
    assert len(page_meta)==1804==spec["targetPageCount"]
    assert len(texts)==1732
    # Check every generated link. An anchor may be a page route, fragment or tel.
    import re
    hrefs=set()
    for html_file in out.rglob("*.html"):
        html_text=html_file.read_text(encoding="utf-8")
        hrefs.update(re.findall(r'<a[^>]*\bhref="([^"]+)"',html_text))
    paths={m["path"] for m in page_meta}
    bad=[u for u in hrefs if u.startswith("/") and u not in paths]
    if bad:
        raise ValueError("Broken internal links: " + repr(sorted(bad)[:20]))
    write(out/"robots.txt",robots())
    write(out/"404.html",error_page())
    verified_assets=sample.copy_verified_assets(out)
    report.mkdir(parents=True,exist_ok=True)
    manifest={"siteId":"winterbbang","mode":"preview-noindex","regionSourceSHA256":REGION_SOURCE_SHA,
       "count":len(page_meta),"localityCount":len(texts),"hubCount":len(page_meta)-len(texts)-1,
       "uniqueURLCount":len({x["path"] for x in page_meta}),"titleSource":"approved sample design",
       "assets":verified_assets,"noSitemap":True,"published":False,"pages":page_meta}
    write(report/"manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    return texts,manifest

def grams(text: str):
    text = re.sub(r"\s+", "", text)
    return {text[i:i+5] for i in range(len(text)-4)}

def jaccard(a,b):
    return len(a&b)/len(a|b) if a or b else 1.0

def audit_similarity(narratives: dict, report: Path):
    all_items=sorted(narratives.items())
    # A stable 1% sample, compared against the entire 1,732-document population.
    rng=random.Random(20261029)
    sample_items=rng.sample(all_items,max(18,(len(all_items)+99)//100))
    all_grams=[grams(body) for path,body in all_items]
    id_by_path={p:i for i,(p,_) in enumerate(all_items)}
    max_pair={"a":None,"b":None,"value":0.0}
    comparisons=0
    above=0
    for key,text in sample_items:
        a=all_grams[id_by_path[key]]
        for (other,_),b in zip(all_items,all_grams):
            if key==other:continue
            score=jaccard(a,b)
            comparisons+=1
            if score>=0.49:above+=1
            if score>max_pair["value"]:
                max_pair={"a":key,"b":other,"value":round(score,6)}
    assert comparisons==len(sample_items)*(len(all_items)-1)
    assert above==0, f"Regional narrative copy overlap >= 0.49: {above} pairs, max {max_pair}"
    if len({digest(text) for text in narratives.values()})!=len(narratives):
        raise ValueError("Duplicate complete regional narratives")
    result={"site":"winterbbang","metric":"char-5gram-jaccard","population":"region narrative 4 seed and 8 extension paragraphs, excluding common boilerplate",
       "totalLocalities":len(all_items),"sampleCount":len(sample_items),"sampleSeed":20261029,
       "comparisons":comparisons,"maxPair":max_pair,"overlapAtOrAbove49Percent":above,
       "exactDuplicateNarratives":0,"passed":True,"limitations":"Sample vs all; not all-pairs and not SEO or official region-status proof."}
    write(report/"similarity.json",json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=OUT)
    ap.add_argument("--report",type=Path,default=REPORT)
    args=ap.parse_args()
    if args.out.resolve() in (ROOT,ROOT/"sites") or (ROOT/"sites") in args.out.resolve().parents:
        raise ValueError("Cannot overwrite source")
    args.out.mkdir(parents=True,exist_ok=True)
    content,manifest=render_all(args.out,args.report)
    audit=audit_similarity(content,args.report)
    print(json.dumps({"status":"PASS","pageCount":manifest["count"],"localities":manifest["localityCount"],
                      "districts":69,"provinces":2,"images":len(manifest["assets"]),"sampleAudit":audit["maxPair"],
                      "comparisons":audit["comparisons"],"previewOnly":True},ensure_ascii=False))
if __name__=="__main__":
    main()
