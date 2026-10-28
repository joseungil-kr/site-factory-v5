"""Isolated office-opening site; no paid dependencies, customer storage or order submission."""
from pathlib import Path
from html import escape
import argparse
import hashlib
import json
import random
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from v5.site_plan import require_site_plan

SITE = ROOT / 'sites/officeplant'
DOMAIN = 'https://officeplant.nalmada.net'
PRODUCTS = [
    dict(sku='D144', name='금전수 탁상용', price=53000, use='책상·작은 선반'),
    dict(sku='D158', name='스투키 탁상용', price=50000, use='업무 책상·카운터'),
    dict(sku='D149', name='녹보수 소형', price=65000, use='접견 자리·사무공간'),
]
for p in PRODUCTS:
    p['url'] = 'https://fwith.co.kr/shop/item.php?it_id=' + p['sku']
    p['image'] = 'https://fwith.co.kr/data/item/flower379/' + p['sku'] + '/thumb-1_500x500.jpg'

def shell(title, content, path, public=False):
    canonical = f'<link rel="canonical" href="{DOMAIN}{path}">' if public else ''
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | 오피스화분</title><meta name="description" content="{escape(title)}. 놓을 자리와 예산으로 개업화분을 고르고 리본 문구와 수령 정보를 준비하세요."><meta name="robots" content="{'index,follow' if public else 'noindex,nofollow'}">{canonical}<link rel="stylesheet" href="/assets/officeplant.css"><script src="/assets/officeplant.js" defer></script></head><body><header><a class="brand" href="/">오피스<span>화분</span><small>새로운 일의 시작에</small></a><nav aria-label="주 메뉴"><a href="/#collection">화분 고르기</a><a href="/regions.html">지역 안내</a><a href="/order.html">주문 준비</a></nav><a class="phone" href="tel:18440644">1844-0644</a></header><main>{content}</main><footer><div><strong>오피스화분</strong><p>사무실 개업·이전·거래처 선물</p></div><div><a href="tel:18440644">꽃이랑 상담 1844-0644</a><p><a href="https://fwith.co.kr">상품 주문 · 꽃이랑</a></p></div><a href="/order.html">리본과 수령정보 준비하기 ↗</a></footer></body></html>'''

def card(p):
    return f'''<article class="product" data-price="{p['price']}" data-space="{'desk' if p['sku'] in ('D144','D158') else 'reception'}"><a href="{p['url']}"><img src="/assets/{p['sku']}.jpg" alt="{p['name']}" width="500" height="500" loading="lazy"></a><div class="product-info"><small>{p['use']}</small><h3>{p['name']}</h3><strong>{p['price']:,}원</strong><p><a href="{p['url']}">상품 상세 · 주문하기 ↗</a></p><a class="subtle" href="/order.html?sku={p['sku']}">이 화분으로 주문 준비</a></div></article>'''

def helper():
    options = ''.join(f'<option value="{p["sku"]}">{p["name"]} · {p["price"]:,}원</option>' for p in PRODUCTS)
    return '''<div class="wrap"><div class="intro"><span class="eyebrow">ORDER NOTE</span><h1>마음을 적고,<br>받을 곳을 확인해요.</h1><p>작성 내용은 이 화면에서만 정리합니다. 메모를 복사한 뒤 꽃이랑 상품 상세에서 주문하거나 전화로 상담하세요.</p></div><form id="order-note"><div class="form-grid"><label>선택한 화분<select name="sku">'''+options+'''</select></label><label>선물 목적<select name="purpose"><option>사무실 개업 축하</option><option>사무실 이전 축하</option><option>거래처 개업선물</option></select></label><label>축하 리본문구<input name="ribbon" maxlength="80" placeholder="새로운 시작을 응원합니다"></label><label>보내는 이름·회사<input name="sender" maxlength="80"></label><label>받는 회사·담당자<input name="recipient" maxlength="100" autocomplete="off"></label><label>수령 연락처<input name="phone" type="tel" maxlength="30" autocomplete="off"></label><label class="wide">수령 주소·건물·층·호수<input name="address" maxlength="200" autocomplete="off"></label><label>희망 날짜<input name="date" type="date"></label><label>수령 가능 시간<input name="time" maxlength="60" placeholder="예: 오전 10시~오후 1시"></label><label class="wide">반입·수령 요청<textarea name="note" maxlength="500" rows="3" placeholder="로비 수령 등 필요한 사항"></textarea></label></div><button type="submit" class="button">주문 메모 정리하기</button><button type="reset" class="outline">입력 지우기</button></form><section class="note-output" hidden><h2>상담·주문에 사용할 메모</h2><pre id="summary"></pre><button type="button" class="button" id="copy-note">메모 복사</button><a id="checkout" class="outline" href="https://fwith.co.kr/shop/item.php?it_id=D144">꽃이랑에서 주문 이어가기 ↗</a><p id="copy-status" role="status"></p><p>복사한 메모는 판매처의 주문 입력란이나 상담에 사용하세요. 상품 상세로 이동해도 작성 내용이 자동 전송되지는 않습니다.</p></section><section class="steps"><h2>주문은 이렇게 이어집니다</h2><ol><li>화분과 수량을 선택합니다.</li><li>리본 문구·보내는 이름·받는 주소를 확인합니다.</li><li>꽃이랑에서 최종 금액·전달 일정을 확인하고 주문합니다.</li></ol><a href="tel:18440644">전화로 상담 1844-0644</a></section></div>'''

def build(public=False):
    require_site_plan('officeplant')
    out = ROOT / 'dist' / ('officeplant-public' if public else 'officeplant')
    (out/'assets').mkdir(parents=True, exist_ok=True)
    (out/'r').mkdir(exist_ok=True)
    for asset in (SITE/'assets').iterdir():
        shutil.copy2(asset, out/'assets'/asset.name)
    rows = json.loads((ROOT/'data/regions/seoul_gyeonggi_current_dong.json').read_text(encoding='utf-8'))['rows']
    assert len(rows) == 1732 and len({tuple(r) for r in rows}) == 1732
    pool = [line.split('|',1) for line in (SITE/'copy-pool.txt').read_text(encoding='utf-8').splitlines() if line]
    pages = []
    # Bound shared paragraph combinations across the whole corpus, independently of QA sample.
    assigned = []
    def write(path,title,body):
        (out/('index.html' if path=='/' else path.lstrip('/'))).write_text(shell(title,body,path,public),encoding='utf-8')
        pages.append(dict(path=path,title=title))
    home = '''<section class="hero wrap"><div><span class="eyebrow">A GREEN START FOR YOUR OFFICE</span><h1>새로운 사무실,<br>첫 인사는 <em>초록으로.</em></h1><p>책상 한켠의 작은 응원부터<br>거래처에 전하는 단정한 축하까지.</p><a class="button" href="#collection">놓을 자리에 맞춰 고르기 ↓</a><a class="text-link" href="/order.html">리본문구 먼저 준비하기 ↗</a></div><figure><img src="/assets/D144.jpg" alt="금전수 탁상용 화분" width="500" height="500"><figcaption><span>01 / DESK PLANT</span><strong>금전수 탁상용</strong><span>53,000원</span></figcaption></figure></section><section class="band"><div class="wrap three"><div><b>01</b><h2>공간을 먼저</h2><p>책상·선반·접견 자리.<br>놓을 곳의 폭부터 생각해요.</p></div><div><b>02</b><h2>예산에 맞게</h2><p>상품과 전달 비용을 확인해<br>마음에 맞는 선물을 골라요.</p></div><div><b>03</b><h2>인사를 또렷하게</h2><p>리본문구와 보내는 이름,<br>수령정보까지 한 번에 정리해요.</p></div></div></section><section class="wrap collection" id="collection"><div class="section-title"><div><span class="eyebrow">THE OFFICE COLLECTION</span><h2>어디에 놓을 선물인가요?</h2></div><p>작은 공간을 위한 세 가지 선택</p></div><div class="products">'''+''.join(card(p) for p in PRODUCTS)+'''</div></section><section class="editorial wrap"><div><span class="eyebrow">A NOTE FOR YOUR NEW BEGINNING</span><h2>화분보다 먼저<br>전하고 싶은 한마디.</h2><p>“새로운 일의 시작을 함께 응원합니다.”<br>축하의 말과 보내는 이름을 나누어 적어 보세요.</p><a class="button" href="/order.html">리본 · 수령 메모 만들기 ↗</a></div><div class="paper"><small>TO YOUR NEW OFFICE</small><p>축 개업<br>새로운 시작을 응원합니다</p><span>보내는 이름 · 회사명</span></div></section><section class="wrap bottom-links"><h2>받는 지역부터 확인할까요?</h2><a href="/regions.html">서울·경기 지역별 개업선물 안내 ↗</a><a href="/moran.html">모란시장 주변 사무실 선물 준비 ↗</a></section>'''
    filters='''<div class="filters"><label>놓을 공간<select id="space-filter"><option value="all">전체 공간</option><option value="desk">책상·카운터</option><option value="reception">접견 자리</option></select></label><label>상품 예산<select id="budget-filter"><option value="999999">전체 예산</option><option value="50000">5만원 이하</option><option value="60000">6만원 이하</option><option value="70000">7만원 이하</option></select></label><label>선물 목적<select id="purpose-filter"><option value="opening">사무실 개업</option><option value="move">사무실 이전</option><option value="partner">거래처 개업</option></select></label></div><p id="selection-advice" role="status">놓을 자리의 크기를 확인하고 리본에 담을 인사를 골라보세요.</p><p id="no-products" hidden>이 조건의 상품은 전화로 상담하세요. <a href="tel:18440644">1844-0644</a></p>'''
    home=home.replace('<div class="products">',filters+'<div class="products">',1)
    write('/','사무실 개업화분·개업선물',home)
    write('/order.html','사무실 개업화분 주문 준비',helper())
    directory = '<div class="wrap"><div class="intro"><span class="eyebrow">FIND YOUR AREA</span><h1>받는 주소의 지역을 찾아보세요</h1><p>지역명을 입력해 사무실 개업화분과 개업선물 안내를 찾아보세요.</p><label>지역 검색<input id="region-search" type="search" placeholder="예: 성남시 중원구 성남동"></label></div><div class="region-list">'
    for i,(district,dong) in enumerate(rows,1):
        region = district+' '+dong
        directory += f'<div class="region-row"><strong>{region}</strong><a href="/r/{i}-opening.html">개업화분</a><a href="/r/{i}-gift.html">개업선물</a></div>'
        for intent,label in [('opening','사무실 개업화분'),('gift','사무실 개업선물')]:
            key=f'{region}/{intent}'
            rng=random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16],16))
            for attempt in range(100000):
                indices=rng.sample(range(len(pool)),10)
                mask=sum(1<<n for n in indices)
                if all((mask & prior).bit_count() <= 4 for prior in assigned):
                    assigned.append(mask)
                    selected=[pool[n] for n in sorted(indices)]
                    break
            else:
                raise RuntimeError('Copy pool cannot allocate distinct paragraph combinations')
            paragraphs=''.join(f'<section><h2>{escape(h)}</h2><p>{escape(t)}</p></section>' for h,t in selected)
            p=PRODUCTS[i%len(PRODUCTS)]
            lead = '사무실에 놓을 자리를 정하고 상품 크기와 수령 방법을 함께 준비하세요.' if intent=='opening' else '받는 분과의 관계, 예산, 축하 문구를 정리해 마음에 맞는 선물을 선택하세요.'
            other='gift' if intent=='opening' else 'opening'
            body=f'<div class="wrap document"><a class="breadcrumb" href="/regions.html">서울·경기 지역 안내</a><span class="eyebrow">OFFICE GIFT GUIDE</span><h1>{region}<br>{label}</h1><p class="lead">{lead}</p><div class="article-layout"><article>{paragraphs}</article><aside>{card(p)}<a class="button" href="/order.html?sku={p["sku"]}">리본·수령 메모 작성</a><p><a href="tel:18440644">1844-0644 상담</a></p></aside></div><nav class="related" aria-label="관련 지역 문서"><a href="/r/{i}-{other}.html">{region} 다른 선물 안내</a><a href="/r/{i%len(rows)+1}-{intent}.html">다음 지역 안내</a><a href="/moran.html">모란시장 주변 사무실</a></nav></div>'
            write(f'/r/{i}-{intent}.html',region+' '+label,body)
    write('/regions.html','서울·경기 사무실 개업선물 지역 안내',directory+'</div></div>')
    moran='''<div class="wrap document"><span class="eyebrow">MORAN · OFFICE OPENING</span><h1>모란시장 주변 사무실,<br>개업선물을 준비하는 순서</h1><p class="lead">모란시장이라는 장소명만으로 주문 주소를 대신하지 마세요. 받는 회사의 도로명 주소와 층·호수를 먼저 적어 두면 상담이 구체적이 됩니다.</p><section><h2>작은 책상에 둘지, 접견 자리에 둘지</h2><p>놓을 자리가 정해졌다면 받침 폭과 잎이 펼쳐지는 공간을 살펴보세요. 방문객이 드나드는 출입문 앞보다는 업무 동선에 겹치지 않는 위치를 받는 분과 정하는 편이 좋습니다.</p></section><div class="products">'''+''.join(card(p) for p in PRODUCTS)+'''</div><section><h2>개업 인사와 보내는 이름</h2><p>거래처 선물이라면 회사 이름을 정확히 적고, 개인 선물이라면 받는 분이 알아볼 이름을 사용하세요. 여러 사람이 함께 보낼 때에는 모임명과 축하의 한마디를 따로 정리해 두세요.</p></section><section><h2>수령 주소를 빠짐없이</h2><p>회사명, 도로명 주소, 건물명, 층과 호수, 연락 가능한 담당자를 준비하세요. 희망 날짜와 수령 가능한 시간대, 로비 전달 여부를 적은 뒤 상품과 함께 전화로 상담할 수 있습니다.</p><a class="button" href="/order.html">주문 메모 정리하기</a> <a href="tel:18440644">1844-0644</a></section></div>'''
    write('/moran.html','모란시장 사무실 개업꽃집·개업화분 선물 안내',moran)
    assert len(pages)==3468
    (out/'404.html').write_text(shell('페이지를 찾을 수 없습니다','<div class="wrap intro"><h1>페이지를 찾을 수 없습니다</h1><a href="/">홈으로 돌아가기</a></div>','/404.html'),encoding='utf-8')
    (out/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n' if public else 'Disallow: /\n'),encoding='utf-8')
    sitemap=out/'sitemap.xml'
    if public:
        sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+DOMAIN+p['path']+'</loc></url>' for p in pages)+'</urlset>',encoding='utf-8')
    elif sitemap.exists():
        sitemap.unlink()
    report=ROOT/'reports/officeplant';report.mkdir(parents=True,exist_ok=True)
    manifest={'site':'officeplant','public':public,'pages':pages,'contentCount':len(pages),'regions':len(rows),'poolBlocks':len(pool),'sourceRegionSHA256':hashlib.sha256((ROOT/'data/regions/seoul_gyeonggi_current_dong.json').read_bytes()).hexdigest()}
    (report/('manifest-public.json' if public else 'manifest.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='pages'},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--public',action='store_true');args=parser.parse_args();build(args.public)