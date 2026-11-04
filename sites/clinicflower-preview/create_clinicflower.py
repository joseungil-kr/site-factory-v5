"""Clinicflower V5: curated situation-based copy pool + one noindex sample.
No network, no invented branch/delivery/price claims. Images come from this chat's imagegen outputs.
"""
from __future__ import annotations
import json,re,hashlib,html,shutil
from pathlib import Path
from collections import Counter
from PIL import Image

ROOT=Path(__file__).resolve().parent
IMAGES=(ROOT/'original-imagegen' if (ROOT/'original-imagegen').is_dir() else Path('/mnt/data/ghostwriter_images/generated'))
IMAGE_MAP={
 'hero.webp':('a_photorealistic_high_end_modern_clinic_lobby_in_1_batch_1.png','cc45db70-f0a4-4b34-b93d-8dbe7ecdb9fe','hero','여러 개원 축하 식물로 장식된 밝은 클리닉 로비'),
 'hospital.webp':('a_bright_clean_modern_hospital_reception_lobby_i_2_batch_2.png','9a354c7d-eb3b-4831-8882-c45604b34063','hospital','개원 축하 화분을 배치한 병원 로비 연출'),
 'dental.webp':('a_bright_modern_dental_clinic_reception_waiting_a_3_batch_3.png','19c68071-6ad9-46e6-bb1a-4ea3bcecd6d0','dental','개원 화분과 치과 대기실 연출'),
 'oriental.webp':('a_crisp_photorealistic_interior_scene_of_a_modern_4_batch_4.png','da72a39a-4ae9-4f26-b4ad-29769cad247c','oriental','원목 인테리어의 한의원 개원 축하 화분 연출'),
 'phone.webp':('a_bright_clean_modern_florist_shop_interior_phot_5_batch_5.png','6ece85fa-5a78-45fc-b089-a107ffb00ce1','phone','축하 화분을 준비하며 전화 주문을 상담하는 연출'),
}
# Verbatim tool request prompts from this conversation. The image-generation response
# omitted generatedAt; neither file mtime nor chat time is falsely assigned as generation time.
PROMPTS={
 'hero.webp':"Create a photorealistic website hero image for a Korean flower-delivery service focused on hospital, dental clinic, and Korean medicine clinic opening congratulation plants. Show an elegant modern clinic lobby with several high-quality congratulatory potted plants and tasteful ribbons, in a bright clean premium atmosphere. Leave generous negative space on the left side for webpage headline text and a phone-order call-to-action overlay. Style: realistic commercial photography, warm natural light, clean composition, trustworthy local business feel, refined and premium, no visible logos, no watermarks, no embedded website UI.",
 'hospital.webp':"Create a photorealistic commercial image for a hospital opening congratulation plant delivery webpage. Show a modern hospital reception area with one prominent elegant congratulatory potted plant near the desk, clean medical interior, professional and welcoming mood, natural lighting, visually clear subject, realistic Korean business setting. Keep the composition suitable for a website section image. No logos, no watermarks, no embedded UI.",
 'dental.webp':"Create a photorealistic commercial image for a dental clinic opening congratulation plant delivery webpage. Show a bright, modern dental clinic reception or waiting area with a stylish congratulatory potted plant placed appropriately, white and light-wood interior, clean and friendly atmosphere, polished realistic photography, suitable for a website section image. No logos, no watermarks, no embedded UI.",
 'oriental.webp':"Create a photorealistic commercial image for a Korean medicine clinic (한의원) opening congratulation plant delivery webpage. Show a refined Korean medicine clinic interior or entrance lounge with an elegant congratulatory potted plant, calm natural palette, wood accents, clean and welcoming atmosphere, realistic commercial photography, suitable for a website section image. No logos, no watermarks, no embedded UI.",
 'phone.webp':"Create a photorealistic website support image emphasizing phone-order flower service. Show a florist in a neat flower shop or workshop preparing an opening congratulation potted plant with a ribbon while taking or confirming a phone order. Include beautiful plants and packaging materials in the scene, with some open space for possible webpage text overlay. Style: realistic commercial photography, friendly and trustworthy, bright and clean, Korean local business feel, no visible logos, no watermarks, no embedded UI."
}

hospital=[
('진료 시작일과 개원식','진료 시작일과 개원 축하 행사가 서로 다른 날일 수 있습니다','행사 일정과 실제 수령 가능 시간을 따로 확인합니다','진료 시작일을 배송 가능 일시와 동일하게 가정하지 않습니다','개원식 날짜와 화분을 받을 날짜 중 어느 쪽을 원하시는지 확인하세요'),
('병원 정식 명칭','병원 명칭에는 고유 상호와 진료과 표기가 함께 들어갈 수 있습니다','공식 병원명을 리본 제작 전에 문자로 확인합니다','확인하지 않은 전문과목이나 직함을 더하지 않습니다','리본에 사용할 수신자 병원명을 정확히 알려주세요'),
('공동 개원 축하','여러 의료진이 함께 개원하는 곳에서는 호칭을 정하기 어려울 수 있습니다','원장 개인명 또는 기관명 중 적절한 표기를 선택합니다','공동 원장 여부를 모른 채 개인 이름을 임의로 적지 않습니다','받는 분 이름은 병원 상호와 원장 성함 중 어떤 것으로 할까요'),
('대기 공간 동선','접수대와 대기석 사이 통로는 환자가 오가는 공간입니다','화분을 놓을 바닥 면적과 이동 동선을 함께 확인합니다','큰 화분이면 무조건 눈에 띄고 좋다고 단정하지 않습니다','접수대 주변에 화분을 세워 둘 여유 공간이 있는지 확인해주세요'),
('접수 창구 인계','진료 중인 병원의 접수 직원은 환자 응대로 바쁠 수 있습니다','배송 연락을 받을 담당자와 대체 연락처를 준비합니다','수령 담당자가 확인되지 않았는데 임의로 물건을 놓지 않습니다','누가 수령할 수 있는지 연락 가능한 번호를 알려주세요'),
('원장실 전달','대표실로 전하고 싶은 축하 선물은 일반 로비 선물과 전달 방식이 다릅니다','원장실 직접 전달과 접수대 보관 중 수령 방식을 정합니다','원장실 출입 가능 여부를 기사에게 임의로 맡기지 않습니다','원장님께 직접 전달해야 하는지 접수대 인계가 가능한지 알려주세요'),
('건물 층수','상가 건물에 입주한 병원은 층수와 출입구가 배송에 영향을 줍니다','층수·건물명·엘리베이터 정보를 함께 전합니다','같은 건물 주소라는 이유로 출입 경로까지 안다고 가정하지 않습니다','건물 층수와 사용 가능한 입구가 어디인지 확인해주세요'),
('공사 마무리 일정','개원 직전에는 간판·실내 공사가 끝나지 않았을 수 있습니다','정리 작업 완료 후 화분을 받을 수 있는지 문의합니다','공사 중인 건물 내부에 임의로 설치할 수 있다고 약속하지 않습니다','받을 공간이 준비된 날과 시간을 확인해주세요'),
('병원 이전 축하','기존 병원이 다른 주소로 이전했다면 축하 메시지의 성격이 달라집니다','개원과 이전 개원 중 알맞은 표현을 정합니다','이전한 병원을 신규 개원 병원으로 단정하지 않습니다','리본 문구를 축 개원 또는 이전 축하 중 무엇으로 적을까요'),
('진료시간과 배송','접수 업무가 집중되는 시간대에는 화분 수령이 부담될 수 있습니다','수령처가 편한 시간대와 연락 방법을 정합니다','홈페이지 진료시간만 보고 반입 가능한 시간을 확정하지 않습니다','진료 시작 전·점심시간 중 수령 가능한 시간대가 있나요'),
('병원 로비 채광','병원 내부의 창가와 복도는 자연광 조건이 다릅니다','빛이 들어오는 위치에 맞춰 관리할 수 있는 식물을 상담합니다','모든 식물이 어두운 실내에서도 같은 상태로 유지된다고 말하지 않습니다','화분이 놓일 곳에 창문이 가까이 있나요'),
('환자 이동 통로','병원에서는 이동 보조기기와 유모차의 통행을 고려해야 합니다','화분 높이와 폭을 실제 비치 위치에 맞춥니다','예쁜 화분이라는 이유로 통로를 막는 배치를 권하지 않습니다','통로 폭을 침해하지 않을 장소를 정했는지 확인해주세요'),
('병원 축하 리본','리본에는 축하 문구뿐 아니라 보내는 사람 이름도 들어갑니다','수신자·발신자 표기를 문자로 재확인합니다','상호에 쓰이는 특수문자·띄어쓰기를 임의로 바꾸지 않습니다','발신자 이름과 소속을 그대로 적어 주세요'),
('선물 예산 공유','직장 동료 여러 명이 함께 보내는 축하 화분은 예산 상한이 중요합니다','배송비·리본을 포함한 총액 기준으로 상담합니다','특정 규모의 병원에 정해진 선물 가격이 있다고 말하지 않습니다','생각하신 전체 예산 범위를 말씀해주세요'),
('정기 관리 편의','인력이 바쁜 공간에서는 화분 관리에 많은 시간을 쓰기 어렵습니다','물주기·채광·용기 배수 방식 등을 구매 전에 묻습니다','물만 자주 주면 어떤 화분도 잘 자란다고 설명하지 않습니다','식물 관리를 맡을 분이 있는지 확인해 주세요'),
('신규 주소 정확성','개원 초기에는 지도 서비스의 주소 정보가 늦게 갱신될 수 있습니다','건물명과 도로명 주소를 직접 받은 자료로 확인합니다','검색 결과에 나온 병원 위치만 믿고 배송을 확정하지 않습니다','도로명 주소·층수·호수를 함께 적어주세요'),
('축하 선물 늦은 전달','개원식 후에도 축하 의미를 담아 화분을 전할 수 있습니다','현재 방문 및 수령이 가능한 날짜를 새로 확인합니다','개원식이 지났다고 선물을 보낼 수 없다고 단정하지 않습니다','개원일과 관계없이 수령하기 편한 날짜가 언제인가요'),
('향과 선호','의료 공간에는 향에 민감한 방문자가 있을 수 있습니다','향이 강한 꽃장식과 관엽 화분의 차이를 상담합니다','특정 종류를 무조건 무향·무알레르기라고 주장하지 않습니다','수령처에서 향이나 꽃가루를 피하고 싶은지 확인해주세요'),
('배송 완료 안내','직접 방문하지 못하는 발신자는 수령 여부를 알고 싶어할 수 있습니다','판매처가 제공할 수 있는 인계 확인 방식을 미리 묻습니다','완료 사진이 항상 제공된다고 확약하지 않습니다','배송 후 문자 또는 사진 확인을 원하시는지 말씀해주세요'),
('행사 장소와 상시 비치','개원식 행사장과 일상적으로 화분을 놓을 로비는 다를 수 있습니다','행사 종료 후에도 놓일 공간을 고려해 제품을 상담합니다','행사 당일 한 번 보기 좋다는 이유만으로 과도한 크기를 추천하지 않습니다','행사 후에도 같은 장소에 둘 예정인지 확인해주세요')]

dental=[
('치과 개원일 확인','치과의 진료 개시일과 개원 행사일이 다른 경우가 있습니다','행사일·의료진 출근일·수령 가능 시간을 구분합니다','의료기관 개업일을 일방적인 배송일로 잡지 않습니다','축하화분은 어느 날 받을 수 있는지 치과에 확인해주세요'),
('치과의원 명칭','치과 명칭에는 의원과 병원 등 구분이 포함될 수 있습니다','리본에 들어갈 상호를 정확히 받아둡니다','상호의 병원·의원 구분을 임의 변경하지 않습니다','리본용 치과 공식 명칭을 문자로 보내주세요'),
('접수 데스크 크기','치과 접수대에는 전산 장비와 접수 서류가 놓이기도 합니다','탁상용·바닥형 중 배치 가능한 크기를 정합니다','접수대가 보인다는 이유로 화분을 무조건 그 위에 놓지 않습니다','탁상형과 바닥형 중 어떤 자리가 있나요'),
('치과 대기실 채광','치과 대기 공간은 창가와 안쪽의 조도 차이가 큽니다','놓을 위치의 햇빛과 실내 환경을 확인합니다','빛이 적어도 어떤 식물이나 똑같이 유지된다고 말하지 않습니다','화분을 놓을 곳이 창가인가요 대기실 안쪽인가요'),
('진료 장비 동선','치과 내부에는 환자·의료진과 장비가 오가는 길이 있습니다','관엽 화분이 진료 구역을 방해하지 않도록 배치합니다','진료실 통로에 대형 화분을 바로 놓는 방식을 권하지 않습니다','화분은 진료실 밖 대기 공간에 두실 예정인가요'),
('공동 원장 수신자','치과 원장 여러 명의 공동 개원이 있을 수 있습니다','개인 이름 대신 치과 상호를 쓰는 방안도 검토합니다','확인되지 않은 원장 성함을 리본에 넣지 않습니다','받는 분을 치과 상호로 통일할지 확인해주세요'),
('치과 이전 오픈','이전 개원을 축하하는 경우 새 주소 확인이 중요합니다','이전 축하인지 신규 개원인지 정확히 구분합니다','지도상 옛 주소로 배송할 수 있다고 판단하지 않습니다','새로 이전한 치과 주소와 리본 문구를 확인해주세요'),
('개원 전 반입','정식 진료 전날에도 건물 출입 제한이 있을 수 있습니다','직원이 실제로 있는 시간과 로비 개방 시간을 확인합니다','준비 중인 치과는 항상 현장에 사람이 있다고 보지 않습니다','화분을 받을 직원의 방문 시간을 알려주세요'),
('치과 축하 예산','치과 개원 선물의 적절한 금액은 보내는 사람 예산에 따라 달라집니다','원하는 예산과 화분 크기를 함께 상담합니다','의료기관 업종만으로 특정 가격대를 필수라고 하지 않습니다','리본·배송을 포함해 얼마를 생각하고 계신가요'),
('인테리어와 화분','밝은 벽과 원목 가구가 많은 실내에는 용기 색감도 중요합니다','치과의 분위기와 어울리는 식물·화기를 상담합니다','실내 사진이 없는데 색상과 구조를 임의로 단정하지 않습니다','원하는 화분 용기 색감이나 분위기가 있나요'),
('치과 직원 인계','진료 중 접수 담당자가 바뀌면 인계 경로가 달라집니다','연락 가능한 직원과 부재 시 연락 방법을 정합니다','직원이 안 보인다고 무단으로 복도에 두지 않습니다','수령 담당자 휴대전화 또는 안내 가능한 번호가 있나요'),
('향이 강한 꽃 회피','대기 공간에는 냄새에 예민한 내원객도 있을 수 있습니다','관엽 식물과 꽃 장식의 종류를 구분해 상담합니다','모든 식물이 향이나 꽃가루가 없다고 단정하지 않습니다','향이 강하지 않은 구성으로 상담해드릴까요'),
('반입 통로와 엘리베이터','치과가 상층부에 있다면 입구 폭과 운반 동선을 확인해야 합니다','배송지 층수와 엘리베이터 접근 조건을 전달합니다','모든 규격을 추가 확인 없이 운반 가능하다고 약속하지 않습니다','건물에 엘리베이터가 있나요'),
('동일 건물 여러 치과','같은 상가 건물에 비슷한 이름의 의료기관이 있을 수 있습니다','도로명·층·호수·수령 연락처를 함께 기입합니다','상호 검색만으로 도착 위치가 정확하다고 생각하지 않습니다','건물명과 치과의 정확한 층·호수를 적어주세요'),
('치과 개원 행사','축하 행사를 별도 장소에서 진행하면 화분 수령지가 달라집니다','진료 공간과 행사 장소 중 배송받을 곳을 정합니다','치과 주소로 보내면 행사장에서 보일 거라고 보장하지 않습니다','개원식은 치과 내부에서 진행하나요'),
('긴 리본 문구','치과 공식 상호와 발신자명이 길면 리본 가독성을 고려해야 합니다','기본 축하 문구를 짧고 정확하게 정합니다','장문의 메시지를 리본에 전부 넣을 수 있다고 확답하지 않습니다','리본에 가장 먼저 보여줄 문구가 무엇인가요'),
('화분 관리 부담','진료실이 바쁜 치과에서는 관리가 쉬운 화분을 원하기도 합니다','햇빛과 물주기 조건을 설명받고 선택합니다','물주기를 전혀 하지 않아도 된다고 광고하지 않습니다','관리하는 직원이 따로 계신가요'),
('외부 발신자','거래처나 학교 동문 등 다양한 분들이 치과 개원을 축하할 수 있습니다','발신자 표기 명의와 소속을 주문 전에 확인합니다','실제 관계를 꾸며서 리본 문구를 작성하지 않습니다','보내는 분의 이름과 회사명을 정확히 알려주세요'),
('개원 후 배송','치과 개원 직후보다 운영이 안정된 뒤 보내는 선물도 있습니다','실제 수령 가능 일시를 최신 정보로 확인합니다','개원식이 지났다는 이유로 배송을 못 한다고 가정하지 않습니다','축하 선물 받을 편한 시간을 직접 확인해주세요'),
('현장 사진 요청','멀리서 주문하는 경우 배송 완료 확인이 중요합니다','판매처가 제공 가능한 확인 절차를 먼저 문의합니다','배송 사진이 기본 제공된다고 단정해 표시하지 않습니다','어떤 방식의 배송 완료 안내를 원하시나요')]

oriental=[
('한의원 개원식','한의원 개원식 날짜와 실제 진료 시작일이 다를 수 있습니다','어느 일정에 맞춰 화분을 받는지 미리 정합니다','진료 시작일을 당연히 개원식과 같은 날로 보지 않습니다','축하화분 수령일을 한의원 측과 확인해주세요'),
('한의원 상호','전통적인 한의원 이름은 한글·한자 표기가 함께 있는 경우가 있습니다','리본의 공식 표기 방식과 띄어쓰기를 확인합니다','한자 표기를 확인 없이 임의로 넣지 않습니다','한의원 이름을 리본에 어떤 글자로 적을까요'),
('진료실과 대기 공간','한의원에는 상담 공간과 치료 공간이 분리되어 있을 수 있습니다','식물을 놓을 곳의 동선과 가구 배치를 확인합니다','공간 구분을 모른 채 치료실 내부 설치를 약속하지 않습니다','화분은 입구·대기실·원장실 중 어디에 둘까요'),
('원목 인테리어','한의원 내부가 원목이나 차분한 색감으로 꾸며진 경우가 있습니다','식물 잎 모양과 화분 용기 톤을 함께 비교합니다','현장 확인 없이 모든 한의원이 전통적인 실내라고 단정하지 않습니다','개원 공간의 분위기를 알려주시면 선택에 참고하겠습니다'),
('한약장 주변 배치','진료 준비 공간에는 약재 보관함이나 장비가 있을 수 있습니다','출입구와 업무 가구를 피할 수 있는 공간을 찾습니다','약재 보관 공간 근처에 화분을 임의로 둘 수 있다고 안내하지 않습니다','업무 공간과 분리된 비치 자리가 있나요'),
('한의원 환기와 채광','진료 공간의 자연광과 온도가 식물 관리에 영향을 줄 수 있습니다','창가·내부 복도 중 비치할 위치를 확인합니다','실내 환경에 관계없이 동일한 품종을 추천하지 않습니다','햇빛이 들어오는 자리인가요'),
('한의원 이전 개원','기존 한의원이 새 장소로 이동하는 경우도 있습니다','이전 개원과 신규 개원을 구분한 축하 문구를 고릅니다','이전한 한의원을 신규 설립이라 단정하지 않습니다','개원 축하와 이전 축하 중 어느 표현이 맞을까요'),
('한의원 수령 담당자','개원 준비 직원이 많지 않다면 배송 연락이 중요합니다','연락받을 담당자와 비상 연락 방법을 확보합니다','원장님의 진료 시간을 방해하는 임의 연락은 피합니다','당일 수령 가능한 직원 연락처가 있나요'),
('한의원 층수','한의원은 주거·상가가 섞인 건물에 입주할 수 있습니다','층수와 출입로·엘리베이터 정보를 확인합니다','건물에 들어갈 수 있다고 단순히 주소만으로 판단하지 않습니다','정확한 층·호수와 방문 출입구를 알려주세요'),
('한의원 원장 이름','선물 리본에 원장님 성함을 명시하는 사례가 있습니다','성함·직함·상호를 수령 측 자료로 확인합니다','모르는 원장 이름을 검색만으로 채우지 않습니다','정확한 받는 분의 성함이나 한의원명을 알려주세요'),
('장식용과 장기 비치','개원식 하루 장식용인지 장기간 둘 화분인지 목적이 다릅니다','인테리어와 관리 편의를 함께 고려합니다','화분을 실내에 영구적으로 둘 수 있다고 보장하지 않습니다','행사 뒤에도 그대로 비치할 예정인가요'),
('목재 가구와 화기','가구 소재에 따라 화분의 받침과 물관리도 중요합니다','배수받침 등 실내 사용에 필요한 조건을 묻습니다','물로 인한 가구 손상 위험이 없다고 단정하지 않습니다','바닥에 둘지 가구 위에 둘지 확인해주세요'),
('한의원 축하 메시지','개원 축하 문구는 상대방의 새 출발을 응원하는 내용이 어울립니다','짧은 문장과 정확한 발신자 표기를 조합합니다','불필요하게 건강 효능이나 치료 성과를 연상시키는 문구는 피합니다','축 개원과 발전 기원 중 원하는 문구가 있나요'),
('한의원 방문 안내','수령처 안내가 제한된 건물에서는 방문 절차 확인이 필요합니다','경비실·출입문·연락 가능한 시간을 확인합니다','배송 기사가 별도 연락 없이 들어갈 수 있다고 판단하지 않습니다','차량 접근과 출입 안내가 필요한 건물인가요'),
('개원 전 청소','인테리어 청소를 마치기 전에는 화분 반입이 방해가 될 수 있습니다','비치 장소 정리 완료 시점에 맞춰 상담합니다','청소 중인 공간에 별도 설치가 가능하다고 약속하지 않습니다','실내 정리 후 받을 수 있는 시각을 확인해주세요'),
('한의원 동료 선물','의료계 동료나 가족이 개원을 축하하는 경우가 많습니다','발신자의 명의와 리본 수신자를 별도로 정합니다','수신자와 보내는 분 관계를 임의로 꾸며 적지 않습니다','리본에 쓰일 발신자 이름을 확인해주세요'),
('여름과 겨울 반입','계절의 외부 기온은 식물 운반 시 고려할 요소입니다','날씨에 맞춘 수령 일정과 실내 인계를 상담합니다','계절에 관계없이 식물이 전혀 영향을 받지 않는다고 말하지 않습니다','배송 당일 바로 실내에서 받을 수 있나요'),
('대기실 화분 크기','차분한 대기 공간에서는 화분의 높이보다 여유 공간이 중요할 수 있습니다','사람이 앉고 움직이는 자리와 식물 폭을 비교합니다','큰 화분이 항상 좋은 선물이라고 단정하지 않습니다','대기실에 놓을 공간의 크기를 알려주세요'),
('한의원 배송 확인','개원 선물 발신자가 직접 방문하지 못하는 경우도 있습니다','인계 확인을 받을 방법을 주문 전에 확인합니다','사진 발송이나 정확한 도착 시각을 사전 확약하지 않습니다','배송 결과 안내 방법을 전화로 문의해주세요'),
('한의원 개원 후 축하','개원 첫날이 지난 뒤 선물을 전하는 경우도 있습니다','일정이 지난 뒤에는 현재 수령 가능 시간을 다시 확인합니다','개원식 당일에만 화분 배송이 된다고 단정하지 않습니다','이번 주 중 언제 받기 편하신가요')]

COMMON={
'수령 장소':[
('접수대 앞','수령 장소는 접수대 앞인지 건물 로비인지에 따라 설치 방식이 달라집니다','실제 직원이 인계받을 수 있는 위치를 정합니다','수령할 장소를 확인하지 않은 채 복도에 두지 않습니다'),
('건물 지하 주차장','지하 주차장에서 화분을 옮기려면 건물 반입 경로가 중요합니다','주차장에서 내부로 이어지는 입구 정보를 확인합니다','차량 진입이 반드시 가능하다고 단정하지 않습니다'),
('출입 통제 건물','의료 건물의 출입 통제 방식은 장소마다 다릅니다','경비실 연락이나 방문 허용 절차가 필요한지 확인합니다','문 앞에 임의로 두고 배송 완료라고 처리하지 않습니다'),
('복수 출입구','큰 건물에 출입구가 여러 개면 기사와 수령자가 엇갈릴 수 있습니다','기사에게 안내할 정확한 문 이름과 층수를 적어 둡니다','건물 주소만 있으면 누구나 찾는다고 생각하지 않습니다'),
('접수 업무 시간','접수대가 가장 바쁜 시간을 피하면 인계가 원활할 수 있습니다','담당자가 화분을 받을 수 있는 시간을 확인합니다','진료시간이 곧 배송 수령시간이라고 주장하지 않습니다'),
('층수 표기','상가의 층수는 같은 주소 안에서 배송 위치를 구분합니다','층수와 호수까지 직접 확인한 주소를 전달합니다','주소에서 숫자가 빠진 채 주문을 확정하지 않습니다'),
('일시 보관 위치','수령자가 자리를 비울 때를 대비한 인계 장소가 필요할 수 있습니다','대체 수령 위치를 미리 결정합니다','보관 동의 없이 화분을 임의로 놓지 않습니다'),
('행사장과 진료실','행사장을 별도로 빌렸다면 화분의 최종 위치가 달라집니다','행사장 주소와 병원 주소를 구분합니다','개원 행사 참석 장소를 병원 주소라고 가정하지 않습니다'),
('큰 화분 반입','화분 크기에 따라 문폭과 엘리베이터 조건이 달라질 수 있습니다','설치 희망 위치까지 운반할 수 있는지 사전 상담합니다','운반 조건을 모른 채 모든 제품이 가능하다고 안내하지 않습니다'),
('현장 연락처','받는 곳 대표번호가 바쁘면 실제 인계가 늦어질 수 있습니다','수령 연락을 담당할 전화번호를 별도로 적습니다','대표번호만으로 즉시 연결된다고 기대하지 않습니다')],
'선물 목적':[
('신규 개원','새롭게 문을 여는 병원에는 새 출발을 응원하는 문구가 어울립니다','정확한 개원 목적과 시점을 확인합니다','개원 사실을 확인하지 않은 상호에 축하 메시지를 임의로 보내지 않습니다'),
('이전 확장','기존 공간에서 더 넓은 곳으로 이전한 경우 축하 표현을 조정합니다','이전·확장 중 실제 상황을 확인합니다','모든 이전을 규모 확장이라고 단정하지 않습니다'),
('개원 기념 행사','개원식 당일에 어울리는 선물과 장기 비치용 화분은 선택 기준이 다릅니다','행사 이후 어디에 둘지 함께 검토합니다','사진 촬영용 연출을 실제 장기 관리 가능성과 혼동하지 않습니다'),
('늦은 축하','개원 일정이 지난 후에도 새 출발을 축하할 수 있습니다','수령하기 편한 날짜를 새로 정합니다','늦었다는 이유로 불필요한 부담을 주는 문구를 강요하지 않습니다'),
('의료진 동료 선물','동료 의료진의 축하 선물은 발신자 표기가 중요합니다','병원 이름과 개인 이름 가운데 어떤 명의를 쓸지 정합니다','확인되지 않은 관계나 직함을 리본에 더하지 않습니다'),
('가족 축하','가족이 보내는 화분은 응원 메시지의 온도가 다를 수 있습니다','가족 이름과 축하 문구를 간결하게 조합합니다','받는 분이 원하지 않는 별칭을 임의로 넣지 않습니다'),
('협력 업체 선물','협력 업체의 선물은 상호 표기 정확성이 우선입니다','사업자 상호와 담당자명을 확인합니다','계약 관계나 의료 성과를 과장하는 문구는 피합니다'),
('단체 선물','단체 명의로 보내면 발신자 표기의 길이를 조정해야 합니다','공식 단체명과 담당자 연락처를 확인합니다','공동 발신자 전원을 작은 리본에 다 넣겠다고 보장하지 않습니다'),
('개원 축하와 감사','기존 거래에 감사하면서 개원을 축하하는 선물은 목적이 복합적입니다','주된 메시지를 개원 축하와 감사 중 무엇으로 할지 정합니다','서로 다른 목적을 한 문구에 무리하게 담지 않습니다'),
('실내 인테리어 선물','행사용보다 실내 분위기를 위한 선물은 크기와 관리성이 중요합니다','배치 공간과 선호 식물 종류를 함께 검토합니다','실내 장식 효과를 측정할 수 있는 수치로 과장하지 않습니다')],
'예산':[
('총액 기준','화분 가격과 배송에 필요한 비용을 따로 생각하면 최종 금액이 달라질 수 있습니다','리본·배송비를 포함한 최종 견적을 확인합니다','통화 전에 확정가를 임의로 표기하지 않습니다'),
('예산 상한','선물 예산의 최대 금액을 정하면 선택지가 단순해집니다','상한과 희망 분위기를 함께 전달합니다','비싼 상품만 개원 선물에 적합하다고 주장하지 않습니다'),
('공동 구매','여러 사람이 함께 보내는 축하 화분은 결제 명의를 정해야 합니다','발신자 대표 이름과 예산을 확인합니다','참여한 모든 사람의 이름을 무조건 노출하지 않습니다'),
('추가 배송비','도착 지역과 반입 조건에 따라 추가비 여부를 확인할 수 있습니다','상세 주소로 최종 배송비를 질문합니다','같은 시·군·구는 모두 배송비가 같다고 안내하지 않습니다'),
('리본 포함','리본 제작비 포함 여부는 주문 상품마다 달라질 수 있습니다','가격 안에 무엇이 포함되는지 통화에서 확인합니다','리본이 모든 상품에 무료라고 단정하지 않습니다'),
('할인 오인 방지','화면상의 구식 가격표를 그대로 믿으면 결제 금액이 달라질 수 있습니다','현재 주문 가능한 구성과 금액을 확인합니다','최신 확인이 없는 할인율을 표시하지 않습니다'),
('화기 선택','식물 종류뿐 아니라 화분 용기에 따라 견적이 달라질 수 있습니다','화기 소재와 크기를 함께 문의합니다','사진 속 화기를 항상 동일하게 제공한다고 약속하지 않습니다'),
('단체 주문','같은 날 여러 지점에 보내는 주문은 주소별 조건이 다릅니다','각 수령지의 배송 가능 여부를 나누어 확인합니다','묶음 주문이면 무조건 할인된다고 단정하지 않습니다'),
('예산 변경','주문 도중 예산이 바뀌면 후보 식물의 규격도 달라질 수 있습니다','최종 확인한 금액을 다시 읽어 확인합니다','최초 상담 금액을 최종 결제금액이라고 혼동하지 않습니다'),
('결제 수단','주문자의 결제 방식은 실제 판매처 정책에 따라 달라집니다','결제 수단과 증빙 가능 여부를 전화로 확인합니다','확인 없이 현금영수증·카드 결제가 모두 된다고 주장하지 않습니다')],
'식물 관리':[
('채광 확인','같은 실내에서도 창가와 안쪽 공간의 빛이 다릅니다','놓을 곳의 채광과 식물별 권장 조건을 비교합니다','모든 관엽 식물을 무광 환경에 적합하다고 설명하지 않습니다'),
('물주기','물주기는 품종과 계절·실내 환경에 따라 달라집니다','선택한 식물의 관리 안내를 확인합니다','한 달에 한 번 같은 획일적인 주기를 강요하지 않습니다'),
('배수받침','큰 화분을 실내에 둘 때는 물이 흐르는 문제도 생각해야 합니다','실내 비치용 받침과 화기 구조를 확인합니다','배수 방식이 다른 화기를 동일하게 관리하지 않습니다'),
('공간 환기','잎이 많은 식물도 적절한 환기와 관리가 필요합니다','실내 공기 흐름과 식물 배치 위치를 상담합니다','환기가 전혀 없어도 상관없다고 단정하지 않습니다'),
('냉난방 바람','냉난방기 바로 앞 자리는 식물에 부담이 될 수 있습니다','바람이 직접 닿지 않는 위치를 검토합니다','입구 장식이라는 이유로 에어컨 바로 아래만 권하지 않습니다'),
('크기와 성장','식물은 시간이 지나며 높이와 폭이 달라질 수 있습니다','현재 규격뿐 아니라 비치 여유 공간도 고려합니다','촬영 이미지의 크기가 실물 규격과 같다고 말하지 않습니다'),
('관리 담당자','선물 받은 뒤 돌볼 사람이 없다면 관리가 어려워질 수 있습니다','수령 측의 관리 여건을 먼저 물어봅니다','누가 관리하는지 모른 채 장기 생육을 보장하지 않습니다'),
('관리 안내','화분 종류별 관리 자료의 상세함은 판매처에 따라 다릅니다','구매 전에 관리 방법 제공 여부를 확인합니다','모든 주문에 별도 안내서를 제공한다고 단정하지 않습니다'),
('잎 닦기','먼지와 잎 상태를 보는 작은 관리가 도움이 될 수 있습니다','해당 품종에 맞는 관리법을 확인합니다','모든 식물을 같은 세척 방식으로 다루지 않습니다'),
('식물 교체 상담','수령 공간에 이미 큰 화분이 많다면 다른 형태를 고려할 수 있습니다','중복되는 크기·색감인지 미리 묻습니다','축하 선물은 반드시 큰 화분이어야 한다고 강요하지 않습니다')],
'리본 문구':[
('축 개원','축 개원은 의료기관의 새 출발을 짧게 알리는 표현입니다','정확한 상호·발신자명을 함께 확인합니다','실제 이전 개원에 적합하지 않을 수 있는 문구를 강요하지 않습니다'),
('축 개업','개업화분이라는 검색어로 찾더라도 리본은 개원 표현을 선호할 수 있습니다','축 개업과 축 개원 중 선호 문구를 선택합니다','검색 키워드와 리본 문구를 무조건 똑같이 쓰지 않습니다'),
('이전 축하','새 장소로 옮기는 의료기관에는 이전을 축하하는 표현이 자연스러울 수 있습니다','이전·확장 여부를 확인합니다','이전 사실을 모른 채 이전 축하라고 적지 않습니다'),
('발신자 상호','법인이나 협회 이름은 리본 제작 전에 검토가 필요합니다','정식 상호의 띄어쓰기를 정확히 적습니다','발신자 이름을 임의 줄임말로 바꾸지 않습니다'),
('긴 병원 이름','긴 명칭은 리본 폭에 따라 가독성이 떨어질 수 있습니다','핵심 수신자 표기를 우선하고 길이를 조정합니다','주문 전 확인 없이 모든 글자가 잘 보인다고 단정하지 않습니다'),
('동명이인 수신자','같은 성함의 원장님이 여럿이라면 수신자를 혼동할 수 있습니다','병원명과 성함을 함께 확인합니다','이름만으로 배송지까지 특정하지 않습니다'),
('정중한 문장','공식 거래처 선물에는 짧고 정중한 표현이 잘 어울립니다','과장 없는 축하 문구를 고릅니다','건강·성공을 확정적으로 예언하는 문장은 피합니다'),
('개인적 메시지','가까운 관계의 선물은 개인적인 응원을 추가하기도 합니다','받는 분이 원할 분위기를 파악합니다','부담을 줄 수 있는 별명이나 사적인 표현을 임의 기재하지 않습니다'),
('문구 수정 시점','리본 제작 이후에는 문구 변경이 제한될 수 있습니다','제작에 들어가기 전에 최종 문구를 확인합니다','제작 후에도 언제든 무료 변경된다고 약속하지 않습니다'),
('한글·영문 혼용','영문 상호가 포함될 때 오타 여부가 특히 중요합니다','받은 원문을 그대로 복사해 확인합니다','정확하지 않은 영문 철자를 추측해 적지 않습니다')],
'배송 확인':[
('가능 지역','지역명만으로 실제 배송 가능 여부가 확정되지는 않습니다','도로명·건물명으로 배송 가능 여부를 문의합니다','전 지역 당일 배송을 보장한다고 광고하지 않습니다'),
('희망 날짜','행사 일정에 맞추려면 날짜뿐 아니라 수령 시간을 확인해야 합니다','희망일·희망 시간·수령자를 함께 기록합니다','희망 시간에 반드시 도착한다고 약속하지 않습니다'),
('기사 연락','배송을 원활하게 하려면 수령자와 연락이 되는지가 중요합니다','연락 가능한 휴대전화 또는 대표번호를 확인합니다','연락 불가 상황에서 문 앞 인계를 임의 결정하지 않습니다'),
('부재 시 처리','수령자가 잠시 자리를 비우면 사전 협의가 필요할 수 있습니다','대체 연락처와 허용된 인계 방법을 확인합니다','수령 동의 없이 임의 장소에 두지 않습니다'),
('기상 상황','날씨나 도로 상황에 따라 배송 일정 확인이 필요할 수 있습니다','상담 시 가능한 수령 시간대를 다시 확인합니다','교통이나 날씨와 무관하게 정확한 시각을 보장하지 않습니다'),
('배송 완료 안내','주문자는 선물 수령 여부를 확인하고 싶어합니다','판매처에서 제공하는 안내 방식을 확인합니다','배송 사진을 반드시 제공한다고 약속하지 않습니다'),
('연락처 오기입','잘못된 휴대전화 번호는 배송 연락을 어렵게 만듭니다','수령 연락처를 한번 더 읽어 확인합니다','정확한 번호 확인 없이 접수를 끝내지 않습니다'),
('지역 경계','행정동 경계와 실제 배송 동선이 일치하지 않을 수 있습니다','실제 주소를 기준으로 문의합니다','같은 동이라는 이유만으로 배송 조건을 같다고 말하지 않습니다'),
('행사 시간 변경','개원식 시간이 바뀌면 배송 접수 정보도 수정해야 할 수 있습니다','가능한 변경 시점을 판매처에 확인합니다','당일 시간 변경을 무조건 수용한다고 약속하지 않습니다'),
('수령 증빙','단체나 회사 발신자는 인계 확인이 필요할 수 있습니다','제공 가능한 수령 확인 방식을 상담합니다','사진·서명 등 특정 증빙이 무조건 제공된다고 말하지 않습니다')],
'주문 방법':[
('전화 먼저','상품 선택이 어려우면 전화로 조건을 먼저 정리하는 편이 간단합니다','업종·배송지·날짜·예산을 준비합니다','상담 자체가 배송 확정이라고 혼동하지 않습니다'),
('받는 분 확인','의료기관 상호와 실제 수령자를 구분해 두면 좋습니다','받는 분 이름과 연락처를 함께 적습니다','수신자 정보를 추측해서 입력하지 않습니다'),
('보내는 분 확인','리본 발신자와 결제자가 다를 수 있습니다','리본에 표시할 명의와 주문자 연락처를 나눠 확인합니다','결제자 이름을 자동으로 리본에 인쇄하지 않습니다'),
('배송지 전달','도로명 주소만으로 층수를 알 수 없을 때가 많습니다','건물명·층수·호수까지 문자로 확인합니다','주소 일부만으로 배송 약속을 확정하지 않습니다'),
('리본 원문','정확한 리본 문구는 보이는 글자를 그대로 전달해야 합니다','최종 문구를 문자로 복사해 재확인합니다','직함이나 상호를 임의로 줄여 쓰지 않습니다'),
('예산 상담','예산에 맞는 선택지는 품종과 규격에 따라 달라집니다','총액 기준으로 견적을 받습니다','최초 본 사진이 견적 금액에 포함된다고 가정하지 않습니다'),
('상품 확정','연출 사진과 실제 제품은 다를 수 있습니다','현재 공급 가능한 품종·규격·화기를 확인합니다','AI 연출 사진을 실제 판매 상품이라고 안내하지 않습니다'),
('결제 확인','결제는 판매처가 안내하는 실제 방법으로 진행해야 합니다','금액·계좌·입금자명 등 정보를 다시 확인합니다','사이트 본문에 임의 계좌나 확정된 결제 수단을 넣지 않습니다'),
('주문 변경','배송 준비 단계에 따라 주문 변경 가능 범위가 달라질 수 있습니다','변경 연락은 가능한 빨리 합니다','제작 직전 수정이 항상 가능하다고 약속하지 않습니다'),
('상담 시간','전화 연결이 어려운 경우 다시 연락해야 할 수 있습니다','연결 가능한 시간에 주문 정보를 정리해 전달합니다','24시간 상시 상담이라고 근거 없이 표시하지 않습니다')],
'상품 선택':[
('공간 크기','받는 공간이 작다면 식물 높이보다 전체 폭이 더 중요할 수 있습니다','배치 가능한 면적과 식물 규격을 비교합니다','대형 화분만 고급 선물이라고 단정하지 않습니다'),
('인테리어 분위기','실내 디자인과 화분 용기의 조화도 선택 기준입니다','벽·바닥·가구의 색감과 어울리는 구성을 상담합니다','사진 없이 현장 분위기를 안다고 주장하지 않습니다'),
('빛 요구량','동일한 관엽 식물이라도 요구하는 빛의 양이 다릅니다','실제 놓을 자리에 적합한지 확인합니다','빛이 없어도 모든 식물이 잘 자란다고 설명하지 않습니다'),
('관리 난도','새로 개원한 의료기관은 화분 관리가 부담될 수 있습니다','관리 가능한 빈도와 품종을 비교합니다','어떤 화분도 관리가 필요 없다고 말하지 않습니다'),
('화분 재질','용기 재질에 따라 무게와 분위기가 달라질 수 있습니다','운반·관리·배치를 함께 고려합니다','사진의 화기를 항상 동일하게 공급한다고 확약하지 않습니다'),
('식물 잎 모양','큰 잎과 가는 잎은 공간에서 보이는 인상이 다릅니다','받는 분의 선호와 인테리어에 맞는 모습을 상담합니다','미신이나 풍수를 확정적 효능처럼 설명하지 않습니다'),
('기념성','개원 축하화분은 오래 보관할 수도 있는 선물입니다','받는 분이 선호하는 식물 유형을 먼저 확인합니다','관엽식물의 수명이나 생장을 무조건 보장하지 않습니다'),
('진열 위치','접수대 위와 바닥에는 적절한 크기가 다릅니다','최종 비치 위치를 알려주고 견적받습니다','탁상 제품을 바닥용 대형 화분과 동일하게 표시하지 않습니다'),
('품종 대체 가능성','계절이나 실제 공급 사정에 따라 상품 구성이 달라질 수 있습니다','상담 시 가능한 대체 옵션을 확인합니다','연출 사진과 완전히 동일한 구성이라고 약속하지 않습니다'),
('축하용 꽃과 식물','꽃바구니와 개원축하 화분은 관리 방식과 표현이 다릅니다','당일 행사장 장식인지 장기 비치인지 목적을 확인합니다','꽃과 식물을 동일한 상품이라고 안내하지 않습니다')]
}

HUB_TOPICS=[
('전국 지역 찾기','광역단체·기초단체·상세 지역명을 단계적으로 찾아볼 수 있습니다','확인된 상위 지역명과 연결해 잘못된 주소로 이동하지 않도록 합니다'),
('동 이름 중복','동명이 다른 시·군·구에 속한 경우가 있습니다','광역단체와 기초단체를 함께 표기해 혼동을 줄입니다'),
('읍면 단위','읍·면 주소가 동 주소와 배송 조건이 다를 수 있습니다','원장에 존재하는 정확한 행정주소와 실제 배송지를 구분합니다'),
('시군구 허브','상위 지역 페이지는 하위 지역 검색을 돕는 안내 역할을 합니다','실제 하위 지역이 확인된 곳만 연결합니다'),
('광역 허브','시·도 페이지는 한 지역의 후보를 한눈에 비교하게 돕습니다','도시와 지역 상세페이지를 중복 생성하지 않습니다'),
('행정구역 변경','행정구역 명칭이나 소속이 갱신되는 경우가 있습니다','지역 원장을 실제 관리 코드와 대조합니다'),
('동 경계','지역명이 배송 기사 동선과 정확히 일치하지 않을 수 있습니다','주소 확인 상담을 최종 기준으로 안내합니다'),
('주소 표준화','도로명주소와 지번주소가 혼재돼 입력되기도 합니다','배송지는 실제 현행 도로명주소로 재확인합니다'),
('지역 탐색 UX','긴 지역 목록은 사용자에게 선택 부담을 줄 수 있습니다','광역·기초·상세 단계의 탐색과 검색을 구분합니다'),
('지역 표시 정확성','동 이름만으로 병원의 실제 소재지를 확정할 수 없습니다','하위 지역명은 안내 후보이며 실재 시설 목록이 아니라는 점을 명확히 합니다')]
FAQS={
'병원':[
('병원 개업화분과 개원축하화분은 다른 상품인가요?','검색할 때 자주 함께 쓰는 표현입니다. 실물 선택은 식물 종류·크기·화기·리본 구성과 받는 장소 기준으로 상담하세요.'),
('병원 개원식이 아직 확정되지 않았어도 주문 상담이 되나요?','가능한 일정과 주소를 먼저 정리해 문의할 수 있습니다. 실제 제작·배송 확정은 판매처 안내에 따릅니다.'),
('원장님 성함 대신 병원 이름으로 리본을 써도 되나요?','기관명으로 받는 분을 표시하는 방식도 검토할 수 있습니다. 주문 전 공식 상호 표기를 확인해 주세요.'),
('병원 접수대 앞에 놓을 큰 화분을 주문할 수 있나요?','비치할 바닥 면적과 통로 폭을 확인한 뒤 알맞은 크기와 실제 공급 가능 여부를 상담하세요.'),
('병원 개원식 당일 배송 시간을 지정할 수 있나요?','희망 시간은 전달할 수 있지만 가능 시간과 도착 보장은 실제 상담 결과로 확인해야 합니다.'),
('병원 주소를 몰라도 상호로 찾을 수 있나요?','검색된 상호가 유사한 다른 병원일 수 있으므로 도로명주소·건물명·층수를 직접 재확인하는 편이 안전합니다.'),
('리본에 축 개업과 축 개원 중 어느 문구가 좋을까요?','의료기관 개원 축하 목적이라면 축 개원을 자주 사용하지만 수령처나 발신자의 선호가 우선입니다.'),
('병원 이전을 축하할 때도 개원화분을 보내나요?','이전 축하 선물로 화분을 선택할 수 있습니다. 리본 문구는 실제 상황에 맞춰 조정하세요.'),
('원장실로 직접 전달할 수 있나요?','직접 전달 가능 여부는 해당 병원의 출입 방식과 수령 담당자 협의에 따라 달라집니다.'),
('진료시간 외에도 병원에서 화분을 받을 수 있나요?','진료시간과 실제 건물 출입 가능 시간이 다를 수 있어 병원 담당자 확인이 필요합니다.'),
('배송 완료 사진을 받을 수 있나요?','사진이나 문자 안내 제공 여부는 판매처의 실제 서비스 범위에 따라 다르므로 주문 전에 확인하세요.'),
('큰 화분이 병원 개원 선물로 더 좋은가요?','크기보다 안전한 배치 공간, 관리 가능 여부와 받는 분 취향이 중요합니다.'),
('병원 대기실에 어울리는 화분은 무엇인가요?','채광·폭·환기와 관리 여건을 알려주면 가능한 품종을 구체적으로 상담할 수 있습니다.'),
('개원식이 지난 뒤에도 축하화분을 보낼 수 있나요?','늦은 축하도 의미가 있습니다. 현재 수령 가능한 날짜와 시간을 다시 확인하세요.'),
('병원명이 긴데 리본에 모두 적을 수 있나요?','리본 규격에 따라 글자 크기가 달라질 수 있으니 원문을 전달하고 가독성을 상담하세요.'),
('회사 이름으로 병원 개원 선물을 보내려면?','발신자 상호·받는 병원명·주소·수령 연락처·희망일을 준비해 전화 상담하면 됩니다.'),
('의료기관에 향이 있는 식물은 피해야 하나요?','의료기관마다 방침과 방문자의 선호가 다르므로 향·꽃가루 우려가 있는지 확인한 뒤 상담하세요.'),
('화분 관리 방법도 문의할 수 있나요?','선택한 품종과 화기별로 채광·물주기·배수 조건을 주문 시 확인하는 것이 좋습니다.'),
('병원 개원 축하 리본 발신자는 어떻게 표기하나요?','개인명 또는 업체·단체명을 정확하게 적고 직함과 띄어쓰기를 최종 확인하세요.'),
('안산시 병원 개원화분 주문 전에 무엇이 필요한가요?','정확한 안산시 내 배송지, 희망일, 받는 분, 리본 문구, 예산을 준비해 전화 1844-0644로 문의하세요.')],
'치과':[
('치과 개업화분과 개원축하화분을 함께 검색해도 되나요?','둘 다 개원 축하 선물 문맥에서 사용되지만 실제 상품은 화분 규격과 배송 조건을 확인해 선택하세요.'),
('치과의원 명칭과 치과병원 명칭을 바꿔 써도 되나요?','정식 상호 구분이 중요하므로 리본 제작 전에 실제 간판이나 수령처의 표기를 확인하세요.'),
('치과 접수대에 두는 작은 화분도 가능한가요?','탁상용 제품은 접수대의 사용 가능한 면적과 실제 공급 옵션을 확인해 상담할 수 있습니다.'),
('치과 개원식 당일에 맞춰 받을 수 있나요?','실제 배송 가능 일시와 수령 담당자를 확인해야 하며 미확인 상태에서 도착을 보장하지 않습니다.'),
('치과 진료실 안까지 화분을 넣을 수 있나요?','의료 장비와 직원 동선에 영향을 줄 수 있으므로 진료 공간 외 수령 장소를 우선 협의하세요.'),
('공동 원장 치과는 리본에 누구 이름을 적나요?','개인명을 모두 적거나 치과 상호를 쓰는 방법이 있습니다. 실제 수신자 표기를 먼저 결정하세요.'),
('치과 이전개원 축하는 어떤 문구가 자연스럽나요?','상황에 따라 축 이전 또는 새로운 출발을 축하하는 문구를 선택할 수 있습니다.'),
('치과 대기실이 어두워도 화분을 둘 수 있나요?','식물마다 필요한 빛과 관리 조건이 달라 실제 실내 환경에 맞는 선택이 필요합니다.'),
('치과에 향이 강한 꽃장식을 피해야 할까요?','선호와 실내 운영 방침이 다르므로 향이 부담될지 수령처에 미리 확인하세요.'),
('치과 건물에 엘리베이터가 없으면 어떻게 하나요?','층수·계단 폭·제품 크기를 알려주고 운반 가능 여부와 비용을 직접 상담하세요.'),
('치과 예약 접수 중에 배송해도 되나요?','직원 응대가 집중되는 시간일 수 있으므로 실제 인계가 편한 시간대를 협의하세요.'),
('치과 화분은 무조건 흰색 화기가 좋나요?','실내 가구·벽 색과 선호에 따라 화기 선택이 달라집니다. 일률적인 정답은 없습니다.'),
('치과 개원화분 가격은 얼마인가요?','상품 종류·규격·화기·배송 조건에 따라 다를 수 있습니다. 현재 총액은 전화로 확인하세요.'),
('치과 개원 후 며칠이 지나도 선물이 괜찮나요?','개원 직후가 아니어도 축하 선물로 전달할 수 있습니다. 수령 가능한 날짜를 문의하세요.'),
('치과 개원 화분의 리본 문구를 바꿀 수 있나요?','리본 제작 전에는 수정 상담을 할 수 있지만 실제 가능 범위는 제작 단계에 따라 달라집니다.'),
('치과 상호만으로 주소를 확정해도 되나요?','비슷한 이름의 치과가 있을 수 있으므로 도로명주소·층수·연락처를 다시 확인하세요.'),
('치과 개원 축하 화분에 식물 관리 안내가 있나요?','제공 여부는 판매처 정책에 따라 다릅니다. 필요한 품종 관리법을 주문 시 요청하세요.'),
('치과 배송 완료를 문자로 확인할 수 있나요?','판매처의 제공 범위를 주문 전에 확인해야 합니다. 제공 여부를 미리 약속하지 않습니다.'),
('단체에서 치과에 축하화분을 보내려면 무엇이 필요하나요?','수신 치과명·주소·희망일·발신 단체명·예산을 정리해 전화 상담하세요.'),
('안산시 치과 개원축하화분은 어디로 연락하나요?','꽃이랑 전화 1844-0644로 배송지와 일정, 리본 문구를 알려주고 주문 가능 여부를 확인하세요.')],
'한의원':[
('한의원 개업화분과 개원축하화분은 어떻게 고르나요?','검색 표현은 비슷하게 쓰이지만 실제 선물은 비치 공간과 식물 종류를 기준으로 비교하세요.'),
('한의원 상호에 한자를 써도 되나요?','정확한 한자 원문과 리본 제작 가능 여부를 함께 확인해야 합니다.'),
('한의원 개원 행사일과 배송일을 달리할 수 있나요?','수령처가 가능한 일시를 확인한 뒤 실제 배송 가능 일정으로 상담하세요.'),
('한의원 대기실에 큰 화분을 놓아도 될까요?','통로와 대기석 동선을 방해하지 않는지 공간을 보고 결정하는 것이 좋습니다.'),
('한의원 원목 인테리어에 어울리는 화분은?','식물 잎 모양과 화기 색감·크기를 함께 보고 취향에 맞춰 선택하세요.'),
('한약장 주변에도 화분을 놓을 수 있나요?','약재 보관과 업무 동선을 방해하지 않을 공간인지 수령처에 확인해야 합니다.'),
('한의원 이전 축하도 개원화분으로 주문하나요?','이전 축하 선물로 관엽 화분을 선택할 수 있습니다. 실제 이전 여부에 맞게 리본을 작성하세요.'),
('한의원 개원식 때 원장님이 부재중이면?','직원 인계가 가능한지, 대체 연락처가 있는지 먼저 협의하세요.'),
('한의원 화분의 수령 장소를 복도로 잡아도 되나요?','출입·통행을 방해할 수 있으므로 동의된 지정 장소로 인계하는 것이 안전합니다.'),
('햇빛이 적은 한의원 내부에는 어떤 화분이 좋은가요?','실내 채광·환기와 관리 가능성을 알려주고 적합한 식물 종류를 상담하세요.'),
('한의원 리본에 축 개원 대신 다른 표현을 써도 되나요?','축하 목적에 맞는 짧은 문구라면 선택할 수 있습니다. 제작 전 정확한 원문을 확인하세요.'),
('한의원 개원화분은 당일 배송이 되나요?','가능 여부는 실제 주소·재고·배송 일정에 따라 달라집니다. 사전 확인 없이 보장하지 않습니다.'),
('한의원 화분의 받침도 함께 확인해야 하나요?','실내 바닥이나 원목 가구를 보호하려면 화기와 배수 방식에 맞는 받침을 상담하세요.'),
('한의원 개원 축하화분 가격은?','화분 종류·크기와 배송 조건에 따라 달라질 수 있으니 총액을 전화로 확인하세요.'),
('한의원 선물을 보내는 업체 이름을 리본에 써도 되나요?','발신 업체의 정확한 상호와 표기 길이를 확인해 주문할 수 있습니다.'),
('한의원 개원식이 지나도 축하 선물을 보내도 될까요?','개원 이후에도 응원 선물로 전달할 수 있습니다. 최근 수령 가능 일정을 확인하세요.'),
('한의원 실내 식물은 물을 얼마나 줘야 하나요?','식물 품종·계절·실내 조건별로 달라 구매한 화분에 맞는 관리법을 확인해야 합니다.'),
('한의원 개원축하화분 배송 사진도 받을 수 있나요?','사진 제공 여부는 주문 전 실제 서비스 범위 확인이 필요합니다.'),
('가족이 한의원에 화분을 보낼 때 리본은 어떻게 쓰나요?','축하 문구와 발신자 이름을 간결히 적되 수령자가 원하는 호칭을 확인하세요.'),
('안산시 한의원 개원축하화분 주문은 어떻게 하나요?','배송지·희망일·예산·리본 문구를 준비하고 꽃이랑 1844-0644로 전화해 가능 여부를 확인하세요.')]
}

records=[]
def add(cat,topic,title,body,**kw):
    text=' '.join(body.split())
    # Correct omitted sentence boundaries when combining curated source clauses.
    text=re.sub(r'(습니다|합니다|됩니다|주세요|세요|예요|인가요|있나요|없나요)(?=\s+[가-힣])',r'\1.',text)
    assert text and 26<=len(text)<=520, (cat,topic,len(text))
    records.append({'id':f'CF-{len(records)+1:04d}','category':cat,'topic':topic,'title':title,'body':text,**kw})

angles=['상황 판단','주문 준비','주의사항','전화 상담','상품 선택 기준']
for category,items in [('병원 특화',hospital),('치과 특화',dental),('한의원 특화',oriental)]:
    assert len(items)==20,(category,len(items))
    for theme,situation,check,avoid,question in items:
        contexts=[
            f'{situation} {check} 상황에 맞지 않는 선물보다 받는 곳의 실제 여건을 먼저 살펴보는 편이 좋습니다.',
            f'{theme} 관련 주문을 준비한다면 {check} 화분 종류나 가격을 정하기 전에 이 항목을 정리하면 상담이 수월해집니다.',
            f'{avoid} {situation} 실제 배송 가능 여부와 상품 구성은 주문 시 다시 확인해야 합니다.',
            f'{question} {check} 상담이 필요한 경우 꽃이랑 1844-0644로 문의해 배송지와 날짜를 함께 알려주세요.',
            f'{situation} {check} {avoid} 크기와 관리 난도는 판매 가능한 제품 범위에서 비교해 결정하세요.'
        ]
        for a,b in zip(angles,contexts):add(category,theme,f'{theme} · {a}',b,angle=a,scope='업종 안내',factStatus='일반적 주문 안내')
assert len(records)==300

common_angles=['기본 안내','준비 절차','피해야 할 오해','상담 체크']
for topic,cases in COMMON.items():
    assert len(cases)==10,(topic,len(cases))
    for detail,context,check,avoid in cases:
        variants=[
            f'{context} {check} 지역명과 업종이 같아도 실제 수령처의 조건을 따로 확인해야 합니다.',
            f'{detail} 항목은 전화 주문 전에 확인해둘 만합니다. {check} 화분 종류와 배송 일정을 정할 때 이 정보를 함께 전달하세요.',
            f'{avoid} {context} 확인되지 않은 조건을 확정 안내로 표시하지 않는 것이 좋습니다.',
            f'{check} {avoid} 원하는 조건을 정리한 뒤 꽃이랑 1844-0644로 현재 가능한 선택지를 문의하세요.'
        ]
        for angle,body in zip(common_angles,variants):add('공통 실무',topic,f'{detail} · {angle}',body,subtopic=detail,angle=angle,factStatus='일반적 주문 안내')
assert len(records)==620
hub_angles=['지역명 선택','주소 확인','탐색 방법','발행 주의']
for name,context,check in HUB_TOPICS:
    variants=[
      f'{context} {check} 지역 이름은 배송 가능 여부를 보장하는 표기가 아니라 주소를 찾는 출발점입니다.',
      f'{name} 안내는 현행 행정주소와의 일치 확인이 필요합니다. {check} 주문 전 상세 주소 확인을 먼저 권합니다.',
      f'{context} {check} 특히 동명이 여러 곳에 있을 경우 시·군·구와 시·도를 함께 표시하는 편이 안전합니다.',
      f'{check} 지역 원장의 검증되지 않은 후보를 실제 행정구역이나 의료기관의 존재 근거처럼 사용하지 않습니다.'
    ]
    for angle,body in zip(hub_angles,variants):add('지역 허브',name,f'{name} · {angle}',body,angle=angle,factStatus='실제 지역 존재 검증 별도')
assert len(records)==660
for cat,qa in FAQS.items():
    assert len(qa)==20,(cat,len(qa))
    for q,answer in qa:
        # FAQ Q and A are one usable block
        add('업종 FAQ',cat,q,answer,question=q,answer=answer,industry=cat,factStatus='전화 상담 조건 안내')
assert len(records)==720
assert len({r['id'] for r in records})==720
assert len({r['body'] for r in records})==720
assert len({r['title'] for r in records})==720, [v for v,n in Counter(r['title'] for r in records).items() if n>1][:10]
assert Counter(r['category'] for r in records)=={'병원 특화':100,'치과 특화':100,'한의원 특화':100,'공통 실무':320,'지역 허브':40,'업종 FAQ':60}
# A word-for-word title collision is an error. Avoid nearly identical repeated copy per page.
pool={'project':'Clinicflower','version':'sample-2026-11-04','brand':'꽃이랑','phone':'1844-0644',
    'policy':{'noUnverifiedPrices':True,'noUnverifiedDeliveryGuarantee':True,'noFakeLocalOffices':True,
    'noUserDataCollection':True,'sampleOnly':True,'populationSimilarityAuditDone':False,
    'selection':'sha256(regionCode + regionName + pageType + topic + sourceVersion) deterministic, no duplicate ID on one page'},
    'plannedCategoryCounts':{'병원 특화':100,'치과 특화':100,'한의원 특화':100,'공통 실무':320,'지역 허브':40,'업종 FAQ':60},
    'blocks':records}
(ROOT/'clinicflower-copy-pool-720.json').write_text(json.dumps(pool,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

provenance=[]
for dest,(src,genid,role,alt) in IMAGE_MAP.items():
    old=IMAGES/src; assert old.is_file(),old
    image=Image.open(old).convert('RGB')
    width,height=image.size
    out=ROOT/'assets/images'/dest
    # Full-resolution originals -> independent webp, never upscale.
    image.save(out,format='WEBP',quality=81,method=6)
    provenance.append({'assetPath':f'assets/images/{dest}','role':role,
      'sourceType':'GENERATION_EVIDENCE_PARTIAL',
      'tool':'image_gen.text2im','toolResultRef':genid,
      'toolPromptVerbatim':PROMPTS[dest],
      'userRequestText':'네가 새로 이미지 제작해서 페이지 제작하는데 사용해',
      'generatedAt':None,'generationTimeEvidence':'Not supplied by image tool; no invented timestamp',
      'originalFilename':src,'originalSha256':hashlib.sha256(old.read_bytes()).hexdigest(),
      'originalArchiveLocation':str(old),
      'transformations':[{'type':'PNG to WebP','library':'Pillow','quality':81,'method':6,'upscaled':False}],
      'finalSha256':hashlib.sha256(out.read_bytes()).hexdigest(),
      'finalBytes':out.stat().st_size,'width':width,'height':height,
      'depictedFactRole':'illustration','alt':alt,
      'releaseStatus':'preview only; production asset provenance gate not yet cleared'})
(ROOT/'image-provenance.json').write_text(json.dumps({'project':'clinicflower','assets':provenance},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# A sample uses actual, individually authored, on-page copy + representative pool IDs.
# SEO preview is noindex and has no canonical, no sitemap/indexnow key.
get=lambda i:next(r for r in records if r['id']==f'CF-{i:04d}')
sel=[get(x) for x in [1,27,46,102,132,185,205,247,289,304,356,412,468,527,590,668,687,708]]
assert len({s['id'] for s in sel})==len(sel)

css=r'''/* No external font dependency; use device Korean system font */
:root{--ink:#172b27;--muted:#576963;--forest:#124a3a;--forest2:#1f6c54;--cream:#f8f6ef;--pale:#eef5ec;--line:#e1e7e0;--sand:#e9deca;--pink:#b48083}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#fff;font-family:'Noto Sans KR',system-ui,-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.75;word-break:keep-all}a{color:inherit}img{max-width:100%;display:block}button,a{-webkit-tap-highlight-color:transparent}a:focus-visible,summary:focus-visible{outline:3px solid #eab04a;outline-offset:3px}
.wrap{width:min(1160px,calc(100% - 44px));margin:auto}.notice{background:#173d31;color:#f0f6ef;font-size:13px;text-align:center;padding:8px 16px}.top{background:white;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20;box-shadow:0 2px 16px #112e2110}.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:76px}.brand{font-size:26px;letter-spacing:-1.3px;font-weight:800;color:var(--forest);text-decoration:none}.brand small{display:block;font-size:11px;letter-spacing:0;color:var(--muted);font-weight:500;margin-top:-6px}.topnav{display:flex;align-items:center;gap:24px;font-size:14px}.topnav a{text-decoration:none;font-weight:600}.call{border:0;background:var(--forest);color:white!important;display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:13px 23px;border-radius:10px;text-decoration:none;font-weight:800;box-shadow:0 5px 12px #123e2b24;min-height:50px}.call:hover{background:var(--forest2)}.top .call{border-radius:50px;padding:11px 18px;font-size:14px}
.hero{min-height:560px;background:#f5eee5 url('images/hero.webp') center center /cover no-repeat;display:flex;align-items:center;position:relative}.hero:before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,#faf8f1f7 0%,#faf8f1ed 34%,#faf8f193 54%,transparent 79%)}.hero .wrap{position:relative;z-index:1}.heroContent{max-width:630px;padding:60px 0 72px}.eyebrow{color:var(--forest2);font-weight:800;letter-spacing:1.4px;font-size:12px;text-transform:uppercase}.hero h1{font-size:clamp(32px,3.9vw,58px);line-height:1.28;letter-spacing:-2.9px;margin:18px 0 20px;font-weight:800}.hero h1 strong{color:var(--forest)}.hero p{font-size:18px;max-width:560px;margin:0 0 27px;color:#3d4a45}.heroAction{display:flex;align-items:center;gap:20px;flex-wrap:wrap}.call.heroCall{font-size:19px;padding:16px 27px}.heroAction span{font-size:13px;color:#475c4e;max-width:180px}.heroNote{font-size:12px;color:#617367;margin-top:18px}
.section{padding:88px 0}.section.alt{background:#f5f7f3}.heading{margin-bottom:35px;max-width:740px}.heading h2{font-size:clamp(28px,2.9vw,40px);line-height:1.35;letter-spacing:-1.5px;margin:12px 0}.heading p{color:var(--muted);font-size:17px;margin:0}.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.service{overflow:hidden;background:white;border:1px solid var(--line);border-radius:20px;box-shadow:0 12px 35px #173b2810}.service img{width:100%;aspect-ratio:4/3;object-fit:cover}.service .content{padding:25px}.service h3{font-size:23px;letter-spacing:-.7px;margin:0 0 12px}.service p{margin:0 0 17px;color:#526359}.miniCall{display:inline-block;font-weight:800;text-decoration:underline;text-underline-offset:4px;color:var(--forest)}.aside{margin-top:20px;font-size:12px;color:#6b776f}
.banner{border-radius:25px;overflow:hidden;background:var(--forest);color:white;display:grid;grid-template-columns:1fr 1fr;align-items:stretch}.banner .btext{padding:56px 50px;display:flex;flex-direction:column;align-items:flex-start;justify-content:center}.banner h2{font-size:34px;line-height:1.4;letter-spacing:-1.5px;margin:6px 0 15px}.banner p{color:#d9ebe1;margin:0 0 24px}.banner .call{background:white;color:var(--forest)!important}.banner img{width:100%;height:100%;object-fit:cover;min-height:350px}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.step{border:1px solid var(--line);border-radius:18px;padding:24px;background:#fff}.step .num{display:inline-block;background:#e3f0e7;color:var(--forest);border-radius:8px;padding:3px 9px;font-weight:800;font-size:12px}.step h3{font-size:20px;margin:12px 0 8px}.step p{font-size:15px;color:var(--muted);margin:0}.checklist{background:#fff;border-radius:20px;border:1px solid var(--line);display:grid;grid-template-columns:repeat(2,1fr);gap:0;overflow:hidden}.checklist div{padding:20px 25px;border-bottom:1px solid var(--line)}.checklist div:nth-child(odd){border-right:1px solid var(--line)}.checklist div:nth-last-child(-n+2){border-bottom:0}.checklist strong{color:var(--forest);display:block;margin-bottom:4px}.checklist span{color:var(--muted);font-size:14px}
.faq{max-width:850px}.faq details{border-bottom:1px solid var(--line);padding:20px 8px}.faq summary{cursor:pointer;font-size:17px;font-weight:700;padding-right:24px;list-style:none;position:relative}.faq summary:after{content:'+';font-size:25px;position:absolute;right:0;top:-5px;color:var(--forest)}.faq details[open] summary:after{content:'−'}.faq p{color:var(--muted);margin:12px 0 2px;font-size:15px}.bottom{background:var(--cream);padding:70px 0}.footCall{text-align:center}.footCall h2{font-size:35px;margin:0 0 10px}.footCall p{color:var(--muted);margin:0 0 24px}.footCall .call{font-size:19px}.footer{background:#152c26;color:#cad9d1;padding:34px 0;font-size:13px}.footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}.footer strong{color:white}.mobileCall{display:none}
@media(max-width:900px){.topnav .jump{display:none}.grid3{gap:14px}.service .content{padding:19px}.service h3{font-size:19px}.steps{grid-template-columns:repeat(2,1fr)}.banner .btext{padding:30px}}
@media(max-width:640px){body{padding-bottom:75px}.wrap{width:min(100% - 32px,560px)}.notice{font-size:11px}.top .wrap{min-height:64px}.brand{font-size:23px}.top .call{padding:8px 12px;font-size:12px;min-height:38px}.hero{min-height:600px;align-items:flex-start;background-position:58% 100%}.hero:before{background:linear-gradient(180deg,#faf8f2 0%,#faf8f2ed 45%,#faf8f2c4 67%,#faf8f235 95%)}.heroContent{padding:45px 0 33px;max-width:100%}.hero h1{font-size:35px;letter-spacing:-1.7px;line-height:1.3}.hero p{font-size:15px;max-width:95%}.heroAction{gap:10px}.call.heroCall{font-size:16px;padding:13px 19px}.heroNote{font-size:11px}.section{padding:61px 0}.heading h2{font-size:29px}.heading p{font-size:15px}.grid3{grid-template-columns:1fr;gap:18px}.service img{aspect-ratio:16/9;object-position:center 47%}.service h3{font-size:21px}.banner{grid-template-columns:1fr}.banner .btext{padding:29px 26px}.banner h2{font-size:26px}.banner img{max-height:250px;min-height:200px}.steps{grid-template-columns:1fr 1fr;gap:10px}.step{padding:16px}.step h3{font-size:16px}.step p{font-size:13px}.checklist{grid-template-columns:1fr}.checklist div{border-right:0!important;border-bottom:1px solid var(--line)!important}.checklist div:last-child{border-bottom:0!important}.footCall h2{font-size:26px}.footer{padding:28px 0}.mobileCall{display:flex;position:fixed;z-index:30;bottom:0;left:0;width:100%;height:72px;background:#fff;padding:9px 15px;box-shadow:0 -6px 26px #112c2030;border-top:1px solid #dde3dd}.mobileCall a{width:100%;background:var(--forest);color:white;text-align:center;text-decoration:none;display:flex;align-items:center;justify-content:center;border-radius:13px;font-weight:800;font-size:17px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}'''
(ROOT/'assets/style.css').write_text(css+'\n',encoding='utf-8')

T='안산시 병원·치과·한의원 개업화분, 개원축하화분 | 꽃이랑'
H=lambda t:html.escape(t,quote=True)
faqHTML='\n'.join('<details><summary>'+H(q)+'</summary><p>'+H(a)+'</p></details>' for q,a in [
('개업화분과 개원축하화분은 별도 상품인가요?','병원·치과·한의원 개원 축하라는 같은 목적에서 함께 사용되는 검색 표현입니다. 실제 주문은 식물 종류, 크기, 리본과 배송지 조건을 기준으로 상담합니다.'),
('안산시 어느 지역까지 배송되나요?','배송 가능 여부와 배송비는 실제 도로명주소, 날짜 및 상품에 따라 달라질 수 있습니다. 전화로 상세 주소를 알려주시면 확인할 사항을 안내받을 수 있습니다.'),
('리본에는 어떤 문구를 쓰면 좋을까요?','축 개원, 개원을 축하드립니다 등의 표현을 참고할 수 있습니다. 보내는 분 이름과 의료기관 정식 명칭은 리본 제작 전에 정확히 확인합니다.'),
('개원식 당일 배송을 확정할 수 있나요?','희망일과 시간은 전달할 수 있지만 실제 가능 여부와 정확한 배송 조건은 전화 상담 후 확인해야 합니다.'),
('홈페이지의 사진과 똑같은 화분이 배송되나요?','이 페이지의 이미지는 AI가 제작한 상황 연출 이미지로 실물 판매상품 사진이 아닙니다. 실제 가능한 품종, 크기, 화기와 리본 디자인은 전화 상담에서 확인해주세요.'),
('전화 주문 전 무엇을 준비하면 되나요?','의료기관 명칭, 정확한 주소와 층수, 수령 가능 일시, 연락처, 예산, 리본 문구를 준비하면 상담이 수월합니다.')
])
# Showcase nine real pool records, without inventing local facility facts.
TIP_IDS=(1,185,205,304,468,527)
TIP_HTML='\n'.join('<article class="step"><span class="num">'+H(get(i)['category'])+'</span><h3>'+H(get(i)['title'].split(' · ')[0])+'</h3><p>'+H(get(i)['body'])+'</p></article>' for i in TIP_IDS)
FAQ_POOL_IDS=(668,687,708)
faqHTML+='\n'+'\n'.join('<details><summary>'+H(get(i)['question'])+'</summary><p>'+H(get(i)['answer'])+'</p></details>' for i in FAQ_POOL_IDS)
PAGE=f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{H(T)}</title><meta name="description" content="안산시 병원·치과·한의원 개업화분, 개원축하화분 전화 주문 안내. 배송지·행사일·예산·리본 문구 확인 후 꽃이랑 1844-0644로 상담하세요.">
<meta name="robots" content="noindex,nofollow,noarchive"><meta name="theme-color" content="#124a3a">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<div class="notice">이 페이지는 상품·배송 내용 검수용 샘플입니다. 지역별 배송 가능 여부는 전화로 확인해주세요.</div>
<header class="top"><div class="wrap"><a class="brand" href="#top" aria-label="꽃이랑 샘플페이지 맨 위로">꽃이랑<small>개원 축하 화분 상담</small></a><nav class="topnav" aria-label="주요 메뉴"><a href="#types" class="jump">업종별 안내</a><a href="#order" class="jump">전화 주문 방법</a><a href="#faq" class="jump">자주 묻는 질문</a><a class="call" href="tel:1844-0644" aria-label="1844-0644 전화 상담">☎ 전화주문</a></nav></div></header>
<main id="top">
<section class="hero" aria-labelledby="hero-title"><div class="wrap"><div class="heroContent"><span class="eyebrow">ANSAN · CLINIC OPENING GIFT</span><h1 id="hero-title">안산시<br><strong>병원·치과·한의원</strong><br>개업화분 · 개원축하화분</h1><p>새로운 시작을 축하하는 식물 선물. 받는 공간, 축하 일정, 리본 문구와 예산을 정리해 전화로 상담하세요.</p><div class="heroAction"><a class="call heroCall" href="tel:1844-0644" aria-label="1844-0644로 전화 주문 상담">☎ 전화주문 1844-0644</a><span>배송 가능 지역·상품·가격은 상담 시 확인</span></div><p class="heroNote">* 사진은 AI로 제작한 개원 축하 연출 이미지이며, 실제 판매·배송 사례가 아닙니다.</p></div></div></section>
<section class="section" id="types"><div class="wrap"><div class="heading"><span class="eyebrow">THE RIGHT GIFT FOR THE SPACE</span><h2>개원하는 공간에 맞춰<br>축하화분을 고르세요</h2><p>업종마다 공간과 수령 방식이 다를 수 있어, 주문 전에 필요한 정보를 먼저 확인합니다.</p></div><div class="grid3">
<article class="service"><img src="assets/images/hospital.webp" width="1448" height="1086" loading="lazy" alt="병원 접수대 옆 축하화분을 표현한 AI 연출 이미지"><div class="content"><h3>병원 개원축하화분</h3><p>접수대·대기실의 통로 폭, 직원 수령 시간과 정확한 병원명을 확인하면 화분 크기와 리본 문구를 상담하기 편합니다.</p><a class="miniCall" href="tel:1844-0644">병원 개원화분 전화 상담 ↗</a></div></article>
<article class="service"><img src="assets/images/dental.webp" width="1448" height="1086" loading="lazy" alt="치과 대기실의 개원 축하 화분을 표현한 AI 연출 이미지"><div class="content"><h3>치과 개원축하화분</h3><p>치과의원 정식 명칭과 층수, 접수대 주변 공간을 먼저 확인하세요. 화분을 둘 위치와 관리 여건도 함께 고려합니다.</p><a class="miniCall" href="tel:1844-0644">치과 개원화분 전화 상담 ↗</a></div></article>
<article class="service"><img src="assets/images/oriental.webp" width="1448" height="1086" loading="lazy" alt="한의원 원목 인테리어와 축하화분을 표현한 AI 연출 이미지"><div class="content"><h3>한의원 개원축하화분</h3><p>원목 인테리어·대기 공간과 어울리는 색감뿐 아니라 채광, 화기, 받는 분의 정확한 이름을 확인해 선택합니다.</p><a class="miniCall" href="tel:1844-0644">한의원 개원화분 전화 상담 ↗</a></div></article>
</div><p class="aside">* 업종별 이미지는 실제 납품 상품·고객 사례가 아닌 AI 연출 예시입니다. 이미지 안 리본 글자는 주문에 사용되는 확정 문구가 아닙니다.</p></div></section>
<section class="section alt" id="order"><div class="wrap"><div class="heading"><span class="eyebrow">CALL & ORDER</span><h2>전화로 간편하게 주문 조건 확인</h2><p>쇼핑몰에서 제품을 일일이 고르지 않아도 됩니다. 먼저 필요한 정보를 알려주세요.</p></div><div class="steps"><div class="step"><span class="num">01</span><h3>배송지 확인</h3><p>안산시 내 도로명주소, 건물명, 층·호수, 수령처 연락처</p></div><div class="step"><span class="num">02</span><h3>날짜와 예산</h3><p>개원식과 실제 수령 가능일, 희망 예산·화분 크기</p></div><div class="step"><span class="num">03</span><h3>리본 문구</h3><p>받는 의료기관명, 축하 문구와 보내는 사람 이름</p></div><div class="step"><span class="num">04</span><h3>전화 상담</h3><p>실제 상품과 가격·배송 가능 여부를 확인해 주문 결정</p></div></div>
<div class="banner" style="margin-top:32px"><div class="btext"><span class="eyebrow" style="color:#c7e3d4">PHONE ORDER</span><h2>개원 축하화분 주문은<br>전화로 상담하세요</h2><p>병원·치과·한의원 개업화분, 개원축하화분. 상품과 정확한 배송 조건은 상담 시 확인합니다.</p><a class="call" href="tel:1844-0644">☎ 1844-0644 전화 연결</a></div><img src="assets/images/phone.webp" width="1672" height="941" loading="lazy" alt="화분 준비와 전화 상담을 나타내는 AI 연출 이미지"></div></div></section>
<section class="section" id="tips"><div class="wrap"><div class="heading"><span class="eyebrow">PRACTICAL GUIDE</span><h2>개원화분 선택 시 실무 팁</h2><p>지역·업종별 문구 POOL에서 선별한 상담 안내입니다. 실제 조건은 주문 전 확인해야 합니다.</p></div><div class="grid3">{TIP_HTML}</div></div></section>\n<section class="section" id="check"><div class="wrap"><div class="heading"><span class="eyebrow">ORDER CHECKLIST</span><h2>주문 전에 확인하면 좋은 내용</h2><p>개원식이 지나치게 바쁘거나 수령처가 부재중이라면 화분 전달에 어려움이 생길 수 있습니다.</p></div><div class="checklist"><div><strong>정확한 의료기관명</strong><span>동일·유사한 병원명과 치과·한의원 이름을 혼동하지 않도록 확인</span></div><div><strong>받는 주소와 층수</strong><span>도로명주소, 건물명, 층·호수를 함께 정리</span></div><div><strong>개원식과 수령 날짜</strong><span>행사일과 실제 인계 가능 시간이 다른지 확인</span></div><div><strong>리본 문구와 발신자</strong><span>축 개원·축 개업·이전 축하 등 실제 목적에 맞게 작성</span></div><div><strong>식물 관리 환경</strong><span>대기실·접수대의 채광과 통로 크기 고려</span></div><div><strong>최종 금액과 가능 여부</strong><span>화분·화기·리본·배송비 포함 조건을 상담에서 확인</span></div></div></div></section>
<section class="section alt" id="faq"><div class="wrap"><div class="heading"><span class="eyebrow">FAQ</span><h2>개원축하화분 자주 묻는 질문</h2><p>전화 주문 전에 많이 확인하는 항목을 정리했습니다.</p></div><div class="faq">{faqHTML}</div></div></section>
<section class="bottom"><div class="wrap footCall"><span class="eyebrow">A THOUGHTFUL OPENING GIFT</span><h2>새 출발을 축하하는 마음,<br>꽃이랑에 전화로 문의하세요</h2><p>안산시 병원·치과·한의원 개업화분 · 개원축하화분</p><a class="call" href="tel:1844-0644" aria-label="꽃이랑 1844-0644 전화 걸기">☎ 1844-0644 전화 주문 상담</a></div></section>
</main><footer class="footer"><div class="wrap"><span><strong>꽃이랑</strong> · 개원 축하화분 상담 안내 · 1844-0644</span><span>AI 연출 이미지 사용 · 의료기관 실제 배송 실적 아님 · 배송 가능 여부는 전화 확인</span></div></footer>
<div class="mobileCall"><a href="tel:1844-0644" aria-label="전화주문 1844-0644">☎ 전화주문 · 1844-0644</a></div>
</body></html>'''
(ROOT/'index.html').write_text(PAGE,encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')

report={'project':'Clinicflower','site':'안산시 통합 클리닉 개원축하화분 샘플','stage':'noindex preview only','expectedTotal':720,
'actualTotal':len(records),'categories':dict(Counter(x['category'] for x in records)),
'images':[{'file':x['assetPath'],'bytes':x['finalBytes'],'width':x['width'],'height':x['height'],'sha256':x['finalSha256']} for x in provenance],
'phoneLinks':PAGE.count('href="tel:1844-0644"'), 'noindex':True,'containsCanonical':False,
'orderLinks':0,'externalCustomerDataForm':False,'productionProvenanceCleared':False,
'criticalLimits':['대량 5,302개 페이지 생성·유사도 전수 검사 전','원장 1,438개 미검증 보존','운영 Worker 미선정·미배포', 'AI 이미지 생성시각 증빙 없음']}
assert report['phoneLinks']>=7
assert PAGE.count('src="assets/images/')==4 and "url('images/hero.webp')" in css
assert 'href="tel:1844-0644"' in PAGE
(ROOT/'reports/build-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pool':len(records),'categories':report['categories'],'images':[(x['assetPath'],x['finalBytes'],x['width']) for x in provenance],'phoneLinks':report['phoneLinks'],'html_bytes':(ROOT/'index.html').stat().st_size},ensure_ascii=False,indent=2))