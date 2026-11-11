"""Source-only Worker6 locality independence audit. No HTML build or deployment."""
from collections import Counter,defaultdict
from pathlib import Path
import hashlib,json
from scripts.worker6_nationwide_inputs import prepare
from scripts.worker6_shipping_render import lookup
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
OUT=ROOT/'reports/promotion-gift-plants/source-independence'
def analyze():
    pages,_=prepare()
    catalog=json.loads((SITE/'products.json').read_text(encoding='utf-8'))
    skus={p['sku']:{'name':p['name'],'price':p['referencePrice'],'orderUrl':p['orderUrl'],
       'source':p['priceEvidence'],'stockConfirmed':False,'localAvailabilityConfirmed':False}
          for p in catalog if p.get('priceConfirmed')}
    assert len(skus)==6
    locality=[p for p in pages if p['pageKind']=='locality-detail']
    buckets=defaultdict(list);fee=Counter();flags=Counter()
    examples=[]
    for p in locality:
        # Four purposes are chosen by a hash of the place name, not by buyer intent.
        purpose=p['purpose']
        province,district,local_name=p['region'].split(' ',2)
        match=lookup(province,district,local_name)
        flags[str(p['sourceFlag'])]+=1
        fee[match['state']]+=1
        # The underlying four pools are shared; locality name and fee state
        # cannot prove distinct local buying conditions.
        key=(purpose,match['state'],tuple(sorted(p['productSkus'])))
        buckets[key].append(p['region'])
        if match['state'] in ('overlap-unknown-priority','exact-locality-display') and len(examples)<25:
            examples.append({'region':p['region'],'purpose':purpose,'feeState':match['state'],
               'sellerRows':match['candidates'],'finalShippingConfirmed':False})
    largest=sorted(buckets.items(),key=lambda kv:(-len(kv[1]),kv[0]))
    representative=[{'purpose':k[0],'feeState':k[1],'skuSet':list(k[2]),
        'count':len(names),'exampleRegions':names[:3],
        'independentBuyerEvidence':'not established by matching purpose/fee-state/product-set'}
        for k,names in largest[:20]]
    report={'scope':'source-only, no rendered HTML, no new 49% or 85-point pass',
        'candidateCount':len(locality),'totalTarget':len(pages),
        'sourceFlags':dict(sorted(flags.items())),
        'sellerFeeStates':dict(sorted(fee.items())),
        'structuralBucketCount':len(buckets),'largestBucketCount':len(largest[0][1]),
        'topRepeatedBuckets':representative,'sellerRowExamples':examples,
        'catalog':skus,
        'fieldMapping':{
          'regionName':'2025 candidate inventory; not a verified current delivery location',
          'purpose':'SHA256 assignment by region name; NOT verified local intent',
          'productNamePriceOrderUrl':'seller-confirmed SKU catalog, same nationwide',
          'surcharge':'seller D144 displayed rows only; never final fee or eligibility',
          'officeHomeVenue':'generic buyer receipt questions, not local facility proof',
          'actualLocalStock':'unknown','deliveryArrivalCutoff':'unknown',
          'facilityAdmission':'unknown unless separate current venue evidence passes gate',
          'sourceFlag':'candidate provenance flag, not evidence of delivery'},
        'similarityThreshold':0.49,'editorialThreshold':85,
        'releaseAllowed':False}
    return report
def write():
    result=analyze();OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'source-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 전국 5,302 후보 소스 독립성 증거표','',
      '본 보고서는 원장·생성기 입력만 검사한다. HTML 유사도/품질 점수 PASS가 아니다.','',
      '| 분류 | 수량/근거 | 고객 확정주장 가능 여부 |','|---|---|---|',
      f"| 전체 후보 | {result['totalTarget']} (읍면동 {result['candidateCount']}) | 개별 배송가능 확정 불가 |",
      f"| 생성기 구조 버킷 | {result['structuralBucketCount']} | 같은 버킷은 독립 지역 사실 아님 |",
      f"| 최대 반복 버킷 | {result['largestBucketCount']}개 지역 | 지명 차이만으로 독립성 불인정 |",
      '| 상품 | 꽃이랑 검증 SKU 6종·가격·상세링크 | 상품 정보만 가능, 지역 재고 불가 |',
      '| 추가요금 | 판매처 D144 표행 및 중복 상태 | 표시 사실만 가능, 최종 요금 불가 |',
      '| 목적 | 지역명 SHA 해시로 4목적 배정 | 실제 지역 구매수요 근거 아님 |',
      '| 수령 유형 | 회사·자택·행사장 공통 질문 | 특정 지역 시설 수령 가능 추정 금지 |','',
      '## 반복 구조 상위 20개 버킷','',
      '| 목적 | 요금표 상태 | SKU | 지역 수 | 예시 지역 |','|---|---|---|---:|---|']
    for b in result['topRepeatedBuckets']:
        lines.append(f"| {b['purpose']} | {b['feeState']} | {', '.join(b['skuSet'])} | {b['count']} | {', '.join(b['exampleRegions'])} |")
    lines+=['','## 결론','동일 목적/배송표 상태/상품 집합은 지역별 독립 구매정보를 제공하지 않는다. 지역명 교체, 무관 시설 나열, 임의 상품순서로 49% 기준을 통과시켜서는 안 된다. 전체 5,302 목표 및 49%/85점 기준 유지.']
    (OUT/'source-evidence.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    x=write();print(json.dumps({k:x[k] for k in ('totalTarget','candidateCount','structuralBucketCount','largestBucketCount','sellerFeeStates')},ensure_ascii=False))
