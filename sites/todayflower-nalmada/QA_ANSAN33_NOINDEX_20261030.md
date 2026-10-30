# Todayflower 안산 33개 지역 — 확장·QA 인수 기록

2026-10-30. **대상은 검색 차단 상태의 오프라인 33페이지 생성물**이며 `todayflower.nalmada.net`의 공개·색인·DNS·소유확인이나 기존 noindex Worker의 재배포가 아니다.

## 확정된 빌드 증거
- GitHub Actions [run 41033421847](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41033421847) **success**. 소스 HEAD `166d9853a699534095888bc82068ac9ca083bf1f`.
- 아티팩트 `12966946765`, ZIP SHA256 `8c4fee9d6ea204d851b29d2f851ca0c5419008c360777ccc9c16c6f37454d4bb`. GitHub artifact digest 및 내려받은 ZIP 해시 일치.
- `dist/todayflower-nalmada`: 내용 HTML **33개 + 404 1개**, 전체 정적 파일 **50개**. `reports/todayflower-nalmada/manifest.json`의 **50개 파일 SHA256 전수 재계산 일치**.
- `v5.audit`: 내부링크 참조 **2,462개**, 오류 **0**, 경고 **0**. 본문 **33개 전수 528쌍** 문자 5-gram Jaccard 최대 **0.35578** (최대 쌍 22/27). 테스트 값은 문장 중복 탐지 지표이며, 특정 지역에 실제 배송 서비스가 있음을 증명하지 않는다.
- **기존 대표 3개**의 `manifest.contentHashes`는 고정 2026-10-30 3페이지 아티팩트 `12965067290`와 **1~3 모두 정확히 일치**.
- 사용자용 페이지에 어색한 `을(를)` 미처리 표현 없음. 각각의 30개 신규 문서가 주문 목적·수령·상품 비교·결제 점검의 4개 본문과 3개 FAQ를 제공하도록 구성했지만, 독립적인 사람의 전체 문장 의미검수는 아직 제한적이다.
- `index.html`, `2.html`…`33.html`에서 메타 `noindex,nofollow`, 자기 canonical 없음; `robots.txt`는 `Disallow: /`. `sitemap.xml` 없음, IndexNow 제출 없음.
- Chromium 샘플 **6개 경로 × 390/1440px = 12개** 실제 화면. `/`, `/2.html`, `/3.html`, `/4.html`, `/5.html`, `/33.html`. 가로 넘침 0, 기존 ImageGen 5장 각 **1448×1086**, 표시너비 모바일 332px/PC 330px. `reports/todayflower-nalmada/large-image-qa.json` 등 첨부.
- `fwith.co.kr` 기존 SKU 상품 8종, 페이지별 실제 주문 링크·표시가 기록 유지. 신뢰성 범위는 2026-10-30 이전 확인 기록이며 현재 판매가·재고·당일 발송과 구분.

## 원장 검증 수준
- 법정동 30개: `sites/todayflower-nalmada/ansan-legal-regions-evidence.json`. V4 2026-10-22 공식 원 ZIP SHA256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd` 기록과 고정 Flowershop HTML/manifest(아티팩트 `12874109256`)에서 안산 30개 코드·명칭 대조.
- V4 공식 시/구 코드3개 중 안산시 1과 일반구 2개: `data/regions/master.json` (2026-10-22) 대조. 전체 공식 원장에 284개 시도/시군구/일반구가 있다고 해서 이를 배송 가능한 284개 지역이라고 단정하지 않는다.
- V5 `seoul_gyeonggi_current_dong.json`의 서울·경기 **1,732** 후보 동명은 이번 *공식 법정동* 30개로 대체하지 않았으며, 데이터베이스 모델 차이를 명시적으로 보존.
- 전국 협력 꽃집 배송 설명은 V4 `site/data/service-facts.json`에 적힌 2026-10-21 사용자의 업체 운영 설명. 개별 주소 당일배송/시각/지역 추가요금/실제 지점은 독립 확인하지 못했고, 별도 연락·판매처 결제 과정 확인이 필요.
- 별도 `todayflower.nalmada.net` DNS/권한/신규 Secret 없음, 임의의 local store/배송 수수료/최저가/리뷰 생성 없음.

## 이미지 출처
- 5개 AI 연출 이미지의 `gen_id` 및 최초 생성 출처는 `site-spec.json images.provenance`의 **제작 기록**. 부모가 원본 실행을 직접 열지 못했으므로 독립 확인이라고 쓰지 않음.
- GitHub에 보관한 **WebP 실제 바이트, Git blob, VP8 1448×1086 헤더**, 2026-10-30 Chromium 화면과 기존 Worker 11건 HTTP 응답은 독립적으로 검증했다. ImageGen 연출 이미지는 판매처 실제 SKU 사진과 명확히 구별된다.

## 향후 별도 승인/검증 범위
1. 추가 30개 문서의 사람에 의한 의미·검색가치 검토 및 실제 주소 단위 배송조건 확인.
2. 페이지별 지역 실정보의 추가 확보 없이 상권·업체·후기·당일배송 보장을 창작하거나 수천 페이지로 확대하지 않기.
3. 이미 성공한 noindex Worker `sfv56-todayflower-preview`에는 **기존 3개 대표 URL만 공개**된 상태. 이번 아티팩트 33개는 GitHub에 보존된 *오프라인 생성본*이며, 운영 배포·검색 색인 전환은 하지 않았다.
