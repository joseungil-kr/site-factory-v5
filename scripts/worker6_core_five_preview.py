"""Isolated five-page preview, reusing V5.1 plan and renderer. No deployment."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
from copy import deepcopy

def product_summary(items):
    """Single source for product count, names, prices and cards."""
    ordered=sorted(items,key=lambda p:(p['priceKRW'],p['sku']))
    return {'count':len(ordered),
            'label':' / '.join(f"{p['name']} {p['priceKRW']:,}원 ({p['sku']})" for p in ordered),
            'skus':[p['sku'] for p in ordered],
            'priceBands':sorted({p['priceKRW']//10000 for p in ordered})}

def operator_policy(source):
    """One verified operator record, one customer-facing policy for all pages."""
    if not (source['regionalDispatch'] and source['nationwideSameDayAvailableAsGeneralService']):
        raise ValueError('operator nationwide dispatch confirmation required')
    if source['individualSameDayArrivalGuaranteed'] or source['deliveryWindow']['guaranteed']:
        raise ValueError('individual arrival must not be guaranteed')
    phone=source['orderPhone']
    order=source['phoneOrderHours']
    delivery=source['deliveryWindow']
    if source['individualCutoff']!='phone-confirm' or source['regionalSurcharge']!='phone-confirm':
        raise ValueError('order cutoff and regional surcharge require consultation')
    return (f"지역별 지점에서 발송하며 전국 당일배송 서비스를 안내합니다. "
            f"전화 주문은 {order['start']}~{order['end']}, "
            f"배송 가능 시간대는 지역 꽃집 운영시간에 따른 {delivery['earliestPossible']}~{delivery['latestPossible']}입니다. "
            f"개별 주문의 당일 도착시각·접수 마감·재고·추가요금은 {phone}로 확인하세요. "
            "23시 전화 주문이 그날 도착한다는 뜻은 아닙니다.")

def generate_inputs(source,base_spec,site_input,require_orchids=True,operator_source=None):
    spec=deepcopy(base_spec)
    operator_source=operator_source or json.loads((SITE/'operator-service-confirmation-20261109.json').read_text(encoding='utf-8'))
    shared_operator_copy=operator_policy(operator_source)
    product_ids=[x['sku'] for x in source['sources']]
    if not product_ids or len(set(product_ids))!=len(product_ids):
        raise ValueError('nonempty unique product SKUs required')
    if any(type(x.get('priceKRW')) is not int or x['priceKRW']<=0 or not x.get('name') for x in source['sources']):
        raise ValueError('verified name and positive integer price required')
    summary=product_summary(source['sources'])
    assert len(summary['skus'])==len(product_ids)
    spec['purposePools']['home']={
     'productSkus':product_ids,
     'introductions':['승진·영전·일반 축하 선물과 당일 문의의 차이를 먼저 살펴보세요. 확인된 상품을 비교하고 목적별 안내에서 주문 순서를 선택할 수 있습니다.'],
     'sections':[
      {'slot':'choice','role':'required','heading':'목적별 안내를 먼저 선택','paragraph':'승진은 새 직함과 부서, 영전·전보는 새 근무지와 출근일, 일반 축하는 선물 메시지와 배치 장소, 당일 문의는 희망 시간과 실제 배송지를 먼저 정리하는 방식으로 구분합니다. 아래 페이지 번호 링크에서 해당 안내로 이동할 수 있습니다.'},
      {'slot':'choice','role':'required','heading':'판매처 확인 상품 목록','paragraph':'D152 레드카네이션 화분은 50,000원, D144 금전수 탁상용은 53,000원, D156 포인세티아 소형은 60,000원, D026 아로우카리아 대형은 90,000원으로 판매처에 표시됩니다. 네 상품 모두 선택옵션과 추가옵션이 0개이며 수량을 선택해 주문할 수 있습니다. 현재 재고와 화분의 실제 크기는 별도로 확인해야 합니다.'},
      {'slot':'order','role':'required','heading':'상품을 고른 뒤 주문하는 순서','paragraph':'상품 상세 링크에서 상품명·수량·가격을 확인한 다음 받는 분의 이름, 상세 주소, 수령 가능한 날짜를 준비합니다. 메시지 또는 리본 제공 방식은 판매처에 확인하고 배송비를 포함한 결제 금액을 검토한 후 주문합니다.'},
      {'slot':'order','role':'required','heading':'배송비와 당일 요청의 구분','paragraph':'판매처는 지역별 추가 배송비 표를 게시하지만 주소별 최종 요금과 당일 배송 가능 시간은 확정되어 있지 않습니다. 오늘 수령해야 한다면 1844-0644로 상품번호·배송지·희망 시간을 먼저 문의하세요.'}
     ],
     'faqs':[{'q':'가격과 옵션은 확인되었나요?','a':'D152 50,000원, D144 53,000원, D156 60,000원, D026 90,000원이며 네 상품의 선택·추가옵션은 0개로 표시됩니다.'},{'q':'당일 배송이 보장되나요?','a':'아닙니다. 주소와 희망 시간을 전달해 가능 여부를 먼저 확인해야 합니다.'}]
    }
    # Derive every home product claim from the same catalog as product cards.
    home=spec['purposePools']['home']
    home['productSkus']=summary['skus']
    home['introductions']=[f"승진·영전·일반 축하 선물과 당일 문의를 비교합니다. 판매처에서 확인한 상품 {summary['count']}종을 예산과 상품명상 형태로 살펴보고 목적별 안내를 선택하세요."]
    home['sections'][1]['heading']=f"판매처에서 확인한 상품 {summary['count']}종"
    home['sections'][1]['paragraph']=f"확인된 상품과 가격: {summary['label']}. 각 상품의 실제 크기, 현재 재고, 배송 가능 여부는 확인이 필요합니다."
    home['faqs'][0]['a']=f"확인된 상품 {summary['count']}종: {summary['label']}. 표시 가격은 결제 시 다시 확인하세요."
    # Purpose guides have no geographic location; never inject fake region labels.
    guide_introductions={
     'promotion':'승진 선물은 새 자리에서 놓을 공간과 수령할 부서를 먼저 확인합니다. 확인된 상품을 예산과 상품명 기준으로 비교하세요.',
     'transfer':'영전·전보 선물은 새 근무지에서 실제 수령할 사람이 있는 날짜를 기준으로 준비합니다. 확인된 상품의 주문 조건을 비교하세요.',
     'congratulations':'축하화분을 고를 때는 받는 분의 선호와 놓을 자리를 먼저 생각해 보세요. 확인된 상품을 예산에 따라 비교할 수 있습니다.',
     'sameDayInquiry':'오늘 축하화분을 보내려면 상품 선택보다 상세 주소와 수령 가능한 시간을 먼저 확인해야 합니다. 당일 배송 가능 여부는 주소와 접수 시점에 따라 별도 확인이 필요합니다.'
    }
    for purpose,intro in guide_introductions.items():
        spec['purposePools'][purpose]['introductions']=[intro]
    # Replace overlapping generic selection sections with one substantive,
    # purpose-specific buyer decision module. Do not append a fifth repetition.
    decision_modules={
     'promotion':{
      'choice':('승진 선물 선택','금전수 탁상용 D144는 53,000원, 포인세티아 소형 D156은 60,000원입니다. 두 상품의 크기와 재고는 미확인이므로 수령 공간을 정한 뒤 상세상품에서 확인하세요.'),
      'message':('승진 축하 문구 예시','예시: “새로운 자리에서의 활약을 응원합니다.” 보내는 사람 표기 예: “○○회사 영업팀 일동”. 꽃이랑 경조사어도우미에 승진 문구 참고 이미지가 있으나, 리본 포함·문구 입력·무료 제공 여부는 확인되지 않았습니다.'),
      'order':('승진 선물 주문 확인','새 직함, 받는 회사·부서·층·호실, 실제 수령 날짜와 담당자를 정리합니다. 상품별 최종 배송비·메시지 제공 여부를 확인한 뒤 결제합니다.')},
     'transfer':{
      'choice':('영전·전보 선물 선택','D156 포인세티아 소형 60,000원과 D144 금전수 탁상용 53,000원을 비교합니다. 새 근무지의 배치 공간과 실제 수령 가능한 날짜가 상품 선택의 기준입니다.'),
      'message':('영전 축하 문구 예시','예시: “새로운 자리에서 뜻하신 일을 이루시길 바랍니다.” 보내는 사람 표기 예: “○○회사 대표 홍길동”. 꽃이랑 문구 참고 이미지에 영전 축하 예시가 있으나, 주문 상품에 리본이 제공되는지는 미확인입니다.'),
      'order':('영전·전보 수령 확인','발령일과 출근일을 구분하고 새 근무지의 정확한 주소·부서·대리 수령 담당자를 확인합니다. 이전 근무지로 잘못 보내지 않도록 배송지와 수령일을 결제 전에 점검합니다.')},
     'congratulations':{
      'choice':('축하화분과 예산 선택','확인된 상품은 D144 금전수 탁상용 53,000원, D156 포인세티아 소형 60,000원입니다. 상품명으로만 실제 크기나 식물관리 조건을 추정하지 말고 받는 분의 선호와 배치 장소를 확인하세요.'),
      'message':('축하 메시지 준비','예시: “새 출발을 진심으로 축하드립니다.” 보내는 사람 표기 예: “○○동호회 회원 일동”. 문구 예시는 직접 작성한 참고 문장으로, 판매처의 리본 제작 서비스나 무료 제공을 뜻하지 않습니다.'),
      'order':('축하 선물 주문 확인','받는 분의 이름, 축하 행사일, 정확한 수령 장소와 연락처를 확인합니다. 리본·메시지 선택 가능 여부는 상품 상세 또는 판매처 문의로 확인한 뒤 주문하세요.')},
     'sameDayInquiry':{
      'choice':('당일 문의 1단계 · 상품과 수령지 준비','문의할 정보: 선택한 상품번호 / 수령지 시군구·읍면동·건물·층 / 받는 분 연락처 / 희망 수령 시각. 실제 재고와 주문 마감은 확인되지 않았습니다.'),
      'message':('당일 문의 2단계 · 판매처 답변 확인','판매처에 확인할 항목: 해당 주소 배송 가능 여부 / 접수 마감 / 예상 수령 가능 시간 / 지역 추가 배송비와 최종 결제금액 / 부재 시 수령 방법. 답변이 확정되기 전에는 당일 도착을 전제로 결제하지 마세요.'),
      'order':('당일 문의 3단계 · 결제 판단','전화 1844-0644로 문의 결과를 확인하고 상품 상세의 수량·옵션·금액을 재확인합니다. 배송 가능 여부와 시간·요금에 대한 판매처 답변을 받기 전에는 주문을 진행하지 않습니다.')}
    }
    for purpose,modules in decision_modules.items():
        pool=spec['purposePools'][purpose]
        # One module per independent job: choice, message, transaction.
        # Preserve V5.1 slots without multiplying repetitive generic paragraphs.
        pool['sections']=[
          {'slot':'choice','role':'required','heading':modules['choice'][0],'paragraph':modules['choice'][1]},
          {'slot':'choice','role':'required','heading':modules['message'][0],'paragraph':modules['message'][1],
           **({'sourceUrl':'https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg'} if purpose in ('promotion','transfer') else {})},
          {'slot':'order','role':'required','heading':modules['order'][0],'paragraph':modules['order'][1]}]
        pool['faqs']=[{'q':'당일 배송이 보장되나요?','a':'배송 가능 여부와 도착 시간은 판매처에 확인해야 합니다.'},
                      {'q':'리본·메시지가 제공되나요?','a':'참고 문구가 공개되어 있어도 해당 상품의 제공 여부와 입력 방법은 별도 확인해야 합니다.'}]
    # Product catalog is shared by four guides; role-specific selection order is
    # based on confirmed name/price only, never dimensions or availability.
    for purpose in ('promotion','transfer','congratulations','sameDayInquiry'):
        spec['purposePools'][purpose]['productSkus']=product_ids

    # Replace only product-selection paragraphs; keep message and order separate.
    # Recompute all price/SKU listings from the verified seller catalog.
    for purpose in ('promotion','transfer','congratulations','sameDayInquiry'):
        pool=spec['purposePools'][purpose]
        pool['productSkus']=summary['skus']
        pool['sections'][0]['paragraph']=(
            f"판매처 확인 상품 {summary['count']}종: {summary['label']}. "
            +"탁상용·소형·대형은 상품명 표기이며 실제 치수와 재고는 확인되지 않았습니다. "
            +({'promotion':'승진 선물은 새 직함과 수령 공간을 확인해 선택하세요.',
               'transfer':'영전·전보는 새 근무지의 배치 장소와 수령일을 확인하세요.',
               'congratulations':'축하 사유와 받는 분의 선호를 기준으로 선택하세요.',
               'sameDayInquiry':'당일 배송 가능 여부는 상품번호와 상세 주소로 판매처에 확인하세요.'}[purpose]))
        pool['faqs'][0]['a']='배송 가능 여부와 도착 시간은 판매처에 확인해야 합니다.'
    # Seller-posted returns guidance is a general checkout consideration, not
    # proof of locality delivery and not a legal determination.
    returns_url='https://fwith.co.kr/data/common/flower379/de_change_content.jpg'
    returns_copy=('판매처 게시 안내에는 불량·파손·주문과 전혀 다른 상품의 환불 가능, '
     '주소 오기·수취 거부 시 교환·환불 제한, 배송 당일 문제 신고, '
     '결제 후 배송 불가·재고 없음 시 전액 환불이 표시되어 있습니다. '
     '계절·지역 소재 차이와 배송완료 당일 교환·왕복배송료 관련 조건도 있으므로 '
     '결제 전에 원문을 확인하세요. 이는 판매처 게시 안내의 요약이며 법정 권리나 '
     '특정 지역 배송 가능 여부를 판단한 내용이 아닙니다.')
    for purpose in ('home','promotion','transfer','congratulations','sameDayInquiry'):
        pool=spec['purposePools'][purpose]
        pool['sections'].append({'slot':'order','role':'required','heading':'결제 전 교환·환불 안내 확인',
                                  'paragraph':returns_copy,'sourceUrl':returns_url})
    # Purpose-fit validation: a promotion/transfer guide must offer both
    # seller-verified oriental and western orchids, not funeral products.
    seller_by_sku={x['sku']:x for x in source['sources']}
    orchid_evidence={'E008':('일향금','동양란'),'F055':('연핑크 호접란','서양란')}
    if require_orchids:
        for orchid_sku,(expected_name,expected_category) in orchid_evidence.items():
            x=seller_by_sku.get(orchid_sku)
            if not x or x.get('name')!=expected_name or x.get('category')!=expected_category:
                raise ValueError('promotion/transfer orchid evidence missing: '+orchid_sku)
    if any(x['name'].startswith('장례식장 근조') for x in source['sources']):
        raise ValueError('funeral product must not be presented as promotion orchid')
    orchid_copy=('난류를 고려한다면 동양란 일향금 E008 110,000원과 '
                 '서양란 연핑크 호접란 F055 60,000원을 비교할 수 있습니다. '
                 '이는 꽃이랑 상품 상세에서 확인된 이름·가격·카테고리이며 '
                 '품종별 실제 크기·관리방법·재고·배송가능 시간은 확인되지 않았습니다. '
                 '일반 관엽화분과 난류 중 받는 분의 선호, 배치 장소와 예산을 기준으로 선택하세요.')
    for purpose in (('promotion','transfer') if require_orchids else ()):
        pool=spec['purposePools'][purpose]
        pool['sections'].insert(1,{'slot':'choice','role':'required',
             'heading':'승진·영전 선물에 난류를 포함해 비교',
             'paragraph':orchid_copy})
        pool['faqs'].append({'q':'승진·영전에 난류 상품도 고를 수 있나요?',
            'a':'꽃이랑 확인 상품으로 동양란 일향금 E008 110,000원과 서양란 연핑크 호접란 F055 60,000원이 있습니다. 주문 전 실제 상품 상태와 배송 가능 시간을 확인하세요.'})
    relationship_messages={
      'promotion':('직장 동료라면 “새 직책에서 펼칠 활약을 응원합니다.” / '
                   '거래처라면 “승진을 축하드리며 앞으로의 발전을 기원합니다.” / '
                   '가족이라면 “오랫동안 쌓아온 노력이 빛나는 날, 진심으로 축하해요.”'),
      'transfer':('동료라면 “새로운 근무지에서도 뜻깊은 성과를 이루시길 바랍니다.” / '
                  '거래처라면 “새로운 자리에서의 출발을 축하드립니다.” / '
                  '가족이라면 “새로운 환경에서도 늘 응원할게요.”')
    }
    for purpose,examples in relationship_messages.items():
        pool=spec['purposePools'][purpose]
        pool['sections'].insert(2,{'slot':'choice','role':'required',
             'heading':'관계에 따라 축하 메시지 고르기',
             'paragraph':examples+' 보내는 사람 표기는 회사·부서·성명을 구분해 준비하세요. '
                '문구는 직접 작성한 예시이며 리본 제공이나 입력 옵션이 포함된다는 뜻은 아닙니다.'})
    # Purpose-specific decision sequence replaces repeated long six-SKU listings.
    # Shared product cards remain sourced from the verified product catalog.
    catalog={p['sku']:p for p in source['sources']}
    def item(sku):
        p=catalog[sku]
        return f"{p['name']}({sku}, {p['priceKRW']:,}원)"
    def section(heading,paragraph,slot='choice',source_url=None):
        return {'slot':slot,'role':'required','heading':heading,'paragraph':paragraph,
                **({'sourceUrl':source_url} if source_url else {})}
    operator_info=shared_operator_copy
    if require_orchids:
        promotion=spec['purposePools']['promotion']
        promotion['introductions']=['승진은 받는 분의 새 직책을 확인한 다음 축하할 관계와 선물 예산을 정하고, 마지막에 수령할 부서와 날짜를 확인하는 순서로 준비합니다.']
        promotion['sections']=[
          section('1. 새 직책과 축하할 관계를 먼저 정하기',
            '예를 들어 과장에서 부장으로 승진했다면 현재 직책이 아니라 새 직책을 확인합니다. '
            '직장 동료·거래처·가족 중 보내는 관계에 따라 메시지의 격식과 발신자 표기를 정하세요. '
            '회사 이름과 부서명, 보내는 사람 성명을 별도 항목으로 적어두면 문구 작성이 수월합니다.'),
          section('2. 승진 축하 문구 작성 예',
            '동료: “새 직책에서 펼칠 활약을 응원합니다.” — “○○회사 영업팀 일동”. '
            '거래처: “승진을 축하드리며 앞으로의 발전을 기원합니다.” — “○○기업 대표 ○○○”. '
            '가족: “오랫동안 쌓아온 노력이 빛나는 날, 진심으로 축하해요.” — “가족 일동”. '
            '문구는 직접 작성한 예시이며 실제 리본 제공이나 입력 옵션은 판매처에 확인하세요.',
            source_url='https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg'),
          section('3. 예산별 승진 선물 후보 비교',
            '6만 원 예산으로 난류를 원한다면 '+item('F055')+'을, 11만 원 예산으로 동양란을 원한다면 '+item('E008')+'을 비교하세요. '
            '탁상에 놓을 후보를 찾는다면 '+item('D144')+'도 함께 살펴볼 수 있습니다. '
            '상품명만으로 실제 크기·관리방법·재고를 확정하지 않고 상품 상세에서 주문 조건을 확인합니다.'),
          section('4. 승진 선물 수령지 체크리스트',
            '받는 분의 새 직함 / 회사명 / 부서·층·호실 / 수령 담당자 / 실제 근무하는 날짜를 확인하세요. '
            '책상이나 공용 공간에 놓을지 물어본 뒤 상품번호와 상세 주소를 전달합니다. '
            '리본 제공 방식, 최종 결제금액과 수령 가능 시각은 상담으로 결정합니다.','order'),
          section('전화 주문과 배송 가능 시간',operator_info,'order')]
        promotion['faqs']=[
          {'q':'승진 축하 메시지에 무엇을 적나요?','a':'새 직책과 보내는 사람의 관계를 먼저 정하고 회사·부서·성명을 구분해 적으세요. 문구 제공 여부는 판매처에 확인합니다.'},
          {'q':'승진 난류를 고를 때 무엇을 비교하나요?','a':item('F055')+'과 '+item('E008')+'의 가격·난류 종류를 비교하고 실제 크기와 재고는 전화로 확인하세요.'}]
        transfer=spec['purposePools']['transfer']
        transfer['introductions']=['영전·전보는 발령 발표일과 실제 새 근무지 출근일을 구분하는 것이 우선입니다. 이전 근무지로 잘못 보내지 않도록 배송지와 수령 담당자를 확정한 다음 선물과 문구를 선택합니다.']
        transfer['sections']=[
          section('1. 발령일·출근일·실제 수령일 구분',
            '발령 소식을 들은 날에 바로 새 사무실로 보내면 아직 근무하지 않을 수 있습니다. '
            '발령 발표일, 새 근무지 출근일, 선물을 실제 받을 수 있는 날짜를 각각 확인하세요. '
            '예: 발령 발표는 월요일, 새 근무지 첫 출근은 목요일이라면 목요일 수령 가능 여부를 먼저 확인합니다.'),
          section('2. 이전 주소와 새 주소 혼동 방지',
            '받는 분의 이전 근무지 주소는 주문지에서 제외하고 새 회사·기관명, 건물 주소, 부서·층·호실을 다시 확인합니다. '
            '부재 시 대신 받을 담당자가 있는지, 새 부서가 화분을 받을 수 있는지도 확인하세요. '
            '특정 기관의 반입 규칙을 확인한 것은 아니며 고객이 직접 수령지를 정하는 절차입니다.'),
          section('3. 새 근무지에 맞는 상품과 예산',
            '새 자리의 배치 공간을 확인한 뒤 '+item('E008')+' 동양란과 '+item('F055')+' 서양란을 비교할 수 있습니다. '
            '난류가 아닌 상품을 원한다면 '+item('D026')+' 또는 '+item('D152')+'도 후보입니다. '
            '상품명상 대형·소형 표기는 실측 크기가 아니므로 수령 공간에 맞는 치수와 재고를 문의하세요.'),
          section('4. 영전 축하 문구와 발신자',
            '동료: “새로운 근무지에서도 뜻깊은 성과를 이루시길 바랍니다.” — “○○팀 동료 일동”. '
            '거래처: “새로운 자리에서의 출발을 축하드립니다.” — “○○기업 대표 ○○○”. '
            '가족: “새로운 환경에서도 늘 응원할게요.” — “가족 일동”. '
            '예시 문구는 자체 작성한 것으로 리본 제공 여부와는 별개입니다.',
            source_url='https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg'),
          section('5. 새 근무지 배송 상담 순서',
            '새 근무지 상세 주소 → 출근일과 희망 수령일 → 대리 수령 담당자 → 선택 상품번호 순서로 준비하세요. '
            '이전 주소로 주문하지 않았는지 마지막으로 확인하고 1844-0644로 최종 추가요금과 도착 가능 시각을 상담합니다.','order'),
          section('전화 주문과 배송 가능 시간',operator_info,'order')]
        transfer['faqs']=[
          {'q':'영전 선물은 발령일에 보내야 하나요?','a':'발령 발표일과 새 근무지 첫 출근일이 다를 수 있으므로 실제 수령 가능한 날짜를 확인하세요.'},
          {'q':'이전 근무지와 새 근무지 중 어디로 보내나요?','a':'받는 분이 실제 수령할 새 근무지 주소와 담당자를 확인한 뒤 주문하세요.'}]
    for purpose in ('promotion','transfer'):
        spec['purposePools'][purpose]['sections'].append(
          section('결제 전 교환·환불 안내 확인',returns_copy,'order',returns_url))
    # Distinct buyer jobs: general congratulations chooses an occasion/message,
    # while same-day inquiry checks a live fulfillment decision in ordered steps.
    congrats=spec['purposePools']['congratulations']
    congrats['introductions']=['축하할 사유와 받는 분과의 관계를 먼저 정한 다음 선물 예산·상품 종류를 고릅니다. 행사 당일 수령이 필요한지, 받는 분이 실제로 받을 수 있는 날짜도 확인하세요.']
    congrats['sections']=[
      {'slot':'choice','role':'required','heading':'축하 사유와 받는 분 관계 확인',
       'paragraph':'개업·기념일·성과 축하 등 실제 사유를 먼저 확인하세요. 거래처에 보낸다면 회사명과 담당자 호칭을, 가족이나 지인에게 보낸다면 친밀한 표현을 선택할 수 있습니다. 보내는 사람은 회사·부서·성명을 따로 정리해 문구에 누락되지 않도록 합니다.'},
      {'slot':'choice','role':'required','heading':'선물 종류와 예산 결정',
       'paragraph':f"예산과 받는 분 선호에 따라 {item('D152')} 화분과 {item('D144')} 탁상용을 비교하거나, 난류를 선호한다면 {item('F055')} 서양란을 확인하세요. 상품명은 실제 크기·재고 보장이 아니므로 놓을 장소를 확인한 뒤 선택합니다."},
      {'slot':'choice','role':'required','heading':'축하 메시지 작성 예',
       'paragraph':'거래처: “뜻깊은 성과를 진심으로 축하드립니다.” — “○○회사 대표 ○○○”. 지인: “기쁜 날을 함께 축하해요.” — “친구 ○○○”. 메시지는 직접 작성한 참고 예시이며 리본 제작·제공 여부는 별도 확인합니다.'},
      {'slot':'order','role':'required','heading':'행사 일정과 수령인 확인',
       'paragraph':'행사 날짜, 행사장 또는 회사·자택 중 실제 수령 장소, 수령 담당자와 연락 가능한 시간을 확인하세요. 행사 시작 전 수령이 필요하다면 희망 시각을 구체적으로 전달하고 판매처와 실제 도착 가능 시간을 상담합니다.'}]
    congrats['faqs']=[
      {'q':'축하 메시지는 어떻게 정하나요?','a':'축하 사유와 보내는 사람 관계에 맞는 표현을 직접 정하고 발신자 이름을 확인하세요. 리본 제공은 별도 확인합니다.'},
      {'q':'행사일에 맞춰 받을 수 있나요?','a':'행사일과 희망 수령시각, 수령 담당자를 알려주고 개별 주문의 도착 가능 시간을 상담하세요.'}]
    day=spec['purposePools']['sameDayInquiry']
    day['introductions']=['당일배송 문의는 상품을 고른 다음 현재 접수 시각과 지역 꽃집의 실제 배송 가능 시간대를 대조하는 절차입니다. 전국 당일배송 서비스 안내와 개별 주문의 도착 확정은 구분합니다.']
    day['sections']=[
      {'slot':'choice','role':'required','heading':'1단계 · 상품과 배송지 정보를 준비',
       'paragraph':'선택한 상품번호, 수량, 시도·시군구·읍면동·건물·층·호실, 수령인에게 연락 가능한 방법과 희망 수령시각을 정리하세요. 실제 상품 재고와 주문 접수 마감은 전화 상담으로 확인합니다.'},
      {'slot':'order','role':'required','heading':'2단계 · 전화로 당일 수령 가능 시간 확인',
       'paragraph':'1844-0644에 선택 상품번호와 상세 주소를 알려주고 해당 주문의 도착 가능 시각, 접수 마감, 지역 추가 배송비, 부재 시 수령방법을 확인합니다. 전국 당일배송 서비스를 안내하더라도 원하는 시각의 도착이 자동 확정되는 것은 아닙니다.'},
      {'slot':'order','role':'required','heading':'3단계 · 판매처 답변을 확인하고 결제',
       'paragraph':'상담에서 확인한 수령 가능 시간과 최종 추가요금을 주문 내용과 대조합니다. 받는 분이 실제 수령할 수 있는지 확인한 다음 결제하고, 배송시간이나 비용이 맞지 않으면 주문 전에 조건을 다시 조정하세요.'}]
    day['faqs']=[
      {'q':'늦은 밤에 주문하면 바로 받을 수 있나요?','a':'전화 주문 가능 시간과 지역 꽃집의 배송 가능 시간대는 다릅니다. 23시 전화 접수는 당일 도착 보장이 아닙니다.'},
      {'q':'전화할 때 무엇을 알려줘야 하나요?','a':'상품번호·수량·상세 배송지·희망 시각을 알려주고 마감·재고·최종 추가요금을 확인하세요.'}]
    # Append the SAME operational policy to every page, without purpose-specific rewording.
    for purpose in ('home','promotion','transfer','congratulations','sameDayInquiry'):
        pool=spec['purposePools'][purpose]
        pool['sections']=[x for x in pool['sections'] if x.get('heading')!='전화 주문과 배송 가능 시간']
        pool['sections'].append({'slot':'order','role':'required',
            'heading':'전화 주문시간과 배송 가능 시간',
            'paragraph':shared_operator_copy})
    # The nationwide service is operator-confirmed; only per-order arrival is conditional.
    for purpose in ('home','congratulations','sameDayInquiry'):
        pool=spec['purposePools'][purpose]
        pool['faqs']=[x for x in pool['faqs'] if x.get('q')!='당일 배송이 보장되나요?']
        pool['faqs'].append({'q':'전국 당일배송 서비스를 이용할 수 있나요?',
          'a':'지역별 지점 발송으로 전국 당일배송 서비스를 안내합니다. 주문별 도착시각과 마감·추가요금은 전화상담으로 확인하세요.'})
    day=spec['purposePools']['sameDayInquiry']
    day['sections']=[dict(x,paragraph=x['paragraph'].replace(
        '해당 주소 배송 가능 여부 / 접수 마감',
        '개별 주문의 실제 도착 가능 시간 / 접수 마감').replace(
        '배송 가능 여부와 시간·요금에 대한 판매처 답변',
        '도착 시간·접수 마감·추가요금에 대한 판매처 답변'))
        for x in day['sections']]
    home=spec['purposePools']['home']
    home['sections']=[dict(x,paragraph=x['paragraph'].replace(
        '주소별 최종 요금과 당일 배송 가능 시간은 확정되어 있지 않습니다',
        '전국 당일배송 서비스를 안내하며 개별 주문의 도착 시간과 최종 요금은 전화로 확인합니다'))
        for x in home['sections']]
    spec['pageTypes']=['homepage','purpose-guide']
    spec['targetPageCount']=5
    spec['publishPolicy']['mode']='preview'
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
          'productSkus':summary['skus'],
          'faq':[{'q':'주문 방법은?','a':'상품 상세 링크에서 확인합니다.'}]})
    regions={'source':'purpose-based guides, not locality delivery evidence','regions':[{'name':p['region'],'code':None,'level':'purpose-guide'} for p in pages]}
    site=site_input
    site['navigation']=[{'label':'홈','href':'/'},{'label':'승진','href':'/2.html'},{'label':'영전·전보','href':'/3.html'},{'label':'축하','href':'/4.html'},{'label':'당일 문의','href':'/5.html'}]
    return spec,pages,regions,site

if __name__=='__main__':
    source=json.loads((SITE/'core-five-seller-evidence.json').read_text(encoding='utf-8'))
    spec=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
    site=json.loads((SITE/'site.json').read_text(encoding='utf-8'))
    spec,pages,regions,site=generate_inputs(source,spec,site)
    (SITE/'site-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (SITE/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (SITE/'regions.json').write_text(json.dumps(regions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (SITE/'site.json').write_text(json.dumps(site,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CORE_FIVE_INPUT_OK',[(p['number'],p['purpose'],p['title']) for p in pages])
