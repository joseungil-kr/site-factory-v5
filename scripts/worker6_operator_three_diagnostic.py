"""Private 3-region diagnostic HTML, not a publishable or audit-passing build."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from worker6_shipping_render import lookup,evidence_section
from v5.purpose_render import render,assemble
from v5.audit import similarity
SITE=ROOT/'sites/promotion-gift-plants'
out=ROOT/'reports/promotion-gift-plants/operator-three'
out.mkdir(parents=True,exist_ok=True)
site=json.loads((SITE/'site.json').read_text(encoding='utf-8'))
site['publishEnabled']=False
site['domain']=None
products=json.loads((SITE/'products.json').read_text(encoding='utf-8'))
seller=json.loads((SITE/'core-five-seller-evidence.json').read_text(encoding='utf-8'))
operator=json.loads((SITE/'operator-service-confirmation-20261109.json').read_text(encoding='utf-8'))
spec=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
sku=[x['sku'] for x in products]
product_copy=' / '.join(f"{p['name']} {p['referencePrice']:,}원 ({p['sku']})" for p in sorted(products,key=lambda x:x['referencePrice']))
operator_copy=('사업자 운영확인에 따르면 지역별 지점에서 발송하며 전국 당일배송 서비스를 제공합니다. '
 '주문전화 1844-0644 접수 안내 시간은 08:00~23:00이고, 배송 가능 시간대는 지역 꽃집 영업시간에 따른 06:00~20:00입니다. '
 '이는 특정 주문의 당일 도착 보장이 아니며 접수 마감·재고·실제 배송 가능 여부·최종 배송비는 전화로 확인해야 합니다. '
 '특히 23시 전화 주문이 그날 배송된다는 뜻은 아닙니다.')
modules=json.loads((SITE/'customer-decision-modules-20261109.json').read_text(encoding='utf-8'))
module_by_id={x['id']:x for x in modules['modules']}
common_sections=[
 {'slot':'order','role':'required','heading':'전국 공통 주문·배송 운영안내','paragraph':operator_copy}]
common_faq=[
 {'q':'전국 당일배송 서비스를 이용할 수 있나요?','a':'사업자 운영확인상 전국 당일배송 서비스가 가능하지만 개별 주문의 실제 도착과 마감은 전화 확인이 필요합니다.'},
 {'q':'주문전화와 배송 가능 시간은 같은가요?','a':'전화 주문 08~23시, 배송 가능 시간대 06~20시로 구분하며 지역 꽃집 운영시간에 따릅니다.'}]
def module_section(module_id,slot):
 m=module_by_id[module_id]
 return {'slot':slot,'role':'required','heading':m['heading'],'paragraph':m['body'],
         **({'sourceUrl':m['sourceUrl']} if 'sourceUrl' in m else {})}
def scenario_pool(state):
 config=next(x for x in modules['scenarioChoices'] if x['case']==state)
 return {'productSkus':sku,
 'introductions':['승진 축하화분 주문에서 상품 예산, 메시지, 실제 수령상황과 지역별 추가 배송비 표를 나누어 확인합니다. 아래 수령 사례는 선택 가능한 상황이지 지역별 시설 현황이 아닙니다.'],
 'sections':[
  module_section(config['primary'],'choice'),
  module_section(config['recipient'],'choice'),
  module_section('order-call-timing','order'),
  module_section(config['fee'],'order')],
 'faqs':common_faq}
cases=[('경기도','파주시','적성면'),('경기도','가평군','설악면'),('전라남도','강진군','대구면')]
pages=[];records=[]
for i,(province,district,locality) in enumerate(cases,1):
 match=lookup(province,district,locality)
 page={'id':f'worker6-operator-region-{i}','number':i,'region':match['region'],
 'pageType':'regional-detail','purpose':'promotion','title':match['region']+' 승진화분 주문 안내',
 'productSkus':sku,'evidenceSections':[evidence_section(match)]}
 page['purposePool']=scenario_pool(match['state'])
 pages.append(page)
 records.append({'region':match['region'],'state':match['state'],'sourceRows':[x['row'] for x in match['candidates']]})
texts=[]
for page in pages:
 pools={'promotion':page['purposePool']}
 assembled=assemble(page,pools,products)
 texts.append({'region':page['region'],'text':assembled['intro']+'\n'+'\n'.join(x['heading']+' '+x['paragraph'] for x in assembled['sections'])})
 html=render(site,page,pages,products,[],pools)
 assert 'noindex' in html
 assert all('it_id='+x in html for x in sku)
 assert '08:00~23:00' in html and '06:00~20:00' in html
 assert module_by_id['order-call-timing']['body'] in html
 assert '참고 원문 보기' in html
 (out/f'{page["number"]}.html').write_text(html,encoding='utf-8')
pairs=[{'pair':[texts[i]['region'],texts[j]['region']],'similarity':similarity(texts[i]['text'],texts[j]['text'])}
 for i in range(3) for j in range(i+1,3)]
report={'source':'user provided operator confirmation, not external verification',
 'qualityGateThresholdExclusive':0.49,'auditPassed':all(p['similarity']<0.49 for p in pairs),
 'pairs':pairs,'regions':records,'bodies':texts,'publicationApproved':False,
 'scenarioEvidenceIsLocalFact':False,'selectionRule':'buyer decision scenario, not factual regional prevalence'}
(out/'diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('THREE_DIAGNOSTIC',json.dumps({'pairs':pairs,'auditPassed':report['auditPassed']},ensure_ascii=False))
