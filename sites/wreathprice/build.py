"""Isolated Wreath Price V5 sample generator. No deployment, no API calls."""
from pathlib import Path
from html import escape
import json, sys

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "site-spec.json").read_text(encoding="utf-8"))
OUT = ROOT / "dist"
ASSETS = ["funeral-wreath.webp","celebration-wreath.webp","flower-detail.webp","ribbon-guide.webp","florist-preparation.webp"]
CSS = """
*{box-sizing:border-box}body{margin:0;color:#253d30;background:#f7f8f4;font:16px/1.7 system-ui,'Malgun Gothic',sans-serif;word-break:keep-all}a{color:#275e3d}.wrap{max-width:1080px;margin:auto;padding:20px}header,main section{background:white}header{border-bottom:1px solid #dde6dc}.hero{background:linear-gradient(125deg,#e3f2df,#f7f0e5);padding:55px 0}h1{font-size:clamp(28px,5vw,46px);line-height:1.25}h2{font-size:clamp(22px,3vw,30px)}.note{padding:20px;background:#fff4dc;border-left:4px solid #947c40}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card{border:1px solid #dee6d9;border-radius:15px;overflow:hidden;padding:15px}.card img{display:block;width:100%;height:auto;aspect-ratio:1024/300;object-fit:cover}.muted{font-size:13px;color:#5c6a60}.btn{display:inline-block;background:#315e44;color:#fff;padding:9px 13px;border-radius:10px;text-decoration:none;font-weight:bold}table{border-collapse:collapse;width:100%;background:#fff}th,td{padding:14px;text-align:left;border-bottom:1px solid #e1e9dd}th{background:#edf3eb}.overflow{overflow:auto}.overflow table{min-width:670px}main section{padding:26px;margin:18px 0;border-radius:15px}footer{padding:35px;background:#244534;color:#fff}footer a{color:#fff}@media(max-width:700px){.cards{grid-template-columns:1fr}.hero{padding:30px 0}}
"""

def build():
    assert SPEC["siteId"] == "wreathprice"
    assert SPEC["deployment"].startswith("blocked")
    assert len(SPEC["regions"]) == 3 and len(SPEC["images"]) == 5
    image_dir = ROOT / "assets"
    if not all((image_dir / filename).is_file() for filename in ASSETS):
        raise SystemExit("BINARY_ASSETS_MISSING: attach five actual ImageGen WebP files before build")
    (OUT / "assets").mkdir(parents=True,exist_ok=True)
    (OUT / "assets" / "site.css").write_text(CSS,encoding="utf-8")
    for filename in ASSETS:
        (OUT / "assets" / filename).write_bytes((image_dir / filename).read_bytes())
    products=SPEC["catalog"]
    assert len(products) == 5 and all(p["orderUrl"].startswith("https://fwith.co.kr/shop/item.php?it_id=") for p in products)
    rows="".join(
        '<tr><td>'+escape(p["kind"])+'</td><td>'+escape(p["name"])+'</td><td>'+format(p["referenceKRW"],",")+
        '원 <small>기준가</small></td><td><a class="btn" href="'+escape(p["orderUrl"])+'" rel="noopener noreferrer" target="_blank">상품 확인·주문</a></td></tr>'
        for p in products)
    titles=["근조화환의 형태","축하화환의 형태","꽃 구성 확대","리본 배치","포장 준비 장면"]
    notes=["AI 안내 이미지: 실판매 상품 사양 아님","AI 안내 이미지: 납품 사진 아님",
           "AI 이미지: 실제 꽃의 수량·품종 보장 아님","AI 이미지: 리본 비용·문구 포함 여부 별도 확인",
           "AI 이미지: 실제 포장·배송 사례 아님"]
    photos="".join('<figure class="card"><img src="/assets/'+name+'" width="1024" height="300" loading="lazy" decoding="async" alt="'+escape(title+' — '+note)+'"><figcaption><strong>'+title+'</strong><p class="muted">'+note+'</p></figcaption></figure>'
        for name,title,note in zip(ASSETS,titles,notes))
    nav=" | ".join('<a href="/'+item["path"]+'">'+escape(item["label"])+'</a>' for item in SPEC["regions"])
    for region in SPEC["regions"]:
        label=region["label"]
        title=label+" 화환 가격, 근조·축하 상품과 최종 주문금액 | 알뜰화환"
        first=label+" 화환 주문을 준비할 때 상품 기준가와 배송·리본 추가 비용을 구분하세요. 최종 결제금액은 실제 배송지와 선택사항 확인 후 결정됩니다."
        venue="정확한 장례식장·예식장 또는 행사장명, 배송주소, 희망 도착 시각을 판매처에 확인하세요."
        body='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'''+escape(title)+'''</title><meta name="description" content="'''+escape(first)+'''"><link rel="stylesheet" href="/assets/site.css"></head><body><header><div class="wrap"><b>알뜰화환 · 가격 비교</b></div></header><section class="hero"><div class="wrap"><h1>'''+escape(title)+'''</h1><p>'''+escape(first)+'''</p><p class="muted">상품가 확인 기준: 근조 2026-10-22 · 축하 2026-10-30, 최종 결제금액 미확정</p></div></section><main class="wrap"><section><h2>'''+escape(label)+''' 화환 가격 핵심 답변</h2><p>'''+escape(venue)+'''</p><p class="note">최종금액 = 상품 기준가 + 확인된 배송 추가금 + 리본·옵션 비용(해당 시). <b>배송비·리본 포함 여부는 미확인</b>이므로 주문 전 확인하세요.</p></section><section><h2>확인된 근조·축하화환 가격표</h2><div class="overflow"><table><tr><th>종류</th><th>상품</th><th>표시 상품가</th><th>판매처 링크</th></tr>'''+rows+'''</table></div></section><section><h2>등급·꽃 구성·용도 비교</h2><p>근조는 3단 기본·고급·특대형의 꽃 구성과 장식이 다를 수 있으며 축하 3단과 축하 2단 오브제는 설치 형태가 다릅니다. 실제 품종·수량은 상품 상세에서 확인하세요.</p><div class="cards">'''+photos+'''</div></section><section><h2>최종금액·배송비·리본 점검</h2><ol><li>근조·축하와 상품 코드를 선택하세요.</li><li>배송지·시설 반입 규정과 희망 시각을 확인하세요.</li><li>배송 추가비가 있는지 확인하세요.</li><li>리본문구 포함 및 추가비를 확인하세요.</li><li>주문 화면의 실결제 총액을 확인한 뒤 결제하세요.</li></ol></section><section><h2>주문 정보와 지역 배송 조건</h2><p>'''+escape(label)+''' 지역명만으로 배송 가능·무료배송·당일 도착을 보장하지 않습니다. 수령 시설과 정확한 주소를 주문처에 전달하세요. 개인정보는 안내 사이트가 아닌 fwith.co.kr에서만 입력합니다.</p><p>'''+nav+'''</p><a class="btn" href="https://fwith.co.kr/" rel="noopener noreferrer">실제 판매처 확인</a></section><section><h2>자주 묻는 질문</h2><details><summary>화환 가격이 최종 결제액인가요?</summary><p>아닙니다. 추가 배송비와 리본·옵션 비용을 주문 단계에서 확인해야 합니다.</p></details><details><summary>표시 상품 사진과 안내 이미지가 같나요?</summary><p>아닙니다. 안내 이미지 5장은 AI 생성 예시이고 실제 상품 사양·배송 사례가 아닙니다.</p></details></section></main><footer><div class="wrap">알뜰화환 시안 · 전화 1844-0644 · 실제 주문은 fwith.co.kr에서 진행</div></footer></body></html>'''
        target=OUT/region["path"];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(body,encoding="utf-8")
        assert body.count('<img ')==5
        print("PREVIEW_PAGE",target.relative_to(OUT),len(body))
    (OUT/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")

if __name__=="__main__":build()
