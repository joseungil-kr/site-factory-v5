"""Portable, semantic V5 templates. Marketing index and long-form numbered documents.

Only labels and HTML contain a region, product, shop URL or phone number;
illustrative image assets are intentionally language-neutral and reusable.
"""
from __future__ import annotations
import html
import json
from urllib.parse import quote


# Portable icon outlines; no customer names, prices, or region names in any imagery.
_ICONS = {
    'leaf': '<path d="M20 4C11 5 5 11 5 18c8 0 15-6 15-14Z"/><path d="M5 21c2-6 6-10 12-14"/>',
    'truck': '<path d="M3 6h12v11H3zM15 10h4l3 4v3h-7z"/><circle cx="7" cy="19" r="2"/><circle cx="18" cy="19" r="2"/>',
    'heart': '<path d="M20.5 8.5c0 5-8.5 11-8.5 11s-8.5-6-8.5-11a4.5 4.5 0 0 1 8.5-2 4.5 4.5 0 0 1 8.5 2Z"/>',
    'shield': '<path d="M12 2 4.5 5v6c0 5 3 8 7.5 11 4.5-3 7.5-6 7.5-11V5Z"/><path d="m9 12 2 2 4-5"/>',
    'chat': '<path d="M21 11a8 8 0 0 1-8 8c-2.2 0-4.2-.7-5.7-1.9L3 19l1.3-4.2A8 8 0 1 1 21 11Z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/>',
    'clipboard': '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2M9 11h6M9 15h6"/>',
    'card': '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
    'gift': '<rect x="3" y="9" width="18" height="12" rx="1"/><path d="M12 9v12M3 13h18M12 9c-5-1-7-7-3-7 2 0 3 3 3 7Zm0 0c5-1 7-7 3-7-2 0-3 3-3 7Z"/>',
    'sparkles':'<path d="m12 2 2 7 7 3-7 2-2 8-2-8-7-2 7-3Z"/><path d="m19 2 1 2 2 1-2 1-1 2-1-2-2-1 2-1Z"/>',
    'map':'<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
}
def icon(name):
    return '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+_ICONS[name]+'</svg>'


def h(value):
    return html.escape(str(value), quote=True)


def filename(number):
    return 'index.html' if number==1 else ('page-404.html' if number==404 else f'{number}.html')


def url_path(number):
    return '/' if number == 1 else '/'+filename(number)


def pagination(pages, current_number, width=7):
    ordered=sorted(pages,key=lambda p:p['number'])
    positions=[i for i,p in enumerate(ordered) if p['number']==current_number]
    if len(positions)!=1:
        raise ValueError('Current page number not found')
    index=positions[0]
    start=max(0,min(index-width//2,len(ordered)-width))
    return [p['number'] for p in ordered[start:start+width]]


def render_pagination(pages, number):
    items=[]
    for n in pagination(pages,number):
        if n==number:
            items.append(f'<span aria-current="page" class="active">{n}</span>')
        else:
            items.append(f'<a href="{h(url_path(n))}" aria-label="{n}번 페이지">{n}</a>')
    return '<nav class="pagination" aria-label="다른 글 페이지">'+''.join(items)+'</nav>'


def relevant_links(links, page, placement, self_path=None):
    selected=[]
    for link in links:
        if not link.get('enabled',True) or link['placement'] not in (placement,'both'):
            continue
        if self_path and link['target']==self_path:
            continue
        scope=link['scope']
        if scope=='region' and (page is None or page.get('region') not in link.get('regions',[])):
            continue
        if scope=='selected' and (page is None or page.get('id') not in link.get('pageIds',[])):
            continue
        selected.append(link)
    return selected


def link_block(links, css_class):
    if not links:
        return ''
    return f'<nav class="{h(css_class)}" aria-label="추가 안내 링크">'+''.join(
        f'<a href="/{quote(l["target"])}">{h(l["label"])}</a>' for l in links)+'</nav>'


def head(site,title,description,path,share_image):
    canonical=''
    robots='<meta name="robots" content="noindex,nofollow">'
    if site['domain'] and (site['publishEnabled'] or site.get('publicIndexingApproved',False)):
        domain=site['domain'].rstrip('/')
        robots='<meta name="robots" content="index,follow">'
        canonical=f'<link rel="canonical" href="{h(domain+path)}">'
    verification=(f'<meta name="naver-site-verification" content="{h(site["naverSiteVerification"])}">' if path=='/' and site.get('naverSiteVerification') else '')
    return ('<!doctype html>\n<html lang="ko"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{h(title)} | {h(site["brand"])}</title>'
        f'<meta name="description" content="{h(description[:155])}">{robots}{canonical}'
        f'{verification}'
        '<link rel="stylesheet" href="/assets/site.css">'
        f'<link rel="stylesheet" href="/assets/theme-{h(site["theme"])}.css">'
        f'<meta property="og:title" content="{h(title)}">'
        f'<meta property="og:description" content="{h(description[:155])}">'
        f'<meta property="og:image" content="{h(share_image)}">'
        '</head>')


def main_navigation(site):
    rows=site.get('navigation', [{'label':'홈','href':'/'}])
    return ''.join(f'<a href="{h(item["href"])}">{h(item["label"])}</a>' for item in rows)


def header(site):
    tel=h(site['phone'].replace('-',''))
    return ('<body><a class="skip-link" href="#main">본문 바로가기</a>'
        '<header class="site-header"><div class="header-inner">'
        f'<a class="brand" href="/" aria-label="{h(site["brand"])} 홈">'
        '<span class="brand-mark" aria-hidden="true">'+icon('leaf')+'</span>'
        f'<span class="brand-text">{h(site["brand"])}<small>소중한 마음을 전하는 특별한 선택</small></span></a>'
        '<nav class="primary-nav" aria-label="주요 메뉴">'+main_navigation(site)+'</nav>'
        f'<a data-track-event="phone" class="phone" href="tel:{tel}"><span aria-hidden="true">☎</span> {h(site["phone"])}</a>'
        '</div></header>')


def footer(site,links,page=None,self_path=None):
    tel=h(site['phone'].replace('-',''))
    return ('<footer class="site-footer"><div class="footer-inner">'
        '<div class="footer-brand"><span aria-hidden="true" class="footer-leaf">'+icon('leaf')+'</span>'
        f'<strong>{h(site["brand"])}</strong><p>축하와 응원의 마음을 전하는 안내 서비스</p></div>'
        '<nav class="footer-main-nav" aria-label="사이트 안내">'+main_navigation(site)+'</nav>'
        f'{link_block(relevant_links(links,page,"footer",self_path),"footer-nav")}'
        '<div class="footer-contacts">'
        f'<a data-track-event="phone" href="tel:{tel}">☎ {h(site["phone"])} 전화 상담</a>'
        f'<a href="{h(site["orderBaseUrl"])}" rel="noopener" target="_blank">판매처 바로가기 ↗</a></div>'
        '</div></footer>'
        +('<script src="/assets/analytics.js" defer></script>' if site.get('analytics',{}).get('enabled') else '')
        +'</body></html>')


def illustration(site,index,css_class,alt):
    image=site['imagePool'][index%len(site['imagePool'])]
    return f'<img class="{h(css_class)}" src="/assets/images/{h(image)}" alt="{h(alt)}" loading="{"eager" if index == 0 else "lazy"}" {"fetchpriority=\"high\"" if index == 0 else ""} width="1000" height="620">'


def phone_buttons(site,shop=True,context=''):
    tel=h(site['phone'].replace('-',''))
    content=f'<a class="button btn-coral" data-track-event="phone" href="tel:{tel}">☎ 전화 상담 {h(site["phone"])} <span aria-hidden="true">→</span></a>'
    if shop:
        content+=f'<a class="button btn-outline" href="{h(site["orderBaseUrl"])}" rel="noopener noreferrer" target="_blank">온라인 주문 확인 <span aria-hidden="true">↗</span></a>'
    return f'<div class="button-row {h(context)}">{content}</div>'


def product_html(products,selected):
    catalog={p['sku']:p for p in products}
    rows=[]
    for sku in selected:
        p=catalog[sku]
        rows.append('<article class="product">'
            '<div class="product-glyph" aria-hidden="true">✿</div><div class="product-copy">'
            f'<h3>{h(p["name"])}</h3><p>축하와 응원의 마음을 담은 식물 선물입니다.</p></div>'
            f'<a data-track-event="shop" class="button btn-outline" target="_blank" rel="noopener noreferrer" href="{h(p["orderUrl"])}">상품 보러가기 ↗</a>'
            '</article>')
    return ''.join(rows)


def moment_cards(site,pages):
    images=['moment-leaves.webp','moment-blooms.webp','hero-florist.webp','atelier-florist.webp']
    chosen=[p for p in pages if p['number']!=1][:4]
    return '<div class="moment-grid">'+''.join(
        '<a class="moment-card" href="'+h(url_path(p['number']))+'">'
        '<img loading="lazy" src="/assets/images/'+h(images[i])+'" alt="" width="420" height="250">'
        '<span class="moment-caption"><strong>'+h(p['topic'])+'</strong>'
        '<small>'+h(p['region'])+'</small><span class="moment-arrow" aria-hidden="true">→</span></span></a>'
        for i,p in enumerate(chosen))+'</div>'


def related_documents(pages,current=None,limit=4):
    chosen=[x for x in pages if x['number']!=current][:limit]
    return '<div class="related-grid">'+''.join(
        '<a class="related-card" href="'+h(url_path(p['number']))+'">'
        '<span class="related-icon" aria-hidden="true">✿</span>'
        '<strong>'+h(p['topic'])+'</strong><small>'+h(p['region'])+'</small>'
        '<span class="related-arrow" aria-hidden="true">↗</span></a>' for p in chosen)+'</div>'


def faq_markup(page):
    return ''.join(f'<details><summary>{h(q["q"])}</summary><p>{h(q["a"])}</p></details>' for q in page.get('faq',[]))


def article_body(page):
    return ('<article class="article-content" data-content-id="'+h(page['id'])+'">'+''.join(
        f'<section class="document-section" id="section-{i}"><span class="section-index">{i:02d}</span>'
        f'<h2>{h(s["heading"])}</h2><p>{h(s["paragraph"])}</p></section>'
        for i,s in enumerate(page['sections'],1))+'</article>')


def home(site,page,pages,products,links):
    """Free-form marketing index with the exact saved document content retained."""
    share='/assets/images/'+site['imagePool'][0]
    title=page['title'];region=site['region'];keyword=site['keyword']
    body=(head(site,title,page['intro'],'/',share)+header(site)+
        '<main id="main" class="home-page">'
        '<section class="home-hero"><div class="hero-inner"><div class="hero-copy">'
        f'<span class="section-tag">SPECIAL MOMENTS · {h(region)}</span>'
        '<h1>소중한 마음을 전하는<br><em>'+h(region.split()[-1])+' '+h(keyword)+'</em></h1>'
        '<p class="hero-description">'+h(page['intro'])+'</p>'
        +phone_buttons(site,context='hero-actions')+'</div>'
        '<div class="hero-art">'+illustration(site,0,'hero-plant','꽃 선물을 준비하는 일러스트')+'</div>'
        '</div></section>'
        '<section class="benefit-band" aria-label="서비스 이용 안내"><div class="wide-inner benefit-grid">'
        '<div><span aria-hidden="true">'+icon('leaf')+'</span><strong>상황에 맞는 선택</strong><small>용도와 장소를 함께 고려해요</small></div>'
        '<div><span aria-hidden="true">'+icon('truck')+'</span><strong>배송 상담</strong><small>마음을 전할 장소와 날짜를 함께 이야기해요</small></div>'
        '<div><span aria-hidden="true">'+icon('shield')+'</span><strong>편리한 주문 안내</strong><small>원하는 식물 선물을 간편하게 찾아요</small></div>'
        '<div><span aria-hidden="true">'+icon('heart')+'</span><strong>따뜻한 축하 메시지</strong><small>전하고 싶은 마음을 담아요</small></div>'
        '</div></section>'
        '<section class="home-section moments wide-inner"><div class="section-header"><div>'
        '<span class="section-tag">OCCASIONS</span><h2>이런 순간에 도움이 됩니다</h2>'
        '<p>축하하는 순간마다 어울리는 화분 이야기를 소개합니다.</p></div>'
        '<a href="/2.html" class="text-link">안내 문서 더 보기 ↗</a></div>'
        +moment_cards(site,pages)+'</section>'
        '<section class="story-split wide-inner"><div class="story-copy">'
        '<span class="section-tag">THOUGHTFUL SERVICE</span>'
        f'<h2>{h(page["sections"][0]["heading"])}</h2><p>{h(page["sections"][0]["paragraph"])}</p>'
        '<a href="/2.html" class="text-link">꽃 선물 이야기 더 보기 ↗</a>'
        '</div><div class="story-art">'+illustration(site,1,'story-picture','식물 선물을 준비하는 꽃집 일러스트')+'</div></section>'
        '<section class="home-section wide-inner"><div class="section-header"><div>'
        '<span class="section-tag">ORDER GUIDE</span><h2>처음부터 끝까지 간단하게</h2>'
        '<p>축하의 마음을 담아 상품을 고르고 주문하는 흐름을 소개합니다.</p></div></div>'
        '<div class="steps-grid"><div><span class="step-icon">'+icon('chat')+'</span><b>01</b><strong>상담 및 문의</strong><small>원하는 상황을 알려주세요</small></div>'
        '<div><span class="step-icon">'+icon('clipboard')+'</span><b>02</b><strong>식물 선물 고르기</strong><small>어울리는 화분을 찾아보세요</small></div>'
        '<div><span class="step-icon">'+icon('card')+'</span><b>03</b><strong>주문 진행</strong><small>마음을 전할 상품을 선택해요</small></div>'
        '<div><span class="step-icon">'+icon('gift')+'</span><b>04</b><strong>축하 마음 전하기</strong><small>축하 메시지로 기쁨을 더해요</small></div></div></section>'
        '<section class="home-section home-reading wide-inner"><div class="section-header"><div>'
        '<span class="section-tag">DETAIL GUIDE</span><h2>꽃과 식물에 담긴 이야기</h2>'
        '<p>선물의 의미와 공간에 어울리는 식물의 매력을 전합니다.</p></div></div>'
        +article_body(page)+'</section>'
        '<section class="home-section faq-section wide-inner"><div class="section-header"><div>'
        '<span class="section-tag">FAQ</span><h2>자주 묻는 질문</h2></div></div>'
        '<div class="faq-list">'+faq_markup(page)+'</div></section>'
        '<section class="order-cta home-cta wide-inner"><div><span class="section-tag">CONTACT</span>'
        f'<h2>{h(region)} {h(keyword)}, 궁금한 점부터 물어보세요.</h2>'
        '<p>축하화분과 승진화분으로 소중한 순간을 더욱 특별하게 전하세요.</p></div>'
        +phone_buttons(site)+'</section>'
        +link_block(relevant_links(links,page,'body'),'body-links wide-inner')
        +render_pagination(pages,page['number'])+'</main>')
    return body+footer(site,links,page)


def detail(site,page,pages,products,links):
    share='/assets/images/'+site['imagePool'][(page['number']-1)%len(site['imagePool'])]
    body=(head(site,page['title'],page['intro'],url_path(page['number']),share)+header(site)+
        '<main id="main" class="container document-page">'
        '<nav class="breadcrumbs" aria-label="현재 위치"><a href="/">홈</a><span aria-hidden="true">›</span><span>안내 문서</span></nav>'
        '<header class="doc-hero"><div class="doc-hero-copy">'
        f'<span class="section-tag">{h(page["region"])} · {h(page.get("searchKeyword",site["keyword"]))}</span>'
        f'<h1>{h(page["title"])}</h1><p class="lead">{h(page["intro"])}</p>'
        '</div><div class="doc-hero-art">'
        +illustration(site,(page['number']-1)%2,'hero-image','축하 식물의 범용 일러스트')+'</div></header>'
        '<div class="document-grid"><div class="document-main">'+article_body(page)+
        '<section class="recommendations" aria-labelledby="products-heading"><div class="section-heading">'
        '<span class="section-tag">PLANT COLLECTION</span><h2 id="products-heading">관련 식물 선물</h2>'
        '<p>취향과 공간에 따라 어울리는 화분을 만나보세요.</p>'
        '</div><div class="product-list">'+product_html(products,page['productSkus'])+'</div></section>'
        '<section class="faq" aria-label="자주 묻는 질문"><span class="section-tag">FAQ</span>'
        '<h2>자주 묻는 질문</h2><div class="faq-list">'+faq_markup(page)+'</div></section>'
        +link_block(relevant_links(links,page,'body'),'body-links')+
        '</div><aside class="document-aside" aria-label="빠른 주문 안내"><div class="aside-panel">'
        '<span class="section-tag">QUICK ORDER</span><h2>꽃 선물 상담</h2>'
        '<p>축하하는 마음을 전할 식물 선물을 함께 골라보세요.</p>'
        f'<a class="button btn-coral" data-track-event="phone" href="tel:{h(site["phone"].replace("-",""))}">☎ 전화 {h(site["phone"])}</a>'
        f'<a class="button btn-outline" href="{h(site["orderBaseUrl"])}" rel="noopener noreferrer" target="_blank">온라인 주문 ↗</a>'
        '</div><div class="aside-art">'+illustration(site,(page['number']+1)%2,'aside-picture','식물 선물의 일러스트')+'</div></aside></div>'
        '<section class="related-section"><div class="section-header"><div><span class="section-tag">MORE GUIDES</span>'
        '<h2>이런 내용도 함께 살펴보세요</h2></div></div>'+related_documents(pages,page['number'],3)+'</section>'
        '<section class="order-cta doc-cta"><div><h2>상담부터 편하게 시작하세요</h2>'
        '<p>마음에 드는 식물 선물과 축하 메시지로 새로운 시작을 응원하세요.</p></div>'
        +phone_buttons(site)+'</section>'
        +render_pagination(pages,page['number'])+'</main>')
    return body+footer(site,links,page)


def special_page(site,item,products,links):
    path=item['path']
    body=(head(site,item['title'],item['description'],'/'+quote(path),'/assets/images/'+site['imagePool'][0])+header(site)
        +'<main id="main" class="container document-page special-page">'
        '<nav class="breadcrumbs" aria-label="현재 위치"><a href="/">홈</a><span aria-hidden="true">›</span><span>이용 안내</span></nav>'
        '<header class="doc-hero"><div class="doc-hero-copy">'
        '<span class="section-tag">SERVICE GUIDE</span>'
        f'<h1>{h(item["title"])}</h1><p class="lead">{h(item["description"])}</p></div>'
        '<div class="doc-hero-art">'+illustration(site,1,'hero-image','식물 선물 일러스트')+'</div></header>'
        '<div class="special-content">')
    if item['type']=='calculator':
        options=''.join(f'<option value="{h(p["sku"])}">{h(p["name"])} ({p["referencePrice"]:,}원)</option>' for p in products)
        prices={p['sku']:p['referencePrice'] for p in products}
        body+=('<section class="document-section"><span class="section-tag">BUDGET CALCULATOR</span>'
            '<h2>화분 선물 예산 계산</h2><p>마음에 드는 상품과 수량을 골라 예산을 계산해 보세요.</p>'
            '<div class="calculator">'
            '<label for="sku">상품 종류</label><select id="sku">'+options+'</select>'
            '<label for="quantity">수량 (1~99)</label><input id="quantity" type="number" min="1" max="99" value="1" step="1">'
            '<button class="button btn-coral" type="button" id="estimate-submit">예산 계산하기</button>'
            '<output id="estimate" aria-live="polite">상품 합계 계산 중</output>'
            '</div></section>'
            f'<script type="application/json" id="price-data">{json.dumps(prices,ensure_ascii=False).replace("<",r"\u003c")}</script>'
            '<script src="/assets/calculator.js" defer></script>')
    else:
        body+=('<section class="document-section"><span class="section-tag">DELIVERY CHECK</span>'
        '<h2>화분이 어울리는 공간</h2><p>사무실과 행사장, 새로운 출발을 축하하는 자리까지 화분은 초록빛 생기와 따뜻한 마음을 더합니다.</p></section>'
        '<section class="document-section"><h2>축하의 순간을 함께해요</h2>'
        '<p>특별한 날의 분위기에 어울리는 꽃과 식물을 고르고, 축하 메시지를 담아 마음을 전하는 즐거움을 만나보세요.</p></section>')
    body+=link_block(relevant_links(links,None,'body',path),'body-links')
    body+=('<section class="order-cta doc-cta"><div><h2>도움이 필요하신가요?</h2>'
        '<p>소중한 순간을 위한 꽃과 식물 이야기를 함께 나눠보세요.</p></div>'
        +phone_buttons(site)+'</section></div></main>')
    return body+footer(site,links,None,path)


def error_page(site,links):
    return (head({**site,'publishEnabled':False,'publicIndexingApproved':False},'페이지를 찾을 수 없습니다','요청한 페이지가 존재하지 않습니다.','/404.html','/assets/images/'+site['imagePool'][0])
        +header(site)+'<main id="main" class="container utility-page"><h1>페이지를 찾을 수 없습니다</h1>'
        '<p>주소가 잘못되었거나 삭제된 페이지입니다.</p><p><a class="button btn-outline" href="/">첫 페이지로 돌아가기</a></p></main>'
        +footer(site,links))


def search_page(site,links):
    return (head({**site,'publishEnabled':False,'publicIndexingApproved':False},'사이트 글 검색','이 사이트 안의 글을 제목과 소개로 검색합니다.','/search.html','/assets/images/'+site['imagePool'][0])
        +header(site)+'<main id="main" class="container utility-page"><h1>사이트 글 검색</h1>'
        '<p>찾으려는 지역이나 주제를 입력하세요.</p>'
        '<form id="site-search-form"><label for="site-query">검색어</label>'
        '<input id="site-query" name="query" maxlength="80" required>'
        '<button class="button btn-coral" type="submit">검색</button></form>'
        '<ol id="search-results" aria-live="polite"></ol>'
        '<script src="/assets/search.js" defer></script></main>'
        +footer(site,links))
