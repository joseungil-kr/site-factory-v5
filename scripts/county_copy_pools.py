"""Customer-purpose editorial pools for the isolated 82-county V5.1 trial.

No locality facts beyond official county name/province are inferred.
Variations are different purchasing questions, not shuffled adjectives.
"""
from __future__ import annotations

# Each question is answerable from the real SKU catalogue or a purchaser's
# actual receiving-place data, without inventing a local branch or delivery time.
INTRO={
 'budget':[
  '{county}으로 근조화환을 보낼 때 B201·B202·B205·B206의 표시 가격을 비교할 수 있습니다.',
  '{county} 근조화환을 예산에 맞춰 고르신다면 59,000원대 두 상품과 상위 표시가 상품을 나눠 살펴볼 수 있습니다.',
  '{county} 근조화환 주문에서는 상품가뿐 아니라 수령지에 적용되는 배송비를 함께 확인하는 것이 중요합니다.',
  '{province} {county} 수령지에 보내는 근조화환은 실상품 링크의 가격과 결제 직전 총액을 구분해 비교할 수 있습니다.',
  '근조화환 B201과 B202는 기준가가 같으며, {county} 주문 시 실제 상품 구성을 비교할 수 있습니다.',
  '{county} 지역 근조화환은 B205와 B206을 포함해 네 개의 검증된 상품 주문 링크를 제공하고 있습니다.'
 ],
 'venue':[
  '{county}의 장례식장으로 근조화환을 보낼 때는 시설명과 정확한 주소가 주문 확인의 출발점입니다.',
  '{province} {county}으로 보내는 근조화환은 장례식장 빈소와 수령 시간을 기준으로 주문 가능 여부를 상담할 수 있습니다.',
  '장례식장에 화환을 보내기 전 시설의 3단 화환 반입 안내를 확인하는 과정이 필요할 수 있습니다. {county}의 특정 시설에 대한 허용 여부는 별도 확인 사항입니다.',
  '{county}에서 수령하는 화환을 고를 때 상품가와 시설 반입 조건을 함께 살펴볼 수 있습니다.',
  '{county} 지역의 장례식장 수령을 준비한다면 이름이 비슷한 시설 사이에서 주소와 빈소를 구분하는 것이 중요합니다.',
  '근조화환의 수령 시설과 배송 주소를 준비하시면 {county} 주문 문의 시 실제 접수 조건을 확인할 수 있습니다.'
 ],
 'ribbon':[
  '{county}에 근조화환을 보내면서 조의 문구와 보내는 이름을 함께 정리할 수 있습니다.',
  '{county} 수령지에 전달할 근조화환의 리본에는 고인을 추모하는 문구와 보내는 분의 명의를 표시합니다.',
  '{province} {county} 근조화환 주문 전에는 상품 선택과 별도로 리본 문구의 표기를 확인할 수 있습니다.',
  '같은 표시가의 B201과 B202 중 어떤 상품을 고르든 {county} 화환 리본에는 보내는 이름이 정확하게 들어가야 합니다.',
  '{county} 근조화환 리본 문구와 상품 유형을 함께 정리한 뒤 주문 화면으로 이동할 수 있습니다.',
  '조의 문구를 정하셨다면 {county}으로 전달할 화환의 받는 시설과 보내는 분 명의를 함께 확인할 수 있습니다.'
 ]
}
SLOTS={
 'choice':[
  ('상품별 표시가 비교','근조 B201과 B202의 상품가는 각각 59,000원이며 B205는 109,000원, B206은 149,000원으로 기록돼 있습니다. 꽃 수량·규격은 상품별 상세정보에서 확인할 수 있습니다.'),
  ('같은 가격의 두 상품','B201과 B202는 모두 59,000원입니다. 두 상품 중 하나를 고르기 전에 판매처 상세에서 구성 안내와 주문 옵션을 비교할 수 있습니다.'),
  ('추가 예산을 사용하는 경우','59,000원 기준의 B201·B202에서 109,000원의 B205로 바꾸면 기준가 차이는 50,000원입니다. 구성과 크기 차이는 상품 상세로 확인하는 것이 정확합니다.'),
  ('상위 표시가 선택','B206은 149,000원으로 기록돼 있으며 B205의 109,000원과 40,000원 차이가 있습니다. 실제 꽃의 종류와 크기가 그 차이와 같다는 뜻은 아닙니다.'),
  ('근조 상품 네 가지','판매처 B201, B202, B205, B206을 각각 확인할 수 있습니다. 이름이 비슷해도 상품코드로 구분해 주문하면 원하는 제품을 명확히 전달할 수 있습니다.'),
  ('결제 예산을 정하는 기준','상품의 표시가격은 59,000원부터 149,000원까지이며 수령 시설에 따른 배송비와 선택 옵션이 추가될 수 있습니다. 합계는 실제 주문서에서 확인할 수 있습니다.'),
  ('동일 용도 비교','장례식장으로 보내는 근조화환 중 상품번호별 사진과 규격, 가격을 비교해 보세요. 선택한 상품의 주문 옵션에서 리본과 수령 정보를 입력할 수 있습니다.'),
  ('최종금액과 표시가','예를 들어 59,000원 상품을 선택하더라도 확정 총액은 배송지 확인이 필요합니다. 읍·면별 적용 금액은 수령지 정보를 입력한 뒤 주문서에서 확인할 수 있습니다.')
 ],
 'order':[
  ('시설명 확인','{county}에서 받는 장례식장 이름과 실제 주소를 함께 전달하면 같은 이름의 다른 장소로 접수되는 착오를 줄일 수 있습니다. 빈소 번호가 있는 경우 주문 정보에 포함할 수 있습니다.'),
  ('수령 날짜 전달','{county}으로 화환을 보낼 희망 날짜와 시간대를 판매처에 알려주시면 해당 주소의 주문 접수 가능 여부와 배송 일정을 안내받을 수 있습니다.'),
  ('빈소 번호 확인','장례식장에 빈소가 지정된 경우 시설명 외에 빈소 번호와 수령 정보를 정확하게 준비할 수 있습니다. 시설의 반입 절차가 있다면 접수 전에 확인합니다.'),
  ('배송 주소 입력','수령 장소의 도로명 주소와 건물명을 주문처에 전달해 배송비 적용 범위를 확인할 수 있습니다. 같은 군 안에서도 읍·면별 배송 조건은 달라질 수 있어 수령 주소가 필요합니다.'),
  ('주문서에 기재할 정보','상품코드, 받는 시설명, 정확한 주소, 희망 날짜, 조의 문구와 보내는 명의를 차례로 입력하면 주문 내용을 구분하기 쉽습니다.'),
  ('시설 반입 규정','일부 장례식장에서는 화환 설치 형태나 반입 위치에 관한 별도 규정을 운영할 수 있습니다. {county}의 개별 시설에 적용되는 최신 조건은 주문 시 확인할 수 있습니다.'),
  ('대체 형태 문의','수령 시설에 3단 화환 반입 제한이 있다면 판매처에서 실제 주문 가능한 대체 형태를 상담받을 수 있습니다. 대체 상품을 실제로 주문할 수 있는지는 판매처 상품 정보와 상담을 통해 확인할 수 있습니다.'),
  ('주문에 필요한 수령 정보','장례식장명·도로명 주소·빈소, 희망 전달일을 준비해 주세요. 상품을 고른 뒤 판매처 주문 화면에 입력하면 실제 접수 가능 여부를 확인할 수 있습니다.')
 ],
 'ribbon':[
  ('조의 문구 입력','근조 리본에 적는 조의 문구와 보내는 사람 또는 단체의 명칭을 각각 확인할 수 있습니다. 제작에 들어가기 전 표기와 맞춤법을 점검하면 좋습니다.'),
  ('보내는 명의 표기','단체에서 보내는 근조화환이면 회사명 또는 모임명을 정확하게 입력할 수 있습니다. 개인이라면 이름과 필요시 관계를 구분해 전달할 수 있습니다.'),
  ('문구와 행사 목적','근조 상품에는 조의 목적에 맞는 리본 문구를 사용하며 축하 문구와 혼용하지 않습니다. 실제 입력 가능한 글자 수는 주문 옵션에서 확인할 수 있습니다.'),
  ('리본 비용 안내','리본이 상품가에 기본 포함되는지와 추가 인쇄 비용이 있는지는 상품별 주문 조건에 따라 확인합니다. 리본 포함 여부와 인쇄 옵션의 실제 비용은 주문 화면에서 확인할 수 있습니다.'),
  ('리본과 빈소 정보 구분','리본에는 조의 문구와 보내는 이름을, 수령지에는 장례식장명과 빈소를 구분해 입력해 주세요. 화환 설치 위치는 시설 안내에 따라 확인할 수 있습니다.'),
  ('조의 문구 예시','근조 리본에는 “삼가 고인의 명복을 빕니다” 또는 “깊은 애도를 표합니다”와 같은 조의 문구를 사용할 수 있습니다. 보내는 분의 이름은 주문 옵션에서 별도로 입력합니다.'),
  ('발신인과 수령인 구분','리본에 적을 보내는 사람의 명의와 수령 시설에 전달할 연락처는 목적이 다릅니다. 두 정보를 분리해 작성할 수 있습니다.'),
  ('리본 제작 요청','리본 문구를 지정할 때 단체명, 조의 문구, 배송할 장례식장을 한 번에 정리할 수 있습니다. 실제 추가 옵션은 주문처에서 확인합니다.')
 ],
 'delivery':[
  ('주문 시 배송비 확인','판매처는 B201·B202·B205·B206의 배송비를 주문 단계에서 결제하도록 안내합니다. 군 단위 안내가 있더라도 읍·면 상세 주소에 따라 추가비용이 달라질 수 있습니다.'),
  ('배송비 확인 경로','수령할 장례식장의 정확한 주소와 선택한 상품번호를 준비해 주세요. 실제 배송비와 주문 총액은 판매처 주문 화면에서 확인할 수 있습니다.'),
  ('결제 화면 총액','상품 표시가는 배송비를 포함한 최종 결제금액과 다를 수 있습니다. 받는 시설·주소를 입력한 뒤 배송비와 리본 옵션 금액이 반영된 총액을 확인할 수 있습니다.'),
  ('희망 도착 시간','배송 시간을 지정해도 실제 접수·도착 일정은 지역과 주문 시점에 따라 달라집니다. 판매처에 날짜와 시간을 전달해 가능한 일정을 확인할 수 있습니다.'),
  ('배송료 예외 확인','읍·면과 실제 장례식장 주소를 정리해 주세요. 선택한 상품의 배송비는 판매처 주문 화면에서 정확한 수령지를 기준으로 확인할 수 있습니다.'),
  ('배송지에 맞춘 상담','{county}의 수령 시설명과 도로명 주소를 전달하면 배송 가능 여부, 추가 배송료와 접수 가능한 시간대를 함께 안내받을 수 있습니다.'),
  ('예산과 별도 비용','상품가격 외에 배송료와 리본 선택 옵션이 추가되는지 주문 화면에서 살펴보세요. 받는 주소를 지정하면 결제 전 총액을 확인할 수 있습니다.'),
  ('배송 관련 주문 문의','해당 시설명과 희망 날짜를 알려주시면 판매처에서 접수 가능 여부와 요금 적용 조건을 안내받을 수 있습니다. 실제 적용 요금은 판매처가 받는 곳 주소를 확인한 뒤 안내합니다.')
 ],
 'information':[
  ('상품번호로 재확인','주문 전 B201, B202, B205, B206 중 선택한 상품번호를 확인해 판매처에 전달하면 비슷한 상품명으로 인한 혼동을 줄일 수 있습니다.'),
  ('실물 구성 확인','꽃 품종과 수량, 높이·너비는 상품별 상세 설명과 판매처 주문 옵션에서 비교할 수 있습니다.'),
  ('상품 상세 안내','상품 카드의 판매처 링크에서 꽃 구성과 규격, 옵션을 살펴볼 수 있습니다. 원하는 상품번호를 확인해 주문할 수 있습니다.'),
  ('수령 정보와 결제','받는 장례식장과 빈소 정보, 연락 가능한 방법과 희망 날짜를 준비한 다음 주문서에서 상품과 배송비를 확인할 수 있습니다.'),
  ('리본 문구 확인 경로','주문 과정에서 리본의 조의 문구와 보내는 분 이름을 입력할 수 있습니다. 입력한 내용을 판매처 주문내역에서 다시 검토할 수 있습니다.'),
  ('가격 확인 시점','상품가격은 2026-11-07 판매처 확인 기록을 기준으로 표시합니다. 이후 가격 변경이나 실제 재고는 현재 주문 화면의 안내를 기준으로 판단할 수 있습니다.'),
  ('선택하지 않은 상품','B201과 B202의 기준가가 같더라도 실물 구성이나 주문 옵션이 동일하다는 뜻은 아닙니다. 두 상품 상세를 따로 확인할 수 있습니다.'),
  ('상품을 고른 뒤 확인할 것','원하시는 화환의 사진과 규격을 판매처에서 비교하고 받는 장례식장 주소를 입력하면, 적용 배송비가 포함된 결제금액을 확인할 수 있습니다.')
 ]
}
def _purpose(title):
 return 'budget' if '예산' in title else 'venue' if '수령' in title or '장례식장' in title else 'ribbon'
def purpose_intros(title,intro):
 return [intro]+INTRO[_purpose(title)]
def purpose_sections(title,choice,delivery,extra):
 fields={
 'choice':('상품 선택',choice),
 'order':('수령시설·주문 정보','{county}의 장례식장명과 상세 주소, 희망 도착일을 판매처에 전달하면 접수 가능 여부와 실제 요금을 확인할 수 있습니다.'),
 'ribbon':('리본 문구와 보내는 이름','조의 문구와 보내는 분의 이름 또는 단체명을 함께 확인할 수 있습니다. 리본 포함 여부는 실제 상품 옵션에 따릅니다.'),
 'delivery':('배송비 및 결제총액',delivery),
 'information':('상품 확인과 주문 문의',extra)
 }
 result=[]
 for slot,(h,p) in fields.items():
  result.append({'slot':slot,'heading':h,'paragraph':p})
  result.extend({'slot':slot,'heading':heading,'paragraph':paragraph} for heading,paragraph in SLOTS[slot])
 return result

# Distinct purchase decisions, never unverified locality facts.
# These additional slots are compulsory per purpose; they cannot be chosen away
# by hashed variants. A county page carries only the products for its decision.
INTENTS=[
 ('budget-entry','budget',['B201','B202'],'기본 주문 정보',
  '판매처에는 B201이 근조 3단 화환, B202가 근조 3단 화환로 등록돼 있습니다. 각 상품 카드에서 해당 상품의 주문 상세로 이동할 수 있습니다.',
  '가격 외 확인 항목','상품을 고른 뒤에는 수령 장례식장명·빈소·희망 날짜와 리본에 적을 이름을 준비하면 주문 내용을 정확하게 입력하기 편리합니다.'),
 ('budget-upgrade','budget',['B201','B205'],'표시가 5만 원 차이 비교',
  'B201과 B205는 서로 다른 가격대의 상품입니다. 표시가격만으로 꽃 수량과 크기를 판단하기보다 각 판매처 상세의 구성과 규격을 비교해 주세요.',
  '예산 결정의 기준','선택한 상품의 주문 화면에서 배송료와 리본 선택비가 최종 결제금액에 반영되는지 살펴보세요. 상품가와 결제 합계를 나눠 비교할 수 있습니다.'),
 ('budget-premium','budget',['B205','B206'],'상위 표시가 두 상품 비교',
  'B205는 109,000원, B206은 149,000원으로 표시가 차이는 40,000원입니다. 이름이 비슷해도 실제 상품 코드와 상세 구성을 확인해야 합니다.',
  '금액 외 차이','꽃 종류·장식·높이 등 상품별 구성은 연결된 판매처 상세페이지에서 비교할 수 있습니다.'),
 ('budget-total','budget',['B202','B206'],'상품가와 주문총액',
  'B202는 59,000원, B206은 149,000원으로 표시됩니다. 배송 주소와 리본 옵션을 선택한 뒤 결제 화면에서 실제 주문 총액을 비교할 수 있습니다.',
  '장바구니 확인','받는 장례식장의 주소·희망일과 리본 문구를 입력한 뒤 추가 배송료와 최종 합계를 확인하는 흐름을 안내합니다.'),
 ('budget-basic','budget',['B201','B202','B205'],'기본형 선택부터 비교',
  '59,000원 기준가의 두 상품을 비교한 다음 109,000원 B205를 후보에 더할 수 있습니다. 실제 꽃 구성 차이는 상품별 상세정보로 구분합니다.',
  '표시가 차이 읽기','59,000원과 109,000원 사이 기준가 50,000원 차이가 있지만 배송비·리본 비용을 포함한 최종 차액은 별도로 확인됩니다.'),
 ('budget-four','budget',['B201','B202','B205','B206'],'네 가지 근조화환 비교',
  'B201·B202·B205·B206의 표시가는 59,000원·59,000원·109,000원·149,000원입니다. 꽃 구성과 크기는 가격순위가 아닌 실제 상품 상세 설명으로 비교할 수 있습니다.',
  '선택 순서','용도에 맞는 상품코드를 확인하고 받는 곳 주소에 따른 추가 비용과 리본 문구를 반영한 총액으로 최종 선택할 수 있습니다.'),
 ('venue-room','venue',['B201','B202'],'장례식장 빈소 구분',
  '받는 장례식장명과 빈소 번호는 근조화환 전달에 필요한 별도 정보입니다. 시설의 동일하거나 비슷한 이름을 주소와 함께 확인하는 방법을 안내합니다.',
  '수령 정보 준비','시설명, 도로명 주소, 빈소·고인 정보의 정확한 표기는 주문 화면에서 기재하며 시설명과 빈소 정보는 판매처 주문 화면의 수령지 항목에 입력할 수 있습니다.'),
 ('venue-location','venue',['B205','B206'],'시설 주소와 반입 위치',
  '받는 시설의 건물명과 정확한 수령 위치를 준비하면 배송 문의에 도움이 됩니다. 개별 장례식장의 화환 반입 허용 여부는 이 지역명만으로 판단하지 않습니다.',
  '반입 조건 문의','시설별 3단화환 설치 장소와 접수 시간을 확인한 뒤 실제 주문 가능한 상품을 판매처에서 안내받는 흐름입니다.'),
 ('venue-timing','venue',['B201','B205'],'희망 전달 일시',
  '장례식장에 근조화환이 도착해야 할 날짜와 희망 시간대를 정해 상품 상세 및 실제 배송 접수 가능 여부를 확인하는 방법을 안내합니다.',
  '일정 문의 정보','상품코드, 정확한 시설 주소, 희망 도착 시간과 빈소 정보를 묶어 문의하면 해당 주소의 실제 접수 가능 시간을 안내받을 수 있습니다.'),
 ('venue-form','venue',['B202','B206'],'3단 상품명과 빈소 안내',
  'B202는 판매처의 근조 3단 화환, B206은 근조 특특대 3단 화환으로 분류되어 있습니다. 받는 시설에 전달할 빈소 번호는 상품과 별도로 기입할 정보입니다.',
  '대체 상품 문의','해당 시설에서 3단화환을 받지 않는 경우 실제 주문 가능한 다른 형태의 상품이 있는지 판매처에 따로 문의할 수 있습니다.'),
 ('venue-shipping','venue',['B201','B206'],'배송비 표와 주문정보',
  'B201과 B206은 판매처에서 주문하는 근조 3단 상품으로 분류됩니다. 배송비는 해당 상품의 배송정보와 받는 군·읍면을 함께 기준으로 삼으므로, 이 페이지에 확인되지 않은 횡성군 추가금액을 적지 않습니다.',
  '배송비 확인 경로','장례식장명과 도로명 주소를 알려주시면 판매처가 해당 주문의 추가 배송비와 가능한 접수일을 안내할 수 있습니다.'),
 ('venue-order','venue',['B202','B205'],'주문 내용 재확인',
  '근조화환의 상품번호와 장례식장명, 빈소와 리본을 분리해 확인하면 비슷한 상품명이나 수령지 혼동을 줄일 수 있습니다.',
  '주문서 기록','상품 선택과 수령지 정보가 일치하는지 주문 화면에서 다시 확인하는 흐름을 제공합니다. 실제 배송 확인은 판매처 주문내역에서 진행합니다.'),
 ('ribbon-text','ribbon',['B201','B202'],'리본 문구 예시',
  'B201과 B202는 모두 59,000원으로 확인된 별도 근조화환 상품입니다. 주문할 상품번호를 선택한 뒤 리본 인쇄 항목을 입력할 수 있습니다.',
  '표현 확인','회사·단체 명의가 길다면 사용할 정식 명칭이나 약칭을 미리 결정해 주세요. 리본에 인쇄될 이름은 주문 확정 전 한 번 더 확인할 수 있습니다.'),
 ('ribbon-sender','ribbon',['B205','B206'],'보내는 분 이름',
  '개인 명의인지 회사나 단체 명의인지에 따라 리본에 적을 보내는 이름이 달라집니다. 정식 명칭과 문구를 혼동하지 않도록 별도로 확인합니다.',
  '발신인 표기','단체명과 개인명을 주문처에 정확히 전달하여 인쇄될 최종 내용을 확인할 수 있습니다. 배송 연락처와 리본 발신 명의는 다릅니다.'),
 ('ribbon-company','ribbon',['B201','B205'],'단체 명의 근조화환',
  '회사·협회·모임에서 보내는 근조화환의 리본에는 단체 정식 명칭을 사용할 수 있습니다. 축약된 이름을 사용할지 여부는 보내는 측의 실제 표기를 따릅니다.',
  '주문 담당자 정보','보내는 명칭과 주문 담당자 연락정보는 역할이 다릅니다. 리본 인쇄명과 결제·배송 연락처를 구분해 주문할 수 있습니다.'),
 ('ribbon-charge','ribbon',['B202','B206'],'리본 옵션 비용',
  '리본 문구 추가나 특수 인쇄 옵션이 유료인지 여부는 상품의 실제 옵션에 따릅니다. 리본 문구·인쇄 옵션의 최종 금액은 판매처 주문 화면에서 확인할 수 있습니다.',
  '결제 전 리본 확인','리본 문구와 보내는 명의를 입력한 뒤 옵션 추가금이 주문합계에 포함되는지 확인하는 흐름입니다.'),
 ('ribbon-proof','ribbon',['B201','B206'],'리본 오탈자 확인',
  '고인·유족에 대한 조의 표현과 보내는 명칭에 오탈자가 없는지 검토할 수 있습니다. 입력한 리본 문구는 주문서 확정 전에 확인합니다.',
  '수정 요청 방법','문구가 변경된 경우 접수 단계와 제작 진행 상태에 따라 수정 가능 여부가 달라질 수 있어 판매처에 직접 확인합니다.'),
 ('ribbon-venue','ribbon',['B202','B205'],'리본과 수령시설 관계',
  '장례식장에 여러 빈소가 있는 경우 시설명뿐 아니라 고인 성함과 빈소 번호까지 준비하면 수령 장소를 더 정확하게 전달할 수 있습니다.',
  '빈소 정보와 문구','주문 후 빈소가 변경되면 판매처에 새 빈소 번호를 전달해 수령 정보 수정 가능 여부를 문의하세요. 리본에 적는 발신인 명의는 별도로 보존할 수 있습니다.')
]
# Each introduction answers one actual buyer decision in natural Korean.
# The selected cohort is defined in INTENTS; prices below belong only to it.
INTENT_INTROS={
 'budget-entry':'{county} 장례식장으로 보낼 근조화환을 준비할 때, 상품 주문 링크와 수령지·조의 문구 정보를 함께 살펴볼 수 있습니다.',
 'budget-upgrade':'{county} 근조화환의 B201은 59,000원, B205는 109,000원으로 기준가격 차이가 50,000원입니다. 두 상품의 구성과 배송 조건을 함께 비교해 보세요.',
 'budget-premium':'{county} 근조화환을 상위 가격대에서 고르신다면 B205와 B206 두 상품의 상세 사진·규격·주문 옵션을 나란히 살펴보세요.',
 'budget-total':'{county}에 보낼 근조 3단 화환와 B206은 상품가격뿐 아니라 선택할 수 있는 옵션을 함께 살펴본 뒤 예산에 맞게 결정해 보세요.',
 'budget-basic':'{county} 근조화환은 B201·B202 두 상품을 먼저 살펴보고 B205를 함께 비교할 수 있습니다. 상품별 구성과 옵션은 각 상세 페이지에서 확인해 보세요.',
 'budget-four':'{county}에 보낼 근조화환으로 B201·B202·B205·B206 네 가지 상품을 비교할 수 있습니다. 각 상품의 표시가격과 주문 옵션을 확인한 뒤 선택해 보세요.',
 'venue-room':'{county} 장례식장으로 근조화환을 보낼 때는 시설명과 빈소를 먼저 정리해 주세요. 상품을 선택하고 희망 전달 시간을 알려주시면 주문 가능 일정을 상담할 수 있습니다.',
 'venue-location':'{county}에서 근조화환을 받을 장례식장의 정확한 주소와 화환 반입 위치를 준비해 주세요. 상품번호와 함께 전달하면 배송 조건을 확인하기 편리합니다.',
 'venue-timing':'{county} 근조화환 주문은 장례식장에 전달할 날짜와 희망 시간을 정하는 데서 시작합니다. 상품별 접수 가능 시간과 배송비를 판매처에서 확인할 수 있습니다.',
 'venue-form':'{county} 근조화환의 판매처 상품명, 빈소를 적을 항목과 공식 읍·면 명칭을 안내합니다.',
 'venue-shipping':'{county} 근조화환의 상품별 배송정보 확인 경로와 공식 읍·면 명칭을 안내합니다. 시설 주소와 빈소는 주문자가 별도로 준비해야 합니다.',
 'venue-order':'{county} 근조화환 주문서에는 상품번호와 장례식장·빈소, 희망일, 리본 문구를 구분해 입력하면 편리합니다. 상품별 주문 링크를 통해 확인할 수 있습니다.',
 'ribbon-text':'{county} 장례식장에 보낼 조의 문구 예시와 빈소에 전달할 정보를 정리했습니다.',
 'ribbon-sender':'{county} 근조화환에 적을 보내는 사람의 이름을 정리해 주세요. 개인 명의와 회사·단체 명의를 구분하고 리본 문구를 함께 확인할 수 있습니다.',
 'ribbon-company':'{county} 근조화환을 회사나 단체 명의로 보내신다면 리본에 표시할 정식 명칭을 준비해 주세요. 실제 받는 시설명과 발신 명의는 별도 항목으로 정리하면 됩니다.',
 'ribbon-charge':'{county} 근조화환 리본의 문구·인쇄 옵션을 고르실 때 추가 비용이 있는지도 살펴보세요. 선택한 상품의 표시가격과 배송비를 함께 비교할 수 있습니다.',
 'ribbon-proof':'{county} 근조화환의 리본 문구와 단체·개인 이름은 제작 전에 최종 표기를 확인해 보세요. 변경 요청이 필요하다면 주문 진행 상태에 따라 판매처에 문의할 수 있습니다.',
 'ribbon-venue':'{county} 근조화환 주문에서 리본에 적는 발신 명의와 실제 화환을 받을 장례식장·빈소는 서로 다른 정보입니다. 두 항목을 구분하면 주문이 수월합니다.'
}

def product_skus_in_text(text):
    """Read B-prefixed SKU codes even with Korean particles attached.

    Unicode \\b is not a SKU boundary: B201과 and B206의 must be captured.
    Do not silently split a longer Latin/alphanumeric SKU into a known code.
    """
    import re
    return set(re.findall(r'(?<![A-Za-z0-9])B[0-9]{3}(?![0-9])', text))


def listed_prices_in_text(text):
    """Return comma-normalized KRW amounts, including 원+Korean endings.

    Both 59,000원입니다 and 59000원으로 are amounts. Relative price
    differences remain allowed only if selected-card prices imply them.
    """
    import re
    pattern=r'(?<![0-9,])(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})원(?![0-9])'
    results=set()
    for item in re.findall(pattern, text):
        try:
            amount=int(item[:-1].replace(',', ''))
        except ValueError:
            raise AssertionError("Invalid KRW price token")
        results.add(f'{amount:,}원')
    return results


def expanded_pools(base):
    """Keep every displayed SKU/price in the chosen product cohort."""
    import copy
    catalog_price={'B201':59000,'B202':59000,'B205':109000,'B206':149000}
    output=dict(base)
    for name,group,skus,heading,paragraph,other_title,other_paragraph in INTENTS:
        selected=set(skus)
        assert selected and selected<=set(catalog_price)
        pool=copy.deepcopy(base[group])
        pool['productSkus']=list(dict.fromkeys(skus))
        # Distinct introduction, not a duplicated decision-context paragraph.
        pool['introductions']=[INTENT_INTROS[name]]
        names=' · '.join(sku+' '+format(catalog_price[sku],',')+'원' for sku in skus)
        prices=[catalog_price[sku] for sku in skus]
        allowed_prices={format(x,',')+'원' for x in prices}
        allowed_prices.update(format(abs(x-y),',')+'원' for x in prices for y in prices if x!=y)
        first,last=skus[0],skus[-1]
        pool['sections']=[
            {'slot':'choice','heading':'선택 가능한 근조상품과 표시가',
             'paragraph':'비교할 상품은 '+names+'입니다. 각 상품의 실제 구성은 주문 상세에서 확인하고 선택할 수 있습니다.'},
            {'slot':'choice','heading':'기준가격별 선택',
             'paragraph':first+'와 '+last+' 중 원하시는 상품을 선택해 보세요. 꽃 구성과 규격은 각각의 판매처 상품 설명에서 비교할 수 있습니다.'},
            {'slot':'choice','heading':'상품코드별 구매 확인',
             'paragraph':names+'을 살펴보고 상품 상세를 열어 보세요. 표시가격이 같더라도 사진·규격·선택 옵션은 상품별로 확인할 수 있습니다.'},
            {'slot':'choice','heading':'예산과 배송비',
             'paragraph':names+' 중 예산에 맞는 화환을 고른 뒤 장례식장 주소를 입력해 주세요. 배송비와 선택 옵션이 반영된 결제 총액을 확인할 수 있습니다.'}
        ]
        # Each shared slot covers a distinct practical part of a purchase, so the
        # deterministic choice is not merely an adjective shuffle for SEO.
        additional={
          'order':[
            ('장례식장 주소','{county}에 있는 장례식장의 공식 명칭과 도로명 주소, 빈소 번호가 있으면 함께 전달할 수 있습니다. 비슷한 이름의 시설을 구분하는 데 도움이 됩니다.'),
            ('희망 수령 날짜','빈소에 근조화환을 전달할 희망일과 시간대를 정하고 받는 장소를 함께 지정할 수 있습니다. 판매처의 실제 접수 가능 시간을 기준으로 주문이 진행됩니다.'),
            ('주문 담당자와 리본 명의','주문 연락 담당자와 화환 리본에 표시할 보내는 이름은 구분해서 입력할 수 있습니다. 회사·단체 명의라면 정확한 표기를 준비할 수 있습니다.'),
            ('시설 반입 위치','실제 수령 시설의 화환 반입 위치나 설치 조건이 있다면 주문 전에 판매처에 알려 배송 방식과 반입 가능 형태를 상담할 수 있습니다.'),
            ('빈소 정보','받는 시설에 여러 빈소가 있다면 고인·빈소 번호와 수령 시설 주소를 구분해 준비할 수 있습니다. 결제 내용은 판매처 주문 화면에서 확인합니다.'),
            ('상품 선택 후 주문','상품코드를 먼저 고르고 시설명·주소·수령 날짜를 주문서에 입력할 수 있습니다. 선택한 상품과 받는 장소가 일치하는지 결제 전에 확인할 수 있습니다.')
          ],
          'ribbon':[
            ('조의 문구와 발신인','근조 리본의 조의 문구와 보내는 사람·단체의 명칭은 서로 다른 항목입니다. 실제 인쇄 표기는 판매처 주문 옵션에 입력할 수 있습니다.'),
            ('보내는 단체명','회사나 단체가 화환을 보낼 때 사용할 정식 명칭을 준비할 수 있습니다. 주문 연락처와 리본에 적는 명의는 다르게 입력할 수 있습니다.'),
            ('리본 수정 문의','리본 인쇄 전 문구와 이름의 맞춤법을 검토할 수 있습니다. 제작 진행 상태에 따른 변경 가능 여부는 판매처에서 안내합니다.'),
            ('리본 추가금','리본 인쇄·옵션 비용이 별도로 표시되면 상품 표시가와 구분해 결제 총액을 확인할 수 있습니다.'),
            ('문구와 수령지','리본에 적는 조의 문구 외에 받는 장례식장과 빈소를 별도 입력하면 전달 장소와 발신인을 구분할 수 있습니다.')
          ],
          'delivery':[
            ('군별 배송비 확인','상품 상세의 배송비 안내는 수령지 읍·면에 따라 달라질 수 있습니다. 정확한 주소를 기준으로 주문 시 적용 금액을 확인할 수 있습니다.'),
            ('추가비용 계산','배송료와 리본 선택비용은 상품 기준가와 구분됩니다. 판매처 결제 화면에서 실제 합계가 안내됩니다.'),
            ('배송 요청 시각','희망하는 도착 시간대와 실제로 접수 가능한 시간은 다를 수 있습니다. 장례식장 주소·날짜를 판매처에 전달하면 일정을 확인할 수 있습니다.'),
            ('정확한 읍면 주소','같은 군의 배송지라도 읍·면과 상세 주소가 다르면 배송비가 달라질 수 있습니다. 정확한 수령 장소로 주문비용을 계산할 수 있습니다.'),
            ('배송비 결제 방식','판매처 상품 페이지는 배송비를 주문 시 결제하는 방식으로 안내합니다. 배송지에 따른 실제 추가금은 주문 과정에서 확인할 수 있습니다.'),
            ('수령 시설 확인','장례식장명과 정확한 주소를 함께 전달하면 해당 주문의 배송 여부와 수령 일정을 확인하는 데 도움이 됩니다.')
          ],
          'information':[
            ('상품 상세 비교','상품코드가 다른 근조화환은 판매처 상세페이지에서 꽃 구성·규격과 주문 옵션을 각각 비교할 수 있습니다.'),
            ('기준가의 확인 시점','표시된 가격은 2026-11-07 판매처 화면에서 확인한 금액입니다. 재고와 최종 결제액은 실제 주문 시점의 판매처 정보가 기준입니다.'),
            ('상품 주문 화면으로 이동','원하시는 근조화환의 상품 상세를 열어 사진과 선택 옵션을 확인하고 받는 장소를 입력해 주문할 수 있습니다.'),
            ('판매처 상품 사진과 구성','연결된 판매처 상품 상세페이지에서 근조화환 사진과 구성 안내를 확인할 수 있습니다. 상품별 사진과 설명을 비교한 뒤 원하시는 상품을 선택해 주세요.'),
            ('상품 구성 문의','상품의 높이·폭, 꽃 수량과 종류는 판매처 상품 상세 설명으로 확인할 수 있습니다. 상품별 규격과 꽃 구성은 판매처 상세에 적힌 정보를 기준으로 선택할 수 있습니다.')
          ]
        }
        for slot in ('order','ribbon','delivery','information'):
            options=[]
            for item in base[group]['sections']:
                if item['slot']==slot:
                    options.append(copy.deepcopy(item))
            options.extend({'slot':slot,'heading':title,'paragraph':body}
                for title,body in additional[slot])
            for item in options:
                # Budget introductions and decision sections already explain prices
                # and checkout costs. Reserve the delivery slot for scheduling or
                # hand-off instead of repeating the same fee disclaimer.
                if group=='budget' and slot=='delivery' and item['heading'] not in (
                    '희망 도착 시간','배송 요청 시각','수령 시설 확인','수령 날짜 전달'):
                    continue
                text=item['heading']+' '+item['paragraph']
                if not product_skus_in_text(text).issubset(selected):
                    continue
                if not listed_prices_in_text(text).issubset(allowed_prices):
                    continue
                if len(skus)!=4 and any(word in text for word in ('네 상품','네 가지','네 개','4개')):
                    continue
                pool['sections'].append(item)
        # The old renderer displayed eight simultaneous sections, often saying
        # "choose a product / check delivery fee / final total" four times.
        # Compose only FOUR buyer tasks: product decision, receipt handoff,
        # ribbon identity and official 읍/면 lookup. The decision-specific
        # paragraph replaces the generic price list already visible in cards.
        # This is intentional CONTENT deletion, not a banned-phrase rewrite.
        pool['sections']=[
            {'slot':'choice','heading':heading,'paragraph':paragraph},
            *[item for item in pool['sections'] if item['slot'] in ('order','ribbon')],
            {'slot':'verified-townships',
             'heading':'{county}의 읍·면',
             'paragraph':'{county}의 읍·면 {townshipCount}곳: {townships}. 이 목록은 행정지역명이며 장례식장명이나 시설 도로명주소가 아닙니다. 받는 시설 주소와 빈소는 별도로 준비해 주세요.'}
        ]
        # Ribbon intent: introduction=why this page, choice=which confirmed
        # SKU, ribbon=concrete example, FAQ=post-order edits (a NEW question).
        # Never restate the senders/condolence distinction in four sections.
        if name=='venue-form':
            # The introduction states what exists; each section owns a new task.
            pool['sections']=[
                {'slot':'choice','heading':'판매처 상품명 구분',
                 'paragraph':'B202는 근조 3단 화환, B206은 근조 특특대 3단 화환이라는 판매처 등록명입니다. 두 상품의 규격·꽃 수량이 같거나 다르다는 자료는 이 페이지에서 주장하지 않습니다.'},
                {'slot':'order','heading':'수령 빈소와 희망일',
                 'paragraph':'주문할 때 장례식장명, 고인 또는 빈소 번호, 희망 전달 날짜를 별도로 준비할 수 있습니다. 시설별 도로명주소는 이 페이지에 제공되지 않습니다.'},
                {'slot':'ribbon','heading':'리본에 적는 조의 문구',
                 'paragraph':'“삼가 고인의 명복을 빕니다”와 “깊은 애도를 표합니다”는 근조 리본에 사용할 수 있는 표현입니다. 보내는 분 이름은 문구와 구분해 준비할 수 있습니다.'},
                {'slot':'verified-townships','heading':'{county} 읍·면 이름',
                 'paragraph':'{county}의 읍·면 {townshipCount}곳은 {townships}입니다. 장례식장명과 도로명주소는 포함되어 있지 않으므로 실제 받는 시설의 정보를 별도로 준비해야 합니다.'}
            ]
            pool['faqs']=[{'q':'접수한 화환 주문내역은 어디서 볼 수 있나요?',
                           'a':'판매처 상단의 주문내역조회 메뉴에서 주문내역을 조회할 수 있습니다.'}]
        elif name=='venue-shipping':
            pool['sections']=[
                {'slot':'choice','heading':'배송정보가 연결된 상품',
                 'paragraph':'판매처의 B201 근조 3단 화환과 B206 근조 특특대 3단 화환에는 각각 상품 상세 링크가 있습니다. 수령지역 {county}의 읍·면에 따라 배송 안내가 달라질 수 있으며 두 상품의 지역별 추가 요금은 각 판매처 상품 상세를 통해 구분할 수 있습니다.'},
                {'slot':'order','heading':'배송 문의에 필요한 수령지',
                 'paragraph':'선택 상품번호와 장례식장 도로명주소, 빈소 번호, 희망 전달일을 갖추면 받는 장소를 특정할 수 있습니다. 실제 시설 주소는 이 페이지의 읍면 목록에서 자동 검색되지 않습니다.'},
                {'slot':'ribbon','heading':'조의 문구와 보내는 명의',
                 'paragraph':'리본에는 “삼가 고인의 명복을 빕니다” 같은 조의 문구와 보내는 개인·단체 이름을 분리해 적을 수 있습니다.'},
                {'slot':'verified-townships','heading':'{county} 읍·면 명칭',
                 'paragraph':'{county}의 읍·면 {townshipCount}곳은 {townships}입니다. 행정구역명 목록이며 장례식장별 이름·도로명주소 목록은 아닙니다.'}
            ]
            pool['faqs']=[{'q':'주문을 마친 후 배송·주문 상태는 어디서 확인하나요?',
                           'a':'판매처 사이트의 주문내역조회 메뉴에서 접수한 주문 정보를 확인할 수 있습니다.'}]
        if name=='ribbon-text':
            region_lookup=[s for s in pool['sections'] if s['slot']=='verified-townships']
            pool['sections']=[
                {'slot':'choice','heading':'동일 표시가 두 상품',
                 'paragraph':'B201과 B202는 각각 59,000원으로 표시됩니다. 두 SKU는 서로 다른 판매 항목이므로 선택할 번호를 구분할 수 있습니다.'},
                {'slot':'choice','heading':'근조화환 종류 확인',
                 'paragraph':'판매처에서 B201은 근조 3단 화환으로 표기하며 B202는 다른 상품번호입니다. 같은 가격의 두 링크 중 원하는 항목을 선택할 수 있습니다.'},
                {'slot':'choice','heading':'B201과 B202 구분',
                 'paragraph':'B201은 근조 3단 화환, B202는 근조 3단 화환라는 판매처 이름으로 등록돼 있습니다. 각각의 상품 카드에서 주문 상세를 열 수 있습니다.'},
                {'slot':'choice','heading':'가격 외 주문번호',
                 'paragraph':'B201과 B202는 각각 별도의 상품 상세주소로 연결됩니다. 표시가격은 같으므로 상품번호로 주문 항목을 구분할 수 있습니다.'},
                {'slot':'choice','heading':'59,000원 상품 선택',
                 'paragraph':'동일 표시가격의 B201과 B202 중 선택한 번호가 실제 주문 화면과 일치하는지 확인할 수 있습니다.'},
                {'slot':'order','heading':'빈소 전달 정보',
                 'paragraph':'화환을 받을 장례식장명과 빈소 번호, 희망 날짜를 정하면 선택한 상품 화면에 입력할 수 있습니다.'},
                {'slot':'order','heading':'시설 주소와 빈소',
                 'paragraph':'장례식장 도로명 주소와 빈소를 구분해서 준비하면 받을 장소를 정확하게 기재할 수 있습니다.'},
                {'slot':'order','heading':'희망 전달 날짜',
                 'paragraph':'조문 일정에 맞춰 도착 희망일을 정하고 상품번호와 함께 전달하면 접수 가능한 일정을 확인할 수 있습니다.'},
                {'slot':'order','heading':'현장 인계 위치',
                 'paragraph':'시설에서 화환을 받는 장소가 별도로 지정되면 그 위치와 빈소 정보를 주문할 때 함께 전달할 수 있습니다.'},
                {'slot':'order','heading':'주문 연락 정보',
                 'paragraph':'수령 시설의 정확한 이름과 연락 가능한 담당자, 희망 전달 시각을 한 주문에 묶어 전달할 수 있습니다.'},
                {'slot':'ribbon','heading':'조의 문구 예시',
                 'paragraph':'“삼가 고인의 명복을 빕니다”와 “깊은 애도를 표합니다”는 리본에 사용할 수 있는 조의 표현입니다.'},
                {'slot':'ribbon','heading':'간결한 조문 표현',
                 'paragraph':'짧은 문구를 원한다면 “謹弔(근조)”처럼 조의를 나타내는 글귀를 고려할 수 있습니다.'},
                {'slot':'ribbon','heading':'단체 발신인 표기',
                 'paragraph':'단체에서 보내는 근조화환은 “깊은 애도를 표합니다”와 같은 문구에 회사나 모임의 정식 명칭을 함께 적을 수 있습니다.'},
                {'slot':'ribbon','heading':'개인 발신인 표기',
                 'paragraph':'개인 명의의 조의 문구로는 “삼가 고인의 명복을 빕니다”를 사용할 수 있습니다. 보내는 이름은 별도 리본 항목에 입력할 수 있습니다.'},
                {'slot':'ribbon','heading':'인쇄할 문구와 이름 예시',
                 'paragraph':'조의 문구로 “삼가 고인의 명복을 빕니다” 또는 “謹弔(근조)”를 사용할 수 있습니다. 보내는 분의 명칭은 예를 들어 “○○회사 임직원 일동”처럼 별도로 적을 수 있습니다.'},
                *region_lookup
            ]
            pool['faqs']=[{'q':'주문한 뒤 리본 문구를 바꿀 수 있나요?',
                           'a':'리본 인쇄 진행 상태에 따라 변경 가능 여부가 달라집니다. 주문한 판매처에 변경할 문구와 상품번호를 전달해 확인할 수 있습니다.'}]
        elif name=='budget-entry':
            # The ribbon section must give new concrete text rather than repeating
            # the receipt address already owned by the order section.
            ribbon_examples=[
              ('개인 명의 조의 문구','개인이 조의를 전할 때는 “삼가 고인의 명복을 빕니다” 같은 문구를 사용할 수 있습니다. 보내는 이름은 본인의 이름으로 준비할 수 있습니다.'),
              ('회사 이름으로 보내기','회사 명의라면 “깊은 애도를 표합니다” 같은 조의 문구와 “○○회사 임직원 일동” 같은 보내는 명칭을 함께 준비할 수 있습니다.'),
              ('단체와 모임의 명의','협회나 모임에서 보낸다면 “謹弔(근조)” 같은 짧은 표현에 “○○동창회 일동”처럼 단체 이름을 별도로 적을 수 있습니다.'),
              ('짧은 조의 표현','리본 공간에 간결하게 적을 표현으로 “謹弔(근조)”를 사용할 수 있습니다. 발신인 이름을 문구와 분리해 적으면 전달하는 분이 드러납니다.'),
              ('인쇄명 오탈자 확인','“삼가 고인의 명복을 빕니다” 같은 조의 문구와 보내는 명칭을 분리해 준비한 뒤, 회사명·개인명 등의 띄어쓰기를 확인할 수 있습니다.')
            ]
            # Several valid real buyer roles, selected once by purpose/variant.
            # No locality-specific facts are invented to satisfy similarity metrics.
            selected_roles=[item for item in pool['sections'] if item['slot'] in ('choice','order')]
            region_roles=[item for item in pool['sections'] if item['slot']=='verified-townships']
            pool['sections']=(selected_roles+
                [{'slot':'ribbon','heading':head,'paragraph':text}
                 for head,text in ribbon_examples]+region_roles)
            # The choice section already answers "which 59,000 won items?".
            # FAQ must add a new answer about receiving venue compatibility.
            pool['faqs']=[{'q':'주문한 근조화환 내역은 어디서 확인하나요?',
                           'a':'판매처 상단의 주문내역조회 메뉴에서 주문 정보를 조회할 수 있습니다. 주문 시 이용한 구매 경로에서 내역을 확인해 주세요.'}]
        else:
            pool['faqs']=[pool['faqs'][-1]]
        for item in pool['sections']:
            text=item['heading']+' '+item['paragraph']
            assert product_skus_in_text(text).issubset(selected),(name,text)
            assert listed_prices_in_text(text).issubset(allowed_prices),(name,text)
            if len(skus)!=4:
                assert not any(word in text for word in ('네 상품','네 가지','네 개','4개')),(name,text)
        assert paragraph not in pool['introductions'][0]
        output[name]=pool
    return output


def county_intents():
    return [x[0] for x in INTENTS]


def skus_for(purpose):
    return next(x[2] for x in INTENTS if x[0]==purpose)
