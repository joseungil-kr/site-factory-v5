"""Private six-region same-purpose controlled HTML, not a publishable build."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from worker6_shipping_render import lookup,evidence_section
from v5.purpose_render import render,assemble
from v5.audit import similarity
from worker6_core_five_preview import generate_inputs,operator_policy
from v5 import markup
import re, shutil
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
# Reuse the exact real promotion buyer-decision pool and shared operator source.
source=json.loads((SITE/'core-five-seller-evidence.json').read_text(encoding='utf-8'))
base_spec,_,_,_=generate_inputs(source,spec,site,operator_source=operator)
shared=operator_policy(operator)
promotion=base_spec['purposePools']['promotion']
assert sum(x.get('paragraph')==shared for x in promotion['sections'])==1
cases=[('경기도','파주시','적성면'),('경기도','양평군','단월면'),
       ('경기도','가평군','설악면'),('경기도','포천시','이동면'),
       ('전라남도','강진군','대구면'),('전라남도','영광군','법성면')]
pages=[];records=[]
for i,(province,district,locality) in enumerate(cases,1):
 match=lookup(province,district,locality)
 page={'id':f'worker6-operator-region-{i}','number':i,'region':match['region'],
 'pageType':'regional-detail','purpose':'promotion','title':match['region']+' 승진화분 주문 안내',
 'productSkus':sku,'evidenceSections':[evidence_section(match)]}
 page['purposePool']=promotion
 pages.append(page)
 records.append({'region':match['region'],'state':match['state'],'sourceRows':[x['row'] for x in match['candidates']]})
texts=[]
normalized=[]
consumer_banned=('지역 후보 원장','원문 행이 없다고 판단할 수 없습니다','지역별 시설 현황이 아닙니다')
for page in pages:
 pools={'promotion':page['purposePool']}
 assembled=assemble(page,pools,products)
 body=assembled['intro']+'\n'+'\n'.join(x['heading']+' '+x['paragraph'] for x in assembled['sections'])
 texts.append({'region':page['region'],'text':body})
 # Remove place-name tokens only for an additional diagnostic, not to alter output.
 norm=body
 for other in pages:
  for token in other['region'].split():norm=norm.replace(token,'[지역]')
 normalized.append(norm)
 assert not any(x in body for x in consumer_banned)
 html=render(site,page,pages,products,[],pools)
 assert 'noindex' in html
 assert all('it_id='+x in html for x in sku)
 assert '08:00~23:00' in html and '06:00~20:00' in html
 assert html.count(shared)==1
 assert not any(x in html for x in consumer_banned)
 assert '참고 원문 보기' in html
 assert all(html.count('data-product-sku="'+x+'"')==1 for x in sku)
 (out/f'{page["number"]}.html').write_text(html,encoding='utf-8')
pairs=[{'pair':[texts[i]['region'],texts[j]['region']],'similarity':similarity(texts[i]['text'],texts[j]['text'])}
 for i in range(len(texts)) for j in range(i+1,len(texts))]
normalizedPairs=[{'pair':[texts[i]['region'],texts[j]['region']],'similarity':similarity(normalized[i],normalized[j])} for i in range(len(texts)) for j in range(i+1,len(texts))]
report={'source':'user provided operator confirmation, not external verification',
 'qualityGateThresholdExclusive':0.49,'auditPassed':all(p['similarity']<0.49 for p in pairs),
 'pairs':pairs,'nameRemovedPairs':normalizedPairs,'regions':records,'bodies':texts,'publicationApproved':False,
 'failedPairs':[p for p in pairs if p['similarity']>=0.49],
 'scenarioEvidenceIsLocalFact':False,'selectionRule':'identical real promotion pool and six SKUs; only evidenced seller fee row differs'}
(out/'diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SIX_DIAGNOSTIC',json.dumps({'pairs':pairs,'nameRemovedPairs':normalizedPairs,'auditPassed':report['auditPassed']},ensure_ascii=False))
