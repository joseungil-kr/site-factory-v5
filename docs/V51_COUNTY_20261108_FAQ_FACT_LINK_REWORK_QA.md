# V5.1 군 시험: FAQ 사실 연결 및 거창 75 재작업 검증 (2026-11-08)

## 인수와 원인
- 수신 최신 HEAD `fb24b5faca1c5f41060e8082587dc10e460bcd39`; 당시 진행 중 Action 없음. 직전 091c2d19의 계실장 독립 검수: 28·59 각 90, 13=90, 26=91, 78=92, 37=92, 60=90, 75 거창 86(FAIL).
- /75 실패: 리본 이름을 묻는 FAQ가 선택옵션 0개를 답하고, 앞의 상품고시·주문단락과 역할 중복. 이전 검증은 두 쌀 유형만 검사하고 빈 factIds를 허용하며 원장을 생성 시 실제 로드하지 않았음.
- 지침 **df1fabe9e7bb1e7b32bcd8c82b440ab8ba488613**가 코드보다 선행. `docs/V51_COUNTY_FAQ_FACT_CONTRACT_20261108.md` 확인 대상.

## 원인 조치 (시험 브랜치 전용)
- 증거원장 `docs/evidence/v51-county-buyer-fact-registry-20261108.json`: verified/source_url/checked_at/region_scope/facility_scope/product_id/allowed_slots/kind/value. B054 청도 +10,000원, 완도 +20,000원은 SKU별 판매처 배송표의 제한적 사실이며 결제총액·배송성공 약속으로 쓰지 않음. 판매처 확인일 2026-11-08, 정확한 원문 조회 시각 미기록(unrecorded). 이전 청도·완도 fact_id는 동일 범위의 검증된 alias로 유지함.
- `scripts/county_fact_contract.py`: 모든 purposePool의 FAQ customer_question/answer_topic/answer_fact_ids/answer_kind/output_slot, section factIds/outputSlot/customerQuestion/answerKind를 생성 중 연결하고, 실제 외부 JSON registry를 로드해 검증. 확정된 숫자/공지/옵션 등은 source ID 없이 통과 금지. 일반 구매 행동은 빈 ID가 아닌 명시적 buyer_guidance 분류로 구분. 질문-답변 주제 불일치, 리본 이름 질문에 옵션 0개 답변, 동일 선택옵션 사실의 FAQ 재진술을 실패 처리. 의미를 완전 자동판단한다고 주장하지 않음.
- `scripts/build_county_funeral_trial_inputs.py`: 95페이지 각 목적에 공통 validator 적용. 거창 FAQ는 **접수한 근조상품 주문내역은 어디서 조회하나요?** / **판매처 사이트의 주문내역조회 메뉴에서 접수한 주문 정보를 확인할 수 있습니다.**로 교체하여 01 상품 옵션, 02 리본/수령지와 역할 분리. 연천 B213 배송비 FAQ는 scope/sku/amount가 동일한 fact ID에 연결. 지역/시설 Notice 사실은 원장 일치 검증.
- `v5/purpose_render.py`: 시험군 HTML assemble 시 생성된 FAQ 메타데이터의 현재성 및 원장 정합성을 재검사하여 site-spec을 후수정한 불일치가 최종 HTML에 통과하지 않게 함. 일반 운영 사이트는 제외.
- `tests/test_v51_county_selected_skus.py`: 18개 일반 구매 목적 + 특수 유형 FAQ의 검증 메타데이터 확인. 거창의 원래 리본 질문→옵션0 답변 반례와 빈 사실 ID 위조 반례를 실제 assemble 단계에서 FAIL 확인. 청도·완도의 이전 fact ID와 신규 원장 ID 모두 보존 확인.

## 원격 코드 및 테스트 결과
- 선행 지침: `df1fabe9e7bb1e7b32bcd8c82b440ab8ba488613`
- 신규 fact registry 최초: `f020434c5a70e8ab1d781dad498106d8287415d8`; scope alias 정리 `25163e2e542d959bb15bddcd4d01ef9471e18940`
- 공통 validator 신설: `5d6e13501ccdda02291836e293eb1dc39bf0ba14`, 후속 runtime 보강 `a3f464e2a5fb8d594ebc316becb19c93c194bf41`.
- 생성기: `546f52a219f70b89309596c98d8d32c7c3e343d3`; 조립 단계 검증: `ad309a28bedde789068343fcf98362a72f0f8c71`.
- 최종 테스트 커밋/콘텐츠 SHA: **`5fcc06c298f4c6ee2fa626a62428f590a87a1be0`**.
- CI 중간 실패는 신규 validator 자체에서 미등록된 연천 배송수치, 전국 공지 요약, province 반입 범위, 구 alias 매핑이 fail-closed 된 것이 원인. 실제 각 해당 source/slot/범위를 보정하고 재실행. 실패를 무시하거나 PASS로 보고하지 않음.
- 최종 빌드 run **42468831215**: https://github.com/joseungil-kr/site-factory-v5/actions/runs/42468831215 SUCCESS. 원본 artifact **13612314362** (archive 안 site ZIP SHA256 **8719c4850dce50e780f5d337b3b0ae6ad7fb250e344e046323f8b43166bf60ef**). 정적 ZIP 103파일, 페이지 95 + 404.
- 최종 HTML review run **42468831230**: https://github.com/joseungil-kr/site-factory-v5/actions/runs/42468831230 SUCCESS. artifact **13613050392**.
- 최종 390px/1440px 브라우저 run **42468831314**: https://github.com/joseungil-kr/site-factory-v5/actions/runs/42468831314 SUCCESS. screenshot artifact **13612543361**. 35 경로 × 2 = 70 화면. `qa.json` passed=true, 대표화면 가로 넘침 0/70.

## 원문 및 화면 실검수(작업자 / 독립 평가 아님)
- 최종 review ZIP에서 /28, /59, /75, /13, /26, /37, /60, /78, /95, /14, /24, /42, /86 등 13개 경로 실제 HTML 제목/상품 카드/FAQ/CTA를 직접 읽음 (13/95=13.68%). 거창 /75 FAQ는 주문내역 조회라는 별도 구매 후 과업을 답하고 섹션01 옵션 0개·섹션02 리본명/수령지와 다른 정보를 제공함.
- 청도 /59와 완도 /28의 반입 notice 각 1곳, B054 상품 가격 90,000원 각 1곳, 실제 B054 CTA 보존. 연천 /37 B213 SKU, 횡성 /78 B201 배송비 원문, 고령 /60 B211 상품 유지.
- 최종 screenshot ZIP에서 mobile/desktop /75, /28, /59를 각각 실제 이미지로 확인. 자간/한글/CTA/폭 레이아웃 확인, 모바일 가로 넘침 없음. 전수 70화면의 자동 검사는 이를 보조하는 결과.
- 일반 목적의 문맥 중복은 규칙과 별개로 여전히 독립 편집 검수 대상. 13페이지 자체 검수는 계실장의 90점 판정을 대체하지 않음.

## 금지 범위 보존
운영 사이트, Todayflower, main, 배포/공개/색인·IndexNow/검색등록, DNS, 인증·보안·권한 변경 없음. 시험은 로컬 파일과 GitHub Actions artifacts뿐이며 실제 owner-private 공개 호스트가 구축된 것으로 보고하지 않음.
