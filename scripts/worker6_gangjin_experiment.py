"""Isolated Gangjin two-document experiment using the unchanged V5.1 builder."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
site=root/'sites/promotion-gift-plants'
research=json.loads((site/'gangjin-two-page-experiment.json').read_text(encoding='utf-8'))
pages=[]
for i,record in enumerate(research['pages'],1):
    purpose=record['purpose']
    p={'id':record['id'],'number':i,'region':record['region'],'purpose':purpose,
       'topic':'승진 축하화분' if purpose=='promotion' else '영전·전보 축하화분',
       'title':record['region']+' 승진화분 주문, 축하화분 당일 배달',
       'intro':'원문에 근거한 지역 수령 정보',
       'sections':[{'heading':'선택','paragraph':'실제 상품 비교'},
                   {'heading':'주문','paragraph':'정확한 수령지 확인'}],
       'productSkus':record['productSkus'],'evidenceSections':record['evidenceSections'],
       'faq':[{'q':'배송 가능한가요?','a':'배송지로 확인하세요.'}]}
    pages.append(p)
(site/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(site/'regions.json').write_text(json.dumps({'source':'Gangjin official two-location evidence experiment','regions':[{'name':p['region'],'code':None,'level':'myeon'} for p in pages]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('EXPERIMENT_INPUT_OK',len(pages),[p['region'] for p in pages])
