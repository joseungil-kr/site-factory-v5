"""Worker6 nationwide input preparation. Does not publish or modify existing sites."""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/regions/nationwide_locality_candidates_5034.json'
PURPOSES=('promotion','transfer','congratulations','sameDayInquiry')
SKUS={'promotion':['D144','D156'],'transfer':['D156','D144'],
      'congratulations':['D156','D144'],'sameDayInquiry':['D144','D156']}
TITLE='{region} 승진화분 주문, 축하화분 당일 배달'
def prepare():
    src=json.loads(SOURCE.read_text(encoding='utf-8'))
    rows=src['records']
    assert len(rows)==5034 and sum(row[3]==0 for row in rows)==1438
    provinces=sorted({row[0] for row in rows})
    districts=sorted({(row[0],row[1]) for row in rows})
    assert len(provinces)==17 and len(districts)==250
    pages=[];regions=[];seen=set()
    def add(number,region,purpose,kind,parent=None,source_flag=None):
        assert region not in seen,(region,kind)
        seen.add(region)
        digest=int(hashlib.sha256((region+purpose).encode()).hexdigest()[:8],16)
        context=('새 부서와 직함' if purpose=='promotion' else '새 근무지의 수령 담당자' if purpose=='transfer' else '축하 문구와 배치 공간' if purpose=='congratulations' else '희망 도착 시간과 상세 주소')
        p={'id':f'w6-{number:05d}','number':number,'region':region,'purpose':purpose,'topic':context,
           'title':TITLE.format(region=region),
           'intro':f'{region}에서 {context}을 기준으로 화분을 비교합니다.',
           'sections':[{'heading':'선택 상황','paragraph':f'{region}에서 선물을 준비한다면 {context}을 먼저 정리해 주세요.'},
                       {'heading':'주문 정보','paragraph':'상품번호, 상세 주소, 수령 담당자, 희망 수령일을 확인한 뒤 주문 링크에서 상품을 선택합니다.'}],
           'productSkus':SKUS[purpose] if digest%2 else list(reversed(SKUS[purpose])),
           'faq':[{'q':'상품 주문은 어디에서 하나요?','a':'각 상품의 상세 링크에서 확인할 수 있습니다.'}],
           'sourceFlag':source_flag,'pageKind':kind}
        if parent:p['parentPageId']=parent
        pages.append(p)
        regions.append({'name':region,'code':None,'level':kind,'verifiedBy':'2025 candidate inventory; current locality status unverified'})
        return p['id']
    home_id=add(1,'전국','promotion','homepage')
    province_ids={}
    for province in provinces:
        province_ids[province]=add(len(pages)+1,province,'congratulations','province-hub',home_id)
    district_ids={}
    for province,district in districts:
        region=province+' '+district
        district_ids[(province,district)]=add(len(pages)+1,region,'transfer','district-hub',province_ids[province])
    for province,district,locality,flag in rows:
        region=' '.join((province,district,locality))
        purpose=PURPOSES[int(hashlib.sha256(region.encode()).hexdigest()[:8],16)%4]
        add(len(pages)+1,region,purpose,'locality-detail',district_ids[(province,district)],flag)
    assert len(pages)==5302 and len(regions)==5302
    assert Counter(p['pageKind'] for p in pages)=={'locality-detail':5034,'district-hub':250,'province-hub':17,'homepage':1}
    return pages,{'source':str(SOURCE.relative_to(ROOT)),'regions':regions,'candidateOnly':True}
if __name__=='__main__':
    pages,regions=prepare()
    out=ROOT/'reports/promotion-gift-plants/nationwide-input'
    out.mkdir(parents=True,exist_ok=True)
    (out/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'regions.json').write_text(json.dumps(regions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pages':len(pages),'regions':len(regions),'output':str(out)},ensure_ascii=False))
