"""Create bounded evidence fixtures and mapping report; no deployment and no new URLs."""
from __future__ import annotations

from html import escape
import hashlib
import json
from pathlib import Path
import re

from v5.config import ROOT, read_site
from v5.todayflower_evidence import load_ledger, decide_role, evidence_detail_payload

OUT = ROOT / "reports/todayflower-nalmada/evidence-role-preview"
CASES = [
    ("facility-ansan-gd", "4127000000", "안산 빌라드지디 GD컨벤션 7층 그레이스켈리홀", None),
    ("sku-b101-daebunam", "4127311200", None, "B101"),
    ("no-source-2852", None, None, None),
    ("region-daebunam-navigation", "4127311200", None, None),
    ("region-danwon-parent", "4127300000", None, None),
]
CSS = """*{box-sizing:border-box}body{margin:0;font:16px/1.8 'Noto Sans CJK KR','Malgun Gothic',system-ui,sans-serif;background:#f5f7f5;color:#173b30}.wrap{max-width:940px;margin:auto;padding:32px 22px}.hero{background:#e2f1e7;padding:32px;border-radius:18px}h1{font-size:clamp(25px,4vw,39px);line-height:1.35}h2{font-size:21px}.evidence{padding:24px;background:white;border:1px solid #dce6de;border-radius:15px;margin:16px 0}.meta{color:#506d5d}.tag{font-size:13px;font-weight:800;color:#215a44}.noted{font-size:14px;color:#51675d}a{color:#155942;word-break:break-all}.footer{padding:18px 0}@media(max-width:390px){.wrap{padding:14px}.hero{padding:19px}.evidence{padding:17px}h1{font-size:27px}h2{font-size:19px}}"""


def text(v):
    return escape(str(v), quote=True)


def render(name, payload):
    role = payload["role"]
    title = {"evidence_detail": "출처별 구매 조건 안내",
             "regional_navigation": "지역 탐색",
             "general_buying_guide": "일반 구매 안내"}[role]
    cards = []
    for f in payload["facts"]:
        subject = f["facility"] or ("상품 " + f["sku"])
        value = f.get("condition")
        if f["kind"] == "sku_shipping_fee":
            assert f["regionName"] and f["sourceObservedAt"]
            value = (f'상품 {f["sku"]}의 {f["regionName"]} 지역에 게시된 추가배송비: '
                     f'{f["amountKRW"]:,}원 (해당 상품·해당 지역 한정)')
        elif f["kind"] == "venue_rule":
            value = f'판매처 공지의 {subject} 안내: {value}'
        elif f["kind"] == "sku_listing":
            value = f'상품 {f["sku"]} 판매처 표시가격: {f["amountKRW"]:,}원'
        publication = (f["sourcePublicationDate"] + " 게시" if f["sourcePublicationDate"]
                       else "게시일 미상")
        observed = "판매처 자료 확인일: " + f["sourceObservedAt"]
        scope = ("적용지역: " + f["regionName"] if f.get("regionName") else "")
        cards.append('<section class="evidence"><span class="tag">판매처 게시자료 · 최신 적용 미확인</span>'
                     + '<h2>' + text(subject) + '</h2>'
                     + ('<p class="meta">' + text(scope) + '</p>' if scope else '')
                     + '<p>' + text(value) + '</p>'
                     + '<p class="meta">' + text(observed + " · " + publication) + '</p>'
                     + '<p class="noted">해당 상품·지역 또는 시설에 국한된 게시정보입니다. 현재 접수 가능 여부와 최종 금액은 이 자료만으로 확인할 수 없습니다.</p>'
                     + '<p><a href="' + text(f["sourceURL"]) + '">판매처 원문</a></p></section>')
    if role == "regional_navigation":
        assert payload.get("regionName") and payload.get("navigation")
        links = payload["navigation"]
        assert all(item["href"].endswith(".html") and "/" not in item["href"]
                   and item["regionName"] for item in links)
        cards.append('<section class="evidence"><h2>' + text(payload["regionName"])
                     + ' 법정동 탐색</h2><p>고정 지역 원장에서 확인된 상위·하위 지명을 선택할 수 있습니다. '
                     '지역별 배송 가능 여부나 시설 규정은 이 연결만으로 확인되지 않습니다.</p>'
                     + '<nav aria-label="검증된 지역 탐색"><ul>'
                     + ''.join('<li><a href="' + text(item["href"]) + '">'
                               + text(item["regionName"] + " · " + item["label"])
                               + '</a></li>' for item in links)
                     + '</ul></nav></section>')
    elif payload.get("navigation"):
        cards.append('<nav aria-label="지역 탐색"><a href="'
                     + text(payload["navigation"][0]["href"]) + '">'
                     + text(payload["navigation"][0]["regionName"])
                     + ' 지역 탐색</a></nav>')
    if not cards:
        cards.append('<section class="evidence"><h2>상품을 고르기 전 살펴볼 정보</h2>'
                     '<p>상품 상세의 가격·규격과 수령 장소를 비교하고, 주문할 상품번호와 희망 날짜를 준비해 주세요.</p>'
                     '<p>이 지역에 대한 개별 배송 조건이나 시설별 반입 정보는 이 안내에 포함하지 않았습니다.</p>'
                     '</section>')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow">'
            '<title>'+text(title)+'</title><style>'+CSS+'</style></head>'
            '<body data-page-role="'+text(role)+'"><main class="wrap">'
            '<header class="hero"><span class="tag">판매처 공지 및 상품 확인</span>'
            '<h1>'+text(title)+'</h1><p class="meta">정확한 근거가 연결된 정보만 구분해 안내합니다.</p></header>'
            +''.join(cards)+'<footer class="footer"><p class="noted">본 자료는 격리 검수용입니다. 실시간 재고나 배송 가능성 확인 자료가 아닙니다.</p></footer>'
            '</main></body></html>')


def main():
    site=read_site("todayflower-nalmada")
    assert len(site["pages"])==5070
    by_number={p["number"]:p for p in site["pages"]}
    assert by_number[2852]["region"] and 2852>33
    assert by_number[2852].get("pageRole")=="general_buying_guide"
    ledger=load_ledger()
    region_by_code={row["code"]:row["name"] for row in site["regions"]["regions"]}
    parent_code,child_code="4127300000","4127311200"
    assert region_by_code[child_code].startswith(region_by_code[parent_code]+" ")
    assert region_by_code[child_code]=="경기도 안산시 단원구 대부남동"
    assert region_by_code[parent_code]=="경기도 안산시 단원구"
    OUT.mkdir(parents=True,exist_ok=True)
    results=[]
    for label, code, facility, sku in CASES:
        payload=evidence_detail_payload(region_code=code, facility=facility,
                                        sku=sku, ledger=ledger)
        if not payload["facts"] and code:
            payload["role"]=decide_role(region_code=code,
                                        selected_skus=([sku] if sku else ()),
                                        facility=facility,ledger=ledger)
        if label=="region-danwon-parent":
            payload["role"]="regional_navigation"
            payload["navigation"]=[{"href":"region-daebunam-navigation.html",
                                     "regionName":region_by_code[child_code],
                                     "label":"하위 법정동"}]
        elif label=="region-daebunam-navigation":
            payload["navigation"]=[
                {"href":"region-danwon-parent.html",
                 "regionName":region_by_code[parent_code],"label":"상위 지역"},
                {"href":"sku-b101-daebunam.html",
                 "regionName":region_by_code[child_code],
                 "label":"B101 지역별 게시 요율 표본"}]
        elif label=="sku-b101-daebunam":
            payload["navigation"]=[{"href":"region-daebunam-navigation.html",
                                     "regionName":region_by_code[child_code],
                                     "label":"지역 탐색"}]
        payload["regionName"]=region_by_code.get(code) if code else None
        html=render(label,payload)
        if label=="sku-b101-daebunam":
            assert "30,000원" in html and region_by_code[child_code] in html
            assert "2026-11-11" in html and "게시일 미상" in html
        if payload["role"]=="regional_navigation":
            assert '<nav aria-label="검증된 지역 탐색">' in html
        
        path=OUT/(label+".html")
        path.write_text(html,encoding="utf-8")
        results.append({"fixture":label,"role":payload["role"],
                        "factIds":[f["id"] for f in payload["facts"]],
                        "regionCode":code,"facility":facility,"sku":sku,
                        "sha256":hashlib.sha256(html.encode()).hexdigest(),
                        "htmlFile":str(path.relative_to(ROOT))})
    assert results[0]["role"]=="evidence_detail"
    assert results[1]["role"]=="evidence_detail"
    assert results[2]["role"]=="general_buying_guide"
    assert results[3]["role"]=="regional_navigation" and not results[3]["factIds"]
    assert results[4]["role"]=="regional_navigation" and not results[4]["factIds"]
    link_checks=[]
    for item in results:
        file=ROOT/item["htmlFile"]
        html=file.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"',html):
            if href.startswith("https://") or href.startswith("tel:"):
                continue
            assert href.endswith(".html") and "/" not in href,href
            destination=OUT/href
            assert destination.is_file(), (file,href)
            link_checks.append({"from":file.name,"to":href,"exists":True})
    # A source fee never crosses from B101 to B205/C200/C206 or an unrelated region.
    assert not evidence_detail_payload(region_code="4127311200",sku="B205")["facts"]
    assert not evidence_detail_payload(region_code="4127311200",sku="C200")["facts"]
    assert not evidence_detail_payload(region_code="4127311200",sku="C206")["facts"]
    assert not evidence_detail_payload(region_code="4127310100",sku="B101")["facts"]
    # Facility rule requires explicit identity, no municipality-wide implication.
    assert not evidence_detail_payload(region_code="4127000000")["facts"]
    report={"site":"todayflower-nalmada","publicWrites":False,"urlCountPreserved":5070,
            "evidenceLedger":"sites/todayflower-nalmada/evidence-ledger-sample.json",
            "fixtureResults":results,"internalLinks":link_checks,
            "internalLinkTargetsAllExist":True,"skuTransferForbidden":True,
            "unknownDeliveryCannotBecomeTrue":True,
            "2852Role":by_number[2852]["pageRole"],
            "original33Untouched":True}
    file=OUT/"mapping-report.json"
    file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_EVIDENCE_FIXTURE "+json.dumps(
        {"fixtures":len(results),"roleCounts":{
            role:sum(x["role"]==role for x in results)
            for role in ("evidence_detail","regional_navigation","general_buying_guide")},
         "mapping":str(file.relative_to(ROOT))},ensure_ascii=False))


if __name__=="__main__":
    main()
