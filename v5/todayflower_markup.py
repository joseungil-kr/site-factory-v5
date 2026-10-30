"""Todayflower pilot-specific visual layer. All commerce records are seller-ledger input.

The V5 engine, config, output manifest, preview robots, hashing and audit stay shared.
Never claim the five editorial AI images are real SKU or delivered-order photographs.
"""
from __future__ import annotations

from . import markup as base

KINDS = (
    ("bouquet", "꽃다발", "생일·기념일·감사와 같은 직접적인 선물"),
    ("plant", "개업·축하화분", "매장·사무실에 놓아두는 식물 선물"),
    ("celebration", "축하화환", "개업식·기념행사 등 축하 자리"),
    ("condolence", "근조화환", "장례식장·빈소에 조의를 전하는 선물"),
)

# Only this site's rendered pages get these styles; no shared V5 theme mutation.
STYLE = r"""
.tf-layout{--pine:#174a3d;--mint:#f1f7ef;--pink:#f8eee9;--line:#e4e9e3;color:#213d33;font-family:system-ui,-apple-system,'Malgun Gothic',sans-serif}
.tf-shell{max-width:1160px;margin:auto;padding-inline:22px}.tf-layout a{text-underline-offset:3px}
.tf-hero{background:linear-gradient(108deg,#f9f7f1 12%,#e8f3e9 95%);padding:46px 0 38px}
.tf-hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:42px;align-items:center}
.tf-kicker{display:block;font-size:12px;color:#568575;font-weight:800;letter-spacing:.12em}
.tf-hero h1{font-size:clamp(33px,4.2vw,56px);line-height:1.25;letter-spacing:-.052em;margin:14px 0 18px;color:#174636}
.tf-lead{font-size:17px;line-height:1.9;color:#445f53;max-width:600px}
.tf-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:21px}
.tf-action{background:#206b54;color:#fff!important;font-weight:800;text-decoration:none;border-radius:11px;padding:12px 19px}
.tf-action.secondary{background:#fff;color:#1c654d!important;border:1px solid #a3c3b1}
.tf-figure{margin:0}.tf-figure img{display:block;width:100%;height:100%;object-fit:cover;border-radius:16px}
.tf-hero-photo{height:365px;overflow:hidden;border-radius:19px}.tf-img-caption{font-size:11px;color:#6c7a71;margin-top:8px}
.tf-section{padding-block:39px;border-bottom:1px solid #e7ece7}
.tf-section-head{margin:0 0 19px}.tf-section h2{font-size:clamp(24px,3vw,33px);color:#194e39;margin:0 0 9px}
.tf-section-desc{color:#687d6f;font-size:15px;margin:0}
.tf-choose{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.tf-choose-card{background:#fff;border:1px solid #e0e9df;border-radius:17px;overflow:hidden}
.tf-choose-card img{height:200px;border-radius:0}.tf-choose-card-body{padding:25px}
.tf-choose-card h3{font-size:20px;margin:0 0 8px}.tf-choose-card p{font-size:13px;color:#61776a;margin:0;line-height:1.75}
.tf-articles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}
.tf-articles .article-content{display:contents}.tf-articles .document-section{margin:0;border:1px solid #e2e9e2;background:#fff;border-radius:15px;padding:23px}
.tf-articles .document-section h2{font-size:21px;margin-bottom:10px}.tf-articles .document-section p{line-height:1.95;font-size:14px;color:#4b6556}
.tf-group{margin:25px 0 35px}.tf-group h3{font-size:22px;margin:0 0 12px;color:#174a3d}
.tf-product-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}
.tf-product{border:1px solid #e5ece3;border-radius:14px;background:white;overflow:hidden;display:flex;flex-direction:column}
.tf-product img{width:100%;aspect-ratio:1/1;object-fit:cover;background:#f1f4f0}
.tf-product-copy{padding:13px 14px 17px;display:flex;flex-direction:column;flex:1}
.tf-product small{font-size:11px;color:#789081}.tf-product h4{margin:7px 0 6px;font-size:16px;line-height:1.4}
.tf-product-price{font-size:20px;font-weight:850;color:#185540;margin:0 0 4px}
.tf-product-date{font-size:11px;color:#728579;margin:0 0 14px}
.tf-product a{background:#245f49;color:white!important;font-weight:800;text-decoration:none;border-radius:8px;padding:10px 6px;text-align:center;margin-top:auto;font-size:13px}
.tf-coverage{font-size:13px;color:#566d5c;background:#f2f7f0;border-radius:12px;padding:14px 18px}
.tf-check-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:25px;align-items:start}
.tf-pack-photo{height:360px}.tf-check{list-style:none;padding:0;margin:0;display:grid;gap:12px}
.tf-check li{border:1px solid #e0e8e0;background:#fff;border-radius:12px;padding:13px 17px;font-size:14px;line-height:1.75}
.tf-check strong{display:block;color:#1b5e45}.tf-faq details{margin-bottom:9px;background:#f8fbf7;border:1px solid #e2ebe1;border-radius:11px;padding:14px 18px}
.tf-faq summary{font-weight:800;cursor:pointer}.tf-faq details p{font-size:14px;line-height:1.85;color:#53695c;margin:10px 0 0}
.tf-related{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.tf-related a{border:1px solid #cfdfd3;background:#f4f8f3;border-radius:14px;padding:19px;color:#246149;text-decoration:none;font-weight:800}
.tf-order{margin:35px 0;padding:26px;background:linear-gradient(110deg,#e6f4e9,#fff0e9);border-radius:19px}
.tf-order h2{margin:0 0 9px;font-size:23px}.tf-order p{font-size:14px;color:#597466;margin:0 0 16px}

.tf-story-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:18px;align-items:start}
.tf-story-item{grid-column:span 2;min-width:0;margin:0;background:#f7f9f4;border:1px solid #e3eae0;border-radius:15px;padding:14px;display:flex;flex-direction:column;gap:11px}
.tf-story-item:nth-child(4){grid-column:2 / span 2}
.tf-story-item:nth-child(5){grid-column:4 / span 2}
.tf-story-item img{display:block;width:100%;height:auto;aspect-ratio:4 / 3;object-fit:cover;border-radius:10px}
.tf-story-item figcaption{font-size:15px;line-height:1.5;color:#486c57;font-weight:750;white-space:normal;overflow-wrap:anywhere}
@media(max-width:980px){.tf-story-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.tf-story-item,.tf-story-item:nth-child(4),.tf-story-item:nth-child(5){grid-column:auto}}
@media(max-width:740px){.tf-story-grid{grid-template-columns:minmax(0,1fr);gap:15px}.tf-story-item{padding:12px}.tf-story-item img{width:100%;height:auto}.tf-story-item figcaption{font-size:14px}}
@media(max-width:950px){.tf-product-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.tf-hero-grid{gap:21px}}
@media(max-width:740px){.tf-shell{padding-inline:16px}.tf-hero{padding:29px 0}.tf-hero-grid,.tf-check-grid{grid-template-columns:1fr}
.tf-hero h1{font-size:36px}.tf-lead{font-size:15px}.tf-hero-photo{height:270px}.tf-choose{grid-template-columns:1fr;gap:12px}
.tf-choose-card{display:block}.tf-choose-card img{display:none}
.tf-choose-card-body{padding:16px}.tf-articles{grid-template-columns:1fr}.tf-product-grid{gap:9px}
.tf-product-copy{padding:11px}.tf-product h4{font-size:14px}.tf-product-price{font-size:18px}
.tf-pack-photo{height:245px}.tf-related{grid-template-columns:1fr}.tf-section{padding-block:30px}}
@media(max-width:390px){.tf-hero h1{font-size:31px}.tf-choose-card h3{font-size:17px}.tf-product a{font-size:11px}}
"""

GENERATED_FILES = frozenset({
    "gift-bouquet.webp", "opening-plant.webp", "celebration-wreath.webp",
    "condolence-wreath.webp", "flower-wrapping.webp"
})

def _h(value):
    return base.h(value)

def _img(path, alt, css_class="", loading="lazy", priority=False):
    attrs = ' fetchpriority="high"' if priority else ""
    dimensions = 'width="1448" height="1086"' if path in GENERATED_FILES else 'width="600" height="860"'
    return (f'<img class="{_h(css_class)}" src="/assets/images/{_h(path)}"'
            f' alt="{_h(alt)}" {dimensions} loading="{loading}"'
            ' decoding="async"' + attrs + '>')

def _head(site,page):
    number=page["number"]
    path=base.url_path(number)
    original=base.head(site,page["title"],page["intro"],path,"/assets/images/"+site["imagePool"][0])
    return original.replace("</head>","<style>"+STYLE+"</style></head>")

def _hero(site,page):
    picture=_img(site["imagePool"][0],"꽃다발 선물을 주제로 한 AI 연출 이미지","tf-hero-visual","eager",True)
    return ('<section class="tf-hero"><div class="tf-shell tf-hero-grid"><div>'
            '<span class="tf-kicker">'+_h(page["heroTag"])+'</span>'
            '<h1>'+_h(page["title"])+'</h1>'
            '<p class="tf-lead">'+_h(page["intro"])+'</p>'
            '<div class="tf-actions"><a class="tf-action" href="tel:18440644">배송 가능 시간 상담</a>'
            '<a class="tf-action secondary" href="#products">실제 상품·가격 보기</a></div>'
            '</div><figure class="tf-figure"><div class="tf-hero-photo">'+picture+'</div>'
            '<figcaption class="tf-img-caption">AI 연출 이미지 · 실제 판매 상품의 사진과 구성은 아래 상품에서 확인하세요.</figcaption>'
            '</figure></div></section>')

def _choices(site):
    rows=(
        ("꽃다발","기념일·감사·응원의 선물. 받는 사람의 취향과 수령 가능한 시간을 확인하세요.",site["imagePool"][1]),
        ("개업화분","매장·사무실에 놓을 공간과 관리 조건, 실제 크기를 살펴보세요.",site["imagePool"][2]),
        ("축하·근조화환","행사장 반입·장례식장 빈소명과 리본 문구를 구분해 준비하세요.",site["imagePool"][3])
    )
    result=[]
    for title,desc,_pic in rows:
        result.append('<article class="tf-choose-card">'
                      '<div class="tf-choose-card-body"><h3>'+_h(title)+'</h3>'
                      '<p>'+_h(desc)+'</p></div></article>')
    return '<div class="tf-choose">'+"".join(result)+'</div>'

def _product_cards(products,selected):
    catalog={p["sku"]:p for p in products}
    sections=[]
    for kind,label,description in KINDS:
        entries=[catalog[sku] for sku in selected if catalog[sku].get("group")==kind]
        if not entries:continue
        cards=[]
        for p in entries:
            sku=_h(p["sku"]);order=_h(p["orderUrl"])
            # V4 seller-original image URL, not AI editorials or promised delivered-order photos.
            image=_h(p.get("imageUrl",""))
            pic=(f'<img src="{image}" alt="{_h(p["name"])} · 판매처 상품 이미지"'
                 ' width="500" height="500" loading="lazy" decoding="async">') if image else ""
            cards.append('<article class="tf-product">'+pic+'<div class="tf-product-copy">'
                         '<small>'+sku+'</small><h4>'+_h(p["name"])+'</h4>'
                         '<p class="tf-product-price">'+f'{p["referencePrice"]:,}'+'원</p>'
                         '<p class="tf-product-date">판매처 표시가 확인 '+_h(p["referenceDate"])+'</p>'
                         '<a target="_blank" rel="noopener noreferrer" href="'+order+'">상품 상세·주문 확인</a>'
                         '</div></article>')
        sections.append('<div class="tf-group"><h3>'+_h(label)+'</h3>'
                        '<p class="tf-section-desc">'+_h(description)+'</p>'
                        '<div class="tf-product-grid">'+"".join(cards)+'</div></div>')
    return "".join(sections)

def _story(site):
    """Five newly generated, locally bundled AI-topic images; not item photos."""
    captions=(
        ("gift-bouquet.webp", "꽃다발 선물", "분홍 꽃다발을 표현한 AI 연출 이미지"),
        ("opening-plant.webp", "개업화분", "실내 식물 화분을 표현한 AI 연출 이미지"),
        ("celebration-wreath.webp", "축하화환", "축하 꽃장식을 표현한 AI 연출 이미지"),
        ("condolence-wreath.webp", "근조화환", "흰 조의 꽃장식을 표현한 AI 연출 이미지"),
        ("flower-wrapping.webp", "꽃 포장", "꽃다발 포장 과정을 표현한 AI 연출 이미지"),
    )
    assert set(p for p,_,_ in captions) <= set(site["imagePool"])
    items=[]
    for photo,label,alt in captions:
        items.append('<figure class="tf-story-item">'
                     +_img(photo,alt,loading="lazy")
                     +'<figcaption>'+_h(label)+'</figcaption></figure>')
    return '<div class="tf-story-grid">'+"".join(items)+'</div>'

def _body(site,page,pages,products,links):
    snippet='<div class="tf-layout">'+_hero(site,page)+'<main id="main" class="tf-shell">'
    snippet+='<section class="tf-section" id="choices"><header class="tf-section-head"><h2>꽃다발·화분·화환, 용도에 맞게 선택</h2>'
    snippet+='<p class="tf-section-desc">'+_h(page["sectionLead"])+'</p></header>'+_choices(site)+'</section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>꽃 선물을 준비하는 다섯 장면</h2><p class="tf-section-desc">AI 생성 연출 이미지로 용도를 살펴보세요. 실제 판매 상품 사진이나 배송완료 사진은 아닙니다.</p></header>'+_story(site)+'</section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>지역과 상황에 맞는 주문 판단</h2></header>'
    snippet+='<div class="tf-articles">'+base.article_body(page)+'</div></section>'
    snippet+='<section class="tf-section" id="products"><header class="tf-section-head"><h2>확인된 실제 꽃 상품·가격</h2>'
    snippet+='<p class="tf-section-desc">상품별 표시 금액은 주문 전 다시 확인해 주세요. 지역·시간·옵션에 따라 최종 금액은 달라질 수 있습니다.</p></header>'
    snippet+=_product_cards(products,page["productSkus"])
    snippet+='<p class="tf-coverage">당일배송을 확정하는 화면이 아닙니다. 배송 가능한 날짜·마감시각·상품 준비·지역 추가요금은 선택한 상품의 판매처에서 확인해야 합니다.</p></section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>오늘 받을 꽃, 주문 전 체크리스트</h2></header>'
    snippet+='<div class="tf-check-grid"><figure class="tf-figure"><div class="tf-pack-photo">'
    snippet+=_img(site["imagePool"][4],"꽃 선물 포장 과정을 표현한 AI 연출 이미지")
    snippet+='</div><figcaption class="tf-img-caption">연출 이미지로 실제 상품 제작·배송 증빙이 아닙니다.</figcaption></figure>'
    snippet+='<ol class="tf-check">'
    for title,paragraph in (
        ("① 상품·SKU 선택","판매처 상품 화면에서 사진·규격·표시가와 포장·옵션을 확인합니다."),
        ("② 수령 주소·담당자 확인","도로명 주소와 건물·호실, 실제로 꽃을 받을 사람의 연락처를 준비합니다."),
        ("③ 배송 시각·마감 문의","오늘 수령 가능 여부와 주문 마감·수령 가능 시간대를 결제 전에 상담합니다."),
        ("④ 지역 배송비·최종 금액","추가배송비, 상품 구성과 최종 결제금액을 판매처에서 확인합니다."),
        ("⑤ 카드·리본 문구","기념일 카드 또는 축하·근조 리본의 받는 이름과 보내는 명의를 대조합니다."),
    ):
        snippet+='<li><strong>'+_h(title)+'</strong>'+_h(paragraph)+'</li>'
    snippet+='</ol></div></section>'
    snippet+='<section class="tf-section tf-faq"><header class="tf-section-head"><h2>지역 꽃배달 FAQ</h2></header>'
    snippet+=base.faq_markup(page)+'</section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>다른 지역 주문 안내</h2></header><nav class="tf-related" aria-label="지역별 관련 글">'
    snippet+=''.join('<a href="'+_h(base.url_path(p["number"]))+'">'+_h(p["region"])+' 꽃배달 확인</a>' for p in pages if p["number"]!=page["number"])
    snippet+='</nav></section>'
    snippet+='<section class="tf-order"><h2>상품번호·배송지를 준비해 상담하세요</h2><p>실제 주문과 결제는 꽃이랑 판매처에서 진행됩니다. 1844-0644로 당일 가능 여부를 확인하세요.</p>'
    snippet+='<div class="tf-actions"><a class="tf-action" href="tel:18440644">전화 상담</a>'
    snippet+='<a class="tf-action secondary" href="https://fwith.co.kr" target="_blank" rel="noopener noreferrer">꽃이랑 상품 전체 보기</a></div></section>'
    snippet+=base.render_pagination(pages,page["number"])+'</main></div>'
    return snippet

def home(site,page,pages,products,links):
    return _head(site,page)+base.header(site)+_body(site,page,pages,products,links)+base.footer(site,links,page)

def detail(site,page,pages,products,links):
    return home(site,page,pages,products,links)
