"""Offline-only evidence-grounded regional buying guides: exactly three pages plus index.

No writes to operational HTML, canonical sitemap, Workers, redirects, DNS, or index state.
"""
from __future__ import annotations
from datetime import datetime
from html import escape as E
from pathlib import Path
from urllib.parse import urlsplit
import argparse,hashlib,json,shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD_BRANCH_SHA="3543f3a93ab6f38bd2a97a1281bbaaffcacddc90"
CASES=("ansan-opening","seoul-relocation","suwon-celebration")
def esc(v): return E(str(v),quote=True)
def asset(rel): return Path(__file__).resolve().parent/rel

def legacy_comparison(raw):
    rows=raw["records"]
    assert len(rows)==5034
    targets={
       "ansan-opening":("경기도","안산시"),
       "seoul-relocation":("서울특별시","종로구"),
       "suwon-celebration":("경기도","수원시")
    }
    output={}
    for slug,pair in targets.items():
        records=[]
        for i,row in enumerate(rows,1):
            parent=" ".join(map(str,row[:2]))
            # Exact city names in the candidate dataset can have '수원시 영통구'.
            if row[0]==pair[0] and pair[1] in row[1]:
                records.append({"oldPath":f"/r/{i:05d}.html","recordIndex":i,
                    "sourceRecord":row,"oldSiteHosts":[
                        "clinicflower.nalmada.net","clinicopen.nalmada.net","clinicpresent.nalmada.net"]})
        assert records,(slug,pair)
        output[slug]={"scope":"existing candidate names only; no region facility facts",
                      "matchedOldRecordCount":len(records),"examples":records[:5],
                      "existingURLChange":"NONE","redirect":"NONE",
                      "comparisonSource":OLD_BRANCH_SHA}
    return output

def source_link(ref,source):
    return '<a class="source" href="'+esc(source["url"])+'" target="_blank" rel="noopener noreferrer">['+esc(ref)+'] 공식 원문</a>'

def render_header(title,desc):
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow">'
            '<title>'+esc(title)+' | 꽃이랑 근거 검증 실험</title>'
            '<meta name="description" content="'+esc(desc)+'">'
            '<link rel="stylesheet" href="./style.css"></head><body>'
            '<header class="top"><div class="wrap bar"><a href="./index.html" class="logo">꽃이랑 <span>근거 검증 지역 구매안내</span></a>'
            '<div class="privacy">비공개 후보 · 운영 미반영</div></div></header>')
def nav(active):
    labels={"ansan-opening":"안산 · 개원식","seoul-relocation":"서울 · 이전 축하","suwon-celebration":"수원 · 축하화환"}
    return '<nav class="nav wrap" aria-label="대표 지역과 목적 전환">'+''.join(
      '<a href="./'+esc(k)+'.html" '+('aria-current="page"' if active==k else '')+'>'+esc(v)+'</a>'
      for k,v in labels.items())+'</nav>'
def cta():
    return ('<section class="cta" id="order"><div><h2>실제 주문 전 최종 확인</h2>'
            '<p>수령 기관의 정식 명칭·행사 날짜·받는 담당자·장소, 상품의 현재 가격과 배송 가능 여부를 판매처에 확인하세요.</p></div>'
            '<a href="tel:1844-0644" class="button">꽃이랑 전화 1844-0644</a></section>')
def footer():
    return '<footer class="footer"><div class="wrap">2026-11-11 조사 · 의료기관 공개 위치정보 참고 · 환자 개인정보 미수집 · 배송·반입 허용 미확인</div></footer></body></html>'

def render_case(c,ledger,sources):
    html=render_header(c["title"],c["region"]+" "+c["purpose"]+" 구매 판단에 참고할 공식 시설 위치와 과거 판매처 상품정보")
    html+=nav(c["id"])
    html+='<main class="wrap"><div class="eyebrow">REGIONAL EVIDENCE / '+esc(c["region"])+'</div><h1>'+esc(c["title"])+'</h1>'
    html+='<p class="lead">공식 위치·시설 안내를 읽고, 실제 새로 개원하거나 이전한 수령 기관과 주문 목적을 분리해 확인하는 사례입니다. 특정 의료기관의 개원·이전 또는 꽃 반입 허용을 주장하지 않습니다.</p>'
    html+='<div class="warning"><strong>시설 예시:</strong> '+esc(c["facility"])+' · '+esc(c["facilityRelation"])+'</div>'
    html+='<section class="section" id="verified"><div class="section-title"><span>01 / VERIFIED REFERENCE</span><h2>공식 자료에서 확인한 내용</h2></div>'
    html+='<p class="subtle">검증한 원문 범위만 표시합니다. 환자정보·진료기록은 수집하거나 사용하지 않았습니다.</p>'
    html+='<div class="facts">'
    for fact in c["facts"]:
        source=sources[fact["source"]]
        html+='<article class="fact" data-source-id="'+esc(fact["source"])+'"><div class="fact-mark">'+esc(fact["id"])+'</div><p>'+esc(fact["claim"])+'</p>'
        html+='<div class="source-row">'+source_link(fact["source"],source)+'<span>조회 2026-11-11 · '+esc(source["scope"])+'</span></div></article>'
    html+='</div></section>'
    html+='<section class="section" id="decision"><div class="section-title"><span>02 / DECISION FLOW</span><h2>'+esc(c["purpose"])+' 주문 의사결정</h2></div>'
    html+='<ol class="decisions">'
    for item in c["decisions"]:
        html+='<li><h3>'+esc(item["title"])+'</h3><p>'+esc(item["text"])+'</p>'
        if item["sourceFacts"]:
            html+='<div class="proof">판단 배경이 된 공식 사실: '+', '.join(esc(x) for x in item["sourceFacts"])+'</div>'
        else:html+='<div class="proof">일반 구매 준비 조언 · 특정 시설 정책 근거가 아님</div>'
        html+='</li>'
    html+='</ol></section>'
    html+='<section class="section" id="sku"><div class="section-title"><span>03 / SELLER ORIGINAL</span><h2>목적에 맞는 상품 원문 확인</h2></div>'
    html+='<p class="subtle">가격은 2026-11-05에 확인된 과거 판매처 기록이며 오늘의 판매가격이 아닙니다. 재고·실제 배송비·수령지역·도착일·상품 상세 URL 현재 응답은 미확인입니다.</p>'
    html+='<div class="products">'
    for sku in c["skus"]:
        product=ledger[sku]
        assert product["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id="+sku
        assert product["priceCurrentKRW"] is None and product["deliveryAreaCurrent"] is None
        html+='<article class="product" data-sku="'+esc(sku)+'"><div class="sku">'+esc(sku)+'</div>'
        html+='<h3>'+esc(product["name"])+'</h3><p>2026-11-05 확인된 판매처 표시가격 <strong>'+format(product["priceKRWHistorical"],",")+'원</strong></p>'
        html+='<p class="unknown">현재 가격·재고·배송 가능 지역 및 추가 배송비 미확인</p>'
        html+='<a href="'+esc(product["orderUrl"])+'" target="_blank" rel="noopener noreferrer">판매처 상품 원문 보기</a></article>'
    html+='</div></section>'
    html+='<section class="section"><div class="section-title"><span>04 / NOT VERIFIED</span><h2>주문 전에 아직 확인해야 할 사항</h2></div><ul class="unknown-list">'
    for unknown in c["unknown"]:html+='<li>'+esc(unknown)+'</li>'
    html+='</ul><p class="subtle">시설 주소 확인은 배송 가능·선물 수령·화환 설치 허가의 증거가 아닙니다. 필요한 수령처 동의와 판매처 조건은 별도 확인하세요.</p></section>'
    html+=cta()+'</main>'+footer()
    return html

def build(output):
    if output.exists():raise RuntimeError("Output directory exists; refusing overwrite "+str(output))
    evidence=json.loads((HERE/"evidence.json").read_text("utf-8"))
    cases=evidence["cases"];sources={x["id"]:x for x in evidence["sources"]}
    assert len(cases)==3 and {x["id"] for x in cases}==set(CASES)
    ledger_path=ROOT/"sites/nalmada-shared3/clinic-retail-candidate-ledger-20261111.json"
    ledger={x["sku"]:x for x in json.loads(ledger_path.read_text("utf-8"))["items"]}
    raw=json.loads((ROOT/"data/regions/nationwide_locality_candidates_5034.json").read_text("utf-8"))
    compare=legacy_comparison(raw)
    output.mkdir(parents=True)
    pages=[]
    for c in cases:
        for fact in c["facts"]:
            assert fact["source"] in sources
        assert c["id"] in CASES
        text=render_case(c,ledger,sources)
        file=output/(c["id"]+".html")
        file.write_text(text,"utf-8")
        assert 'noindex,nofollow' in text
        assert 'rel="canonical"' not in text
        pages.append(file.name)
    intro=render_header("공식 근거 기반 지역 구매 안내 3개 사례","안산 개원식, 서울 이전축하, 수원 축하화환 비교 후보")
    intro+='<main class="wrap"><div class="eyebrow">THREE VERIFIED REFERENCE CASES</div><h1>실제 지역 근거를 확인한<br>세 가지 구매 상황</h1>'
    intro+='<p class="lead">지역명만 바꿔 복제한 콘텐츠가 아닙니다. 공개된 공식 위치·시설 안내를 토대로 구매 전에 확인할 질문을 지역·목적별로 달리 구성했습니다. 다음 사례의 의료기관이 개원·이전 중이거나 꽃 반입을 허용한다는 뜻은 아닙니다.</p>'
    intro+='<div class="case-list">'
    for c in cases:
        intro+='<article class="case-card"><div class="eyebrow">'+esc(c["region"])+'</div><h2>'+esc(c["purpose"])+'</h2>'
        intro+='<p>'+esc(c["title"])+'</p><a href="./'+esc(c["id"])+'.html">공식 근거 확인하고 구매 안내 보기</a></article>'
    intro+='</div><p class="subtle">기존 324개 검수 경로와 운영 HTML은 그대로 보존합니다. 별도 후보 페이지로 운영 URL 대체·삭제·리디렉션하지 않습니다.</p></main>'+footer()
    (output/"index.html").write_text(intro,"utf-8")
    shutil.copyfile(HERE/"style.css",output/"style.css")
    (output/"evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n","utf-8")
    (output/"comparison-to-legacy.json").write_text(json.dumps(compare,ensure_ascii=False,indent=2)+"\n","utf-8")
    report={"prototypeHTML":4,"regionBuyingHTML":3,"oldPathsTouched":0,"redirects":0,
            "sitemapOrCanonical":False,"noindex":True,"caseIDs":list(CASES),
            "sourceIDs":sorted(sources),"legacyComparison":{x:compare[x]["matchedOldRecordCount"] for x in CASES},
            "historicalPriceOnly":True,"deliveryPermissionVerified":False}
    (output/"build-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    assert len(list(output.rglob("*.html")))==4
    print("CLINIC_EVIDENCE_BUILD="+json.dumps(report,ensure_ascii=False))
    return report
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--output",required=True,type=Path)
    build(a.parse_args().output.resolve())
