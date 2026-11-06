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
.tf-hero{background:linear-gradient(108deg,#f9f7f1 12%,#e8f3e9 95%);padding:54px 0 48px}.tf-hero-inner{max-width:920px}
.tf-hero-grid{display:block}
.tf-kicker{display:block;font-size:12px;color:#568575;font-weight:800;letter-spacing:.12em}
.tf-hero h1{font-size:clamp(32px,3.35vw,46px);line-height:1.27;letter-spacing:-.046em;word-break:keep-all;overflow-wrap:break-word;margin:14px 0 18px;color:#174636}
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
@media(max-width:740px){.tf-shell{padding-inline:16px}.tf-hero{padding:29px 0}.tf-hero-grid,.tf-check-grid{display:block}
.tf-hero h1{font-size:36px}.tf-lead{font-size:15px}.tf-choose{grid-template-columns:1fr;gap:12px}
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
    path=base.url_path(page["number"])
    original=base.head(site,page["title"],page["intro"],path,"")
    # No approved representative image is currently available for social metadata.
    return original.replace('<meta property="og:image" content="">','').replace(
        "</head>","<meta property=\"og:type\" content=\"website\"></head>"
    )

def _hero(site,page):
    return ('<section class="tf-hero"><div class="tf-shell tf-hero-inner">'
            '<span class="tf-kicker">'+_h(page["heroTag"])+'</span>'
            '<h1>'+_h(page["title"])+'</h1>'
            '<p class="tf-lead">'+_h(page["intro"])+'</p>'
            '<div class="tf-actions"><a class="tf-action" href="tel:18440644">배송 일정 상담</a>'
            '<a class="tf-action secondary" href="#products">상품 비교하기</a></div>'
            '</div></section>')

def _choices(site):
    rows=(
        ("꽃다발","기념일·감사·응원의 선물. 받는 분의 취향과 원하는 색감, 포장 분위기를 골라보세요."),
        ("개업화분","매장·사무실에 놓을 공간과 채광, 관리할 사람에 맞춰 크기를 선택하세요."),
        ("축하·근조화환","행사와 조문 목적에 맞는 종류를 고르고, 리본 문구와 수령 위치를 정리해 주세요.")
    )
    result=[]
    for title,desc in rows:
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
            image=_h(p.get("imageUrl",""))
            pic=(f'<img src="{image}" alt="{_h(p["name"])} 상품 사진"'
                 ' width="500" height="500" loading="lazy" decoding="async">') if image else ""
            price=(f'{p["referencePrice"]:,}원' if isinstance(p.get("referencePrice"),int)
                   else "상품 상세에서 가격 확인")
            cards.append('<article class="tf-product">'+pic+'<div class="tf-product-copy">'
                         '<small>'+sku+'</small><h4>'+_h(p["name"])+'</h4>'
                         '<p class="tf-product-price">'+_h(price)+'</p>'
                         '<a target="_blank" rel="noopener noreferrer" href="'+order+'">상품 상세·주문 확인</a>'
                         '</div></article>')
        sections.append('<div class="tf-group"><h3>'+_h(label)+'</h3>'
                        '<p class="tf-section-desc">'+_h(description)+'</p>'
                        '<div class="tf-product-grid">'+"".join(cards)+'</div></div>')
    return "".join(sections)

def _body(site,page,pages,products,links):
    snippet='<div class="tf-layout">'+_hero(site,page)+'<main id="main" class="tf-shell">'
    snippet+='<section class="tf-section" id="choices"><header class="tf-section-head"><h2>꽃다발·화분·화환, 목적에 맞게 선택</h2>'
    snippet+='<p class="tf-section-desc">'+_h(page["sectionLead"])+'</p></header>'+_choices(site)+'</section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>지역과 상황에 맞는 주문 정보</h2></header>'
    snippet+='<div class="tf-articles">'+base.article_body(page)+'</div></section>'
    snippet+='<section class="tf-section" id="products"><header class="tf-section-head"><h2>상품별 사진·가격·주문 링크</h2>'
    snippet+='<p class="tf-section-desc">상품 사진과 표시가격을 비교하고, 상세 페이지에서 현재 판매가·옵션·배송비를 확인한 뒤 주문할 수 있습니다.</p></header>'
    snippet+=_product_cards(products,page["productSkus"])
    snippet+='<p class="tf-coverage">원하는 날짜와 수령 주소를 알려주시면 상품별 배송 가능 일정과 추가 배송비를 안내해 드립니다.</p></section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>주문에 필요한 정보</h2></header>'
    snippet+='<ol class="tf-check">'
    for title,paragraph in (
        ("① 상품 선택","꽃다발·화분·화환 중 선물 목적에 맞는 상품을 고르고 SKU를 정리해 주세요."),
        ("② 수령 정보","받는 분의 이름과 연락처, 도로명 주소·건물명·층·호실을 준비해 주세요."),
        ("③ 희망 일정","원하는 날짜와 시간대를 알려주시면 상품 준비 일정과 전달 가능 시간을 안내해 드립니다."),
        ("④ 최종 금액","상품 상세에서 현재 판매가와 옵션, 배송 주소에 적용되는 배송비를 확인해 주세요."),
        ("⑤ 카드·리본","받는 분과 보내는 분의 이름, 카드·리본 문구를 구분해 적어 주세요."),
    ):
        snippet+='<li><strong>'+_h(title)+'</strong>'+_h(paragraph)+'</li>'
    snippet+='</ol></section>'
    snippet+='<section class="tf-section tf-faq"><header class="tf-section-head"><h2>지역 꽃배달 FAQ</h2></header>'
    snippet+=base.faq_markup(page)+'</section>'
    snippet+='<section class="tf-section"><header class="tf-section-head"><h2>다른 지역 주문 안내</h2></header><nav class="tf-related" aria-label="지역별 관련 글">'
    if len(pages)<=50:
        suggested=[p for p in pages if p["number"]!=page["number"]]
    else:
        index=page["number"]-1 if page["number"]<404 else page["number"]-2
        positions={0,1,2,3}
        positions.update(range(max(0,index-2),min(len(pages),index+3)))
        suggested=[pages[i] for i in sorted(positions) if i!=index][:8]
    snippet+=''.join('<a href="'+_h(base.url_path(p["number"]))+'">'+_h(p["region"])+' 꽃배달 안내</a>' for p in suggested)
    snippet+='</nav></section>'
    snippet+='<section class="tf-order" id="order"><h2>상품번호와 배송지를 준비해 상담하세요</h2><p>상품번호, 받으실 주소, 희망 날짜를 알려주시면 주문 상담을 도와드립니다.</p>'
    snippet+='<div class="tf-actions"><a class="tf-action" href="tel:18440644">전화 상담 1844-0644</a></div></section>'
    snippet+='</main></div>'
    return snippet

def home(site,page,pages,products,links):
    if site.get("todayflowerNational",{}).get("enabled",False):
        # Nationwide pages need useful in-page navigation, never a fixed
        # Ansan / Danwon / Gojan menu shown as if it were the country menu.
        presentation_site={
            **site,
            "navigation":[
                {"label":"꽃 종류","href":"#choices"},
                {"label":"실상품·가격","href":"#products"},
                {"label":"주문 상담","href":"#order"},
            ],
        }
    else:
        presentation_site=site
    return (_head(site,page)+base.header(presentation_site)
            +_body(site,page,pages,products,links)
            +base.footer(presentation_site,links,page))

def detail(site,page,pages,products,links):
    return home(site,page,pages,products,links)
