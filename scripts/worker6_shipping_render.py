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
    rows=result['candidates']
    if result['state']=='jurisdiction-unresolved':
        description=f"{result['region']}의 행정명과 판매처 배송비 표의 지역명 연결이 확인되지 않았습니다. 원문 행이 없다고 판단할 수 없습니다."
    elif result['state']=='exact-locality-display':
        item=rows[0]
        description=f"판매처 추가 배송비 표 {item['row']}행에는 {result['region']}에 추가 배송비 {item['extraKRW']:,}원이 표시됩니다."
    elif result['state']=='overlap-unknown-priority':
        pairs=', '.join(f"{x['row']}행 {x['extraKRW']:,}원" for x in rows)
        description=f"판매처 표에는 {result['region']}에 겹쳐 적용될 수 있는 항목({pairs})이 있습니다. 어떤 금액이 우선 적용되는지 확인되지 않았습니다."
    elif result['state']=='district-display-only':
        pairs=', '.join(f"{x['row']}행 {x['extraKRW']:,}원" for x in rows)
        description=f"판매처 표의 시군구 단위 항목({pairs})에 {result['region']}의 상위 지역이 표시됩니다. 개별 읍면동에 실제 적용되는지는 확인되지 않았습니다."
    else:
        description=f"판매처의 확인된 추가 배송비 표에서 {result['region']}의 정확한 읍면동 행을 찾지 못했습니다. 미기재는 무료배송을 의미하지 않습니다."
    return {'heading':'배송비 표에 표시된 범위',
      'paragraph':description+' 사업자 운영확인상 지역별 지점 발송으로 전국 당일배송 서비스가 가능합니다. 다만 해당 주문의 도착 가능 시각·마감·재고와 최종 추가요금은 전화 1844-0644로 확인합니다. 출처: '+result['sourceUrl']+' (확인일 '+result['checkedAt']+').',
      'sourceUrl':result['sourceUrl'],'checkedOn':result['checkedAt']}
