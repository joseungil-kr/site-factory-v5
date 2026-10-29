"""Reproducible isolated Wallsky build from the preserved handoff and V5 source ledgers."""
import argparse,hashlib,json,random,shutil,sys
from html import escape as h
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from v5.site_plan import require_site_plan
from v5.skycar_pool import _grams,_jaccard
BASE=ROOT/'sites/wallsky';OUT=ROOT/'dist/wallsky';REPORT=ROOT/'reports/wallsky'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def load_sources():
    ledger=read(ROOT/'data/regions/seoul_gyeonggi_current_dong.json')
    pin=read(BASE/'regions.json')
    if ledger.get('asOf')!='2026-10-12' or ledger.get('sourceSHA256')!=pin['sourceSHA256'] or len(ledger['rows'])!=1732 or len(set(map(tuple,ledger['rows'])))!=1732:
        raise ValueError('Pinned V5 region-name source changed; do not silently regenerate')
    source=read(BASE/'copy-pool.json')
    if source.get('site')!='wallsky' or set(source['intents'])!={'빌딩외벽','공장외벽','상가외벽'}:
        raise ValueError('Wallsky intent source mismatch')
    work=read(ROOT/'data/pools/daysky_work_pool.json')['topics']
    shared=read(ROOT/'data/pools/daysky_shared_pool.json')['shared']
    buckets={k:[] for k in ('scene','access','workflow','handoff')}
    for key in buckets:
        for topic in ('facade','facility','hvac'): buckets[key]+=work[topic][key]
    buckets['access']+=shared['access']+shared['ground']
    buckets['workflow']+=shared['timing']+shared['coordination']
    buckets['handoff']+=shared['photo']+shared['consult']
    excluded=tuple(source.get('claimPolicy',{}).get('excludedPoolPhrases',[]))
    for key in buckets:
        buckets[key]=list(dict.fromkeys(
            sentence.replace('참고가 됩니다','도움이 됩니다')
            for sentence in buckets[key]
            if not any(term in sentence for term in excluded)
            and not any(term in sentence for term in ('즉시','보장','전 지역 출동'))
        ))
        if len(buckets[key])<8: raise ValueError('Insufficient in-scope pool '+key)

    return ledger['rows'],source,buckets
def pages():
    rows,source,buckets=load_sources();result=[]
    for parent,dong in rows:
        region=parent+' '+dong
        for intent,leads in source['intents'].items():
            rng=random.Random(int(hashlib.sha256((region+'|'+intent).encode()).hexdigest(),16))
            sections=[]
            for key,title in [('scene','작업 범위와 접근 지점'),('access','차량 진입과 벽면 거리'),('workflow','시설 담당자와 일정 조율'),('handoff','전화 상담 전 준비할 내용')]:
                sections.append({'heading':title,'paragraph':' '.join(rng.sample(buckets[key],3))})
            number=len(result)+2
            if number>=404:number+=1
            result.append({'number':number,'region':region,'intent':intent,'title':f'{region} {intent} 스카이차 작업','intro':rng.choice(leads),'sections':sections})
    if len(result)!=5196 or result[-1]['number']!=5198:raise ValueError('Unexpected page inventory')
    return result
CSS='''*{box-sizing:border-box}body{margin:0;background:#f4f4ef;color:#172e32;font:17px/1.85 system-ui,sans-serif;word-break:keep-all;overflow-wrap:anywhere}a{color:inherit}header,main,footer{max-width:1160px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;gap:12px;align-items:center}.brand{font-size:25px;font-weight:850;text-decoration:none;word-break:keep-all;overflow-wrap:anywhere}.call{background:#e9fa80;color:#172e32;border:1px solid #172e32;padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:750;display:inline-block}.hero{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center;padding:38px 0 54px}.eyebrow{font-size:13px;letter-spacing:.18em;font-weight:800}h1{font-size:42px;line-height:1.35;letter-spacing:-.04em;margin:16px 0;word-break:keep-all;overflow-wrap:anywhere}h2{font-size:24px;line-height:1.4;word-break:keep-all;overflow-wrap:anywhere}p{margin:16px 0}.hero img{width:100%;height:420px;object-fit:cover;border-radius:14px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}.card{background:#fff;padding:30px;border:1px solid #d6dfda;border-radius:12px}.lead{font-size:19px}.guide{background:#173c3c;color:white;padding:32px;border-radius:12px;margin:28px 0}.links{display:flex;gap:12px;flex-wrap:wrap}.links a{padding:7px 12px;background:#fff;border:1px solid #c5d2cd;border-radius:5px;text-decoration:none;word-break:keep-all;overflow-wrap:anywhere}details{padding:16px 0;border-bottom:1px solid #c5d2cd}summary{cursor:pointer;font-weight:700;word-break:keep-all;overflow-wrap:anywhere}footer{font-size:14px;padding-bottom:100px}.mobile{display:none}@media(max-width:640px){header,main,footer{padding:18px}header .call{font-size:13px;padding:8px}h1{font-size:31px}.hero{grid-template-columns:1fr;gap:20px;padding:20px 0}.hero img{height:260px}.grid{grid-template-columns:1fr}.card{padding:23px}.mobile{display:block;position:fixed;bottom:12px;left:18px;right:18px;text-align:center;z-index:5;box-shadow:0 5px 20px #0002}body{padding-bottom:65px}}'''
def render(title,description,content,path,public=False,error=False):
    robots='index,follow' if public and not error else 'noindex,nofollow'
    naver = '<meta name="naver-site-verification" content="18ea052bde5a6c7edd2733bee7f30cfdeb03ce77">' if public and path == '/' else ''
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)} | 외벽스카이</title><meta name="description" content="{h(description)}"><meta name="robots" content="{robots}"><link rel="canonical" href="https://wallsky.nalmada.net{path}"><link rel="stylesheet" href="/style.css">{naver}</head><body><header><a class="brand" href="/">외벽스카이</a><a class="call" href="tel:01053221952">010-5322-1952</a></header><main>{content}</main><footer>외벽스카이 · 서울·경기 외벽 장비 작업 상담<br><a href="/">홈으로</a> · <a href="tel:01053221952">전화 상담</a></footer><a class="call mobile" href="tel:01053221952">외벽 작업 전화 상담 ↗</a></body></html>'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--public',action='store_true');args=ap.parse_args()
    require_site_plan('wallsky');spec=read(BASE/'site-spec.json');items=pages()
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    (OUT/'style.css').write_text(CSS,encoding='utf-8')
    shutil.copy2(ROOT/'assets/library/daysky/skycar-facade.webp',OUT/'facade.webp')
    groups={}
    by_number={item['number']:item for item in items}
    for p in items:
        path=f'/{p["number"]}.html'
        hero=f'<section class="hero"><div><div class="eyebrow">WALLSKY / EXTERIOR ACCESS</div><h1>{h(p["title"])}</h1><p class="lead">{h(p["intro"])}</p><a class="call" href="tel:01053221952">현장 조건 상담하기 ↗</a></div><img src="/facade.webp" alt="건물 외벽에 접근하는 스카이차 작업 모습" width="1200" height="1152"></section>'
        body='<div class="grid">'+''.join(f'<section class="card"><h2>{h(s["heading"])}</h2><p>{h(s["paragraph"])}</p></section>' for s in p['sections'])+'</div>'
        body+='<section class="guide"><h2>장비 이용과 시공 범위를 나누어 상담합니다</h2><p>외벽스카이는 외벽 점검과 시설물 접근에 필요한 스카이차 작업을 상담합니다. 방수·도장 등 전문 공정은 시공 담당자가 진행할 범위와 장비 이용 시간을 구분해 알려 주세요.</p><p>현장 주소 · 대상 높이 · 벽면 사진 · 희망 날짜를 준비해 전화해 주세요.</p><a class="call" href="tel:01053221952">010-5322-1952</a></section>'
        adjacent=[by_number[n] for n in range(max(2,p['number']-3),min(5199,p['number']+4))
                  if n not in (p['number'],404) and n in by_number]
        body+='<nav class="links" aria-label="주변 외벽 작업 문서">'+''.join(
            f'<a href="/{item["number"]}.html">{h(item["region"]+" "+item["intent"]+" 스카이차")}</a>'
            for item in adjacent)+'</nav>'
        (OUT/path[1:]).write_text(render(p['title'],p['title']+'. '+p['intro'],hero+body,path,args.public),encoding='utf-8')
        groups.setdefault(p['region'].rsplit(' ',1)[0],[]).append(p)
    home='<section class="hero"><div><div class="eyebrow">WALLSKY / SEOUL & GYEONGGI</div><h1>벽면 가까이,<br>현장에 맞게.</h1><p class="lead">빌딩·공장·상가 외벽의 점검과 시설물 작업.<br>접근 위치와 작업 시간을 함께 상담합니다.</p><a class="call" href="tel:01053221952">외벽 스카이차 상담 ↗</a></div><img src="/facade.webp" alt="스카이차 외벽 작업" width="1200" height="1152"></section><section class="guide"><h2>현장을 알려주시면 장비 이용을 상담합니다</h2><p>건물 주소, 벽면까지의 거리, 작업 높이와 날짜를 알려 주세요. 필요한 전문 시공팀의 공정과 장비 이용 범위를 나누어 살펴봅니다.</p></section><h2>서울·경기 지역별 외벽 작업</h2>'
    for parent,ps in groups.items():
        home+=f'<details><summary>{h(parent)}</summary><div class="links">'+''.join(f'<a href="/{p["number"]}.html">{h(p["region"].rsplit(" ",1)[1]+" "+p["intent"])}</a>' for p in ps)+'</div></details>'
    (OUT/'index.html').write_text(render('빌딩·공장·상가 외벽 스카이차 작업','서울·경기 외벽 작업 장비 전화 상담',home,'/',args.public),encoding='utf-8')
    (OUT/'404.html').write_text(render('페이지를 찾을 수 없습니다','다른 지역 문서를 확인해 주세요','<h1>페이지를 찾을 수 없습니다</h1><a href="/">홈으로</a>','/404.html',args.public,True),encoding='utf-8')
    urls=['/']+[f'/{p["number"]}.html' for p in items]
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://wallsky.nalmada.net'+u+'</loc></url>' for u in urls)+'</urlset>',encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: https://wallsky.nalmada.net/sitemap.xml\n' if args.public else 'Disallow: /\n'),encoding='utf-8')
    write(REPORT/'pages.json',items)
    write(REPORT/'manifest.json',{'count':len(urls),'expected':spec['targetPageCount'],'mode':'public' if args.public else 'preview','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()}})
    print('GENERATED',len(urls),'URLs; mode', 'public' if args.public else 'noindex')
if __name__=='__main__':main()
