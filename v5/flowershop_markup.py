"""Flowershop-only image/price/direct-order product layout.

All product data comes from the seller ledgers. It is not a real-time inventory API.
Other Site Factory themes and renderers must remain unchanged.
"""
from __future__ import annotations

from . import markup as base

GROUPS = (
    ("plant", "개업·관엽화분", "새로운 매장과 사무실에 오래 두는 식물 선물"),
    ("celebration", "개업·축하화환", "개업식과 행사장에 전달하는 축하 선물"),
    ("condolence", "근조화환", "장례식장·빈소에 조의를 전하는 화환"),
)

# Product photos are seller-sourced; CSS fills the frame without side padding.
CSS = """
.fs-wrap{width:min(1160px,calc(100% - 36px));margin:0 auto}
.fs-hero{background:linear-gradient(120deg,#f4faf2,#fff6f0);padding:42px 0}
.fs-hero-grid{display:grid;grid-template-columns:1.15fr 1fr;align-items:center;gap:32px}
.fs-kicker{display:block;font-size:12px;font-weight:800;color:#39745d;letter-spacing:.12em;margin-bottom:9px}
.fs-hero h1{margin:0 0 18px;color:#154332;font-size:clamp(30px,4vw,48px);letter-spacing:-.055em;line-height:1.35}
.fs-lead{font-size:17px;color:#425d50;line-height:1.85;margin:0 0 24px}
.fs-hero-image{width:100%;height:340px;object-fit:cover;border-radius:22px;display:block}
.fs-content{padding:40px 0 64px}
.fs-section{margin:0 0 47px}
.fs-section h2{margin:0 0 8px;font-size:clamp(23px,3vw,31px)}
.fs-section-desc{color:#63766b;margin-bottom:22px}
.fs-products-group{margin:0 0 32px}
.fs-products-group>h3{font-size:21px;margin:0 0 3px;color:#184b39}
.fs-products-group>p{margin:0 0 14px;color:#687c70;font-size:14px}
.fs-product-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px}
.fs-product{border:1px solid #e3eae4;border-radius:17px;overflow:hidden;background:#fff;box-shadow:0 6px 24px rgba(23,65,42,.045)}
.fs-product-image{display:block;aspect-ratio:1/1;overflow:hidden;background:#edf1eb}
.fs-product-image img{display:block;width:100%;height:100%;object-fit:cover}
.fs-product-body{padding:19px 19px 21px}
.fs-kind{display:block;color:#438568;font-size:12px;font-weight:800;margin-bottom:5px}
.fs-product h4{font-size:19px;line-height:1.35;margin:0 0 13px;color:#233c2f}
.fs-price{font-size:25px;font-weight:850;color:#164c34;line-height:1.25;margin:0}
.fs-date{font-size:12px;color:#657c71;margin:5px 0 15px}
.fs-order{display:inline-flex;align-items:center;justify-content:center;background:#216c50;color:#fff!important;text-decoration:none;border-radius:10px;padding:11px 16px;font-weight:800;font-size:14px;min-height:43px}
.fs-order:hover{background:#12563a}
.fs-notice{margin-top:15px;font-size:13px;color:#596c61;background:#f4f8f3;padding:13px 16px;border-radius:10px}
.fs-article{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.fs-article .article-content{display:contents}
.fs-article .document-section{margin:0;border:1px solid #e4eae4;border-radius:14px;padding:23px}
.fs-article .document-section h2{font-size:20px}
.fs-article .document-section p{color:#486354;line-height:1.9}
.fs-related-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}
.fs-related-grid a{padding:23px;border:1px solid #d9e7dc;border-radius:14px;text-decoration:none;background:#f8fbf7;display:block}
.fs-related-grid strong{display:block;font-size:17px;color:#14593e}
.fs-related-grid small{display:block;color:#73867a;margin-top:6px}
.fs-faq details{border:1px solid #e2eae2;border-radius:10px;padding:13px 19px;margin:0 0 9px}
.fs-faq summary{font-weight:750;cursor:pointer}
.fs-faq details p{margin:10px 0 0;color:#536b5a}
.fs-cta{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;padding:24px;border-radius:18px;background:#edf7ee}
.fs-cta h2{font-size:23px;margin:0 0 6px}
.fs-cta p{font-size:13px;margin:0;color:#607269}
.fs-hero-mini{padding:32px 0}
.fs-hero-mini .fs-hero-image{height:260px}
@media(max-width:830px){.fs-product-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.fs-hero-grid{grid-template-columns:1fr}.fs-hero-image{height:280px}.fs-article{grid-template-columns:1fr}}
@media(max-width:520px){.fs-wrap{width:calc(100% - 28px)}.fs-product-grid{grid-template-columns:1fr 1fr;gap:9px}.fs-product-body{padding:13px}.fs-product h4{font-size:15px}.fs-price{font-size:20px}.fs-order{font-size:12px;padding:9px 6px;width:100%}.fs-date{font-size:11px}.fs-hero{padding:24px 0}.fs-hero-image{height:220px}.fs-related-grid{grid-template-columns:1fr}.fs-cta{padding:18px}}
"""


def head(site, page, url):
    css = "<style>" + CSS + "</style>"
    return base.head(
        site, page["title"], page["intro"], url,
        "/assets/images/" + site["imagePool"][0]
    ).replace("</head>", css + "</head>")


def product_gallery(products, selected_skus):
    catalog = {item["sku"]: item for item in products}
    selected = [catalog[sku] for sku in selected_skus]
    sections = []
    for group, title, caption in GROUPS:
        subset = [p for p in selected if p["group"] == group]
        if not subset:
            continue
        cards = []
        for item in subset:
            name = base.h(item["name"])
            href = base.h(item["orderUrl"])
            image = base.h(item.get("localImagePath") or item["imageUrl"])
            amount = f'{item["referencePrice"]:,}원'
            checked = base.h(item["referenceDate"])
            cards.append(
                '<article class="fs-product">'
                f'<a class="fs-product-image" href="{href}" target="_blank" rel="noopener noreferrer"'
                f' aria-label="{name} 상품 상세 보기">'
                f'<img src="{image}" alt="{name} 상품 사진" width="500" height="500"'
                ' loading="lazy" decoding="async"></a>'
                '<div class="fs-product-body">'
                f'<span class="fs-kind">{base.h(title)}</span>'
                f'<h4>{name}</h4>'
                f'<p class="fs-price">{amount}</p>'
                f'<p class="fs-date">판매처 가격 확인일 {checked}</p>'
                f'<a class="fs-order" data-track-event="shop" href="{href}"'
                ' rel="noopener noreferrer" target="_blank">상품 상세·주문 ↗</a>'
                '</div></article>'
            )
        sections.append(
            '<div class="fs-products-group">'
            f'<h3>{base.h(title)}</h3><p>{base.h(caption)}</p>'
            '<div class="fs-product-grid">' + "".join(cards) + '</div></div>'
        )
    return (
        "".join(sections)
        + '<p class="fs-notice">표시 가격은 각 확인일의 판매처 상품 페이지 기준입니다.'
        ' 실제 상품 구성·배송 가능 여부·지역별 추가배송비와 최종 결제금액은 상품 상세 화면에서 확인해 주세요.</p>'
    )


def pagination(pages, number):
    """O(1) pagination for immutable consecutive flower URL identities."""
    count = len(pages)
    if (count == 0 or pages[0]["number"] != 1
            or pages[-1]["number"] != count):
        return base.render_pagination(pages, number)
    start = max(1, min(number - 3, max(1, count - 6)))
    items = []
    for index in range(start, min(count, start + 6) + 1):
        if index == number:
            items.append(f'<span aria-current="page" class="active">{index}</span>')
        else:
            items.append(
                f'<a href="{base.h(base.url_path(index))}"'
                f' aria-label="{index}번 페이지">{index}</a>'
            )
    return '<nav class="pagination" aria-label="다른 글 페이지">' + "".join(items) + "</nav>"


def related(pages, current):
    """Use nearby region/topic records rather than repeating six national links."""
    if pages and pages[0]["number"] == 1 and pages[-1]["number"] == len(pages):
        if current == 1:
            chosen = pages[1:7]
        else:
            index = current - 1
            chosen = pages[max(1, index - 3):index] + pages[index + 1:index + 4]
    else:
        chosen = [p for p in pages if p["number"] != current][:6]
    links = []
    for p in chosen[:6]:
        links.append(
            '<a href="' + base.h(base.url_path(p["number"])) + '">'
            '<strong>' + base.h(p["title"]) + '</strong>'
            '<small>' + base.h(p["region"]) + '</small></a>'
        )
    return '<div class="fs-related-grid">' + "".join(links) + '</div>'


def article(page):
    return '<div class="fs-article">' + base.article_body(page) + '</div>'


def faq(page):
    return '<div class="fs-faq">' + base.faq_markup(page) + '</div>'


def contact(site):
    return (
        '<section class="fs-section fs-cta">'
        '<div><h2>꽃 선물 주문 상담</h2><p>상품·배송지·희망 날짜를 정리해 문의해 주세요.</p></div>'
        + base.phone_buttons(site) + '</section>'
    )


def hero(site, page, small=False):
    img = base.h("/assets/images/" + site["imagePool"][0])
    return (
        '<section class="fs-hero' + (' fs-hero-mini' if small else '') + '">'
        '<div class="fs-wrap fs-hero-grid"><div>'
        '<span class="fs-kicker">꽃이랑 · 꽃 선물 주문 안내</span>'
        '<h1>' + base.h(page["title"]) + '</h1>'
        '<p class="fs-lead">' + base.h(page["intro"]) + '</p>'
        + base.phone_buttons(site)
        + '</div><img class="fs-hero-image" src="' + img + '"'
        ' alt="꽃과 식물이 있는 꽃집" width="800" height="520"'
        ' loading="eager" fetchpriority="high"></div></section>'
    )


def home(site, page, pages, products, links):
    return (
        head(site, page, "/") + base.header(site)
        + '<main id="main" class="fs-site">'
        + hero(site, page)
        + '<div class="fs-wrap fs-content">'
        '<section class="fs-section" id="products">'
        '<h2>개업화분·축하화환·근조화환 상품 살펴보기</h2>'
        '<p class="fs-section-desc">상품 사진, 가격과 판매처 주문 화면을 한곳에서 비교할 수 있습니다.</p>'
        + product_gallery(products, page["productSkus"]) + '</section>'
        '<section class="fs-section"><h2>선물을 고르기 전에</h2>'
        + article(page) + '</section>'
        '<section class="fs-section"><h2>지역별 안내</h2>'
        + related(pages, page["number"]) + '</section>'
        '<section class="fs-section"><h2>자주 묻는 질문</h2>'
        + faq(page) + '</section>'
        + base.link_block(base.relevant_links(links, page, "body"), "body-links")
        + contact(site) + pagination(pages, page["number"])
        + '</div></main>' + base.footer(site, links, page)
    )


def detail(site, page, pages, products, links):
    return (
        head(site, page, base.url_path(page["number"])) + base.header(site)
        + '<main id="main" class="fs-site">'
        + hero(site, page, small=True)
        + '<div class="fs-wrap fs-content">'
        '<section class="fs-section"><h2>주문 전 알아둘 점</h2>'
        + article(page) + '</section>'
        '<section class="fs-section" id="products"><h2>관련 꽃 선물 상품</h2>'
        '<p class="fs-section-desc">아래 제품별 사진과 가격을 비교한 다음 판매처 상세 화면에서 주문할 수 있습니다.</p>'
        + product_gallery(products, page["productSkus"]) + '</section>'
        '<section class="fs-section"><h2>자주 묻는 질문</h2>'
        + faq(page) + '</section>'
        '<section class="fs-section"><h2>다른 지역·상품 안내</h2>'
        + related(pages, page["number"]) + '</section>'
        + base.link_block(base.relevant_links(links, page, "body"), "body-links")
        + contact(site) + pagination(pages, page["number"])
        + '</div></main>' + base.footer(site, links, page)
    )
