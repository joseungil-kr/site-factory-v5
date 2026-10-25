"""Responsive, phone-first site renderer for general equipment/service leads.

No webshop checkout controls, product SKUs or flower-specific copy.
All regional/brand/price text is escaped HTML, not embedded in artwork.
"""
from __future__ import annotations
from urllib.parse import quote
from .markup import h, render_pagination, filename, url_path


def _tel(site):
    return ''.join(c for c in site['phone'] if c.isdigit())


def _head(site,title,description,path,error=False):
    # The service model cannot be indexed or published without an explicit future gate.
    return ('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{h(title)} | {h(site["brand"])}</title>'
            f'<meta name="description" content="{h(description[:155])}">'
            '<meta name="robots" content="noindex,nofollow">'
            '<link rel="stylesheet" href="/assets/service.css"></head>')


def _image(site,i,css,alt):
    name=site['imagePool'][i%len(site['imagePool'])]
    return f'<img src="/assets/images/{h(name)}" class="{h(css)}" alt="{h(alt)}" loading="{"eager" if i==0 else "lazy"}">'


def _phone(site,label='전화 견적 문의'):
    return f'<a class="call-button" href="tel:{_tel(site)}">☎ {h(label)} <strong>{h(site["phone"])}</strong></a>'


def _header(site):
    nav=''.join(f'<a href="{h(x["href"])}">{h(x["label"])}</a>' for x in site.get('navigation',[]))
    return ('<body><a class="skip" href="#main">본문 바로가기</a><header class="site-header">'
            '<div class="header-wrap"><a class="brand" href="/">'
            '<span aria-hidden="true" class="brand-mark">↗</span><span>'+h(site['brand'])+'</span></a>'
            '<nav aria-label="주요 메뉴">'+nav+'</nav>'
            f'<a class="top-tel" href="tel:{_tel(site)}">☎ {h(site["phone"])}</a></div></header>')


def _footer(site):
    return ('<footer class="site-footer"><div class="footer-wrap"><div>'
            f'<strong>{h(site["brand"])}</strong><p>{h(site["region"])} · {h(site["serviceLabel"])} 상담</p>'
            '</div><div><p>24시간 365일 전화 상담</p>'
            f'<a href="tel:{_tel(site)}">{h(site["phone"])}</a></div></div></footer>'
            '<div class="mobile-dial">'+_phone(site,'상담 전화')+'</div></body></html>')


def _prices(rates,services,selected=None):
    selected=set(selected or [s['id'] for s in services])
    by_id={s['id']:s for s in services}
    rows=[]
    for p in rates['plans']:
        if p['serviceId'] not in selected:continue
        name=by_id[p['serviceId']]['name']
        rows.append('<tr><th scope="row">'+h(name)+'</th>'+
            f'<td>{p["hour"]:,}원</td><td>{p["halfDay"]:,}원</td><td>{p["fullDay"]:,}원</td></tr>')
    return ('<div class="table-scroll"><table class="rate-table"><caption>스카이차 기본 요금표</caption>'
            '<thead><tr><th scope="col">장비</th><th scope="col">기본 1시간</th>'
            '<th scope="col">반나절(4시간)</th><th scope="col">하루(8시간)</th></tr></thead>'
            '<tbody>'+''.join(rows)+'</tbody></table></div>'
            '<p class="rate-note">부가세 별도 · 타사 공개 요금표를 참고한 기본 요금 · '
            '현장 여건과 야간·추가 작업 비용은 전화 상담으로 확인합니다.</p>')


def _faq(faq):
    if not faq:return ''
    return '<section class="faq"><h2>자주 묻는 질문</h2>'+''.join(
        '<details><summary>'+h(x['q'])+'</summary><p>'+h(x['a'])+'</p></details>' for x in faq)+'</section>'


def _sections(page):
    return '<article class="article-content">'+''.join(
        '<section class="text-section"><h2>'+h(x['heading'])+'</h2><p>'+h(x['paragraph'])+'</p></section>'
        for x in page['sections'])+'</article>'


def _call_section(site):
    return ('<section class="contact-band"><div><span class="eyebrow light">TELEPHONE CONSULTATION</span>'
            '<h2>작업 위치와 현장 조건부터 알려주세요</h2>'
            '<p>작업 종류, 현장 주소, 대략적인 작업 높이와 예상 시간을 알려주시면 장비 선택과 비용 상담을 도와드립니다. '
            '24시간 상담 가능하며 배차 가능 시점은 별도로 안내합니다.</p></div>'+_phone(site)+'</section>')


def home(site,page,pages,services,rates):
    body=_head(site,page['title'],page['intro'],'/')+_header(site)
    body+=('<main id="main" class="wrap"><section class="hero"><div class="hero-copy">'
           '<span class="eyebrow">SEOUL · GYEONGGI · SKY TRUCK</span>'
           f'<h1>{h(site["region"])} <em>{h(site["serviceLabel"])} 작업</em><br>필요할 때, {h(site["brand"])}</h1>'
           f'<p>{h(page["intro"])}</p>'
           '<div class="hero-actions">'+_phone(site)+'<a class="outline-button" href="#rates">작업 요금표 보기</a></div>'
           '<p class="service-hours">● 24시간 365일 전화 상담</p></div>'
           '<div class="hero-visual">'+_image(site,0,'hero-art','한국 건물 앞에서 작업하는 스카이차를 표현한 예시 일러스트')+'</div></section>')
    body+=('<section class="intro-tiles"><div><span class="accent-number">01</span><h2>1톤·3.5톤·5톤</h2>'
           '<p>높이와 현장 여건에 맞춰 적합한 장비를 상담합니다.</p></div>'
           '<div><span class="accent-number">02</span><h2>외벽·간판·시설물</h2>'
           '<p>유리·페인트·보수 등 다양한 고소작업 현장을 대상으로 합니다.</p></div>'
           '<div><span class="accent-number">03</span><h2>전화로 간편 문의</h2>'
           '<p>현장 주소와 작업 내용을 알려주시면 비용을 안내합니다.</p></div></section>')
    body+='<section id="equipment" class="block-section"><span class="eyebrow">EQUIPMENT</span><h2>작업에 맞는 장비 선택</h2><div class="equip-grid">'
    for i,s in enumerate(services):
        body+='<div class="equip-card">'+_image(site,i+1,'equip-art','스카이차 장비 관련 공용 일러스트')+'<h3>'+h(s['name'])+'</h3><p>'+h(s['description'])+'</p></div>'
    body+='</div></section>'
    body+='<section id="rates" class="block-section rate-section"><span class="eyebrow">PRICING</span><h2>스카이차 작업 기본 요금</h2>'+_prices(rates,services)+'</section>'
    body+='<section id="works" class="block-section works-section"><span class="eyebrow">WORK TYPES</span><h2>다양한 고소작업 현장에 대응합니다</h2><div class="work-grid">'
    for name in site.get('workTypes',[]):body+='<span>'+h(name)+'</span>'
    body+='</div></section>'
    body+='<section class="block-section doc-overview"><span class="eyebrow">FIELD GUIDE</span><h2>현장과 장비를 이해하는 안내</h2>'+_sections(page)+'</section>'
    body+=_faq(page.get('faq',[]))+_call_section(site)
    body+='<nav class="region-links" aria-label="안산 지역 상세 문서"><h2>안산 지역별 스카이차 작업 정보</h2><div>'
    for p in pages[1:]:body+=f'<a href="{url_path(p["number"])}">{h(p["region"])} ↗</a>'
    body+='</div></nav>'+render_pagination(pages,1)+'</main>'+_footer(site)
    return body


def detail(site,page,pages,services,rates):
    body=_head(site,page['title'],page['intro'],url_path(page['number']))+_header(site)
    body+='<main id="main" class="wrap document"><nav class="breadcrumb" aria-label="현재 위치"><a href="/">홈</a><span>›</span>'+h(page['region'])+'</nav>'
    body+='<header class="document-header"><div><span class="eyebrow">LOCAL SKY TRUCK GUIDE</span>'
    body+=f'<h1>{h(page["title"])}</h1><p class="lead">{h(page["intro"])}</p><p class="service-hours">● 24시간 365일 전화 상담</p></div>'
    body+=_image(site,page['number']%len(site['imagePool']),'document-art','스카이차 작업 환경 안내용 공용 일러스트')+'</header>'
    body+='<div class="article-layout"><div>'+_sections(page)
    body+='<section class="block-section rate-section"><h2>'+h(page['region'])+' 스카이차 기본 요금</h2>'+_prices(rates,services,page['serviceIds'])+'</section>'
    body+=_faq(page.get('faq',[]))+'</div><aside class="side-contact"><strong>현장 상담 안내</strong><p>작업 위치, 높이와 이용 시간을 말씀해 주세요.</p>'+_phone(site,'전화하기')+'</aside></div>'
    body+=_call_section(site)+render_pagination(pages,page['number'])+'</main>'+_footer(site)
    return body


def error_page(site):
    return (_head(site,'페이지를 찾을 수 없습니다','요청한 페이지가 존재하지 않습니다.','/404.html',True)
            +_header(site)+'<main id="main" class="wrap not-found"><h1>페이지를 찾을 수 없습니다</h1>'
            '<p>주소를 다시 확인하거나 홈페이지로 이동해 주세요.</p><a class="outline-button" href="/">홈으로 이동</a></main>'
            +_footer(site))
