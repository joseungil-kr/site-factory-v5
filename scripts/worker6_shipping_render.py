"""Display seller surcharge evidence, never infer shipping eligibility or final price."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'sites/promotion-gift-plants/seller-shipping-raw-rows.json'
ALIASES={'경기도':'경기','강원도':'강원','경상남도':'경남','경상북도':'경북','인천광역시':'인천','울산광역시':'울산','대구광역시':'대구','전라북도':'전북','충청남도':'충남','충청북도':'충북','제주특별자치도':'제주'}
def lookup(province,district,locality,source=None):
    data=source if source is not None else json.loads(SOURCE.read_text(encoding='utf-8'))
    province_label=ALIASES.get(province)
    if not province_label:
        return {'region':' '.join((province,district,locality)),'state':'jurisdiction-unresolved',
            'candidates':[],'sourceUrl':data['sourceUrl'],'checkedAt':data['checkedAt'],
            'finalShippingPriceKnown':False,'deliveryAvailabilityKnown':False,
            'absenceMeansFree':False,'aliasOnlyNotOfficialAddressValidation':True,
            'reason':'province label cannot be mapped without authoritative jurisdiction evidence'}
    candidates=[]
    for row in data['rows']:
        if province_label!=row['provinceLabel']:continue
        if district not in [v.strip() for v in row['districtText'].split(',')]:continue
        names=[] if row['localityText']=='-' else [v.strip() for v in row['localityText'].split(',')]
        if not names or locality in names:
            candidates.append({'row':row['row'],'extraKRW':row['extraKRW'],
                 'scope':'district-display' if not names else 'exact-locality-display'})
    exact=[x for x in candidates if x['scope']=='exact-locality-display']
    parents=[x for x in candidates if x['scope']=='district-display']
    if exact and parents:state='overlap-unknown-priority'
    elif exact:state='exact-locality-display'
    elif parents:state='district-display-only'
    else:state='not-listed-unknown'
    return {'region':' '.join((province,district,locality)),'state':state,
        'candidates':candidates,'sourceUrl':data['sourceUrl'],'checkedAt':data['checkedAt'],
        'finalShippingPriceKnown':False,'deliveryAvailabilityKnown':False,
        'absenceMeansFree':False,'aliasOnlyNotOfficialAddressValidation':True}
def evidence_section(result):
    """Customer-facing action; preserve exact raw rows and matching status in ledger."""
    rows=result['candidates']
    if result['state']=='exact-locality-display':
        item=rows[0]
        description=(f"{result['region']}의 판매처 추가 배송비 표에는 {item['extraKRW']:,}원이 표시됩니다. "
                     "상품과 상세 주소에 실제 적용되는 최종 요금은 전화로 확인하세요.")
    elif result['state']=='overlap-unknown-priority':
        amounts=' / '.join(f"{x['extraKRW']:,}원" for x in rows)
        description=(f"{result['region']}의 판매처 배송비 표에는 {amounts} 두 금액이 표시됩니다. "
                     "상품번호와 상세 주소를 알려주시면 상담으로 최종 적용 요금을 확인할 수 있습니다.")
    elif result['state']=='district-display-only':
        description=(f"{result['region']}의 상위 지역에 추가 배송비가 표시됩니다. "
                     "읍면동 상세 주소와 상품번호를 알려주시면 실제 적용 요금을 상담할 수 있습니다.")
    else:
        description=(f"{result['region']}에 보낼 상품번호와 정확한 배송지를 알려주시면 "
                     "추가 배송비와 수령 방법을 전화로 확인할 수 있습니다. 표에 별도 금액이 보이지 않아도 무료배송으로 확정하지 않습니다.")
    return {'heading':'배송비와 수령 방법 상담',
      'paragraph':description+' 전화 1844-0644로 희망 수령일·시간도 함께 알려주세요. 판매처 표 확인일: '+result['checkedAt']+'.',
      'sourceUrl':result['sourceUrl'],'checkedOn':result['checkedAt']}
