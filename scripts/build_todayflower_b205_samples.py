"""Produce and verify read-only B205 seller-posted-fee samples; no live HTML changes."""
from __future__ import annotations
import hashlib
from html import escape
import json
from pathlib import Path

from scripts.extend_todayflower_5070_b205_evidence import extend_rows, EXTRA

CSS = """*{box-sizing:border-box}body{font:16px/1.8 'Noto Sans CJK KR',sans-serif;background:#f4f8f4;color:#183c30;margin:0}.wrap{max-width:900px;margin:auto;padding:26px}.card{padding:28px;background:white;border:1px solid #dce7dc;border-radius:16px}h1{font-size:clamp(26px,4vw,36px);line-height:1.35}h2{font-size:22px}a{color:#1b694d;overflow-wrap:anywhere}.fine{color:#536d60;font-size:14px}@media(max-width:390px){.wrap{padding:12px}.card{padding:19px}h1{font-size:27px}}"""


def render(row):
    esc=lambda s:escape(str(s),quote=True)
    has_fee=bool(row["wreathpriceMatchedIds"])
    assert row["proposedRole"]=="regional_navigation"
    scope=row["regionName"]
    if has_fee:
        assert row["sellerPostedFeeSku"]=="B205"
        assert row["wreathpriceScopeKind"]=="explicit_locality_row"
        assert row["sellerPostedFeeSourceObservedAt"]=="2026-11-11"
        assert row["sellerPostedFeePublishedAt"] is None
        main=('<h2>B205 상품에 한정된 게시 추가배송비</h2>'
              '<p>적용 행정구역: <strong>'+esc(scope)+'</strong></p>'
              '<p>판매처가 게시한 금액: <strong>'+f'{row["sellerPostedFeeKRW"]:,}원'+'</strong></p>'
              '<p class="fine">상품 B205 한정 · 게시표 조회일 2026-11-11 · 게시일 미상 · '
              '현재 주문 적용·실제 배송가능 여부 미확인.</p>'
              '<p class="fine">원장에 기록된 판매처 행 범위: '+esc(row["sellerPostedFeeRowScope"])+'</p>'
              '<a href="'+esc(row["sellerPostedFeeSourceURL"])+'">B205 판매처 원문</a>')
    else:
        assert row["sellerPostedFeeKRW"] is None
        main=('<h2>현행 요율로 확인되지 않은 지역</h2>'
              '<p>지역: '+esc(scope)+'</p><p class="fine">이 지역 페이지에는 '
              'B205의 정확한 별도행 요율을 붙일 충분한 근거가 없습니다. '
              '배송비가 무료라는 뜻도 아닙니다.</p>')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><style>'+CSS+'</style>'
            '<title>지역별 상품 게시정보</title></head><body><main class="wrap">'
            '<div class="card"><h1>지역별 상품 게시정보</h1>'+main+'</div>'
            '</main></body></html>')


def main():
    rows,_=extend_rows()
    matched=[r for r in rows if r["wreathpriceMatchedIds"]]
    blocked=[r for r in rows if r["wreathpriceContextIds"] and not r["wreathpriceMatchedIds"]]
    EXTRA.mkdir(parents=True,exist_ok=True)
    chosen=(matched[:3] + blocked[:2])
    assert chosen, "No observed seller-posted sample remains to render"
    report=[]
    for row in chosen:
        file=EXTRA/("b205-sample-"+str(row["number"])+".html")
        html=render(row)
        file.write_text(html,encoding="utf-8")
        assert "noindex,nofollow" in html
        if row["wreathpriceMatchedIds"]:
            assert "B205" in html and row["regionName"] in html
            assert "2026-11-11" in html and "게시일 미상" in html
        else:
            assert "판매처가 게시한 금액" not in html
        report.append({"number":row["number"],"regionCode":row["regionCode"],
                       "regionName":row["regionName"],"matched":bool(row["wreathpriceMatchedIds"]),
                       "file":file.name,"sha256":hashlib.sha256(html.encode()).hexdigest()})
    (EXTRA/"sample-html-manifest.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_B205_HTML_SAMPLES "+json.dumps(
        {"count":len(report),"matched":sum(x["matched"] for x in report),
         "blocked":sum(not x["matched"] for x in report)},ensure_ascii=False))


if __name__=="__main__":
    main()
