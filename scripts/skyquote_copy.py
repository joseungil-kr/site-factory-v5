"""Visitor-first Korean Skyquote copy shared by all three page generators.

Only verified operator-published rates/contact details are stated as facts.
No defensive AI captions, coaching tone, unsupported local/service claims or lowest-price guarantees.
"""
from html import escape

PHONE="010-5322-1952"
TEL="tel:01053221952"
OPERATOR_URL="https://www.skycar1day.com/"
PRICE_ROWS=[
    ("1톤 스카이차","30만 원","50만 원"),
    ("3.5톤 스카이차","40만 원","60만 원"),
    ("5톤 스카이차","50만 원","70만 원"),
]
def hero(location):
    return (
      f"<p>{escape(location)} 현장에 필요한 스카이차를 알아보시나요? "
      "작업 높이와 차량을 세울 자리, 예상 시간을 알려주시면 조건에 맞춰 상담해 드립니다.</p>"
    )

def image(index, names, alt):
    loading='eager' if index==0 else 'lazy'
    priority=' fetchpriority="high"' if index==0 else ''
    return (f'<figure class="skyquote-illustration"><img src="/assets/{names[index]}.webp" '
            f'loading="{loading}"{priority} width="1536" height="1024" alt="{escape(alt[index])}"></figure>')

def section(title, body, image_html=""):
    return f'<section class="media"><div><h2>{title}</h2>{body}</div>{image_html}</section>'

def quote_sections(location, note, names, alts):
    blocks=[]
    blocks.append(section("작업 위치와 높이를 알려주세요",
        "<p>작업할 주소와 날짜, 시작 시간을 알려주세요. 건물 층수와 함께 작업 지점까지 높이(미터), "
        "차량을 세울 자리에서 작업 지점까지의 수평거리도 알려주시면 장비 상담에 도움이 됩니다.</p>"
        "<p>현장 전체와 작업할 면이 함께 보이는 사진을 보내주시면 위치를 파악하기 좋습니다.</p>",
        image(0,names,alts)))
    blocks.append(section("탑승 인원과 자재 무게도 함께 확인합니다",
        "<p>작업대에 오를 인원과 공구·자재의 무게, 작업 내용을 알려주세요. 차량은 높이뿐 아니라 "
        "수평거리와 적재 조건을 함께 살펴 선택합니다.</p>"
        "<p>차량을 세울 공간과 아웃트리거를 펼칠 자리도 사진에 담아 보내주세요.</p>",
        image(3,names,alts)))
    rows="".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a,b,c in PRICE_ROWS)
    blocks.append(section("영진스카이 공개 이용요금",
        "<p>아래는 운영업체가 공개한 기본 단가입니다. 부가세는 별도이며 기사 인건비·유류비·기본 장비 보험료가 포함됩니다.</p>"
        f'<div class="table"><table><thead><tr><th>장비</th><th>반나절 · 4시간</th><th>하루 · 8시간</th></tr></thead><tbody>{rows}</tbody></table></div>'
        "<p>초과·대기 시간 요금은 상담 시 확인해 주세요. 18시 이후 야간, 휴일 작업과 원거리 운반은 사전 협의에 따라 추가 비용이 발생할 수 있습니다.</p>",
        image(2,names,alts)))
    blocks.append(section("현장 진입과 작업 공간을 확인합니다",
        "<p>차량 진입로 폭과 회전 공간, 정차 위치, 지지대를 펼칠 바닥, 주변 전선과 장애물을 알려주세요. "
        "현장 조건을 살펴 적합한 장비와 준비 사항을 상담해 드립니다.</p>"
        "<p>간판·외벽·설비 등 어떤 작업인지도 함께 알려주시면 견적 상담이 수월합니다.</p>",
        image(4,names,alts)))
    blocks.append(section("견적 문의 전에 준비하면 좋은 내용",
        "<ul><li>정확한 작업 주소와 희망 날짜·시작 시간</li>"
        "<li>작업 지점의 실제 높이와 차량 정차 위치에서의 수평거리</li>"
        "<li>탑승 인원, 공구·자재 무게, 작업 내용</li>"
        "<li>진입로와 차량 정차 공간이 보이는 현장 사진</li>"
        "<li>예상 작업시간과 한 장소·여러 장소 작업 여부</li></ul>"
        "<p>기본 4시간·8시간 단가와 초과·대기·야간·이동 비용을 함께 확인해 총 이용금액을 비교해 보세요.</p>",
        image(1,names,alts)))
    return "".join(blocks)

def faq():
    return (
      '<section><h2>자주 묻는 질문</h2>'
      '<details><summary>반나절과 하루 요금은 몇 시간 기준인가요?</summary><p>공개 단가표 기준 반나절은 4시간, 하루는 8시간입니다. 초과·대기 시간 요금은 상담 시 확인해 주세요.</p></details>'
      '<details><summary>공개 요금에 포함되는 항목은 무엇인가요?</summary><p>기사 인건비와 유류비, 기본 장비 보험료가 포함되며 부가세는 별도입니다.</p></details>'
      '<details><summary>야간이나 먼 거리 작업은 추가 비용이 있나요?</summary><p>18시 이후 야간, 휴일 작업과 원거리 운반은 사전 협의에 따라 추가 비용이 발생할 수 있습니다.</p></details>'
      '<details><summary>견적을 받으려면 무엇을 알려드리면 되나요?</summary><p>작업 주소와 일정, 높이와 수평거리, 탑승 인원과 자재 무게, 예상 작업시간을 알려주세요. 현장 사진도 함께 보내주시면 상담에 도움이 됩니다.</p></details>'
      '</section>'
    )

def contact():
    return (
      '<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>'
      '<p>작업 위치와 희망 시간, 장비가 필요한 이유를 알려주세요. 공개 단가와 추가 비용을 확인한 뒤 이용 조건을 상담할 수 있습니다.</p>'
      f'<a class="cta" href="{TEL}">영진스카이 전화 상담 {PHONE}</a> '
      f'<a href="{OPERATOR_URL}">영진스카이 운영 사이트</a></section>'
    )

def footer():
    return f'<footer><a href="{TEL}">전화 상담 {PHONE}</a></footer>'
