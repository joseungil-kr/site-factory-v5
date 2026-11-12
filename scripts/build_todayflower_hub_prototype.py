"""No-deploy two-document information architecture prototype (333 event regions).

Outputs only under reports/todayflower-nalmada/hub-prototype/.
The 333 region records remain data, never 333 new HTML documents.
"""
from __future__ import annotations
from collections import Counter
from html import escape
import hashlib
import json
from pathlib import Path
from v5.config import ROOT,read_site
from v5.todayflower_copy_pool import SCENARIOS
from scripts.extend_todayflower_5070_b205_evidence import extend_rows

OUT=ROOT/"reports/todayflower-nalmada/hub-prototype"
EVENT="행사장 꽃 반입"
HTML_FILES=("index.html","buying-guide.html")
STYLE="""*{box-sizing:border-box}body{margin:0;font:16px/1.7 'Noto Sans CJK KR',system-ui,sans-serif;background:#f5f7f6;color:#173b30}main{max-width:1040px;margin:auto;padding:24px}.hero{padding:24px;background:#deefe5;border-radius:15px}h1{font-size:clamp(26px,4vw,36px);line-height:1.35}h2{font-size:21px}section,.panel{background:white;border:1px solid #dbe6df;padding:20px;border-radius:14px;margin:16px 0}label{font-weight:700;display:block;margin:10px 0 5px}input,select,button{font:inherit;padding:10px;border:1px solid #b7cfc0;border-radius:8px;background:white;color:#173b30;max-width:100%;width:100%}button{cursor:pointer;text-align:left}button[aria-pressed=true]{background:#daf1e2;border-color:#34664a}a{color:#166344;overflow-wrap:anywhere}ul{padding-left:24px}.muted{color:#506b5d;font-size:14px}.chip{font-size:13px;font-weight:700;color:#255c40}.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}.results{max-height:320px;overflow:auto}.results li{margin:7px 0}.hidden{display:none}details{margin:12px 0}@media(max-width:520px){main{padding:10px}.hero{padding:16px}.row{grid-template-columns:1fr}section{padding:15px}h1{font-size:27px}}"""
def h(s):return escape(str(s),quote=True)
def wrap(title,body,*,script=""):
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow">'
            '<title>'+h(title)+'</title><style>'+STYLE+'</style></head><body>'
            '<main><header class="hero"><div class="chip">격리 정보구조 시험 · 비공개</div><h1>'
            +h(title)+'</h1><p class="muted">현재 배송 가능·접수·재고를 보장하지 않습니다.</p></header>'
            +body+'</main>'+script+'</body></html>')
def guide():
    sections=[]
    for i,(intent,focus,product,q1,q2,response) in enumerate(SCENARIOS):
        sections.append('<section id="intent-'+str(i)+'"><h2>'+h(intent)+'</h2>'
                        '<p>'+h(focus)+'</p><p>'+h(product)+'</p>'
                        '<p class="muted">상품 규격·현재가격·배송 가능 여부는 판매처에서 확인해야 합니다.</p>'
                        '</section>')
    body='<nav class="panel"><a href="./index.html">지역 검색으로 돌아가기</a></nav>'+''.join(sections)
    return wrap("꽃 선물 목적별 공통 구매 안내",body)
def generate():
    data=read_site("todayflower-nalmada")
    rows,source=extend_rows()
    bynum={p["number"]:p for p in data["pages"]}
    mapnum={r["number"]:r for r in rows}
    event=[p for p in data["pages"][33:] if p["topic"]==EVENT]
    assert len(event)==333 and len({p["number"] for p in event})==333
    guide_names=[p[0] for p in SCENARIOS]
    assert guide_names.count(EVENT)==1
    common_id=guide_names.index(EVENT)
    entries=[]
    for p in event:
        r=mapnum[p["number"]]
        e={"number":p["number"],"urlPath":r["urlPath"],"code":r["regionCode"],
           "name":r["regionName"],"parent":" ".join(r["regionName"].split()[:-1]),
           "province":r["regionName"].split()[0],"intent":EVENT,
           "guideAnchor":"intent-"+str(common_id),
           "verifiedPostedFee":None,"applicableFactIds":[],
           "currentAvailabilityVerified":False}
        if r["wreathpriceMatchedIds"]:
            assert r["sellerPostedFeeSku"]=="B205"
            e["verifiedPostedFee"]={"sku":"B205","amountKRW":r["sellerPostedFeeKRW"],
                 "sourceURL":r["sellerPostedFeeSourceURL"],"observedAt":r["sellerPostedFeeSourceObservedAt"],
                 "publishedAt":None,"currentEffective":False}
            e["applicableFactIds"]=r["wreathpriceMatchedIds"]
        entries.append(e)
    # The three exact B205 posting matches from the pinned source may not
    # belong to the 333-event cohort. Keep them visibly separate, never
    # inflate the event count or pretend they belong to the event cohort.
    proof=[]
    for r in rows:
        if not r["wreathpriceMatchedIds"]:continue
        assert r["sellerPostedFeeSku"]=="B205"
        proof.append({"number":r["number"],"code":r["regionCode"],"name":r["regionName"],
                      "parent":" ".join(r["regionName"].split()[:-1]),
                      "province":r["regionName"].split()[0],
                      "guideAnchor":"intent-"+str(common_id),
                      "verifiedPostedFee":{"sku":"B205","amountKRW":r["sellerPostedFeeKRW"],
                          "sourceURL":r["sellerPostedFeeSourceURL"],"observedAt":"2026-11-11",
                          "publishedAt":None,"currentEffective":False},
                      "pageRole":"research-only-not-detail"})
    assert len(proof)==3
    assert len({e["code"] for e in entries})==333
    assert len({e["number"] for e in entries})==333
    provinces=sorted({e["province"] for e in entries})
    body=('<section><h2>공식 지역명 검색·선택</h2><p class="muted">2026-10-22 고정 법정동 자료에서 '
          '확인된 행사장 꽃 반입 관련 333개 기존 지역을 탐색합니다. 개별 배송 가능 여부는 확인되지 않았습니다.</p>'
          '<div class="row"><div><label for="region-search">지역명 또는 법정동 코드 검색</label>'
          '<input id="region-search" placeholder="예: 제천시 산곡동 / 4315012300" autocomplete="off"></div>'
          '<div><label for="province">광역명 필터</label><select id="province"><option value="">모든 광역</option>'
          +''.join('<option value="'+h(p)+'">'+h(p)+'</option>' for p in provinces)
          +'</select></div></div>'
          '<p id="count" aria-live="polite"></p><ul id="results" class="results" aria-label="지역 검색 결과"></ul></section>'
          '<section id="selected" aria-live="polite"><h2>선택한 지역</h2>'
          '<p id="selection-status">검색 결과에서 지역을 선택해 주세요.</p>'
          '<dl><dt>선택 지역</dt><dd id="region-name">-</dd>'
          '<dt>상위 지역 표기</dt><dd id="region-parent">-</dd>'
          '<dt>고정 행정코드</dt><dd id="region-code">-</dd></dl>'
          '<p id="region-evidence">구체적인 지역·시설 배송조건은 아직 확인되지 않았습니다.</p>'
          '<div id="fee" class="hidden"><p id="fee-detail"></p><p class="muted">'
          '판매처 게시자료 조회일 2026-11-11, 게시일 미상, 현재 주문 적용/배송 가능 여부 미확인.</p>'
          '<a id="fee-source" href="">B205 판매처 근거 원문</a></div>'
          '<p><a id="common-link" href="./buying-guide.html#intent-'+str(common_id)+'">'
          '행사장 꽃 반입 공통 구매 안내 보기</a></p></section>'
          '<section><h2>별도 검증된 B205 게시 요율 사례</h2>'
          '<p class="muted">아래 3곳은 333개 행사장 탐색 대상과 별도로 수집한 판매처 연구 사례입니다. '
          '해당 상품·지역만의 과거 게시요율이지 배송 가능성 증거가 아닙니다.</p>'
          '<ul id="proof-list"></ul></section>')
    # No remote JS and no network: browser operates on embedded escaped JSON
    # with textContent only. User-selectable proof records remain distinct.
    script_data=json.dumps({"regions":entries,"proof":proof},ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    js="""const payload=JSON.parse(document.getElementById('data').textContent);
const items=payload.regions,proof=payload.proof;
const q=document.getElementById('region-search'),province=document.getElementById('province');
const out=document.getElementById('results'),count=document.getElementById('count');
const $=id=>document.getElementById(id);
const safeSource='https://fwith.co.kr/shop/item.php?it_id=B205';
function selectRegion(e){
 $('region-name').textContent=e.name;
 $('region-parent').textContent=e.parent;
 $('region-code').textContent=e.code;
 $('selection-status').textContent='선택한 지역의 원장 확인 상태';
 $('region-evidence').textContent='이 지역에서 현재 실제 시설 반입 규정, 주문 마감, 배송 가능 여부를 확인하지 못했습니다.';
 const fee=e.verifiedPostedFee; $('fee').classList.toggle('hidden',!fee);
 if(fee){if(fee.sku!=='B205'||fee.sourceURL!==safeSource||fee.currentEffective!==false)throw Error('invalid scope');
 $('fee-detail').textContent=e.name+' · 상품 B205의 게시 추가배송비 '+fee.amountKRW.toLocaleString('ko-KR')+'원 (확정 요금 아님)';
 $('fee-source').href=fee.sourceURL;}
 $('common-link').href='./buying-guide.html#'+e.guideAnchor;
 for(const b of out.querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.code===e.code));
}
function render(){
 const term=q.value.trim().toLowerCase(),pv=province.value;
 const filtered=items.filter(e=>(!pv||e.province===pv)&&(!term||e.name.toLowerCase().includes(term)||e.code.includes(term)));
 count.textContent=filtered.length+' / '+items.length+'개 지역';out.replaceChildren();
 for(const e of filtered){
  const li=document.createElement('li'),b=document.createElement('button');b.type='button';b.dataset.code=e.code;
  b.textContent=e.name+' ('+e.code+')';b.setAttribute('aria-pressed','false');
  b.addEventListener('click',()=>selectRegion(e));li.append(b);out.append(li);
 }
}
q.addEventListener('input',render);province.addEventListener('change',render);
for(const p of proof){const li=document.createElement('li'),btn=document.createElement('button');btn.type='button';
 btn.textContent=p.name+' · B205 게시 요율 근거 선택 (333개 탐색 지역과 별도)';
 btn.addEventListener('click',()=>{selectRegion(p);$('selection-status').textContent='별도 B205 연구 사례 · 333개 대상과 별도';});
 li.append(btn);$('proof-list').append(li);}
render();"""
    script='<script type="application/json" id="data">'+script_data+'</script><script>'+js+'</script>'
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"index.html").write_text(wrap("지역 탐색 통합 허브 — 333개 지역",body,script=script),encoding="utf-8")
    (OUT/"buying-guide.html").write_text(guide(),encoding="utf-8")
    (OUT/"regions-333.json").write_text(json.dumps(entries,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={"noDeploy":True,"existing5070UrlChanged":False,
             "sourcePopulation":333,"dataRows":len(entries),"supplementaryB205Proof":len(proof),
             "candidateHtmlDocuments":2,"originalRegionalHtmlDocuments":333,
             "commonBuyerAdviceOwners":1,"existingOriginalQualityStillFailed":True,
             "similarity49PercentNotApplicableToOneHub":True,
             "uniqueCodes":len({x["code"] for x in entries}),
             "withMatchingSkuFee":sum(bool(x["verifiedPostedFee"]) for x in entries),
             "unmappedRegionCount":sum(not x["verifiedPostedFee"] for x in entries),
             "sourceURLs":["https://fwith.co.kr/shop/item.php?it_id=B205"],
             "files":{"index.html":hashlib.sha256((OUT/"index.html").read_bytes()).hexdigest(),
                      "buying-guide.html":hashlib.sha256((OUT/"buying-guide.html").read_bytes()).hexdigest(),
                      "regions-333.json":hashlib.sha256((OUT/"regions-333.json").read_bytes()).hexdigest()},
             "editorialUtility":"Centralized guide answers intent; hub supports name/code search and exact archived parent names; no independent local delivery verification"}
    (OUT/"prototype-report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_HUB_PROTOTYPE "+json.dumps(summary,ensure_ascii=False),flush=True)
    return summary
if __name__=="__main__":generate()
