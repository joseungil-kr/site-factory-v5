"""Strict local preflight: asset links, SEO metadata, safe preview and text differences."""
from __future__ import annotations
from collections import Counter
from math import ceil
import hashlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
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
        if tag=='article' and 'article-content' in a.get('class',''):
            self.in_article=True
    def handle_endtag(self,tag):
        if tag=='article' and self.in_article:self.in_article=False
    def handle_data(self,text):
        if self.in_article:self.articles.append(text)


def grams(s,n=5):
    value=re.sub(r'\s+','',s).lower()
    return set(value[i:i+n] for i in range(max(0,len(value)-n+1)))


def similarity(left,right):
    a,b=grams(left),grams(right)
    return len(a&b)/len(a|b) if a|b else 1.0


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
    # Whole-population exact duplicate guard; pinned stratified 1% similarity
    # gate for large projects, explicitly NOT a complete semantic review.
    full_pages=data['pages']
    all_bodies={p['id']:' '.join([p['intro']]+[x['paragraph'] for x in p['sections']]) for p in full_pages}
    counts=Counter(hashlib.sha256(v.encode('utf-8')).hexdigest() for v in all_bodies.values())
    if max(counts.values(),default=0)>1:
        errors.append('Exact repeated regional article body detected')
    similarity_mode='complete'
    if len(full_pages)>300:
        by_topic={}
        for p in full_pages:
            by_topic.setdefault(p.get('searchKeyword',site['keyword']),[]).append(p)
        selected=[]
        for topic,rows in sorted(by_topic.items()):
            n=max(1,ceil(len(rows)*0.01))
            selected.extend(sorted(rows,key=lambda x:hashlib.sha256(('v5-dong-similarity-v1:'+x['id']).encode()).digest())[:n])
        selected=sorted(selected,key=lambda x:x['number'])
        similarity_mode='fixed-stratified-1pct'
        warnings.append('Similarity calculated on pinned 1% stratified sample, not complete pairs; independent semantic review required before indexable publication')
    else:
        selected=full_pages
    content_pairs=[]
    for i,p in enumerate(selected):
        a=all_bodies[p['id']]
        for q in selected[i+1:]:
            content_pairs.append((similarity(a,all_bodies[q['id']]),p['number'],q['number']))
    max_sim=max(content_pairs,default=(0,0,0))
    if max_sim[0]>=0.49:errors.append(f'Body similarity over 49%: {max_sim}')
    if site['domain'] is None:
        if (out/'sitemap.xml').exists():errors.append('Preview must not have production sitemap')
        if (out/'robots.txt').read_text(encoding='utf-8')!='User-agent: *\nDisallow: /\n':
            errors.append('Robots preview must disallow indexing')
    if any(not p.get('verifiedLive') for p in data['products']):
        warnings.append('Product price/stock and order destinations are referenced V4 data, not independently rechecked live')
    if any(p.suffix=='.svg' for p in out.rglob('*')):
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
