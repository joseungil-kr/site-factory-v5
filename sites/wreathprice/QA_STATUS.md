# 알뜰화환 3페이지 대표 시안 QA — 2026-10-30

## 실행 범위
- 신규 독립 브랜치: `feature/v52-wreathprice-20261030`
- 독립 경로: `sites/wreathprice/`
- 운영·DNS·Worker·Secret·Google/Naver 인증·결제·IndexNow POST 없음
- 가격/상품 소스: V4 `data/funeral-products/CATALOGUE.json` 원장(근조 2026-10-22), fwith.co.kr 원문 C205/C030 (2026-10-30)
- 축하 C205 149,000원/C030 200,000원은 제품 표시가이며 배송비/리본 포함은 **미확인**. 지역 전체 배송 가능 주장 금지.

## 검수 결과
- 독립 Python 표준 라이브러리 시안 빌드 성공: `ansan/index.html`, `ansan/sangnok/index.html`, `ansan/sangnok/bono/index.html`
- 5종 공용 ImageGen 래스터를 1024px 너비 WebP로 압축. 각 페이지는 5장 모두 포함, alt/width/height 및 비핵심 lazy loading 확인.
- Python HTTP 서버: 3 HTML + 5 WebP + robots.txt 모두 HTTP 200. 세 HTML 모두 `noindex,nofollow`, Sitemap 없음.
- Playwright Chromium 직접 localhost 접속: `net::ERR_BLOCKED_BY_ADMINISTRATOR` (환경 접근 제한); **실제 HTTP 브라우저 탐색 완료로 주장하지 않음**.
- 보완 렌더링: 동일한 로컬 HTML/CSS/실제 WebP를 data: URL로 불러와 Chromium set_content로 1440×900, 390×844 렌더링 검수. 두 크기 모두 5/5 이미지 로딩, 가로 overflow 0. 스크린샷 별도 ZIP 포함.
- 운영 preview URL: **없음**. GH 바이너리 업로드는 아직 미완료이므로 운영 또는 미리보기 배포 금지.\n- 로컬 ZIP SHA-256: `d67e2d3b4d0ee1e8f0fc289330e933e04f2914db1ba4a264e3c09027cccae119`, 1,967,704 bytes, 21개 파일. 이미지 5종 WebP 원본 및 build 산출 포함.

## 타 프로젝트 조사와 재사용 판단
- 내부 `joseungil-kr/site-factory-v5`: 이미 검증된 Python 정적 페이지·QA·Workers 배포 구조. **구조 일부 재사용이 최경제적**, 신규 Astro/Shopify 스택 추가 도입 불필요.
- `owaaquino/astro-shopify-template`: 공개 MIT License, Astro + Shopify 연결 스타터. 외부 Shopify 의존성·구매/카트 구현이 불필요해 **구조만 참고**.
- `njbSaab/astro-njx-store`: 공개 MIT License, Astro storefront, 상품 UI 참고 가능. 사용 흔적/최근 업데이트 일자 별도 확인 필요. **UI 구조만 참고**.
- `thomasKn/astro-shopify`: GitHub 조회 당시 504 stars/145 forks, MIT, Astro+Shopify. 자체 주문서가 아닌 fwith.co.kr 상세 연결 목적이므로 **신규 도입 제외**.
- 외부 저장소 코드를 그대로 복제하지 않았으므로 외부 코드의 라이선스/의존성 유입 없음.

## 참고 조사 URL
- 자사: https://fwith.co.kr/shop/item.php?it_id=C205 , https://fwith.co.kr/shop/item.php?it_id=C030
- 비교: https://flowername.co.kr/guide/wreath-price/ , https://xn--9m1bt77dma.com/price , https://www.imflower.co.kr/prices.php , https://www.dogus.co.kr/life/wreath-cost

## 진행 차단/남은 일
1. 실제 WebP 5종을 GitHub 리포지터리에 이미지 바이너리로 업로드하고 원격 해시 readback. 현재 독립 다운로드 ZIP에만 전부 포함.
2. GitHub 소스 빌드, 실제 별도 noindex Workers 미리보기, 브라우저/HTTP 검증.
3. `wreathprice.nalmada.net` 기존 충돌/보유 계정 읽기 확인, 이후 **별도 승인 전 DNS/Custom Domain 연결 금지**.
4. 공식 지역 원장과 기존 사이트 커버리지 확인 전 전국 확대 금지.

## 이전 담당 미완 작업
기존 `feature/v52-wreath-region`의 네이버 인증 복구/기존 인계 상태는 이번 작업과 무관하게 그대로 보존. 이 브랜치에서 운영 원장이나 기존 Worker를 수정하지 않음.

## 2026-10-30 후속 검증 기록
- `build.py` 35행의 리터럴 `\\n`을 실제 줄바꿈으로 수정, 원격 readback 확인. GitHub 소스 기준 문법 검증 Actions 결과는 별도 확보 필요.
- 기존 ZIP 21파일/1,967,704바이트, SHA-256 `d67e2d3b4d0ee1e8f0fc289330e933e04f2914db1ba4a264e3c09027cccae119` 재확인. 5개 WebP 모두 너비 1024px이며 ZIP 실파일 SHA는 `image-manifest.json`에 저장.
- ZIP 내부 대표 3개 HTML 각각 이미지 5개와 fwith 주문 링크 5개 확인. Python 내장 HTTP 서버에서 3 HTML/5 WebP/robots 총 9개 경로 HTTP 200 확인.
- 모바일 Chromium `set_content`에서 실제 WebP data URL을 eager 전환하여 이미지 5/5 로딩, 390px 가로 넘침 없음. localhost 직접 browser.goto는 `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- `test_pilot.py`, 격리 `worker.js`, `wrangler.preview.json`, `wreathprice-preview-qa.yml` 준비. 사이트 전용 Actions 통과/Cloudflare 배포는 아직 확인하지 않음.
- **원격 실이미지 업로드 미완료:** GitHub `fetch_file`에서 `sites/wreathprice/assets/funeral-wreath.webp`는 404. `mcp__GitHub__create_file`은 UTF-8 텍스트 전용, `mcp__GitHub__create_blob`은 base64 콘텐츠 인자만 받으며 현재 컨테이너 경로를 직접 업로드하는 도구 인자가 없음. 이 차단이 해소되기 전 미리보기 배포 금지.
- 기존 Wreath 운영/인증, 타 사이트, DNS, 보안 권한은 변경 없음.

## 2026-10-30 실제 원격 noindex 미리보기 검수 결과
- **저장 소스 HEAD:** `7c9d9ca735e9729c91286b1e03b8d6501a897305` (5개 WebP 바이너리 포함, 다른 사이트 변경 없음).
- **사이트 전용 CI:** [V5 run 41018200247](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41018200247) success — Python 컴파일, WebP 5개 전체 SHA-256/치수, 실제 3페이지 빌드 및 내용 검증 3 tests pass.
- **별도 미리보기 Worker:** `sfv52-wreathprice-preview`, 최초 배포 version `dab3c828-4662-4228-a4b9-21fec3334e14` (V4 run 41018933326: Worker 배포는 성공, 직후 첫 /ansan/ 요청 404로 QA 실패).
- **읽기 재검증:** [V4 run 41019094135](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41019094135)에서 URL 반영 후 /ansan/ 200 확인. 초기 404 원인은 확정하지 않음.
- **최종 원격 검증:** [V4 run 41019185898](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41019185898) success. 공개되지 않는 `https://sfv52-wreathprice-preview.joseungil.workers.dev`에서 시/구/동 대표 3페이지 HTTP 200 및 각 이미지 5개/상품 주문 링크 5개 확인. 5개 WebP HTTP 200, 정확한 전체 바이트 SHA-256/크기 검증 통과. X-Robots-Tag noindex, HTML meta noindex, robots Disallow, sitemap 404, 임의 누락 경로 404 통과.
- **영수증:** run 41019185898 artifact 12960339636 (`wreathprice-preview-final.json` 및 응답 진단).
- **도메인:** `wreathprice.nalmada.net` DNS/Custom Domain 연결하지 않음. Workers Custom Domain에서는 충돌 검증 당시 해당 호스트 바인딩 없음; DNS/Routes 별도 읽기 상태는 미확인.
- 실제 운영/공개색인/Google/Naver/IndexNow, 인증·Secret·권한 변경 없음. 본 시안은 부모 화면 검수 후에만 다음 범위를 결정한다.

## 2026-10-30 공식 코드 대조 및 noindex 확장 실행 증거
- **실제 성공:** [run 41031299548](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41031299548), artifact `12966760028`, Workflow SHA `2c8d268f4ce91c7c95ac7edd9d6b2691603fbf73`. 3개 대표 + 16개 증분 = 19개 noindex HTML, 실제 이미지 5장 공용 재사용, 6개 단위 테스트(대표 3 + 확장 3), Python 컴파일 통과.
- **공식 자료:** V4 `data/regions/master.json` Blob `13d43fc3f2492b29b1680858235fe0ac0cd10580`, 2026-10-22 확보. 시·도 16 + 시·군·구 229 + 일반구 39 = 총 284 **상위 법정동 코드**. 2026-10-30 실시간 원본 최신 여부 및 하위 읍면동 유효성은 추가 검증되지 않음. 기존 Wreath 5,034개 중 상위명 불일치 1,438건은 확장에 사용하지 않음.
- **확장 대상:** `verified-regions.json` 경기 18개 코드 중 이미 대표 페이지가 있는 안산시/상록구 코드를 제외한 16개. 기록하는 근거는 지명·코드·상위 계층뿐이며 **판매자 배송 서비스 가용성 검증 건수 0**. 주문자 위치별 가격/배송 확약 불가.
- **고유 내용 검사:** 별도 가격 비교 초점·상품 3개 SKU 선택 조합 16가지, 모두 서로 다른 HTML 해시/제목. 실제 판매처 기준가와 가격 차이만 계산, 배송비·리본비 미확인은 유지. 공통 제품 표/FAQ/AI 시각 자산은 공용이며 검색 엔진 품질 우위가 입증됐다는 결론은 아님.
- **이미지 출처 체인:** 대화의 AI 이미지 생성 기록 gen ID `15f669dd-7ef4-46ee-9a3a-56e90f900200`, 원 PNG `a_vertical_collage_strip_style_photo_composite_sho.png` SHA-256 `db9ebc5272573c3ec97b5aeefe43fee8f37dfcc99b6f6d5d554a34361f43c3d1`, 1024×1536, 2,536,172바이트. 기획상 5개 세로 구획을 좌표 `image-provenance.json`대로 Crop + Pillow WebP quality80/method6로 재인코딩해 원 ZIP WebP **5개 바이트 전부 정확히 일치**함을 직접 확인. 원 PNG는 GitHub에는 없음; 원본 부재 상황의 독립 재현 제한은 공개적으로 남김.
- **배포 상태:** 기존 검증된 3페이지 noindex `workers.dev` 미리보기는 그대로 유지. 신규 16개는 GitHub Actions artifact에만 생성했으며 Cloudflare 재배포·커스텀 도메인/DNS/인증 변경·IndexNow POST·공개 index 전환 없음.
- **기존 기록과의 구분:** 문서 상단 '원격 실이미지 업로드 미완료' 및 'preview URL 없음'은 과거 시점의 작업 로그이며 현재 상태는 run 41018200247/41019185898의 성공 기록이 우선함.

## 2026-10-30 19페이지 고객 문구 교정 및 noindex 실제 배포 검증 (최신 정정)
- **문구 오류:** 기존 16페이지의 '수원시은 municipality 등급', '장안구은 ward 등급', '가장 높은 B205은' 등의 표현을 제거. 법정동 코드/내부 enum은 고객 본문에서 제외하고 원장/QA에서만 보존. 모든 지역의 배송 가능·배송료·리본 포함 여부는 **미확인**; 실제 확인된 배송 가능 지역은 0.
- **비교 구조:** 기존 초안의 5종 중 3개 `combinations(5,3)`은 정확히 10종의 상품 조합, 16개 지역 출력 중 6개가 반복됨. '16개 독립 가격 비교 조합' 또는 '16개 고유 지역 콘텐츠'라는 주장은 취소. 수정본은 *근조 3단 상품끼리* B201/B203/B205 가격을 비교하는 공통 1종으로 명시하고 축하 C205/오브제 C030는 별도 상품 유형 소개. 비교 본문 및 FAQ 재사용 사실도 별도로 기록.
- **수정 테스트:** [V5 run 41035612269](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41035612269) success. 대표 3페이지 테스트 3개 + 확장 16페이지 검증 테스트 3개, 이미지 5개 해시/치수, 가격링크 수, noindex/robots, 문구 회귀 테스트 통과.
- **현재 Worker:** [V4 run 41035787113](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41035787113) success. 배포 전 현행 활성 버전 `dab3c828-4662-4228-a4b9-21fec3334e14` 및 기존 도메인 미연결 대조 통과. 동일 noindex Worker에 새 버전 `e8bbac15-aec5-4d90-bf58-18669346af20` 실제 배포, 롤백 불필요. 단정 가능한 검증은 HTTP 기반이며 시각적 픽셀 렌더/스크린샷 검수와 혼동하지 않음.
- **실제 원격 응답:** 19/19 HTML HTTP200, 전체 페이지 noindex 헤더/HTML meta, 각 페이지 AI WebP 5개 및 fwith 상품 링크 5개, 실제 이미지 5종 HTTP200/전체 SHA 일치, robots Disallow HTTP200, Sitemap/누락 경로 HTTP404. 영수증 artifact `12968555792` (run 41035787113).
- **원장 시점:** 출처 V4 `data/regions/master.json` 2026-10-22 확인, 현재 상태에 대한 2026-10-30 재수집 아님. 법적 원본 적용일은 미확인. 지역별 실제 사양/배송 조건 조사 없이 고유 지역 콘텐츠를 주장하지 않음.
- **변경 범위:** 수정 확장 소스와 격리 noindex Worker뿐. 이미지·실상품 링크·기존 3페이지 보존. Custom Domain/DNS, Secret, 인증/권한, 운영 색인, IndexNow 전송 변경 없음.

## 2026-10-30 수정본 브라우저 실제 렌더·스크린샷 증거
- **읽기 전용 렌더 QA:** [V4 run 41036075172](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41036075172) 성공, screenshot artifact `12967189850` (데스크톱 1440×900, 모바일 390×844, 총 8장).
- 실제 workers.dev URL에서 Chromium Playwright로 안산시 대표·수원시·수원시 장안구·안산시 단원구 각 2개 뷰포트를 탐색하고 HTTP200/실이미지 5장 전부 naturalWidth>0/가로 오버플로 없음/HTML noindex를 검증. 조사 오류 및 내부 enum이 고객 본문에 재출현하지 않는지도 검사.
- 이 테스트는 실제 브라우저 렌더링과 스크린샷 생성을 검증하며 사람이 각 픽셀·시각 디자인 완성도를 별도 검수했다는 주장으로 확대하지 않음.

## 2026-10-31 전국 286 HTML noindex 실제 배포·검수 (최신)
- source: `sites/wreathprice/verified-regions-nationwide.json` (V4 법정동 상위 지역 코드 284건, 2026-10-22 자료, 법적 적용일 미확인). 사용자에게 배송 가능한 지역을 확인한 수는 **0**.
- 빌드: 기존 대표 3 + 신규 상위 지역 282 + 목록 허브 1 = **286 HTML**. 기존 16개 경기권 추가 페이지도 재활용되는 282에 포함되어 중복 생성하지 않음. 동일 비교/FAQ/AI이미지 재사용으로 독립 고유 SEO 품질을 주장하지 않음.
- V5 [run 41094905895](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41094905895) 성공, artifact `12996141154`. 문법/원장코드 중복0/홈→16개 신규 지역과 /regions/ 허브/허브→전국284지역/내부 링크 0 broken/이미지5 해시/전체 HTML noindex 검증.
- V4 [run 41095222881](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41095222881) 성공, artifact `12995952552`. 수정 전 Worker 100% version `e8bbac15-aec5-4d90-bf58-18669346af20` 대조 → 새 version `7be165ca-d1dc-4d20-9226-5ae0ea6bbc5a` 배포. 정확한 소스 `d23a603f74290f245bda613271bf2ac6d2bc94ac`.
- 실제 `https://sfv52-wreathprice-preview.joseungil.workers.dev`: HTML 286/286 HTTP200, HTML/헤더 noindex, home 직접 지역링크 최소16개/허브 282개 신규 링크, 페이지마다 WebP 5/상품 상세 링크5, 원래 WebP 5장 원격 SHA256 일치, robots Disallow HTTP200, sitemap/없는 페이지 HTTP404. worker preview에는 **canonical 없음**(public canonical 주장 금지). 롤백 실행 없음.
- 미완: 신규 운영 도메인 `wreathprice.nalmada.net`은 연결·검증 대상 아님. DNS/Custom Domain/권한/Secret/소유확인·Google/Naver·IndexNow/공개 index 변경 전혀 없음. 현재 실제 지역별 배송 가능·추가 배송비 미확인 유지.

## 전국 미리보기 모바일·PC 실제 화면 최종 검증
- [V4 run 41095998098](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41095998098) 성공, artifact `12995957893`(스크린샷 12장). Chromium 실제 HTTP 탐색: 1440×900 PC 및 390×844 모바일 × 안산시 홈, 전국지역 허브, 수원시, 서울특별시, 부산광역시, 안산 단원구 = **12개 화면**. 모두 HTTP 200, 390px/1440px 가로 넘침 0, 페이지당 WebP 5/5 로드 성공(이미지 없는 목록 허브 제외), HTML noindex 통과.
- 주의: 자동화 화면 검증·스크린샷 저장 성공이며 화면 디자인을 사람이 주관적으로 검수한 증거는 아님. 검색엔진 공개 운영은 미승인 상태이고, 현 Workers 미리보기는 noindex 상태를 유지함.
