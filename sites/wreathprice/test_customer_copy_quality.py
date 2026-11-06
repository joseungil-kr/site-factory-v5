"""Read-only 50-page deterministic, scored customer copy review for WreathPrice.

Scores are transparent rule-based editorial QA proxies, not proof that repeated
regional templates are unique SEO content. Any score below 90 fails deployment.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import expand_lower

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist-all-localities'
BASE_URL='https://wreathprice.nalmada.net'
PROVINCES=16
SKUS=['B201','B203','B205','C205','C030']
PRICES=['59,000원','79,000원','109,000원','149,000원','200,000원']

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.meta={};self.links=[];self.img=[];self.title=[];self.sections=[];self.tags=[]
        self._t=None
    def handle_starttag(self,tag,attributes):
        d=dict(attributes)
        self.tags.append(tag)
        if tag=='meta' and d.get('name'):self.meta[d['name'].lower()]=d.get('content','')
        if tag=='a':self.links.append(d.get('href',''))
        if tag=='img':self.img.append(d)
        if tag in ('title','h1','h2'):self._t=tag
    def handle_endtag(self,tag):
        if tag==self._t:self._t=None
    def handle_data(self,text):
        if self._t=='title':self.title.append(text)
        if self._t=='h2':self.sections.append(text.strip())

def sample(report):
    rows=report['localities']
    by_prov=collections.defaultdict(list)
    for r in rows:by_prov[r['provinceCode']].append(r)
    assert len(by_prov)==16
    chosen=[]
    for province in sorted(by_prov):
        names=sorted(by_prov[province],key=lambda x:x['code'])
        chosen.extend([names[0], names[len(names)//2]])
    selected={x['code'] for x in chosen}
    for i in range(0,len(rows),max(1,len(rows)//200)):
        if len(chosen)>=38:break
        x=rows[i]
        if x['code'] not in selected:
            chosen.append(x);selected.add(x['code'])
    assert len(chosen)==38
    # Recheck iteration 2 keeps representative coverage and adds a new locality.
    fresh=next(x for x in rows if x['code'] not in selected and x['provinceCode']==chosen[-1]['provinceCode'])
    chosen[-1]=fresh
    upper=json.loads((ROOT/'verified-regions-nationwide.json').read_text())['entries']
    upper_new=sorted([x for x in upper if x['code'] not in {'4127000000','4127100000'}],key=lambda x:x['code'])
    region=[upper_new[i*(len(upper_new)-1)//7] for i in range(8)]
    paths=['/locality/'+x['code']+'.html' for x in chosen]
    paths+=['/region/'+x['code']+'.html' for x in region]
    paths+=['/ansan/','/ansan/sangnok/bono/','/regions/','/localities/']
    assert len(paths)==50 and len(set(paths))==50
    return paths

def score_page(path):
    real=OUT/path.lstrip('/')
    if path.endswith('/'):real=real/'index.html'
    raw=real.read_text(encoding='utf-8')
    d=Page();d.feed(raw)
    is_hub=path in ('/regions/','/localities/')
    reasons=[]
    forbidden=['AI 생성','AI 안내','AI 이미지','AI로 생성','AI가 생성','시안','지역별 배송 가능 사례: 0건','보장하지 않습니다']
    flags=[word for word in forbidden if word in raw]
    naturally_stated=(not flags and bool(''.join(d.title)) and raw.count('확인하세요')<=3)
    natural=25 if naturally_stated else 17
    reasons.append('고객용 제목·문장, 불필요한 제작 표현과 훈계 문장 '+('없음' if naturally_stated else '발견 '+str(flags)))
    has_prices=all(p in raw for p in PRICES)
    seller_links={re.search('it_id=([A-Z0-9]+)',href).group(1) for href in d.links
                  if re.search('https://fwith.co.kr/shop/item.php\\?it_id=([A-Z0-9]+)',href)}
    correct_meta=d.meta.get('robots')=='noindex,nofollow'
    correct_price_evidence=is_hub or (has_prices and set(SKUS).issubset(seller_links))
    provenance_or_caveat=any(x in raw for x in ['배송비','추가 비용','실제 배송 조건'])
    accuracy=30 if correct_meta and correct_price_evidence and provenance_or_caveat else 18
    reasons.append('표시 가격·실상품 SKU 링크·조건부 배송·noindex '+('검사 충족' if accuracy==30 else '누락'))
    useful=is_hub and sum(x.startswith('/') for x in d.links)>=15
    useful=useful or (not is_hub and
           '<section class="customer-choice">' in raw and len(d.img)==5 and len(seller_links)>=5 and
           any(x in raw for x in ['수령 시설','배송지','상품 상세']) and
           any(x in raw for x in ['리본','결제금액','추가비용']))
    utility=30 if useful else 16
    reasons.append('상품 선택·문의·지역탐색 '+('실행 가능' if useful else '정보 부족'))
    # Known repeated catalogue and FAQ: apply honest penalty, not fake localization.
    repetition=13 if is_hub else 10
    reasons.append('공통 가격표·질문 재사용 인정, 지역별 고유 데이터로 해석하지 않음')
    score=natural+accuracy+utility+repetition
    return {'url':BASE_URL+path,'path':path,'score':score,
       'natural':natural,'accuracy':accuracy,'utility':utility,
       'repetition':repetition,'reasons':reasons,'flaggedExpressions':flags,
       'products':sorted(seller_links),'images':len(d.img),'indexable':False}

def main(archive):
    build=expand_lower.main(archive)
    paths=sample(build)
    results=[score_page(path) for path in paths]
    failures=[x for x in results if x['score']<90]
    kinds=collections.Counter('locality' if p.startswith('/locality/') else
       'region' if p.startswith('/region/') else 'pilot' if p.startswith('/ansan/') else 'hub'
       for p in paths)
    report={'totalPages':4935,'sampleMinimum':math.ceil(4935*.01),
       'sampleCount':len(results),'sampleDistribution':dict(kinds),
       'minScore':min(x['score'] for x in results),'maxScore':max(x['score'] for x in results),
       'average':round(sum(x['score'] for x in results)/len(results),2),
       'failures':len(failures),'allPassed':len(failures)==0,
       'scoring':{'natural':25,'accuracy':30,'utility':30,'repetition':15},
       'caveat':'Rule-based text/links QA; regional uniqueness and real shipping availability NOT proven.',
       'pages':results,'reviewIteration':2,'previousFailure':{'path':'/localities/','score':86,'cause':'hub lacked explicit delivery-fee and purchase-condition context'}}
    target=ROOT/'CUSTOMER_COPY_50_SAMPLE_QA.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('WREATHPRICE_COPY_QA_50='+json.dumps({k:v for k,v in report.items() if k!='pages'},ensure_ascii=False),flush=True)
    for r in results:
        print('WREATHPRICE_SAMPLE_SCORE='+json.dumps({'url':r['url'],'score':r['score'],
             'natural':r['natural'],'accuracy':r['accuracy'],'utility':r['utility'],'repetition':r['repetition']},ensure_ascii=False))
    if failures:
        raise AssertionError('Any sample below 90 is a failed release: '+str([x['path'] for x in failures]))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,required=True)
    main(parser.parse_args().archive)
