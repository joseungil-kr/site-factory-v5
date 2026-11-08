# V5.1 군 시험 사실 소유권 게이트 — 2026-11-08

인수 HEAD c012238e98f1df80a600a47cace118fbda77c9ae. 계실장 독립 검수 청도 /59 88점, 완도 /28 87점. 공통 원인은 반입 조건과 카드 가격의 슬롯 간 의미 반복이다. 개별 문장 땜질 대신 아래 원칙을 적용한다.

## 사실 원장 필수 필드
fact_id, source_url, checked_at(시간대 포함), region_scope, facility_scope(군 전체 또는 특정 시설), product_id, verification_status(confirmed/unconfirmed), fact_type, value. 근거 없는 정보는 생성하지 않는다. 시설 단위 조건을 군 전체로 확대하지 않는다.

## 슬롯 소유권
- intro: 구매 목적만. 반입 제약 및 가격 재진술 금지.
- notice: 확인된 반입 제약 한 번. restricted-rice, restricted-rice-basket 모두 동일 규칙.
- product_card: SKU, 상품명, 표시가격, CTA의 유일한 소유자.
- choice: 카드에서 알 수 없는 검증된 선택 차이만. 없다면 생략.
- order: 장례식장명, 주소, 빈소, 날짜 등 실제 주문 입력 사항.
- faq: 앞 슬롯이 답하지 않은 새로운 질문만. 새 정보가 없으면 생략.
- 각 pool 항목은 fact_ids, customer_question, output_slot에 연결한다. 필요한 한 문장 요약과 불필요한 의미 반복을 구분한다.

## 회귀 게이트
최종 조립 HTML의 fact_id별 슬롯 중복, H1 약속-본문 일치, 상품군/CTA 일치, 사실의 지역·시설 적용범위를 검사한다. 금지문자열 검사만으로 대체하지 않는다. 18개 목적 유형과 제한 유형 모두 검사한다. 홈/14/26/37/95/2/7/60/12/77/78/24/42/86/59/28을 고정 회귀 표본에 포함한다.

작업 순서: 이 지침 선행 커밋 → 사실원장 → pool → 생성기 → 검사기 → 95개 전량 오프라인 재생성 → 전수 기계 검사 → HTML 및 390/1440 화면 검수. 자동 PASS와 작업자 점수는 독립 승인 아님.

시험 브랜치만 변경한다. main, 기존 운영 사이트, Todayflower, 배포, DNS, 보안·인증·권한, 공개, 검색등록 변경 금지.
