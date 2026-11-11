"""Isolated venue-specific WreathPrice buyer pages, two evidence-backed venues only.
No publish/index/write to production. Official ZIP and source HTML are read-only.
"""
from __future__ import annotations
import argparse, csv, hashlib, html, io, json, re, shutil, sys, zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]/"sites"/"wreathprice"
sys.path.insert(0,str(SITE))
import expand_lower

EXPECTED_ZIP="44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
SKUS={"B205":109000,"C205":149000,"C030":200000}
def esc(s):return html.escape(str(s),quote=True)

def legal_code(archive:Path, full_name:str):
    raw=archive.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED_ZIP
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert len(z.namelist())==1
        rows=list(csv.reader(io.StringIO(z.read(z.namelist()[0]).decode("cp949")),delimiter="\t"))
    matches=[r[0] for r in rows[1:] if len(r)==3 and r[1]==full_name and r[2]=="존재"]
    assert len(matches)==1,(full_name,matches)
    return matches[0]

def source_link(url,title):
    return '<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(title)+'</a>'

def document(record, css, media):
    is_funeral=record["eventType"]=="funeral"
    address=record["address"]
    quoted=record["sellerNotice"]["text"]
    official=record["identitySource"]["url"]
    notice="https://fwith.co.kr/page/notice.php"
    if is_funeral:
        heading="은하수공원 근조화환: 오브제 형태 확인부터"
        summary=("세종시설관리공단은 이 시설의 주소와 장례식장 존재를 확인해 줍니다. "
                 "꽃이랑 과거 공지에는 은하수공원 '오브제' 안내가 있지만 현재 시설 반입 규칙은 독립 확인되지 않았습니다.")
        decision=(
          '<section data-role="buyer-decision"><h2>1. 먼저 근조용 오브제 접수 가능 여부 확인</h2>'
          '<p>상품 이름에 오브제가 들어 있다고 시설에 적합한 것은 아닙니다. '
          '꽃이랑의 C030은 <strong>축하 2단 오브제</strong>로 기록돼 있어 '
          '근조용 오브제의 대체상품이라고 주장하지 않습니다.</p>'
          '<p>기존 B205는 <strong>근조 특대 3단</strong>으로 기록돼 있습니다. '
          '과거 게시된 오브제 안내에 맞는 상품이라고 확인된 것은 아닙니다. '
          '이 페이지에서 바로 주문 가능한 확정 SKU는 없습니다.</p>'
          '</section>'
          '<section data-role="venue-checklist"><h2>2. 빈소와 반입 형식을 먼저 확인</h2>'
          '<p>정확한 빈소 번호·수령인·희망 도착 시각을 정리하고, 시설에는 '
          '근조용 오브제의 규격·반입 위치·현재 접수 여부를 확인한 뒤 판매처의 '
          '실제 근조용 상품 목록과 대조하세요.</p></section>'
        )
        comparison=(
          '<div class="item"><strong>B205 · 근조 특대 3단</strong><p>2026-10-22 참고 표시가 109,000원. '
          '오브제 반입 가능 규격이라는 근거가 없습니다.</p>'+
          source_link("https://fwith.co.kr/shop/item.php?it_id=B205","B205 상품 원문 확인 (적합성 미확정)")+'</div>'
          '<div class="item"><strong>C030 · 축하 2단 오브제</strong><p>2026-10-30 참고 표시가 200,000원. '
          '축하용이므로 근조용으로 전용하지 않습니다.</p>'+
          source_link("https://fwith.co.kr/shop/item.php?it_id=C030","C030 축하 상품 원문 확인 (근조용 아님)")+'</div>'
        )
        art="funeral-wreath.webp"
        alt="근조화환 형태의 공용 참고 이미지이며 은하수공원 반입 가능 상품의 사진이나 배송 실적이 아닙니다"
    else:
        heading="원주 빌라드아모르 예식화환: 수령 날짜부터 확인"
        summary=("원주시가 공식 행사 장소를 '빌라드아모르, 북원로 2888'로 기록했습니다. "
                 "꽃이랑의 과거 공지에는 예식화환 전날 배송·당일 불가 안내가 있으나 "
                 "시설의 현행 정책으로 확인되지는 않았습니다.")
        decision=(
          '<section data-role="buyer-decision"><h2>1. 예식일과 반입 가능한 날짜 확인</h2>'
          '<p>판매처의 기존 공지에는 주차 사유로 예식 당일 화환이 어렵고 '
          '전날 배송한다는 안내가 있습니다. 이는 현재 적용되는 확정 규정이 아닙니다. '
          '예식일·홀 이름·반입 시간·전날 보관 가능 여부를 시설 기준으로 확인하세요.</p></section>'
          '<section data-role="venue-checklist"><h2>2. 축하 상품 형태와 설치 위치 비교</h2>'
          '<p>축하 3단과 축하 2단 오브제는 형태가 다릅니다. '
          '정확한 반입 허용 형태와 설치 공간을 확인한 후 판매처 상품 상세를 비교하세요. '
          '두 SKU 모두 이 시설에 현재 접수 가능하다고 검증되지 않았습니다.</p></section>'
        )
        comparison=(
          '<div class="item"><strong>C205 · 축하 특특대 3단</strong><p>2026-10-30 참고 표시가 149,000원. '
          '시설 반입·전날 수령 가능 여부 미확인.</p>'+
          source_link("https://fwith.co.kr/shop/item.php?it_id=C205","C205 상품 상세 확인")+'</div>'
          '<div class="item"><strong>C030 · 축하 2단 오브제</strong><p>2026-10-30 참고 표시가 200,000원. '
          '현장 설치 가능 여부 및 추가비용 미확인.</p>'+
          source_link("https://fwith.co.kr/shop/item.php?it_id=C030","C030 상품 상세 확인")+'</div>'
        )
        art="celebration-wreath.webp"
        alt="축하화환 형태의 공용 참고 이미지이며 빌라드아모르의 실제 설치 사례가 아닙니다"
    operator_section=''
    if is_funeral:
        operator_notice=record["operatorPolicyFollowup"]["operatorAnnouncement"]
        operator_guide=record["operatorPolicyFollowup"]["operatorUsageGuide"]
        assert operator_notice["publishedOn"]=="2018-10-01"
        operator_section=(
          '<section data-role="operator-dated-policy"><h2>은하수공원 운영기관의 2018년 공지</h2>'
          '<p>세종시설관리공단이 2018-10-01 게시한 공지에는 인조부품이 많은 '
          '기존 3단화환 반입 금지, 신근조화환대에 생화를 제작하여 빈소에 납품하는 '
          '방식이 명시돼 있습니다. 발인 후 지정 장소에서 폐기한다는 내용도 있습니다.</p>'
          '<p>이는 <strong>2018년 시행 공지의 내용</strong>이지, 2026-11-11 현재 '
          '개별 상품·크기·당일 반입을 확인한 결과는 아닙니다. '
          'B205가 신화환 규격을 충족한다고 단정하지 않고, 축하용 C030을 '
          '근조용 대체상품으로 권장하지 않습니다.</p>'
          '<p>'+source_link(operator_notice["url"],"운영기관 신근조화환 공식 공지(2018-10-01)")+'</p>'
          '<p>운영기관의 현재 공개 이용안내는 장례식장 이용절차와 24시간 상담을 '
          '소개하지만, 이는 24시간 화환 배송·반입 허용을 뜻하지 않습니다. '
          +source_link(operator_guide["url"],"운영기관 장례식장 이용안내")+'</p></section>'
        )
    figure=('<figure><img src="./assets/'+art+'" alt="'+esc(alt)+'" loading="eager" decoding="async" '
            'width="1024"><figcaption>공용 형태 참고 이미지 · 실제 판매 상품·시설 납품 사례 아님</figcaption></figure>')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width, initial-scale=1">'
      '<meta name="robots" content="noindex,nofollow">'
      '<title>'+esc(heading)+' | 알뜰화환 격리 시안</title>'
      '<link rel="stylesheet" href="./assets/style.css"></head>'
      '<body><header><div class="wrap"><span>알뜰화환 · 시설별 구매 검토 시안</span></div></header>'
      '<main class="wrap"><div class="hero"><p class="eyebrow">공식 주소 확인 · 현행 반입정책 미확인</p>'
      '<h1>'+esc(heading)+'</h1><p>'+esc(summary)+'</p></div>'
      '<section data-role="venue-identity"><h2>공식 확인된 수령 시설</h2>'
      '<p><strong>'+esc(record["facilityName"])+'</strong> · '+esc(address)+'</p>'
      '<p>'+source_link(official,"공식 시설·주소 출처")+'</p></section>'
      +decision+operator_section+
      '<section data-role="product-compare"><h2>3. 판매처 상품을 목적에 맞게 비교</h2>'
      '<div class="products">'+comparison+'</div></section>'
      '<section data-role="seller-notice"><h2>판매처 공지의 원문 범위와 한계</h2>'
      '<p>꽃이랑 판매처 공지에 <strong>'+esc(quoted)+'</strong>가 게시돼 있습니다. '
      '2026-11-11 조회 당시 확인된 내용으로 게시·수정일은 미상이며, '
      '현재 시설 운영자가 동일 규정을 적용하는지는 확인되지 않았습니다.</p>'
      '<p>'+source_link(notice,"꽃이랑 공식 주요공지사항 원문")+'</p></section>'
      '<section data-role="checkout-boundary"><h2>주문 전 마지막 확인</h2>'
      '<p>수령시설의 현재 반입 허용, SKU별 배송 가능 여부, 날짜·시간, '
      '리본과 추가 배송비, 최종 결제금액은 모두 미확인입니다. '
      '판매처 상품 링크는 상세정보 확인용이며 주문 가능·결제금액을 보장하지 않습니다.</p></section>'
      '<section data-role="visual-reference"><h2>상품 형태 참고</h2>'+figure+'</section>'
      '<section data-role="source-date"><h2>근거의 시점</h2>'
      '<p>주소는 시설 운영 공단·원주시 공개자료에서 확인했습니다. '
      '상품가격은 2026-10-22/30 보관 원장 기준이며 현재 판매가가 아닐 수 있습니다. '
      '실제 배송 지역·비용을 확정하는 지역·시설 행은 확보되지 않았습니다.</p></section>'
      '</main><footer><div class="wrap">격리 검수 전용 · 기존 50개 지역 표본 외 · 비공개·noindex</div></footer>'
      '</body></html>')

STYLE="""*{box-sizing:border-box}body{margin:0;font:16px/1.65 system-ui,'Malgun Gothic',sans-serif;color:#273b32;background:#f6f8f5;overflow-wrap:anywhere}header{background:#214b35;color:white;padding:15px 0}.wrap{max-width:960px;padding:0 20px;margin:auto}.hero{padding:35px 0}h1{font-size:clamp(26px,4vw,40px);line-height:1.3}.eyebrow{font-size:14px;color:#526c5b}section{background:#fff;border:1px solid #dbe3da;border-radius:12px;padding:22px;margin:16px 0}h2{font-size:clamp(19px,2.5vw,25px);margin-top:0}.products{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.item{border:1px solid #becfbe;border-radius:10px;padding:16px;min-width:0}.item a{display:block;background:#265c40;color:white;padding:12px;border-radius:7px;text-align:center;text-decoration:none;min-height:44px}a:focus-visible{outline:3px solid #d78f21;outline-offset:3px}figure{max-width:580px;margin:0}figure img{display:block;width:100%;height:auto;border-radius:8px}figcaption{font-size:13px;color:#596c61}footer{margin-top:25px;background:#214b35;color:white;padding:25px 0}@media(max-width:650px){.products{grid-template-columns:1fr}.wrap{padding:0 15px}section{padding:16px}}"""

def main(archive, out):
    evidence=json.loads((HERE/"facility-evidence.json").read_text())
    assert evidence["schemaVersion"]==1 and len(evidence["facilities"])==2
    assert archive.is_file() and hashlib.sha256(archive.read_bytes()).hexdigest()==EXPECTED_ZIP
    # Freeze old, general WreathPrice locality HTML for true before/after intent comparisons.
    rep=expand_lower.main(archive)
    assert rep["grandTotalHTML"]==4935
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True)
    comparison=[]
    for record in evidence["facilities"]:
        full_region=("세종특별자치시 산울동" if record["id"]=="sejong-eunhasu"
                     else "강원특별자치도 원주시 태장동")
        code=legal_code(archive,full_region)
        if record["localityCode"] is not None: assert code==record["localityCode"]
        old=(expand_lower.OUT/"locality"/(code+".html")).read_text(encoding="utf-8")
        folder=out/record["id"]
        (folder/"assets").mkdir(parents=True)
        (folder/"before.html").write_text(old,encoding="utf-8")
        (folder/"index.html").write_text(document(record,STYLE,None),encoding="utf-8")
        (folder/"assets"/"style.css").write_text(STYLE,encoding="utf-8")
        fn=("funeral-wreath.webp" if record["eventType"]=="funeral" else "celebration-wreath.webp")
        (folder/"assets"/fn).write_bytes((SITE/"assets"/fn).read_bytes())
        candidate=(folder/"index.html").read_text()
        assert 'noindex,nofollow' in candidate and 'rel="canonical"' not in candidate
        assert candidate!=old and candidate.count("shop/item.php?it_id=")==2
        assert "현재" in candidate and "미확인" in candidate
        assert all(t in candidate for t in ("venue-identity","buyer-decision","product-compare","checkout-boundary"))
        assert record["isOriginalFixed50"] is False
        comparison.append({"facilityId":record["id"],"localityCode":code,"localityName":full_region,
                           "beforeSHA256":hashlib.sha256(old.encode()).hexdigest(),
                           "afterSHA256":hashlib.sha256(candidate.encode()).hexdigest(),
                           "beforeGeneric":True,"afterVenueSpecific":True,
                           "sample":"out-of-fixed50","currentDeliveryProven":False,"indexEligible":False})
    result={"createdPages":2,"sourceZipSHA256":EXPECTED_ZIP,"baselineHTML":4935,
            "sameBaselineURLsChanged":0,"oldFixed50Changed":0,"indexEligible":0,"items":comparison}
    (out/"comparison.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    main(a.archive,a.out)
