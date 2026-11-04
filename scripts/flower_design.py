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
RELEASE=ROOT/"data/flower/nalmada_release_authorization_20261027.json"
CSS=ROOT/"templates/flower-nalmada/site.css"
IMAGE_SOURCE=ROOT/"assets/library/flower-nalmada"
IMAGE_NAMES=("B201.jpg","B203.jpg","B205.jpg","A160.jpg","D143.jpg")

def products():
    original=json.loads(CATALOG.read_text(encoding="utf-8"))
    evidence=json.loads(RELEASE.read_text(encoding="utf-8"))
    assert original["commercialPublicationApproved"] is False
    assert original["priceFreshness"] == "snapshot_only_revalidate_before_public_release"
    assert evidence["authorizationDate"] == "2026-10-27"
    assert evidence["images"]["originalSHA256MustMatch"] is True
    assert evidence["products"]["verifiedAtUTC"].startswith("2026-10-27T11:20")
    approved={p["id"]:p for p in evidence["products"]["records"]}
    assert set(approved)=={"B201","B203","B205"}
    record=dict(original)
    record["products"]=[]
    for p in original["products"]:
        assert p["id"] in approved
        assert p["localImage"]=="/assets/images/"+p["id"]+".jpg"
        assert p["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id="+p["id"]
        item=approved[p["id"]]
        assert p["orderUrl"]==item["uri"] and p["referencePrice"]==item["priceKRW"]
        row=dict(p)
        row["referencePrice"]=item["priceKRW"]
        row["priceVerifiedOn"]="2026-10-27"
        record["products"].append(row)
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

def head(title,description,*,public=False,path="/"):
    if public:
        if not path.startswith("/") or "?" in path or "#" in path or "//" in path:
            raise ValueError("Invalid production canonical path")
        robots='index,follow'
        canonical='<link rel="canonical" href="https://flower.nalmada.net'+escape(path,quote=True)+'">'
    else:
        robots='noindex,nofollow'
        canonical=''
    naver = ('<meta name="naver-site-verification" content="4294f019f90dbaab16b91e588be60fca64a40ca8">'
             if public and path == '/' else '')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="'+robots+'">'+canonical+naver
            +'<title>'+escape(title)+'</title>'
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
        cards.append('<div class="product-card"><div class="product-photo">'+photo(p["id"]+".jpg",p["name"]+" 상품 이미지")+'</div>'
                     '<div class="info"><h3>'+escape(p["name"])+'</h3>'
                     '<span class="product-price-label reference">2026.10.27 판매처 확인 가격</span>'
                     '<div class="product-price">'+format(p["referencePrice"],",")+'원</div>'
                     '<a class="more" href="'+escape(p["orderUrl"],quote=True)+'" target="_blank" rel="noopener noreferrer">'
                     '판매처 상품정보 보기 ↗</a></div></div>')
    return '<div class="'+escape(class_name,quote=True)+'">'+"".join(cards)+'</div>'

def reference_note():
    """Internal price provenance belongs in the private catalogue/QA, not customer UI."""
    return ""

def footer():
    return ('<footer class="footer"><div class="wrap inner">'
            '<div><b>✿ 날마다꽃</b><p>전국 꽃배달 상담 · 1844-0644</p></div>'
            '<p>근조화환 · 축하화환 · 꽃바구니 · 관엽식물</p>'
            '</div></footer><div class="mobile-call"><a class="btn" href="tel:18440644">'
            '☎ 날마다꽃 전화 상담 1844-0644</a></div></body></html>')

def contact_band():
    return ('<section class="wrap contact-band"><div><h2>근조화환 주문, 필요한 정보부터 확인하세요</h2>'
            '<p>장례식장명·빈소·상주명·희망일·리본 문구를 알려주시면 상담에 도움이 됩니다.</p>'
            '</div><a class="btn" href="tel:18440644">☎ 1844-0644 전화 상담</a></section>')
