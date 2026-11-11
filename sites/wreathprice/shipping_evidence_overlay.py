"""Research-scoped seller fee overlay for the 50 frozen noindex audit HTML only.

Not imported by production generators. No network access and no write to live deploy
paths. Evidence is a historical seller-posted fee, never checkout confirmation.
"""
from __future__ import annotations
import csv
import hashlib
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"posted-shipping-evidence-50.json"
REGRESSION=("1111010100","1111010200","1123010100")
SKU_IDS=("B201","B203","B205","C205","C030")

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sku_links(text):
    return tuple(re.findall(r'https://fwith.co.kr/shop/item.php\?it_id=([A-Z0-9]+)',text))

def transform(text, entry, notices):
    if entry is None:
        return text
    assert 'noindex,nofollow' in text
    sources=entry["sourceUrls"]
    assert entry["sourceSkuIds"]==["B205","C030"]
    price=f'{entry["postedAdditionalFeeKRW"]:,}원'
    scope=entry["sourceRowScope"]
    # Explicit SKU-only fee evidence: do not write this figure into other SKU rows.
    info=(
      '<section data-proof="seller-posted-fee" aria-label="판매처 게시 추가배송비 근거">'
      '<h2>판매처 게시 추가배송비 참고 (최종 적용 미확인)</h2>'
      '<p>2026-11-11 검색 자료에서 <strong>'+html.escape(scope)+'</strong> 범위에 '
      '<strong>'+html.escape(price)+'</strong>의 추가배송비 안내 행이 확인됐습니다. '
      '판매처의 안내는 실제 배송 가능 여부, 최종 결제 요금, 현재 유효성을 확정하지 않습니다.</p>'
      '<p>이 게시 요율의 출처는 판매처 근조 특대 3단 <strong>B205</strong>와 '
      '축하 2단 오브제 <strong>C030</strong> 상품 상세 안내입니다. '
      '두 상품의 원문 링크는 위 상품 가격표에서 확인할 수 있습니다. '
      'B201·B203·C205의 동일 요율 적용은 확인하지 못했습니다.</p>'
      '<p>게시 정보 조회일 2026-11-11 · 원문 수정일 미상 · 실제 수령 주소와 주문일 적용 여부 미확인.</p>'
    )
    for notice in notices:
        if entry["regionCode"] not in notice["regionCodes"]:
            continue
        venue=("·".join(notice["venueNames"]) if notice.get("venueNames")
                else notice.get("venueFilter","해당 장례식장"))
        info+=(
          '<p class="venue-specific"><strong>지정 수령시설에 한한 판매처 공지:</strong> '
          +html.escape(venue)+' — '+html.escape(notice["description"])+'. '
          '이 지역 모든 시설에 적용되는 조건이 아니며 해당 시설의 현재 정책을 다시 확인해야 합니다. '
          '<a href="'+html.escape(notice["sourceUrl"],quote=True)+'">공식 주요공지사항</a> '
          '(2026-11-11 조회, 공지 갱신일 미상).</p>'
        )
    info+='</section>'
    if text.count("</main>") != 1:
        raise ValueError("Unexpected main closing tag")
    updated=text.replace("</main>",info+"</main>",1)
    assert sku_links(text)==sku_links(updated)
    assert len(sku_links(updated))==5
    for sku in SKU_IDS:
        assert sku in sku_links(updated)
    assert text.count("<img ")==updated.count("<img ")==5
    assert text.count('noindex,nofollow')==updated.count('noindex,nofollow')
    assert "<link rel=\"canonical\"" not in updated
    return updated

def apply(root:Path, selected:list, evidence_dir:Path):
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    assert ledger["indexEligibleRegions"]==0
    assert ledger["regionalFactsProven"]==0
    entries={r["regionCode"]:r for r in ledger["postedFees"]}
    assert len(entries)==20
    assert all(set(r["sourceSkuIds"])=={"B205","C030"} for r in entries.values())
    assert set(entries).issubset({r["code"] for r in selected})
    # Preserve all original 50 + 3 regression HTML unmodified in a separate audit directory.
    original=evidence_dir/"before-html"
    original.mkdir(parents=True,exist_ok=True)
    changed=evidence_dir/"html"
    changed.mkdir(parents=True,exist_ok=True)
    compare=[]
    for row in selected:
        code=row["code"]
        path=root/"locality"/(code+".html")
        before=path.read_text(encoding="utf-8")
        (original/path.name).write_text(before,encoding="utf-8")
        after=transform(before, entries.get(code), ledger["venueNotices"])
        (changed/path.name).write_text(after,encoding="utf-8")
        # QA-only dist tree: expose candidate HTML to real Chromium screenshotter.
        if code in entries:
            path.write_text(after,encoding="utf-8")
        assert (after==before) if code not in entries else (after!=before)
        compare.append(dict(code=code,regionName=row["name"],matched=code in entries,
                    postedAdditionalFeeKRW=entries[code]["postedAdditionalFeeKRW"] if code in entries else None,
                    sourceSkuIds=entries[code]["sourceSkuIds"] if code in entries else [],
                    sellerSources=entries[code]["sourceUrls"] if code in entries else [],
                    sourcesAsOf="2026-11-11" if code in entries else None,
                    liveDeliveryAvailable="unverified",sellerFeeCurrentlyEffective="unverified",
                    beforeSHA256=digest(before),afterSHA256=digest(after),
                    changed=before!=after))
    reg_before=evidence_dir/"regressions-before"
    reg_after=evidence_dir/"regressions"
    reg_before.mkdir(exist_ok=True);reg_after.mkdir(exist_ok=True)
    for code in REGRESSION:
        p=root/"locality"/(code+".html")
        text=p.read_text(encoding="utf-8")
        (reg_before/p.name).write_text(text,encoding="utf-8")
        out=transform(text,entries.get(code),ledger["venueNotices"])
        (reg_after/p.name).write_text(out,encoding="utf-8")
        assert 'noindex,nofollow' in out
    assert sum(row["changed"] for row in compare)==20
    assert sum(not row["changed"] for row in compare)==30
    (evidence_dir/"shipping-overlay-audit.json").write_text(
        json.dumps(dict(ledgerSHA256=hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
            sourceType="2026-11-11 indexed seller page, current checkout unverified",
            matched20=True,unmatched30Untouched=True,actualDeliveryConfirmed=0,
            venueRestrictionsConditional=True,comparison=compare),
            ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (evidence_dir/"shipping-50.csv").open("w",encoding="utf-8-sig",newline="") as f:
        cols=["code","regionName","matched","postedAdditionalFeeKRW","sourceSkuIds",
              "sellerSources","sourcesAsOf","liveDeliveryAvailable","sellerFeeCurrentlyEffective",
              "beforeSHA256","afterSHA256","changed"]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in compare:
            d=r.copy();d["sourceSkuIds"]="|".join(d["sourceSkuIds"])
            d["sellerSources"]="|".join(d["sellerSources"])
            w.writerow(d)
    return compare
