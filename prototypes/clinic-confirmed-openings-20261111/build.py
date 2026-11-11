"""Build two strictly archival, source-confirmed opening examples. No site deployment."""
from pathlib import Path
from html import escape as esc
import json,shutil,argparse,hashlib
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
PRODUCTS={"D144","D149","C200","C206"}
def cards(case,items):
    content=""
    for sku in case["skus"]:
        x=items[sku]
        assert x["priceCurrentKRW"] is None and x["deliveryAreaCurrent"] is None
        assert x["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id="+sku
        content+=f'<article class="product" data-sku="{esc(sku)}"><div class="sku">{esc(sku)}</div><h3>{esc(x["name"])}</h3><p>2026-11-05 판매처 기록 <strong>{x["priceKRWHistorical"]:,}원</strong> (현재 판매가 아님)</p><p class="unknown">현재 가격·재고·배송비·배송 가능 지역·링크 응답 미확인</p><a href="{esc(x["orderUrl"])}" rel="noopener noreferrer" target="_blank">판매처 원문 SKU 페이지</a></article>'
    return content
def article(case,items):
    title=f'{case["region"]} {case["target"]} {case["event"]} — 과거 공식 기록'
    text=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(title)}</title><link rel="stylesheet" href="style.css"></head><body><header class="top"><div class="wrap bar"><a class="logo" href="index.html">꽃이랑 <span>의료기관 개원 사실·구매 검증</span></a><span class="privacy">비공개 · 과거 기록</span></div></header><main class="wrap"><div class="eyebrow">HISTORICALLY CONFIRMED EVENT</div><h1>{esc(title)}</h1>'
    text+=f'<div class="warning">이 기관의 {esc(case["event"])}은 <b>{esc(case["eventDate"])}</b>에 발생한 과거 사실입니다. 2026년 11월 현재 진행되는 신규 행사나 배송 주문 대상이라는 뜻이 아닙니다.</div>'
    text+=f'<section class="section"><div class="section-title"><span>01 / HISTORIC FACTS</span><h2>공식 원문에서 확인한 사실</h2></div><div class="facts">'
    facts=[("기관 및 사건",f'{case["target"]} — {case["event"]}'),("행사·개소일",case["eventDate"]),("공식 안내 주소",case["address"]),("공간 안내",case["floor"])]
    if case.get("startOfCare"):facts.insert(2,("진료 개시일 (기념식과 구분)",case["startOfCare"]))
    for i,(h,v) in enumerate(facts):
        text+=f'<article class="fact"><span class="fact-mark">{i+1:02d}</span><div><strong>{esc(h)}</strong><p>{esc(v)}</p></div></article>'
    text+='</div><p class="subtle">다음 출처는 기관·날짜·주소·층별 안내의 근거이며, 꽃 반입 허가를 입증하지 않습니다.</p>'
    for x in case["officialSources"]:
        text+=f'<p class="source-row"><a class="source" data-source="{esc(x["id"])}" href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">공식 자료 [{esc(x["id"])}]</a><span> {esc(x["publisher"])} · {esc(x["scope"])} · 게시일 {esc(x["noticeDate"] or "미표기")} · 조회 2026-11-11</span></p>'
    text+='</section><section class="section"><div class="section-title"><span>02 / ORDER DECISIONS</span><h2>이 기록으로 구분할 구매 조건</h2></div><ol class="decisions">'
    for decision in case["decision"]:text+=f'<li><p>{esc(decision)}</p></li>'
    text+='</ol></section><section class="section"><div class="section-title"><span>03 / SELLER SNAPSHOT</span><h2>과거 상품 정보 확인</h2></div><p class="subtle">다음 가격은 2026-11-05 보존 판매처 기록이며 현재 유효성이 검증되지 않았습니다.</p><div class="products">'+cards(case,items)+'</div></section>'
    text+='<section class="section"><h2>확인되지 않은 내용</h2><ul class="unknown-list"><li>해당 의료기관의 꽃·화환 수령 허용 여부</li><li>현장 반입 가능 출입구·수령 담당자 및 허용 시간</li><li>오늘의 주문 가격·재고·배송비·지역별 배송 가능 여부</li><li>현재 진행 중인 개원·이전 행사 여부</li></ul></section>'
    text+='<section class="cta"><div><h2>현재 진행 행사로 오해하지 마세요</h2><p>역사적 사례를 참고해 일반 상품 조건을 알아볼 수는 있지만, 이 기관의 과거 행사에 현재 배송을 예약하는 안내가 아닙니다.</p></div><a class="button" href="tel:1844-0644">일반 상품 전화문의 1844-0644</a></section>'
    return text+'</main><footer class="footer"><div class="wrap">2026-11-11 공식 기록 검토 · 역사적 사례만 · 운영·색인 미반영 · 개인 건강정보 없음</div></footer></body></html>'
def build(out):
    if out.exists():raise RuntimeError("No overwrite")
    ev=json.loads((BASE/"evidence.json").read_text("utf-8"))
    assert len(ev["approvedCases"])==2 and len(ev["deferredCases"])==2
    ledger=json.loads((ROOT/ev["retailerSource"]).read_text("utf-8"))
    items={x["sku"]:x for x in ledger["items"]}
    assert set(items)==PRODUCTS
    old=json.loads((ROOT/"data/regions/nationwide_locality_candidates_5034.json").read_text("utf-8"))
    assert len(old["records"])==5034
    out.mkdir(parents=True)
    shutil.copyfile(ROOT/"prototypes/clinic-evidence-regions-20261111/style.css",out/"style.css")
    summaries={}
    for c in ev["approvedCases"]:
        doc=article(c,items)
        path=out/(c["id"]+".html")
        path.write_text(doc,"utf-8")
        oldrow=old["records"][c["legacy"]["index"]-1]
        assert c["region"].endswith(oldrow[2]) and c["legacy"]["path"]==f'/r/{c["legacy"]["index"]:05d}.html'
        summaries[c["id"]]={"oldRoute":c["legacy"]["path"],"oldSite":c["legacy"]["site"],"oldRegionRow":oldrow,
            "eventDate":c["eventDate"],"sourceIDs":[x["id"] for x in c["officialSources"]],
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"newCandidate":path.name,
            "oldURLChanged":False,"liveDeliveryAllowed":None,"currentOpening":False}
    nav='<div class="case-list">'+''.join(f'<article class="case-card"><h2>{esc(c["target"])}</h2><p>{esc(c["eventDate"])} {esc(c["event"])}</p><a href="{esc(c["id"])}.html">과거 공식 사실과 구매 판단 읽기</a></article>' for c in ev["approvedCases"])+'</div>'
    index='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>개원 공식확인 과거 사례</title><link rel="stylesheet" href="style.css"></head><body><main class="wrap"><div class="eyebrow">OFFLINE EVIDENCE TEST</div><h1>의료기관 공식 개원 기록</h1><p>과거 날짜가 확인된 사례만 검토합니다. 현재 개원·배송 영업 대상이 아닙니다.</p>'+nav+'<p>안산 구강보건센터는 개소 사후 증거가 없어 보류했습니다. 의료기관 이전의 현재 공식 확정 사례도 이 범위에서는 찾지 못했습니다.</p></main></body></html>'
    (out/"index.html").write_text(index,"utf-8")
    (out/"evidence.json").write_text(json.dumps(ev,ensure_ascii=False,indent=2)+"\n","utf-8")
    report={"generatedHTML":3,"evidenceConfirmedHistoricCaseCount":2,"deferredCount":2,
        "newRegionalGenerated":2,"oldRoutesModified":0,"redirects":0,"deployment":False,
        "cases":summaries}
    (out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    assert len(list(out.glob("*.html")))==3
    print("HISTORIC_OPENING_BUILD "+json.dumps(report,ensure_ascii=False))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);build(ap.parse_args().out.resolve())
