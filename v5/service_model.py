"""Phone-lead service site validator; fully isolated from webshop SKUs."""
from __future__ import annotations
import json
import re
from pathlib import Path


def read_service_site(site_id: str, site: dict, root: Path) -> dict:
    from .config import ConfigError, ROOT, read_json, unique_by, SITE_ID, check_https_url
    def fail(message): raise ConfigError('Service site: '+message)
    if site.get('id')!=site_id or site.get('businessModel')!='service-lead': fail('site identity mismatch')
    for field in ('brand','siteTitle','phone','region','keyword','serviceLabel'):
        if not isinstance(site.get(field),str) or not site[field].strip():fail('missing '+field)
    if not re.fullmatch(r'0\d{1,2}-\d{3,4}-\d{4}|1\d{3}-\d{4}',site['phone']):fail('invalid phone number')
    if site.get('theme') not in {'classic','modern','minimal'}:fail('invalid theme')
    if site.get('publishEnabled') is not False:
        fail('service product-checkout production mode is not supported')
    if site.get('homeIndexingApproved'):
        home_allowed=(site_id=='quicksky'
            and site.get('domain')=='https://quicksky.nalmada.net'
            and site.get('homeIndexingScope')=='quicksky-home-1-20261027'
            and site.get('publicIndexingApproved') is False
            and site.get('imageAssetsApproved') is True
            and site.get('domainOwnershipVerified') is True
            and site.get('homeBusinessFactsVerified') is True
            and site.get('homeContentQualityApproved') is True)
        if not home_allowed:fail('Home-only index approval lacks exact approved business/content evidence')
    if site.get('publicIndexingApproved') and site.get('homeIndexingApproved'):
        fail('Bulk index and home-only index approvals are mutually exclusive')
    if site.get('publicIndexingApproved'):
        daysky=(site_id=='daysky' and site.get('domain')=='https://daysky.nalmada.net'
                and site.get('publicIndexingScope') in ('daysky-ansan-29-20261025','daysky-seoul-gyeonggi-1736-20261025'))
        quicksky=(site_id=='quicksky' and site.get('domain')=='https://quicksky.nalmada.net'
                and site.get('publicIndexingScope')=='quicksky-seoul-gyeonggi-1733-20261027'
                and site.get('imageAssetsApproved') is True
                and site.get('contentQualityApproved') is True
                and site.get('domainOwnershipVerified') is True)
        if not (daysky or quicksky):
            fail('Indexable release requires exact approved hostname, content/image rights, and provider ownership')
    if any(site.get(field,{}).get('enabled') for field in ('analytics','siteSearch')):
        fail('analytics and search remain disabled on service sites')
    if site.get('indexNow',{}).get('enabled'):
        if not (site_id=='quicksky' and site.get('publicIndexingApproved')
                and re.fullmatch(r'[a-f0-9]{32,64}',str(site['indexNow'].get('key','')))):
            fail('IndexNow requires approved Quicksky public release and a valid hosted key')
    if site.get('domain'):
        p=check_https_url(site['domain'],'service domain')
        if p.path not in ('','/') or p.query:fail('domain must be bare HTTPS origin')
    if not isinstance(site.get('imagePool'),list) or not site['imagePool'] or len(set(site['imagePool']))!=len(site['imagePool']):
        fail('unique imagePool is required')
    library=site.get('imageLibrary',site_id)
    if not SITE_ID.fullmatch(library):fail('unsafe image library')
    for name in site['imagePool']:
        if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9-]+\.(?:svg|png|jpe?g|webp)',name):fail('unsafe image filename')
        if not (ROOT/'assets/library'/library/name).is_file():fail('missing shared image '+name)
    if not isinstance(site.get('staticAssetSoftLimit',18000),int) or not 10<=site.get('staticAssetSoftLimit',18000)<=20000:
        fail('invalid asset soft limit')
    pages=read_json(root/'pages.json');services=read_json(root/'services.json')
    rates=read_json(root/'rates.json');regions=read_json(root/'regions.json')
    links=read_json(root/'links.json');special=read_json(root/'special-pages.json')
    if not isinstance(pages,list) or not pages or len(pages)>19970:fail('unexpected pages')
    if not isinstance(services,list) or not services:fail('missing equipment')
    if not isinstance(rates,dict) or not isinstance(rates.get('plans'),list):fail('missing central rates')
    if rates.get('currency')!='KRW' or rates.get('vatIncluded') is not False:fail('only VAT-exclusive KRW prices supported')
    if not isinstance(regions,dict) or not isinstance(regions.get('regions'),list):fail('missing region ledger')
    if links or special:fail('service v1 has no webshop special pages or product links')
    if site_id=='quicksky':
        from .quicksky_pages import expand
        pages,regions=expand(pages,regions)
    if site_id=='daysky' and site.get('publicIndexingScope')=='daysky-seoul-gyeonggi-1736-20261025':
        from .skycar_pool import candidates
        original, generated, _ = candidates()
        if pages != original:fail('original 29 pages drifted from the generator baseline')
        pages = pages + generated
        regions['regions'] += [{'name':p['region'],'kind':'administrative-dong'} for p in generated]
    unique_by(pages,'number','page number');unique_by(pages,'id','page id')
    ordered=sorted(pages,key=lambda x:x['number'])
    if [p['number'] for p in ordered]!=list(range(1,len(ordered)+1)):
        fail('page numbers must be 1..N, never silent renumbering')
    valid_regions={x['name'] for x in regions['regions']}
    if len(valid_regions)!=len(regions['regions']):fail('duplicate region')
    unique_by(services,'id','equipment id');unique_by(rates['plans'],'serviceId','rate id')
    services_by_id={s['id']:s for s in services}
    plans={r['serviceId']:r for r in rates['plans']}
    consult_only=(site_id=='quicksky' and site.get('pricingPolicy')=='consult-only')
    if consult_only:
        if plans:fail('Quicksky consultation-only pricing must not contain numeric rates')
    elif set(services_by_id)!=set(plans):fail('rate plans and equipment mismatch')
    for s in services:
        if not re.fullmatch(r'[a-z0-9-]{2,40}',str(s['id'])) or not s.get('name') or not s.get('description'):
            fail('invalid equipment')
    for ident,plan in plans.items():
        for key in ('hour','halfDay','fullDay'):
            amount=plan.get(key)
            if type(amount) is not int or amount<1000 or amount>50000000:fail('invalid price '+ident+'/'+key)
        if not plan['hour']<=plan['halfDay']<=plan['fullDay']:fail('price order invalid '+ident)
    for p in pages:
        if not p.get('id') or not p.get('title') or not p.get('intro'):fail('incomplete page identity')
        if p.get('region') not in valid_regions:fail('unknown page region')
        if site['keyword'] not in p['title']:fail('keyword absent from title')
        if not isinstance(p.get('sections'),list) or len(p['sections'])<3:fail('too few sections')
        if not all(isinstance(s.get('paragraph'),str) and len(s['paragraph'])>=80 and s.get('heading') for s in p['sections']):
            fail('incomplete prose section')
        assigned=p.get('serviceIds')
        if not isinstance(assigned,list) or not assigned or any(x not in services_by_id for x in assigned):
            fail('invalid service references')
        if not isinstance(p.get('faq'),list) or not all(x.get('q') and x.get('a') for x in p['faq']):
            fail('incomplete FAQ')
    from .markup import filename
    allowed={'/'}|{'/'+filename(x['number']) for x in pages}
    if site_id=='daysky':
        allowed.update({'/#rates','/#works','/#regions'})
    for nav in site.get('navigation',[]):
        if nav.get('href') not in allowed or not nav.get('label'):fail('navigation refers to nonexistent page')
    if site_id=='daysky' and site.get('publicIndexingApproved'):
        target = 1736 if site.get('publicIndexingScope')=='daysky-seoul-gyeonggi-1736-20261025' else 29
        if len(ordered)!=target:
            fail('Daysky page count differs from its explicit indexing scope')
        if target==29 and site.get('indexNow',{}).get('enabled'):
            fail('Original 29-page scope disables IndexNow')
    if site_id=='quicksky' and site.get('publicIndexingApproved') and len(ordered)!=1733:
        fail('Quicksky indexable release requires exactly 1733 pages')
    if site_id in ('daysky','quicksky'):
        public=json.dumps({'site':site,'pages':pages,'services':services,'rates':rates},ensure_ascii=False)
        foreign=('영진','1844-0644','fwith') if site_id=='daysky' else ('당일스카이','영진','1844-0644','fwith')
        if any(x in public for x in foreign):fail('foreign customer branding detected')
    from .addons import validate as validate_addons
    validate_addons(site.get('addOns'), pages)
    return {'site':site,'pages':ordered,'products':[],'services':services,'rates':rates,
            'links':links,'special':special,'regions':regions,'root':root}
