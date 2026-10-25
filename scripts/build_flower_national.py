"""Independent nationwide florist information site. No unverified product listings."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse, json

DOMAIN="https://flower.nalmada.net"
PHONE="1844-0644"
PAGES=[
 ("index.html","전국 꽃배달","근조화환부터 축하화환, 꽃바구니, 관엽식물까지 받는 분과 행사 목적에 맞춰 꽃배달 주문 전 확인할 사항을 안내합니다.","종합 꽃배달 안내",
  ["전국 꽃배달을 알아볼 때는 받는 분의 지역과 원하는 전달 날짜, 꽃 선물의 용도를 먼저 정리하는 편이 좋습니다. 지역 및 상품에 따라 주문 가능 여부와 실제 배송 일정은 달라질 수 있습니다.",
   "근조화환은 장례식장의 정확한 명칭과 빈소 정보를 확인하고, 축하화환은 행사장 반입 가능 시간과 리본 문구를 함께 준비하면 상담이 수월합니다.",
   "꽃바구니나 관엽식물은 받는 장소의 분위기와 공간을 고려해 선택하세요. 계절과 수급에 따라 실제 제작되는 꽃과 식물의 구성은 달라질 수 있습니다."]),
 ("funeral.html","전국 근조화환","장례식장으로 보내는 근조화환 주문 시 장례식장명·빈소·상주명과 전달 희망 시간을 확인하세요.","근조화환 주문 안내",
  ["장례식장으로 근조화환을 보내려면 같은 이름의 장례시설을 혼동하지 않도록 정확한 주소까지 확인하는 것이 중요합니다.",
   "고인과 유가족에게 전할 리본 문구는 지나치게 길지 않게 작성하고, 보내는 사람의 회사명이나 성함도 분명하게 전달하세요.",
   "장례 절차와 조문 일정은 현장 상황에 따라 달라집니다. 당일 배송 가능 여부와 도착 예정 시간은 주문 전에 개별 확인이 필요합니다."]),
 ("celebration.html","전국 축하화환","개업식·결혼식·공연·기념식 등 행사 목적별 축하화환과 리본 문구 준비 방법을 안내합니다.","축하화환 주문 안내",
  ["축하화환을 준비할 때는 행사가 열리는 정확한 장소, 날짜, 시작 시간과 행사 담당자를 확인하세요.",
   "개업과 결혼식, 공연은 행사별로 선호하는 크기와 화환 설치 위치가 다릅니다. 반입 제한이나 회수 기준이 있는 장소라면 사전에 문의하는 편이 안전합니다.",
   "축하 리본은 행사 성격에 맞는 짧은 문구와 보내는 분의 이름을 구분해 알려주세요. 실제 상품 구성과 최종 금액은 상담 시 확인할 수 있습니다."]),
 ("basket.html","전국 꽃바구니","생일·기념일·감사 인사를 위한 꽃바구니 선택과 전달 전 확인 사항을 소개합니다.","꽃바구니 주문 안내",
  ["꽃바구니는 색상과 꽃 종류에 따라 인상이 달라집니다. 선물받는 분이 선호하는 색상과 전달 목적을 알려주시면 상담에 도움이 됩니다.",
   "계절별 생화 공급 상황에 따라 사진과 동일한 꽃을 준비하기 어려운 경우가 있습니다. 필요한 색감과 예산 범위를 중심으로 최종 구성을 확인하세요.",
   "배송지의 상세 주소와 연락처, 부재 시 수령 가능한 방법을 미리 확인하고, 수령 희망일은 판매처와 협의해 주세요."]),
 ("plants.html","전국 관엽식물·화분","승진·이전·개업 선물에 적합한 관엽식물과 화분을 선택할 때 확인할 사항을 정리했습니다.","관엽식물·화분 안내",
  ["화분을 선물할 때는 놓을 장소의 빛과 공간, 받는 분이 관리할 수 있는 여건을 생각하세요.",
   "실내 식물은 용기와 식물 크기에 따라 배송과 배치 조건이 달라집니다. 상품 사진뿐 아니라 전체 높이와 화분 폭도 함께 확인하는 것이 좋습니다.",
   "개업과 승진 축하 문구를 적을 때는 성함과 소속을 정확하게 확인하세요. 특정 상품의 재고와 현재 가격은 주문 상담에서 확인해야 합니다."]),
 ("delivery.html","전국 꽃배달 주문·배송 안내","전국 꽃배달 주문에 필요한 배송지·희망일·리본 문구 및 상담 절차를 안내합니다.","배송·주문 안내",
  ["먼저 상품 종류와 받는 분의 정확한 주소, 연락처, 희망 전달 날짜를 준비해 주세요.",
   "장례식장이나 행사장에 보내는 경우 빈소·행사장 명칭과 현장 반입 규정이 중요합니다. 해당 시설의 안내를 먼저 확인하면 변경과 재배송 위험을 줄일 수 있습니다.",
   "전화 상담은 1844-0644로 가능합니다. 전국 모든 지역의 당일 배송이나 특정 시간 도착을 보장한다는 의미는 아니며, 주문 가능 지역·시간·가격은 상담 후 확정합니다."])
]
NAV=[("종합안내","/"),("근조화환","/funeral.html"),("축하화환","/celebration.html"),("꽃바구니","/basket.html"),("관엽식물","/plants.html"),("배송안내","/delivery.html")]
CSS="""*{box-sizing:border-box}body{margin:0;background:#faf9f6;color:#263b35;font-family:system-ui,-apple-system,'Malgun Gothic',sans-serif;line-height:1.75}a{color:inherit;text-decoration:none}.wrap{width:min(1100px,calc(100% - 40px));margin:auto}.top{background:#fff;border-bottom:1px solid #e6e9e1}.nav{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:16px 0;flex-wrap:wrap}.logo{font-size:24px;font-weight:800;color:#166453}.links{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}.tel{background:#146b5a;color:#fff;padding:9px 16px;border-radius:30px;font-weight:700}.hero{padding:80px 0 60px;background:linear-gradient(120deg,#edf5ee,#f8efe9)}.eyebrow{font-weight:700;letter-spacing:2px;color:#548577;font-size:12px}h1{font-size:clamp(31px,5vw,52px);line-height:1.3;margin:14px 0 20px;word-break:keep-all}.lead{max-width:760px;font-size:18px;color:#486159}.cta{display:inline-block;padding:13px 24px;background:#176856;border-radius:8px;color:white;font-weight:bold;margin-top:20px}.content{padding:52px 0 80px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}.card,.section{background:white;border:1px solid #e4eae4;border-radius:16px;padding:26px}.card h2{font-size:21px}.card p{color:#577168}.card span{color:#08725c;font-weight:700}.section{margin-bottom:18px}.section h2{font-size:21px}footer{background:#153a33;color:#e8f3ed;padding:30px 0}footer a{text-decoration:underline} @media(max-width:650px){.nav{align-items:flex-start}.links{gap:12px}.hero{padding:50px 0}.section{padding:20px}}"""
def render(item,indexable):
    filename,title,description,kicker,paragraphs=item
    path="/" if filename=="index.html" else "/"+filename
    nav="".join('<a href="'+escape(href,quote=True)+'">'+escape(name)+'</a>' for name,href in NAV)
    links=""
    if filename=="index.html":
        links='<div class="cards">'+''.join('<a class="card" href="/'+escape(row[0])+'"><h2>'+escape(row[1])+'</h2><p>'+escape(row[2])+'</p><span>자세히 보기 →</span></a>' for row in PAGES[1:])+'</div>'
    sections="".join('<section class="section"><h2>'+escape(head)+'</h2><p>'+escape(p)+'</p></section>' for head,p in zip(["주문 전 확인","현장·상품 선택","배송·상담 준비"],paragraphs))
    robots="index,follow" if indexable else "noindex,nofollow"
    canonical='<link rel="canonical" href="'+DOMAIN+path+'">' if indexable else ""
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+' | 꽃이랑</title><meta name="description" content="'+escape(description,quote=True)+'"><meta name="robots" content="'+robots+'">'+canonical+'<link rel="stylesheet" href="/assets/site.css"></head><body><header class="top"><div class="wrap nav"><a class="logo" href="/">✿ 꽃이랑</a><nav class="links" aria-label="주요 서비스">'+nav+'</nav><a class="tel" href="tel:18440644">☎ '+PHONE+'</a></div></header><main><div class="hero"><div class="wrap"><div class="eyebrow">NATIONWIDE FLOWER DELIVERY GUIDE</div><h1>'+escape(title)+'</h1><p class="lead">'+escape(description)+'</p><a class="cta" href="tel:18440644">전화로 꽃배달 상담하기</a></div></div><div class="wrap content"><h2>'+escape(kicker)+'</h2>'+links+sections+'</div></main><footer><div class="wrap"><strong>꽃이랑 · 전국 꽃배달 상담</strong><p>☎ <a href="tel:18440644">'+PHONE+'</a> · 상품·배송 가능 여부는 상담 후 확정됩니다.</p></div></footer></body></html>')
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--public",action="store_true")
    parser.add_argument("--output",default="dist/flower-national")
    a=parser.parse_args()
    out=Path(a.output);(out/"assets").mkdir(parents=True,exist_ok=True)
    for item in PAGES:(out/item[0]).write_text(render(item,a.public),encoding="utf-8")
    (out/"assets/site.css").write_text(CSS,encoding="utf-8")
    (out/"404.html").write_text(render(("404.html","페이지를 찾을 수 없습니다","홈페이지에서 꽃배달 상품 종류와 주문 안내를 확인해 주세요.","안내",["주소를 다시 확인해 주세요."]*3),False),encoding="utf-8")
    (out/"robots.txt").write_text("User-agent: *\n"+("Allow: /\nSitemap: "+DOMAIN+"/sitemap.xml\n" if a.public else "Disallow: /\n"),encoding="utf-8")
    if a.public:
        xml='<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+DOMAIN+("/" if x[0]=="index.html" else "/"+quote(x[0]))+'</loc></url>' for x in PAGES)+'</urlset>'
        (out/"sitemap.xml").write_text(xml,encoding="utf-8")
    assert len(PAGES)==6
    for row in PAGES:
        html=(out/row[0]).read_text()
        assert '<h1>'+escape(row[1])+'</h1>' in html and "1844-0644" in html
    print(json.dumps({"site":DOMAIN,"contentPages":len(PAGES),"public":a.public,"out":str(out)},ensure_ascii=False))
if __name__=="__main__":main()
