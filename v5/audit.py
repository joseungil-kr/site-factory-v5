"""Strict local preflight: asset links, SEO metadata, safe preview and text differences."""
from __future__ import annotations
from collections import Counter
from math import ceil
import hashlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, quote
import json
import re
from .config import read_site
from .engine import target_dir, report_dir, sha
from . import markup


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs=[];self.alts=[];self.links=[];self.meta=[];self.titles=0;self.h1s=0
        self.in_article=False;self.articles=[];self.current=[]
        self.in_jsonld=False;self.jsonld=[];self._schema=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):
            self.refs.append(a['href'])
            self.links.append(a)
        if tag in ('img','script','link'):
            target=a.get('src') or a.get('href')
            if target:self.refs.append(target)
        if tag=='img':self.alts.append(a.get('alt'))
        if tag=='title':self.titles+=1
        if tag=='h1':self.h1s+=1
        if tag=='meta':self.meta.append(a)
        if tag=='script' and a.get('type')=='application/ld+json':
            self.in_jsonld=True;self._schema=''
        if tag=='article' and 'article-content' in a.get('class',''):
            self.in_article=True
    def handle_endtag(self,tag):
        if tag=='script' and self.in_jsonld:
            self.in_jsonld=False;self.jsonld.append(self._schema)
        if tag=='article' and self.in_article:self.in_article=False
    def handle_data(self,text):
        if self.in_jsonld:self._schema+=text
        if self.in_article:self.articles.append(text)


def grams(s,n=5):
    value=re.sub(r'\s+','',s).lower()
    return set(value[i:i+n] for i in range(max(0,len(value)-n+1)))


def similarity(left,right,metric='char-5gram-jaccard'):
    if metric=='char-5gram-jaccard':
        a,b=grams(left,5),grams(right,5)
        return len(a&b)/len(a|b) if a|b else 1.0
    if metric=='char-3gram-cosine':
        from math import sqrt
        normalized=lambda text:re.sub(r'\s+','',text).lower()
        def count(text):
            v=normalized(text)
            return Counter(v[i:i+3] for i in range(max(0,len(v)-2)))
        a,b=count(left),count(right)
        top=sum(v*b.get(k,0) for k,v in a.items())
        base=sqrt(sum(v*v for v in a.values())*sum(v*v for v in b.values()))
        return top/base if base else (1.0 if not a and not b else 0.0)
    raise ValueError('Unsupported similarity metric: '+str(metric))


def similarity_violation(score:float,threshold_exclusive:float)->bool:
    """The configured maximum is exclusive; equality fails."""
    if not 0 < threshold_exclusive < 1:
        raise ValueError('Invalid similarity threshold')
    return score >= threshold_exclusive

def resolved_reference(ref):
    if not ref or ref.startswith(('#','mailto:','tel:','data:')):
        return None
    parts=urlsplit(ref)
    if parts.scheme or parts.netloc:
        return None
    if not parts.path.startswith('/'):
        return None
    file_path=unquote(parts.path).lstrip('/')
    return file_path or 'index.html'


def audit(site_id, *,output:Path|None=None,write_report=True):
    data=read_site(site_id);site=data['site']
    from .config import ROOT
    plan_path=ROOT/'sites'/site_id/'site-spec.json'
    plan=json.loads(plan_path.read_text(encoding='utf-8')) if plan_path.is_file() else {}
    purpose_mode=plan.get('version')==2
    if purpose_mode:
        from .purpose_render import assemble, regional_index
        service=site.get('businessModel')=='service-lead'
        data={**data,'pages':[assemble(p,plan['purposePools'],data['services'] if service else data['products'],service=service) for p in data['pages']]}
        region_index=regional_index(data['pages'])
    out=(output or target_dir(site_id)).resolve()
    errors=[];warnings=[]
    if not out.exists():
        return {'site':site_id,'errors':['Build directory absent'],'warnings':[]}
    html_pages=sorted(out.glob('*.html'))
    expected={markup.filename(p['number']) for p in data['pages']}|{s['path'] for s in data['special'] if s.get('enabled',True)}|{'404.html'}
    if site.get('siteSearch',{}).get('enabled',False):expected.add('search.html')
    actual={p.name for p in html_pages}
    if actual!=expected:errors.append(f'Unexpected/missing HTML: {sorted(expected-actual)}, extra={sorted(actual-expected)}')
    extracted={}
    for file in html_pages:
        scan=Scan();content=file.read_text(encoding='utf-8');scan.feed(content)
        for raw in scan.jsonld:
            try:json.loads(raw)
            except (ValueError,TypeError):errors.append(f'Invalid JSON-LD: {file.name}')
        if scan.titles!=1 or scan.h1s!=1:errors.append(f'Invalid document outline: {file.name}')
        if any(alt is None for alt in scan.alts):errors.append(f'Image missing alt: {file.name}')
        meta={r.get('name'):r.get('content') for r in scan.meta}
        if file.name in ('404.html','search.html'):
            if meta.get('robots')!='noindex,nofollow':errors.append('404 page must be noindex')
        elif not site['domain'] and meta.get('robots')!='noindex,nofollow':
            errors.append(f'Domainless page missing noindex: {file.name}')
        if not site['domain'] and 'rel="canonical"' in content:
            errors.append(f'Unverified canonical in preview: {file.name}')
        if content.count('href="tel:')<1:errors.append(f'Phone link missing: {file.name}')
        for link in scan.links:
            href=link.get('href','')
            if href.startswith('https://') and 'fwith.co.kr' in href:
                if link.get('target')!='_blank' or 'noopener' not in link.get('rel',''):
                    errors.append(f'Unsafe webshop target: {file.name}')
        for ref in scan.refs:
            target=resolved_reference(ref)
            if target and not (out/target).is_file():
                errors.append(f'Dangling local reference: {file.name} -> {ref}')
        extracted[file.name]=scan
    for p in data['pages']:
        file=markup.filename(p['number'])
        html=(out/file).read_text(encoding='utf-8')
        if purpose_mode and site.get('businessModel')!='service-lead':
            from .purpose_render import assemble, schema
            assembled=assemble(p,plan['purposePools'],data['products'])
            expected_schema=schema(site,assembled,data['products'],region_index)
            # Only indexable builds have canonical/JSON-LD. Compare complete JSON
            # emitted by the same validated inputs, not merely script existence.
            if '<link rel="canonical"' in html:
                index_site={**site,'publishEnabled':True}
                expected_schema=schema(index_site,assembled,data['products'],region_index)
                if expected_schema not in html:errors.append('V5.1 JSON-LD mismatch: '+file)
            for sku in assembled['productSkus']:
                if f'data-product-sku="{markup.h(sku)}"' not in html:
                    errors.append('V5.1 product card missing: '+file+' '+sku)
        elif purpose_mode and '<link rel="canonical"' in html:
            from .purpose_render import service_schema
            expected_schema=service_schema({**site,'publicIndexingApproved':True},p)
            if expected_schema not in html:errors.append('V5.1 service JSON-LD mismatch: '+file)
        numbers=markup.pagination(data['pages'],p['number'])
        for n in numbers:
            if n==p['number']:
                if not re.search(rf'aria-current="page"[^>]*>{n}</span>',html):
                    errors.append(f'Current number not marked: {file}')
            elif f'href="{markup.url_path(n)}"' not in html:
                errors.append(f'Missing pagination link {file} => {n}')
        if p['number'] not in numbers:errors.append(f'Current page omitted in pagination: {file}')
        if len(numbers)>7:errors.append(f'Pagination longer than 7: {file}')
        if p.get('searchKeyword',site['keyword']) not in p['title']:warnings.append(f'Unexpected keyword in title: {file}')
        if len(p['intro'])+sum(len(s['paragraph']) for s in p['sections'])<250:
            warnings.append(f'Thin sample content: {file}')
    # Whole-population identical-body guard; for V5.1 compare using the
    # exact metric/threshold/fraction specified by the approved plan.
    full_pages=data['pages']
    all_bodies={p['id']:' '.join([p['intro']]+[x['paragraph'] for x in p['sections']]) for p in full_pages}
    counts=Counter(hashlib.sha256(v.encode('utf-8')).hexdigest() for v in all_bodies.values())
    if max(counts.values(),default=0)>1:
        errors.append('Exact repeated regional article body detected')
    similarity_config=(plan.get('similarityAudit') or {}) if purpose_mode else {}
    sim_metric=similarity_config.get('metric','char-5gram-jaccard')
    sim_limit=similarity_config.get('thresholdExclusive',0.49)
    fraction=similarity_config.get('sampleFraction',0.01)
    if sim_metric not in ('char-5gram-jaccard','char-3gram-cosine') or not (0<sim_limit<1) or not (0<fraction<=1):
        errors.append('Invalid similarity policy')
        sim_metric,sim_limit,fraction='char-5gram-jaccard',0.49,0.01
    similarity_mode='complete'
    if len(full_pages)>300:
        by_topic={}
        for p in full_pages:
            by_topic.setdefault(p.get('searchKeyword',site['keyword']),[]).append(p)
        selected=[]
        for topic,rows in sorted(by_topic.items()):
            n=max(1,ceil(len(rows)*fraction))
            selected.extend(sorted(rows,key=lambda x:hashlib.sha256(('v51-similarity:'+x['id']).encode()).digest())[:n])
        selected=sorted(selected,key=lambda x:x['number'])
        similarity_mode='fixed-stratified-'+str(fraction)
        warnings.append('Similarity sample is stratified; independent full content review required')
    else:
        selected=full_pages
    content_pairs=[]
    for i,p in enumerate(selected):
        a=all_bodies[p['id']]
        for q in selected[i+1:]:
            content_pairs.append((similarity(a,all_bodies[q['id']],sim_metric),p['number'],q['number']))
    max_sim=max(content_pairs,default=(0,0,0))
    if similarity_violation(max_sim[0],sim_limit):
        errors.append(f'Body similarity over {sim_limit:.1%} ({sim_metric}): {max_sim}')

    robots_text=(out/'robots.txt').read_text(encoding='utf-8')
    indexable='Allow: /' in robots_text
    if not indexable:
        if (out/'sitemap.xml').exists():errors.append('Preview must not have production sitemap')
        if robots_text!='User-agent: *\nDisallow: /\n':
            errors.append('Robots preview must disallow indexing')
        for f,scan in extracted.items():
            if next((m.get('content') for m in scan.meta if m.get('name')=='robots'),None)!='noindex,nofollow':
                errors.append('Preview page missing noindex: '+f)
    else:
        if not site['domain']:errors.append('Indexed build requires configured public domain')
        elif f'Sitemap: {site["domain"]}/sitemap.xml' not in robots_text:
            errors.append('Indexed robots.txt must reference verified domain sitemap')
        if not (out/'sitemap.xml').exists():errors.append('Indexed build missing sitemap')
        for f,scan in extracted.items():
            actual_robots=next((m.get('content') for m in scan.meta if m.get('name')=='robots'),None)
            if f in ('404.html','search.html'):
                if actual_robots!='noindex,nofollow':errors.append('Error/search page must remain noindex: '+f)
            elif actual_robots!='index,follow':errors.append('Indexed HTML missing index,follow: '+f)
            if f not in ('404.html','search.html') and site['domain']:
                uri='/' if f=='index.html' else '/'+quote(f)
                if f'<link rel="canonical" href="{site["domain"]}{uri}">' not in (out/f).read_text(encoding='utf-8'):
                    errors.append('Indexed page canonical mismatch: '+f)
        if site.get('naverSiteVerification'):
            text=(out/'index.html').read_text(encoding='utf-8')
            if text.count(f'<meta name="naver-site-verification" content="{site["naverSiteVerification"]}">')!=1:
                errors.append('Homepage Naver verification missing or duplicated')
        warnings.append('Indexing permitted by user; indexed pages still require independent inventory, delivery and content quality review')
    if any(not p.get('verifiedLive') for p in data['products']):
        warnings.append('Product price/stock and order destinations are referenced V4 data, not independently rechecked live')
    if any(p.suffix=='.svg' for p in out.rglob('*')):
        if site.get('businessModel') == 'service-lead':
            warnings.append('Service SVG illustrations are conceptual placeholders, not verified real worksite photographs')
        else:
            warnings.append('Illustrative shared SVG art is placeholder; replace with approved actual product images before production')
    files=[f for f in out.rglob('*') if f.is_file()]
    if len(files)>site.get('staticAssetSoftLimit',18000):errors.append('Static assets exceed safety budget')
    result={'site':site_id,'checkedHtmlFiles':len(html_pages),'checkedAssetFiles':len(files),
            'verifiedInternalReferences':sum(len(x.refs) for x in extracted.values()),
            'similarityMode':similarity_mode,'similaritySampleSize':len(selected),'similarityPopulation':len(full_pages),
            'similarityPairs':len(content_pairs),'maxBodyChar5gramJaccard':round(max_sim[0],5),
            'maxSimilarPair':[max_sim[1],max_sim[2]],'errors':errors,'warnings':warnings}
    if write_report:
        report=report_dir(site_id);report.mkdir(parents=True,exist_ok=True)
        (report/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
