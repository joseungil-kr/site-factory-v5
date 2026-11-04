# Clinicflower·Clinicopen·Clinicpresent 실제 상품형 대표 페이지 검수 기록 — 2026-11-05

## 실행 범위와 중복 방지
- **일반 Chat에서 기존 V5 프로젝트를 직접 이어 진행**. 신규 Work·Codex·별도 사용자 대화 없음.
- 2026-11-05 작업 착수 시 기존 V5 제작 규칙 `main:f769c6c7c6710dff5147265b0b4f4fc69a0d335d`과 기존 대표 시안 `review/clinic-product-pilot-20261105:07263a8eab63611cdb846a413529279daa1640a4` 확인. 기존 배포 `sfv5-nalmada-domain`을 덮어쓰지 않음.
- 원본 5,034개 지역명(상위 코드 미대응 1,438 포함)은 **수정하지 않음**. 기존 세 호스트의 총 15,906개 공개 HTML, URL, sitemap, RSS, robots, IndexNow 및 다른 운영 Worker의 DNS를 보존.
- **전국 재제작·배포는 이번 대표 검수 단계에서 실시하지 않음**. 샘플 승인·완전 검증 후 별도 진행.

## 실물 상품·가격·사진·주문 경로 근거
2026-11-05 실제 `fwith.co.kr` 판매처 4개 상품과 이미지의 HTTP200, 상품명·가격·구매 버튼 일치를 확인했다. [읽기 전용 Actions run 41875442755](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41875442755), 고정 원장 `sites/nalmada-shared3/pilot_review/retail-products-20261105.json`.

| 상품 SKU | 판매처 상품명 | 확인 표시가격 | 상세·주문 |
|---|---|---:|---|
| D144 | 금전수 탁상용 | 53,000원 | https://fwith.co.kr/shop/item.php?it_id=D144 |
| D149 | 녹보수 소형 | 65,000원 | https://fwith.co.kr/shop/item.php?it_id=D149 |
| C200 | 축하 3단 화환 | 59,000원 | https://fwith.co.kr/shop/item.php?it_id=C200 |
| C206 | 축하 4단 화환 | 120,000원 | https://fwith.co.kr/shop/item.php?it_id=C206 |

- 판매처의 실제 JPG 경로: `https://fwith.co.kr/data/item/flower379/{SKU}/thumb-1_500x500.jpg`. 네 가지 모두 직접 읽기 HTTP200·JPEG 검사 통과.
- 판매처 표시상품가격과 결제 단계 최종 배송비·재고·정해진 도착시간을 혼동하지 않는다.
- **사용자 승인 범위:** 이번 사용자 지시에서 `fwith.co.kr` 사진 사용 승인 사실과 Clinic 3개 사이트 활용을 재확인했다. 이전 대화의 동일 취지 지시는 일부 확인되나 과거 사용 승인 발언의 **정확한 완전 원문**은 검색에서 아직 회수하지 못했다. 모르는 원문을 임의로 생성하지 않는다.
- C200/C206 사진에 보이는 **결혼 리본은 판매처 화환 상품 구성 예시**다. 실제 병원 개원식 현장 배송 사진이라고 표시하지 않는다. 사용자 요청에 따라 의료기관 수신자명·축하 문구는 주문 시 별도 확인.

## 사이트별 의도·상품과 대표 페이지
- `clinicflower.nalmada.net`: 개업·개원 후 계속 두는 **화분 선택**. D144·D149 / 설치 위치·관리 난도·리본.
- `clinicopen.nalmada.net`: **개원식 당일 일정과 인수 인계**. D149·D144 / 행사일·수령 담당자·입구·변경 대응.
- `clinicpresent.nalmada.net`: 개업식 **축하화환**. C200·C206 / 3단·4단, 규격·반입 가능 장소, 리본과 철수 조건.
- 대표 `안산시` 페이지 3개와 전국 지역명 원장의 정확한 624번 **경기도 안산시 상록구 본오동** 상세 3개, 합계 **6개 지역 시안**. 모두 `noindex,nofollow,noarchive`; JSON-LD 미추가; 실제 판매처 직접 주문 링크 + 전화 `tel:1844-0644`. 루트 페이지 신규 배포 아님.

## 검수 및 사용자 가치 개선 과정
1. 1차 제품형 시안: `build_pilot.py` 개편, commit `02176e3c2376125f02f9a797bb6031953dc9add2` → 본오동 전체 지역 표기 commit `d1e42ac68c64f37a1b96306b151c79afd37f6893`.
2. 1차 QA: [Actions run 41876766850](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41876766850), artifact `13346983861`. 로그상 6페이지 생성 및 Chromium 390px·1440px **12화면 통과**, 상품사진 3장/페이지의 실제 로딩, 정확한 주문 URL 2개, 전화 버튼·오버플로 검사.
3. **독립적인 문서 중복 문제 발견:** 1차 시안 동일 사이트 `안산시 대표` ↔ `본오동 상세` 본문 비교(공백 정리 후 char 5-gram Jaccard) 약 `0.919/0.921/0.923`. 이는 원장이 같더라도 문서가 너무 비슷하다는 품질 경고이며 전국 완료 근거가 아니다.
4. 2차 대표 수정: commit `e4af4dfcbeed0192e752da3ac7ab2d405351466d`, 본오동 페이지 3개를 상위 상품 비교를 반복하는 대신 **각 사이트 목적에 맞는 수령·현장 준비 5개 섹션, 별도 FAQ, 구체적인 문의 대본**으로 재작성. 실제 SKU·가격·사진·주문 연결, 390px·1440px 구성은 유지.
5. **2차 QA:** [Actions run 41878073990](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41878073990), 새 지역 상세 수정본. **성공 여부·12화면·동일 사이트 본문 유사도 재측정은 아직 회수 전**. 1차 시안의 Chromium 결과를 2차 수정본 결과로 둔갑시키지 않는다.
6. 현재 풀려야 할 **검증 세부 위험**: 2차 QA 소스 내 `clinicpresent` 지역 페이지 설명이 “해당 의료기관으로 배송된 사진을 뜻하지 않습니다”를 사용하고 있으나 기존 QA 문자열은 “병원 현장 배송 사례를 나타내지 않습니다”를 고정 기대한다. 실제 실패 시 의미를 훼손하지 않고 QA/원고를 최소 수정해 재검사. 본문 자연스러움과 실제 사진 리본 안내가 화면에 명확한지도 직접 재확인.

## 배포·복구 및 향후 게이트
- 운영 Worker `sfv5-nalmada-domain` 현재 실제 100% active version은 변경 전에 독립적으로 다시 확인할 것. 과거 마지막 성공 배포 보고 version `4cc52a1b-8e4d-42dc-b598-1b4e1b41e048`를 추정치가 아닌 **과거 기록**으로 취급한다. 재배포 전 기존 버전·전체 호스트/자산/ZIP·롤백 경로 확보.
- 1차/2차 대표 시안·URL·사진·가격·문장 의미·모바일·PC 수동 검수가 완료되지 않은 한 **전국 15,906페이지 재생성·재배포·IndexNow 재제출 금지**.
- 전국 전개 시 보유 지역명 5,034건/사이트 전체 사용, URL 안정성 보존, 목적별 페이지 고유 가치, 설명문/OG/canonical/이미지 링크/고아·sitemap·RSS 전수 검사. 지역명만 바꾼 문장 수치로 통과 처리하지 않는다.
- 색인: 과거 IndexNow HTTP200은 접수이고 실제 Naver 색인·순위는 미확인. 새 대표 noindex 시안을 IndexNow 제출하지 않는다.

**검증 상태:** `PLAN/RETAIL_FACTS_PASS / FIRST_SIX_PILOT_QA_PASS / SECOND_REVISION_QA_PENDING / NATIONAL_RELEASE_NOT_STARTED`. 이 문서는 완료를 과장하지 않는다.
