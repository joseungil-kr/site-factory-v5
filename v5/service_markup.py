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
    """Use exact-domain canonical only for explicitly authorized indexable releases."""
    indexable=(not error and site.get('publicIndexingApproved',False)
               and ((site.get('id')=='daysky' and site.get('domain')=='https://daysky.nalmada.net')
                    or (site.get('id')=='onehour-sky'
                        and site.get('domain')=='https://1hrsky.nalmada.net'
                        and site.get('publicIndexingScope')=='onehour-5436-20261028')))
    robots='index,follow' if indexable else 'noindex,nofollow'
    canonical=('<link rel="canonical" href="'+h(site['domain'].rstrip('/')+path)+'">'
               if indexable else '')
    title_text=h(title if site['brand'] in title else title+' | '+site['brand'])
    summary=h(description[:155])
    verification=('<meta name="naver-site-verification" content="'+h(site['naverSiteVerification'])+'">'
                  if indexable and site.get('id')=='onehour-sky' and path=='/' else '')
    ogimage=('<meta property="og:image" content="'
             +h(site['domain']+'/assets/images/'+site['imagePool'][0])+'">'
             if indexable else '')
    return ('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>'+title_text+'</title>'
            '<meta name="description" content="'+summary+'">'
            '<meta name="robots" content="'+robots+'">'+canonical+verification
            +'<meta property="og:type" content="website">'
            +'<meta property="og:title" content="'+title_text+'">'
            +'<meta property="og:description" content="'+summary+'">'+ogimage
            +'<link rel="stylesheet" href="/assets/service.css"></head>')

def _image(site,i,css,alt):
    name=site['imagePool'][i%len(site['imagePool'])]
    description=('스카이차 차량을 이용한 실제 건물 외부 작업 사진'
                 if site.get('id')=='daysky' and name.endswith('.webp') else alt)
    return f'<img src="/assets/images/{h(name)}" class="{h(css)}" alt="{h(description)}" loading="{"eager" if i==0 else "lazy"}">'


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
            '</div><div><p>'+h(site.get('serviceHours','전화 상담'))+'</p>'
            f'<a href="tel:{_tel(site)}">{h(site["phone"])}</a></div></div></footer>'
            '<div class="mobile-dial">'+_phone(site,'상담 전화')+'</div></body></html>')


def _prices(site,rates,services,selected=None):
    if site.get('id')=='onehour-sky':
        return ('<div class="rate-note onehour-pricing"><strong>1시간 작업도 반나절 요금 기준</strong>'
                '<p>'+h(site['minimumBillingText'])+'</p>'
                '<p>장비 종류·현장 접근 조건·요청 시각에 따라 최종 금액이 달라질 수 있습니다. '
                '정확한 금액은 전화로 상담해 주세요.</p></div>'
                +_phone(site,'반나절 기준 견적 상담'))
    selected=set(selected or [s['id'] for s in services])
    by_id={s['id']:s for s in services}
    rows=[]
    for p in rates['plans']:
        if p['serviceId'] not in selected:continue
        name=by_id[p['serviceId']]['name']
        rows.append('<tr><th scope="row">'+h(name)+'</th>'+
            f'<td>{p["hour"]:,}원</td><td>{p["halfDay"]:,}원</td><td>{p["fullDay"]:,}원</td></tr>')
    return ('<div class="table-scroll"><table class="rate-table"><caption>'+h(site['serviceLabel'])+' 기본 요금표</caption>'
            '<thead><tr><th scope="col">서비스</th><th scope="col">기본 1시간</th>'
            '<th scope="col">반나절(4시간)</th><th scope="col">하루(8시간)</th></tr></thead>'
            '<tbody>'+''.join(rows)+'</tbody></table></div>'
            '<p class="rate-note">부가세 별도 · 운영자 승인 기본 요금 · '
            '현장 여건과 추가 작업 조건은 전화 상담으로 확인합니다.</p>')


def _faq(faq):
    if not faq:return ''
    return '<section class="faq"><h2>자주 묻는 질문</h2>'+''.join(
        '<details><summary>'+h(x['q'])+'</summary><p>'+h(x['a'])+'</p></details>' for x in faq)+'</section>'


def _sections(page):
    return '<article class="article-content">'+''.join(
        '<section class="text-section"><h2>'+h(x['heading'])+'</h2><p>'+h(x['paragraph'])+'</p></section>'
        for x in page['sections'])+'</article>'


def _call_section(site):
    title=site.get('callTitle','작업 위치와 현장 조건부터 알려주세요')
    description=site.get('callDescription','희망 지역, 작업 종류, 상담 내용과 일정을 알려주시면 비용 상담을 도와드립니다.')
    hours=site.get('serviceHours','전화 상담')
    return ('<section class="contact-band"><div><span class="eyebrow light">TELEPHONE CONSULTATION</span>'
            '<h2>'+h(title)+'</h2><p>'+h(description)+' '+h(hours)+'</p></div>'+
            _phone(site)+'</section>')


def _onehour_region_links(page,pages):
    """V4 official region hierarchy for scalable 5,436-page discovery."""
    if page["number"]==1:
        children=[p for p in pages[1:] if p.get("regionLevel")=="province"]
    else:
        children=[p for p in pages[1:] if p.get("parentRegionCode")==page.get("regionCode")]
    parent=next((p for p in pages[1:] if p.get("regionCode")==page.get("parentRegionCode")),None)
    links='<nav class="region-links" aria-label="지역별 스카이차 안내"><h2>하위 지역별 스카이차 안내</h2><div>'
    if parent:
        links+=f'<a href="{url_path(parent["number"])}">상위 지역: {h(parent["region"])} ↗</a>'
    elif page["number"]!=1:
        links+='<a href="/">전국 안내 ↗</a>'
    links+=''.join(f'<a href="{url_path(p["number"])}">{h(p["region"])} ↗</a>' for p in children)
    return links+'</div></nav>'


def home(site,page,pages,services,rates):
    body=_head(site,page['title'],page['intro'],'/')+_header(site)
    if site.get('id')=='onehour-sky':
        hero_h1='<h1>'+h(page['title'])+'</h1>'
        hero_note='<p>'+h(site['heroSlogan'])+'</p>'
    else:
        hero_h1=f'<h1>{h(site["region"])} <em>{h(site["serviceLabel"])} 작업</em><br>필요할 때, {h(site["brand"])}</h1>'
        hero_note=''
    body+=('<main id="main" class="wrap"><section class="hero"><div class="hero-copy">'
           '<span class="eyebrow">LOCAL SERVICE CONSULTATION</span>'
           +hero_h1+hero_note
           +f'<p>{h(page["intro"])}</p>'
           +'<div class="hero-actions">'+_phone(site)+'<a class="outline-button" href="#rates">'+('반나절 기준요금 상담' if site.get('id')=='onehour-sky' else '작업 요금표 보기')+'</a></div>'
           f'<p class="service-hours">● {h(site.get("serviceHours","전화 상담"))}</p></div>'
           '<div class="hero-visual">'+_image(site,0,'hero-art','서비스 현장 안내용 공용 일러스트')+'</div></section>')
    body+=('<section class="intro-tiles"><div><span class="accent-number">01</span><h2>'+h(' · '.join(s['name'] for s in services))+'</h2>'
           '<p>이용 목적과 현장 여건에 맞는 서비스 범위를 상담합니다.</p></div>'
           '<div><span class="accent-number">02</span><h2>'+h('·'.join(site.get('workTypes',[])[:3]) or site['serviceLabel'])+'</h2>'
           '<p>다양한 작업 유형과 이용 가능 범위를 확인해 보세요.</p></div>'
           '<div><span class="accent-number">03</span><h2>전화로 간편 문의</h2>'
           '<p>현장 주소와 작업 내용을 알려주시면 비용을 안내합니다.</p></div></section>')
    facts=site.get('trustFacts') or []
    if facts:
        body+='<section class="trust-grid" aria-label="안전 운행 및 상담 안내">'
        for fact in facts:
            body+='<div><strong>'+h(fact['title'])+'</strong><p>'+h(fact['text'])+'</p></div>'
        body+='</section>'
    body+='<section id="equipment" class="block-section"><span class="eyebrow">SERVICE OPTIONS</span><h2>서비스 항목 안내</h2><div class="equip-grid">'
    for i,s in enumerate(services):
        body+='<div class="equip-card">'+_image(site,i+1,'equip-art','서비스 안내용 공용 일러스트')+'<h3>'+h(s['name'])+'</h3><p>'+h(s['description'])+'</p></div>'
    body+='</div></section>'
    body+='<section id="rates" class="block-section rate-section"><span class="eyebrow">PRICING</span><h2>'+h(site['serviceLabel'])+(' 반나절 기준요금 상담' if site.get('id')=='onehour-sky' else ' 기본 요금')+'</h2>'+_prices(site,rates,services)+'</section>'
    body+='<section id="works" class="block-section works-section"><span class="eyebrow">WORK TYPES</span><h2>상담 가능한 서비스 유형</h2><div class="work-grid">'
    for name in site.get('workTypes',[]):body+='<span>'+h(name)+'</span>'
    body+='</div></section>'
    body+='<section class="block-section doc-overview"><span class="eyebrow">FIELD GUIDE</span><h2>서비스 이용 안내</h2>'+_sections(page)+'</section>'
    body+=_faq(page.get('faq',[]))+_call_section(site)
    body+='<nav id="regions" class="region-links" aria-label="지역별 서비스 문서"><h2>지역별 ' + h(site['serviceLabel']) + ' 안내</h2><div>'
    for p in (p for p in pages[1:] if p.get("regionLevel")=="province") if site.get('id')=='onehour-sky' else pages[1:]:
        body+=f'<a href="{url_path(p["number"])}">{h(p["region"])} ↗</a>'
    body+='</div></nav>'+render_pagination(pages,1)+'</main>'+_footer(site)
    return body


def detail(site,page,pages,services,rates):
    body=_head(site,page['title'],page['intro'],url_path(page['number']))+_header(site)
    body+='<main id="main" class="wrap document"><nav class="breadcrumb" aria-label="현재 위치"><a href="/">홈</a><span>›</span>'+h(page['region'])+'</nav>'
    body+='<header class="document-header"><div><span class="eyebrow">LOCAL SERVICE GUIDE</span>'
    body+=f'<h1>{h(page["title"])}</h1><p class="lead">{h(page["intro"])}</p><p class="service-hours">● {h(site.get("serviceHours","전화 상담"))}</p></div>'
    body+=_image(site,page['number']%len(site['imagePool']),'document-art','서비스 현장 안내용 공용 일러스트')+'</header>'
    body+='<div class="article-layout"><div>'+_sections(page)
    body+='<section class="block-section rate-section"><h2>'+h(page['region'])+' '+h(site['serviceLabel'])+(' 반나절 기준요금 상담' if site.get('id')=='onehour-sky' else ' 기본 요금')+'</h2>'+_prices(site,rates,services,page['serviceIds'])+'</section>'
    body+=_faq(page.get('faq',[]))+'</div><aside class="side-contact"><strong>현장 상담 안내</strong><p>현장 위치, 요청 범위와 희망 이용 시간을 알려주세요.</p>'+_phone(site,'전화하기')+'</aside></div>'
    body+=_call_section(site)
    if site.get('id')=='onehour-sky':
        body+=_onehour_region_links(page,pages)
    body+=render_pagination(pages,page['number'])+'</main>'+_footer(site)
    return body


def error_page(site):
    return (_head(site,'페이지를 찾을 수 없습니다','요청한 페이지가 존재하지 않습니다.','/404.html',True)
            +_header(site)+'<main id="main" class="wrap not-found"><h1>페이지를 찾을 수 없습니다</h1>'
            '<p>주소를 다시 확인하거나 홈페이지로 이동해 주세요.</p><a class="outline-button" href="/">홈으로 이동</a></main>'
            +_footer(site))