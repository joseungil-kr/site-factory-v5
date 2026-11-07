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
from scripts.county_copy_pools import purpose_intros,purpose_sections,expanded_pools,county_intents,skus_for

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
       'purpose':'national','title':'전국 군 근조화환 가격과 상품 안내','productSkus':list(PRICES),
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
  purpose=county_intents()[i%len(county_intents())]
  num=len(pages)+1
  pages.append({'id':'county-'+c['code'],'number':num,'region':c['fullName'],
   'county':c['name'],'province':p['fullName'],'parentRegion':p['fullName'],
   'parentPageId':'province-'+p['code'],'purpose':purpose,
   'title':c['name']+' 근조화환 가격·상품 선택 | 군 근조화환 안내',
   'productSkus':skus_for(purpose),'intro':c['name']+' 근조화환 상품 가격과 수령지 안내.',
   'sections':[{'heading':'상품 선택','paragraph':'같은 상품 유형의 표시가를 확인할 수 있습니다.'},
               {'heading':'주문 요청','paragraph':'받는 시설명과 주소를 확인할 수 있습니다.'}],
   'faq':[],'pageType':'county','officialCode':c['code'],
   'shippingEvidence':SOURCE_SHIPPING.get(c['code']),
   'townships':'·'.join(township_names),'townshipCount':str(len(township_names)),
   'officialTownshipCodes':[x[0] for x in lower]})
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
 # National and province pages only show county-bearing province coverage.
 national=pool('전국 근조화환 상품 선택',
    '전국 군 지역의 근조화환 가격과 실제 주문 링크를 살펴볼 수 있습니다.',
    'B201·B202는 각 59,000원, B205는 109,000원, B206은 149,000원입니다. 상품별 꽃 구성·크기는 판매처 상세에 따릅니다.',
    '군별 배송 추가비와 읍·면 예외는 받는 시설의 상세 주소를 기준으로 판매처에서 확인할 수 있습니다.',
    '받는 군과 장례식장 주소, 희망일, 리본 문구를 준비하면 실제 결제 총액을 확인할 수 있습니다.',
    '군 지역 화환의 배송비는 어떻게 확인하나요?')
 national['introductions']=['전국 군 지역 근조화환의 표시가와 상품 선택, 주문 절차를 정리했습니다.']
 province=pool('광역 지역별 군 근조화환',
    '{province}에 속한 군 지역의 근조화환 상품 표시가와 주문 연결을 확인할 수 있습니다.',
    '{province}의 군 지역으로 보낼 근조화환 상품 B201·B202·B205·B206의 가격과 유형을 비교합니다.',
    '수령 시설의 읍·면 상세 주소를 기준으로 추가 배송비와 주문 가능 여부를 상담할 수 있습니다.',
    '관내 군 지역을 선택한 뒤 장례식장명과 빈소·희망일을 판매처에 전달할 수 있습니다.',
    '해당 광역 지역의 군 근조화환을 어떻게 주문하나요?')
 province['introductions']=['{province} 관내 군 지역 근조화환의 상품 가격과 수령 시설별 주문 안내를 확인할 수 있습니다.']
 spec['purposePools']['national']=national
 spec['purposePools']['province']=province
 # Only counties attested by the pinned official parent ledger are listed.
 for p in provinces:
  names=[c['name'] for c in counties if c['parent']==p['code']]
  assert names
  scope=__import__('copy').deepcopy(province)
  joined='·'.join(names)
  scope['introductions']=[p['fullName']+'에서 '+str(len(names))+'개 군 지역 근조화환의 표시가와 주문 절차를 비교할 수 있습니다. 수령지의 실제 배송 조건은 주문 과정에서 확인할 수 있습니다.']
  scope['sections'].append({'slot':'covered-counties',
    'heading':p['fullName']+'의 군 지역 검색',
    'paragraph':p['fullName']+'의 군 지역 목록은 '+joined+'입니다. 2026-10-22에 확보한 법정동 코드 기준 명칭이며, 군 페이지에서 받는 시설명과 주소를 따로 확인할 수 있습니다.'})
  selection=(names[0]+'의 수령 시설명과 주소를 준비한 다음 B201·B202·B205·B206의 가격과 주문조건을 볼 수 있습니다.' if len(names)==1 else '목록에서 해당 군을 선택하고 장례식장명과 빈소·주소를 확인한 다음 B201·B202·B205·B206의 주문조건을 비교할 수 있습니다.')
  scope['sections'].append({'slot':'county-selection',
    'heading':'군 지역 선택과 상품 주문',
    'paragraph':selection})
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
    'priceEvidence':'2026-11-07 09:53 UTC direct read-only HTTP200 SKU and listed price and 주문시 배송비 결제; source run 42361620276',
    'priceCheckedOn':'2026-11-07','orderUrl':'https://fwith.co.kr/shop/item.php?it_id='+sku,
    'verifiedLive':False,'imageUseApproved':False,
    'verifiedSource':True})
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
   'shippingEvidenceState':'No county-specific amount accepted until exact B201 source rows, 읍/면 exceptions and checkout calculation are verified',
   'priceReadback':'2026-11-07 09:53 UTC independent HTTP200 four SKU price/delivery readback, GitHub run 42361620276',
   'imageUsage':'Only new owned simple SVG illustration. No seller image copied.',
   'privateDeploymentReady':False,'productionHost':None})
 print('V51_COUNTY_TRIAL_INPUTS_BUILT='+json.dumps({'siteId':ID,'totalPages':len(pages),
   'counties':len(counties),'provinces':len(provinces),'purposes':dict(Counter(x['purpose'] for x in pages))},ensure_ascii=False))
if __name__=='__main__':main()
