"""Isolated Signsky build/audit. No provider writes or shared-site mutations."""
from pathlib import Path
import argparse, hashlib, html, json, math, random, re, shutil, sys
from collections import defaultdict
from xml.etree import ElementTree as ET
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from v5.site_plan import require_site_plan
BASE=ROOT/'sites/signsky'
OUT=ROOT/'dist/signsky'
ORIGIN='https://signsky.nalmada.net'
PHONE='010-5322-1952'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def grams(s):
    s=re.sub(r'\s+','',s).lower()
    return {s[i:i+5] for i in range(len(s)-4)}
def score(a,b): return len(a&b)/len(a|b) if a|b else 1
class VisibleBody(HTMLParser):
    def __init__(self): super().__init__(); self.active=False; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='body': self.active=True
    def handle_endtag(self,tag):
        if tag=='body': self.active=False
    def handle_data(self,text):
        if self.active:self.parts.append(text)
def records():
    ledger=read(ROOT/'data/regions/seoul_gyeonggi_current_dong.json')
    assert len(ledger['rows'])==1732 and ledger['sourceSHA256']=='057679a9a6312dbb4dd284d2ca42856d40a828239b2483540a7000b630fc30eb'
    groups=defaultdict(list)
    for parent,dong in ledger['rows']: groups[parent].append(dong)
    assert len(groups)==69
    pool=read(BASE/'copy-pool.json')
    pages=[]
    for parent,dongs in sorted(groups.items()):
        for key in ['signage','advertising']:
            topic=pool['topics'][key]
            label={'signage':'간판교체','advertising':'현수막설치'}[key]
            slug=hashlib.sha256(parent.encode()).hexdigest()[:10]
            rng=random.Random(parent+'|'+key+'|signsky-v1')
            parts=[]
            for heading,fields in [
                ('작업 범위를 먼저 정리하세요',[topic['scene'],topic['workflow'],topic['handoff']]),
                ('장비는 높이와 접근 방향을 함께 봅니다',[topic['access'],pool['shared']['equipment'],pool['shared']['ground']]),
                ('예약 시간을 정하는 순서',[pool['shared']['timing'],pool['shared']['coordination'],topic['workflow']]),
                ('현장 사진에 담아 둘 내용',[pool['shared']['photo'],topic['handoff'],pool['shared']['access']]),
                ('통화 전에 한 번 더 확인하세요',[pool['shared']['consult'],pool['shared']['safety'],pool['shared']['regionContext']])]:
                sentences=[]
                for field in fields:
                    available=[x for x in field if x not in [v for _,ss in parts for v in ss] and x not in sentences]
                    sentences.append(rng.choice(available))
                parts.append((heading,sentences))
            intro=rng.choice(topic['lead'])
            pages.append({'path':f'/{slug}-{key}.html','region':parent,'dongs':dongs,'intent':key,'label':label,
              'title':f'{parent} {label} 스카이차 예약 | 간판스카이','intro':intro,'sections':parts})
    assert len(pages)==138
    return pages

def description_for(p):
    """Unique region + purpose description; avoid only repeating the intro pool."""
    task = {
        'signage': '기존 간판 철거와 새 간판 설치 범위, 장비 접근 방향, 현장 사진과 시공 일정을 전화 상담 전에 확인하세요.',
        'advertising': '현수막 크기와 수량, 고정 지점, 장비 접근 방향과 설치·철거 일정을 전화 상담 전에 확인하세요.'
    }[p['intent']]
    return f"{p['region']} {p['label']} 스카이차 예약 안내. {p['intro']} {task}"


class HeadMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.description = None
        self.robots = None
        self.canonicals = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('name') == 'description':
            self.description = a.get('content', '')
        elif tag == 'meta' and a.get('name') == 'robots':
            self.robots = a.get('content', '')
        elif tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href', ''))


def shell(title,description,path,body,mode):
    index=mode=='public'
    canonical=f'<link rel="canonical" href="{ORIGIN}{path}">' if index else ''
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(description,quote=True)}"><meta name="robots" content="{'index,follow' if index else 'noindex,nofollow'}">{canonical}<link rel="stylesheet" href="/assets/signsky.css"></head><body><header><a class="brand" href="/">간판<span>스카이</span></a><nav><a href="/#regions">지역 찾기</a><a href="tel:{PHONE}">전화 상담 ↗</a></nav></header>{body}<footer><strong>간판스카이</strong><p>서울·경기 간판교체 · 현수막설치 스카이차 상담</p><a href="tel:{PHONE}">{PHONE}</a></footer><a class="mobile-call" href="tel:{PHONE}">작업 일정 전화 상담　{PHONE}</a></body></html>'''

def render(p,pages,mode):
    peer=next(x for x in pages if x['region']==p['region'] and x['intent']!=p['intent'])
    sections=''.join(f'<section><span class="number">0{i+1}</span><h2>{h}</h2><p>{" ".join(ss)}</p></section>' for i,(h,ss) in enumerate(p['sections']))
    task={'signage':('철거할 기존 간판','새 간판 설치 위치','시공팀 도착 시간'),'advertising':('현수막 수량과 크기','상단·하단 고정 위치','설치일과 철거일')}[p['intent']]
    checklist=''.join(f'<label><input type="checkbox">{x}</label>' for x in task)
    body=f'''<main><div class="breadcrumb"><a href="/">홈</a> / {p['region']} / {p['label']}</div><div class="hero detail"><div><p class="eyebrow">SIGN WORK / {p['label']}</p><h1>{p['region']}<br>{p['label']}<br><em>스카이차 예약</em></h1><p>{p['intro']}</p><a class="button" href="#call">상담 준비 항목 보기 ↓</a></div><figure><img src="/assets/skycar-truck.webp" alt="스카이차와 고소작업 장비" width="884" height="514"></figure></div><div class="article-grid"><article>{sections}</article><aside id="call"><p class="eyebrow">BEFORE YOU CALL</p><h2>통화할 때<br>이렇게 알려주세요</h2><p>{p['region']}의 작업 주소와 함께 다음 항목을 준비하면 상담이 구체적입니다.</p>{checklist}<p class="note">높이·진입 여건·작업 인원과 자재를 함께 전달해 주세요. 장비 이용 범위와 시공 담당자의 역할, 금액과 일정을 통화에서 정합니다.</p><a class="button" href="tel:{PHONE}">{PHONE} ↗</a></aside></div><section class="local"><h2>{p['region']} 작업 주소 확인</h2><p class="dong-list">{' · '.join(p['dongs'])}</p><p>도로명 주소와 건물 앞 진입 사진을 함께 준비해 주세요.</p><a class="text-link" href="{peer['path']}">{p['region']} {peer['label']} 안내 →</a></section></main>'''
    return shell(p['title'],description_for(p),p['path'],body,mode)

def build(mode):
    require_site_plan('signsky')
    pages=records()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'assets').mkdir(exist_ok=True)
    shutil.copyfile(BASE/'signsky.css',OUT/'assets/signsky.css')
    for name in ['skycar-hero.webp','skycar-truck.webp']:
        shutil.copyfile(ROOT/'assets/library/daysky'/name,OUT/'assets'/name)
    for p in pages: (OUT/p['path'].lstrip('/')).write_text(render(p,pages,mode),encoding='utf-8')
    cards=''.join(f'<div class="region-card"><h3>{p[0]["region"]}</h3>'+''.join(f'<a href="{x["path"]}">{x["label"]} →</a>' for x in p)+'</div>' for p in [pages[i:i+2] for i in range(0,len(pages),2)])
    home=f'''<main><div class="hero"><div><p class="eyebrow">SIGN WORK, PLANNED WELL.</p><h1>간판을 바꾸는 날,<br>현수막을 거는 날.<br><em>장비부터 맞추세요.</em></h1><p>서울·경기 간판교체와 현수막설치를 위한 스카이차 상담.<br>작업 위치, 접근 조건, 시공 일정을 한 번에 정리하세요.</p><a class="button" href="#regions">우리 지역 예약 안내 ↓</a></div><figure><img src="/assets/skycar-hero.webp" alt="건물 외부 작업에 사용하는 스카이차" width="1200" height="531"></figure></div><section class="intro"><p class="eyebrow">TWO JOBS. DIFFERENT CHECKLISTS.</p><h2>같은 높이여도,<br>준비할 내용은 다릅니다.</h2><div class="two"><div><h3>01 / 간판교체</h3><p>기존 간판 철거부터 새 프레임 설치까지. 전기 작업과 시공팀 일정, 간판 앞 접근 공간을 함께 정리합니다.</p></div><div><h3>02 / 현수막설치</h3><p>현수막 양 끝의 고정 위치와 작업 동선부터. 수량과 크기, 설치·철거 일정을 나누어 상담합니다.</p></div></div></section><section id="regions"><p class="eyebrow">SEOUL & GYEONGGI</p><h2>작업할 지역을 선택하세요</h2><p>시·구별 안내에서 작업 목적과 해당 동을 확인할 수 있습니다.</p><div class="regions">{cards}</div></section><section class="closing"><h2>주소와 현장 사진부터 준비하세요.</h2><p>1톤·3.5톤·5톤 장비 상담은 높이와 수평 거리, 차량 진입 여건을 함께 살펴 진행합니다.</p><a class="button" href="tel:{PHONE}">{PHONE} 전화 상담 ↗</a></section></main>'''
    (OUT/'index.html').write_text(shell('간판스카이 | 서울·경기 간판교체·현수막설치 스카이차 예약','지역과 작업 목적별로 장비 접근 조건, 작업 일정, 전화 상담 준비를 확인하세요.','/',home,mode),encoding='utf-8')
    (OUT/'404.html').write_text(shell('페이지를 찾을 수 없습니다 | 간판스카이','지역 안내에서 작업 지역을 찾아보세요.','/404.html','<main><h1>페이지를 찾을 수 없습니다.</h1><a href="/">지역 안내로 돌아가기</a></main>','preview'),encoding='utf-8')
    urls=['/']+[p['path'] for p in pages]
    robots='User-agent: *\n'+('Allow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n' if mode=='public' else 'Disallow: /\n')
    (OUT/'robots.txt').write_text(robots,encoding='utf-8')
    sitemap=OUT/'sitemap.xml'
    if mode=='public': sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+u+'</loc></url>' for u in urls)+'</urlset>',encoding='utf-8')
    elif sitemap.exists(): sitemap.unlink()
    write(ROOT/'reports/signsky/manifest.json',{'mode':mode,'pageCount':len(urls),'urls':urls,'regionCount':69,'dongCount':1732,'pages':pages})
    print(json.dumps({'generated':len(urls),'mode':mode}))

def audit():
    manifest=read(ROOT/'reports/signsky/manifest.json')
    pages=manifest['pages']; errors=[]; texts=[]
    descriptions=[]
    expected_robots = 'index,follow' if manifest['mode']=='public' else 'noindex,nofollow'
    assert len(manifest['urls']) == 139 and len(set(manifest['urls'])) == 139
    for path in manifest['urls']:
        raw=(OUT/('index.html' if path=='/' else path[1:])).read_text(encoding='utf-8')
        assert raw.count('<h1>')==1 and 'tel:'+PHONE in raw
        meta=HeadMetadata();meta.feed(raw)
        assert meta.robots==expected_robots,(path,meta.robots,expected_robots)
        assert meta.description and meta.description.strip(),(path,'missing description')
        descriptions.append(meta.description)
        if manifest['mode']=='public':
            assert meta.canonicals==[ORIGIN+path],(path,meta.canonicals)
        else:
            assert meta.canonicals==[],(path,meta.canonicals)
        for link in re.findall(r'(?:href|src)="([^"#]+)',raw):
            if link.startswith('/'):
                file=link.split('#')[0]
                assert (OUT/('index.html' if file=='/' else file[1:])).exists(),(path,link)
        for word in ['준비 중','검수용','미검증','참고가','원장 기준','보유 상품 사진','영진','당일스카이']:
            assert word not in raw,(path,word)
    page_descriptions=descriptions[1:]
    assert len(page_descriptions)==138 and len(set(page_descriptions))==138, 'Repeated regional descriptions'
    for p in pages:
        # Primary metric matches V5: intro + article paragraphs; additionally audit rendered main text below.
        texts.append(grams(p['intro']+' '+' '.join(' '.join(s) for _,s in p['sections'])))
    seed=20261028; sample=sorted(random.Random(seed).sample(range(len(pages)),math.ceil(len(pages)*.01)))
    pairs=[]
    for i in sample:
        best=max((score(texts[i],texts[j]),j) for j in range(len(pages)) if i!=j)
        pairs.append({'sample':pages[i]['path'],'nearest':pages[best[1]]['path'],'score':best[0]})
    fullmax=max((score(texts[i],texts[j]),i,j) for i in range(len(pages)) for j in range(i))
    result={'urlCount':139,'structuralAudit':'all 139 URLs','metric':'char-5gram-jaccard; whitespace removed, lowercase; intro+article paragraphs','thresholdExclusive':.49,'seed':seed,'population':138,'sampleCount':len(sample),'sampleComparisons':len(sample)*(len(pages)-1),'sample':pairs,'allPairsComparisons':len(pages)*(len(pages)-1)//2,'allPairsMax':fullmax[0],'allPairsNearest':[pages[fullmax[1]]['path'],pages[fullmax[2]]['path']],'passed':fullmax[0]<.49}
    visible=[]
    for p in pages:
        parser=VisibleBody();parser.feed((OUT/p['path'][1:]).read_text(encoding='utf-8'))
        visible.append(grams(' '.join(parser.parts)))
    visiblemax=max(score(visible[i],visible[j]) for i in range(len(pages)) for j in range(i))
    result['fullVisibleBodyAllPairsMax']=visiblemax
    result['fullVisibleBodyIncludes']='headers, footer, checklists, district/dong list, all article text'
    from v5.skycar_pool import candidates,body
    old,new,_=candidates(); daysky=[grams(body(x)) for x in old+new]
    result['crossDayskySampleComparisons']=len(sample)*len(daysky)
    result['crossDayskySampleMax']=max(score(texts[i],other) for i in sample for other in daysky)
    result['passed']=result['passed'] and visiblemax<.49 and result['crossDayskySampleMax']<.49
    robots=(OUT/'robots.txt').read_text(encoding='utf-8')
    if manifest['mode']=='public':
        assert robots=='User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n'
        sitemap=ET.parse(OUT/'sitemap.xml').getroot()
        assert sitemap.tag=='{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'
        ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        locs=[node.text for node in sitemap.findall(ns+'url/'+ns+'loc')]
        expected={ORIGIN+path for path in manifest['urls']}
        assert len(locs)==139 and len(set(locs))==139
        assert set(locs)==expected, 'Sitemap must exactly equal all 139 canonical URLs'
        assert all(x.startswith(ORIGIN+'/') or x==ORIGIN+'/' for x in locs)
    else:
        assert robots=='User-agent: *\nDisallow: /\n'
        assert not (OUT/'sitemap.xml').exists(), 'Preview must not publish a sitemap'
    error_page=(OUT/'404.html').read_text(encoding='utf-8')
    error_meta=HeadMetadata();error_meta.feed(error_page)
    assert error_meta.robots=='noindex,nofollow', '404 must remain noindex'
    write(ROOT/'reports/signsky/qa.json',result)
    print(json.dumps(result))
    assert result['passed'],'copy similarity threshold failed'

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['build','audit']);ap.add_argument('--mode',choices=['preview','public'],default='preview');a=ap.parse_args()
    build(a.mode) if a.command=='build' else audit()
