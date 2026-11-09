"""Isolated five-page preview, reusing V5.1 plan and renderer. No deployment."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
source=json.loads((SITE/'core-five-seller-evidence.json').read_text(encoding='utf-8'))
spec=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
product_ids=['D144','D156','D152','D026']
assert {x['sku'] for x in source['sources']}==set(product_ids)
spec['purposePools']['home']={
 'productSkus':product_ids,
 'introductions':['승진·영전·일반 축하 선물과 당일 문의의 차이를 먼저 살펴보세요. 판매처에서 확인한 금전수 탁상용 D144와 포인세티아 소형 D156을 비교하고 목적별 안내에서 주문 순서를 선택할 수 있습니다.'],
 'sections':[
  {'slot':'choice','role':'required','heading':'목적별 안내를 먼저 선택','paragraph':'승진은 새 직함과 부서, 영전·전보는 새 근무지와 출근일, 일반 축하는 선물 메시지와 배치 장소, 당일 문의는 희망 시간과 실제 배송지를 먼저 정리하는 방식으로 구분합니다. 아래 페이지 번호 링크에서 해당 안내로 이동할 수 있습니다.'},
  {'slot':'choice','role':'required','heading':'판매처에서 확인한 두 상품','paragraph':'D152 레드카네이션 화분은 50,000원, D144 금전수 탁상용은 53,000원, D156 포인세티아 소형은 60,000원, D026 아로우카리아 대형은 90,000원으로 판매처에 표시됩니다. 네 상품 모두 선택옵션과 추가옵션이 0개이며 수량을 선택해 주문할 수 있습니다. 현재 재고와 화분의 실제 크기는 별도로 확인해야 합니다.'},
  {'slot':'order','role':'required','heading':'상품을 고른 뒤 주문하는 순서','paragraph':'상품 상세 링크에서 상품명·수량·가격을 확인한 다음 받는 분의 이름, 상세 주소, 수령 가능한 날짜를 준비합니다. 메시지 또는 리본 제공 방식은 판매처에 확인하고 배송비를 포함한 결제 금액을 검토한 후 주문합니다.'},
  {'slot':'order','role':'required','heading':'배송비와 당일 요청의 구분','paragraph':'판매처는 지역별 추가 배송비 표를 게시하지만 주소별 최종 요금과 당일 배송 가능 시간은 확정되어 있지 않습니다. 오늘 수령해야 한다면 1844-0644로 상품번호·배송지·희망 시간을 먼저 문의하세요.'}
 ],
 'faqs':[{'q':'가격과 옵션은 확인되었나요?','a':'D152 50,000원, D144 53,000원, D156 60,000원, D026 90,000원이며 네 상품의 선택·추가옵션은 0개로 표시됩니다.'},{'q':'당일 배송이 보장되나요?','a':'아닙니다. 주소와 희망 시간을 전달해 가능 여부를 먼저 확인해야 합니다.'}]
}
# Purpose guides have no geographic location; never inject fake region labels.
guide_introductions={
 'promotion':'승진 선물은 새 자리에서 바로 놓을 수 있는 형태인지가 먼저입니다. 금전수 탁상용 D144는 책상 선물 후보로, 포인세티아 소형 D156은 다른 분위기의 소형 선물 후보로 비교할 수 있습니다.',
 'transfer':'영전·전보 선물은 새 근무지에서 실제 수령할 사람이 있는 날짜를 기준으로 준비합니다. 포인세티아 소형 D156과 금전수 탁상용 D144의 상세를 비교하세요.',
 'congratulations':'축하화분을 고를 때는 받는 분의 선호와 놓을 자리를 먼저 생각해 보세요. D156 포인세티아 소형과 D144 금전수 탁상용의 상품 정보를 비교할 수 있습니다.',
 'sameDayInquiry':'오늘 축하화분을 보내려면 상품 선택보다 상세 주소와 수령 가능한 시간을 먼저 확인해야 합니다. D152·D144·D156·D026의 당일 배송 가능 여부는 주소와 접수 시점에 따라 별도 확인이 필요합니다.'
}
for purpose,intro in guide_introductions.items():
    spec['purposePools'][purpose]['introductions']=[intro]
# Replace overlapping generic selection sections with one substantive,
# purpose-specific buyer decision module. Do not append a fifth repetition.
decision_modules={
 'promotion':{
  'choice':('승진 선물 선택','금전수 탁상용 D144는 53,000원, 포인세티아 소형 D156은 60,000원입니다. 두 상품의 크기와 재고는 미확인이므로 수령 공간을 정한 뒤 상세상품에서 확인하세요.'),
  'message':('승진 축하 문구 예시','예시: “새로운 자리에서의 활약을 응원합니다.” 보내는 사람 표기 예: “○○회사 영업팀 일동”. 꽃이랑 경조사어도우미에 승진 문구 참고 이미지가 있으나, 리본 포함·문구 입력·무료 제공 여부는 확인되지 않았습니다. 참고: https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg'),
  'order':('승진 선물 주문 확인','새 직함, 받는 회사·부서·층·호실, 실제 수령 날짜와 담당자를 정리합니다. 상품별 최종 배송비·메시지 제공 여부를 확인한 뒤 결제합니다.')},
 'transfer':{
  'choice':('영전·전보 선물 선택','D156 포인세티아 소형 60,000원과 D144 금전수 탁상용 53,000원을 비교합니다. 새 근무지의 배치 공간과 실제 수령 가능한 날짜가 상품 선택의 기준입니다.'),
  'message':('영전 축하 문구 예시','예시: “새로운 자리에서 뜻하신 일을 이루시길 바랍니다.” 보내는 사람 표기 예: “○○회사 대표 홍길동”. 꽃이랑 문구 참고 이미지에 영전 축하 예시가 있으나, 주문 상품에 리본이 제공되는지는 미확인입니다. 참고: https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg'),
  'order':('영전·전보 수령 확인','발령일과 출근일을 구분하고 새 근무지의 정확한 주소·부서·대리 수령 담당자를 확인합니다. 이전 근무지로 잘못 보내지 않도록 배송지와 수령일을 결제 전에 점검합니다.')},
 'congratulations':{
  'choice':('축하화분과 예산 선택','확인된 상품은 D144 금전수 탁상용 53,000원, D156 포인세티아 소형 60,000원입니다. 상품명으로만 실제 크기나 식물관리 조건을 추정하지 말고 받는 분의 선호와 배치 장소를 확인하세요.'),
  'message':('축하 메시지 준비','예시: “새 출발을 진심으로 축하드립니다.” 보내는 사람 표기 예: “○○동호회 회원 일동”. 문구 예시는 직접 작성한 참고 문장으로, 판매처의 리본 제작 서비스나 무료 제공을 뜻하지 않습니다.'),
  'order':('축하 선물 주문 확인','받는 분의 이름, 축하 행사일, 정확한 수령 장소와 연락처를 확인합니다. 리본·메시지 선택 가능 여부는 상품 상세 또는 판매처 문의로 확인한 뒤 주문하세요.')},
 'sameDayInquiry':{
  'choice':('당일 문의 1단계 · 상품과 수령지 준비','문의할 정보: 상품번호 D144 또는 D156 / 수령지 시군구·읍면동·건물·층 / 받는 분 연락처 / 희망 수령 시각. 실제 재고와 주문 마감은 확인되지 않았습니다.'),
  'message':('당일 문의 2단계 · 판매처 답변 확인','판매처에 확인할 항목: 해당 주소 배송 가능 여부 / 접수 마감 / 예상 수령 가능 시간 / 지역 추가 배송비와 최종 결제금액 / 부재 시 수령 방법. 답변이 확정되기 전에는 당일 도착을 전제로 결제하지 마세요.'),
  'order':('당일 문의 3단계 · 결제 판단','전화 1844-0644로 문의 결과를 확인하고 상품 상세의 수량·옵션·금액을 재확인합니다. 배송 가능 여부와 시간·요금에 대한 판매처 답변을 받기 전에는 주문을 진행하지 않습니다.')}
}
for purpose,modules in decision_modules.items():
    pool=spec['purposePools'][purpose]
    # One module per independent job: choice, message, transaction.
    # Preserve V5.1 slots without multiplying repetitive generic paragraphs.
    pool['sections']=[
      {'slot':'choice','role':'required','heading':modules['choice'][0],'paragraph':modules['choice'][1]},
      {'slot':'choice','role':'required','heading':modules['message'][0],'paragraph':modules['message'][1]},
      {'slot':'order','role':'required','heading':modules['order'][0],'paragraph':modules['order'][1]}]
    pool['faqs']=[{'q':'당일 배송이 보장되나요?','a':'배송 가능 여부와 도착 시간은 판매처에 확인해야 합니다.'},
                  {'q':'리본·메시지가 제공되나요?','a':'참고 문구가 공개되어 있어도 해당 상품의 제공 여부와 입력 방법은 별도 확인해야 합니다.'}]
# Product catalog is shared by four guides; role-specific selection order is
# based on confirmed name/price only, never dimensions or availability.
for purpose in ('promotion','transfer','congratulations','sameDayInquiry'):
    spec['purposePools'][purpose]['productSkus']=product_ids
spec['purposePools']['home']['introductions']=['승진·영전·축하화분을 5만·6만·9만 원대에서 비교합니다. 꽃이랑에서 확인한 D152 레드카네이션 화분 50,000원, D144 금전수 탁상용 53,000원, D156 포인세티아 소형 60,000원, D026 아로우카리아 대형 90,000원 중 목적별 안내를 선택하세요.']
# Replace only product-selection paragraphs; keep message and order separate.
choice_copy={
 'promotion':'5만 원대 D144 금전수 탁상용(53,000원)과 D152 레드카네이션 화분(50,000원), 6만 원 D156 포인세티아 소형, 9만 원 D026 아로우카리아 대형을 비교하세요. 탁상용·소형·대형은 판매자 상품명 표기이며 실제 치수와 재고는 확인되지 않았습니다.',
 'transfer':'새 근무지의 배치 장소에 따라 D144 탁상용 53,000원, D156 소형 60,000원, D026 대형 90,000원, D152 화분 50,000원을 비교합니다. 상품명만으로 실제 크기나 수령 가능 여부를 확정하지 마세요.',
 'congratulations':'예산 5만 원대 D152 레드카네이션 화분 50,000원·D144 금전수 탁상용 53,000원, 6만 원 D156 포인세티아 소형, 9만 원 D026 아로우카리아 대형을 비교합니다. 식물 종류·크기·배송 가능 여부는 주문 전에 확인합니다.',
 'sameDayInquiry':'후보 상품은 D152 50,000원, D144 53,000원, D156 60,000원, D026 90,000원입니다. 오늘 배송 가능 상품은 확인되지 않았으므로 네 상품 중 선택한 번호와 정확한 배송지·희망 시간을 판매처에 전달합니다.'
}
for purpose,copy in choice_copy.items():
    spec['purposePools'][purpose]['sections'][0]['paragraph']=copy
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
