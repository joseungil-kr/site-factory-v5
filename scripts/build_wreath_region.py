"""V5-2 Wreath Region static generator. Independent of existing live sites.
Preview is always noindex; --public creates a release CANDIDATE, not a deployment.
"""
from __future__ import annotations
import argparse, hashlib, html, json, random, re, shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from v5.site_plan import require_site_plan

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'sites/wreath-region'
OUT=ROOT/'dist/wreath-region'
REPORT=ROOT/'reports/wreath-region'
DOMAIN='https://wreath.nalmada.net'
PHONE='1844-0644'
INTENTS=('same-day','flower-shop')
INTENT_NAMES={'same-day':'근조화환 당일배송','flower-shop':'화환전문 꽃집'}
HEADINGS={
'delivery':'당일 전달 가능 시각과 마감 확인',
'choice':'근조 3단·오브제 상품 비교',
'ribbon':'조의 리본과 보내는 이 문구',
'venue':'장례식장·빈소와 수령 장소 확인',
'fees':'반입 제한과 지역 추가 배송비',
'order':'상품 주문부터 배송 확인까지'
}
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f9f8f5;color:#24362f;font-family:system-ui,-apple-system,"Malgun Gothic",sans-serif;line-height:1.75;word-break:keep-all}a{color:inherit;text-decoration:none}.wrap{width:min(1160px,calc(100% - 32px));margin:auto}.top{background:#fff;border-bottom:1px solid #e6e5df}.top .wrap{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:17px 0}.logo{font-weight:850;font-size:23px;color:#476047}.nav{display:flex;gap:15px;align-items:center;flex-wrap:wrap;font-size:14px}.call{color:#fff!important;background:#3c5645;padding:10px 18px;border-radius:10px;display:inline-block;font-weight:700}.hero{background:linear-gradient(120deg,#eff3e9,#f7f0e9);padding:65px 0 56px}.eyebrow{font-size:12px;letter-spacing:.13em;color:#698371;font-weight:800}h1{font-size:clamp(29px,4.4vw,51px);line-height:1.25;margin:14px 0}h2{font-size:clamp(21px,2.6vw,28px);line-height:1.4}h3{font-size:18px}.lead{font-size:18px;color:#526358;max-width:780px}.pill{display:inline-flex;align-items:center;border:1px solid #c9d4c8;border-radius:100px;padding:5px 14px;margin:0 8px 8px 0;font-size:13px}.main{padding:35px 0 75px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}.card,.section{background:#fff;border:1px solid #e4e8df;border-radius:16px;padding:22px;min-width:0}.card p,.section p{color:#53655c}.card a.more,.more{color:#336b50;font-weight:750}.product img{width:100%;height:190px;object-fit:cover;border-radius:10px;background:#ecece6}.product .price{font-weight:800;font-size:19px;color:#3c5645}.product .muted{font-size:12px;color:#6e7970}.section{margin:22px 0}.section p{margin:10px 0 0}.step{display:inline-block;background:#dfede0;padding:3px 11px;border-radius:100px;color:#406047;font-weight:800;font-size:12px}.note{background:#f1ede4;border-left:4px solid #ad9573;padding:18px;border-radius:7px;margin:20px 0;color:#5d5348}.crumb{font-size:13px;color:#718277;margin:0 0 12px}.crumb a{text-decoration:underline}footer{background:#253f33;color:#f0f5ec;padding:40px 0}footer p{color:#d1dfd5}footer a{text-decoration:underline}.tags{display:flex;gap:8px;flex-wrap:wrap}.tags a{border:1px solid #dbe2d7;padding:6px 12px;border-radius:30px;background:white}.section ul{padding-left:22px}.faq{margin:14px 0;background:white;border:1px solid #e5e7df;border-radius:12px;padding:18px}.faq summary{font-weight:750;cursor:pointer}.faq p{margin-bottom:0}.footbar{position:fixed;bottom:12px;right:12px;background:#47624e;color:#fff!important;padding:13px 20px;border-radius:100px;box-shadow:0 5px 24px #17372b44;font-weight:750}@media(max-width:650px){.hero{padding:42px 0}.main{padding:26px 0 80px}.top .wrap{align-items:flex-start}.nav{gap:9px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.card{padding:14px}.product img{height:130px}.card h3{font-size:15px}.product .price{font-size:16px}.section{padding:18px}.footbar{bottom:8px;right:8px}}@media(max-width:390px){.grid{grid-template-columns:1fr}.product img{height:200px}}'''
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def esc(x):return html.escape(str(x),quote=True)
def slug(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
def province_url(province):return '/p/'+slug(province)+'.html'
def district_url(province,district):return '/d/'+slug(province+'|'+district)+'.html'
def area_url(record,intent):return '/r/'+slug('|'.join(record[:3]))+'-'+intent+'.html'
def title_name(record):return ' '.join(record[:3])
def pick(values,key,n=2):
    if n>len(values):raise ValueError('Not enough sentences')
    rng=random.Random(hashlib.sha256(key.encode('utf-8')).hexdigest())
    return rng.sample(values,n)
def breadcrumbs(*items):
    return '<div class="crumb"><a href="/">전국</a> / '+' / '.join('<a href="'+esc(href)+'">'+esc(label)+'</a>' for label,href in items)+'</div>'
def page(path,title,description,main,public):
    assert path=='/' or path.startswith('/') and path.endswith('.html')
    canonical='<link rel="canonical" href="'+DOMAIN+path+'">' if public else ''
    nav='<a href="/">전국 근조화환</a><a href="/#products">화환 상품</a><a href="/#steps">주문 순서</a>'
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width,initial-scale=1">'
     '<title>'+esc(title)+'</title><meta name="description" content="'+esc(description)+'">'
     '<meta name="robots" content="'+('index,follow' if public else 'noindex,nofollow')+'">'
     +canonical+'<link rel="stylesheet" href="/assets/wreath.css"></head><body>'
     '<header class="top"><div class="wrap"><a class="logo" href="/">꽃이랑 <small>근조화환</small></a>'
     '<nav class="nav" aria-label="주요 안내">'+nav+'<a class="call" href="tel:18440644">☎ '+PHONE+'</a></nav></div></header>'
     +main+'<footer><div class="wrap"><strong>꽃이랑 · 근조화환 주문 안내</strong>'
     '<p>근조화환 주문은 fwith.co.kr 상품 상세에서 진행합니다. 제작·배송 가능 시각과 지역별 추가비용은 주문 전에 확인해 주세요.</p>'
     '<p>고객센터 <a href="tel:18440644">'+PHONE+'</a> · 배송지·수령인 개인정보는 판매처 주문서에만 입력하세요.</p></div></footer>'
     '<a class="footbar" href="tel:18440644">전화 상담</a></body></html>')
def hero(head,desc,eyebrow='CONDOLENCE FLOWERS'):
    href='/#products' if eyebrow.endswith('DIRECTORY') or '찾을 수 없습니다' in head else '#products'
    return '<section class="hero"><div class="wrap"><div class="eyebrow">'+esc(eyebrow)+'</div><h1>'+esc(head)+'</h1><p class="lead">'+esc(desc)+'</p><a class="call" href="'+href+'">근조화환 상품 선택하기</a></div></section>'
def products_html(products):
    cards=[]
    for p in products:
        assert p['orderUrl']=='https://fwith.co.kr/shop/item.php?it_id='+p['id']
        assert p['imageUrl'].startswith('https://fwith.co.kr/data/item/')
        cards.append('<article class="card product"><img loading="lazy" decoding="async" alt="'+esc(p['name'])+' 판매처 상품 사진" src="'+esc(p['imageUrl'])+'">'
          '<h3>'+esc(p['name'])+'</h3><div class="price">'+format(p['referencePriceKRW'],',')+'원 <small>기준가</small></div>'
          '<p class="muted">2026-10-22 판매처 확인 기준 · 실제 금액은 주문 단계에서 확인</p>'
          '<a class="call" target="_blank" rel="noopener noreferrer" href="'+esc(p['orderUrl'])+'">상품 확인·주문</a></article>')
    return '<section id="products"><h2>실제 판매 상품에서 고르기</h2><p>최종 가격·상품 구성·추가 배송비는 상품별 주문 상세에서 확인하세요.</p><div class="grid">'+''.join(cards)+'</div></section>'
def order_steps():
    labels=['3단·오브제 상품 확인','장례식장명과 정확한 주소 확인','빈소·상주명과 희망일 준비','조의 문구와 보내는 이름 검토','판매처에서 최종 금액 확인·결제','주문내역·배송 상태 확인']
    return '<section id="steps" class="section"><h2>주문 전 확인할 여섯 단계</h2><ol>'+''.join('<li>'+esc(x)+'</li>' for x in labels)+'</ol><p>이 안내 사이트는 주문자·유가족의 이름, 연락처, 빈소 번호를 수집하지 않습니다. 결제와 입력은 판매처에서 합니다.</p></section>'
def all_rows(sampling=False):
    source=read(BASE/'regions.json')
    assert len(source['records'])==5034
    rows=[tuple(x) for x in source['records']]
    if sampling:
        wanted={('경기도','안산시 상록구','본오동'),('경기도','성남시 분당구','야탑동'),
                ('경기도','광명시','철산동'),('서울특별시','강남구','역삼동'),
                ('부산광역시','해운대구','우동'),('제주특별자치도','제주시','애월읍')}
        rows=[r for r in rows if tuple(r[:3]) in wanted]
        assert len(rows)==len(wanted),(len(rows),wanted)
    return rows
def home(rows,products,public):
    provinces=sorted({r[0] for r in rows})
    area_tiles=''.join('<a class="card" href="'+province_url(p)+'"><h3>'+esc(p)+'</h3><span class="more">지역별 주문 안내 →</span></a>' for p in provinces)
    body=hero('전국 근조화환 당일배송 · 화환전문 꽃집 선택','근조 3단화환과 오브제를 비교하고 리본 문구·장례식장 빈소·도착 희망 시각을 준비해 주문하세요. 당일 배송 가능 여부와 접수 마감은 지역별로 확인합니다.')
    body+='<main class="wrap main"><section><h2>지역 선택</h2><div class="grid">'+area_tiles+'</div></section>'
    body+=products_html(products)+order_steps()+'<section class="note">오늘 받을 수 있는지 여부는 주문 시각, 꽃 수급, 제작처와 수취 장소의 조건에 따라 달라집니다. 도서·산간 또는 일부 읍면동은 추가 배송비가 발생할 수 있습니다.</section></main>'
    return page('/','전국 근조화환 당일배송·화환전문 꽃집 선택 | 꽃이랑','전국 근조 3단·오브제 화환 종류·기준가격·리본 문구·빈소 확인과 주문 단계 안내.',body,public)
def province_page(province,groups,public):
    district=sorted([d for (p,d) in groups if p==province])
    tiles=''.join('<a class="card" href="'+district_url(province,d)+'"><h3>'+esc(d)+'</h3><span class="more">읍면동별 주문 안내</span></a>' for d in district)
    desc=province+' 장례식장 근조화환 3단·오브제 주문과 배송 가능 여부를 확인하는 방법.'
    body=hero(province+' 근조화환 주문 지역 찾기',desc,'PROVINCE DIRECTORY')
    return page(province_url(province),province+' 근조화환·화환전문 꽃집 지역 안내 | 꽃이랑',desc,body+'<main class="wrap main">'+breadcrumbs((province,province_url(province)))+'<div class="grid">'+tiles+'</div></main>',public)
def district_page(province,district,records,public):
    tiles=[]
    for r in records:
        tiles.append('<div class="card"><h3>'+esc(r[2])+'</h3><div class="tags">'+
            ''.join('<a href="'+area_url(r,intent)+'">'+esc(INTENT_NAMES[intent])+'</a>' for intent in INTENTS)+'</div></div>')
    desc=province+' '+district+' 읍면동 이름별 근조화환 주문 조건과 꽃집 상품 선택.'
    body=hero(province+' '+district+' 근조화환 주문',desc,'DISTRICT DIRECTORY')
    return page(district_url(province,district),province+' '+district+' 근조화환·꽃집 지역별 안내 | 꽃이랑',desc,
         body+'<main class="wrap main">'+breadcrumbs((province,province_url(province)),(district,district_url(province,district)))+
         '<p class="note">아래 목록은 지역명 탐색을 위한 것으로 해당 동에 실제 오프라인 매장이나 당일 배송이 보장된다는 뜻이 아닙니다.</p>'
         '<div class="grid">'+''.join(tiles)+'</div></main>',public)
def article(record,intent,products,public):
    name=title_name(record)
    label=INTENT_NAMES[intent]
    key=name+'|'+intent
    pool=read(BASE/'copy-pool.json')
    lead=pick(pool['leads'][intent],key+'|intro',1)[0]
    intro=name+' '+label+' 주문을 알아보실 때에는 상품 선택과 실제 배송 장소를 함께 확인해 주세요. '+lead
    sections=[]
    for group,heading in HEADINGS.items():
        sentences=pick(pool['sections'][group],key+'|'+group,2)
        sections.append((group,heading,' '.join(sentences)))
    if intent=='same-day':
        title=name+' 근조화환 당일배송 가능 여부·주문방법 | 꽃이랑'
        desc=name+' 근조화환 당일 배송 마감 확인부터 3단·오브제 선택, 빈소·리본·배송비·주문 확인까지 안내.'
    else:
        title=name+' 화환전문 꽃집 근조 3단·오브제 선택 | 꽃이랑'
        desc=name+' 화환전문 꽃집 상품 비교, 기준가격·조의 리본·장례식장 빈소·배송 확인 절차 안내.'
    desc=desc[:155]
    head=name+' '+label+' 주문 안내'
    body=hero(head,intro,'SAME DAY · CHECK FIRST' if intent=='same-day' else 'FLOWER SHOP · COMPARE')
    body+='<main class="wrap main">'+breadcrumbs((record[0],province_url(record[0])),(record[1],district_url(record[0],record[1]))) 
    body+='<div class="tags"><a href="'+area_url(record,INTENTS[1] if intent==INTENTS[0] else INTENTS[0])+'">같은 지역의 다른 주문 방법 보기 →</a></div>'
    body+='<article class="article">'
    for n,(group,heading,paragraph) in enumerate(sections,1):
        body+='<section class="section"><span class="step">'+str(n).zfill(2)+'</span><h2>'+esc(heading)+'</h2><p>'+esc(paragraph)+'</p></section>'
    body+='</article>'+products_html(products)+order_steps()
    body+='<section class="note"><strong>당일 배송 안내</strong><p>'+esc(name)+'이라는 지역명만으로 오늘 도착이나 추가 배송비 무료를 보장하지 않습니다. 접수 마감·배송 가능성·반입 규정은 fwith.co.kr 판매처에서 상품과 정확한 장례식장 주소를 기준으로 확인하세요.</p></section>'
    body+='<section class="faq"><h2>자주 묻는 질문</h2><details><summary>당일 근조화환 배송이 확정되나요?</summary><p>아닙니다. 주문 시간·제작·배송 지역 및 빈소 상황을 확인한 뒤 가능 여부를 안내합니다.</p></details><details><summary>리본에는 어떤 문구를 쓰나요?</summary><p>‘삼가 고인의 명복을 빕니다’와 보내는 분의 성함 또는 단체명을 구분해 작성합니다.</p></details><details><summary>가격과 배송비는 어디에서 최종 확인하나요?</summary><p>상품별 fwith.co.kr 상세·주문 단계에서 실제 금액과 배송 조건을 확인합니다.</p></details></section>'
    body+='</main>'
    return page(area_url(record,intent),title,desc,body,public),intro,sections
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sample',action='store_true')
    ap.add_argument('--public',action='store_true')
    args=ap.parse_args()
    if args.sample and args.public:raise ValueError('Do not release subset as nationwide public sitemap')
    require_site_plan('wreath-region')
    products=read(BASE/'products.json')['list']
    assert len(products)==6
    for p in products:
        assert p['orderUrl']=='https://fwith.co.kr/shop/item.php?it_id='+p['id']
        assert urlparse(p['imageUrl']).netloc=='fwith.co.kr'
    records=all_rows(args.sample)
    if OUT.exists():shutil.rmtree(OUT)
    (OUT/'p').mkdir(parents=True)
    (OUT/'d').mkdir()
    (OUT/'r').mkdir()
    (OUT/'assets').mkdir()
    REPORT.mkdir(parents=True,exist_ok=True)
    (OUT/'assets'/'wreath.css').write_text(CSS,encoding='utf-8')
    groups=defaultdict(list)
    for record in records:groups[(record[0],record[1])].append(record)
    published=[]
    def write(url,body):
        path=OUT/('index.html' if url=='/' else url.lstrip('/'))
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(body,encoding='utf-8')
        published.append(url)
    write('/',home(records,products,args.public))
    for province in sorted({x[0] for x in records}):
        write(province_url(province),province_page(province,groups,args.public))
    for key,rr in sorted(groups.items()):
        write(district_url(*key),district_page(*key,rr,args.public))
    candidate=[]
    for record in records:
        for intent in INTENTS:
            body,intro,sections=article(record,intent,products,args.public)
            write(area_url(record,intent),body)
            candidate.append({'url':area_url(record,intent),'region':title_name(record),'intent':intent,'body':intro+' '+' '.join(x[2] for x in sections)})
    error=page('/404.html','찾을 수 없는 페이지 | 꽃이랑','올바른 지역 안내에서 주문 방법을 확인해 주세요.',hero('페이지를 찾을 수 없습니다','지역 선택으로 돌아가 근조화환 주문 정보를 확인해 주세요.')+'<main class="wrap main"><a href="/">홈으로 돌아가기</a></main>',False)
    (OUT/'404.html').write_text(error,encoding='utf-8')
    if args.public:
        key_path=BASE/'indexnow-public-key.txt'
        key=key_path.read_text(encoding='utf-8').strip()
        assert re.fullmatch(r'[a-f0-9]{32}',key), 'Invalid existing public IndexNow key format'
        (OUT/(key+'.txt')).write_text(key+chr(10),encoding='utf-8')
        (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n',encoding='utf-8')
        ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
        root=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
        for url in published:ET.SubElement(ET.SubElement(root,'{http://www.sitemaps.org/schemas/sitemap/0.9}url'),'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=DOMAIN+url
        ET.ElementTree(root).write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    else:(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    manifest={'site':'wreath-region','mode':'public-candidate' if args.public else 'preview','sample':args.sample,'pageCount':len(published),
       'regionRows':len(records),'articleCount':len(candidate),'provinceCount':len({r[0] for r in records}),'districtCount':len(groups),
       'links':[DOMAIN+u for u in published[:8]],'regionSource':'sites/wreath-region/regions.json',
       'sellerCatalog':'sites/wreath-region/products.json','pages':published}
    (REPORT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (REPORT/'article-content.json').write_text(json.dumps(candidate,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('pages','links')},ensure_ascii=False))
if __name__=='__main__':main()
