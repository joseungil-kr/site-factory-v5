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

def scope_class(entry):
    """Only an individually named 읍/면/동 별도행 may be mapped to that locality."""
    if entry is None:
        return "no_seller_row"
    scope = entry["sourceRowScope"]
    locality = entry["regionName"].split()[-1]
    if "별도행" in scope and locality in scope and not any(
        marker in scope for marker in ("전체", "기본행", "단위 행")
    ):
        return "explicit_locality_row"
    return "broader_or_ambiguous_seller_row"


def transform(text, entry, notices):
    """Separate product facts, official region navigation, and purchase instructions.

    Shared statements remain shared; do not simulate uniqueness with synonyms.
    """
    assert 'noindex,nofollow' in text
    before_links = sku_links(text)
    kind = scope_class(entry)
    old_caution = "해당 수령지의 실제 주문 가능 여부와 추가 비용은 현재 검증된 자료가 없습니다."
    assert text.count(old_caution) == 1, "Unexpected source caution drift"
    # Evidence applies to SKU B205/C030 only; a county/city row is NOT an exact
    # 읍/면/동 fee. It remains context without a price on the locality page.
    if kind == "explicit_locality_row":
        new_caution = (
            "해당 수령지의 실제 주문 가능 여부와 최종 적용 추가비용은 아직 "
            "확인되지 않았습니다. B205·C030 상품 안내에는 이 지역 별도행의 "
            "게시 요율이 있으나 현재 주문에 적용되는 요금인지 확인되지 않았습니다."
        )
    else:
        new_caution = old_caution
    text = text.replace(old_caution, new_caution, 1)

    # One product comparison and one purchase guide, without another
    # hashed question pool that merely repeats the same basic price/FAQ.
    choice = re.search(r'<section class="customer-choice">.*?</section>', text, re.S)
    assert choice is not None
    text = text[:choice.start()] + text[choice.end():]
    text = text.replace('<section><h2>상품별 선택 기준</h2>',
                        '<section data-role="product-comparison"><h2>상품별 선택 기준</h2>',1)
    text = text.replace('<section><h2>결제 전 한 번에 확인</h2>',
                        '<section data-role="purchase-guidance"><h2>결제 전 한 번에 확인</h2>',1)
    text = text.replace('<section><h2>배송지에 적용되는 정보의 한계</h2>',
                        '<section data-role="region-navigation"><h2>지역명 탐색과 정보 범위</h2>',1)
    assert all('data-role="'+role+'"' in text for role in
               ('product-comparison','purchase-guidance','region-navigation'))
    faq_start = '<section><h2>실제 주문 전 확인 질문</h2>'
    faq_end = '</section>'
    start = text.find(faq_start)
    assert start >= 0
    end = text.find(faq_end, start)
    assert end > start
    # Existing purchase guide already explains final charges; keep only
    # actionable location and facility inputs in the one remaining FAQ.
    faq = ('<section data-role="facility-checklist"><h2>수령시설 확인</h2>'
           '<p>수령 시설명·도로명 주소·빈소 또는 행사장 위치와 희망일시를 '
           '판매처 주문서에 입력합니다. 실제 반입 가능 조건은 수령 시설의 '
           '현재 안내를 확인해야 합니다.</p></section>')
    text = text[:start] + faq + text[end+len(faq_end):]

    evidence = ''
    if entry is not None:
        assert entry["sourceSkuIds"] == ["B205","C030"]
        assert entry["appliesToLiveOrder"] == "unverified"
        scope = html.escape(entry["sourceRowScope"])
        if kind == "explicit_locality_row":
            fee = f'{entry["postedAdditionalFeeKRW"]:,}원'
            description = (
                '판매처 B205·C030 상품 안내에 <strong>'+scope+'</strong> 별도행의 '
                '게시 추가배송비 <strong>'+fee+'</strong>가 있습니다. '
                '이 금액은 현행 결제 적용금액이나 배송 가능 여부를 확정하지 않습니다.'
            )
        else:
            description = (
                '판매처 B205·C030 상품 안내에 <strong>'+scope+'</strong>의 '
                '상위 지역 요율 행이 있지만, 이를 이 읍면동의 게시 추가배송비 '
                '금액으로 확정할 수 없습니다. 여기에는 금액을 표시하지 않습니다.'
            )
        evidence = (
            '<section data-role="seller-evidence" data-scope="'+kind+'">'
            '<h2>판매처 게시 배송비 자료의 적용 범위</h2><p>'+description+'</p>'
            '<p>B201·B203·C205에는 이 게시 요율을 전용하지 않습니다. '
            '게시자료 조회일 2026-11-11, 원문 게시·수정일 미상, '
            '실제 수령지의 주문 가능 여부 및 현재 결제 요율 미확인. '
            '기준 원문: 기존 가격표의 B205 및 C030 판매처 상품 링크.</p>'
        )
        for notice in notices:
            if entry["regionCode"] not in notice["regionCodes"]:
                continue
            # Explicitly conditional on exact named recipient venue.
            names = '·'.join(notice["venueNames"]) if notice.get("venueNames") else notice.get("venueFilter","해당 장례식장")
            evidence += (
                '<p data-role="venue-only">지정 수령시설에 한한 과거 판매처 공지: '
                +html.escape(names)+' — '+html.escape(notice["description"])
                +'. 해당 지역 전체의 규칙이 아니며 현재 적용 여부 미확인. '
                '<a href="'+html.escape(notice["sourceUrl"],quote=True)
                +'">판매처 공지 원문</a> (2026-11-11 조회, 수정일 미상).</p>'
            )
        evidence += '</section>'
    assert text.count("</main>") == 1
    updated = text.replace("</main>", evidence+"</main>",1)
    assert sku_links(updated)==before_links
    assert len(before_links)==5 and all(s in before_links for s in SKU_IDS)
    assert updated.count('<img ')==text.count('<img ')==5
    assert updated.count('noindex,nofollow')==1
    assert 'rel="canonical"' not in updated
    if kind != "explicit_locality_row":
        # Broad-scope rows must never imply a local amount.
        assert 'data-scope="explicit_locality_row"' not in updated
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
