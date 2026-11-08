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
 ('B202','근조화환 B202',59000),
 ('B205','근조 특대 3단 화환',109000),
 ('B206','근조 특특대 3단 화환',149000),
 ('B213','근조 2단 오브제',120000),
 ('B054','근조 쌀화환 10Kg',90000),
]
PURPOSES=['budget','venue','ribbon']
PROVINCE_PURCHASE_FOCUSES={
  "1200000000": [
    "군 지역을 순서대로 고르기",
    "군 이름이 여러 개라면 받는 분의 장례식장 주소가 어느 군에 속하는지 확인한 후 상품을 고릅니다. 표시가 59,000원의 B201과 B202는 상품 코드가 다르므로 각 상세 페이지에서 구성과 옵션을 비교할 수 있습니다.",
    "주문 장소 확정",
    "선택한 군과 빈소 이름을 한 줄로 적는 것보다 도로명 주소와 시설명을 별도로 전달하면 수령지가 분명해집니다. 이어서 B205와 B206의 기준가 차이 40,000원을 비교하고 실제 배송비를 주문 화면에서 확인합니다."
  ],
  "2600000000": [
    "한 개 군 지역의 주문 흐름",
    "이 목록에는 기장군 한 곳만 포함됩니다. 광역 지역을 추가로 선택할 필요 없이 실제 수령 시설명을 정하고 주문 링크로 이동할 수 있습니다. B201과 B202는 기준가가 같아 상세 구성 차이를 먼저 비교하는 방식이 적합합니다.",
    "수령지 입력 항목",
    "장례식장 이름뿐 아니라 주소와 빈소·희망일이 주문 내용에 반영되어야 합니다. 지정한 장소의 추가 배송비를 확인한 뒤 최종 합계를 비교할 수 있습니다. 배송 요금과 주문 가능 시각은 수령 시설의 실제 주소를 기준으로 안내됩니다."
  ],
  "2700000000": [
    "두 군 중 받는 곳 선택",
    "달성군과 군위군 가운데 실제 수령 시설의 주소가 있는 군을 고르면 해당 페이지로 이동할 수 있습니다. B205(109,000원)와 B206(149,000원)의 차이는 기준가 40,000원이며 꽃의 규격 차이는 상품 상세로 확인합니다.",
    "상품과 보내는 이름",
    "상품을 선택한 뒤 리본에 적을 조의 문구와 보내는 분의 명칭을 준비합니다. 해당 군 페이지는 시설의 접수 조건과 주문서 배송비 확인 방법을 안내하며, 두 군의 배송 요금이 같다고 가정하지 않습니다."
  ],
  "2800000000": [
    "수령 군 확인과 주소 선택",
    "강화군과 옹진군 중 실제 주문하려는 시설의 주소가 있는 곳을 선택합니다. 군 이름이 같더라도 주소가 정확하지 않으면 접수 조건을 확인하기 어렵습니다. 상품별 사진·구성·표시가를 먼저 살펴볼 수 있습니다.",
    "희망 일정 준비",
    "받는 시설의 빈소명과 연락 방법, 도착 희망 날짜를 분리해 전달합니다. 추가 배송비와 실제 접수 가능 시간은 판매처 주문 단계에서 확인할 수 있으며 군 이름만으로 확정적인 약속을 만들지 않습니다."
  ],
  "3100000000": [
    "한 군의 근조상품 비교",
    "울주군 하나가 해당 광역 목록의 군 페이지로 연결됩니다. 59,000원에 표시된 B201·B202 중 어떤 상품을 고를지 비교한다면 판매처의 꽃 구성 안내를 참고할 수 있습니다. 두 상품이 같은 사양이라고 전제할 필요는 없습니다.",
    "빈소와 주문처 정보",
    "받는 장례식장명, 빈소 정보, 배송할 실제 주소를 준비하면 접수 가능 여부를 상담하기 좋습니다. 리본에 표기할 개인·단체 명의를 별도로 검토하면 받는 분의 정보와 보내는 분의 이름을 구분할 수 있습니다."
  ],
  "4100000000": [
    "근조화환 예산의 단계",
    "연천군·가평군·양평군에 속한 수령지를 선택할 때 B201과 B202의 59,000원 기준가를 비교한 다음 109,000원의 B205까지 예산 범위를 넓혀 볼 수 있습니다. 모든 금액은 추가비용 이전의 상품 표시가입니다.",
    "구매 전 합계 점검",
    "B206의 기준가는 149,000원이지만 실제 결제금액은 선택한 상품·주소·리본 옵션에 따라 달라집니다. 장례식장 주소와 행사 정보를 판매처에 알려 각 군의 주문 조건을 확인한 후 구매 결정을 내릴 수 있습니다."
  ],
  "4300000000": [
    "같은 용도 기준가 비교",
    "근조화환 네 상품은 가격이 두 단계 이상으로 구분됩니다. B201·B202 각각 59,000원, B205 109,000원, B206 149,000원이라는 사실은 확인됐지만 꽃 개수·크기를 가격에서 추론할 수 없습니다. 실제 상품별 상세를 확인해야 하는 정보입니다.",
    "군 목록 탐색 순서",
    "이 광역 목록에서 먼저 받는 군을 찾고 해당 군 페이지의 주문 링크로 이동할 수 있습니다. 수령지 읍·면 이름과 건물 주소까지 준비하면 배송비 및 실제 접수 일정을 확인하는 데 도움이 됩니다."
  ],
  "4400000000": [
    "리본 문구와 발신인 구분",
    "리본의 조의 문구는 받는 분에게 전달하는 말이고 보내는 이름은 발신인을 나타냅니다. 개인이 보낼지 회사·단체가 보낼지에 따라 이름 기재가 달라지므로 상품을 선택한 뒤 정확한 표기를 준비합니다.",
    "보낼 시설 정보 분리",
    "군을 선택한 뒤 장례식장과 빈소를 구분하여 입력합니다. 리본 발신인과 주문 담당자 연락처는 서로 다른 정보이며, 주문 화면에서 각각 필요한 항목에 기입하면 확인이 편리합니다. 가격과 옵션은 최종 주문서에 표시됩니다."
  ],
  "4700000000": [
    "상품코드에 따른 선택",
    "B205는 109,000원, B206은 149,000원으로 기준가가 다릅니다. 같은 근조 용도라도 상품번호가 다르기 때문에 판매처에서 사진과 구성 안내를 따로 비교한 뒤 선택할 수 있습니다. 가격 차이를 꽃 수량으로 환산하지 않습니다.",
    "군과 읍면을 함께 확인",
    "군 목록이 길어도 받는 시설이 어느 군의 어떤 읍·면에 있는지 확인하면 주문 문의가 구체적입니다. 실제 배송비 표에 있는 지역명과 주문서 적용 금액이 다를 수 있으므로 최종 금액은 주문처의 확인 결과를 따릅니다."
  ],
  "4800000000": [
    "배송비를 포함한 총예산",
    "표시가 59,000원의 상품을 고르더라도 총예산에 배송비와 리본 옵션이 포함되는지 확인할 수 있습니다. 받는 곳이 확정되지 않은 상태에서는 B201과 B202의 총액 차이를 가격표만으로 비교하기 어렵습니다.",
    "수령지 확정과 문의",
    "광역권의 군 목록에서 해당 군을 선택한 다음 정확한 시설 주소와 빈소 정보를 준비합니다. 주문처에 상품번호와 날짜를 함께 전달하면 옵션과 추가비용을 포함한 실제 접수 조건을 확인할 수 있습니다."
  ],
  "5100000000": [
    "도착 희망일을 먼저 확인",
    "장례식장에 화환이 필요한 날짜가 정해졌다면 상품코드와 함께 희망 도착 시간을 전달할 수 있습니다. 실제 접수 가능한 시각은 수령 시설 주소와 주문 시점에 따라 확인해야 하며 고정된 시간을 이 목록에서 제공하지는 않습니다.",
    "상품과 리본 내용 정리",
    "희망 일정과 별도로 B201·B202·B205·B206의 상품 상세를 살펴보고 리본의 문구·보내는 명칭을 확인할 수 있습니다. 군을 선택하는 단계와 배송 조건 확인 단계를 구분해 주문 과정을 진행합니다."
  ],
  "5200000000": [
    "동일 가격 상품을 비교할 때",
    "B201과 B202는 모두 59,000원입니다. 두 상품의 꽃 구성·장식·주문 옵션은 각각의 판매처 상세에서 비교할 수 있습니다. 실제 결제액에는 주문 주소에 따른 요금이 추가될 수 있습니다.",
    "군별 주문 주소와 리본 표기",
    "군 목록에서 받는 곳을 고른 뒤 장례식장명·빈소와 리본의 보내는 명의를 준비합니다. 주문 접수 가능 여부와 리본 옵션 추가비용은 판매처에서 확인할 수 있으며, 상품 정보와 받는 시설 정보를 구분하여 입력합니다."
  ]
}

SOURCE_SHIPPING={}  # Seller B201 county fee applicability was not independently parsed into verified SKU-specific records.
# SKU-scoped seller shipping TABLE facts, re-read 2026-11-08.
# No row found is NOT a zero-fee guarantee. Do not extrapolate across SKUs.
VERIFIED_SHIPPING_FACTS={
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
 '완도군':('rice-basket',['B054']),'고령군':('basket',['CAT2090'])}
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
   'productSkus':['CAT2090'],
   'introductions':['{county} 장례식장으로 보내는 영정바구니의 조의 문구와 수령지 정보를 정리했습니다.'],
   'sections':[
    {'slot':'choice','heading':'조의 문구 준비','paragraph':'리본에 쓸 조의 표현으로 “삼가 고인의 명복을 빕니다”나 “깊은 애도를 표합니다”를 고려할 수 있습니다. 보내는 분의 이름은 별도로 준비해 주세요.'},
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
  scope['introductions']=[p['fullName']+'의 '+str(len(names))+'개 군 지역을 안내합니다. 근조화환을 받을 군을 고르면 상품가격과 주문처로 이동할 수 있습니다.']
  # Province-specific sources prevent county name substitution alone.
  # Compare each county against the actual ledger before rendering.
  assert len(names)>0
  scope['sections'].append({
   'slot':'covered-counties','heading':p['fullName']+'의 군 지역',
   'paragraph':'군 선택 대상은 '+joined+'입니다. 받는 장례식장의 주소가 어느 군인지 확인하고 해당 군 페이지로 이동해 주세요.'})
  focus=PROVINCE_PURCHASE_FOCUSES[p['code']]
  scope['sections'].extend([
   {'slot':'purchase-focus','heading':focus[0],'paragraph':focus[1]},
   {'slot':'purchase-details','heading':focus[2],'paragraph':focus[3]},
  ])
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
    'referenceDate':'2026-11-07','priceConfirmed':True,
    'priceEvidence':('2026-11-08 seller product or category listing readback, source https://fwith.co.kr/shop/item.php?it_id='+sku if sku in ('B213','B054') else '2026-11-07 09:53 UTC direct read-only HTTP200 SKU and listed price and 주문시 배송비 결제; source run 42361620276'),
    'priceCheckedOn':('2026-11-08' if sku in ('B213','B054') else '2026-11-07'),'orderUrl':'https://fwith.co.kr/shop/item.php?it_id='+sku,
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
