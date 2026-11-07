# Todayflower — 2026-11-07 운영 RSS 수정 및 방문자 문구 검수

> 이 보고서는 작업자1의 단일 담당 사이트 `todayflower.nalmada.net`만 대상으로 한다. WreathPrice, Skyquote, 병원 3개 사이트, 기존 병원 RSS, 보안·DNS·Secret·권한은 변경하지 않았다.

## 검증 가능한 결론

**운영 RSS 404 해결: 완료.** 기존 공개 HTML 및 이미지 전체를 보존하고 동일한 기존 Worker에 RSS 50개 항목을 추가했다.

**새로운 전국 본문 품질 개선: 진행했지만 배포 보류.** 문장 혼합 오류를 줄였으나 독립 본문 유사도 49% 미만 기준 및 51개 표본 전원 90점 기준을 충족하지 못했다. 기존 운영 페이지를 변경하지 않았다.

## 실제 운영과 배포 원장

- 실제 운영본 소스: V5 `0ca5705aa12950da571f089b2d4ac7256111f77e`의 고정 전국 빌드. V4 기존 Worker 배포 경로에서 유지.
- 운영 RSS 전용 배포 경로: V4 `.github/workflows/todayflower-rss-only-release-20261107.yml`; 최종 workflow commit `ce4051221fc4c12e2c9c051a109d81a2b224a70b`.
- [배포 및 운영 390/1440px QA 성공 #42339345069](https://github.com/joseungil-kr/site-factory-v4/actions/runs/42339345069).
- Cloudflare 기존 Worker: `sfv56-todayflower-preview`; 이전 활성 버전 `79e425cf-2592-40ec-a55b-7ad383d132f1` 확인 후 배포. 새 활성 버전 `da6d6007-38b1-4ddd-8c65-76cefb15da24` GET readback.
- RSS 생성 스크립트: `scripts/build_todayflower_rss.py`의 V5 고정 SHA `01563363af7c7b968f1a03c24729cc2f23c81664` 사용. 실제 HTML `<main>` 콘텐츠 50건, 자기 공개 URL 및 permalink GUID, XML 구조 검사. 발행일 미확인으로 pubDate는 만들지 않음.
- 배포 RSS 파일: 902,005 바이트, SHA256 `7e10b1fff72fcd105adcef830cfc0763ee0a9b8c1fa2505e09d066ed574482a9`. 원본 바이트와 실제 공개 응답 바이트 일치.
- 공개 `https://todayflower.nalmada.net/rss.xml`: HTTP 200, 50건 유효 XML 및 본문 확인.
- 별도 `https://sfv56-todayflower-preview.joseungil.workers.dev/rss.xml`: HTTP 404, noindex 유지.
- 원래 사이트맵 5,070 URL, 홈 네이버 확인 태그 `d970eeb70abc7b36cbcc02fadd9362c5c57fcb46` 1개, 자기 canonical, 공개 index, 상품 링크 보존.
- 기존 정적 5,087개 파일 SHA 매니페스트 재대조, 운영 16개 Chromium 화면 390/1440 PASS.
- [배포 후 별도 읽기 전용 공개 HTTP 검증 #42340191357](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42340191357): 공개 홈/28/34/5071 각 200, RSS 50, 사이트맵 5070, 네이버 홈 1개, 상품 상세 8개 HTTP 200 및 구매 UI, 별도 Worker RSS 404 PASS. 이는 다른 Repository/Runner에서 재실행한 독립 운영 검수다.

## 새로운 고객 중심 문구 생성기: 실제 미통과

- 작업 브랜치: `site/todayflower-nalmada-pilot-20261030`.
- `v5/todayflower_copy_pool.py`: 16개 구매 의도별 선택/수령/배송 문장 576개, 무관한 자유 혼합 풀 제거.
- `v5/todayflower_regions.py`: 실제 문구 풀이 5,037 신규 지역 페이지 생성 경로에 적용, 지역 원장/URL/상품 SKU 보존. 출처가 확인되지 않은 지역 서비스 지점·배송시간·실적을 만들지 않음.
- `sites/todayflower-nalmada/pages.json`: 기존 안산시 대표 33개 문구 교정, 문단 중복·잘못된 조사 일부 수정.
- `v5/todayflower_markup.py`: 기존 이미지 7개, 상품 SKU 및 문의 경로를 보존하며 고객용 내부 AI·제작 검수 캡션 일부 수정.
- `tests/test_todayflower_national.py`: 생일/개업/근조 등 목적을 섞는 잘못된 문구, 대부지역 안내를 타지역에 재사용하는 오류를 5,037개 전국 페이지에 대해 거부하도록 보강.
- `scripts/audit_todayflower_customer.py`: 51개 URL을 25+30+30+15점으로 사전평가. 기존 무조건 100점에 가까운 부실 검증을 개선하고 타 페이지와의 실제 5-gram 본문 중복 및 지역별 근거 부재에 감점 추가.
- 정식 QA 실패: [V5 Actions](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42339761186) — 기존 49% 유사도 경고가 아닌 **오류**. 대표 실패 예: 2412/2852 본문 54.082% 유사.
- 독립 진단 생성 (배포 금지): [51페이지 원문과 JSON 점수/HTML·RSS 산출물 #42340029743](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42340029743). 이 진단은 동일 `v5.markup` 렌더러를 사용하지만 공식 `v5 build`가 아니며 실제 공개에는 쓰지 않는다.

### 고정 1% 샘플 51개 점수

기계적 사전평가(사람의 최종 90점 독립 검수가 아님) 결과: 85점 **2페이지**, 97점 **44페이지**, 100점 **5페이지**. 최소 85점이므로 FAIL. 모든 51개 URL과 세부 범주 점수 및 근거는 `qa/customer-review-51-20261107.json`에 저장.

- `https://todayflower.nalmada.net/564.html`: 85점 — 다른 지역과 본문 유사도 51.927% 및 배송지 고유 정보 부족.
- `https://todayflower.nalmada.net/3603.html`: 85점 — 위 페이지와 본문 유사도 51.927% 및 배송지 고유 정보 부족.
- 별도의 공식 전국 1% 층화 표본에서는 2412/2852 페이지 쌍이 54.082%로 측정되어, 서로 다른 두 표본의 기준 모두 만족하지 못함.

51개 정량 점수가 높더라도 검색 의도별 지역 고유성이 부족한 경우 사람의 90점 합격을 주장하지 않는다. 최신 생성본은 **서로 다른 법정동에 현장배송 정보가 검증되지 않은 상태**라 문장 순서와 SKU 조합만 바꾸는 것으로 실제 지역 정보 가치가 생기는 것은 아니다. 진짜 지역별 안내와 근거가 확보되지 않는 한 대규모 재배포와 색인 재요청을 계속 보류해야 한다.

## 실패 재검수 / 범위

- 기존 2026-11-06 초기 2회 Actions 실패(오래된 테스트 기대 문구 및 Python 호출 경로)를 수정함.
- 2026-11-07 문구 풀 분리/확장, 문장 중복 완화, 구매 의도별 SKU 선택, 5,037개 관련성 회귀 검증, 51페이지 판정기 개선을 단계별로 반복함. 정식 49% 검사와 새로운 51페이지 90점 판정은 **최종 미통과**.
- 실행 경로와 실제 공개 소스를 구분하여, V5 후보의 수정 커밋을 운영 완료로 표시하지 않음.
- 고객이 실제로 보는 운영 RSS와 HTML은 원래 배포본의 문구를 포함한다. RSS 복원은 콘텐츠 문구 수정과 별개의 회복이며, RSS가 200이라고 방문자 문구가 모두 개선됐다는 뜻은 아니다.
- 다른 사이트의 Worker·DNS·인증·결제·개인정보·인덱스 상태는 수정하지 않음.

## 최종 판정

| 항목 | 상태 |
| --- | --- |
| LIVE_HTTP / RSS | PASS — 50건 HTTP200 |
| SITE_MAP / Naver tag / 390·1440 / seller SKU | PASS — 정식 배포 직후와 별도 읽기 검증 |
| 새로운 문구 POOL/생성기 COMMITTED | PASS — 후보 브랜치 |
| 전국 5,070페이지 재제작 품질 49% | FAIL — 최대 54.082% |
| 51페이지 기계 점수 전원 90점 | FAIL — 2페이지 85점 |
| 최종 사람 검수 90점 | 미완료 |
| 새 콘텐츠 DEPLOYED | NO — 기존 공개본 유지 |

다음 수정에는 검증 가능한 배송/상품 지역별 근거나 의미가 다른 핵심 구매 질문을 수집해 페이지 본문을 실제로 구분해야 한다. 단순 자동 문장 퍼즐 변경·전국 재생성·비공개 해제는 해결책으로 인정하지 않는다.
