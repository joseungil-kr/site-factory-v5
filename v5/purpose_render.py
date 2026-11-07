"""V5.1 purpose-scoped assembly for newly planned product sites.

Values supplied by the research ledger are facts; copy pools only provide
phrasing. No stock, delivery promise or price is inferred from old fields.
"""
from __future__ import annotations
import hashlib
import json
import re
from urllib.parse import quote
from .config import ConfigError
from . import markup


def _chosen(items, page, slot):
    if not isinstance(items, list) or not items:
        raise ConfigError(f'purpose pool missing {slot}')
    # Isolated county prototype: repeat occurrences of a legitimate buying purpose
    # cover different useful buyer questions rather than selecting the same copy.
    # All other V5.1 sites retain the original deterministic hash selection.
    if page.get('siteVariantPolicy')=='county-v51' and slot.startswith('section:') and len(items)>1:
        index=page.get('variantIndex')
        if type(index) is not int or index<0:
            raise ConfigError('county-v51 requires nonnegative variantIndex')
        offset=int.from_bytes(hashlib.sha256((page['purpose']+':'+slot).encode()).digest()[:4],'big')
        return items[(index+offset)%len(items)]
    digest = hashlib.sha256((page['id'] + ':' + slot).encode()).digest()
    return items[int.from_bytes(digest[:8], 'big') % len(items)]


def _text(value, page):
    if not isinstance(value, str) or not value.strip():
        raise ConfigError('purpose pool text must be nonempty')
    # Known page variables only; renderers escape the assembled text.
    # Unknown variables fail instead of leaking template syntax to customers.
    allowed={'region':page.get('region'),'county':page.get('county'),
             'province':page.get('province'),'parentRegion':page.get('parentRegion'),
             'townships':page.get('townships'),'townshipCount':page.get('townshipCount')}
    def replace(match):
        key=match.group(1)
        if key not in allowed or not isinstance(allowed[key],str) or not allowed[key].strip():
            raise ConfigError(f'unknown or missing purpose placeholder: {key}')
        return allowed[key]
    return re.sub(r'\{([A-Za-z][A-Za-z0-9]*)\}',replace,value)


def assemble(page, pools, products, *, service=False):
    purpose = page.get('purpose')
    pool = pools.get(purpose) if isinstance(pools, dict) else None
    if not purpose or not isinstance(pool, dict):
        raise ConfigError(f'page {page.get("id")} missing a matching purpose pool')
    field='serviceIds' if service else 'productSkus'
    key='id' if service else 'sku'
    permitted = pool.get(field, [])
    selected = page.get(field, [])
    catalog = {p[key]: p for p in products}
    if not selected or any(s not in permitted or s not in catalog for s in selected):
        raise ConfigError(f'page {page["id"]} has selections outside its purpose pool')
    sections = pool.get('sections')
    faqs = pool.get('faqs')
    if not isinstance(sections, list) or not isinstance(faqs, list) or not faqs:
        raise ConfigError('purpose pool needs sections and FAQs')
    # Preserve every distinct supported slot; the old choice/order-only loop
    # silently discarded delivery, ribbon, budget and venue sections.
    slots=[]
    for item in sections:
        if not isinstance(item,dict) or not isinstance(item.get('slot'),str) or not item['slot'].strip():
            raise ConfigError('purpose section requires a named slot')
        if item['slot'] not in slots: slots.append(item['slot'])
    if not {'choice','order'}.issubset(slots):
        raise ConfigError('purpose pool needs choice and order slots')
    slots=['choice','order']+[x for x in slots if x not in ('choice','order')]
    resolved_sections=[]
    for slot in slots:
        section=_chosen([x for x in sections if x['slot']==slot],page,'section:'+slot)
        resolved_sections.append({'heading':_text(section.get('heading'),page),
                                  'paragraph':_text(section.get('paragraph'),page),'slot':slot})
    if any(not isinstance(f,dict) or not f.get('q') or not f.get('a') for f in faqs):
        raise ConfigError('invalid purpose pool FAQ')
    ordered_faq=sorted(enumerate(faqs),key=lambda pair:hashlib.sha256((page['id']+':faq:'+str(pair[0])).encode()).digest())
    assembled={**page, 'intro': _text(_chosen(pool.get('introductions'), page, 'intro'), page),
            'sections': resolved_sections,
            'faq': [{'q': _text(f.get('q'), page), 'a': _text(f.get('a'), page)}
                    for _,f in ordered_faq[:min(5,len(ordered_faq))]]}
    if page.get('siteVariantPolicy')=='county-v51' and not service:
        # A build cannot silently show B205 or 109,000원 on a page with only
        # B201/B202 cards. Compare all rendered customer-facing text.
        body=' '.join([assembled['intro']]+
            [s['heading']+' '+s['paragraph'] for s in assembled['sections']]+
            [f['q']+' '+f['a'] for f in assembled['faq']])
        # County-only, Unicode-suffix-aware extraction.
        from scripts.county_copy_pools import product_skus_in_text,listed_prices_in_text
        named=product_skus_in_text(body)
        allowed=set(selected)
        if named-allowed:
            raise ConfigError('county-v51 off-card SKU in copy: '+str(sorted(named-allowed)))
        amounts={catalog[sku].get('referencePrice') for sku in selected}
        allowed_amounts={format(price,',')+'원' for price in amounts if type(price) is int}
        allowed_amounts|={format(abs(x-y),',')+'원' for x in amounts for y in amounts
                          if type(x) is int and type(y) is int and x!=y}
        seen_prices=listed_prices_in_text(body)
        if seen_prices-allowed_amounts:
            raise ConfigError('county-v51 off-card price in copy: '+str(sorted(seen_prices-allowed_amounts)))
        if assembled['intro'] in [x['paragraph'] for x in assembled['sections']]:
            raise ConfigError('county-v51 duplicated introduction as section')
    return assembled


def _has_proof(product, kind, site_id=None):
    if kind == 'price':
        return (product.get('priceConfirmed') is True and type(product.get('referencePrice')) is int
                and product['referencePrice']>0 and bool(product.get('priceEvidence'))
                and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(product.get('priceCheckedOn','')))))
    return (product.get('imageUseApproved') is True and bool(product.get('imageApprovalEvidence'))
            and isinstance(product.get('imageApprovedFor'),list) and site_id in product['imageApprovedFor']
            and bool(product.get('imageUrl')))


def products_html(products, selected, site_id=None):
    catalog={p['sku']:p for p in products}
    rows=[]
    for sku in selected:
        p=catalog[sku]
        image=('<img src="'+markup.h(p['imageUrl'])+'" alt="'+markup.h(p['name'])+'" loading="lazy">'
               if _has_proof(p,'image',site_id) else '')
        price=('<p class="product-price">'+format(p['referencePrice'],',')+'원</p>'
               if _has_proof(p,'price') else '')
        note=('<p class="product-note">상품번호 '+markup.h(sku)+
              ' · 기준가 확인 2026-11-07 · 꽃의 상세 구성·규격은 판매처 상품정보에서 볼 수 있습니다.</p>'
              if site_id=='county-funeral-ownerprivate-test' else '')
        rows.append('<article class="product" data-product-sku="'+markup.h(sku)+'">'+image+
                    '<div class="product-copy"><h3>'+markup.h(p['name'])+'</h3>'+price+note+'</div>'+
                    '<a data-track-event="shop" class="button btn-outline" target="_blank" '
                    'rel="noopener noreferrer" href="'+markup.h(p['orderUrl'])+'">상품 보러가기 ↗</a></article>')
    return ''.join(rows)


def schema(site, page, products, region_index=None):
    if not site.get('domain') or not (site.get('publishEnabled') or site.get('publicIndexingApproved')):
        return ''
    url=site['domain'].rstrip('/')+markup.url_path(page['number'])
    catalog={p['sku']:p for p in products}
    items=[]
    for i,sku in enumerate(page['productSkus'],1):
        product=catalog[sku]
        entity={'@type':'Product','name':product['name'],'url':product['orderUrl']}
        if _has_proof(product,'image',site.get('id')):entity['image']=product['imageUrl']
        if _has_proof(product,'price'):
            entity['offers']={'@type':'Offer','price':str(product['referencePrice']),
                              'priceCurrency':'KRW','url':product['orderUrl']}
        items.append({'@type':'ListItem','position':i,'item':entity})
    graph=[{'@type':'WebPage','@id':url+'#webpage','url':url,'name':page['title'],
            'description':page['intro']},
           {'@type':'ItemList','@id':url+'#products','numberOfItems':len(items),'itemListElement':items}]
    if page.get('faq'):
        graph.append({'@type':'FAQPage','@id':url+'#faq','mainEntity':[
            {'@type':'Question','name':f['q'],'acceptedAnswer':{'@type':'Answer','text':f['a']}}
            for f in page['faq']]})
    ancestry=regional_ancestors(page,region_index) if region_index else []
    if ancestry:
        chain=ancestry+[page]
        graph.append({'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[
            {'@type':'ListItem','position':i,'name':node['region'],
             'item':site['domain'].rstrip('/')+markup.url_path(node['number'])}
            for i,node in enumerate(chain,1)]})
    raw=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False,separators=(',',':'))
    return '<script type="application/ld+json">'+raw.replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')+'</script>'


def service_schema(site, page):
    if not site.get('domain') or not (site.get('publishEnabled') or site.get('publicIndexingApproved')):
        return ''
    url=site['domain'].rstrip('/')+markup.url_path(page['number'])
    raw=json.dumps({'@context':'https://schema.org','@type':'WebPage','url':url,
                    'name':page['title'],'description':page['intro']},ensure_ascii=False)
    return '<script type="application/ld+json">'+raw.replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')+'</script>'


def regional_index(pages):
    by_id={p['id']:p for p in pages}
    children={}
    for page in pages:
        parent=page.get('parentPageId')
        if parent:
            if parent not in by_id or parent==page['id']:
                raise ConfigError(f'invalid parentPageId for {page["id"]}')
            children.setdefault(parent,[]).append(page)
    # Reject cycles without inferring geography for unmatched region rows.
    finished=set()
    for page in pages:
        seen=set(); node=page
        while node and node['id'] not in finished:
            if node['id'] in seen:raise ConfigError('cyclic region hierarchy')
            seen.add(node['id']); node=by_id.get(node.get('parentPageId'))
        finished.update(seen)
    return by_id,children


def regional_ancestors(page,index):
    """Return the exact explicitly linked parent chain from root to parent."""
    by_id=index[0]
    chain=[]
    seen={page['id']}
    node=page
    while node.get('parentPageId'):
        parent=by_id.get(node['parentPageId'])
        if parent is None or parent['id'] in seen:
            raise ConfigError('invalid or cyclic regional ancestry')
        chain.append(parent)
        seen.add(parent['id'])
        node=parent
    return list(reversed(chain))


def regional_navigation(page,pages,index=None):
    # Parent relationships must be supplied explicitly, never inferred from names.
    by_id,children_by_parent=index if index is not None else regional_index(pages)
    parent=by_id.get(page.get('parentPageId'))
    children=children_by_parent.get(page['id'],[])
    links=regional_ancestors(page,(by_id,children_by_parent))+children
    if not links:return ''
    return '<nav aria-label="관련 지역"><h2>관련 지역</h2>'+''.join(
        '<a href="'+markup.h(markup.url_path(p['number']))+'">'+markup.h(p['region'])+'</a>' for p in links)+'</nav>'


def render(site,page,pages,products,links,pools,region_index=None):
    page=assemble(page,pools,products)
    region_index=region_index if region_index is not None else regional_index(pages)
    path=markup.url_path(page['number'])
    share=(site.get('domain') or '').rstrip('/')+'/assets/images/'+site['imagePool'][0]
    head=markup.head(site,page['title'],page['intro'],path,share)
    style=('<style>.recommendations{margin:24px 0}.product-list{display:grid;gap:14px}'
           '.product img{width:128px;height:128px;object-fit:cover;border-radius:10px;flex:none}'
           '.product-price{font-weight:700}.document-page>header{padding:25px 0}'
           '@media(max-width:520px){.product{flex-wrap:wrap}.product img{width:96px;height:96px}'
           '.product .button{white-space:normal}}</style>')
    if site.get('id')=='county-funeral-ownerprivate-test':
        style=style.replace('</style>',(
          '.document-page nav[aria-label="관련 지역"]{display:flex;flex-wrap:wrap;gap:9px 12px;align-items:center}'
          '.document-page nav[aria-label="관련 지역"] h2{width:100%;margin-bottom:0}'
          '.document-page nav[aria-label="관련 지역"] a{display:inline-flex;padding:8px 12px;'
          'border:1px solid #d9e2d6;border-radius:8px;line-height:1.35;text-decoration:none}'
          '.document-page nav[aria-label="현재 위치"] a{display:inline-block;margin-right:7px}'
          '.product-note{font-size:.88rem;line-height:1.5;color:#425547;margin-top:8px}'
          '@media(max-width:520px){.product .button{width:100%;text-align:center;min-height:44px}}'
          '</style>'))
    og=('<meta property="og:type" content="website"><meta property="og:url" content="'+
        markup.h(site['domain'].rstrip('/')+path)+'">' if site.get('domain') and
        (site.get('publishEnabled') or site.get('publicIndexingApproved')) else '')
    head=head.replace('</head>',style+og+schema(site,page,products,region_index)+'</head>')
    ancestors=regional_ancestors(page,region_index)
    breadcrumb=('<nav aria-label="현재 위치">'+''.join(
                '<a href="'+markup.h(markup.url_path(node['number']))+'">'+markup.h(node['region'])+'</a> <span>›</span> '
                for node in ancestors)+'<span>'+markup.h(page['region'])+'</span></nav>' if ancestors else '')
    return (head+markup.header(site)+'<main id="main" class="container document-page">'
            +breadcrumb+'<header><h1>'+markup.h(page['title'])+'</h1><p>'+markup.h(page['intro'])+'</p></header>'
            '<section class="recommendations"><h2>상품과 가격</h2><div class="product-list">'+
            products_html(products,page['productSkus'],site.get('id'))+'</div></section>'+markup.article_body(page)+
            '<section class="faq"><h2>자주 묻는 질문</h2>'+markup.faq_markup(page)+'</section>'+
            regional_navigation(page,pages,region_index)+markup.phone_buttons(site)+markup.render_pagination(pages,page['number'])+
            '</main>'+(
                markup.footer(site,links,page).replace(
                    '축하와 응원의 마음을 전하는 안내 서비스',
                    '조의를 전하는 근조화환 상품·주문 안내')
                if site.get('id')=='county-funeral-ownerprivate-test'
                else markup.footer(site,links,page)))


def render_service(site,page,pages,services,rates,pools,region_index=None):
    from . import service_markup
    page=assemble(page,pools,services,service=True)
    path=markup.url_path(page['number'])
    head=service_markup._head(site,page['title'],page['intro'],path)
    if '<link rel="canonical"' in head:
        head=head.replace('</head>',service_schema(site,page)+'</head>',1)
    names={s['id']:s['name'] for s in services}
    chosen=set(page['serviceIds'])
    rows=''.join('<tr><th scope="row">'+markup.h(names[r['serviceId']])+'</th>'+
                 ''.join('<td>'+format(r[k],',')+'원</td>' for k in ('hour','halfDay','fullDay'))+'</tr>'
                 for r in rates['plans'] if r['serviceId'] in chosen)
    return (head+service_markup._header(site)+'<main id="main" class="wrap document">'
            '<header class="document-header"><div><h1>'+markup.h(page['title'])+'</h1><p>'+markup.h(page['intro'])+'</p>'+
            service_markup._phone(site)+'</div></header>'
            '<section class="block-section rate-section"><h2>서비스와 요금</h2><div class="table-scroll">'
            '<table class="rate-table"><caption>기본 이용요금</caption><thead><tr><th scope="col">서비스</th>'
            '<th scope="col">1시간</th><th scope="col">4시간</th><th scope="col">8시간</th></tr></thead><tbody>'+
            rows+'</tbody></table></div><p>부가세 별도</p></section>'+service_markup._sections(page)+
            service_markup._faq(page['faq'])+regional_navigation(page,pages,region_index)+
            service_markup._call_section(site)+markup.render_pagination(pages,page['number'])+'</main>'+
            service_markup._footer(site))
