"""Build inputs for a new isolated V5.1 95-page county condolence wreath trial.

Only writes the new site's paths. No existing site, production release, Access
policy, secret, DNS, or Cloudflare API access. A private protected deployment
cannot be inferred from a robots noindex flag.
"""
from __future__ import annotations
import json,hashlib,re,argparse,zipfile,io,csv
from pathlib import Path
from collections import Counter
from v5.site_plan import initial_spec,validate_plan
from v5.config import ROOT
from scripts.county_copy_pools import purpose_intros,purpose_sections,expanded_pools,county_intents,skus_for,INTENTS

ID='county-funeral-ownerprivate-test'
SITE=ROOT/'sites'/ID
SRC=ROOT/'data/regions/v4_official_parent_regions_20261022.json'
ZIP_SRC=ROOT/'data/regions/v4_official_legal_codes_20261022.zip'
OFFICIAL_ZIP_SHA='44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd'
PAGES_TOTAL=95
PRICES={'B201':59000,'B202':59000,'B205':109000,'B206':149000}
PRODUCTS=[
 ('B201','근조 3단 화환',59000),
 ('B202','근조 3단 화환',59000),
 ('B205','근조 특대 3단 화환',109000),
 ('B206','근조 특특대 3단 화환',149000),
 ('B213','근조 2단 오브제',120000),
 ('B054','근조 쌀화환 10Kg',90000),
 ('B211','근조 영정바구니',59000),
]
PURPOSES=['budget','venue','ribbon']
PROVINCE_PURCHASE_FOCUSES={
  "1200000000": ["받는 장례식장의 소속 군 확인","광역 안내에서 수령 시설이 속한 군 페이지로 이동하면 해당 군의 읍·면을 따로 찾을 수 있습니다. 이름이 비슷한 장례식장은 시설명과 도로명 주소를 함께 구분하는 것이 유용합니다.","조문 일정에 맞춘 수령 정보","장례식장의 빈소 번호와 전달 희망일을 함께 준비할 수 있습니다. 장례 절차 중 빈소가 바뀌었다면 변경된 번호를 주문처에 전달해 수령 혼선을 줄일 수 있습니다."],
  "2600000000": ["단일 군의 장례식장 주소 선택","이 광역의 군 단위 수령지는 기장군 한 곳으로 연결됩니다. 군 페이지에서 실제 수령 시설의 읍·면과 도로명 주소를 확인할 수 있습니다.","수령할 빈소와 연락정보","기장군 장례식장의 빈소 번호와 수령에 필요한 연락 방법을 준비하고 주문할 근조화환의 배송 날짜를 선택할 수 있습니다."],
  "2700000000": ["대구의 두 군에서 수령지 정하기","이 광역의 군 지역을 선택할 때 실제 장례식장의 주소가 달성군인지 군위군인지 확인하면 서로 다른 군 주문 페이지를 구분할 수 있습니다.","조의 리본과 발신 명의","회사·단체에서 보내는 경우 조의 문구와 실제 리본에 인쇄할 정식 단체명을 구분해 준비할 수 있습니다. 개인 명의라면 보내는 분 이름을 따로 적습니다."],
  "2800000000": ["강화와 옹진의 수령 시설 구분","이 광역의 군 수령지는 강화군과 옹진군으로 나뉩니다. 같은 지역명만으로 받는 장례식장의 상세 주소가 정해지지 않으므로 시설 소재지를 군별로 확인할 수 있습니다.","방문하지 않는 조문자의 전달 정보","조문에 직접 참석하지 못하더라도 희망 전달일과 조의 리본 명의를 준비해 판매처에 주문 내용을 전달할 수 있습니다."],
  "3100000000": ["울주군으로 연결되는 광역 페이지","이 광역에는 울주군이 군 단위 선택지로 등록돼 있습니다. 먼저 실제 받는 장례식장 이름과 위치를 확인할 수 있습니다.","반입 위치와 빈소 번호","장례식장에서 꽃을 받는 장소와 빈소가 구분되어 있을 수 있습니다. 시설의 실제 인계 위치를 확인해 받는 곳 정보에 함께 적을 수 있습니다."],
  "4100000000": ["연천군의 오브제 반입 안내","판매처 주요공지사항에는 연천군 모든 장례식장의 반입 형태가 오브제로 기재돼 있습니다. 연천군 페이지에서는 오브제 상품을, 다른 군 상세에서는 각각의 상품과 수령 정보를 안내합니다.","연천군만의 배송표 근거","연천군 상세페이지에는 판매처에서 확인한 오브제 상품의 추가 배송비 근거가 있습니다. 경기 광역 페이지의 일반 3단 카드 가격이 연천 오브제 주문가격을 뜻하지는 않습니다."],
  "4300000000": ["충북 군별 장례식장 찾기","이 광역에 속한 군 중 실제 장례식장 주소를 기준으로 수령 지역을 지정할 수 있습니다. 시설이 있는 읍·면은 군별 안내에서 구체적으로 확인할 수 있습니다.","보내는 명의의 정확한 표기","회사에서 보내는 화환은 법인명이나 부서명을, 개인이 보내는 화환은 발신인 이름을 리본에 적을 수 있습니다. 실제 인쇄할 명칭을 주문 전에 정리합니다."],
  "4400000000": ["충남 군 지역의 수령 장소","군 페이지에서 받는 시설의 위치를 확인한 다음 장례식장명과 빈소를 별개로 기록할 수 있습니다. 같은 시설의 여러 빈소를 혼동하지 않도록 받는 분의 정보가 필요합니다.","조문 문구와 수령인 구분","리본의 조의 문구와 보내는 분의 이름은 서로 다른 표기 항목입니다. 받는 시설 연락처는 수령을 위한 정보이므로 발신 명의와 섞지 않고 작성할 수 있습니다."],
  "4700000000": ["경북 군 선택과 수령지 읍·면","이 광역의 군 페이지에서는 공식 원장에 포함된 읍·면을 확인할 수 있습니다. 실제 수령시설이 어느 읍·면인지 찾아 상세 주소를 주문에 사용할 수 있습니다.","시설별 반입 형태 확인","판매처 공지에는 고령군의 영정바구니와 청도군의 쌀화환 반입 안내가 있습니다. 두 군 페이지는 일반 3단 카드 대신 해당 형태의 상품·분류로 연결됩니다."],
  "4800000000": ["경남 군별 반입 조건","판매처 공지에 따르면 거창군 장례식장은 오브제 형태로 안내됩니다. 해당 군 상세에서 오브제 상품을 찾을 수 있으며, 다른 군의 반입 조건을 거창군 규정으로 단정하지 않습니다.","장례식장명과 빈소 구분","시설마다 수령 장소가 다를 수 있으므로 장례식장 이름·빈소·희망 전달 날짜를 각각 준비할 수 있습니다. 배송 상태는 판매처 주문내역을 통해 확인합니다."],
  "5100000000": ["강원 군 지역의 장례 일정","장례식장 수령 주소는 주문자가 준비해야 할 정보입니다. 군 상세 페이지에서는 해당 군의 읍·면 이름 목록을 확인할 수 있으나 시설별 장례식장명·도로명주소를 제공하지 않습니다.","발신 명의와 수령 시설 분리","리본에 표시할 회사 또는 개인 이름은 장례식장명과 별도로 준비합니다. 상품 선택 화면과 수령지 정보를 구분하면 이름 입력 착오를 줄이는 데 도움이 됩니다."],
  "5200000000": ["전북 군 지역의 대체형 상품","판매처 공지에는 부안군 모든 장례식장의 오브제 반입 안내가 있습니다. 부안군으로 보내는 경우 군 상세의 오브제 상품을 먼저 살펴볼 수 있습니다.","조의 문구와 전달 일시","수령 장례식장의 빈소와 도착 희망일, 리본에 사용할 조의 문구를 구분해 정리하면 주문에 필요한 정보를 한 번에 준비할 수 있습니다."],
}

SOURCE_SHIPPING={}  # Seller B201 county fee applicability was not independently parsed into verified SKU-specific records.
# SKU-scoped seller shipping TABLE facts, re-read 2026-11-08.
# No row found is NOT a zero-fee guarantee. Do not extrapolate across SKUs.
VERIFIED_SHIPPING_FACTS={
 ('횡성군','B201'):{'amount':20000,'scope':'횡성군','exceptions':[],
   'source':'https://fwith.co.kr/shop/item.php?it_id=B201','checkedOn':'2026-11-08',
   'sourceTable':'강원 / 20,000원 / 태백시, 평창군, 횡성군 / -'},
 ('연천군','B213'):{'amount':10000,'scope':'연천군','exceptions':[],
   'source':'https://fwith.co.kr/shop/item.php?it_id=B213','checkedOn':'2026-11-08',
   'sourceTable':'경기 / 10,000원 / 가평군, 연천군, 포천시 / -'},
 ('의성군','B205'):{'amount':10000,'scope':'의성군','exceptions':[],
   'source':'https://fwith.co.kr/shop/item.php?it_id=B205','checkedOn':'2026-11-08',
   'sourceTable':'경북 / 10,000원 / 문경시, 영천시, 예천군, 의성군, 청도군 / -'},
}

# Read-only seller notice observed 2026-11-08; this is a product/venue
# compatibility warning, NOT a delivery promise or an offer for alternative SKU.
SELLER_NOTICE_SOURCE='https://fwith.co.kr/page/notice.php'
RESTRICTED_COUNTY_PRODUCTS={'연천군':('obje',['B213']),'부안군':('obje',['B213']),
 '거창군':('obje',['B213']),'청도군':('rice',['B054']),
 '완도군':('rice-basket',['B054']),'고령군':('basket',['B211'])}
SELLER_NOTICE_SHAPE={
 '연천군':'오브제',
 '부안군':'오브제',
 '거창군':'오브제',
 '고령군':'영정바구니',
 '청도군':'쌀화환',
 '완도군':'쌀화환 또는 꽃바구니',
}

def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def pool(title,intro,choice,delivery,extra,faq):
 # Each FAQ answer must address the question's buying intent; the previous
 # shared address-only answer was irrelevant for budget and ribbon questions.
 if '배송비' in faq:
  answer=('받는 군과 장례식장의 정확한 주소를 정한 뒤 판매처에서 선택한 상품의 배송비 안내를 확인하세요. '
          '해당 주문에 적용되는 배송비와 최종 금액은 주문 화면에서 확인할 수 있습니다.')
 elif '예산' in title:
  answer=('상품 카드에서 예산에 맞는 가격대를 고르고, 원하는 상품번호의 주문 링크를 열어 주세요. '
          '받는 장례식장 주소와 희망일을 입력하면 판매처의 실제 결제금액을 확인할 수 있습니다.')
 elif '리본' in title:
  answer=('선택한 상품의 주문 옵션에서 조의 문구와 보내는 분의 이름을 각각 입력합니다. '
          '주문 확정 전 단체명과 맞춤법을 확인하고, 인쇄 가능 글자 수는 판매처 상세를 참고하세요.')
 elif '장례식장' in title or '수령' in title:
  answer=('받는 장례식장에 근조화환 반입 시간과 설치 가능한 형태를 문의한 뒤, '
          '선택한 상품번호와 희망일을 판매처에 전달해 접수 가능 여부를 확인하세요.')
 else:
  answer=('먼저 수령할 군을 고르고 해당 지역의 상품 카드를 확인하세요. '
          '선택한 근조화환의 판매처 페이지에서 주문 옵션과 배송 정보를 확인할 수 있습니다.')
 return {'productSkus':list(PRICES),
  'introductions':purpose_intros(title,intro),
  'sections':purpose_sections(title,choice,delivery,extra),
  'faqs':[{'q':'근조화환은 어디에서 주문하고 결제하나요?',
           'a':'상품 카드의 ‘상품 보러가기’를 누르면 해당 판매처의 상품 상세페이지로 이동합니다. 주문 옵션과 결제금액을 확인한 뒤 판매처에서 직접 결제할 수 있습니다.'},
          {'q':faq,'a':answer}]}

def main():
 data=json.loads(SRC.read_text(encoding='utf-8'))
 assert data['retrievedOn']=='2026-10-22'
 parents=data['regions']
 assert ZIP_SRC.is_file()
 assert hashlib.sha256(ZIP_SRC.read_bytes()).hexdigest()==OFFICIAL_ZIP_SHA, 'Official frozen legal-code archive changed'
 with zipfile.ZipFile(ZIP_SRC) as zp:
  members=zp.namelist()
  assert len(members)==1
  legal_rows=list(csv.reader(io.StringIO(zp.read(members[0]).decode('cp949')),delimiter=chr(9)))
 assert legal_rows[0][:3]==['법정동코드','법정동명','폐지여부']
 active_lower=[row for row in legal_rows[1:] if len(row)>=3 and row[2].strip()=='존재' and row[1].strip().split()[-1].endswith(('읍','면'))]
 counties=[x for x in parents if x['level']=='municipality' and x['name'].endswith('군') and x['sourceStatus']=='존재']
 all_provinces=[x for x in parents if x['level']=='province' and x['sourceStatus']=='존재']
 county_parent_codes={c['parent'] for c in counties}
 provinces=[p for p in all_provinces if p['code'] in county_parent_codes]
 assert (len(counties),len(all_provinces),len(provinces))==(82,16,12)
 assert len(set(x['code'] for x in counties))==82
 prov_by_code={x['code']:x for x in provinces}
 assert all(x['parent'] in prov_by_code for x in counties)
 # No claims that this old snapshot is the currently effective official naming.
 county_codes={x['code'] for x in counties}
 # A seller table quote is only attached when its official county code matches.
 assert not SOURCE_SHIPPING, 'Never publish unverified county delivery fees'
 pages=[]
 root={'id':'national','number':1,'region':'전국 군 지역','county':'군 지역','province':'전국','parentRegion':'전국',
       'purpose':'national','title':'전국 군 근조화환 지역별 반입 형태와 상품 선택','productSkus':list(PRICES),
       'intro':'전국 군 지역 근조화환 상품별 표시가와 주문 조건을 안내합니다.',
       'sections':[{'heading':'상품 가격','paragraph':'검증된 판매상품 정보를 안내합니다.'},
                   {'heading':'주문 조건','paragraph':'수령지와 배송비를 확인할 수 있습니다.'}],
       'faq':[],'pageType':'national'}
 pages.append(root)
 pnums={}
 for p in sorted(provinces,key=lambda x:x['code']):
  num=len(pages)+1;pnums[p['code']]=num
  pages.append({'id':'province-'+p['code'],'number':num,'region':p['fullName'],'county':'관내 군 지역',
    'province':p['fullName'],'parentRegion':'전국','parentPageId':'national',
    'purpose':'province-'+p['code'],'title':p['fullName']+' 근조화환 군 지역별 상품과 가격',
    'productSkus':list(PRICES),'intro':p['fullName']+' 근조화환 선택 안내입니다.',
    'sections':[{'heading':'상품','paragraph':'상품 가격과 구성 확인'},
                {'heading':'주문','paragraph':'받는 시설 확인'}],
    'faq':[],'pageType':'province','officialCode':p['code']})
 for i,c in enumerate(sorted(counties,key=lambda x:x['code'])):
  p=prov_by_code[c['parent']]
  lower=[(row[0].strip(),row[1].strip().split()[-1])
         for row in active_lower
         if row[0].startswith(c['code'][:5]) and row[1].strip().startswith(c['fullName']+' ')]
  lower.sort()
  township_names=[item[1] for item in lower]
  assert len(township_names)>0 and len(set(township_names))==len(township_names),(c['code'],c['fullName'],township_names)
  restricted=RESTRICTED_COUNTY_PRODUCTS.get(c['name'])
  purpose=(('restricted-obje-'+c['name']) if restricted and restricted[0]=='obje' else
           ('restricted-'+restricted[0]) if restricted else county_intents()[i%len(county_intents())])
  # Headline must reflect the chosen buyer decision, not a generic SEO template.
  purpose_heading=({'obje':'근조 오브제','rice':'근조 쌀화환','rice-basket':'근조 쌀화환·바구니','basket':'영정바구니'}[restricted[0]] if restricted
                   else next(row[3] for row in INTENTS if row[0]==purpose))
  num=len(pages)+1
  pages.append({'id':'county-'+c['code'],'number':num,'region':c['fullName'],
   'county':c['name'],'province':p['fullName'],'parentRegion':p['fullName'],
   'parentPageId':'province-'+p['code'],'purpose':purpose,
   'title':(c['name']+' 근조화환 | B205 추가 배송비와 상품 주문' if c['name']=='의성군' else c['name']+' 근조화환 | '+purpose_heading+('·반입 안내' if restricted else '' if purpose in ('budget-entry','ribbon-text') else '·상품 주문')),
   'productSkus':list(restricted[1]) if restricted else skus_for(purpose),
   'intro':c['name']+' 장례식장에 보내는 근조상품의 반입 형태와 주문 정보를 안내합니다.' if restricted else c['name']+' 근조화환 상품 가격과 수령지 안내.',
   'sections':[{'heading':'상품 선택','paragraph':'같은 상품 유형의 표시가를 확인할 수 있습니다.'},
               {'heading':'주문 요청','paragraph':'받는 시설명과 주소를 확인할 수 있습니다.'}],
   'faq':[],'pageType':'county','officialCode':c['code'],
   'shippingEvidence':SOURCE_SHIPPING.get(c['code']),
   'verifiedSkuShipping':[
      {'sku':sku,**fact} for (county,sku),fact in VERIFIED_SHIPPING_FACTS.items()
      if county==c['name'] and sku in (list(restricted[1]) if restricted else skus_for(purpose))
   ],
   'sellerVenueNotice':({
       'text':'판매처 공지: '+c['name']+' 모든 장례식장 - '+SELLER_NOTICE_SHAPE[c['name']]+'.',
       'sourceUrl':SELLER_NOTICE_SOURCE,'checkedOn':'2026-11-08',
       'alternativeUrl':None,
       'alternativeName':None
   } if c['name'] in SELLER_NOTICE_SHAPE else None),
   'siteVariantPolicy':'county-v51','variantIndex':i//len(county_intents()),
   'townships':'·'.join(township_names),'townshipCount':str(len(township_names)),
   'officialTownshipCodes':[x[0] for x in lower]})
 assert len(pages)==PAGES_TOTAL
 assert all(x['pageType']!='county' or x['id']!='national' for x in pages)
 region_list=[{'name':x['region'],'code':x.get('officialCode','national'),'level':x['pageType']} for x in pages]
 spec=initial_spec(ID,'근조화환 가격 안내','근조화환','전국','1844-0644')
 spec.update({
  'approved':True,'domain':'https://county-funeral-ownerprivate.invalid','businessModel':'webshop',
  'serviceScope':{'region':'전국','granularity':'county','facilities':None},
  'pageTypes':['national','province','county'],'targetPageCount':95,
  'titlePattern':'{county} 근조화환 가격·상품 선택','urlPattern':'/{number}.html',
  'keywordGroups':{'primary':['군 근조화환','근조화환 가격'],'secondary':['화환 추가 배송비','근조 리본 문구']},
  'copyPoolPlan':{'industry':'condolence-flower','source':'pinned-fwith-2026-11-07','sentenceTarget':5},
  'similarityAudit':{'metric':'char-5gram-jaccard','thresholdExclusive':0.49,'sampleFraction':0.01,'seed':20261107},
  'conversion':{'mode':'shop','phone':'1844-0644','orderUrl':'https://fwith.co.kr/shop/item.php?it_id=B201'},
  'images':{'source':'original CSS+SVG decoration only','approved':False},
  'publishPolicy':{'mode':'owner-private-preview-only','indexNow':False},
  'research':{'topic':[{'source':'https://www.code.go.kr/etc/codeFullDown.do','checkedOn':'2026-11-07'}],
   'price':[{'source':'https://fwith.co.kr/shop/item.php?it_id=B201','checkedOn':'2026-11-07'}],
   'order':[{'source':'https://fwith.co.kr/shop/item.php?it_id=B205','checkedOn':'2026-11-07'}]},
  'purposePools':expanded_pools({
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
    '리본 문구와 보낸 사람 이름은 어디에 적나요?')})
 })
 # Venue-wide rules select one appropriate product cohort BEFORE assembling prose.
 # A basket-only category has no SKU-confirmed seller item: show no SKU or price
 # instead of misdirecting visitors to 3-tier wreaths or inventing a listing.
 special_pools={
  'restricted-obje':{
   'productSkus':['B213'],
   'introductions':['{county} 장례식장에 보낼 근조 2단 오브제의 상품정보와 수령지 안내입니다.'],
   'sections':[
    {'slot':'choice','heading':'판매처 상품 고시','paragraph':'B213 판매처 상세에는 상품 선택옵션 0개·추가옵션 0개로 표시되고, 재생 꽃을 사용하지 않는다고 고시돼 있습니다.'},
    {'slot':'order','heading':'수령 시설 정보','paragraph':'장례식장 이름과 정확한 빈소, 희망 전달일을 정한 뒤 상품 주문 화면에서 접수 가능한 일정을 확인할 수 있습니다.'},
    {'slot':'verified-townships','heading':'{county} 읍·면','paragraph':'{county}의 읍·면: {townships}. 수령할 시설의 상세주소를 지정해 주세요.'}],
   'faqs':[{'q':'오브제 상품 배송료는 언제 확인하나요?','a':'B213 상품의 수령지 주소를 지정한 뒤 판매처 주문 화면에서 배송료와 주문 총액을 확인할 수 있습니다.'}]},
  'restricted-rice':{
   'productSkus':['B054'],
   'introductions':['{county} 모든 장례식장은 판매처 공지에서 쌀화환 형태를 안내합니다. 근조 쌀화환 10Kg B054 주문 정보와 반입 안내를 확인할 수 있습니다.'],
   'sections':[
    {'slot':'choice','heading':'쌀화환 상품','paragraph':'근조 쌀화환 10Kg B054는 쌀화환 반입 안내에 맞는 상품군입니다. 상품번호와 장례식장 주소를 함께 확인해 주문할 수 있습니다.'},
    {'slot':'order','heading':'빈소로 보낼 정보','paragraph':'장례식장명과 빈소, 희망 날짜를 정해 해당 상품 주문 화면에 전달해 주세요.'},
    {'slot':'verified-townships','heading':'{county} 읍·면','paragraph':'{county}의 읍·면: {townships}. 해당 시설이 있는 주소를 지정해 주세요.'}],
   'faqs':[{'q':'배송 조건은 어디에서 확인하나요?','a':'B054 상품의 주문 화면에서 수령지에 적용되는 배송비와 주문 가능 여부를 확인할 수 있습니다.'}]},
  'restricted-rice-basket':{
   'productSkus':['B054'],
   'introductions':['{county} 장례식장은 판매처 공지에서 쌀화환과 바구니를 반입 형태로 안내합니다. 쌀화환 10Kg 상품 또는 영정바구니 분류를 선택할 수 있습니다.'],
   'sections':[
    {'slot':'choice','heading':'쌀화환 또는 바구니','paragraph':'근조 쌀화환 10Kg B054의 표시가격은 90,000원입니다. 영정바구니는 판매처 분류에서 상품별 정보를 확인할 수 있습니다.'},
    {'slot':'order','heading':'완도군 수령 정보','paragraph':'장례식장 이름과 빈소, 수령 날짜를 준비하고 원하는 형태를 판매처에 전달해 주세요.'},
    {'slot':'verified-townships','heading':'{county} 읍·면','paragraph':'{county}에 속한 읍·면은 {townships}입니다. 정확한 장례식장 주소를 확인해 주세요.'}],
   'faqs':[{'q':'쌀화환 대신 영정바구니를 선택할 수 있나요?','a':'판매처 공지에는 완도군 장례식장에 쌀화환과 바구니가 안내됩니다. 선택할 상품은 해당 상품 분류와 장례식장의 반입 조건을 함께 확인할 수 있습니다.'}]},
  'restricted-basket':{
   'productSkus':['B211'],
   'introductions':['{county} 장례식장에 보낼 영정바구니 상품의 판매처 표시가격과 수령지 정보를 정리했습니다.'],
   'sections':[
    {'slot':'choice','heading':'조의 리본 문구','paragraph':'“삼가 고인의 명복을 빕니다”와 “깊은 애도를 표합니다”는 영정바구니에 사용할 수 있는 조의 문구입니다. 보내는 분이나 단체 이름은 문구와 구분해 준비할 수 있습니다.'},
    {'slot':'order','heading':'시설과 빈소','paragraph':'장례식장명과 빈소를 정한 뒤 판매처에 영정바구니 주문 가능 여부를 확인해 주세요.'},
    {'slot':'verified-townships','heading':'{county} 읍·면','paragraph':'{county}의 읍·면: {townships}. 해당 시설의 상세 주소를 준비해 주세요.'}],
   'faqs':[]}
 }
 # County-only verified venue restrictions share SKU B213 but must not become
 # three identical SEO articles. Different buying tasks and official 읍/면 lists
 # make the owner-private pages useful without inventing florist or facility data.
 import copy
 obje_actions={
  '연천군':('장례식장과 빈소 선택',
    '연천군에서 오브제를 받는 장례식장명·빈소·받는 분 연락 방법을 구분해 주세요. 주문할 때는 정확한 시설 주소를 입력할 수 있습니다.',
    '연천군 오브제 배송비는 어떻게 확인하나요?',
    'B213 판매처의 2026-11-08 배송정보 표에 연천군 추가 배송비는 10,000원으로 기재돼 있습니다. 표에서 연천군 읍면의 별도 예외 행은 확인되지 않았습니다. 해당 금액은 B213 안내이며 실제 결제금액은 주문 시 확인됩니다.'),
  '부안군':('희망 전달일과 빈소 정보',
    '부안군 장례식장의 빈소 번호와 도착 희망일을 준비하면 B213 상품 주문에 필요한 수령 정보를 전달할 수 있습니다.',
    'B213 판매처 상품 페이지에서 주문은 어떻게 시작하나요?',
    '판매처 B213 상품 상세에는 수량 조절, 바로구매, 장바구니 버튼이 있습니다. 수량을 고른 뒤 원하는 주문 경로를 선택할 수 있습니다.'),
  '거창군':('리본 발신인과 수령 정보',
    '거창군 빈소에 전달할 조의 문구와 보내는 분의 이름을 정리하고, 실제 꽃을 받을 장례식장명과 빈소 정보를 함께 준비해 주세요.',
    '거창군 오브제 리본에는 어떤 이름을 적나요?',
    '상품 상세에는 선택옵션 0개·추가옵션 0개로 표시됩니다. 리본 문구 입력 방법은 판매처 고객센터 1844-0644에서 확인할 수 있습니다.')
 }
 for c in counties:
  if c['name'] not in obje_actions:continue
  label,detail,question,answer=obje_actions[c['name']]
  unique=copy.deepcopy(special_pools['restricted-obje'])
  unique['introductions']=[c['name']+' 근조 2단 오브제의 수령 시설 정보와 판매처 상품고시를 정리했습니다.']
  unique['sections'][1]={'slot':'order','heading':label,'paragraph':detail}
  unique['sections'][2]={'slot':'verified-townships','heading':c['name']+' 읍·면별 수령지','paragraph':c['name']+'의 읍·면 명칭은 {townships}입니다. 실제 받는 장례식장이 속한 읍·면과 도로명 주소를 확인해 주문해 주세요.'}
  unique['faqs']=[{'q':question,'a':answer}]
  special_pools['restricted-obje-'+c['name']]=unique
 spec['purposePools'].update(special_pools)
 # National and province pages only show county-bearing province coverage.
 national=pool('전국 근조화환 상품 선택',
    '전국 군 지역의 근조화환 가격과 실제 주문 링크를 살펴볼 수 있습니다.',
    'B201·B202는 각 59,000원, B205는 109,000원, B206은 149,000원입니다. 상품별 꽃 구성·크기는 판매처 상세에 따릅니다.',
    '군별 배송 추가비와 읍·면 예외는 받는 시설의 상세 주소를 기준으로 판매처에서 확인할 수 있습니다.',
    '받는 군과 장례식장 주소, 희망일, 리본 문구를 준비하면 실제 결제 총액을 확인할 수 있습니다.',
    '군 지역 화환의 배송비는 어떻게 확인하나요?')
 national['introductions']=['전국 82개 군 중 장례식장 소재지를 선택하면 해당 지역의 반입 형태와 주문 가능한 상품 종류를 살펴볼 수 있습니다.']
 # The home already has the entire province navigator and four price cards;
 # repeating prices, shipment caveats and checkout instructions across five
 # generic sections + two FAQs produced the independent 82/100 rejection.
 national['sections']=[
  {'slot':'choice','heading':'받는 군에 따라 달라지는 상품 유형',
   'paragraph':'판매처 공지에서 연천군·부안군·거창군은 오브제, 고령군은 영정바구니, 청도군은 쌀화환, 완도군은 쌀화환 또는 꽃바구니 형태로 안내합니다. 이 군에서는 해당 지역 상세 페이지의 상품군을 먼저 확인할 수 있습니다.'},
  {'slot':'order','heading':'수령할 장례식장 정보',
   'paragraph':'수령 시설이 있는 군을 고르면 해당 군의 읍·면 목록과 주문 가능한 상품 링크를 확인할 수 있습니다. 주문할 때 필요한 장례식장명·빈소·희망 날짜를 준비할 수 있습니다.'}
 ]
 national['faqs']=[
  {'q':'군 지역의 배송료와 주문 합계는 어떻게 확인하나요?',
   'a':'선택한 상품의 주문 화면에서 정확한 장례식장 주소를 입력하면 적용 배송료와 옵션 비용을 포함한 금액을 확인할 수 있습니다.'}
 ]
 province=pool('광역 지역별 군 근조화환',
    '{province}에 속한 군 지역의 근조화환 상품 표시가와 주문 연결을 확인할 수 있습니다.',
    '{province}의 군 지역으로 보낼 근조화환 상품 B201·B202·B205·B206의 가격과 유형을 비교합니다.',
    '수령 시설의 읍·면 상세 주소를 기준으로 추가 배송비와 주문 가능 여부를 상담할 수 있습니다.',
    '관내 군 지역을 선택한 뒤 장례식장명과 빈소·희망일을 판매처에 전달할 수 있습니다.',
    '해당 광역 지역의 군 근조화환을 어떻게 주문하나요?')
 province['introductions']=['{province}에서 근조화환을 보낼 군을 고르면 상품별 주문 링크와 수령 시설 정보를 확인할 수 있습니다.']
 province['sections']=[
  {'slot':'choice','heading':'어느 군으로 보낼지 정하기',
   'paragraph':'수령할 장례식장이 있는 군을 위 지역 목록에서 선택해 주세요. 근조화환 상품은 코드별로 구분되며 가격과 구성은 각 상품 카드·상세 화면에서 비교할 수 있습니다.'},
  {'slot':'order','heading':'장례식장 수령 정보',
   'paragraph':'장례식장명·도로명 주소·빈소와 희망 전달 날짜가 정해지면 선택한 화환의 주문 화면에서 필요한 정보를 입력할 수 있습니다.'}
 ]
 province['faqs']=[
  {'q':'선택한 군의 추가 배송비는 어디서 확인하나요?',
   'a':'상품번호와 장례식장 도로명 주소를 판매처 주문 화면에 입력하면 해당 주소의 배송비·접수 가능 여부·결제금액을 확인할 수 있습니다.'}
 ]
 spec['purposePools']['national']=national
 spec['purposePools']['province']=province
 # Only counties attested by the pinned official parent ledger are listed.
 for p in provinces:
  names=[c['name'] for c in counties if c['parent']==p['code']]
  assert names
  scope=__import__('copy').deepcopy(province)
  joined='·'.join(names)
  scope['introductions']=[p['fullName']+'의 군 지역 '+str(len(names))+'곳을 대상으로 장례식장 소재지에 맞는 근조상품 안내를 제공합니다.']
  # Province-specific sources prevent county name substitution alone.
  # Compare each county against the actual ledger before rendering.
  assert len(names)>0
  # Information ownership: two independently authored provincial buying
  # decisions plus one official county inventory. The old generic choice/order
  # paragraphs repeated these sections without adding information.
  focus=PROVINCE_PURCHASE_FOCUSES[p['code']]
  # Information owner: child names already appear as links in regional nav.
  # Never repeat the same full county list in prose or invent filler sections.
  scope['sections']=[
   {'slot':'choice','heading':focus[0],'paragraph':focus[1]},
   {'slot':'order','heading':focus[2],'paragraph':focus[3]},
  ]
  spec['purposePools']['province-'+p['code']]=scope
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
    'referenceDate':('2026-11-08' if sku in ('B213','B054','B211') else '2026-11-07'),'priceConfirmed':True,
    'priceEvidence':('2026-11-08 seller category list https://fwith.co.kr/shop/list.php?ca_id=20 B211 direct item listing' if sku=='B211' else '2026-11-08 seller product or category listing readback, source https://fwith.co.kr/shop/item.php?it_id='+sku if sku in ('B213','B054') else '2026-11-07 09:53 UTC direct read-only HTTP200 SKU and listed price and 주문시 배송비 결제; source run 42361620276'),
    'priceCheckedOn':('2026-11-08' if sku in ('B213','B054','B211') else '2026-11-07'),'orderUrl':'https://fwith.co.kr/shop/item.php?it_id='+sku,
    'verifiedLive':False,'imageUseApproved':False,
    'verifiedSource':True})
 products.append({'sku':'CAT2090','name':'영정바구니 상품 분류',
   'referencePrice':None,'priceConfirmed':False,'priceEvidence':None,
   'priceCheckedOn':None,'orderUrl':'https://fwith.co.kr/shop/list.php?ca_id=2090',
   'isCategoryLink':True,'imageUseApproved':False,'verifiedSource':True})
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
   'sourceRetrievedOn':'2026-10-22','currentOfficialComparedUTC':'2026-11-07T10:01:16Z','currentOfficialReadbackRun':42362139861,'currentOfficialArchiveMatches':True,'sourceArchiveSHA256':'44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd','sourceBlobSHA':'13d43fc3f2492b29b1680858235fe0ac0cd10580',
   'countyCount':len(counties),'provinceCount':len(provinces),'excludedProvincesWithoutCounty':[p['fullName'] for p in all_provinces if p['code'] not in county_parent_codes],'targetCount':len(pages),
   'countyCodes':[x['code'] for x in counties],
   'deliveryFeeSpecificCases':SOURCE_SHIPPING,
   'skuShippingSourceRows':[{'county':county,'sku':sku,**fact}
      for (county,sku),fact in VERIFIED_SHIPPING_FACTS.items()],
   'shippingEvidenceState':'No county-specific amount accepted until exact B201 source rows, 읍/면 exceptions and checkout calculation are verified',
   'priceReadback':'2026-11-07 09:53 UTC independent HTTP200 four SKU price/delivery readback, GitHub run 42361620276',
   'imageUsage':'Only new owned simple SVG illustration. No seller image copied.',
   'privateDeploymentReady':False,'productionHost':None})
 print('V51_COUNTY_TRIAL_INPUTS_BUILT='+json.dumps({'siteId':ID,'totalPages':len(pages),
   'counties':len(counties),'provinces':len(provinces),'purposes':dict(Counter(x['purpose'] for x in pages))},ensure_ascii=False))
if __name__=='__main__':main()
