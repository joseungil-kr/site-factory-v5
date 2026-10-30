"""Todayflower nationwide noindex generator from the V4 pinned legal-code ZIP.

This is historical administrative coverage (2026-10-22), NOT independently
verified service delivery, current legal status, local popularity, or any shop.
Keep original 33 reviewed pages unchanged and their numbering stable.
No generative API, web scrape, or new location information is used.
"""
from __future__ import annotations

import csv
from functools import lru_cache
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile

from .config import ConfigError

ARCHIVE = "data/regions/todayflower_official_codes_20261022.zip"
ZIP_SHA256 = "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
EXPECTED = {
    "강원특별자치도":298, "경기도":747, "경상남도":546,
    "경상북도":525, "대구광역시":212, "대전광역시":177,
    "부산광역시":192, "서울특별시":467, "세종특별자치시":33,
    "울산광역시":84, "인천광역시":156, "전남광주통합특별시":623,
    "전북특별자치도":410, "제주특별자치도":74,
    "충청남도":285, "충청북도":238
}
EXPECTED_DONG_COUNT=5067
EXPECTED_ORIGINAL=33
EXPECTED_NEW=5037
EXPECTED_TOTAL=5070
ORDER_KINDS=("bouquet","plant","celebration","condolence")
PRODUCT_SETS=(
    ("G067","G073","D144","D149","C200","B201"),
    ("G073","D144","D149","C206","B201","B205"),
    ("G067","G073","D144","C200","C206","B201","B205"),
    ("G067","D144","D149","C200","B201","B205"),
    ("G073","D144","D149","C200","C206","B201"),
)
# Each row describes an actual buyer decision/condition, not a local product
# speciality or invented storefront. No variable is plugged into flower type.
SCENARIOS=(
 ("생일 꽃다발","생일 선물을 받을 사람의 일정부터 확인합니다.",
  "꽃다발은 꽃 색과 포장 형태, 받는 분이 직접 이동할 때의 크기를 비교하세요.",
  "생일 선물 꽃다발을 오늘 받을 수 있나요?",
  "꽃다발과 화분은 어떤 상황에서 골라야 하나요?",
  "당일 수령 가능 여부는 상품 준비 상황과 실제 수령 주소·시간을 확인한 뒤 판매처에 문의해야 합니다."),
 ("개업 축하화분","새 매장에서 꽃을 놓을 위치와 수령 담당자를 정리합니다.",
  "화분은 관리 여건과 실제 높이를, 축하화환은 행사장 반입 규정을 함께 살펴보세요.",
  "개업 매장에 오늘 축하화분을 받을 수 있나요?",
  "매장 개업화분의 크기는 무엇으로 비교하나요?",
  "화분이 놓일 공간의 폭과 식물 관리 조건을 확인한 뒤 상품별 제작·배송 가능 여부를 문의하세요."),
 ("축하화환","개업식과 기념 행사에서는 행사장 인계 위치와 리본 문구를 구분합니다.",
  "축하화환은 현장 설치 허용 위치와 크기를 확인하고 발신 명의를 정확히 입력하세요.",
  "행사장에 축하화환을 오늘 전달할 수 있나요?",
  "축하화환 리본 문구와 설치 장소는 어떻게 확인하나요?",
  "행사 시작과 수령 가능 시간을 따로 파악한 후 화환 준비·설치 가능 여부를 판매처에 확인해 주세요."),
 ("조문 근조화환","조문용 꽃은 정확한 장례시설명과 빈소·발인 일정을 우선 확인합니다.",
  "근조화환은 축하용 상품과 구분하고 리본 발신 명의와 현장 수령처를 대조해 주세요.",
  "조문 장소에 근조화환을 오늘 보낼 수 있나요?",
  "근조화환 주문 전 빈소와 발인 시각은 어떻게 확인하나요?",
  "정확한 장례식장과 빈소를 확인한 뒤 배송 가능 일정을 판매처에 문의해야 합니다."),
 ("수령자 부재 대응","받는 분이 자리에 없는 경우 대신 받아 줄 사람과 인도 방법을 정리합니다.",
  "상품에 따라 보관 방식이 달라질 수 있으므로 문앞 방치가 가능하다고 단정하지 마세요.",
  "받는 분이 부재하면 꽃배달을 어떻게 받아야 하나요?",
  "대리 수령을 계획할 때 무엇을 확인해야 하나요?",
  "받는 분의 일정과 대리 수령자 연락처를 확인한 뒤 인도 방식을 판매처와 상의해 주세요."),
 ("배송지 상세주소","행정구역 이름만으로 주문하지 않고 도로명·건물·호실을 함께 확인합니다.",
  "정확한 주소를 상품번호와 함께 전달하면 수령지에 맞는 가능 시간을 상담하기 쉽습니다.",
  "오늘 꽃배달을 주문하려면 어떤 주소를 알려야 하나요?",
  "건물명과 수령 담당자는 언제 확인하나요?",
  "상세주소와 실제 수령자 연락처를 준비한 뒤 상품별 배송 조건을 확인해 주세요."),
 ("추가배송비 확인","표시된 상품가격과 지역별 추가 배송 요금을 별개로 확인합니다.",
  "다른 상품의 추가요금을 그대로 적용하지 말고 선택한 SKU의 최종 결제금액을 확인하세요.",
  "배송비가 추가되는지 어디서 확인하나요?",
  "상품가격과 최종 결제금액은 어떻게 비교하나요?",
  "정확한 수령 주소를 입력한 뒤 추가배송비·옵션을 포함한 최종 금액을 판매처에서 확인해 주세요."),
 ("사무실 화분","직장으로 보내는 축하화분은 받는 부서와 놓을 자리부터 확인합니다.",
  "화분은 책상형·바닥형 제품의 실제 크기와 관리 조건을 고려해 선택하세요.",
  "직장으로 화분을 당일 보낼 수 있나요?",
  "사무실에 둘 화분은 어떤 크기가 적합한가요?",
  "층·호실과 수령 담당자를 확인하고 해당 상품의 실제 크기와 배송 가능 시간을 비교해 주세요."),
 ("기념일 꽃 선물","기념일 일정과 꽃을 전달받을 장소가 같은지 먼저 파악합니다.",
  "꽃다발은 포장 분위기와 이동 편의성을, 화분은 공간과 관리 부담을 비교해 보세요.",
  "기념일 꽃을 오늘 받을 수 있나요?",
  "기념일 꽃다발의 포장과 크기는 어떻게 고르나요?",
  "집이나 약속 장소 중 수령지를 정하고 가능한 상품 준비 시간을 판매처에 문의해 주세요."),
 ("축하 리본 문구","축하화환과 조의용 화환의 리본 문구를 혼동하지 않도록 확인합니다.",
  "보내는 분의 상호명·성함과 행사 성격을 구분해 정확한 문구를 전달하세요.",
  "리본 문구가 있는 화환을 오늘 주문할 수 있나요?",
  "축하와 근조 리본의 발신 명의는 어떻게 적나요?",
  "상품의 리본 제공 여부와 행사장 인도 일정은 결제 전에 확인해야 합니다."),
 ("감사 꽃다발","감사나 응원의 꽃 선물은 받는 분의 취향과 전달 시점을 살펴봅니다.",
  "꽃다발의 포장과 색감, 카드에 들어갈 짧은 인사말을 함께 준비해 보세요.",
  "감사 꽃다발을 오늘 보낼 수 있나요?",
  "감사 카드와 꽃다발을 준비할 때 무엇을 확인하나요?",
  "상품의 실제 꽃 구성과 수령 가능 날짜를 확인하고 카드 문구를 별도로 전달해 주세요."),
 ("여러 건 주문","받는 사람이 서로 다른 꽃 주문은 상품번호와 주소를 건별로 분리합니다.",
  "꽃다발·화분·화환을 주문번호별로 정리하고 카드와 리본 발신 명의도 따로 확인하세요.",
  "꽃 선물을 여러 주소로 오늘 주문할 수 있나요?",
  "여러 꽃 주문에서 상품번호와 주소를 어떻게 관리하나요?",
  "각 배송 건의 주소·시간과 상품 준비 가능 여부는 판매처에서 개별 확인해야 합니다."),
 ("꽃 상품 구성","판매 이미지와 실제 준비되는 꽃의 종류가 항상 동일한 것은 아닙니다.",
  "꼭 필요한 꽃 색과 대체 가능한 조건을 구분해 개별 상품 상세화면에서 확인하세요.",
  "원하는 꽃 구성으로 오늘 주문할 수 있나요?",
  "꽃 사진과 실제 상품 구성은 어떻게 비교하나요?",
  "해당 품목의 준비 여부와 실제 구성은 판매처의 확인을 받아야 합니다."),
 ("행사장 꽃 반입","행사 장소에 외부 꽃장식을 설치할 수 있는지 먼저 확인합니다.",
  "화환을 세울 위치와 행사 관계자의 인계 시간은 주문 전에 정하는 편이 안전합니다.",
  "행사장에 꽃을 오늘 전달할 수 있나요?",
  "축하화환을 설치하기 전에 어떤 규정을 살펴야 하나요?",
  "반입 담당자와 시설의 수령 가능 시간을 확인해 판매처 상담 시 알려 주세요."),
 ("꽃 선물 예산","상품의 표시가격을 확인한 뒤 배송비와 선택 옵션을 함께 비교합니다.",
  "상품별 가격은 확인일 기준 참고값이며, 최종 결제금액은 판매처에서 다시 확인해야 합니다.",
  "정해진 예산으로 꽃을 오늘 주문할 수 있나요?",
  "상품가격과 배송비를 함께 비교하려면 어떻게 하나요?",
  "예산을 먼저 알려 주고 상품·옵션·배송비를 포함한 금액과 배송 가능 여부를 문의해 주세요."),
 ("당일 접수 일정","오늘 필요한 꽃이라면 선물할 시각보다 실제 수령 가능한 시간대를 확인합니다.",
  "판매처의 마감 시간과 제작 가능 상품은 주문 시점마다 달라질 수 있습니다.",
  "오늘 꽃배달 접수 마감은 언제 확인하나요?",
  "상품을 고르기 전에 어떤 배송 조건을 문의하나요?",
  "상품 종류와 정확한 주소를 알려주고 실제 가능 시간대를 판매처에서 확인해 주세요."),
)
ADDRESS=(
 "도로명 주소·건물명·층수 또는 호실을 빠뜨리지 않았는지 점검해 주세요. 수령자의 연락 가능 시간도 함께 확인하는 것이 좋습니다.",
 "가까운 이름의 건물과 혼동되지 않도록 전체 수령 주소를 사용하세요. 받는 분이 자리를 비운다면 대리 수령 가능 여부를 알아보세요.",
 "선물을 받을 장소가 집인지 직장인지 구분해 주세요. 회사라면 부서·층·호실과 실제 물품을 받을 담당자를 함께 정리하세요.",
 "행사장이나 장례시설은 실제 인계 장소를 확인해야 합니다. 건물 대표주소만으로 물품을 놓을 위치를 확정하지 마세요.",
 "가게 개업 선물은 영업 시작 시각과 수령 담당자가 나오는 시간을 구분해 주세요. 설치 가능한 공간도 미리 확인하는 것이 좋습니다.",
 "현장에서 꽃을 전달받을 수 있는 사람이 누구인지 알아보세요. 원하는 날짜와 수령 가능한 시각이 일치하는지도 살펴보는 편이 좋습니다.",
 "주문자와 받는 분이 다를 경우 두 연락처를 분리해 준비하세요. 정확한 주소를 입력한 뒤 상품번호와 희망일을 함께 전달해야 합니다.",
 "공동으로 주문할 때는 실제 수령인의 연락처와 발신 명의가 서로 다를 수 있습니다. 발신 인사말은 별도로 확인해 주세요.",
 "꽃이 도착한 뒤 다른 장소로 이동해야 한다면 포장 포함 크기를 살펴보세요. 수령 장소에서 보관할 수 있는지도 중요한 조건입니다.",
 "건물 내부 출입 규정과 꽃 수령 담당자 유무를 확인해 주세요. 판매처가 모든 건물의 인도 방식을 이미 알고 있다고 가정하지 마세요.",
 "실제 도로명 주소를 기준으로 주문해 주세요. 검색에 이용한 행정구역명만으로 배송 가능 시간과 요금을 단정할 수는 없습니다.",
 "받는 분이 없는 시간이라면 대신 받아줄 사람과 인도 방법을 확인해 주세요. 무인 보관은 사전 확인 없이 가능한 방식으로 단정하지 않습니다."
)
CHOICE=(
 "들고 이동할 꽃다발인지 오래 놓아둘 화분인지 목적을 먼저 정하세요. 행사장이나 빈소로 보낸다면 축하·근조화환 종류도 분리해야 합니다.",
 "꽃다발의 꽃 색과 포장, 화분의 크기와 관리 방법을 각각 비교해 주세요. 화환이라면 행사 목적과 리본 문구가 맞는지 확인해야 합니다.",
 "선물받는 분의 취향과 놓을 공간을 고려해 꽃을 고르세요. 사진에 나온 구성과 실제 준비 품목의 차이도 확인하는 것이 좋습니다.",
 "꽃다발을 옮겨야 한다면 포장 크기를 확인해 주세요. 화분은 식물을 둘 자리의 채광과 용기를 함께 살펴보세요.",
 "장례 조문과 축하 행사에 쓰는 화환은 명의·문구가 달라집니다. 실제 상품번호를 정한 뒤 리본에 들어갈 내용을 검토해 주세요.",
 "표시가격이 같아도 꽃 종류·크기·추가옵션이 다를 수 있습니다. 비교 중인 상품번호를 함께 적어 두면 주문 내역을 대조하기 쉽습니다.",
 "사무실에 둘 화분은 통로 폭과 관리 부담을 고려해 주세요. 선물 뒤 이동이 필요한 경우 꽃다발의 포장 크기도 중요합니다.",
 "행사 꽃을 주문할 때는 배치 장소와 반입 가능한 시각을 확인해 주세요. 설치형 화환과 손에 들 꽃다발은 조건이 다릅니다.",
 "받는 분이 꽃병을 가지고 있는지 모른다면 포장·용기 포함 여부를 확인해 주세요. 화분을 택했다면 식물 관리 방법도 살펴보세요.",
 "회사나 기관에 보낼 꽃 선물은 받는 사람과 인계 담당자가 다를 수 있습니다. 두 이름을 구분해 주문서에 적어 주세요.",
 "리본에 발신 명의를 넣는다면 오타와 띄어쓰기를 점검하세요. 꽃다발 카드와 화환 리본은 사용 목적을 혼동하지 않아야 합니다.",
 "선호하는 색이 있을 경우 우선순위를 정해 판매처에 알려주세요. 준비 가능한 꽃 종류와 상품 옵션은 최종 주문에서 확인할 수 있습니다."
)
CHECKOUT=(
 "동일한 행정구역 안에서도 상품 준비·배송 조건은 달라질 수 있습니다. 현재 배송 마감과 재고는 판매처에 확인해야 합니다.",
 "배송 희망 시각을 고정된 약속으로 안내하지 마세요. 정확한 주소·상품번호를 기준으로 판매처에 가능한 시간을 문의해 주세요.",
 "추가배송비는 일부 상품이나 주소에서 발생할 수 있습니다. 실제 적용되는 요금은 선택한 SKU의 주문 화면에서 확인해 주세요.",
 "화환은 빈소 또는 행사장 인계 방식이 중요합니다. 반입 허용 여부와 설치 시각은 현장 담당자에게 먼저 확인해야 합니다.",
 "상품의 꽃 종류와 가격은 확인 시점의 자료를 바탕으로 표시됩니다. 결제 전 현재 판매 여부와 금액을 반드시 다시 대조해 주세요.",
 "받는 분이 부재 중이라면 인도 방식부터 판매처와 협의해 주세요. 문앞 보관을 모든 지역의 기본 배송 방식으로 표시하지 않습니다.",
 "같은 날 배송이 필요하면 준비 가능한 품목을 먼저 문의하세요. 꽃 종류와 주문 시점에 따라 실제 제작 일정은 달라집니다.",
 "판매처의 주문 마감시각은 시·군·구별 고정 사실로 가정하지 않습니다. 주소와 상품을 전달해 현재 조건을 확인해 주세요.",
 "축하와 조문 목적은 서로 다른 상품 정보가 필요합니다. 리본 문구·행사 장소·실수령자를 결제 전 대조해 주세요.",
 "최종 결제금액에는 추가배송비나 옵션 비용이 반영될 수 있습니다. 보이는 상품 가격만으로 전체 비용을 확정하지 마세요.",
 "수령 시간을 계획한다면 현장 담당자가 실제로 꽃을 받을 수 있는지부터 확인하세요. 출입 제한이 있다면 미리 설명해 주세요.",
 "상품명만 전달하기보다 판매처의 SKU와 개별 주문 링크를 확인하는 편이 좋습니다. 구성·가격·배송 조건은 마지막 주문 화면을 기준으로 판단해 주세요."
)

def _pick(items, seed):
    value=int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8],"big")
    return items[value%len(items)]

@lru_cache(maxsize=1)
def legal_regions(root:Path):
    data=(root/ARCHIVE).read_bytes()
    if hashlib.sha256(data).hexdigest()!=ZIP_SHA256:
        raise ConfigError("Todayflower pinned legal ZIP SHA-256 mismatch")
    with ZipFile(io.BytesIO(data)) as z:
        names=[n for n in z.namelist() if n.endswith(".txt")]
        if len(names)!=1:raise ConfigError("Unexpected legal ZIP contents")
        t=z.read(names[0]).decode("cp949")
    reader=csv.DictReader(io.StringIO(t),delimiter="\t")
    if reader.fieldnames!=["법정동코드","법정동명","폐지여부"]:
        raise ConfigError("Legal ZIP expected columns changed")
    regions=[];counts={}
    for row in reader:
        if row["폐지여부"]!="존재":continue
        code,name=row["법정동코드"].strip(),row["법정동명"].strip()
        parts=name.split()
        if not (len(code)==10 and code.isdigit()):
            raise ConfigError("Malformed legal code in archived source")
        if not (code.endswith("00") and len(parts)>=2
                and parts[-1].endswith(("동","읍","면","가","로"))):
            continue
        province=parts[0]
        if province not in EXPECTED:raise ConfigError("Unexpected archived province "+province)
        counts[province]=counts.get(province,0)+1
        regions.append((code,name))
    regions.sort()
    if counts!=EXPECTED or len(regions)!=EXPECTED_DONG_COUNT:
        raise ConfigError("Historical nationwide legal-code distribution changed")
    if len(set(regions))!=len(regions) or len({v[0] for v in regions})!=len(regions):
        raise ConfigError("Duplicate legal region codes")
    return tuple(regions)

def _make_page(code,name,number):
    scenario=SCENARIOS[int.from_bytes(hashlib.sha256(("todayflower:"+code).encode()).digest()[:8],"big")%len(SCENARIOS)]
    intent,focus,products,q1,q2,response=scenario
    label=name
    seed=code+":todayflower:delivery"
    intro=(f"{label}에서 꽃배달 당일배송 가능 여부를 확인하려면 실제 수령 주소와 날짜가 필요합니다. "
           f"{focus} 상품 종류와 접수 시점에 따라 가능한 시간은 달라질 수 있으므로 오늘 도착을 보장하지 않습니다.")
    area=(f"{label}의 법정동 코드는 {code}이며 출처는 2026년 10월 22일 고정 자료입니다. "
          "이 코드는 배송을 보장하거나 현재의 행정동 구역·판매처 배송 범위를 증명하지 않습니다.")
    # Distinct independently seeded, relevant customer decision points:
    # never pad uniqueness with fake local shops, delivery times or testimonials.
    sections=[
        {"heading":intent+" 목적과 상품 선택",
         "paragraph":focus+" "+products+" "+_pick(CHOICE,seed+":choice")
            +" "+_pick(CHECKOUT,seed+":opening-condition")},
        {"heading":"실제 수령주소와 담당자 확인",
         "paragraph":_pick(ADDRESS,seed+":address")+" "+area
            +" "+_pick(ADDRESS,seed+":alternative-address")},
        {"heading":"꽃다발·화분·축하·근조화환 주문 기준",
         "paragraph":_pick(CHOICE,seed+":product")+" "+_pick(ADDRESS,seed+":method")
            +" "+_pick(CHOICE,seed+":second-choice")},
        {"heading":"당일 수령 가능 여부·마감·최종 비용",
         "paragraph":_pick(CHECKOUT,seed+":checkout")+" "+_pick(CHECKOUT,seed+":after")
            +" "+_pick(CHECKOUT,seed+":final-condition")},
    ]
    faqs=[
        {"q":f"{label}에서 "+q1,
         "a":response+" "+_pick(CHECKOUT,seed+":first-faq")},
        {"q":q2,
         "a":products+" "+_pick(CHOICE,seed+":second-faq")},
        {"q":f"{label} 꽃배달을 주문할 때 무엇을 알려야 하나요?",
         "a":_pick(ADDRESS,seed+":third-faq")+" 선택한 SKU와 최종 결제금액을 판매처에서 확인해 주세요."},
    ]
    skus=PRODUCT_SETS[int.from_bytes(hashlib.sha256((seed+":sku").encode()).digest()[:2],"big")%len(PRODUCT_SETS)]
    return {
        "id":"today-national-"+code,
        "number":number,
        "region":name,
        "topic":intent,
        "searchKeyword":"꽃배달 당일배송",
        "title":name+" 꽃배달 당일배송 문의 | "+intent+"·수령 조건·주문 안내",
        "intro":intro,
        "heroTag":name+" · "+intent,
        "sectionLead":"정확한 수령주소와 용도에 맞는 상품을 비교하고 판매처에서 배송 가능 시각을 확인하세요.",
        "sections":sections,
        "productSkus":list(skus),
        "faq":faqs,
        "evidenceScope":"2026-10-22 pinned legal-code snapshot; same-day delivery and local service availability NOT verified",
    }

def expand(site,pages,regions,root:Path):
    policy=site.get("todayflowerNational") or {}
    if not policy.get("enabled",False):return pages,regions
    if site.get("id")!="todayflower-nalmada":
        raise ConfigError("Todayflower national generator may not change other sites")
    if site.get("publishEnabled") or site.get("indexNow",{}).get("enabled"):
        raise ConfigError("Bulk nationwide generation is preview-only until verified public release")
    if (len(pages)!=EXPECTED_ORIGINAL or [p["number"] for p in pages]!=list(range(1,34))
            or policy.get("expectedLegalDongCount")!=EXPECTED_DONG_COUNT
            or policy.get("expectedPageCount")!=EXPECTED_TOTAL
            or policy.get("archiveSHA256")!=ZIP_SHA256):
        raise ConfigError("Current 33 reviewed pages or national source identity mismatch")
    official=legal_regions(root)
    prior={r["code"]:r["name"] for r in regions["regions"] if r.get("level")=="legal-dong"}
    if len(prior)!=30:
        raise ConfigError("The preserved Ansan 30 legal-dong source inventory changed")
    official_map=dict(official)
    for code,name in prior.items():
        if official_map.get(code)!=name:
            raise ConfigError("Existing Ansan official code/name disagrees with nationwide snapshot: "+code)
    new=[(code,name) for code,name in official if code not in prior]
    if len(new)!=EXPECTED_NEW:
        raise ConfigError("Unexpected nationwide legal-dong delta count")
    generated=[_make_page(code,name,i+34) for i,(code,name) in enumerate(new)]
    original_ids={p["id"] for p in pages}
    if any(p["id"] in original_ids for p in generated):
        raise ConfigError("National page identity collision")
    all_regions=list(regions["regions"])
    all_regions.extend({
        "code":code, "name":name, "level":"legal-dong",
        "sourceAsOf":"2026-10-22",
        "deliveryVerified":False,
    } for code,name in new)
    if len(pages)+len(generated)!=EXPECTED_TOTAL or len(all_regions)!=EXPECTED_TOTAL:
        raise ConfigError("Unexpected national page or region count")
    return pages+generated, {
        **regions,"regions":all_regions,
        "nationwideLegalDongCount":EXPECTED_DONG_COUNT,
        "nationwideAddedCount":EXPECTED_NEW,
        "nationwideArchiveSHA256":ZIP_SHA256,
        "scopeNote":"Pinned historical legal-code inventory, NOT current legal status or verified local same-day delivery",
    }
