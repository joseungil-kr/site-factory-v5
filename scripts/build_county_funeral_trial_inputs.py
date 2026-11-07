"""Build inputs for a new isolated V5.1 99-page county condolence wreath trial.

Only writes the new site's paths. No existing site, production release, Access
policy, secret, DNS, or Cloudflare API access. A private protected deployment
cannot be inferred from a robots noindex flag.
"""
from __future__ import annotations
import json,hashlib,re,argparse
from pathlib import Path
from collections import Counter
from v5.site_plan import initial_spec,validate_plan
from v5.config import ROOT
from scripts.county_copy_pools import purpose_intros,purpose_sections

ID='county-funeral-ownerprivate-test'
SITE=ROOT/'sites'/ID
SRC=ROOT/'data/regions/v4_official_parent_regions_20261022.json'
PAGES_TOTAL=99
PRICES={'B201':59000,'B202':59000,'B205':109000,'B206':149000}
PRODUCTS=[
 ('B201','근조화환 B201',59000),
 ('B202','근조화환 B202',59000),
 ('B205','근조 특대 3단 화환 B205',109000),
 ('B206','근조화환 B206',149000),
]
PURPOSES=['budget','venue','ribbon']
SOURCE_SHIPPING={}  # Seller B201 county fee applicability was not independently parsed into verified SKU-specific records.
def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def pool(title,intro,choice,delivery,extra,faq):
 return {'productSkus':list(PRICES),
  'introductions':purpose_intros(title,intro),
  'sections':purpose_sections(title,choice,delivery,extra),
  'faqs':[{'q':'상품 가격에 배송비가 포함되나요?','a':'판매처는 주문 시 배송비를 결제하도록 안내합니다. 군·읍·면별 추가금과 총액은 수령지 확인 후 결정됩니다.'},
          {'q':faq,'a':'받는 시설명과 상세 주소, 희망 수령시간을 판매처에 전달하면 실제 접수 조건을 확인할 수 있습니다.'}]}
def main():
 data=json.loads(SRC.read_text(encoding='utf-8'))
 assert data['retrievedOn']=='2026-10-22'
 parents=data['regions']
 counties=[x for x in parents if x['level']=='municipality' and x['name'].endswith('군') and x['sourceStatus']=='존재']
 provinces=[x for x in parents if x['level']=='province' and x['sourceStatus']=='존재']
 assert (len(counties),len(provinces))==(82,16)
 assert len(set(x['code'] for x in counties))==82
 prov_by_code={x['code']:x for x in provinces}
 assert all(x['parent'] in prov_by_code for x in counties)
 # No claims that this old snapshot is the currently effective official naming.
 county_codes={x['code'] for x in counties}
 # A seller table quote is only attached when its official county code matches.
 assert not SOURCE_SHIPPING, 'Never publish unverified county delivery fees'
 pages=[]
 root={'id':'national','number':1,'region':'전국','county':'전국','province':'전국','parentRegion':'전국',
       'purpose':'budget','title':'전국 군 근조화환 가격과 상품 안내','productSkus':list(PRICES),
       'intro':'전국 군 지역 근조화환 상품별 표시가와 주문 조건을 안내합니다.',
       'sections':[{'heading':'상품 가격','paragraph':'검증된 판매상품 정보를 안내합니다.'},
                   {'heading':'주문 조건','paragraph':'수령지와 배송비를 확인할 수 있습니다.'}],
       'faq':[],'pageType':'national'}
 pages.append(root)
 pnums={}
 for p in sorted(provinces,key=lambda x:x['code']):
  num=len(pages)+1;pnums[p['code']]=num
  pages.append({'id':'province-'+p['code'],'number':num,'region':p['fullName'],'county':'각 군',
    'province':p['fullName'],'parentRegion':'전국','parentPageId':'national',
    'purpose':'venue','title':p['fullName']+' 군 근조화환 상품과 가격',
    'productSkus':list(PRICES),'intro':p['fullName']+' 근조화환 선택 안내입니다.',
    'sections':[{'heading':'상품','paragraph':'상품 가격과 구성 확인'},
                {'heading':'주문','paragraph':'받는 시설 확인'}],
    'faq':[],'pageType':'province','officialCode':p['code']})
 for i,c in enumerate(sorted(counties,key=lambda x:x['code'])):
  p=prov_by_code[c['parent']]
  purpose=PURPOSES[i%len(PURPOSES)]
  num=len(pages)+1
  pages.append({'id':'county-'+c['code'],'number':num,'region':c['fullName'],
   'county':c['name'],'province':p['fullName'],'parentRegion':p['fullName'],
   'parentPageId':'province-'+p['code'],'purpose':purpose,
   'title':c['name']+' 근조화환 가격·상품 선택 | 군 근조화환 안내',
   'productSkus':list(PRICES),'intro':c['name']+' 근조화환 상품 가격과 수령지 안내.',
   'sections':[{'heading':'상품 선택','paragraph':'같은 상품 유형의 표시가를 확인할 수 있습니다.'},
               {'heading':'주문 요청','paragraph':'받는 시설명과 주소를 확인할 수 있습니다.'}],
   'faq':[],'pageType':'county','officialCode':c['code'],
   'shippingEvidence':SOURCE_SHIPPING.get(c['code'])})
 assert len(pages)==PAGES_TOTAL
 assert all(x['pageType']!='county' or x['id']!='national' for x in pages)
 region_list=[{'name':x['region'],'code':x.get('officialCode','national'),'level':x['pageType']} for x in pages]
 spec=initial_spec(ID,'근조화환 가격 안내','근조화환','전국','1844-0644')
 spec.update({
  'approved':True,'domain':'https://county-funeral-ownerprivate.invalid','businessModel':'webshop',
  'serviceScope':{'region':'전국','granularity':'county','facilities':None},
  'pageTypes':['national','province','county'],'targetPageCount':99,
  'titlePattern':'{county} 근조화환 가격·상품 선택','urlPattern':'/{number}.html',
  'keywordGroups':{'primary':['군 근조화환','근조화환 가격'],'secondary':['화환 추가 배송비','근조 리본 문구']},
  'copyPoolPlan':{'industry':'condolence-flower','source':'pinned-fwith-2026-11-07','sentenceTarget':5},
  'similarityAudit':{'metric':'char-5gram-jaccard','thresholdExclusive':0.49,'sampleFraction':0.01,'seed':20261107},
  'conversion':{'mode':'shop','phone':'1844-0644','orderUrl':'https://fwith.co.kr/shop/item.php?it_id=B201'},
  'images':{'source':'original CSS+SVG decoration only','approved':False},
  'publishPolicy':{'mode':'owner-private-preview-only','indexNow':False},
  'research':{'topic':[{'source':'https://www.code.go.kr/stdcode/regCodeL.do','checkedOn':'2026-10-22'}],
   'price':[{'source':'https://fwith.co.kr/shop/item.php?it_id=B201','checkedOn':'2026-11-07'}],
   'order':[{'source':'https://fwith.co.kr/shop/item.php?it_id=B205','checkedOn':'2026-11-07'}]},
  'purposePools':{
   'budget':pool('근조화환 예산 선택',
    '{county} 근조화환은 B201/B202 표시가 59,000원과 B205 109,000원, B206 149,000원을 비교할 수 있습니다.',
    '상품 기준가는 59,000원·59,000원·109,000원·149,000원입니다. 상품별 실제 구성·치수와 최종 배송비는 상세 주문 과정에서 확인할 수 있습니다.',
    '{province}의 군별 배송 추가금 안내에는 읍·면 예외가 있을 수 있습니다. 판매처 주문 화면에 표시되는 배송비와 옵션을 확인한 후 결제할 수 있습니다.',
    '기준가를 기준으로 예산을 정하고, 수령지와 리본 문구를 입력한 뒤 최종 합계를 확인할 수 있습니다.',
    '예산 내 근조화환을 고르는 순서는?'),
   'venue':pool('장례식장 수령 안내',
    '{province} {county} 지역 근조화환은 수령 시설과 장례식장 반입 조건을 확인한 후 상품을 선택할 수 있습니다.',
    '장례식장에 설치할 근조화환은 시설명과 빈소 정보를 확인하면 수령 시 혼선을 줄일 수 있습니다. 표시 상품가는 59,000원부터 149,000원까지입니다.',
    '수령 시설의 위치와 반입 조건에 따라 추가 배송비와 배송 가능 시각이 달라질 수 있습니다.',
    '받는 곳 이름·빈소·수령 날짜를 정확하게 전달하면 판매처가 해당 주소의 접수 조건을 안내합니다.',
    '장례식장 반입 가능 여부는 어떻게 확인하나요?'),
   'ribbon':pool('근조 리본 문구와 상품 형태',
    '{county} 근조화환은 보내는 분의 이름과 조의 문구를 준비하고 실제 상품 옵션을 선택할 수 있습니다.',
    '근조 리본에는 보내는 사람·단체 이름과 조의 문구가 들어갑니다. 원하시는 표기와 오탈자를 주문 단계에서 확인할 수 있습니다.',
    '배송비는 주문 시 결제 안내가 있으며 추가요금은 최종 수령지 기준으로 확인합니다.',
    '동일한 가격의 B201과 B202도 실제 구성은 상품 상세를 기준으로 비교해야 합니다. 리본 비용과 꽃 품종·크기는 선택한 상품의 표시 내용을 따릅니다.',
    '리본 문구와 보낸 사람 이름은 어디에 적나요?')}
 })
 result=validate_plan(spec,ID)
 assert result['ready'],result['errors']
 site={
  'id':ID,'brand':'근조화환 가격 안내','siteTitle':'전국 군 근조화환',
  'domain':None,'workerName':None,'locale':'ko-KR','phone':'1844-0644',
  'keyword':'근조화환','region':'전국','theme':'classic',
  'imagePool':['county-wreath.svg'],'imageLibrary':ID,
  'orderBaseUrl':'https://fwith.co.kr','publishEnabled':False,'publicIndexingApproved':False,
  'analytics':{'enabled':False},'siteSearch':{'enabled':False},
  'staticAssetSoftLimit':18000,'source':'Seller listing and pinned 2026-10-22 legal region codes; trial only',
  'imageAssetsApproved':False,'cookiePrivacyReviewed':False,
  'indexNow':{'enabled':False,'key':None},
  'navigation':[{'label':'전국 군 안내','href':'/'}]
 }
 products=[]
 for sku,name,price in PRODUCTS:
  products.append({'sku':sku,'name':name,'referencePrice':price,
    'referenceDate':'2026-11-07','priceConfirmed':True,
    'priceEvidence':'User-supplied independent HTTP 200 seller readback on 2026-11-07 08:49 UTC; '+('additional web readback for B205' if sku=='B205' else 'assistant direct web readback incomplete'),
    'priceCheckedOn':'2026-11-07','orderUrl':'https://fwith.co.kr/shop/item.php?it_id='+sku,
    'verifiedLive':False,'imageUseApproved':False,
    'verifiedSource':sku=='B205'})
 assert all(x['imageUseApproved'] is False for x in products)
 SITE.mkdir(parents=True,exist_ok=True)
 dump(SITE/'site.json',site)
 dump(SITE/'pages.json',pages)
 dump(SITE/'products.json',products)
 dump(SITE/'links.json',[])
 dump(SITE/'special-pages.json',[])
 dump(SITE/'regions.json',{'source':'pinned 2026-10-22 official code ZIP','regions':region_list})
 dump(SITE/'site-spec.json',spec)
 dump(SITE/'county-plan-evidence.json',{'sourceFile':str(SRC.relative_to(ROOT)),
   'sourceRetrievedOn':'2026-10-22','sourceBlobSHA':'13d43fc3f2492b29b1680858235fe0ac0cd10580',
   'countyCount':len(counties),'provinceCount':len(provinces),'targetCount':len(pages),
   'countyCodes':[x['code'] for x in counties],
   'deliveryFeeSpecificCases':SOURCE_SHIPPING,
   'shippingEvidenceState':'No county-specific amount accepted until exact B201 source rows, 읍/면 exceptions and checkout calculation are verified',
   'priceReadback':'User confirmed HTTP 200 2026-11-07 08:49 UTC; assistant web direct readback B205 only',
   'imageUsage':'Only new owned simple SVG illustration. No seller image copied.',
   'privateDeploymentReady':False,'productionHost':None})
 print('V51_COUNTY_TRIAL_INPUTS_BUILT='+json.dumps({'siteId':ID,'totalPages':len(pages),
   'counties':len(counties),'provinces':len(provinces),'purposes':dict(Counter(x['purpose'] for x in pages))},ensure_ascii=False))
if __name__=='__main__':main()
