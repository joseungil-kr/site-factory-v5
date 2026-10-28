"""Static checks and seeded 1% Wallsky-internal sample-vs-population similarity audit."""
import hashlib,json,math,random,re,sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from v5.skycar_pool import _grams,_jaccard
from scripts.build_wallsky import pages,read,write,OUT,REPORT,BASE
class HTML(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.images=[];self.canonical=[];self.robots=[];self.phone=0;self.h1=0;self.title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='a':
            self.links.append(a.get('href',''));self.phone+=a.get('href')=='tel:01053221952'
        if tag=='img':self.images.append(a)
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content'))
def main():
    items=pages();manifest=read(REPORT/'manifest.json');errors=[];edgecount=0
    expected=['index.html']+[str(p['number'])+'.html' for p in items]
    assert '404.html' not in expected and len(set(expected))==5197
    assert len(items)==5196 and items[-1]['number']==5198
    error=HTML();error.feed((OUT/'404.html').read_text(encoding='utf-8'))
    assert error.robots==['noindex,nofollow']
    urls=ET.parse(OUT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    assert len(urls)==len(expected)==5197
    assert {x.text for x in urls}=={'https://wallsky.nalmada.net'+('/' if n=='index.html' else '/'+n) for n in expected}
    for page in items:
        html=(OUT/(str(page['number'])+'.html')).read_text(encoding='utf-8')
        if page['title'] not in html or page['intro'] not in html:errors.append([page['number'],'lost regional content'])
    forbidden=('검수용','미검증','참고가','준비 중','보유 상품 사진','원장 기준','당일 도착','방수 전문 시공','도장 전문 시공','실제 시공 완료','전 지역 출동 보장',
               '옥외 안내판','안내판을 교체','방향표지','공공시설물','공공 시설물','조명탑')
    css=(OUT/'style.css').read_text(encoding='utf-8')
    if 'word-break:keep-all' not in css or 'overflow-wrap:anywhere' not in css:
        errors.append(['style.css','Korean heading word preservation'])
    for name in expected:
        text=(OUT/name).read_text(encoding='utf-8');parser=HTML();parser.feed(text)
        if name!='index.html':
            nav=re.search(r'<nav class="links" aria-label="주변 외벽 작업 문서">(.*?)</nav>',text,re.S)
            if not nav:
                errors.append([name,'missing descriptive neighboring links'])
            elif re.search(r'<a href="/\\d+\\.html">\\d+</a>',nav.group(1)):
                errors.append([name,'numeric-only neighboring link label'])
        path='/' if name=='index.html' else '/'+name
        if parser.canonical!=['https://wallsky.nalmada.net'+path]:errors.append([name,'canonical'])
        if parser.h1!=1 or not parser.phone:errors.append([name,'h1/phone'])
        if parser.robots!=['index,follow' if manifest['mode']=='public' else 'noindex,nofollow']:errors.append([name,'robots'])
        if any(x in text for x in forbidden):errors.append([name,'unsupported/placeholder copy'])
        for link in parser.links:
            if link.startswith('/'):
                edgecount+=1;target=OUT/('index.html' if link=='/' else link[1:].split('#')[0])
                if not target.is_file():errors.append([name,'link',link])
        for img in parser.images:
            if not (OUT/img.get('src','').lstrip('/')).is_file() or not img.get('alt'):errors.append([name,'image'])
    texts=[p['intro']+' '+' '.join(s['paragraph'] for s in p['sections']) for p in items]
    grams=[_grams(t) for t in texts]
    samples=random.Random(20261028).sample(range(len(items)),math.ceil(len(items)*.01))
    results=[]
    for i in samples:
        score,j=max((_jaccard(grams[i],g),j) for j,g in enumerate(grams) if j!=i)
        results.append({'page':items[i]['number'],'closest':items[j]['number'],'score':round(score,6)})
    exact=len(texts)-len(set(texts));worst=max(r['score'] for r in results)
    qa={'static':{'population':len(expected),'allChecked':True,'internalLinksChecked':edgecount,'errors':errors},
        'similarity':{'metric':'whitespace-free char-5gram Jaccard','scope':'intro + four prose paragraphs; excludes repeated navigation, titles and conversion footer',
          'population':len(items),'seed':20261028,'sampleSize':len(samples),'sampleFraction':len(samples)/len(items),
          'comparisons':len(samples)*(len(items)-1),'thresholdExclusive':.49,'worst':worst,'exactDuplicateBodies':exact,
          'passes':worst<.49 and exact==0,'samples':results,
          'limitation':'Seeded sample versus full Wallsky population, not all-pairs proof; cross-site audit is separate.'},
        'passes':not errors and worst<.49 and exact==0}
    write(REPORT/'qa.json',qa);write(REPORT/'qa-public.json',qa)
    print(json.dumps({'static':qa['static'],'similarity':{k:v for k,v in qa['similarity'].items() if k!='samples'},'passes':qa['passes']},ensure_ascii=False))
    sys.exit(0 if qa['passes'] else 1)
if __name__=='__main__':main()
