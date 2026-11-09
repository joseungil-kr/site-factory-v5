"""Isolated five-page preview, reusing V5.1 plan and renderer. No deployment."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
source=json.loads((SITE/'core-five-seller-evidence.json').read_text(encoding='utf-8'))
spec=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
product_ids=['D144','D156']
assert {x['sku'] for x in source['sources']}==set(product_ids)
spec['purposePools']['home']={
 'productSkus':product_ids,
 'introductions':['승진·영전·일반 축하 선물과 당일 문의의 차이를 먼저 살펴보세요. 판매처에서 확인한 금전수 탁상용 D144와 포인세티아 소형 D156을 비교하고 목적별 안내에서 주문 순서를 선택할 수 있습니다.'],
 'sections':[
  {'slot':'choice','role':'required','heading':'목적별 안내를 먼저 선택','paragraph':'승진은 새 직함과 부서, 영전·전보는 새 근무지와 출근일, 일반 축하는 선물 메시지와 배치 장소, 당일 문의는 희망 시간과 실제 배송지를 먼저 정리하는 방식으로 구분합니다. 아래 페이지 번호 링크에서 해당 안내로 이동할 수 있습니다.'},
  {'slot':'choice','role':'required','heading':'판매처에서 확인한 두 상품','paragraph':'D144 금전수 탁상용은 53,000원, D156 포인세티아 소형은 60,000원으로 판매처에 표시됩니다. 두 상품 모두 선택옵션과 추가옵션이 0개이며 수량을 선택해 바로구매할 수 있습니다. 현재 재고와 화분의 실제 크기는 별도로 확인해야 합니다.'},
  {'slot':'order','role':'required','heading':'상품을 고른 뒤 주문하는 순서','paragraph':'상품 상세 링크에서 상품명·수량·가격을 확인한 다음 받는 분의 이름, 상세 주소, 수령 가능한 날짜를 준비합니다. 메시지 또는 리본 제공 방식은 판매처에 확인하고 배송비를 포함한 결제 금액을 검토한 후 주문합니다.'},
  {'slot':'order','role':'required','heading':'배송비와 당일 요청의 구분','paragraph':'판매처는 지역별 추가 배송비 표를 게시하지만 주소별 최종 요금과 당일 배송 가능 시간은 확정되어 있지 않습니다. 오늘 수령해야 한다면 1844-0644로 상품번호·배송지·희망 시간을 먼저 문의하세요.'}
 ],
 'faqs':[{'q':'가격과 옵션은 확인되었나요?','a':'D144 53,000원, D156 60,000원이며 두 상품의 선택·추가옵션은 0개로 표시됩니다.'},{'q':'당일 배송이 보장되나요?','a':'아닙니다. 주소와 희망 시간을 전달해 가능 여부를 먼저 확인해야 합니다.'}]
}
# Purpose guides have no geographic location; never inject fake region labels.
guide_introductions={
 'promotion':'승진 선물은 새 자리에서 바로 놓을 수 있는 형태인지가 먼저입니다. 금전수 탁상용 D144는 책상 선물 후보로, 포인세티아 소형 D156은 다른 분위기의 소형 선물 후보로 비교할 수 있습니다.',
 'transfer':'영전·전보 선물은 새 근무지에서 실제 수령할 사람이 있는 날짜를 기준으로 준비합니다. 포인세티아 소형 D156과 금전수 탁상용 D144의 상세를 비교하세요.',
 'congratulations':'축하화분을 고를 때는 받는 분의 선호와 놓을 자리를 먼저 생각해 보세요. D156 포인세티아 소형과 D144 금전수 탁상용의 상품 정보를 비교할 수 있습니다.',
 'sameDayInquiry':'오늘 축하화분을 보내려면 상품 선택보다 상세 주소와 수령 가능한 시간을 먼저 확인해야 합니다. D144와 D156의 당일 배송 가능 여부는 주소와 접수 시점에 따라 별도 확인이 필요합니다.'
}
for purpose,intro in guide_introductions.items():
    spec['purposePools'][purpose]['introductions']=[intro]
# Real decision modules from observed competitor guide patterns, written for
# verified own products only. Do not imply seller supports unverified ribbon options.
decision_modules={
 'promotion':('승진 선물의 예산과 수령 자리','5만 원대 D144 금전수 탁상용과 6만 원 D156 포인세티아 소형을 먼저 비교합니다. 받는 분의 새 직함과 책상·공용공간 중 실제 배치할 장소를 확인하고, 상품 크기는 판매처에 문의합니다.'),
 'transfer':('영전·전보에서 먼저 확인할 것','발령일과 새 근무지에 실제 출근하는 날짜가 다를 수 있습니다. 이전 부서가 아니라 새 수령 주소와 담당자 연락처를 확인한 다음 D144 또는 D156의 배송 가능 여부를 문의합니다.'),
 'congratulations':('축하 메시지와 보내는 사람 표기','축하 문구는 받는 사람과의 관계에 맞게 직접 작성합니다. 보내는 사람의 회사명·부서·이름을 정확히 준비하고, 리본이나 메시지 제공 여부 및 입력 방식은 상품 주문 전에 판매처에 확인합니다.'),
 'sameDayInquiry':('당일 요청을 위한 문의 순서','희망 배송지의 시군구·읍면동과 상세 건물, D144 또는 D156 상품번호, 희망 수령 시각, 수령 담당자 연락처를 준비합니다. 배송 가능 여부와 최종 배송비가 확인된 다음 결제 여부를 결정합니다.')
}
for purpose,(heading,paragraph) in decision_modules.items():
    spec['purposePools'][purpose]['sections'].append({'slot':'choice','role':'required','heading':heading,'paragraph':paragraph})
spec['pageTypes']=['homepage','purpose-guide']
spec['targetPageCount']=5
spec['publishPolicy']['mode']='preview'
(SITE/'site-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
purposes=[('home','전국 승진·영전·축하화분 안내','승진·영전·축하화분 주문 안내'),
 ('promotion','승진 선물 안내','승진 축하화분 선택과 주문'),
 ('transfer','영전·전보 선물 안내','영전·전보 화분과 새 근무지 수령'),
 ('congratulations','일반 축하 선물 안내','축하화분과 메시지 선택'),
 ('sameDayInquiry','당일 배송 문의 안내','당일 축하화분 주문 가능 여부 확인')]
pages=[]
for i,(purpose,region,title) in enumerate(purposes,1):
    pages.append({'id':f'w6-core-{i:02d}','number':i,'region':region,'pageType':'purpose-guide','purpose':purpose,
      'title':title,'topic':purpose,'intro':'상품 선택과 수령 정보를 비교합니다.',
      'sections':[{'heading':'상품 선택','paragraph':'상품 상세를 확인합니다.'},{'heading':'주문 순서','paragraph':'배송지와 수령일을 확인합니다.'}],
      'productSkus':product_ids if purpose in ('home','promotion','sameDayInquiry') else list(reversed(product_ids)),
      'faq':[{'q':'주문 방법은?','a':'상품 상세 링크에서 확인합니다.'}]})
(SITE/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(SITE/'regions.json').write_text(json.dumps({'source':'purpose-based guides, not locality delivery evidence','regions':[{'name':p['region'],'code':None,'level':'purpose-guide'} for p in pages]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
site=json.loads((SITE/'site.json').read_text(encoding='utf-8'))
site['navigation']=[{'label':'홈','href':'/'},{'label':'승진','href':'/2.html'},{'label':'영전·전보','href':'/3.html'},{'label':'축하','href':'/4.html'},{'label':'당일 문의','href':'/5.html'}]
(SITE/'site.json').write_text(json.dumps(site,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('CORE_FIVE_INPUT_OK',[(p['number'],p['purpose'],p['title']) for p in pages])
