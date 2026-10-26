"""Shared Nalmada Flower layout primitives and owner-sourced product photo assets.

Data is a dated V4 catalogue snapshot. It does not certify current prices,
stock, nationwide delivery at any time, or final page publication approval.
"""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data/flower/nalmada_funeral_product_reference.json"
CSS=ROOT/"templates/flower-nalmada/site.css"
IMAGE_SOURCE=ROOT/"assets/library/flower-nalmada"
IMAGE_NAMES=("B201.jpg","B203.jpg","B205.jpg","A160.jpg","D143.jpg")

def products():
    record=json.loads(CATALOG.read_text(encoding="utf-8"))
    assert record["commercialPublicationApproved"] is False
    assert record["priceFreshness"] == "snapshot_only_revalidate_before_public_release"
    assert [x["id"] for x in record["products"]] == ["B201","B203","B205"]
    for p in record["products"]:
        assert p["localImage"]=="/assets/images/"+p["id"]+".jpg"
        assert p["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id="+p["id"]
    return record

def prepare_assets(output:Path):
    css_target=output/"assets"/"css"/"site.css"
    css_target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(CSS,css_target)
    target=output/"assets"/"images"
    target.mkdir(parents=True,exist_ok=True)
    for name in IMAGE_NAMES:
        source=IMAGE_SOURCE/name
        if not source.is_file() or source.stat().st_size<8000:raise ValueError("Missing verified photo asset "+name)
        shutil.copyfile(source,target/name)

def head(title,description):
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow">'
            '<title>'+escape(title)+'</title>'
            '<meta name="description" content="'+escape(description[:155],quote=True)+'">'
            '<link rel="stylesheet" href="/assets/css/site.css"></head><body>'
            '<a class="skip" href="#main">본문 바로가기</a>')

def header():
    nav=[("근조화환","/#products"),("장례식장 찾기","/#directory"),("꽃바구니","/#categories"),("관엽화분","/#categories"),("주문안내","/#ordering")]
    links="".join('<a href="'+url+'">'+escape(text)+'</a>' for text,url in nav)
    return ('<header class="top"><div class="wrap topin">'
            '<a class="brand" href="/" aria-label="날마다꽃 홈"><span class="mark">✿</span> 날마다<em>꽃</em>'
            '<small>전국 꽃배달 상담</small></a><nav class="nav" aria-label="주요 메뉴">'+links+'</nav>'
            '<a class="btn top-tel" href="tel:18440644">☎ 1844-0644</a></div></header>')

def photo(asset,alt,loading="lazy"):
    return '<img src="/assets/images/'+escape(asset)+'" alt="'+escape(alt,quote=True)+'" loading="'+loading+'">'

def price_cards(class_name="products"):
    source=products()
    cards=[]
    for p in source["products"]:
        cards.append('<div class="product-card"><div class="product-photo">'+photo(p["id"]+".jpg",p["name"]+" 공통 상품 사진")+'</div>'
                     '<div class="info"><h3>'+escape(p["name"])+'</h3>'
                     '<span class="product-price-label reference">2026-10-22 판매처 확인 참고가</span>'
                     '<div class="product-price">'+format(p["referencePrice"],",")+'원</div>'
                     '<a class="more" href="'+escape(p["orderUrl"],quote=True)+'" target="_blank" rel="noopener noreferrer">'
                     '판매처 상품정보 보기 ↗</a></div></div>')
    return '<div class="'+escape(class_name,quote=True)+'">'+"".join(cards)+'</div>'

def reference_note():
    return ('<div class="notice">가격은 2026-10-22 기존 꽃이랑 판매처 확인 자료의 <b>참고 금액</b>으로, '
            '날마다꽃의 현재 최종 판매가·재고·해당 장례식장 배송비를 보장하지 않습니다. '
            '주문 전에 <a href="tel:18440644">1844-0644</a>로 확인해 주세요.</div>')

def footer():
    return ('<footer class="footer"><div class="wrap inner">'
            '<div><b>✿ 날마다꽃</b><p>전국 꽃배달 상담 · 1844-0644</p></div>'
            '<p>디자인 검수용 페이지 · 시설 및 상품 정보 확인 중 · 검색 제외(noindex)</p>'
            '</div></footer><div class="mobile-call"><a class="btn" href="tel:18440644">'
            '☎ 날마다꽃 전화 상담 1844-0644</a></div></body></html>')

def contact_band():
    return ('<section class="wrap contact-band"><div><h2>근조화환 주문, 필요한 정보부터 확인하세요</h2>'
            '<p>장례식장명·빈소·상주명·희망일·리본 문구를 알려주시면 상담에 도움이 됩니다.</p>'
            '</div><a class="btn" href="tel:18440644">☎ 1844-0644 전화 상담</a></section>')
