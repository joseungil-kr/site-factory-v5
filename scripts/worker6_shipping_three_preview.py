"""Three-region private shipping display experiment; same purpose and products."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from worker6_shipping_render import lookup,evidence_section
SITE=ROOT/'sites/promotion-gift-plants'
examples=[('경기도','파주시','적성면'),('경기도','가평군','설악면'),('전라남도','강진군','대구면')]
pages=[];rows=[]
for i,(province,district,locality) in enumerate(examples,1):
    result=lookup(province,district,locality)
    pages.append({'id':f'w6-shipping-{i:02d}','number':i,'pageType':'regional-detail',
      'region':result['region'],'purpose':'promotion',
      'topic':'승진화분 주문','title':result['region']+' 승진화분 주문, 축하화분 당일 배달',
      'intro':'배송비 표기와 주문 절차','productSkus':['D144','D156'],
      'sections':[{'heading':'상품 선택','paragraph':'D144와 D156 상품 상세 비교'},
                  {'heading':'주문','paragraph':'상세 주소와 수령일 확인'}],
      'faq':[{'q':'배송비는?','a':'정확한 배송지를 전달해 확인합니다.'}],
      'evidenceSections':[evidence_section(result)]})
    rows.append(result)
(SITE/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(SITE/'regions.json').write_text(json.dumps({'source':'nationwide candidate locality ledger, not validated official address','regions':[{'name':p['region'],'code':None,'level':'locality'} for p in pages]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=ROOT/'reports/promotion-gift-plants/shipping-three'
out.mkdir(parents=True,exist_ok=True)
(out/'three-scenario-input.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'region':r['region'],'state':r['state'],'candidates':r['candidates']} for r in rows],ensure_ascii=False))
