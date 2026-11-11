"""Clinic sites national static builder, evidence-first and no claim of SEO ranking.

One existing domain Worker, three exact hosts. 5034 V5 original name rows are mandatory.
All 3,600 extra pool blocks are deterministic recombinations of a curated concept catalog;
they are NOT represented as 3,600 independently-researched local facts.
"""
from __future__ import annotations
import argparse, collections, hashlib, html, json, random, re, shutil, sys
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from rss_feed import create_rss

SITE_META={
 'clinicflower': {
   'host':'clinicflower.nalmada.net','title':'병원·치과·한의원 개업화분·개원축하화분',
   'short':'개업·개원 축하화분','noun':'관엽식물과 화분',
   'intro':'진료공간에 오래 둘 선물이라면 식물의 크기, 채광과 관리 여건을 먼저 확인해야 합니다.',
   'sectors':[
      ('병원 대기실 화분','접수대와 환자 통로를 막지 않을 배치 위치부터 확인합니다.'),
      ('치과 개원화분','접수·진료 구역이 분리된 공간을 고려하여 높이와 화분 폭을 상담합니다.'),
      ('한의원 축하화분','입구나 로비의 채광, 관리 담당자와 용기 분위기를 살펴봅니다.')],
   'facts':[
     ('식물 크기','접수대 옆에 둘지 바닥에 세워 둘지 먼저 정합니다','화분 높이와 폭이 출입 동선에 맞는지 확인합니다','식물 크기를 기준 없이 큰 것으로 선택하지 않습니다'),
     ('빛과 관리','로비의 창가와 내부 대기 공간은 채광이 다를 수 있습니다','수령처에서 물주기와 식물 관리를 맡을 분을 확인합니다','어두운 진료실에서도 모든 식물이 오래 자란다고 단정하지 않습니다'),
     ('기념 선물 목적','오래 기르는 개원 기념품과 행사장 장식은 목적이 다릅니다','상대방의 취향과 관리 가능성을 우선 상담합니다','축하화환과 개원축하화분을 같은 상품으로 취급하지 않습니다'),
     ('받는 사람 이름','병원 이름과 원장 성함은 리본 제작에 쓰이는 중요한 정보입니다','리본을 쓰기 전에 상호의 띄어쓰기와 발신자 표기를 확인합니다','전문과목이나 대표자를 임의로 추측해 적지 않습니다'),
     ('배송 가능 범위','주소가 같은 시군구라도 품목과 날짜에 따라 수령 조건이 다릅니다','상세주소와 희망 전달일을 전화로 먼저 확인합니다','특정 동 전역의 당일배송을 무조건 보장하지 않습니다'),
     ('설치 위치','화분이 놓일 곳은 접수 업무와 방문객 통행에 영향을 줄 수 있습니다','담당자가 안내한 위치에 인계할 수 있는지 상담합니다','의료 장비나 환자 이동 공간을 가려도 괜찮다고 가정하지 않습니다'),
     ('예산 정하기','구성품과 화기 크기, 운송 조건은 선택 금액에 영향을 줄 수 있습니다','희망하는 전체 예산을 알려주고 선택 가능한 상품을 문의합니다','확인되지 않은 고정 가격이나 배송비를 표시하지 않습니다'),
     ('이전 개원','처음 문을 여는 의료기관과 장소를 이전하는 의료기관은 축하 문구가 다를 수 있습니다','신규 개원 또는 이전 축하 중 실제 상황을 확인합니다','이전 개원을 모두 신규 개업으로 표시하지 않습니다'),
     ('직원 수령','진료 중에는 담당자가 물품을 바로 받을 수 없는 경우가 있습니다','전화 연락이 가능한 수령자와 인계 위치를 정리합니다','부재 중인 문 앞에 화분을 임의로 두도록 안내하지 않습니다'),
     ('리본 문구','축 개원과 축 개업은 상황에 따라 선택하는 짧은 축하 표현입니다','축하 문구와 보내는 사람 이름을 따로 적어 상담합니다','주문자가 요청하지 않은 기관 이름이나 직책을 덧붙이지 않습니다'),
     ('물주기','식물 종류에 따라 햇빛과 물주기 관리가 달라집니다','상품이 결정되면 해당 품종의 관리 조건을 확인합니다','모든 관엽식물에 공통 물주기 주기를 약속하지 않습니다'),
     ('사전 연락','진료 전후의 안내 인력이 달라질 수 있습니다','받으실 시간과 건물 출입 시간대를 알려주세요','영업시간 표기만으로 배송 가능 시간을 확정하지 않습니다')],
   'faqs':[
      ('개업화분과 개원축하화분은 다른가요?','의료기관의 새 출발을 축하하는 용도로 같은 종류의 화분을 고를 수 있지만, 축하 목적과 문구는 구분해 확인하세요.'),
      ('병원 원장실에 화분을 직접 보낼 수 있나요?','직접 인계가 가능한지, 접수대에서 받아 줄 담당자가 있는지 수령처에 확인하는 것이 우선입니다.'),
      ('꽃이랑 전화로 식물 종류를 상담할 수 있나요?','원하는 크기·예산·배치 환경을 알려주시면 선택 가능한 상품의 범위를 문의할 수 있습니다.'),
      ('모든 동으로 오늘 배송되나요?','아닙니다. 실제 주소와 주문 시각에 따른 가능 여부를 주문 전에 개별 확인해야 합니다.'),
      ('화분 리본에 의료기관 상호를 넣어도 되나요?','정확한 공식 상호와 표기 방법을 확인한 뒤 요청하세요.'),
      ('배송을 받은 사진을 제공하나요?','주문 당시 판매처가 제공 가능한 배송 확인 방법을 직접 문의해야 합니다.')]
 },
 'clinicopen': {
   'host':'clinicopen.nalmada.net','title':'병원·치과·한의원 개원식 축하화분 주문',
   'short':'개원식 화분 주문','noun':'개원식 축하화분',
   'intro':'개원식 당일 선물은 행사 시작 시간뿐 아니라 현장 반입과 수령 담당자 확인이 중요합니다.',
   'sectors':[
      ('병원 개원식 수령','로비나 행사 장소로 반입 가능한 시간과 수령 창구를 확인합니다.'),
      ('치과 개원식 준비','직원 출근 시간과 접수 혼잡을 고려해 인계 가능한 시점을 문의합니다.'),
      ('한의원 개원행사 화분','행사 공간 정리 상태와 설치 위치를 먼저 조율합니다.')],
   'facts':[
     ('행사 날짜','진료 시작일과 개원 축하 행사는 서로 다른 날로 잡힐 수 있습니다','선물을 받을 정확한 행사일과 원하는 도착시간을 확인합니다','달력상 개원일만 보고 배송일을 정하지 않습니다'),
     ('준비 완료','개원 전날까지 시설 정리나 청소가 진행될 수 있습니다','수령 가능 구역과 설치 가능 시간을 담당자에게 문의합니다','준비되지 않은 공간에 선물을 무조건 반입한다고 약속하지 않습니다'),
     ('건물 출입','건물의 방문자 출입 시간과 배송 동선이 다를 수 있습니다','주 출입구와 층수, 엘리베이터 유무를 확인합니다','지도 표기만으로 기사 접근 가능성을 판단하지 않습니다'),
     ('수령 담당자','원장과 직원이 모두 행사 준비로 바쁠 수 있습니다','기사 연락을 받을 담당자 한 명을 정해 알려줍니다','행사 시작 전에는 모두 전화가 가능하다고 가정하지 않습니다'),
     ('리본 제작','행사 축하 문구에 기관명과 발신자 정보가 함께 들어갑니다','상호·발신자·문구를 문자로 최종 확인합니다','띄어쓰기와 직함을 판매처가 임의로 고치도록 하지 않습니다'),
     ('개원식 종류','정식 개원식이 없이 진료부터 시작하는 경우도 있습니다','공개 행사가 있는지 먼저 확인하고 상품 크기를 선택합니다','모든 의원에서 별도 행사를 연다고 안내하지 않습니다'),
     ('행사 현장 인계','현장 설치 요청과 접수대 물품 인계는 다른 서비스일 수 있습니다','원하는 인계 방식을 전화 주문 때 분명히 전달합니다','현장 설치 인력이 반드시 포함된다고 약속하지 않습니다'),
     ('바쁜 시간','진료와 개원식이 겹치면 안내 직원이 부족할 수 있습니다','환자 응대가 덜 바쁜 시간대가 있는지 수령처에 묻습니다','일정이 촉박해도 정확한 배송 시각을 임의로 확정하지 않습니다'),
     ('행사 장소','같은 건물에 행사장과 진료 공간이 따로 있을 수 있습니다','로비·대기실·외부 행사 공간 중 정확한 수령 위치를 확인합니다','건물 주소만으로 꽃을 놓을 장소를 정하지 않습니다'),
     ('주문 변경','행사 일정이 변경되면 축하화분 주문에도 영향을 줄 수 있습니다','제작 전 변경 가능 시점과 연락 방법을 확인합니다','출고된 상품의 변경이나 취소 가능성을 보장하지 않습니다'),
     ('메시지 취향','대표 원장 개인에게 보내는 선물과 의료기관 전체에 보내는 선물은 표현이 다를 수 있습니다','수신자를 개인명으로 할지 기관명으로 할지 결정합니다','상대방의 직함을 확인 없이 추가하지 않습니다'),
     ('행사 이후','개원식이 지난 뒤에도 방문 축하 선물을 고민할 수 있습니다','늦은 축하라면 일상적으로 두기 좋은 크기를 우선 고려합니다','행사가 끝났으므로 무조건 축하 선물을 받을 수 없다고 판단하지 않습니다')],
   'faqs':[
      ('행사 시작 전에 꼭 도착하나요?','도착 가능 여부와 예상 시간은 주소·품목·접수 시점에 따라 달라져 전화 확인이 필요합니다.'),
      ('개원식 당일 현장 설치가 가능한가요?','현장 반입·설치가 허용되는지와 해당 상품의 제공 범위를 상담으로 확인하세요.'),
      ('원장님이 부재 중이어도 받을 수 있나요?','수령을 대신할 담당자와 장소가 정해져 있다면 인계 방법을 사전에 협의할 수 있습니다.'),
      ('개원식 날짜가 바뀌면 수정할 수 있나요?','제작 및 출고 진행 상태에 따라 달라집니다. 변경 가능 여부를 주문처에서 확인해야 합니다.'),
      ('개원식이 없는 치과에도 선물할 수 있나요?','네, 새 출발을 축하하는 화분을 고려할 수 있으나 실제 수령 가능한 날짜와 장소부터 정하세요.'),
      ('한의원 이전개원은 어떤 리본 문구가 좋은가요?','이전 상황이 정확하면 축 이전 또는 새로운 출발을 축하하는 문구를 검토할 수 있습니다.')]
 },
 'clinicpresent': {
   'host':'clinicpresent.nalmada.net','title':'병원·치과·한의원 개업 축하화환 추천',
   'short':'개업 축하화환 추천','noun':'개업 축하화환',
   'intro':'개업 축하화환은 행사 현장의 설치 공간, 리본 문구와 반입 시각을 먼저 확인하고 선택합니다.',
   'sectors':[
      ('병원 개업 축하화환','로비 또는 행사장에 화환을 놓을 수 있는지 행사 담당자에게 확인합니다.'),
      ('치과 개업 축하화환','치과 접수 공간과 출입구가 좁다면 설치할 다른 공간을 협의합니다.'),
      ('한의원 개업 축하화환','실제 개원 행사 시간과 화환을 전시할 위치를 정한 후 주문을 상담합니다.')],
   'facts':[
     ('화환 규격','축하화환의 전체 높이와 폭은 상품 구성에 따라 다를 수 있습니다','실제 설치 장소에 맞는 규격을 전화로 문의합니다','모든 개원식 장소에 같은 크기의 화환을 권하지 않습니다'),
     ('꽃 구성','축하화환의 꽃 종류와 색감은 계절과 제작 상황에 영향을 받을 수 있습니다','선호하는 색상과 분위기를 주문 단계에서 전달합니다','사진과 동일한 꽃이 항상 준비된다고 단정하지 않습니다'),
     ('리본 문구','축 개원은 의료기관 축하화환에 사용할 수 있는 짧은 표현입니다','수신 기관명과 발신자의 정확한 표기를 함께 확인합니다','실제 상호를 모르는데 비슷한 이름으로 보내지 않습니다'),
     ('현장 반입','건물이나 행사장에는 화환 설치를 제한하는 규정이 있을 수 있습니다','수령 담당자에게 화환 반입과 설치 가능 여부를 문의합니다','로비에 언제나 화환을 세워 둘 수 있다고 안내하지 않습니다'),
     ('발신자 표시','사업체 명의와 개인 명의는 리본 표기가 다를 수 있습니다','회사명·직함·개인 이름 중 원하는 발신자 표기를 확정합니다','직함을 추측하거나 한 회사에서 보냈다고 가정하지 않습니다'),
     ('행사 시간','개원식의 시작 시각과 화환을 받을 수 있는 시각은 다를 수 있습니다','행사 준비 담당자에게 희망 반입시간을 확인합니다','행사 직전 주문의 특정 시간 도착을 보장하지 않습니다'),
     ('병원명 표기','의료기관의 정식 명칭에는 병원·의원 등의 차이가 있습니다','간판이나 초대장의 상호를 기준으로 리본 글자를 검토합니다','의원과 병원을 임의로 바꿔 쓰지 않습니다'),
     ('화환 놓을 곳','행사장에서 지정한 자리가 화환을 놓기에 편리합니다','행사 주최자가 지정한 설치 위치를 확인합니다','통행을 막는 곳에 세워도 된다고 안내하지 않습니다'),
     ('행사 후 회수','축하화환을 행사 뒤 어떻게 정리할지도 중요한 조건일 수 있습니다','철수·회수 서비스 제공 범위를 판매처에 문의합니다','모든 주문에 회수가 포함된다고 주장하지 않습니다'),
     ('배송비 문의','화환 크기와 실제 운송 구간에 따라 추가비용 여부가 달라질 수 있습니다','정확한 주소를 제공하고 최종 비용을 확인합니다','도시 이름만으로 무료배송이라고 단정하지 않습니다'),
     ('이전 축하','의료기관을 옮기는 행사는 신규 개원식과 상황이 다릅니다','이전 개원인지 처음 개원인지 확인한 뒤 문구를 고릅니다','이전 축하에 신규 개업 문구만 제시하지 않습니다'),
     ('화분과 구분','화환은 행사 축하용 꽃 장식이며 화분은 식물이 심어진 선물입니다','수령처가 원하는 상품 종류부터 분명히 정합니다','화분 사진을 축하화환 상품 사진이라고 소개하지 않습니다')],
   'faqs':[
      ('축하화환과 개원축하화분은 다른가요?','네, 화환은 행사 축하용 꽃 장식이고 화분은 식물이 심어진 선물입니다. 주문 목적에 맞춰 구분하세요.'),
      ('병원 로비에 축하화환을 세울 수 있나요?','병원 건물·행사장의 설치 규정은 다르므로 수령처에 확인이 필요합니다.'),
      ('축하화환의 리본은 어떻게 작성하나요?','축하 문구와 의료기관 공식 상호, 발신자 성명·소속을 확인한 뒤 요청합니다.'),
      ('개원식 당일 축하화환을 보낼 수 있나요?','주소와 주문 시각, 상품 제작 가능 여부를 상담에서 확인해야 합니다.'),
      ('화환 사진과 동일하게 제작되나요?','실제 꽃 구성은 계절과 공급에 따라 달라질 수 있어 상담 전 동일 구성을 보장할 수 없습니다.'),
      ('치과·한의원에도 축하화환이 적합한가요?','행사 공간에 설치할 수 있다면 고려할 수 있습니다. 실제 수령처의 선호와 반입 조건을 우선합니다.')]
 }
}

WREATH_EXTRA_FACTS = [
 ('개원식 초대장','초대장의 장소 표기와 실제 수령 장소가 다를 수 있습니다','행사 안내에 적힌 장소와 담당자 연락처를 비교합니다','초대장 주소만 보고 반입 장소까지 확정하지 않습니다'),
 ('현장 포토존','개원식 사진을 찍는 공간에는 화환을 세울 위치를 따로 정할 수 있습니다','사진 촬영 배경과 이동 통로를 함께 고려해 배치 위치를 문의합니다','포토존에 화환을 임의로 설치하도록 요청하지 않습니다'),
 ('화환 수량','축하화환이 여러 개 도착하면 설치 공간이 부족할 수 있습니다','주최 측이 지정한 반입 위치와 수량 제한을 확인합니다','화환이 많을수록 행사가 좋다는 식으로 권하지 않습니다'),
 ('건물 관리실','건물 관리실에서 외부 화환 반입 방법을 안내하는 경우가 있습니다','관리실과 수령 담당자의 안내가 일치하는지 확인합니다','관리실의 허가 없이 공용 출입구에 세우지 않습니다'),
 ('엘리베이터 운반','상층부 행사장은 화환 규격이 운반 동선에 영향을 줄 수 있습니다','승강기 크기와 화물 반입 경로를 주문 상담에서 확인합니다','상층부라면 어떤 화환도 설치할 수 있다고 단정하지 않습니다'),
 ('주차장 출입','배송 차량의 건물 출입 방법이 현장마다 다를 수 있습니다','행사장에 안내된 차량 반입 위치를 함께 전달합니다','지상 도로의 주차나 통행을 막는 것을 권하지 않습니다'),
 ('주요 출입구','병원·치과 건물에는 층별 출입구와 비상구가 따로 있을 수 있습니다','화환 설치가 승인된 출입구를 확인합니다','비상 출입구 주변을 장식 공간으로 안내하지 않습니다'),
 ('공동 발신','축하화환을 여러 구성원이 함께 보내는 경우 발신 표기가 길어집니다','단체명과 대표자 표기의 우선순위를 협의합니다','발신자 전원의 이름이 한 리본에 들어간다고 약속하지 않습니다'),
 ('직함 확인','보내는 분이나 받는 분의 직함은 정확한 표기가 필요합니다','리본에 필요한 직함만 주문자가 확인해 전달합니다','임의로 이사장·원장 등의 직함을 붙이지 않습니다'),
 ('정식 상호','의료기관 등록 상호와 일반적으로 부르는 이름이 다를 수 있습니다','리본에 쓸 정확한 상호를 수령처와 대조합니다','약칭을 무조건 공식 명칭으로 바꾸지 않습니다'),
 ('영문 리본','리본에 영문 병원명이나 발신자명을 쓰려는 주문도 있습니다','대소문자와 표기 순서를 주문자가 지정하도록 안내합니다','영문 표기를 번역기로 임의 작성해 확정하지 않습니다'),
 ('짧은 문구','화환 리본에는 간결한 문구가 읽기 편할 수 있습니다','행사 목적이 드러나는 짧은 축하 문구를 우선 검토합니다','리본 면적을 확인하지 않고 긴 문장 전체를 인쇄한다고 하지 않습니다'),
 ('화환 종류','일반 축하화환과 행사장 장식용 꽃은 목적과 구성이 다릅니다','문의하는 상품이 화환인지 행사 꽃장식인지 먼저 구분합니다','상품명을 같게 취급해 임의 견적을 안내하지 않습니다'),
 ('오픈식 시간','개원식과 진료 시작 시간이 같은 날일 수도 다른 날일 수도 있습니다','행사 전 인계가 필요한지 날짜와 시각을 함께 확인합니다','시간이 정해졌다는 이유로 자동 배송을 약속하지 않습니다'),
 ('기념식 사회자','행사 진행자가 배치 위치를 지정할 수 있습니다','행사 주최 측의 화환 설치 안내를 전달받습니다','행사 사진에 반드시 노출된다고 보장하지 않습니다'),
 ('시설 청소','행사 당일 오전에도 출입구 정리가 진행될 수 있습니다','정리가 끝난 설치 구역을 인계받을 수 있는지 확인합니다','청소 중인 구역에 화환을 미리 두도록 권하지 않습니다'),
 ('배송 당일 연락','수령자 연락처가 바뀌면 화환 인계가 지연될 수 있습니다','주문 확정 전에 수령 담당자 정보를 다시 점검합니다','연락처를 추측해 임의로 작성하지 않습니다'),
 ('꽃 색상 취향','축하 행사에 선호하는 색상과 분위기가 있을 수 있습니다','원하는 색감이 있는지 주문 시 미리 알려줍니다','해당 색상의 생화가 항상 준비된다고 말하지 않습니다'),
 ('꽃 수급','제작일의 생화 공급 여건에 따라 화환의 색감 구성이 달라질 수 있습니다','상담에서 확정 가능한 구성과 대체 선택지를 확인합니다','원본 사진의 모든 꽃이 언제나 동일하다고 말하지 않습니다'),
 ('행사 이후 처리','행사가 끝난 뒤 화환을 어떻게 정리하는지 확인이 필요할 수 있습니다','철수 방법이나 회수 범위를 주문처에 먼저 문의합니다','회수와 재활용을 모든 상품에 포함된 서비스로 표시하지 않습니다'),
 ('발신 지역','보내는 사람이 다른 지역에 있어도 수령처 정보 확인이 중요합니다','수령 장소와 담당자 연락처를 기준으로 주문 조건을 점검합니다','발신자의 거주지역으로 배송 가능 여부를 추정하지 않습니다'),
 ('이전개원 축하','기존 의료기관이 다른 주소로 이전하는 경우 선물 목적이 다릅니다','이전인지 신규 개원인지 리본 주문 때 확인합니다','이전을 신규 개원으로 잘못 표시하지 않습니다'),
 ('건물 내 표지판','행사 주최자가 화환을 두는 구역에 표지판을 설치할 수 있습니다','현장에 공식 안내가 있는지 수령처에 문의합니다','임의로 화환을 출입문 앞에 진열하지 않습니다'),
 ('당일 준비','긴급 주문은 화환 제작과 운송 가능 여부가 먼저 확인되어야 합니다','희망 시각과 실제 주문 시각을 함께 판매처에 전달합니다','전국 어느 지역이든 당일 설치된다고 약속하지 않습니다'),
 ('도서 지역','도서·외곽 지역은 배송 가능 품목과 시간대가 다를 수 있습니다','정확한 배송 주소를 안내하고 조건을 별도 확인합니다','광역단체가 같다고 배송비가 동일하다고 말하지 않습니다'),
 ('예산 분담','여러 분이 공동으로 보내면 전체 예산과 발신자 표기를 정해야 합니다','주문 전에 결제 담당자와 리본 표기를 함께 결정합니다','누가 비용을 부담하는지 임의로 추정하지 않습니다'),
 ('단체 리본','모임이나 협회 명의로 보내는 축하화환은 단체명 확인이 중요합니다','공식 단체 표기와 축하 문구를 주문자에게 재확인합니다','실제 단체 이름을 확인하지 않고 약칭을 고치지 않습니다'),
 ('상호 띄어쓰기','치과의원과 병원 명칭에는 띄어쓰기 차이가 있을 수 있습니다','공식 명함·안내문에 있는 글자를 기준으로 확인합니다','판매자가 임의로 의료기관 명칭을 바꾸지 않습니다'),
 ('고층 건물','엘리베이터로 운송해야 하는 설치 장소가 있을 수 있습니다','화환 규격과 반입 가능 동선을 사전에 문의합니다','모든 고층 건물에서 같은 화환을 설치한다고 단정하지 않습니다'),
 ('출입 통제','행사장 보안 담당자의 안내가 필요한 경우가 있습니다','주최 측이 지정한 반입 절차를 확인합니다','출입 허가가 없는 곳에 전달을 시도하도록 안내하지 않습니다'),
 ('소규모 행사','작은 공간에서 열리는 개원식에는 큰 화환이 어울리지 않을 수 있습니다','설치 면적과 실제 행사 규모를 먼저 고려합니다','큰 규격의 화환이 항상 더 적절하다고 말하지 않습니다'),
 ('현장 운영시간','건물은 개방 중이어도 행사 담당자가 부재할 수 있습니다','담당 직원의 근무 시간과 전화 가능 여부를 함께 확인합니다','건물 문이 열려 있다는 이유로 인계 완료를 보장하지 않습니다'),
 ('배너 위치','안내 배너나 입구 표지판과 화환이 겹칠 수 있습니다','행사 안내물과 화환을 함께 배치할 수 있는지 묻습니다','안전한 통행 공간을 줄이는 배치를 권하지 않습니다'),
 ('주문 확인','동명이 의료기관은 서로 다른 주소에 위치할 수 있습니다','의료기관명과 도로명주소를 동시에 대조합니다','검색 결과 첫 항목만 보고 수령처를 확정하지 않습니다'),
 ('배송 요청메모','발신자 요청 사항이 많으면 핵심 정보가 누락될 수 있습니다','일시·주소·담당자·리본 문구를 우선순위별로 정리합니다','확인되지 않은 추가 서비스를 요청 메모에 확정 기입하지 않습니다'),
 ('반입 시간 제한','행사장에 지정된 화환 반입 시간대가 있을 수 있습니다','해당 시간대와 주문 가능 일정을 판매처와 협의합니다','사전 확인 없이 새벽·심야 도착을 약속하지 않습니다'),
 ('행사 담당 변경','개원식 현장 담당자가 행사 직전에 바뀔 수 있습니다','발신자와 수신 측 연락 담당자를 다시 확인합니다','예전 담당자 번호만으로 인계가 가능하다고 판단하지 않습니다'),
 ('현장 설치 요청','화환 운송과 설치가 하나의 상품 구성에 포함되는지 다를 수 있습니다','기본 서비스 범위를 주문 전에 확인합니다','별도 작업을 무조건 무료 제공한다고 약속하지 않습니다'),
 ('축하 표현','개원을 축하하는 문구는 개인의 관계와 행사 성격에 따라 달라집니다','짧고 격식 있는 표현이 좋은지 먼저 묻습니다','받는 분과의 관계를 임의로 추정한 문구를 쓰지 않습니다'),
 ('후속 확인','발송 뒤 수령 여부를 확인하고 싶은 주문자가 있을 수 있습니다','판매처의 안내 가능한 확인 방법을 주문 시 문의합니다','사진 확인 또는 실시간 추적이 모든 주문에 제공된다고 단정하지 않습니다'),
]
SITE_META['clinicpresent']['facts'].extend(WREATH_EXTRA_FACTS)

# We do not confuse a generated variant with new source evidence.
# Visitor-first copy composition. The fourth item in historic SITE_META facts
# contains legacy defensive wording and is intentionally NEVER used in the pool.
# This pilot review branch retains it only to compare source changes; deployment
# remains blocked until national semantic QA is independently approved.
PERSPECTIVES=[
 ('보내는 분','보내는 분의 예산과 축하 목적을 알려주시면 고르기 편합니다.'),
 ('받는 분','받는 분의 취향과 놓을 공간을 함께 고려해 보세요.'),
 ('개원식 담당자','개원식 날짜와 수령할 담당자를 함께 알려주시면 편리합니다.'),
 ('전화 주문','상품코드와 받는 주소를 알려주시면 주문을 도와드립니다.'),
 ('배송 인계','배송 연락을 받을 분과 시간대를 함께 정해 보세요.'),
 ('선물 취향','받는 분의 선물 취향과 행사 성격을 함께 고려해 보세요.'),
 ('상품 비교','상품 사진·가격·크기를 함께 비교하면 선택하기 좋습니다.'),
 ('일정 확인','희망 날짜와 받는 주소를 알려주시면 배송 가능한 일정을 안내받으실 수 있습니다.')
]
FRAMES=[
 ('상품 고르기','{context} {action} {view}'),
 ('공간 선택','{action} {context} {choice}'),
 ('수령 준비','{view} {context} {action}'),
 ('날짜와 장소','{context} {choice} {view}'),
 ('주문 비교','{action} {choice} {context}'),
 ('문의 내용','{view} {action} {choice}'),
 ('선물 목적','{choice} {context} {action}'),
 ('필요 정보','{context} {view} {choice}'),
 ('상품 판단','{choice} {action} {view}'),
 ('전달 계획','{view} {choice} {context}')
]

def _visitor_action(s):
    return (s.replace('확인합니다','확인해 보세요')
             .replace('정합니다','정해 보세요')
             .replace('결정합니다','정해 보세요')
             .replace('문의합니다','문의해 보세요')
             .replace('전달합니다','알려주세요')
             .replace('고릅니다','골라보세요')
             .replace('비교합니다','비교해 보세요')
             .replace('알립니다','알려주세요'))

# Avoid mixing wreath-specific purchase advice with potted-plant guidance.
SITE_PURCHASE_VIEWS = {
    'clinicflower': '진료공간에 놓을 화분의 크기·채광·관리 여건을 비교해 보세요.',
    'clinicopen': '행사일과 수령 담당자, 화분을 놓을 위치를 함께 알려주세요.',
    'clinicpresent': '축하화환의 규격·꽃 구성과 행사장 반입 조건을 비교해 보세요.',
}

def generate_extra_pool() -> dict:
    output={'type':'visitor-first-composed-practical-guidance',
      'sourceType':'V5 authored concepts, site-specific purchase questions, no verified local delivery facts',
      'claim':'Ten contextual frames per concept and customer perspective; not independently researched local facts',
      'items':{},'count':0}
    choices={
      'clinicflower':'금전수·녹보수의 사진과 가격을 비교해 놓을 자리에 어울리는 화분을 골라보세요.',
      'clinicopen':'행사 날짜와 수령 담당자를 알려주시면 개원식 선물 주문을 도와드립니다.',
      'clinicpresent':'축하 3단·4단 화환의 꽃 구성과 가격을 비교해 행사 장소에 어울리는 상품을 골라보세요.'
    }
    defensive=('않습니다','못합니다','단정하지','약속하지','보장하지','임의로',
               '가정하지','무조건','확인되지 않은','달력상 개원일만',
               '현장 설치 인력이 반드시 포함','AI 연출','배송 실적 사진')
    output['duplicatesSkippedPerSite']={}
    for site,meta in SITE_META.items():
        rows=[]
        seen_bodies=set()
        skipped=0
        for n,(topic,context,action,_legacyAvoid) in enumerate(meta['facts']):
            for p,(role,view) in enumerate(PERSPECTIVES):
                for f,(kind,template) in enumerate(FRAMES):
                    site_view = SITE_PURCHASE_VIEWS[site] if role in ('선물 취향', '상품 비교') else view
                    body=template.format(context=context,action=_visitor_action(action),
                                         view=site_view,choice=choices[site])
                    body=' '.join(body.split())
                    if any(x in body for x in defensive):
                        raise ValueError('Defensive text detected in new pool: '+site+' '+topic)
                    if body in seen_bodies:
                        skipped+=1
                        continue  # duplicate sentence composition isn't new useful copy
                    seen_bodies.add(body)
                    rows.append({'id':f'{site.upper()}-{n:02d}-{p:02d}-{f:02d}',
                                 'topic':topic,'heading':f'{topic} — {kind}',
                                 'body':body,'role':role,'frame':kind,'sourceConceptNumber':n+1,
                                 'visitorToneVersion':'2026-11-05'})
        assert len(rows)+skipped==len(meta['facts'])*len(PERSPECTIVES)*len(FRAMES)
        assert len({x['body'] for x in rows})==len(rows)
        output['items'][site]=rows
        output['duplicatesSkippedPerSite'][site]=skipped
    output['count']=sum(len(x) for x in output['items'].values())
    assert output['count']>=3600
    return output


def esc(value):return html.escape(str(value),quote=True)
def sha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def key_sort(seed,x):return sha(seed+'|'+str(x))
def sl(province,district=None):return sha(province if district is None else province+'|'+district)[:12]
def parent_rec(r):return (r[0],r[1])
def region_path(n):return f'/r/{n:05d}.html'
def province_path(p):return '/p/'+sl(p)+'.html'
def district_path(p,d):return '/d/'+sl(p,d)+'.html'

def parse_regions(raw):
    assert isinstance(raw,dict) and isinstance(raw.get('records'),list)
    rows=raw['records'];declared=raw['counts']
    assert len(rows)==declared['localities']==5034
    assert declared['provinces']==17 and declared['districts']==250
    assert declared['parentMatchesV4']==3596 and declared['parentNotMatchedV4']==1438
    parsed=[]
    for i,r in enumerate(rows,1):
        assert isinstance(r,list) and len(r)==4 and all(isinstance(v,str) and v.strip() for v in r[:3])
        assert r[3] in (0,1)
        parsed.append((i,r[0],r[1],r[2],r[3]))
    assert len({(p,d,n) for _,p,d,n,_ in parsed})==5034
    assert sum(flag for *_,flag in parsed)==3596
    assert len({p for _,p,_,_,_ in parsed})==17
    assert len({(p,d) for _,p,d,_,_ in parsed})==250
    return parsed

def in_site(href):
    if href.startswith('tel:') or href.startswith('mailto:') or href.startswith('#'):return None
    return href.split('#',1)[0] or None if href.startswith('/') else False


# Editorial media: the first two sites reuse Clinicflower ImageGen WebPs already
# present in the shared Worker. The third uses an existing ImageGen wreath
# illustration from Todayflower, preserving its original Git blob and provenance.
# No image represents a delivered product or a verified local storefront.
SITE_IMAGES={
 'clinicflower':[
    ('hero.webp',1672,941,'밝은 병원 로비에 배치한 개원 축하화분 AI 연출'),
    ('hospital.webp',1448,1086,'병원 접수대와 축하화분을 표현한 AI 연출'),
    ('dental.webp',1448,1086,'치과 대기실 축하화분을 표현한 AI 연출'),
    ('oriental.webp',1448,1086,'한의원 실내 축하화분을 표현한 AI 연출')],
 'clinicopen':[
    ('hospital.webp',1448,1086,'의료기관 개원식 축하화분을 표현한 AI 연출'),
    ('oriental.webp',1448,1086,'한의원 개원식 분위기의 축하화분 AI 연출'),
    ('dental.webp',1448,1086,'치과 개원식 축하화분을 표현한 AI 연출')],
 'clinicpresent':[
    ('celebration-wreath.webp',1448,1086,'병원 개업 축하화환을 표현한 AI 연출')]
}

def media_info(site,path):
    images=SITE_IMAGES[site]
    idx=int(sha(site+'|'+path+'|editorial-media')[:12],16)%len(images)
    return images[idx]

def media_html(site,path):
    name,width,height,alt=media_info(site,path)
    return ('<section class="clinic-visual"><div class="wrap">'
            '<figure class="clinic-image">'
            '<img src="/assets/images/'+esc(name)+'" alt="'+esc(alt)+'" '
            'width="'+str(width)+'" height="'+str(height)+'" '
            'loading="eager" decoding="async" fetchpriority="high">'
    
            '</figure></div></section>')

def header(site, title, description, path, mode):
    host=SITE_META[site]['host']
    canonical=f'<link rel="canonical" href="https://{host}{path}">' if mode=='public' else ''
    if site == 'clinicpresent':
        # Content-specific media guard: a celebration wreath is not a potted plant.
        assert SITE_IMAGES[site][0][0]=='celebration-wreath.webp'
    name,width,height,image_alt=media_info(site,path)
    page_url='https://'+host+path
    image_url='https://'+host+'/assets/images/'+name
    og=(
       '<meta property="og:locale" content="ko_KR">'
       '<meta property="og:type" content="website">'
       '<meta property="og:title" content="'+esc(title+' | 꽃이랑')+'">'
       '<meta property="og:description" content="'+esc(description)+'">'
       '<meta property="og:url" content="'+esc(page_url)+'">'
       '<meta property="og:image" content="'+esc(image_url)+'">'
       '<meta property="og:image:alt" content="'+esc(image_alt)+'">'
       '<meta property="og:image:width" content="'+str(width)+'">'
       '<meta property="og:image:height" content="'+str(height)+'">'
       '<meta name="twitter:card" content="summary_large_image">'
       '<meta name="twitter:title" content="'+esc(title+' | 꽃이랑')+'">'
       '<meta name="twitter:description" content="'+esc(description)+'">'
       '<meta name="twitter:image" content="'+esc(image_url)+'">'
    )
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>'+esc(title)+' | 꽃이랑</title>'
        '<meta name="description" content="'+esc(description)+'">'
        '<meta name="robots" content="'+('index,follow' if mode=='public' else 'noindex,nofollow')+'">'
        +canonical+og+'<link rel="alternate" type="application/rss+xml" href="https://'+host+'/rss.xml" title="꽃이랑 안내 RSS">'
        '<link rel="stylesheet" href="/assets/style.css">'
        '</head><body><header class="top"><div class="wrap">'
        '<a class="brand" href="/">꽃이랑<small>'+esc(SITE_META[site]['short'])+'</small></a>'
        '<nav class="topnav"><a class="jump" href="/">전국 안내</a><a class="call" href="tel:1844-0644">☎ 전화주문</a></nav>'
        '</div></header>')

def foot(site):
    return ('<section class="bottom"><div class="wrap footCall"><h2>주문은 전화로 상담하세요</h2>'
        '<p>실제 상품 종류·꽃 구성·배송 가능 여부·최종 금액은 주문 상담에서 확인합니다.</p>'
        '<a class="call" href="tel:1844-0644">☎ 1844-0644</a></div></section></main>'
        '<footer class="footer"><div class="wrap"><span><strong>꽃이랑</strong> · '+esc(SITE_META[site]['short'])+'</span>'
        '<span>1844-0644 · 지역별 배송 가능 여부는 전화로 확인</span></div></footer>'
        '<div class="mobileCall"><a href="tel:1844-0644" aria-label="전화 주문">☎ 전화주문 1844-0644</a></div></body></html>')

def editorial_body(body):
    """Trim boilerplate filler without changing the source POOL or fabricating facts."""
    for filler in (
        "상황에 맞지 않는 선물보다 받는 곳의 실제 여건을 먼저 살펴보는 편이 좋습니다.",
        "화분 종류나 가격을 정하기 전에 이 항목을 정리하면 상담이 수월해집니다.",
        "실제 배송 가능 여부와 상품 구성은 주문 시 다시 확인해야 합니다.",
    ):
        body=body.replace(filler,"")
    return " ".join(body.split())


# A topic is a single factual/advice unit. Never render the same unit twice on
# one page, regardless of frame, perspective or generated paraphrase.
# Compositional POOL remains historical input but is not page-padding material.
REQUIRED_TOPICS = {
    'clinicflower': ('식물 크기', '빛과 관리', '기념 선물 목적', '리본 문구'),
    'clinicopen': ('행사 날짜', '수령 담당자', '행사 장소', '리본 제작'),
    'clinicpresent': ('화환 규격', '꽃 구성', '현장 반입', '리본 문구', '배송비 문의'),
}

# Concept ownership is stricter than topic IDs: different historical topic IDs
# can contain the same purchasing advice (e.g. flower composition vs color taste).
# One owner per semantic cluster is selected across body AND sidebar.
SEMANTIC_CLUSTERS = {
    'clinicflower': {
        '식물 크기':'placement', '설치 위치':'placement',
        '빛과 관리':'plant-care', '물주기':'plant-care',
        '받는 사람 이름':'ribbon', '리본 문구':'ribbon',
        '직원 수령':'handover', '사전 연락':'handover',
    },
    'clinicopen': {
        '행사 날짜':'schedule', '행사 이후':'schedule',
        '준비 완료':'venue-ready', '행사 장소':'venue-ready',
        '수령 담당자':'handover', '바쁜 시간':'handover',
        '리본 제작':'ribbon', '메시지 취향':'ribbon',
        '행사 현장 인계':'installation', '건물 출입':'installation',
    },
    'clinicpresent': {
        '꽃 구성':'flower-choice', '꽃 색상 취향':'flower-choice', '꽃 수급':'flower-choice',
        '화환 규격':'wreath-size', '엘리베이터 운반':'wreath-size', '고층 건물':'wreath-size',
        '리본 문구':'ribbon', '짧은 문구':'ribbon', '단체 리본':'ribbon',
        '공동 발신':'ribbon', '영문 리본':'ribbon', '축하 표현':'ribbon',
        '현장 반입':'venue-access', '건물 관리실':'venue-access', '출입 통제':'venue-access',
        '화환 놓을 곳':'placement', '현장 포토존':'placement', '배너 위치':'placement',
        '배송비 문의':'delivery-cost', '도서 지역':'delivery-cost',
        '행사 시간':'timing', '오픈식 시간':'timing', '반입 시간 제한':'timing',
        '행사 후 회수':'post-event', '행사 이후 처리':'post-event',
        '발신자 표시':'sender', '직함 확인':'sender', '정식 상호':'sender',
        '현장 설치 요청':'installation', '주요 출입구':'installation',
        '배송 당일 연락':'recipient-contact', '행사 담당 변경':'recipient-contact',
        '화환 수량':'space', '소규모 행사':'space',
        '차량 반입':'vehicle-access', '주차장 출입':'vehicle-access',
    },
}

def semantic_cluster(site, topic):
    return SEMANTIC_CLUSTERS[site].get(topic, 'fact:'+topic)

def decision_units(site, seed):
    facts = SITE_META[site]['facts']
    required = REQUIRED_TOPICS[site]
    topic_ids = {topic:i for i,(topic,_,_,_) in enumerate(facts)}
    assert len(topic_ids)==len(facts), (site, 'ambiguous factual IDs')
    must = [topic_ids[t] for t in required]
    remaining = sorted((i for i in range(len(facts)) if i not in must),
                       key=lambda i:key_sort(seed+'|fact-id',i))
    body_ids=[];side_ids=[];owners=set()
    content_limit = {'clinicflower':6, 'clinicopen':5, 'clinicpresent':9}[site]
    for idx in must+remaining:
        cluster=semantic_cluster(site,facts[idx][0])
        if cluster in owners:
            continue  # Don't manufacture extra paragraphs from the same advice.
        owners.add(cluster)
        if len(body_ids)<content_limit:
            body_ids.append(idx)
        elif len(side_ids)<2:
            side_ids.append(idx)
        else:
            break
    assert len(body_ids)==content_limit and len(side_ids)==2,(site,body_ids,side_ids)
    assert len({semantic_cluster(site,facts[idx][0]) for idx in body_ids+side_ids})==content_limit+2
    return body_ids, side_ids

def advice_sentences(site, ids):
    seen=set()
    for i in ids:
        topic,context,action,_ = SITE_META[site]['facts'][i]
        for sentence in (context, _visitor_action(action)):
            normalized=' '.join(sentence.split()).rstrip('.')
            if normalized in seen:
                raise ValueError('Repeated advice sentence: '+site+' '+topic+' '+normalized)
            seen.add(normalized)

def insight_cards(site, side_ids):
    facts=SITE_META[site]['facts']
    blocks=[]
    audit=[]
    for i in side_ids:
        topic,context,action,_legacyAvoid=facts[i]
        blocks.append('<article class="step"><span class="num">'+esc(topic)+'</span>'
                      '<h3>'+esc(context)+'</h3><p>'+esc(_visitor_action(action))+'</p></article>')
        audit.extend((context,action))
    return ('<section class="section clinic-decision"><div class="wrap">'
            '<div class="heading"><h2>주문 전에 비교할 추가 조건</h2>'
            '<p>해당되는 조건이 있다면 주문 상담에 함께 전달하세요.</p></div>'
            '<div class="steps">'+''.join(blocks)+'</div></div></section>'," ".join(audit))


def render_region(site,rec,pool,mode):
    i,p,d,n,flag=rec
    meta=SITE_META[site]
    place=' '.join((p,d,n))
    path=region_path(i)
    title=place+' '+meta['title']
    description=place+' '+meta['short']+' 주문 시 확인할 품목·일정·수령장소와 리본 문구 안내. 꽃이랑 전화 1844-0644.'
    seed=f'{site}|{i}|{place}'
    body_ids,side_ids=decision_units(site,seed)
    advice_sentences(site,body_ids+side_ids)
    facts=meta['facts']
    sections=[]
    narrative=[]
    for idx in body_ids:
        topic,context,action,_legacyAvoid=facts[idx]
        # The concept is used once. Heading, context and action offer two
        # distinct practical facts; no generic seller pitch is appended.
        message=_visitor_action(action)
        sections.append('<article class="step" data-fact-id="'+esc(site+'-'+str(idx))+'">'
                        '<h3>'+esc(topic)+'</h3><p>'+esc(context)+'</p><p>'+esc(message)+'</p></article>')
        narrative.extend((topic,context,message))
    faqs=meta['faqs']
    faq_start=int(sha(seed+'faq')[:8],16)%len(faqs)
    picked=faqs[faq_start:]+faqs[:faq_start]
    faq=''.join('<details><summary>'+esc(q)+'</summary><p>'+esc(a)+'</p></details>' for q,a in picked[:2])
    insights,insights_text=insight_cards(site,side_ids)
    breadcrumbs='<p class="crumb"><a href="/">전국</a> · <a href="'+province_path(p)+'">'+esc(p)+'</a> · <a href="'+district_path(p,d)+'">'+esc(d)+'</a> · '+esc(n)+'</p>'
    main=(' <main><section class="hero" style="min-height:390px;background-image:none;background-color:#f2f5ef"><div class="wrap heroContent">'
        '<span class="eyebrow">FLOWER WITH CARE · REGIONAL ORDER GUIDE</span>'+breadcrumbs+
        '<h1>'+esc(place)+'<br><strong>'+esc(meta['title'])+'</strong></h1>'
        '<p>'+esc(meta['intro'])+' '+esc(place)+'에 보내는 경우 정확한 수령 주소와 희망 날짜를 전화로 확인해주세요.</p>'
        '<a class="call heroCall" href="tel:1844-0644">☎ 전화주문 1844-0644</a></div></section>'
        +media_html(site,path)+'<section class="section alt"><div class="wrap"><div class="heading"><h2>'+esc(place)+' 주문 전 검토할 내용</h2>'
        '<p>받는 분의 상황에 맞는 상품 선택과 수령 조건을 정리했습니다.</p></div><div class="grid3">'+''.join(sections)+'</div></div></section>'
        '<section class="section"><div class="wrap"><div class="heading"><h2>자주 묻는 질문</h2></div><div class="faq">'+faq+'</div>'
        '<p>다른 지역명도 찾아보려면 <a href="'+district_path(p,d)+'">'+esc(p+' '+d)+' 지역 목록</a>을 이용하세요.</p>'
        '</div></section>'+insights)
    return (header(site,title,description,path,mode)+main+foot(site),
        title+' '+description+' '+meta['intro']+' '+' '.join(narrative)+' '+insights_text+' '+' '.join(q+' '+a for q,a in picked[:2]))

def render_dir(site,kind,place,rows,mode):
    meta=SITE_META[site]
    if kind=='home':
        path='/';title='전국 '+meta['title'];desc='전국 지역별 '+meta['short']+' 전화 주문 준비와 안내. '+meta['intro']
        tiles=[(province_path(p),p) for p in sorted({x[1] for x in rows})]
        pre='<p>전국 시·도 이름을 선택하면 이어서 시·군·구, 읍면동 목록으로 이동할 수 있습니다.</p>'
    elif kind=='province':
        p=place[0];path=province_path(p);title=p+' '+meta['title'];desc=p+' 지역별 '+meta['short']+' 주문 안내. '+meta['intro']
        tiles=[(district_path(p,d),d) for d in sorted({x[2] for x in rows if x[1]==p})]
        pre='<p><a href="/">전국 안내</a> · 시·군·구 목록</p>'
    else:
        p,d=place;path=district_path(p,d);title=p+' '+d+' '+meta['title'];desc=p+' '+d+' 읍면동별 '+meta['short']+' 주문 안내. '+meta['intro']
        tiles=[(region_path(i),n) for i,pp,dd,n,_ in rows if pp==p and dd==d]
        pre='<p><a href="/">전국 안내</a> · <a href="'+province_path(p)+'">'+esc(p)+'</a></p>'
    assert tiles and len({x[0] for x in tiles})==len(tiles)
    cards=''.join('<a class="service" href="'+url+'" style="display:block;text-decoration:none"><div class="content"><strong>'+esc(name)+'</strong><p style="margin:5px 0">지역별 주문 안내 보기</p></div></a>' for url,name in tiles)
    htmlbody='<main><section class="hero" style="min-height:300px;background-image:none;background:#f3f5ed"><div class="wrap heroContent">'+pre+'<h1>'+esc(title)+'</h1><p>'+esc(desc)+'</p><a class="call" href="tel:1844-0644">☎ 1844-0644</a></div></section>'
    htmlbody+=media_html(site,path)
    htmlbody+='<section class="section"><div class="wrap"><div class="heading"><h2>지역 선택</h2></div><div class="grid3">'+cards+'</div></div></section>'
    return header(site,title,desc,path,mode)+htmlbody+foot(site)

def generate(root:Path,output:Path,mode='preview',expected_total=15906):
    if output.exists():raise RuntimeError('Refusing to overwrite existing release '+str(output))
    assert mode in ('preview','public')
    source=json.loads((root/'data/regions/nationwide_locality_candidates_5034.json').read_text(encoding='utf-8'))
    regions=parse_regions(source)
    original=json.loads((root/'sites/clinicflower-preview/clinicflower-copy-pool-720.json').read_text(encoding='utf-8'))
    assert len(original['blocks'])==720
    global ORIGINAL_BLOCKS
    ORIGINAL_BLOCKS=original['blocks']
    pool=generate_extra_pool()
    global GENERATED_BY_TOPIC, ORIGINAL_BY_TOPIC, ORIGINAL_WREATH_BY_SUBTOPIC
    GENERATED_BY_TOPIC={}
    for site,rows in pool['items'].items():
        mapping=collections.defaultdict(list)
        for row in rows:mapping[row['topic']].append(row)
        GENERATED_BY_TOPIC[site]=mapping
    ORIGINAL_BY_TOPIC=collections.defaultdict(list)
    for row in original['blocks']:
        if row['category'] in ('병원 특화','치과 특화','한의원 특화','공통 실무'):
            ORIGINAL_BY_TOPIC[row['topic']].append(row)
    assert len(ORIGINAL_BY_TOPIC)>=50
    ORIGINAL_WREATH_BY_SUBTOPIC=collections.defaultdict(list)
    for row in original['blocks']:
        if row['category']!='공통 실무' or row['topic'] not in ('수령 장소','선물 목적','예산','리본 문구','배송 확인','주문 방법'):continue
        if any(x in row['body'] for x in ('화분','식물','관엽','물주기','화기','꽃바구니','실내','분갈이')):continue
        key=row['topic']+'|'+row.get('subtopic',row['title'])
        ORIGINAL_WREATH_BY_SUBTOPIC[key].append(row)
    assert len(ORIGINAL_WREATH_BY_SUBTOPIC)>=45
    target=output/'public'
    target.mkdir(parents=True)
    src=root/'sites/nalmada-shared3/public/assets'
    shutil.copytree(src,target/'assets')
    wreath_src=root/'sites/nalmada-shared3/public/assets/images/celebration-wreath.webp'
    assert wreath_src.is_file(), 'Original wreath image is not present; do not replace with potted plant photo'
    for site,images in SITE_IMAGES.items():
        for name,iw,ih,alt in images:
            asset=target/'assets/images'/name
            assert asset.is_file() and asset.stat().st_size>5000,(site,name,'missing image')
    indexnow_key=(root/'sites/nalmada-shared3/clinic-indexnow-key.txt').read_text(encoding='ascii').strip()
    assert re.fullmatch('[0-9a-f]{32}',indexnow_key)
    report={'sites':{},'mode':mode,'regionSourceCount':len(regions),'parentUnmatchedCount':sum(x[-1]==0 for x in regions),
            'initialPoolBlocks':720,'extraComposedPoolBlocks':pool['count'],'sitePoolBlocks':{k:len(v) for k,v in pool['items'].items()}}
    alln=0
    for site,meta in SITE_META.items():
        base=target/'sites'/site;base.mkdir(parents=True)
        pages={};narrative={}
        def put(path,content,text=None):
            file=base/path.lstrip('/') if path!='/' else base/'index.html'
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text(content,encoding='utf-8')
            pages[path]=file
            if text:narrative[path]=text
        put('/',render_dir(site,'home',(),regions,mode))
        for p in sorted({x[1] for x in regions}):put(province_path(p),render_dir(site,'province',(p,),regions,mode))
        for p,d in sorted({(x[1],x[2]) for x in regions}):put(district_path(p,d),render_dir(site,'district',(p,d),regions,mode))
        for r in regions:
            markup,substance=render_region(site,r,pool,mode)
            put(region_path(r[0]),markup,substance)
        assert len(pages)==5302
        urls=set(pages)
        # Check every internal anchor target and orphan page: page links are site-local.
        incoming=collections.Counter()
        links=0
        for source_path,file in pages.items():
            doc=file.read_text(encoding='utf-8')
            for ref in re.findall(r'<a\s[^>]*href="([^"]+)"',doc):
                if ref.startswith('tel:') or ref.startswith('#') or ref.startswith('mailto:'):continue
                if not ref.startswith('/'):raise RuntimeError('Unexpected outbound/internal URL '+ref)
                dest=ref.split('#')[0] or source_path
                if dest not in urls:raise RuntimeError(f'Broken link {source_path} -> {dest}')
                incoming[dest]+=1;links+=1
            if mode=='public':
                target_url='https://'+meta['host']+source_path
                if '<link rel="canonical" href="'+target_url+'">' not in doc:raise RuntimeError('Bad canonical '+source_path)
                if '<meta name="robots" content="index,follow">' not in doc:raise RuntimeError('Incorrect index intent')
            else:
                if 'name="robots" content="noindex,nofollow"' not in doc:raise RuntimeError('Noindex missing')
                if 'rel="canonical"' in doc:raise RuntimeError('Preview canonical exists')
        orphan=sorted(set(pages)-set(incoming))
        if orphan:raise RuntimeError('Orphan pages: '+repr(orphan[:10]))
        assert len(narrative)==5034 and len({sha(v) for v in narrative.values()})==5034
        sitemap=None
        if mode=='public':
            # Per-site 5302 < 50k URL and < 50MB protocol limits.
            ns='http://www.sitemaps.org/schemas/sitemap/0.9'
            el=ET.Element('urlset',{'xmlns':ns})
            for pth in pages:
                ET.SubElement(ET.SubElement(el,'url'),'loc').text='https://'+meta['host']+pth
            sitemap=ET.tostring(el,encoding='utf-8',xml_declaration=True)
            (base/'sitemap.xml').write_bytes(sitemap)
        (base/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: https://'+meta['host']+'/sitemap.xml\n' if mode=='public' else 'Disallow: /\n'),encoding='utf-8')
        # Preserve the existing 50 canonical regional URL choices exactly.
        # RSS bodies are derived from corresponding rendered HTML, not invented
        # feed-only excerpts or arbitrary publication timestamps.
        rss,rss_evidence=create_rss(
            host=meta['host'],
            channel_title='꽃이랑 '+meta['short'],
            channel_description=meta['intro'],
            paths=list(narrative)[-50:],
            page_files=pages,
            require_public_canonical=(mode=='public'))
        (base/'rss.xml').write_bytes(rss)
        if mode=='public':(base/(indexnow_key+'.txt')).write_text(indexnow_key,encoding='ascii')
        report['sites'][site]={'host':meta['host'],'htmlCount':len(pages),'regionalCount':len(narrative),
            'provinceHubCount':17,'districtHubCount':250,'incomingLinks':sum(incoming.values()),
            'orphans':len(orphan),'duplicateFullBodyHashes':0,'sitemapUrlCount':len(pages) if sitemap else 0,
            'sitemapBytes':len(sitemap) if sitemap else 0,'rssItems':rss_evidence['itemCount'],'rssBytes':rss_evidence['bytes'],
             'rssHasFullBodies':rss_evidence['allItemsHaveDescription'] and rss_evidence['allItemsHaveContentEncoded'],
             'rssHasUnverifiedDates':rss_evidence['feedHasFabricatedDate'],'paths':sorted(pages),
            'regionalNarrative':narrative}
        alln+=len(pages)
    assert alln==expected_total
    report['htmlCount']=alln
    report['assetCount']=sum(p.is_file() for p in target.rglob('*'))
    assert report['assetCount']<=18000,report['assetCount']
    shutil.copyfile(root/'sites/nalmada-shared3/worker.national.mjs',output/'worker.mjs')
    config={'name':'sfv5-nalmada-domain','main':'./worker.mjs',
       'compatibility_date':'2026-10-30','workers_dev':True,'preview_urls':False,
       'assets':{'directory':'./public','binding':'ASSETS','html_handling':'none',
                 'not_found_handling':'none','run_worker_first':True}}
    (output/'wrangler.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'content-pool-compositions.json').write_text(json.dumps(pool,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    a.add_argument('--output',type=Path,required=True)
    a.add_argument('--mode',choices=['preview','public'],default='preview')
    a.add_argument('--audit-json',type=Path,required=True)
    args=a.parse_args()
    report=generate(args.root.resolve(),args.output.resolve(),args.mode)
    # Narrative only is written separately for pairwise similarity audit; never inside public assets.
    bodies={s:info.pop('regionalNarrative') for s,info in report['sites'].items()}
    (args.output/'narrative-only-audit-input.json').write_text(json.dumps(bodies,ensure_ascii=False)+'\n',encoding='utf-8')
    args.audit_json.parent.mkdir(parents=True,exist_ok=True)
    args.audit_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CLINIC_NATIONAL_BUILD='+json.dumps({'html':report['htmlCount'],'assets':report['assetCount'],
           'sites':{s:{k:v for k,v in row.items() if k!='paths'} for s,row in report['sites'].items()}},ensure_ascii=False))
if __name__=='__main__':main()