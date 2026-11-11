"""Isolated evidence-backed regional buyer-document editorial experiment.

Output only under reports/todayflower-nalmada/three-region-research/.
One location-specific article (SeoSeok); other 2 held as research metadata,
not repeated buyer pages. No deployment or original URL changes.
"""
from __future__ import annotations
import hashlib
from html import escape
import json
from pathlib import Path
import shutil

from v5.config import ROOT,read_site
from scripts.extend_todayflower_5070_b205_evidence import extend_rows
from scripts.audit_todayflower_semantic_gate import article
from v5.audit import grams

SITE="todayflower-nalmada"
BASE=ROOT/"reports"/SITE/"three-region-research"
EVIDENCE=ROOT/"sites"/SITE/"isolated-three-region-evidence-20261111.json"
TARGET=(1039,4360,4582)
STYLE="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f8f5;color:#15382e;font:16px/1.8 'Noto Sans CJK KR',system-ui,sans-serif}main{max-width:940px;margin:auto;padding:24px}.hero{background:#e0f0e6;padding:28px;border-radius:20px}.eyebrow{color:#246c4b;font-weight:800;letter-spacing:.04em;font-size:13px}h1{font-size:clamp(28px,4.4vw,40px);line-height:1.35;margin:12px 0}h2{font-size:22px;margin:0 0 12px}section{background:white;border:1px solid #dce5df;border-radius:15px;padding:23px;margin:18px 0}.subtitle{color:#506d5d}.columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.steps{margin:0;padding-left:24px}.steps li{padding:8px 0}.status{color:#735521}.footnote{font-size:13px;color:#5b6c61}a{color:#13603f;overflow-wrap:anywhere}strong{font-weight:750}.tags{font-size:13px;color:#476a55}.links a{display:block;padding:8px 0}@media(max-width:520px){main{padding:12px}.hero{padding:20px}section{padding:17px}.columns{grid-template-columns:1fr}h1{font-size:28px}}"""
def h(t):return escape(str(t),quote=True)
def doc(title,body):
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow">'
            '<title>'+h(title)+'</title><style>'+STYLE+'</style></head>'
            '<body data-isolated="yes"><main><header class="hero">'
            '<span class="eyebrow">격리 편집 후보 · 근거 대조 전용 · 공개 불가</span>'
            '<h1>'+h(title)+'</h1>'
            '<p class="subtitle">시점이 다른 시설 안내와 상품 게시자료를 분리했습니다. '
            '실제 주문·배송 가능 여부는 검증되지 않았습니다.</p></header>'+body+'</main></body></html>')
def checksum(content):return hashlib.sha256(content.encode("utf-8")).hexdigest()
def main():
    data=read_site(SITE)
    assert data["site"]["publishEnabled"] is False
    assert data["site"]["indexNow"]["enabled"] is False
    rows,old=extend_rows()
    by={r["number"]:r for r in rows}
    evidence=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    by_research={r["number"]:r for r in evidence["regions"]}
    assert set(by_research)==set(TARGET)
    assert len(evidence["claimMap"])==4
    assert all(evidence["researchedOn"]=="2026-11-11" for _ in [0])
    sku_products={p["sku"] for p in data["products"]}
    assert "B205" in sku_products and "C030" not in sku_products
    original={}
    BASE.mkdir(parents=True,exist_ok=True)
    source=BASE/"original-html"
    source.mkdir(exist_ok=True)
    for n in TARGET:
        row=by[n]
        record=by_research[n]
        assert record["code"]==row["regionCode"] and record["name"]==row["regionName"]
        assert row["wreathpriceMatchedIds"] and row["sellerPostedFeeSku"]=="B205"
        assert row["sellerPostedFeeSourceObservedAt"]=="2026-11-11"
        assert row["sellerPostedFeeCurrentEffective"] is False
        original_path=ROOT/"dist"/SITE/f"{n}.html"
        assert original_path.is_file(),n
        actual=original_path.read_text(encoding="utf-8")
        assert 'noindex,nofollow' in actual
        (source/f"{n}.html").write_text(actual,encoding="utf-8")
        original[n]={"number":n,"sha256":checksum(actual),"characters":len(actual)}
    seo=by_research[4582]
    assert seo["decision"]=="detail_candidate_for_editorial_review"
    assert seo["facility"]=="서석장례식장"
    claims={x["id"]:x for x in evidence["claimMap"]}
    assert all(x["regionNumber"]==4582 for x in claims.values())
    # Each factual article statement is backed by the claim ledger; only
    # buyer-choice instructions are editorial process recommendations.
    article_html=doc("홍천 서석면 근조화환 주문 전 확인할 장례시설·B205 게시정보",
        '<section id="facility"><h2>1. 수령 시설부터 정확히 지정</h2>'
        '<p data-evidence-ids="S1">'+h(claims["S1"]["claim"])+'</p>'
        '<p data-evidence-ids="S2">'+h(claims["S2"]["claim"])+'</p>'
        '<p>주문지에 단순히 ‘서석면 장례식장’이라고 입력하기보다 '
        '<strong>서석장례식장</strong>과 본관·별관 중 실제 빈소의 위치를 구분해 준비하세요. '
        '이는 시설 구성에 따른 주문 정보 준비 방법이지, 화환 반입 허용을 뜻하지 않습니다.</p>'
        '<p data-evidence-ids="S3">'+h(claims["S3"]["claim"])+'</p>'
        '<p class="footnote">위 시설 정보는 홍천군청 공개 안내(페이지 최종수정 2023-01-02)를 '
        '2026-11-11 조회한 내용입니다. 접수처 전화번호가 현재 연결되는지 재확인하지 않았습니다.</p>'
        '<p><a href="https://www.hongcheon.go.kr/www/contents.do?key=348">'
        '홍천군청 서석장례식장 시설 안내 원문</a></p></section>'
        '<section id="sku"><h2>2. 상품 선택과 비용을 구분</h2>'
        '<p>현재 후보에서 대조하는 상품은 <strong>근조 특대 3단 화환 B205</strong>입니다. '
        '다른 SKU의 구성·배송비와 혼용하지 마세요.</p>'
        '<p data-evidence-ids="S4">'+h(claims["S4"]["claim"])+'</p>'
        '<p class="status">20,000원은 과거 판매처에 게시된 추가배송비 연구값입니다. '
        '현재 배송 가능, 현재 적용요금, 최종 결제금액은 확인되지 않았습니다.</p>'
        '<p><a href="https://fwith.co.kr/shop/item.php?it_id=B205">B205 판매처 상품 원문</a></p>'
        '<p class="footnote">판매처 연구 원장 2026-11-11 조회, 판매처 게시일·변경일 미상. '
        'C030 또는 B201의 동일 요율은 이 근거로 주장하지 않습니다.</p></section>'
        '<section id="handoff"><h2>3. 현장 인계 조건은 별도로 확인</h2>'
        '<ol class="steps"><li>실제 빈소가 본관인지 별관인지 유족·시설 담당자에게 확인합니다.</li>'
        '<li>시설 접수처에 <strong>외부 근조화환 반입 가능 여부·인수 위치·수령 담당자</strong>를 확인합니다.'
        ' 홍천군청의 시설 안내만으로 이 조건은 확인할 수 없습니다.</li>'
        '<li>판매처에 상품번호 B205·시설명·빈소 위치·희망 시각을 전달하고 '
        '현재 배송 가능성과 최종 추가배송비를 확인한 뒤 주문 여부를 결정합니다.</li></ol></section>'
        '<section id="evidence"><h2>원문 근거와 미확인 영역</h2>'
        '<div class="links"><a href="https://www.hongcheon.go.kr/www/contents.do?key=452">'
        '홍천군청 장례식장 운영 현황</a>'
        '<a href="https://www.hongcheon.go.kr/www/contents.do?key=348">'
        '홍천군청 서석장례식장 시설 소개</a>'
        '<a href="https://fwith.co.kr/shop/item.php?it_id=B205">'
        'B205 판매처 상품 상세</a></div>'
        '<p class="footnote">본문 사실 S1~S4는 별도 claim-ledger.json과 1:1 대응합니다. '
        '현재 빈소 이용 현황·시설의 최신 꽃 반입 규정·재고·배송 가능성과 최종 요금은 불명입니다.</p></section>'
        '<nav class="links"><a href="./index.html">세 지역 조사 결과로 돌아가기</a></nav>')
    (BASE/"seoseok-4582.html").write_text(article_html,encoding="utf-8")
    holds=[r for r in evidence["regions"] if r["decision"].startswith("hold")]
    assert len(holds)==2
    cards=""
    for r in holds:
        price=by[r["number"]]["sellerPostedFeeKRW"]
        assert price and r["facility"] is None
        cards+=('<section data-hold-region="'+str(r["number"])+'"><h2>'+h(r["name"])+' — 상세 보류</h2>'
                '<p>기존 URL: <code>/'+str(r["number"])+'.html</code>. '
                'B205의 과거 지역별 게시 추가배송비 '+f'{price:,}'+'원은 연구 원장에 있으나 '
                '<strong>해당 지역의 특정 장례시설 공식 위치·반입 조건을 검증하지 못했습니다.</strong></p>'
                '<p class="footnote">판매처 자료 조회일 2026-11-11, 게시일 미상, 현재 배송 가능 여부 미확인.</p>'
                '<p>추가 확보 필요: '+h("; ".join(r["unverified"]))+'</p></section>')
    index=doc("B205 근거 기반 3개 지역 편집 후보 검토",
        '<section><h2>검토 결과</h2><p>서석면은 공식 시설 주소와 본관·별관 정보를 확인해 '
        '시설 지정·상품 비교·현장 인계 확인의 세 단계로 구성했습니다. '
        '다만 현재 외부화환 반입과 배송 가능성은 확인되지 않았으며 공개 승인 대상이 아닙니다.</p>'
        '<p><a href="./seoseok-4582.html">서석면 근거 상세 후보 보기</a></p></section>'+cards)
    (BASE/"index.html").write_text(index,encoding="utf-8")
    (BASE/"claim-ledger.json").write_text(json.dumps({
        "source":str(EVIDENCE.relative_to(ROOT)),
        "claims":evidence["claimMap"],
        "sources":evidence["sources"],
        "held":holds},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Preserve and compare evidence bound source article, never count thin
    # holding briefs as qualified independent locality pages.
    import re
    actual_links=re.findall(r'<a href="([^"]+)"',article_html+index)
    link_check=[]
    for target in actual_links:
        if target.startswith("https://"):
            assert target in {s["url"] for s in evidence["sources"]}
            link_check.append({"href":target,"kind":"registered_official_source"})
        else:
            assert target.startswith("./") and "/" not in target[2:]
            assert (BASE/target[2:]).is_file()
            link_check.append({"href":target,"kind":"local_exists"})
    from v5.todayflower_regions import legal_regions
    official=dict(legal_regions(ROOT))
    for r in evidence["regions"]:
        assert official[r["code"]]==r["name"]
    # One evidence-led detail, two holds, zero guesses.
    result={
        "isolatedOnly":True,"originalUrlCountPreserved":5070,
        "regionCandidates":3,"evidenceLedDetailCandidates":1,
        "heldForMissingFacilityEvidence":2,"published":0,
        "buyerWorkflowDistinct":True,"factsMapped":4,
        "currentDeliveryVerified":0,"merchantRatesCurrentVerified":0,
        "sourceSellerLastModifiedKnown":False,
        "articleHtml":"seoseok-4582.html","heldReviewHtml":"index.html",
        "originalHtml":original,"linksVerified":link_check,
        "candidateFiles":{
          f:checksum((BASE/f).read_text(encoding="utf-8"))
          for f in ("index.html","seoseok-4582.html","claim-ledger.json")},
        "editorialApproved":False,
        "legacy49PercentGateUnchanged":True,
        "noProductionModification":True,
        "unresolved":{r["number"]:r["unverified"] for r in evidence["regions"]}
    }
    (BASE/"audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_THREE_REGION_RESEARCH "+json.dumps({
        "candidateDetail":1,"held":2,"claims":4,"links":len(link_check),
        "originals":len(original),"files":list(result["candidateFiles"])
    },ensure_ascii=False))
    return result
if __name__=="__main__":main()
