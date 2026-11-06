"""Skyquote isolated three-region site; real .webp binaries required before deployment."""
from pathlib import Path
from html import escape
import json,hashlib,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from skyquote_copy import hero,quote_sections,faq,contact,footer
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/skyquote'
OUT=ROOT/'dist/skyquote-preview'
IMG=['city-crane','facade-safety','sign-work','work-height','outrigger-access']
ALT=['도시 작업 환경에서 스카이차 배치를 보여주는 설명 그림','외벽 작업 높이와 작업대 위치를 보여주는 설명 그림','간판 작업 위치와 장비 도달 범위를 보여주는 설명 그림','작업 높이와 차량 정차 위치 사이 거리를 설명하는 그림','아웃트리거 설치 공간과 차량 정차 위치를 설명하는 그림']
ROWS=[('index.html','안산시','시 수준에서는 작업 주소와 장비 이동거리를 먼저 비교합니다.'),('danwon.html','안산시 단원구','구 수준에서는 높이와 차량 정차·진입 조건을 구체화합니다.'),('gojan.html','안산시 단원구 고잔동','동명만으로 현장 접근성이나 최저가가 결정되지 않습니다. 정확한 주소와 사진이 필요합니다.')]
CSS='''*{box-sizing:border-box}body{margin:0;background:#f7f8f6;color:#1b3028;font:16px/1.7 system-ui,sans-serif}header,footer{background:#103c31;color:#fff;padding:24px}header a,footer a{color:inherit}main{max-width:1100px;margin:auto;padding:24px}h1{font-size:clamp(28px,4vw,48px);line-height:1.3}h2{font-size:24px}section{padding:24px;border:1px solid #e1e8e3;border-radius:16px;margin:24px 0;background:#fff}.cta{display:inline-block;background:#096349;color:#fff;padding:14px 18px;border-radius:10px;text-decoration:none}.media{display:flex;gap:24px;align-items:center}.media div{flex:1;min-width:0}.media figure{flex:1;min-width:0;margin:0}.media img{width:100%;height:270px;object-fit:cover;border-radius:12px}.skyquote-illustration img{display:block}.table{overflow-x:auto;max-width:100%}table{min-width:620px;width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #ddd;padding:10px}@media(max-width:700px){.media{display:block}.media img{height:240px}section{padding:18px}main{padding:14px}}'''
def photo(i):
    loading='eager' if i==0 else 'lazy'
    priority=' fetchpriority="high"' if i==0 else ''
    return f'<figure class="skyquote-illustration"><img src="/assets/{IMG[i]}.webp" loading="{loading}"{priority} width="1536" height="1024" alt="{escape(ALT[i])}"></figure>'
def block(n,head,text):
    return f'<section class="media"><div><small>견적 안내 {n:02d}</small><h2>{head}</h2>{text}</div>{photo(n-1)}</section>'
def render(path,loc,note):
    title=f'{loc} 스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이'
    description=f'{loc} 스카이차 이용요금과 작업 높이·수평거리·시간·추가비용을 확인하고 현장에 맞는 견적을 상담하세요.'
    body=quote_sections(loc,note,IMG,ALT)
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
      f'<meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{escape(title)}</title><meta name="description" content="{escape(description)}">'
      f'<meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/assets/style.css"></head>'
      f'<body><header><strong>바른견적스카이</strong><span>현장에 맞는 장비와 요금 상담</span></header>'
      f'<main><h1>{escape(title)}</h1>{hero(loc)}'
      f'<a class="cta" href="tel:01053221952">전화 상담 010-5322-1952</a>'
      f'<p><a href="https://www.skycar1day.com/">영진스카이 운영 사이트</a></p>'
      f'{body}{contact()}{faq()}</main>{footer()}</body></html>')

def build():
    if OUT.exists():shutil.rmtree(OUT)
    (OUT/'assets').mkdir(parents=True)
    for name in IMG:
        path=SITE/'assets'/f'{name}.webp'
        if not path.is_file(): raise RuntimeError(f'Missing REAL AI image file (not placeholder): {path}')
        shutil.copy2(path,OUT/'assets'/path.name)
    (OUT/'assets/style.css').write_text(CSS,encoding='utf-8')
    manifest=[]
    for path,loc,note in ROWS:
        t=render(path,loc,note)
        assert t.count('<img ')==5
        (OUT/path).write_text(t,encoding='utf-8')
        manifest.append({'file':path,'title':loc+' 스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이','images':5})
    (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    (OUT/'404.html').write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><h1>페이지 없음</h1>',encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps({'status':'preview-only','pages':manifest,'imageHashes':{x:hashlib.sha256((OUT/'assets'/f'{x}.webp').read_bytes()).hexdigest() for x in IMG}},ensure_ascii=False,indent=2),encoding='utf-8')
    print('SKYQUOTE_THREE_PAGES_READY',len(manifest))
if __name__=='__main__':build()

