# Worker6: 실제 유사도 계산 대상 및 대표 구매결정 구성 분석 (2026-11-11)

## 범위 및 증거 수준
- 기준 브랜치 `site/v51-promotion-gift-plants-20261109`, 시작 HEAD `e405b6d2172bb4732f0de89bb68ad2d6804a6e66`.
- 직접 읽은 원격 소스: `v5/audit.py`, `v5/engine.py`, `v5/review_gate.py`, `scripts/worker6_nationwide_inputs.py`, `scripts/worker6_core_five_preview.py`, `scripts/worker6_operator_three_diagnostic.py`, `v5/purpose_render.py`, `scripts/worker6_shipping_render.py`, `sites/promotion-gift-plants/products.json`, `customer-decision-modules-20261109.json`, `site-spec.json`, `site.json`, `illustration-provenance.json`.
- **HTML 산출물 직접 열람 한계:** 이전 감독은 5페이지 및 6지역 artifact와 390px 화면을 직접 읽었고, 이 결과는 인계에 기록됨. 이번 조사에서는 해당 ZIP 바이트를 직접 복호화하여 독립 재계산하지 못했다. 그러므로 이전 감독 관측치와 현재 소스의 조립 규칙을 구분한다. 실제 HTML 신규 생성/재빌드/새 화면점수 없음.

## 49%의 정확한 원본 구현
- `v5/audit.py:grams()`: 공백 제거 + 소문자 변환 후 **고유 문자 5-gram 집합**.
- `similarity()`: 두 집합의 교집합 크기 / 합집합 크기 (Jaccard).
- `all_bodies`: `' '.join([p['intro']] + [x['paragraph'] for x in p['sections']])`; V5.1 `assemble()`로 확정된 본문. 제목, 소제목, FAQ, 상품카드, 가격 카드, 주문링크, 내비게이션, footer, JSON-LD는 이 측정 대상에 포함되지 않음. **본문 단락에 직접 쓴 상품명/가격은 포함됨**.
- 모든 페이지에 대한 완전 동일 본문 SHA-256 중복검사는 별도.
- 페이지 <=300: 모든 페이지 쌍. >300: `searchKeyword`별 정렬/고정 해시로 뽑은 약 1% 표본 간 모든 쌍; 표본 외 쌍은 측정하지 않음.
- 최대값 >=0.49면 오류. `site-spec.json`에도 `thresholdExclusive=0.49`, `sampleFraction=0.01` 기록. 변경 금지.
- `scripts/worker6_operator_three_diagnostic.py`는 `assemble()` 결과의 **소개+소제목+본문**을 별도로 이어 붙여 `similarity()` 계산하므로, 실제 V5 audit의 **소제목 제외 방식과 정확히 동일한 입력이 아니다**. 기존 6지역 90.02~98.55%는 그 진단 스크립트의 관측치이며, 이를 V5 audit 정확 점수로 오인하지 말 것. 지역명 제거 비교도 추가 진단일 뿐 정식 게이트가 아님.
- 5목적 페이지 24.8573% 승진↔영전은 별도 capture 진단의 비교이며, 전국 같은 목적의 지역 쌍을 대표하지 않는다.

## 공통/고유/카드/고지 분해
| 층 | 5목적 대표 생성 | 6지역 동일 목적 생성 | 49% 본문 포함 |
|---|---|---|---|
| 공통 골격 | 페이지 intro + 목적별 required choice/order | 동일 승진 pool + 지역 evidenceSections | 예 |
| 목적별 고유본문 | 승진 직책·관계·문구, 영전 발령일·출근일·이전주소, 일반축하 사유·메시지, 당일 상담 단계 | 모두 **승진** 목적; 목적 차이 없음 | 예 |
| 공통 운영정책 | 단일 `operator_policy()` 전5페이지 | 동일 함수 전6지역 | 예 |
| 수령 유형 | 목적별 수령 질문 | 회사·자택·행사장 질문 동일 | 예 |
| 지역 고유 사실 | 없음 | 배송표 행 상태/금액; 적성면 법정리 원장 등 연구자료는 자동 삽입되지 않음 | evidenceSections만 포함 |
| 검증된 상품 | 6 SKU, 상세 링크 | 동일 6 SKU | 상품카드는 아니오; 선택 비교 단락은 예 |
| 필수 고지 | 반품 출처·개별 도착/요금 확인 | 공통 운영정책·지역 요금 확인 | 단락이면 예 |

실제 동일 단락의 원인: (1) `promotion` pool 전체 공유, (2) 동일 `operator_policy()` 문구, (3) 3개 수령 질문 공유, (4) 같은 상품·가격 비교, (5) 동일 배송표 상태는 evidenceSections도 사실상 동일하며 지명만 달라짐. 지역명 치환은 고객에게 새로운 답을 제공하지 않는다. 운영정책과 필수 경로는 **유사도를 낮추려고 생략하거나 변형할 수 없다**.

## 3개 검증 근거 기반 대표 구성안 (새 HTML 아님)
**A. 승진 / 사무실 수령 / 적성면 마지리 주소표기**
- 결정 순서: 새 직책·보내는 관계 확인 → `D144 금전수 탁상용 53,000원` 또는 `E008 일향금 110,000원`의 상품명·가격 비교 → 회사·부서·층·호실·수령 담당자 → 행정 마지1/2/3리로 주소를 들었다면 **법정 마지리와 도로명/건물번호**를 재확인 → 개별 도착·최종 추가요금 전화상담.
- 근거: `core-five-seller-evidence.json`, 파주시 공식 행정리→법정리 대응 `JEOKSEONG_DANWOL_ADDRESS_SOURCE_AUDIT_20261109.json`. 고객에게 확정된 주소/지점/배송시간을 주장하지 않음.

**B. 승진 / 행사장 수령 / 설악면 요금표 중복**
- 결정 순서: 행사명·일자·수령 창구·반입 가능시간 확인 → `F055 연핑크 호접란 60,000원` 또는 `D152 레드카네이션 화분 50,000원` 비교 → 가평군 10,000원/설악면 20,000원 **표시값 중복**을 상품번호·상세주소와 함께 상담 → 개별 도착/반입은 확정 전제 금지.
- 근거: `seller-shipping-raw-rows.json`, `THREE_LOCALITY_ORDER_DECISION_EVIDENCE_20261109.json`. 행사장 자체의 반입 허용을 추정하지 않음.

**C. 영전 / 자택 수령 / 이동면 요금표 중복**
- 결정 순서: 발령 발표일·새 근무지 출근일과 실제 자택 수령일 분리 → 자택 도로명·건물번호·동호수·부재 시 연락 → `D026 아로우카리아 대형 90,000원` 또는 `F055 연핑크 호접란 60,000원` 가격·상품명 비교(실측 치수 미확인) → 포천시 10,000원/이동면 20,000원 표시 중복에 대한 **최종 적용 요금 문의**.
- 근거: `products.json`, `THREE_LOCALITY_ORDER_DECISION_EVIDENCE_20261109.json`, 기존 영전/수령 모듈. 실제 현지 재고·상품 크기·우선요금 규칙 미확인.

**중요:** 위 A/B/C는 목적·수령 상황이 달라서 유용한 답이 다르지만, **동일 목적·동일 수령상황·동일 배송표 상태의 서로 다른 읍면**은 구분되지 않는다. 지역별 목적을 해시로 임의 배정하는 것은 지역 독립성의 근거가 아니다. 구성안 자체를 49%/85점 통과로 보고하지 않는다.

## 기존 구현 재사용 및 잠재 결함
- `scripts/worker6_nationwide_inputs.py`는 지역명을 SHA-256 해시해 4목적을 분배하고, 각 목적의 SKU를 **2종만** 배정한다. 이는 검증 6종을 사용한 대표 생성기와 다른 경로이며, 사용자가 목적을 선택한 결과가 아니다. 단순 해시 분배는 독립 지역 정보가 아님.
- `v5/purpose_render.py`의 필수/variant section 계약과 `worker6_core_five_preview.py`의 6종 원장 파생, `worker6_shipping_render.py`의 요금표 중복 판단, `operator_policy()`는 재사용 가치가 높다. 신규 프레임워크나 라이브러리 도입 필요 없음; 따라서 별도 외부 GitHub 구현 검색은 현 단계에서 불필요.
- `v5/review_gate.py`는 모든 표본 점수 **90 이상**을 요구한다. 지시된 최신 운영 기준 **85 이상**과 불일치. 게이트 임의 수정 금지; 운영자에게 승인된 기준을 코드와 정합화할 결정 필요. 표본은 목적별 1%이고 현재 소스에서 독립적 85/90점 평가 결과 없음.

## 이미지 자산 구분
- GitHub `assets/library/promotion-plant/`에 **WebP 5개** (`atelier-florist.webp`, `hero-florist.webp`, `moment-blooms.webp`, `moment-flowers.webp`, `moment-leaves.webp`) 및 SVG 3개가 존재한다. 파일 존재가 본 사이트 사용·권리 승인이라는 뜻은 아님.
- `site.json`의 `imagePool`은 `plant-a.svg` 하나만 사용하며 `imageAssetsApproved=false`. `site-spec.json`도 `images.approved=false`. `products.json` 6 SKU 모두 `imageUrl=null`, `imageUseApproved=false`.
- `illustration-provenance.json`은 1254×1254 PNG 2장과 별도 WebP 패키지의 생성·해시를 기록하지만 `integrationStatus=not yet uploaded`; GitHub 이미지 라이브러리의 기존 WebP 5개와 **동일 자산이라고 확인되지 않음**. 해당 두 장의 승인·원격 원본 해시 확인 필요.
- 즉 **래스터가 하나도 없는 것이 아니라**, (a) 기존 원격 WebP의 사용권/출처 승인, (b) 특정 생성 WebP 패키지의 원격 실파일/해시, (c) 6 SKU 상품 사진의 사용 승인, (d) 실제 렌더링에 연결 및 검수가 각각 별도 미완료.

## 목표 충돌과 결정안
1. **49%와 5302 독립 지역페이지를 동시에 충족한다는 근거 없음**: 6지역 15쌍 기존 유사도 90.02–98.55%, 같은 배송표 상태 지명 제거 100% 수준. 목적·수령 질문은 유용하지만 전국 동일서비스 공통정보이므로 지역별 차이를 입증하지 않는다.
2. 선택지 **A(권고)**: 5302를 장기 목표로 유지, 실질 지역근거 확보 전 대량 생성·공개 보류; 근거가 있는 지역부터 연구를 누적. 목적별 5페이지는 별도 검증 산출물이지 5302 대체 목표가 아님.
3. 선택지 **B(명시적 사용자 결정 필요)**: 전국 지역 랜딩 5302개를 강제하는 목표를 바꾸고 목적별 정보구조로 공개 범위를 재설계. 목표 축소에 해당하므로 작업자가 임의 실행 불가.
4. 선택지 **C(명시적 사용자 결정 필요)**: 5302 유지하되 49%/품질 기준을 변경. 현행 지시와 충돌하므로 작업자가 임의 실행 불가. 품질/검색 정책 위험이 커 권고하지 않음.
5. 공개 자체도 생산 이미지 승인, `publishPolicy.productionApproved`, `hostnameConfirmed`, 도메인·Cloudflare 사전 검증 및 기존 guarded first-deploy 조건 미충족. 배포하지 않음.
