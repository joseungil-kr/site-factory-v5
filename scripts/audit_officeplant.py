"""Exhaustive generated-file/link checks and fixed 1% versus full-corpus similarity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import hashlib
import json
import math
import random
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/officeplant-public'
REPORT=ROOT/'reports/officeplant'

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.body=False;self.skip=0;self.text=[];self.links=[];self.images=[];self.canonical=[];self.robots=[];self.h1=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='body':self.body=True
        if tag in ('script','style'):self.skip+=1
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='img':self.images.append(a)
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content'))
        if tag=='h1':self.h1+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip-=1
        if tag=='body':self.body=False
    def handle_data(self,text):
        if self.body and not self.skip:self.text.append(text)

def audit():
    manifest=json.loads((REPORT/'manifest-public.json').read_text(encoding='utf-8'))
    paths=[p['path'] for p in manifest['pages']]
    errors=[];texts=[];edge_count=0;images=set();titles=[];grams=[];vocab={}
    def gramset(text):
        result=set()
        for i in range(len(text)-4):
            gram=text[i:i+5]
            if gram not in vocab:vocab[gram]=len(vocab)
            result.add(vocab[gram])
        return result
    for path in paths:
        file=OUT/('index.html' if path=='/' else path.lstrip('/'))
        html=file.read_text(encoding='utf-8');p=Page(html)
        if p.h1!=1:errors.append([path,'h1'])
        if p.canonical!=['https://officeplant.nalmada.net'+path]:errors.append([path,'canonical'])
        if p.robots!=['index,follow']:errors.append([path,'robots'])
        if 'tel:18440644' not in p.links:errors.append([path,'phone'])
        if not any(x.startswith('https://fwith.co.kr') for x in p.links):errors.append([path,'order destination'])
        text=unicodedata.normalize('NFC',re.sub(r'\s+',' ',' '.join(p.text))).strip()
        for banned in ['검수용','미검증','공사 중','참고가','보유 상품 사진','원장 기준','당일배송 보장','모란시장 지점']:
            if banned in text:errors.append([path,'banned copy',banned])
        for href in p.links:
            u=urlsplit(href)
            if not u.scheme and href:
                target=unquote(u.path)
                f=OUT/('index.html' if target in ('','/') else target.lstrip('/'))
                if not f.is_file():errors.append([path,'broken link',href])
                edge_count+=1
        for img in p.images:
            images.add(img.get('src',''))
            if not img.get('alt') or not (OUT/img.get('src','').lstrip('/')).is_file():errors.append([path,'image',img])
        texts.append(text);grams.append(gramset(text));titles.append(re.search(r'<title>(.*?)</title>',html).group(1))
    if len(paths)!=3468 or len(set(paths))!=3468:errors.append(['population'])
    if len(set(titles))!=3468:errors.append(['duplicate title'])
    sitemap=[n.text for n in ET.parse(OUT/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    if set(sitemap)!={'https://officeplant.nalmada.net'+p for p in paths}:errors.append(['sitemap'])
    if 'Allow: /' not in (OUT/'robots.txt').read_text():errors.append(['public robots'])
    preview=ROOT/'dist/officeplant'
    if 'Disallow: /' not in (preview/'robots.txt').read_text() or (preview/'sitemap.xml').exists():errors.append(['preview robots'])
    for f in preview.rglob('*.html'):
        html=f.read_text(encoding='utf-8')
        if 'noindex,nofollow' not in html or 'rel="canonical"' in html:errors.append([str(f),'preview indexing'])
    sample=random.Random(20261028).sample(range(len(paths)),math.ceil(len(paths)*.01))
    nearest=[]
    for i in sample:
        best=(-1,None)
        for j,g in enumerate(grams):
            if i==j:continue
            intersection=len(grams[i]&g);score=intersection/(len(grams[i])+len(g)-intersection)
            if score>best[0]:best=(score,j)
        nearest.append({'path':paths[i],'nearest':paths[best[1]],'score':round(best[0],6),'pass':best[0]<.49})
    report={'generatedFiles':'PASS' if not errors else 'FAIL','errors':errors,'contentPages':len(paths),'htmlFilesIncluding404':len(list(OUT.rglob('*.html'))),'internalLinkChecks':edge_count,'images':sorted(images),'uniqueTitles':len(set(titles)),'sitemapURLs':len(sitemap),'exactDuplicateBodies':len(texts)-len(set(texts)),'similarity':{'metric':'char-5gram-jaccard','normalization':'NFC; collapse whitespace; complete body visible text including chrome, article, product and navigation; exclude head/script/style','seed':20261028,'sampleCount':len(sample),'population':len(paths),'comparisons':len(sample)*(len(paths)-1),'thresholdExclusive':.49,'maximum':max(x['score'] for x in nearest),'pass':all(x['pass'] for x in nearest),'nearest':nearest},'limitations':['Similarity is fixed 1% sample versus full population, NOT all-pairs.','Local file checks are NOT public HTTP checks.','No live order or payment submitted.']}
    (REPORT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('similarity','errors')},ensure_ascii=False))
    print(json.dumps({'errors':errors[:10],'similarityMax':report['similarity']['maximum'],'similarityPass':report['similarity']['pass']},ensure_ascii=False))
    return report

if __name__=='__main__':
    result=audit()
    raise SystemExit(0 if result['generatedFiles']=='PASS' and result['similarity']['pass'] else 1)