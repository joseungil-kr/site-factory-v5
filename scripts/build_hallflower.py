"""Build a 3-facility isolated, noindex prototype. Full corpus requires later source import."""
from pathlib import Path
from html import escape
import json, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/hallflower-preview'
DOMAIN='https://hallflower.nalmada.net'
FACILITIES=[
 ('fh-24ec0a8cbedf5c24ef4f','서울대학교병원장례식장','서울특별시 종로구 대학로 101,서울대학교병원 (연건동)'),
 ('fh-8535f9af931e08a5c478','삼성서울병원장례식장','서울특별시 강남구 일원로 81 (일원동, 삼성의료원)'),
 ('fh-86aa706fd39fc6107d5b','서울아산병원 장례식장','서울특별시 송파구 올림픽로43길 88 (풍납동, 서울아산병원)')
]
PRODUCTS=[
 ('B200','근조 3단 화환',59000),
 ('B203','근조 고급 3단 화환',79000),
 ('B205','근조 특대 3단 화환',109000),
 ('B212','근조 1단 오브제',60000),
 ('B214','장례식장 근조 서양란',200000)
]
CSS="""*{box-sizing:border-box}body{margin:0;background:#f8f7f4;color:#222;font:16px/1.7 system-ui,'Malgun Gothic',sans-serif}header,footer{background:#182a26;color:white;padding:22px max(24px,calc((100vw - 1080px)/2))}header a,footer a{color:white}.wrap{max-width:1080px;margin:auto;padding:24px}h1{font-size:clamp(28px,5vw,48px);line-height:1.3}h2{font-size:24px;margin-top:38px}a{color:#17634c}button,.cta{display:inline-block;background:#17634c;color:white;border:0;border-radius:8px;padding:12px 18px;text-decoration:none;cursor:pointer}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}.card,section{background:white;border:1px solid #e2e1dc;border-radius:14px;padding:22px;margin:16px 0}.price{font-size:24px;font-weight:700}small{color:#566861}.muted{color:#5c625d}label{display:block;margin:12px 0}input,select,textarea{display:block;width:100%;padding:10px;border:1px solid #9aa6a0;border-radius:6px;font:inherit}button:disabled{opacity:.5;cursor:not-allowed}nav a{margin-right:16px}@media(max-width:600px){.wrap{padding:16px}.card,section{padding:16px}header,footer{padding:18px}}"""
JS="""'use strict';
const panel=document.getElementById('memo'), btn=document.getElementById('make-note'), output=document.getElementById('note-output');
if(panel && btn && output){
  try{
    if(panel.tagName==='FORM') throw Error('unsafe native form');
    btn.addEventListener('click',()=>{
      const values=Object.fromEntries([...panel.querySelectorAll('[name]')].map(e=>[e.name,e.value.trim()]));
      const lines=['장례식장: '+document.body.dataset.hall,...Object.entries(values).filter(([k,v])=>v).map(([k,v])=>k+': '+v)];
      output.textContent=lines.join('\\n');output.hidden=false;
    });
    btn.disabled=false;btn.setAttribute('aria-disabled','false');
    document.getElementById('memo-status').textContent='내용은 서버로 전송되지 않습니다. 복사하여 판매처 주문 화면에서 작성하세요.';
  }catch(err){btn.disabled=true;}
}
"""
def layout(title,body,canonical):
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><meta name="robots" content="noindex,nofollow"><meta name="description" content="{escape(title)}. 빈소 확인부터 리본 작성, 상품 비교와 전달 상담까지."><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script></head><body data-hall="{escape(canonical)}"><header><strong>꽃이랑 · 장례식화환 주문 안내</strong><nav><a href="/">장례식장 목록</a><a href="tel:18440644">상담 1844-0644</a></nav></header><main class="wrap">{body}</main><footer>장례식장과 제휴한 공식 사이트가 아닙니다. 상품 주문 및 배송 가능 여부는 꽃이랑에서 최종 확인합니다. <a href="https://fwith.co.kr">꽃이랑 주문몰</a></footer></body></html>'''
def cards():
    return '<div class="cards">'+''.join(f'<article class="card"><small>꽃이랑 상품번호 {sku}</small><h3>{escape(name)}</h3><p class="price">{price:,}원</p><p>지역·수령 조건에 따라 배송비와 가능 품목을 주문 전 확인하세요.</p><a class="cta" href="https://fwith.co.kr/shop/item.php?it_id={sku}" rel="noopener">실제 상품 확인·주문</a></article>' for sku,name,price in PRODUCTS)+'</div>'
def page(i,id,name,address):
    title=name+' 빠른 장례식화환 주문방법'
    intro=['빈소가 정해졌는지 먼저 확인하세요. 같은 병원 안에도 여러 빈소가 있으므로 장례식장 이름만으로 주문을 완료하지 마세요.',
           '받는 곳의 정확한 명칭과 빈소 호실을 확인한 다음 주문 담당자에게 알려주세요. 빈소 미확정 상태에서는 먼저 상담이 필요합니다.',
           '상주 또는 고인 성함을 확인할 수 있다면 빈소 정보와 대조하세요. 해당 내용은 이 안내 페이지에 입력하지 않아도 됩니다.'][i]
    extra=['접수 가능한 빈소와 출입 절차는 당일 운영 상황에 따라 달라질 수 있습니다. 상담에서 반입 가능 품목과 배치 장소도 확인하세요.',
           '화환 종류를 정한 후 가격뿐 아니라 배송비와 도착 희망 시간을 함께 확인하세요. 현장 접수 가능 여부는 보장하지 않습니다.',
           '리본에 보내는 분의 회사명 또는 모임명을 적을 때 오탈자가 없도록 주문 전 재확인하세요. 제작 이후 수정이 제한될 수 있습니다.'][i]
    body=f'''<p><a href="/">전체 장례식장 안내</a></p><h1>{escape(title)}</h1><p class="muted">시설 자료 기준 주소: {escape(address)}. 현재 운영·주소·빈소 정보는 별도 재확인이 필요합니다.</p><section><h2>1. 빈소·상주 정보를 먼저 확인</h2><p>{intro}</p><p>장례식장 이름과 건물 주소, 빈소 호실을 대조하세요. 개인 이름이나 연락처는 공개 페이지에 작성하지 마세요.</p></section><section><h2>2. 상품과 가격 선택</h2><p>실제 꽃이랑 판매 목록에서 확인한 상품 5종입니다. 꽃 구성·금액은 변경될 수 있고 지역별 추가배송비는 별도로 확인해야 합니다.</p>{cards()}</section><section><h2>3. 리본 문구와 보내는 분 준비</h2><p>추모 문구 예: 삼가 고인의 명복을 빕니다. 보내는 분 표기 예: ○○회사 임직원 일동. 종교 표현을 단정하지 않고 유족의 의사를 존중합니다.</p><p>{extra}</p></section><section><h2>4. 희망 전달시간 상담 및 주문 확인</h2><p>장례 일정과 발인 전 전달 가능 시간을 먼저 상담하세요. 주문 후 주문번호·상품·빈소·리본 문구·배송확인 방법을 판매처에서 확인합니다. 몇 시간 이내 도착이나 당일배송을 보장하지 않습니다.</p><a class="cta" href="tel:18440644">꽃이랑 전화 상담</a></section><section><h2>주문 상담용 메모</h2><p>개인정보를 URL이나 서버로 보내지 않는 브라우저 전용 정리 도구입니다. 스크립트가 작동하지 않으면 버튼은 비활성화됩니다.</p><div id="memo" role="group"><label>상품<select name="상품"><option>근조 3단 화환 B200</option><option>근조 고급 3단 화환 B203</option><option>근조 특대 3단 화환 B205</option><option>근조 1단 오브제 B212</option><option>장례식장 근조 서양란 B214</option></select></label><label>빈소 호실<input name="빈소" autocomplete="off" maxlength="40"></label><label>리본 추모 문구<input name="추모문구" maxlength="80"></label><label>보내는 분 표기<input name="보내는분" autocomplete="off" maxlength="80"></label><label>희망 전달시간<input name="희망시간" maxlength="60"></label></div><button id="make-note" type="button" disabled aria-disabled="true">주문 메모 정리</button><p id="memo-status">기능 준비 중: 개인정보를 입력하지 마세요.</p><pre id="note-output" hidden></pre><p>정리한 내용은 복사하여 실제 꽃이랑 주문 화면에서 직접 입력하세요. 자동 전송되지 않습니다.</p></section><section><h2>배송 확인</h2><p>판매처 주문 완료 후 실제 접수 상태와 배송 완료 안내를 확인하세요. 이 안내 페이지는 배송 추적이나 빈소 현황을 조회하지 않습니다.</p></section>'''
    slug=f'{i+1}-{id}.html'
    (OUT/'halls'/slug).write_text(layout(title,body,name),encoding='utf-8')
    return slug
def build():
    (OUT/'assets').mkdir(parents=True,exist_ok=True);(OUT/'halls').mkdir(exist_ok=True)
    (OUT/'assets/site.css').write_text(CSS,encoding='utf-8')
    (OUT/'assets/site.js').write_text(JS,encoding='utf-8')
    slugs=[page(i,*f) for i,f in enumerate(FACILITIES)]
    links=''.join(f'<li><a href="/halls/{s}">{escape(f[1])} 빠른 장례식화환 주문방법</a> — {escape(f[2])}</li>' for f,s in zip(FACILITIES,slugs))
    (OUT/'index.html').write_text(layout('장례식장별 빠른 장례식화환 주문방법','<h1>장례식장별 빠른 장례식화환 주문방법</h1><p>대표 3개 시설 시안입니다. 실시간 운영·빈소 정보는 확인되지 않았습니다.</p><ul>'+links+'</ul><p><a href="tel:18440644">주문 상담 1844-0644</a></p>','장례식장 목록'),encoding='utf-8')
    (OUT/'404.html').write_text(layout('페이지 없음','<h1>페이지를 찾을 수 없습니다</h1><a href="/">홈으로</a>',''),encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps({'preview':True,'facilitySourceRepo':'joseungil-kr/site-factory-v4','facilitySourceBranch':'feature/funeralflower-mini','facilityBlobSHA':'b950e7bf2cde7b247447fbe670c976363e4e1a7e','sourceCount':1080,'sampleCount':3,'facilityCurrentOperation':'unverified','pages':['/']+['/halls/'+s for s in slugs]},ensure_ascii=False,indent=2),encoding='utf-8')
    assert len(slugs)==3 and all((OUT/'halls'/s).is_file() for s in slugs)
    assert all('noindex,nofollow' in (OUT/'halls'/s).read_text() for s in slugs)
    assert not any((OUT/'halls'/s).read_text().count('<form') for s in slugs)
    assert all('https://fwith.co.kr/shop/item.php?it_id=B205' in (OUT/'halls'/s).read_text() for s in slugs)
    print('PASS: three independent noindex pages, private-safe memo, product links')
if __name__=='__main__':build()
