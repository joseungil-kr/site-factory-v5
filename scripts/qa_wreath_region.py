"""V5-2 wreath-region independent SEO/content QA, including exact 5gram Jaccard.
Only static files; no GitHub, Cloudflare or search-engine mutations.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from collections import Counter,defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/wreath-region'
REPORT=ROOT/'reports/wreath-region'
DOMAIN='https://wreath.nalmada.net'

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=[];self.title=[];self.meta={};self.canonical=[];self.links=[];self.images=[];self.current=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.current='h1'
        elif tag=='title':self.current='title'
        elif tag=='meta' and 'name' in a:self.meta[a['name']]=a.get('content')
        elif tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        elif tag=='a':self.links.append(a.get('href',''))
        elif tag=='img':self.images.append(a)
    def handle_endtag(self,tag):
        if self.current==tag:self.current=None
    def handle_data(self,txt):
        if self.current=='h1':self.h1.append(txt)
        elif self.current=='title':self.title.append(txt)

def grams(txt,n=5):
    x=re.sub(r'\s+','',txt).lower()
    return {x[i:i+n] for i in range(max(0,len(x)-n+1))}
def similarity_check(articles,sample_mode):
    # Exact 5gram Jaccard calculation with inverted posting index; equivalent
    # to direct intersection/union against EVERY other article for each sample.
    records=[x for x in articles if x['intent'] in ('same-day','flower-shop')]
    print('BUILDING_CHAR5GRAM_POSTINGS articles=',len(records),flush=True)
    fp=[grams(x['body']) for x in records]
    lengths=[len(x) for x in fp]
    postings=defaultdict(list)
    for i,terms in enumerate(fp):
        for gram in terms:postings[gram].append(i)
    hashes=Counter(hashlib.sha256(x['body'].encode('utf-8')).hexdigest() for x in records)
    duplicated=sum(n-1 for n in hashes.values() if n>1)
    candidates=defaultdict(list)
    for i,x in enumerate(records):
        province=x['region'].split(' ',1)[0]
        candidates[(province,x['intent'])].append(i)
    selected=[]
    for key,ids in sorted(candidates.items()):
        n=max(1,math.ceil(len(ids)*0.01)) if not sample_mode else len(ids)
        selected+=sorted(ids,key=lambda i:hashlib.sha256(('wreath-20261029|'+records[i]['url']).encode()).digest())[:n]
    assert len(set(selected))==len(selected)
    examples=[];violations=[];maximum=(0.,None,None)
    for cnt,i in enumerate(selected):
        collisions=defaultdict(int)
        for gram in fp[i]:
            for j in postings[gram]:
                if i!=j:collisions[j]+=1
        best=(0.,None)
        for j,intersection in collisions.items():
            score=intersection/(lengths[i]+lengths[j]-intersection)
            if score>best[0]:best=(score,j)
            if score>=0.49:violations.append([records[i]['url'],records[j]['url'],round(score,6)])
        if best[0]>maximum[0]:maximum=(best[0],i,best[1])
        examples.append({'url':records[i]['url'],'topSimilarity':round(best[0],6),
                         'closestUrl':records[best[1]]['url'] if best[1] is not None else None})
        if (cnt+1)%50==0:print('SIMILARITY_SAMPLE_PROGRESS',cnt+1,'/',len(selected),flush=True)
    return {'metric':'whitespace-stripped-lowercased-char5gram-Jaccard',
            'mode':'seeded-1pct-stratified-by-province-and-intent-vs-all-exact',
            'population':len(records),'sampleSize':len(selected),
            'comparisons':len(selected)*(len(records)-1),'exactDuplicateBodies':duplicated,
            'maximum':round(maximum[0],6),
            'worstPair':[records[maximum[1]]['url'],records[maximum[2]]['url']] if maximum[1] is not None else [],
            'thresholdExclusive':0.49,'violations':violations[:25],
            'violationCount':len(violations),'passes':not violations and duplicated==0,
            'samples':examples,'limitation':'Sample versus all population; not all-pairs. Product cards, navigation and H1 omitted from body metric.'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sample',action='store_true')
    args=p.parse_args()
    manifest=json.loads((REPORT/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['sample'] is args.sample
    public=manifest['mode']=='public-candidate'
    pages=manifest['pages']
    expected={('index.html' if path=='/' else path.lstrip('/')) for path in pages}|{'404.html'}
    actual={x.relative_to(OUT).as_posix() for x in OUT.rglob('*.html')}
    errors=[]
    if expected!=actual:errors.append(f'HTML files mismatch expected={len(expected)} got={len(actual)}')
    counts={'html':0,'internalLinks':0,'externalProductLinks':0,'images':0}
    title_set=set()
    for rel in sorted(actual):
        raw=(OUT/rel).read_text(encoding='utf-8')
        scan=Scan();scan.feed(raw)
        counts['html']+=1
        if len(scan.h1)!=1 or len(scan.title)!=1:errors.append('h1/title count '+rel)
        if rel!='404.html':
            if ''.join(scan.title) in title_set:errors.append('duplicate title '+rel)
            title_set.add(''.join(scan.title))
        if not scan.meta.get('description'):errors.append('description absent '+rel)
        should_index=public and rel!='404.html'
        if scan.meta.get('robots')!=('index,follow' if should_index else 'noindex,nofollow'):
            errors.append('robots mismatch '+rel)
        canonical=DOMAIN+('/' if rel=='index.html' else '/'+rel)
        if scan.canonical!=([canonical] if should_index else []):errors.append('canonical mismatch '+rel)
        if any(x in raw for x in ('무조건 당일배송','전국 당일배송 보장','모든 지역 무료배송','100% 배송 보장','저희 지점','이미 배송 완료한','배송완료 사례')):errors.append('unverified claim '+rel)
        for link in scan.links:
            if link.startswith('tel:'):
                if link!='tel:18440644':errors.append('wrong tel: '+rel)
            elif link.startswith('https://fwith.co.kr/shop/item.php?it_id='):
                counts['externalProductLinks']+=1
                if re.search(r'(?i)(recipient|name|phone|address|ribbon|message)=',link):errors.append('PII in URL '+rel)
            elif link.startswith('#'):
                if 'id="'+link[1:]+'"' not in raw:errors.append('broken page anchor '+rel+' '+link)
                counts['internalLinks']+=1
            elif link.startswith('/'):
                target='index.html' if link.split('#')[0]=='/' else unquote(link.split('#')[0]).lstrip('/')
                if target and target not in actual and target!='assets/wreath.css':errors.append('broken local link '+rel+' -> '+link)
                counts['internalLinks']+=1
            else:
                errors.append('unknown href '+rel+' '+link[:50])
        for im in scan.images:
            counts['images']+=1
            if not im.get('alt') or not im.get('src','').startswith('https://fwith.co.kr/data/item/'):
                errors.append('untrusted image '+rel)
    if not (OUT/'assets/wreath.css').is_file():errors.append('css missing')
    robots=(OUT/'robots.txt').read_text()
    if public:
        if 'Disallow: /' in robots or 'Allow: /' not in robots:errors.append('public robots wrong')
        sitemap=OUT/'sitemap.xml'
        if not sitemap.is_file():errors.append('public sitemap missing')
        else:
            xmlns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
            urls=[el.text for el in ET.parse(sitemap).findall('.//'+xmlns+'loc')]
            if len(urls)!=len(pages) or len(set(urls))!=len(pages) or set(urls)!={DOMAIN+p for p in pages}:
                errors.append('sitemap inventory mismatch')
    else:
        if robots!='User-agent: *\nDisallow: /\n' or (OUT/'sitemap.xml').exists():
            errors.append('preview robots/sitemap protection failed')
    articles=json.loads((REPORT/'article-content.json').read_text(encoding='utf-8'))
    sim=similarity_check(articles,args.sample)
    if not sim['passes']:errors.append('similarity failures')
    if not args.sample and (manifest['regionRows'],manifest['articleCount'],manifest['pageCount'])!=(5034,10068,10336):
        errors.append('nationwide target inventory mismatch')
    if args.sample and manifest['regionRows']!=6:errors.append('representative scope mismatch')
    result={'site':'wreath-region','mode':manifest['mode'],'sample':args.sample,
            'pages':manifest['pageCount'],'regions':manifest['regionRows'],'counts':counts,
            'similarity':{k:v for k,v in sim.items() if k!='samples'},'errors':errors[:50],
            'errorsTotal':len(errors),'passes':not errors}
    (REPORT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (REPORT/'similarity.json').write_text(json.dumps(sim,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    if errors:raise SystemExit('WREATH_QA_FAILED: '+str(errors[:10]))
if __name__=='__main__':main()
