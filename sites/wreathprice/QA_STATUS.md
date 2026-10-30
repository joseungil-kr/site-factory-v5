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
- 운영 preview URL: **없음**. GH 바이너리 업로드는 아직 미완료이므로 운영 또는 미리보기 배포 금지.

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
