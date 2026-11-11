"""Three evidence-based buyer decision previews; never production or locality uniqueness proof."""
import json,sys,re
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from worker6_core_five_preview import generate_inputs,operator_policy

from worker6_shipping_render import lookup,evidence_section
from v5.purpose_render import assemble,render
def with_required_receipt_paths(pool):
    # Same three required questions as the six-region controlled preview.
    result=deepcopy(pool)
    required=[
      ('수령 장소 선택 · 회사·사무실','회사나 사무실에서 받을 경우 회사명과 새 부서, 건물 층·호실을 확인했나요? 근무하는 날짜와 실제 수령 담당자를 확인하고 상품을 받을 자리를 정하세요.'),
      ('수령 장소 선택 · 자택','자택에서 받을 경우 도로명주소와 건물번호, 동·호수를 확인했나요? 받는 분이 집에 있는 시간과 부재 시 연락·수령 방법을 먼저 확인하세요.'),
      ('수령 장소 선택 · 행사장','행사장에서 받을 경우 행사 시작시각과 물품 반입 가능 시간을 확인했나요? 수령 창구와 담당자를 확인하고 희망 도착시각을 전화로 상담하세요.')]
    for heading,paragraph in required:
        if not any(x.get('heading')==heading for x in result['sections']):
            result['sections'].append({'slot':'choice','role':'required','heading':heading,'paragraph':paragraph})
    return result
SITE=ROOT/'sites/promotion-gift-plants'
OUT=ROOT/'reports/promotion-gift-plants/three-buyer-designs'
OUT.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads((SITE/p).read_text(encoding='utf-8'))
site=read('site.json');site.update(domain=None,publishEnabled=False)
products=read('products.json')
operator=read('operator-service-confirmation-20261109.json')
spec,_,_,_=generate_inputs(read('core-five-seller-evidence.json'),read('site-spec.json'),site,operator_source=operator)
shared=operator_policy(operator)
skus={p['sku'] for p in products}
cases=[
 dict(id='jeokseong-office',region='경기도 파주시 적성면',location=('경기도','파주시','적성면'),purpose='promotion',productSkus=['D144','E008'],
      heading='적성면 마지리 주소를 다시 확인하는 질문',
      paragraph='파주시 공식 관할구역 자료에는 행정 마지1리·마지2리·마지3리가 법정 마지리에 대응합니다. 수령지가 이 가운데 하나로 전달됐다면 실제 도로명과 건물번호, 상세주소를 확인했나요? 지번주소라면 법정 마지리와 지번을 확인하세요.',
      url='https://dong.paju.go.kr/dong/dong_01/dong_sub08/dong_sub08_02.jsp',
      question='실제 도로명과 건물번호, 상세주소를 확인했나요?'),
 dict(id='seorak-venue',region='경기도 가평군 설악면',location=('경기도','가평군','설악면'),purpose='congratulations',productSkus=['F055','D152'],
      heading='설악면 배송비 표의 중복 표시 확인',
      paragraph='꽃이랑 판매처 표에는 가평군 10,000원과 설악면 20,000원이 함께 표시됩니다. 이 금액은 최종 요금이 아닙니다. 행사명·홀·날짜와 선택 상품번호·상세주소를 전달하고 어느 행이 적용되는지 확인했나요? 행사장 반입 가능 여부도 주최자에게 확인하세요.',
      url='https://fwith.co.kr/shop/item.php?it_id=D144',
      question='어느 행이 적용되는지 확인했나요?'),
 dict(id='idong-home',region='경기도 포천시 이동면',location=('경기도','포천시','이동면'),purpose='transfer',productSkus=['D026','F055'],
      heading='이동면 배송비 표와 자택 수령일 확인',
      paragraph='꽃이랑 판매처 표에는 포천시 10,000원과 이동면 20,000원이 함께 표시됩니다. 두 금액 중 어느 것이 최종 적용되는지는 미확인입니다. 자택의 정확한 도로명·건물번호·동호수와 부재 시 연락 방법을 준비하고 적용 요금을 전화로 확인했나요?',
      url='https://fwith.co.kr/shop/item.php?it_id=D144',
      question='적용 요금을 전화로 확인했나요?')
]
pages=[]
for i,c in enumerate(cases,1):
 assert set(c['productSkus']).issubset(skus)
 pool=with_required_receipt_paths(spec['purposePools'][c['purpose']])
 assert sum(x.get('paragraph')==shared for x in pool['sections'])==1
 match=lookup(*c['location'])
 evidence=evidence_section(match)
 evidence['paragraph']=c['paragraph']
 evidence['heading']=c['heading']
 evidence['sourceUrl']=c['url']
 p={'id':c['id'],'number':i,'region':c['region'],'title':c['region']+' 화분 주문 선택 안내','pageType':'regional-detail','purpose':c['purpose'],
    'productSkus':c['productSkus'],'evidenceSections':[evidence]}
 p['purposePool']=pool
 pages.append(p)
rows=[]
for c,p in zip(cases,pages):
 pool={'%s'%p['purpose']:p['purposePool']}
 a=assemble(p,pool,products)
 body=a['intro']+'\n'+'\n'.join(x['heading']+' '+x['paragraph'] for x in a['sections'])
 html=render(site,p,pages,products,[],pool)
 # Keep the renderer's numbered URL contract and suppress links to non-existent
 # pages 4/5 in this three-page isolated preview (never change global renderer).
 html=re.sub(r'<a\\b[^>]*href="/(?:4|5)\\.html"[^>]*>.*?</a>', '', html, flags=re.S)
 html=re.sub(r'<a\\b[^>]*href="/(?:4|5)\\.html"[^>]*>', '', html)
 assert 'href="/4.html"' not in html and 'href="/5.html"' not in html
 for q in ('회사명과 새 부서, 건물 층·호실을 확인했나요?',
           '도로명주소와 건물번호, 동·호수를 확인했나요?',
           '행사 시작시각과 물품 반입 가능 시간을 확인했나요?',c['question']):
  assert q in body and q in html,(c['id'],q)
 assert html.count(shared)==1
 assert 'noindex' in html
 assert all('it_id='+sku in html for sku in c['productSkus'])
 assert '참고 원문 보기' in html
 (OUT/('index.html' if p['number']==1 else str(p['number'])+'.html')).write_text(html,encoding='utf-8')
 (OUT/(c['id']+'.txt')).write_text(body,encoding='utf-8')
 rows.append({'id':c['id'],'region':c['region'],'purpose':c['purpose'],'productSkus':c['productSkus'],'sourceUrl':c['url'],
              'filename':'index.html' if p['number']==1 else str(p['number'])+'.html','htmlBytes':len(html.encode()),'bodyChars':len(body),'allRecipientQuestions':True,'publicationApproved':False})
 (OUT/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('THREE_BUYER_DESIGNS',json.dumps(rows,ensure_ascii=False))
