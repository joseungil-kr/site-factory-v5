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

def price_table_html():
    rows="".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a,b,c in PRICE_ROWS)
    return (
        "<p>아래는 운영업체가 공개한 기본 단가입니다. 부가세는 별도이며 기사 인건비·유류비·기본 장비 보험료가 포함됩니다.</p>"
        f'<div class="table"><table><thead><tr><th>장비</th><th>반나절 · 4시간</th><th>하루 · 8시간</th></tr></thead><tbody>{rows}</tbody></table></div>'
        "<p>초과·대기 시간 요금은 상담 시 확인해 주세요. 18시 이후 야간, 휴일 작업과 원거리 운반은 사전 협의에 따라 추가 비용이 발생할 수 있습니다.</p>"
    )

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
    blocks.append(section("영진스카이 공개 이용요금",price_table_html(),image(2,names,alts)))
    blocks.append(section("현장 진입과 작업 공간을 확인합니다",
        "<p>차량 진입로 폭과 회전 공간, 정차 위치, 지지대를 펼칠 바닥, 주변 전선과 장애물을 알려주세요. "
        "현장 조건을 살펴 적합한 장비와 준비 사항을 상담해 드립니다.</p>"
        "<p>간판·외벽·설비 등 어떤 작업인지도 함께 알려주시면 견적 상담이 수월합니다.</p>",
        image(4,names,alts)))
    blocks.append(section("견적 금액에서 확인할 항목",
        "<p>같은 이용시간이라도 현장 이동이나 대기로 최종 금액이 달라질 수 있습니다. 상담할 때 아래 항목을 함께 확인해 보세요.</p>"
        "<ul><li><strong>출동·이동:</strong> 현장까지 이동거리와 원거리 운반 비용</li>"
        "<li><strong>시간 초과·대기:</strong> 기본 4시간 또는 8시간을 넘겼을 때 적용되는 기준</li>"
        "<li><strong>야간·휴일:</strong> 18시 이후 작업이나 휴일 일정의 추가 비용</li>"
        "<li><strong>부가세:</strong> 공개 단가에 별도로 계산되는 세액</li></ul>"
        "<p>비교 견적을 받으신다면 같은 작업시간과 비용 포함 범위로 총금액을 확인하시면 됩니다.</p>",
        image(1,names,alts)))
    return "".join(blocks)

def faq():
    return (
      '<section><h2>자주 묻는 질문</h2>'
      '<details><summary>현장 사진은 어디를 촬영하면 좋나요?</summary><p>차량을 세울 장소가 넓게 보이는 사진과 실제 작업 지점이 보이는 사진을 각각 준비해 주세요. 전선·차양 등 주변 구조물도 함께 보이면 좋습니다.</p></details>'
      '<details><summary>작업 시간이 길어지면 어떻게 하나요?</summary><p>예상보다 시간이 더 필요할 수 있다면 상담 단계에서 초과시간 요금과 대기료가 언제부터 적용되는지 확인하시면 됩니다.</p></details>'
      '<details><summary>일정 변경이나 취소 조건도 알 수 있나요?</summary><p>희망 날짜와 시작 시간을 정하신 뒤 변경·취소 가능 시점과 재출동 비용을 전화 상담에서 확인하실 수 있습니다.</p></details>'
      '</section>'
    )

def contact():
    return (
      '<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>'
      '<p>현장 사진이나 작업 조건이 준비됐다면 전화로 문의해 주세요. 장비 이용시간과 추가 비용을 함께 상담하실 수 있습니다.</p>'
      f'<a class="cta" href="{TEL}">영진스카이 전화 상담 {PHONE}</a> '
      f'<a href="{OPERATOR_URL}">영진스카이 운영 사이트</a></section>'
    )

def footer():
    return f'<footer><a href="{TEL}">전화 상담 {PHONE}</a></footer>'
