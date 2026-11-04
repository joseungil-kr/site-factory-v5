"""Clinic 3-site product-first representative pages — six noindex HTML files.

This is a reviewed pilot, not the nationwide 15906 HTML release.
User-approved exact seller photos; don't claim any pictured wreath is a clinic delivery.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json

OUT = Path(__file__).resolve().parent
E = lambda s: escape(str(s), quote=True)
PHONE = "1844-0644"
TEL = "tel:1844-0644"
TARGETS = (("ansan", "안산시", "안산시"), ("bono", "경기도 안산시 상록구 본오동", "본오동"))
BODY_RULE = "받으실 주소와 날짜, 원하시는 상품을 알려주시면 배송비와 주문 일정을 함께 안내해 드립니다."
REGION_EXTRA = ("안산시 상록구 본오동에 전달할 때는 '경기도 안산시 상록구 본오동' 뒤에 "
                "건물명과 층수를 함께 알려주세요. 받는 분의 연락처까지 준비하시면 주문이 편리합니다.")

CONFIG = {
    "clinicflower": {
        "name": "개업·개원축하화분",
        "theme": "flower",
        "eyebrow": "병원·치과·한의원 / 오래 두고 볼 축하 선물",
        "heading": "병원·치과·한의원 개업화분·개원축하화분",
        "subheading": "개원 뒤에도 두고 볼 화분, 받는 공간에 맞춰 선택하세요.",
        "lead": "접수대에 올려 둘지 로비에 둘지에 따라 고려할 화분이 달라집니다. 실제 판매 중인 금전수·녹보수의 사진과 가격을 비교하고, 놓을 위치와 관리 여건을 확인하세요.",
        "products": ["D144", "D149"],
        "selection": [
            ("D144", "작은 공간에서 먼저 비교", "금전수 탁상용을 검토할 때는 접수대 주변에 놓을 자리가 있는지 확인하세요. 크기는 상품 상세에서 살펴보실 수 있습니다."),
            ("D149", "식물을 놓을 자리가 따로 있다면", "녹보수 소형을 살펴볼 수 있습니다. 창가와 내부 대기실의 채광이 다르므로 받는 곳의 관리 여건도 함께 묻는 편이 좋습니다.")
        ],
        "advantages": [
            ("어디에 놓나요?", "접수대·대기실·원장실 중 비치할 곳을 정하고 통행을 막지 않을 크기를 상담하세요."),
            ("누가 관리하나요?", "식물별 물주기와 채광 조건은 다릅니다. 관리 담당자에게 확인하기 쉬운 품종을 고르세요."),
            ("어떤 문구가 좋나요?", "‘축 개원’ 또는 ‘개원을 축하합니다’처럼 짧은 문구와 발신자 이름을 준비하세요.")
        ],
        "script": "“안산시 병원 개원선물로 D144와 D149를 비교 중입니다. 받을 곳은 접수대 옆이고 희망일은 ○월 ○일입니다. 크기와 배송비까지 알려주세요.”",
        "faqs": [
            ("접수대 위에 둘 화분은 어떤 것을 보나요?", "금전수 탁상용 D144가 비교 후보입니다. 다만 접수대 공간, 실제 화분 규격, 관리 가능 여부를 확인한 후 결정하세요."),
            ("개원식이 끝난 뒤에도 선물할 수 있나요?", "가능한 상품이 있다면 행사 이후에 비치할 화분을 선택할 수 있습니다. 축하받을 분이 실제로 받을 날짜부터 확인하는 편이 좋습니다."),
            ("최종 가격은 표시된 금액과 같나요?", "표시된 금액은 판매처 확인 시점의 상품가격입니다. 배송지와 희망 날짜에 따른 추가 배송비는 주문 단계에서 안내받으실 수 있습니다.")
        ],
    },
    "clinicopen": {
        "name": "개원식 축하화분 주문",
        "theme": "open",
        "eyebrow": "병원·치과·한의원 / 개원식 날짜와 수령 안내",
        "heading": "병원·치과·한의원 개원식 축하화분 주문",
        "subheading": "개원식은 날짜보다 ‘언제, 누구에게 전달할지’가 중요합니다.",
        "lead": "진료 시작일과 개원식이 다르거나 행사 공간이 따로 있을 수 있습니다. 먼저 받는 곳의 행사 일정과 담당자를 확인하고 실제 상품을 비교하세요.",
        "products": ["D149", "D144"],
        "selection": [
            ("D149", "행사 뒤 비치할 자리를 고려", "녹보수 소형을 보낼 때는 행사장 전시 후 어디에 둘지 생각하세요. 상품 사진과 상세정보에서 화분의 크기를 비교해 보세요."),
            ("D144", "직접 인계할 때 비교", "금전수 탁상용도 개원 축하 선물의 후보입니다. 행사 담당자에게 직접 전할지 접수대에서 받을지 정해 보세요.")
        ],
        "advantages": [
            ("행사 날짜 확정", "‘개원식 당일’인지 ‘진료 시작일’인지 구분하세요. 실제 인수 가능 시간을 먼저 확인합니다."),
            ("수령 담당자 지정", "원장님이 행사 중이면 연락을 받을 직원이나 담당자를 따로 지정하는 편이 수월합니다."),
            ("설치·보관 위치", "행사장·로비·접수대 중 어느 곳에서 화분을 받을 수 있는지 확인하세요. 받는 직원과 인계 장소를 정해 두면 편리합니다.")
        ],
        "script": "“안산시 치과 개원식 축하화분을 보내려고 합니다. 개원식은 ○월 ○일이고 담당자는 접수대 직원입니다. D149·D144 중 행사장에 맞는 상품과 인계 조건을 알려주세요.”",
        "faqs": [
            ("개원식 시간에 맞춰 반드시 도착하나요?", "특정 시간 도착은 상품·수령 주소·주문 시각에 따라 달라집니다. 받을 날짜·시간과 담당자 연락처를 함께 알려주시면 배송 일정을 상담할 수 있습니다."),
            ("병원에 사람이 없으면 문 앞에 둘 수 있나요?", "담당자가 자리를 비운다면 대신 받아주실 분과 장소를 알려주세요. 건물 출입 가능한 시간도 함께 전달하면 좋습니다."),
            ("행사일이 바뀌면 변경할 수 있나요?", "일정이 바뀌었다면 꽃 제작·출고 상황에 따른 변경 가능 시간을 주문처에 문의해 주세요.")
        ],
    },
    "clinicpresent": {
        "name": "개업 축하화환",
        "theme": "present",
        "eyebrow": "병원·치과·한의원 / 개원식 행사 축하화환",
        "heading": "병원·치과·한의원 개업 축하화환 추천",
        "subheading": "개원식 공간에 어울리는 축하화환을 골라보세요.",
        "lead": "개원식에 전할 축하 3단·4단 화환을 사진과 가격으로 비교하세요. 화환을 놓을 공간과 리본 문구를 함께 정리하시면 상품 선택이 쉬워집니다.",
        "products": ["C200", "C206"],
        "selection": [
            ("C200", "3단 화환을 비교한다면", "축하 3단 화환 C200은 개원식에 보낼 화환을 검토할 때 선택지입니다. 꽃 구성과 화환 크기는 상품 상세에서 비교해 보세요."),
            ("C206", "4단을 원한다면", "축하 4단 화환 C206은 3단과 가격 차이가 있으므로 전시 장소의 반입 가능 규격과 실제 꽃 구성을 먼저 비교하세요.")
        ],
        "advantages": [
            ("반입부터 확인", "병원·치과 건물에는 화환을 세울 장소가 없을 수 있습니다. 실내·실외 설치 허용 여부를 수령처에 물어보세요."),
            ("리본 문구 검토", "의료기관의 정식 상호와 ‘축 개원’ 같은 축하 문구, 보내는 분 이름을 정확하게 준비하세요."),
            ("철수·회수 조건", "화환 철수·회수 서비스가 포함돼 있는지 현장에서 요구하는지 판매처에 확인하세요.")
        ],
        "script": "“안산시 한의원 개원식에 축하화환을 보내려 합니다. 건물 로비 반입 여부는 확인 중이며, 축하 3단 C200과 4단 C206의 구성과 최종 배송비를 비교하고 싶습니다.”",
        "faqs": [
            ("축하 리본에는 어떤 문구를 적으면 좋을까요?", "리본에는 ‘축 개원’ 등 전하고 싶은 축하 문구와 보내는 분의 이름을 적으실 수 있습니다. 원하시는 문구를 주문할 때 알려주세요."),
            ("접수대 옆에 축하화환을 세워도 되나요?", "실내에 놓을 수 있는지 행사장 담당자에게 문의해 주세요. 받는 곳에서 정해 주신 위치를 알려주시면 인계 방법을 상담할 수 있습니다."),
            ("3단과 4단 중 무엇이 더 좋은가요?", "단수만으로 우열을 정할 수 없습니다. 상품 사진·규격과 전시 공간, 배송비를 함께 비교하면 선택하기 좋습니다.")
        ],
    },
}

CSS = r"""
:root{color-scheme:light;font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;color:#17362e;background:#fafbf9;font-size:16px;line-height:1.65;word-break:keep-all}
body.theme-flower{--brand:#17684e;--brand2:#0c4d38;--wash:#eaf4eb;--border:#dbe9df}
body.theme-open{--brand:#235c94;--brand2:#164771;--wash:#eaf3fa;--border:#d8e4f0}
body.theme-present{--brand:#864154;--brand2:#682e41;--wash:#faf0f1;--border:#eddce0}
a{color:inherit}
.wrap{width:min(1120px,calc(100% - 36px));margin-inline:auto}
.site-header{background:#fff;border-bottom:1px solid var(--border);position:relative;z-index:3}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:76px}
.brand{font-size:23px;font-weight:850;letter-spacing:-.06em;color:var(--brand2);text-decoration:none}
.brand small{display:block;font-size:11px;font-weight:500;letter-spacing:0;color:#697a72;line-height:1.1}
.header-nav{display:flex;align-items:center;gap:20px;font-size:14px}
.header-nav .nav-link{color:#526459;text-decoration:none;font-weight:700}
.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:10px;padding:13px 20px;text-decoration:none;font-weight:800;min-height:46px;border:1px solid transparent;transition:transform .15s}
.button:hover{transform:translateY(-1px)}
.button-primary{background:var(--brand);color:#fff}
.button-ghost{background:#fff;border:1px solid var(--brand);color:var(--brand2)}
.hero{background:linear-gradient(140deg,var(--wash),#fff 85%);padding:56px 0 44px}
.hero-layout{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:54px;align-items:center}
.eyebrow{font-size:12px;color:var(--brand2);font-weight:850;letter-spacing:.04em}
.hero h1{font-size:clamp(31px,3.9vw,49px);letter-spacing:-.055em;line-height:1.24;margin:16px 0}
.hero h2{font-size:clamp(19px,2.1vw,24px);margin:0 0 12px;color:var(--brand2);letter-spacing:-.03em;font-weight:750}
.hero .lead{font-size:16px;color:#455c50;max-width:620px}
.hero-actions{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0 0}
.hero-small{font-size:13px;color:#506359;margin:16px 0 0}
.hero-picture{margin:0;background:#fff;border:1px solid var(--border);border-radius:20px;box-shadow:0 18px 44px #174a3320;overflow:hidden}
.hero-picture img{display:block;width:100%;height:390px;object-fit:contain;object-position:center;background:#f6f7f4}
.hero-picture figcaption{font-size:12px;color:#54665a;padding:11px 16px}
.proof-strip{background:#fff;border-bottom:1px solid var(--border);padding:15px 0}
.proof-strip .wrap{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
.proof-strip span{font-size:13px;color:#486155;font-weight:650}
.section{padding:58px 0}
.section.alt{background:var(--wash)}
.section-heading{margin-bottom:25px}
.section-heading h2{font-size:clamp(25px,2.8vw,32px);line-height:1.3;margin:5px 0 9px;letter-spacing:-.04em}
.section-heading p{color:#51655a;max-width:760px;margin:0}
.product-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}
.product-card{background:#fff;border:1px solid var(--border);border-radius:18px;overflow:hidden;min-width:0;box-shadow:0 9px 30px #173c2810}
.product-photo{position:relative;padding:17px;background:#f7f8f6}
.product-photo img{display:block;width:100%;height:286px;object-fit:contain;background:#f2f4f1;border-radius:12px}
.product-photo .label{position:absolute;top:27px;left:27px;color:var(--brand);background:#fff;padding:5px 12px;border-radius:999px;font-size:12px;font-weight:800;box-shadow:0 3px 8px #173c2810}
.product-info{padding:26px}
.product-info h3{font-size:23px;margin:0 0 5px;letter-spacing:-.04em}
.product-info p{margin:10px 0;color:#52675b}
.product-price{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.product-price strong{font-size:30px;color:var(--brand2);letter-spacing:-.035em}
.product-price small{font-size:12px;color:#67776c}
.product-actions{display:flex;gap:10px;margin-top:18px}
.product-actions .button{flex:1;min-width:0}
.price-note{font-size:13px;color:#57695e;margin:18px 0 0}
.difference-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.difference{background:#fff;padding:25px;border:1px solid var(--border);border-radius:15px}
.difference b{font-size:17px;color:var(--brand2)}
.difference h3{font-size:19px;margin:7px 0}
.difference p{margin:0;color:#52675b}
.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:17px}
.step{background:#fff;border:1px solid var(--border);padding:22px;border-radius:15px}
.step .n{display:inline-block;background:var(--wash);color:var(--brand2);border-radius:7px;padding:2px 9px;font-weight:800;font-size:12px}
.step h3{font-size:19px;margin:13px 0 8px}
.step p{color:#51665b;margin:0}
.example{border-left:4px solid var(--brand);background:#fff;padding:22px 24px;border-radius:0 12px 12px 0;margin-top:20px;color:#35564a}
.example strong{display:block;margin-bottom:7px}
.faq details{border-bottom:1px solid #dae5dd;padding:18px 0}
.faq summary{cursor:pointer;font-weight:780;font-size:17px}
.faq details p{max-width:850px;margin:12px 0 4px;color:#52665b}
.bottom-cta{background:var(--brand2);color:white;text-align:center;padding:50px 18px}
.bottom-cta h2{font-size:29px;margin:0 0 9px}
.bottom-cta p{color:#e0ece5;margin:0 0 24px}
.bottom-cta .button{background:#fff;color:var(--brand2)}
.footer{background:#f3f6f2;padding:21px 0;color:#506258;font-size:13px}
.footer .wrap{display:flex;gap:12px;justify-content:space-between;flex-wrap:wrap}
.mobile-order{display:none}
@media(max-width:900px){.hero-layout{gap:22px}.hero-picture img{height:330px}.product-actions{flex-direction:column}}
@media(max-width:650px){
 body{padding-bottom:72px}
 .wrap{width:min(100% - 28px,1120px)}
 .site-header .wrap{min-height:64px}
 .brand{font-size:21px}
 .header-nav .nav-link{display:none}
 .header-nav .button{padding:9px 12px;font-size:13px}
 .hero{padding:28px 0 34px}
 .hero-layout{grid-template-columns:1fr;gap:23px}
 .hero h1{font-size:31px;margin:9px 0}
 .hero h2{font-size:19px}
 .hero .lead{font-size:15px}
 .hero-actions{gap:9px}
 .hero-actions .button{font-size:14px}
 .hero-picture img{height:270px}
 .section{padding:37px 0}
 .product-grid,.difference-grid,.steps{grid-template-columns:1fr;gap:14px}
 .section-heading h2{font-size:25px}
 .product-photo img{height:260px}
 .product-info{padding:19px}
 .product-info h3{font-size:21px}
 .product-actions{flex-direction:row}
 .product-actions .button{padding:11px 12px;font-size:14px}
 .difference,.step{padding:19px}
 .proof-strip span{font-size:12px}
 .bottom-cta h2{font-size:24px}
 .mobile-order{display:block;position:fixed;bottom:0;left:0;right:0;padding:10px 14px;background:#fff;box-shadow:0 -7px 22px #12291b20;z-index:20}
 .mobile-order a{display:flex;align-items:center;justify-content:center;background:var(--brand);color:#fff;border-radius:9px;height:50px;text-decoration:none;font-size:17px;font-weight:850}
}
/* 축하화환 제품사진은 꽃 구성 중심으로 표시. 사진 속 행사 리본은 화면 밖으로 배치. */
.theme-present .hero-picture{overflow:hidden}
.theme-present .hero-picture img{object-fit:cover;object-position:center;transform:scale(1.92);transform-origin:50% 46%}
.theme-present .product-photo{overflow:hidden}
.theme-present .product-photo img{object-fit:cover;object-position:center;transform:scale(1.92);transform-origin:50% 47%}

"""

def product_card(info, sku):
    product = info[sku]
    name = E(product["name"])
    value = f'{product["priceKRW"]:,}원'
    photo = E(product["imageUrl"])
    detail = E(product["orderUrl"])
    caption = ("축하 리본 문구를 주문할 때 선택하세요" if sku.startswith("C")
               else "판매처 상품 사진")
    return (f'<article class="product-card" data-sku="{E(sku)}">'
            f'<div class="product-photo"><img loading="lazy" decoding="async" src="{photo}" '
            f'width="500" height="500" alt="{name} 상품 사진 — 꽃이랑 판매처" />'
            f'<span class="label">상품코드 {E(sku)}</span></div>'
            f'<div class="product-info"><h3>{name}</h3>'
            f'<div class="product-price"><strong>{value}</strong><small>판매처 확인가</small></div>'
            f'<p>{E(caption)}</p>'
            f'<div class="product-actions">'
            f'<a class="button button-primary" target="_blank" rel="noopener noreferrer" href="{detail}">상품 상세·주문</a>'
            f'<a class="button button-ghost" href="{TEL}">전화 문의</a></div></div></article>')


# A locality detail is a different user task from a city-wide product chooser.
# The exact address / on-site handover workflow is useful without asserting that
# we have a physical shop or a guaranteed delivery slot in the locality.
REGIONAL = {
  "clinicflower": {
    "headline":"경기도 안산시 상록구 본오동 병원·치과·한의원 개원축하화분",
    "subtitle":"받는 장소와 관리 여건을 먼저 정하고 보내세요.",
    "summary":"본오동 의료기관에 개업화분을 보낼 계획이라면 받는 건물과 화분을 놓을 자리를 알려주시면 선택하기 좋습니다. 상세주소와 희망 날짜를 알려주시면 배송비와 일정을 안내해 드립니다.",
    "photo":"D149",
    "sectionTitle":"본오동 의료기관으로 화분을 보낼 때 확인할 다섯 가지",
    "topics":[
      ("받을 주소를 끝까지 확인","받는 분의 도로명주소와 건물명·층수·호실을 함께 알려주세요. 접수대에서 받을지 원장실로 전달할지도 정하시면 좋습니다."),
      ("화분을 놓을 자리 확인","병원 접수대에 놓으려는 화분인지, 원장실이나 대기실에 두려는지 먼저 결정하세요. 진료공간에서는 방문객과 직원이 지나가는 동선을 막지 않는 것이 중요합니다. 상품 상세에서 크기를 살펴본 후 놓을 공간과 비교해 보세요."),
      ("식물을 돌볼 분 확인","선물하는 분은 개원일에 집중하지만 받는 의료기관은 이후에도 화분을 관리해야 합니다. 자연광이 드는 자리인지, 물주기를 맡을 사람이 있는지 확인해 두면 부담을 줄이는 데 도움이 됩니다. 품종별 관리 조건은 주문 시 함께 확인하세요."),
      ("리본에 쓸 정식 명칭 확인","의료기관 이름에는 병원·의원·치과의원·한의원 등이 포함될 수 있습니다. 리본에는 간판이나 초대장에 적힌 정확한 상호를 사용하는 편이 좋습니다. 발신자 이름·소속과 띄어쓰기도 주문 전에 문자로 정리해 두세요."),
      ("배송비와 인계 방식 확인","금전수 탁상용과 녹보수 소형은 상품가격이 서로 다릅니다. 받는 장소와 주문 날짜에 따라 배송비·제작 가능 여부가 달라질 수 있으므로 배송비까지 포함한 최종 금액은 주문 시 확인하실 수 있습니다. 부재 시 인계할 담당자도 함께 정하면 좋습니다.")
    ],
    "productTitle":"본오동 선물 후보 — 탁상용 금전수와 녹보수 소형",
    "productIntro":"금전수와 녹보수의 가격과 사진을 나란히 비교하고, 놓을 공간에 맞는 크기를 골라보세요.",
    "example":"“경기도 안산시 상록구 본오동의 치과의원에 개원축하화분을 보내려고 합니다. D144 금전수와 D149 녹보수 중 놓을 자리와 배송 가능일에 맞는 상품을 안내받고 싶습니다.”",
    "faqs":[
      ("받는 의료기관의 층수를 아직 모르면 주문할 수 있나요?","우선 정확한 주소와 인계할 담당자를 확인해 주세요. 같은 건물에도 여러 병원·의원이 있을 수 있으므로 의료기관 이름과 층수를 함께 확인한 뒤 주문하는 편이 안전합니다."),
      ("화분을 접수대에 바로 놓아도 되나요?","탁상 위에 놓을지 바닥에 둘지 알려주세요. 접수대 크기에 맞는 화분을 비교해 보실 수 있습니다."),
      ("본오동이라면 배송비가 동일한가요?","상품 가격에 배송지별 추가비용이 붙을 수 있습니다. 건물명과 층수를 알려주시면 배송비를 확인해 드립니다.")
    ]
  },
  "clinicopen": {
    "headline":"경기도 안산시 상록구 본오동 병원·치과·한의원 개원식 축하화분 주문",
    "subtitle":"개원식에 맞춰 받으실 시간과 담당자를 정해 보세요.",
    "summary":"본오동 개원식에 보내는 화분은 행사일과 실제 진료 시작일이 다를 수 있다는 점부터 확인하면 좋습니다. 행사장 입구에 두는지 접수대에서 받는지에 따라 담당자·출입 시간·인계 방법이 달라질 수 있습니다.",
    "photo":"D144",
    "sectionTitle":"본오동 개원식 화분 주문을 위한 행사 당일 체크리스트",
    "topics":[
      ("개원식이 열리는 날짜부터 확정","초대장에 적힌 개원식 날짜와 실제 진료 시작일이 같은지 확인하세요. 꽃을 받을 담당자가 출근하는 시각과 행사가 시작되는 시각도 다를 수 있습니다. 날짜만 전달하면 원하는 수령 장면과 다르게 도착할 수 있습니다."),
      ("행사장 위치와 진료실 주소 구분","개원식은 의료기관 내부 로비 또는 다른 공간에서 진행될 수 있습니다. 도로명주소와 건물명뿐 아니라 수령할 층·출입구를 확인하고, 화분을 행사장에서 직접 받아 줄 분이 있는지 알아두세요."),
      ("수령 담당자를 한 명 정하기","행사 중 원장님은 방문객을 맞이하느라 연락이 어려울 수 있습니다. 배송 기사의 연락을 받을 직원이나 행사 담당자의 연락 방법을 미리 정리하세요. 연락이 닿는 직원에게 인계할 수 있도록 수령 담당자를 정해 주세요."),
      ("리본과 행사 메시지 전달","공식 의료기관명, ‘축 개원’ 같은 짧은 축하 문구, 보내는 분의 소속과 이름을 분리해서 전달하세요. 공동 원장이나 여러 발신자가 있더라도 주문 전에 어떤 표기를 원하는지 확인하면 오탈자를 줄일 수 있습니다."),
      ("지연·일정 변경에 대비","개원 행사 시간은 변경될 수 있고 꽃 제작 후에는 변경이 제한될 수도 있습니다. 예상 인계 시간을 조율할 수 있는지, 일정이 바뀌면 어디로 연락해야 하는지 구매 단계에서 확인해 두세요.")
    ],
    "productTitle":"개원식 현장에서 받을 화분 두 가지",
    "productIntro":"D144 금전수 탁상용과 D149 녹보수 소형의 판매처 사진·가격을 비교하세요. 화분을 전달할 시간·인계할 담당자·행사 이후 비치할 공간을 함께 고려하는 것이 중요합니다.",
    "example":"“경기도 안산시 상록구 본오동 병원 개원식에 화분을 보냅니다. 행사 시작 시각은 ○시이고, 실제 수령 가능 시간과 직원 담당자를 확인 중입니다. D144와 D149 중 주문 가능한 상품을 확인하고 싶습니다.”",
    "faqs":[
      ("개원식 전날 미리 보내는 것이 더 좋은가요?","개원식 전날 받으시려면 담당자가 화분을 보관할 장소와 시간을 알려주세요."),
      ("행사장에 담당자가 없다면 어떻게 하나요?","접수대 직원이나 행사 담당자 중 받아주실 분의 이름과 연락처를 알려주세요."),
      ("리본 문구는 개원식 날 바로 정해도 되나요?","공식 의료기관명과 보내는 분의 이름을 알려주시면 리본 제작 가능 시간을 안내받으실 수 있습니다.")
    ]
  },
  "clinicpresent": {
    "headline":"경기도 안산시 상록구 본오동 병원·치과·한의원 개업 축하화환 추천",
    "subtitle":"실제로 세워 둘 수 있는 행사 장소인지부터 확인하세요.",
    "summary":"본오동 의료기관 개업식에 축하화환을 고르셨다면 행사장에 세울 수 있는 위치와 크기를 함께 살펴보세요. 설치 장소·수령 시간·리본 문구를 확인하고 3단 C200과 4단 C206의 구성을 비교하세요.",
    "photo":"C206",
    "sectionTitle":"본오동 의료기관 개업 축하화환 설치 전 점검",
    "topics":[
      ("꽃화환 반입이 가능한 건물인가요?","의료기관이 입주한 건물의 규정에 따라 화환을 실내에 세우지 못할 수도 있습니다. 수령처에 실내·실외 중 허용되는 위치와 화환 전체 높이를 제한하는지 확인해 주세요. 설치할 장소와 반입 시간을 알려주시면 주문 가능 여부를 상담해 드립니다."),
      ("화환을 어디서 인계할까요?","건물 로비·1층 출입구·행사장이 서로 다른 위치에 있을 수 있습니다. 정확한 도로명주소, 층수, 지정된 반입 출입구를 주문처에 알려 주세요. 환자와 방문객이 통행하는 공간은 피할 수 있는지 확인합니다."),
      ("3단과 4단은 가격만 다른가요?","판매처의 축하 3단 화환 C200은 59,000원, 축하 4단 화환 C206은 120,000원으로 표시돼 있습니다. 가격과 단수가 다르므로 꽃 구성과 실제 규격, 추가 배송비를 상품 상세에서 각각 비교해야 합니다. 꽃 구성과 크기는 각각의 상품 상세에서 확인하실 수 있습니다."),
      ("개원 축하 리본 문구 고르기","‘축 개원’과 의료기관의 정식 이름, 보내는 분의 이름을 함께 준비해 주세요."),
      ("행사 후 회수 조건도 확인하세요","축하화환은 행사 이후 정리·회수가 필요할 수 있습니다. 판매 상품에 회수 서비스가 포함되어 있는지, 행사장 측의 별도 규정이 있는지 확인해 주세요. 필요한 경우 행사 뒤 화환 정리·회수 비용도 함께 문의해 주세요.")
    ],
    "productTitle":"본오동 개업 행사 축하화환 — 3단 C200 / 4단 C206",
    "productIntro":"실제 판매처의 3단·4단 화환 사진과 가격입니다. 축하 3단·4단 화환의 꽃 구성을 비교해 보세요. 개원식 리본에는 원하시는 문구를 적으실 수 있습니다.",
    "example":"“경기도 안산시 상록구 본오동 한의원 개업식에 축하화환을 보내려고 합니다. 반입 장소는 확인 중이고, 3단 C200과 4단 C206의 규격·리본·배송비를 비교해 주문하고 싶습니다.”",
    "faqs":[
      ("실내 반입이 안 된다면 실외에 세우면 되나요?","실외 배치도 건물·행사장 동의를 받아야 합니다. 건물이나 행사장 담당자에게 실외 전시할 자리를 안내받아 주문처에 알려주세요."),
      ("병원명이 아닌 원장님 이름을 리본에 적어도 되나요?","수신 측 선호에 따라 다를 수 있습니다. 병원·치과의원·한의원의 정확한 공식 명칭과 원장 성명·직함을 확인한 뒤 표기 방법을 정해 주세요."),
      ("오늘 받아볼 수 있나요?","받는 주소와 희망 시간을 알려주시면 당일 제작·배송 가능 여부를 안내해 드립니다.")
    ]
  }
}

CSS += r"""
.local-check{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px}
.local-card{background:#fff;border:1px solid var(--border);border-radius:15px;padding:23px;min-width:0}
.local-card:nth-child(5){grid-column:span 2}
.local-card .n{display:inline-block;color:var(--brand2);background:var(--wash);font-size:12px;border-radius:6px;font-weight:800;padding:3px 9px}
.local-card h3{font-size:19px;margin:13px 0 8px}
.local-card p{margin:0;color:#465e52}
.local-hint{color:#52655a;font-size:15px;margin:15px 0}
@media(max-width:650px){.local-check{grid-template-columns:1fr}.local-card:nth-child(5){grid-column:auto}.local-card{padding:19px}}
"""

def render_region_detail(site,productmap):
    meta=CONFIG[site]
    local=REGIONAL[site]
    region="경기도 안산시 상록구 본오동"
    headline=local["headline"]
    title=headline+" | 꽃이랑"
    description=(local["summary"]+" 실제 꽃이랑 상품 사진·판매 가격·주문 링크와 전화 상담 정보를 확인하세요.")
    first=productmap[local["photo"]]
    steps="".join('<article class="local-card"><span class="n">CHECK '+str(i+1)+'</span><h3>'+E(h)+'</h3><p>'+E(t)+'</p></article>'
                  for i,(h,t) in enumerate(local["topics"]))
    cards="".join(product_card(productmap,sku) for sku in meta["products"])
    faqs="".join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>'
                 for q,a in local["faqs"])
    caution=("리본에는 ‘축 개원’ 등 원하시는 축하 문구를 적으실 수 있습니다."
             if site=="clinicpresent" else "받는 분이 좋아하실 식물과 화분 크기를 골라보세요.")
    content=f"""<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>{E(title)}</title>
<meta name="description" content="{E(description)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}">
<meta property="og:type" content="article"><meta property="og:image" content="{E(first['imageUrl'])}">
<meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="style.css"></head>
<body class="theme-{E(meta['theme'])}">
<header class="site-header"><div class="wrap">
<a class="brand" href="#" aria-label="꽃이랑"><span>꽃이랑</span><small>{E(meta['name'])}</small></a>
<nav class="header-nav" aria-label="화면 이동"><a href="#local" class="nav-link">수령 확인</a>
<a href="#products" class="nav-link">상품·가격</a><a href="{TEL}" class="button button-primary">☎ 1844-0644</a></nav>
</div></header><main>
<section class="hero"><div class="wrap hero-layout"><div class="hero-copy">
<span class="eyebrow">{region} · 받는 장소 중심 주문 안내</span>
<h1>{E(headline)}</h1><h2>{E(local['subtitle'])}</h2>
<p class="lead">{E(local['summary'])}</p>
<div class="hero-actions">
<a class="button button-primary" href="#local">수령·배송 확인 순서</a>
<a class="button button-ghost" href="#products">상품 가격 비교</a></div>
</div><figure class="hero-picture">
<img src="{E(first['imageUrl'])}" width="500" height="500"
alt="{E(first['name'])} 판매처 상품 사진" decoding="async" loading="eager" fetchpriority="high">
<figcaption>{E(first['name'])} · {('꽃 부분 확대' if site=='clinicpresent' else '상품 사진')}</figcaption>
</figure></div></section>
<section class="section" id="local"><div class="wrap">
<div class="section-heading"><span class="eyebrow">LOCAL HANDOVER CHECKLIST</span>
<h2>{E(local['sectionTitle'])}</h2>
<p>받으실 장소와 날짜를 알려주시면 상품과 배송 일정을 함께 알아보실 수 있습니다.</p>
</div><div class="local-check">{steps}</div>
<div class="example"><strong>전화로 주문 조건 확인할 때</strong>{E(local['example'])}</div>
</div></section>
<section class="section alt" id="products"><div class="wrap">
<div class="section-heading"><span class="eyebrow">VERIFIED PRODUCT OPTIONS</span>
<h2>{E(local['productTitle'])}</h2><p>{E(local['productIntro'])}</p>
</div><div class="product-grid">{cards}</div>
<p class="price-note">판매처 확인 상품가격이며 배송지별 추가 배송비는 주문할 때 안내받으실 수 있습니다.</p>
<p class="price-note">주문 일정 변경이나 취소를 원하시면 꽃이랑 1844-0644로 연락해 주세요. 상품 제작·출고 상황에 따른 처리 방법과 교환·반품 조건을 안내해 드립니다.</p>
</div></section>
<section class="section faq" id="faq"><div class="wrap">
<div class="section-heading"><span class="eyebrow">FAQ</span><h2>받는 장소에 관한 질문</h2></div>
{faqs}</div></section>
<section class="bottom-cta"><div class="wrap"><h2>{E(region)} 주문 상담</h2>
<p>상품코드와 받는 주소, 희망 날짜를 알려주시면 주문을 도와드립니다.</p>
<a class="button" href="{TEL}">☎ 1844-0644 전화 문의</a></div></section>
</main><footer class="footer"><div class="wrap"><span>꽃이랑 · {E(meta["name"])}</span>
<span>{PHONE} · 판매처 상품 상세에서 최종 금액 확인</span></div></footer>
<div class="mobile-order"><a href="{TEL}">☎ {PHONE} 전화 주문</a></div></body></html>"""
    assert content.count('class="product-card"')==2
    assert region in content and "noindex,nofollow,noarchive" in content
    assert "application/ld+json" not in content
    return content

def render_page(site,kind,productmap):
    if kind=='bono':
        return render_region_detail(site,productmap)
    meta=CONFIG[site]
    label,region,short = TARGETS[0 if kind=="ansan" else 1]
    headline=f'{region if kind=="bono" else short} {meta["heading"]}'
    title=headline+' | 꽃이랑'
    description= (f'{region} {meta["name"]} 추천. '+meta["lead"]+
                  ' 실제 상품사진·가격을 비교하고 1844-0644 또는 판매처에서 주문하세요.')
    src=productmap[meta["products"][0]]["imageUrl"]
    first=productmap[meta["products"][0]]
    cards="".join(product_card(productmap,sku) for sku in meta["products"])
    advantages="".join('<article class="step"><span class="n">'+str(i+1)+'</span><h3>'+E(h)+'</h3><p>'+E(p)+'</p></article>'
                       for i,(h,p) in enumerate(meta["advantages"]))
    differences="".join('<article class="difference"><b>'+E(sku)+'</b><h3>'+E(h)+'</h3><p>'+E(p)+'</p></article>'
                        for sku,h,p in meta["selection"])
    faqs="".join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>' for q,a in meta["faqs"])
    regional=('' if kind=="ansan" else '<p class="hero-small">'+E(REGION_EXTRA)+'</p>')
    important= (""
                "축하 리본에는 ‘축 개원’과 의료기관 이름, 보내는 분 이름을 정리해 주세요."
               if site=="clinicpresent"
               else "판매처에 등록된 상품 사진을 기준으로 비교합니다. 방문 공간의 크기와 관리 여건을 고려하세요.")
    html=f"""<!doctype html><html lang="ko">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>{E(title)}</title><meta name="description" content="{E(description[:190])}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(description[:190])}">
<meta property="og:image" content="{E(src)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="style.css"></head>
<body class="theme-{E(meta['theme'])}">
<header class="site-header"><div class="wrap">
<a href="#" class="brand" aria-label="꽃이랑 안내 첫 화면">꽃이랑<small>의료기관 개원 축하 선물</small></a>
<nav class="header-nav" aria-label="화면 이동">
<a class="nav-link" href="#products">상품 비교</a><a class="nav-link" href="#ordering">주문 준비</a>
<a class="button button-primary" href="{TEL}">☎ 1844-0644</a>
</nav></div></header>
<main>
<section class="hero"><div class="wrap hero-layout">
<div class="hero-copy"><span class="eyebrow">{E(region)} · {E(meta["eyebrow"])}</span>
<h1>{E(headline)}</h1><h2>{E(meta["subheading"])}</h2>
<p class="lead">{E(meta["lead"])}</p>
<div class="hero-actions"><a class="button button-primary" href="#products">실제 상품·가격 비교</a>
<a class="button button-ghost" href="{TEL}">전화로 주문 문의</a></div>
{regional}
</div>
<figure class="hero-picture"><img src="{E(src)}" alt="{E(first['name'])} 판매처 상품 사진"
width="500" height="500" loading="eager" decoding="async" fetchpriority="high">
<figcaption>{E(first['name'])} · {('꽃 부분 확대' if site=='clinicpresent' else '상품 사진')}</figcaption></figure>
</div></section>
<div class="proof-strip"><div class="wrap"><span>✓ 실판매 상품 직접 비교</span><span>✓ 상품별 사진·가격 표시</span>
<span>✓ 상품 상세 주문 및 전화상담</span></div></div>
<section class="section" id="products"><div class="wrap">
<div class="section-heading"><span class="eyebrow">CHOOSE THE RIGHT ITEM</span>
<h2>{E(short)} {E(meta['name'])} — 실제 상품 2종</h2>
<p>{E(important)}</p></div>
<div class="product-grid">{cards}</div>
<p class="price-note">판매처 확인 상품가격입니다. 지역별 추가 배송비는 받으실 주소에 따라 주문 단계에서 안내됩니다.</p>
<p class="price-note">주문 일정 변경이나 취소를 원하시면 꽃이랑 1844-0644로 연락해 주세요. 상품 제작·출고 상황에 따른 처리 방법과 교환·반품 조건을 안내해 드립니다.</p>
</div></section>
<section class="section alt" id="compare"><div class="wrap">
<div class="section-heading"><span class="eyebrow">DECISION POINTS</span>
<h2>무엇을 기준으로 고를까요?</h2>
<p>두 상품은 서로 다른 선택지입니다. 용도에 맞는 판단 기준을 먼저 확인하세요.</p></div>
<div class="difference-grid">{differences}</div>
</div></section>
<section class="section" id="ordering"><div class="wrap">
<div class="section-heading"><span class="eyebrow">BEFORE YOU ORDER</span>
<h2>주문 전에 확인할 세 가지</h2><p>행사 날짜와 받는 주소를 알려주시면 편리하게 주문하실 수 있습니다.</p></div>
<div class="steps">{advantages}</div>
<div class="example"><strong>전화 상담 때 이렇게 말씀해 주세요</strong>{E(meta["script"])}</div>
</div></section>
<section class="section alt faq" id="faq"><div class="wrap">
<div class="section-heading"><span class="eyebrow">FAQ</span><h2>자주 묻는 질문</h2></div>{faqs}
</div></section>
<section class="bottom-cta"><div class="wrap"><h2>상품이 정해졌다면 주문 상담</h2>
<p>{E(BODY_RULE)}</p><a class="button" href="{TEL}">☎ 1844-0644 전화 주문</a></div></section>
</main><footer class="footer"><div class="wrap"><span>꽃이랑 · 의료기관 축하꽃배달</span>
<span>주문 연결: {PHONE} · 판매처 상품 상세에서 최종 조건 확인</span></div></footer>
<div class="mobile-order"><a href="{TEL}">☎ {PHONE} 전화 주문</a></div></body></html>"""
    assert html.count('class="product-card"')==2 and html.count('class="hero-picture"')==1
    assert html.count('name="robots" content="noindex,nofollow,noarchive"')==1
    assert "application/ld+json" not in html
    return html

def main():
    ledger=json.loads((OUT/"retail-products-20261105.json").read_text(encoding="utf-8"))
    items={p["sku"]:p for p in ledger["items"]}
    assert len(items)==4
    for sku,p in items.items():
        assert urlsplit(p["imageUrl"]).hostname=="fwith.co.kr"
        assert p["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id="+sku
        assert p["priceKRW"]>0 and p["imageUrl"].endswith("/"+sku+"/thumb-1_500x500.jpg")
    (OUT/"style.css").write_text(CSS,encoding="utf-8")
    rendered=[]
    for site in CONFIG:
        for kind in ("ansan","bono"):
            name=site+(".html" if kind=="ansan" else "-r-00624.html")
            content=render_page(site,kind,items)
            (OUT/name).write_text(content,encoding="utf-8")
            rendered.append({"site":site,"page":kind,"name":name,
                             "sha256":hashlib.sha256(content.encode()).hexdigest()})
    assert len(rendered)==6
    (OUT/"pilot-manifest.json").write_text(json.dumps({
        "status":"noindex-sample-not-public","samplePages":rendered,
        "regionalSourceRow":624,"currentOrderFactRun":41875442755,
        "only3Hosts":sorted(CONFIG),"noNationwideDeployment":True,
        "noJSONLD":True},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CLINIC_PRODUCT_PILOT_6_GENERATED "+json.dumps({"count":len(rendered),"pages":rendered},ensure_ascii=False))

if __name__=="__main__":
    main()
