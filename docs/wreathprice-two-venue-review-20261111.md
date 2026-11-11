# WreathPrice 시설별 구매 시안 2개 — 격리 후보 독립 검수 (2026-11-11)

## 결과
- 기존 지역 구매 문서 4,935개·원래 고정 50개·운영 URL·리디렉션·배포·robots/index·DNS·Secret·권한 **무변경**
- 격리 새 후보 2개 (고정 50개 외):
  - `sejong-eunhasu` : 은하수공원 장례식장, 세종특별자치시 정안세종로 1527 (산울동 680), 법정동 3611011500
  - `wonju-villa` : 원주 빌라드아모르, 강원특별자치도 원주시 북원로 2888 (태장동), 법정동 5113011200
- 고정 공식 ZIP SHA256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd` 사용, 이전 일반 지역 HTML 각각 추출해 `before.html`에 보존.
- Actions: https://github.com/joseungil-kr/site-factory-v5/actions/runs/43019110059 = completed/success
- Artifact 13853354416, SHA256 `c61ea36b908540d8b8dcdc065b1dda74b8884f9cb2eb9dfb31e3b378a9ce8268`
- 390px·1440px 4개 화면, 이미지 decode 완료 및 픽셀 entropy 약 8.7 이상, horizontal overflow 0, 주문 상세 링크 각각 2개, 폼/구매 전송 0, meta noindex 유지.

## 출처 계층 및 검증 한계
**공식 시설·행정자료:** 세종시설관리공단 시설 소개 https://sjfmc.or.kr/kor/sub04_01_01.do 에 시설명·장례식장 구성·주소가 확인되고, 2020-07-17 공식 공지 https://www.sjfmc.or.kr/jcw/sub05_01/cop/bbs/BBSMSTR_000000000013/selectBoardArticle.do?mno=sub05_01&nttId=4806&pageIndex=8 에 2020-07-15 산울리→산울동 관할 변경이 설명됨. 원주시청 2024-01-16 공식 행사 장소 공지 https://www.wonju.go.kr/www/selectBbsNttView.do?bbsNo=1&nttNo=431172&key=311 에 빌라드아모르/북원로 2888 명시.

**판매처 게시 공지:** https://fwith.co.kr/page/notice.php 의 검색 인덱스 사본(2026-11-11 확인, 게시일/수정일 미상)은 은하수공원 오브제, 빌라드아모르 전날 화환/당일 불가를 게시. 원 URL 직접 열람은 cache miss. **시설 운영자가 현재 똑같이 적용하는지 공식 시설 공지로 확인하지 못함.** 문서에서 판매처의 과거 게시조건과 현재 확정 규칙을 분리.

**상품 SKU 범위:** V4 상품 원장 2026-10-22 B205 근조 특대 3단 109,000원; V5 제품 기록 2026-10-30 C205 축하 특특대 3단 149,000원, C030 축하 2단 오브제 200,000원. 판매처 검색 인덱스 https://fwith.co.kr/shop/item.php?it_id=B205 및 https://fwith.co.kr/shop/item.php?it_id=C030 에 분류·표시가 동일하게 게시됨(원문 직접 열람 cache miss). 실제 결제액, 재고, SKU별 시설 반입 적합성, 배송 가능성, 추가 배송비는 미확인.

## 서로 다른 구매 판단 흐름
- **은하수공원:** 정확한 장례식장과 빈소 확인 → 판매처 과거 오브제 안내 및 현재 시설 반입조건 확인 → *근조용* 오브제에 맞는 SKU 존재 확인. C030은 축하용으로서 근조 오브제 대체 불가; B205 근조 3단은 오브제 적합성 검증 안 됨. 따라서 해당 시설에 적합하다고 증명한 SKU **0개**.
- **빌라드아모르:** 예식일·홀·전날 수령 가능 여부 먼저 확인 → 축하 C205 3단과 C030 2단 오브제의 설치형태 비교 → 시설 최신 반입과 현재 판매처 접수 여부 확인. 2024년 원주시 행사 장소 주소는 시설 자체의 현재 배송 규칙을 뜻하지 않음.

## 실제 HTML 전후 검수
- `qa/wreathprice-venue-2/sejong-eunhasu/before.html` : 일반 산울동 페이지. `index.html` : 은하수공원 구매 목적 전용 후보.
- `qa/wreathprice-venue-2/wonju-villa/before.html` : 일반 태장동 페이지. `index.html` : 빌라드아모르 구매 목적 전용 후보.
- 검증 SHA·구분은 `comparison.json`, 화면 계측은 `screen-evidence.json`; 문장 근거는 `research/wreathprice-venue-pilot/sentence-source-map.json`.
- 현재 시설 운영기관의 공식 화환 반입·배치 정책은 별도로 확인되지 않음. 판매처 공지 내용만 표시하며 현재 정책으로 단정하지 않음.
- 2개 시설은 기존 고정 50개 밖에 있으며 해당 50개 통계·중복 수·색인 적합성 점수를 바꾸지 않음. 검색 공개 합격 **0개** 유지.

## 추가 확보해야 할 자료
- 은하수공원 운영자가 현재 인정하는 근조 오브제 규격·반입장소·접수절차 및 판매처의 일치 SKU, 실제 배송비/날짜.
- 빌라드아모르 운영자의 화환 허용 형태/전날 반입·보관 정책·현재 배송 가능 시간, C205/C030 실제 주소별 적용 비용.
- 공식 시설 담당자 확인이나 주문을 대행하지 않았으며, 해당 정보가 공개 자료로 없을 때 **미확인**으로 유지.
