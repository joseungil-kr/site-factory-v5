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
