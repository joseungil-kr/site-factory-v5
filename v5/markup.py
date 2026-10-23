"""HTML, navigation, special page modules and shared UI rendering."""
from __future__ import annotations
import html
import json
from urllib.parse import quote


def h(text):
    return html.escape(str(text),quote=True)


def filename(number):
    return 'index.html' if number == 1 else f'{number}.html'


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
    all_links=[]
    for n in pagination(pages,number):
        if n==number:
            all_links.append(f'<span aria-current="page" class="active">{n}</span>')
        else:
            all_links.append(f'<a href="{h(url_path(n))}" aria-label="{n}번 페이지">{n}</a>')
    return '<nav class="pagination" aria-label="다른 글 페이지">'+''.join(all_links)+'</nav>'


def relevant_links(links, page, placement, self_path=None):
    out=[]
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
        out.append(link)
    return out


def link_block(links, css_class):
    if not links:
        return ''
    return f'<nav class="{h(css_class)}" aria-label="추가 안내 링크">'+''.join(
        f'<a href="/{quote(l["target"])}">{h(l["label"])}</a>' for l in links)+'</nav>'


def head(site,title,description,path,share_image):
    canonical = ''
    robots = '<meta name="robots" content="noindex,nofollow">'
    if site['domain'] and site['publishEnabled']:
        domain = site['domain'].rstrip('/')
        robots='<meta name="robots" content="index,follow">'
        canonical=f'<link rel="canonical" href="{h(domain+path)}">'
    return ('<!doctype html>\n<html lang="ko"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{h(title)} | {h(site["brand"])}</title>'
        f'<meta name="description" content="{h(description[:155])}">{robots}{canonical}'
        '<link rel="stylesheet" href="/assets/site.css">'
        f'<link rel="stylesheet" href="/assets/theme-{h(site["theme"])}.css">'
        f'<meta property="og:title" content="{h(title)}">'
        f'<meta property="og:description" content="{h(description[:155])}">'
        f'<meta property="og:image" content="{h(share_image)}">'
        '</head>')


def header(site):
    return ('<body><a class="skip-link" href="#main">본문 바로가기</a>'
        '<header class="site-header">'
        f'<a class="brand" href="/">{h(site["brand"])}</a>'
        f'<a data-track-event="phone" class="phone" href="tel:{h(site["phone"].replace("-",""))}">☎ {h(site["phone"])}</a>'
        '</header>'
        + ('<aside class="preview-banner" role="note"><strong>임시 시안 · 검색 제외</strong> 상품 이미지·가격·재고와 배송 조건은 최종 확인 전입니다. 화면과 동선을 검토해 주세요.</aside>'
           if not site.get('publishEnabled',False) else ''))


def footer(site,links,page=None,self_path=None):
    return ('<footer class="site-footer">'
        '<p>승진 축하 화분 · 배송과 상품 조건은 판매처에서 확인해 주세요.</p>'
        f'{link_block(relevant_links(links,page,"footer",self_path),"footer-nav")}'
        f'<p>전화 상담 <a data-track-event="phone" href="tel:{h(site["phone"].replace("-",""))}">{h(site["phone"])}</a> · '
        f'<a href="{h(site["orderBaseUrl"])}" rel="noopener" target="_blank">판매처 바로가기</a></p>'
        '</footer>'+('<script src="/assets/analytics.js" defer></script>' if site.get('analytics',{}).get('enabled') else '')+'</body></html>')


def product_html(products, selected):
    catalog={p['sku']:p for p in products}
    blocks=[]
    for sku in selected:
        p=catalog[sku]
        blocks.append('<article class="product">'
            + (f'<img class="product-photo" src="{h(p["imageUrl"])}" alt="{h(p["name"])} 판매처 참고사진" width="270" height="270" loading="lazy">' if p.get('imageUrl') else '')
            + f'<h3>{h(p["name"])}</h3>'
            '<p>이미지·상품 구성·최종 가격은 판매처에서 확인해 주세요.</p>'
            f'<p class="source-date">가격 참고 자료 기준일: {h(p["referenceDate"])}</p>'
            f'<a data-track-event="shop" class="button secondary" target="_blank" rel="noopener noreferrer" href="{h(p["orderUrl"])}">{h(p["name"])} 온라인 주문 확인</a>'
            '</article>')
    return ''.join(blocks)


def detail(site,page,pages,products,links):
    image=site['imagePool'][(page['number']-1)%len(site['imagePool'])]
    share=f'/assets/images/{image}'
    path=url_path(page['number'])
    body=(head(site,page['title'],page['intro'],path,share)+header(site)+
        '<main id="main" class="container">'
        f'<p class="eyebrow">{h(page["region"])} · {h(site["keyword"])}</p>'
        f'<h1>{h(page["title"])}</h1>'
        f'<img class="hero-image" src="{h(share)}" alt="{h(site['keyword'])} 공용 이미지 예시" width="800" height="400">'
        f'<p class="lead">{h(page["intro"])}</p>'
        '<article class="article-content" data-content-id="'+h(page['id'])+'">')
    for section in page['sections']:
        body+=f'<section><h2>{h(section["heading"])}</h2><p>{h(section["paragraph"])}</p></section>'
    body+='</article>'
    body+=('<section class="recommendations"><h2>상품 정보 확인</h2>'
        '<p>제품과 가격은 변경될 수 있습니다. 구매 전 판매처의 최신 정보를 확인하세요.</p>'
        f'{product_html(products,page["productSkus"])}</section>')
    body+=('<section class="faq"><h2>자주 묻는 질문</h2>'+''.join(
        f'<details><summary>{h(q["q"])}</summary><p>{h(q["a"])}</p></details>' for q in page.get('faq',[]))+'</section>')
    body+=link_block(relevant_links(links,page,'body'),'body-links')
    body+=f'<section class="order-cta"><h2>상담으로 확인하기</h2><a data-track-event="phone" class="button" href="tel:{h(site["phone"].replace("-",""))}">☎ {h(site["phone"])} 전화 문의</a></section>'
    body+=render_pagination(pages,page['number'])
    body+='</main>'
    return body+footer(site,links,page)


def special_page(site,item,products,links):
    path=item['path']
    body=(head(site,item['title'],item['description'],'/'+quote(path),'/assets/images/'+site['imagePool'][0])+header(site)
         +'<main id="main" class="container">'
         f'<h1>{h(item["title"])}</h1><p class="lead">{h(item["description"])}</p>')
    if item['type']=='calculator':
        options=''.join(f'<option value="{h(p["sku"])}">{h(p["name"])} ({p["referencePrice"]:,}원 참고)</option>' for p in products)
        prices={p['sku']:p['referencePrice'] for p in products}
        body+=('<div class="calculator">'
            '<label for="sku">화분 종류</label><select id="sku">'+options+'</select>'
            '<label for="quantity">수량 (1~99)</label><input id="quantity" type="number" min="1" max="99" value="1" step="1">'
            '<button type="button" id="estimate-submit">예산 계산</button><output id="estimate" aria-live="polite">참고 합계 계산 중</output>'
            '<p class="fine">지난 가격 기록을 이용한 단순 참고 계산입니다. 배송비·추가 선택 사항은 미포함이며 실제 결제 금액이 아닙니다.</p>'
            '</div>'
            f'<script type="application/json" id="price-data">{json.dumps(prices,ensure_ascii=False).replace('<',r'\u003c')}</script>'
            '<script src="/assets/calculator.js" defer></script>')
    else:
        body+='<section><h2>주문 전에 확인할 내용</h2><p>받는 분의 회사명·주소·연락처를 준비하세요. 상품 재고와 희망 배송일은 전화 또는 온라인 주문 화면에서 확인해 주세요.</p></section>'
    body+=link_block(relevant_links(links,None,'body',path),'body-links')
    body+='</main>'
    return body+footer(site,links,None,path)


def error_page(site,links):
    return (head({**site,'publishEnabled':False},'페이지를 찾을 수 없습니다','요청한 페이지가 존재하지 않습니다.','/404.html','/assets/images/'+site['imagePool'][0])
        +header(site)+'<main id="main" class="container"><h1>페이지를 찾을 수 없습니다</h1>'
        '<p>주소가 잘못되었거나 삭제된 페이지입니다.</p><p><a href="/">첫 페이지로 돌아가기</a></p></main>'
        +footer(site,links))


def search_page(site,links):
    return (head({**site,'publishEnabled':False},'사이트 글 검색','이 사이트 안의 글을 제목과 소개로 검색합니다.','/search.html','/assets/images/'+site['imagePool'][0])
        +header(site)
        +'<main id="main" class="container"><h1>사이트 글 검색</h1><p>찾으려는 지역이나 주제를 입력하세요.</p>'
         '<form id="site-search-form"><label for="site-query">검색어</label> '
         '<input id="site-query" name="query" maxlength="80" required> '
         '<button type="submit">검색</button></form>'
         '<ol id="search-results" aria-live="polite"></ol>'
         '<script src="/assets/search.js" defer></script></main>'
        +footer(site,links))
