# 한시간스카이 1hrsky.nalmada.net — 제작 착수 및 독립 검수

- 기준일: 2026-10-27 KST
- 대상 브랜드: **한시간스카이**
- 목표 주소: **https://1hrsky.nalmada.net/**
- 단계: **PLAN / POOL / EDITORIAL DRAFT 저장**. GENERATED / QA BUILD / DEPLOYED / LIVE_HTTP / INDEXNOW **미완료**.
- 기존 운영: `daysky.nalmada.net`, `quicksky.nalmada.net`, 기존 flower/plants Worker·DNS 불변.
- 기준 참조: V5 `SITE_CREATION_PROTOCOL.md`, `v5/service_model.py`, `v5/service_markup.py`, `data/pools/daysky_shared_pool.json`, `feature/quicksky-nalmada-com-20261027`. 다른 브랜드 본문을 복사하지 않음.

## 사용자 확정 정보와 미확정 정보

**확정된 주문 내용**
- 브랜드 및 도메인: 한시간스카이 / `1hrsky.nalmada.net`
- 최초 제안 슬로건 원문: “신청 한시간 이내 도착, 1시간 작업도 가능한 빠른 스카이 전문기업”
- 1시간 작업도 상담할 수 있지만 기본 출동·세팅·작업비용 때문에 반나절 요금 기준 청구 및 전화 협의.
- 가장 가까운 기사부터 배차를 시도하며 전국에서 문의받는 구상.
- 지역 페이지 제목: `{지역명} 스카이차 1시간 작업, 반일작업 전문 '한시간스카이'`.

**실증되지 않은 항목**
- 전국 모든 곳 1시간 이내 도착의 실제 보장 능력, 특정 지역의 실제 기사/장비 배치 상태.
- 전용 전화번호: 기존 Daysky/Quicksky에 확인된 `010-5322-1952`는 **한시간스카이용 확인 없이 재사용 금지**.
- 가격 숫자·VAT 여부·휴일/야간 할증·대기/취소 요금.
- 실제 기사와 계약·보유 톤수·도달 높이·출동 가능 지역·사례 및 고객 후기.
- 이미지 재사용 권리: Daysky/Quicksky 작업 사진 원본 2개에서 나온 WebP 3개는 새 브랜드 이용 권한을 별도로 확인할 것.
- 전국 전체 페이지 수·공식 지역 원장·지역 실질 콘텐츠.

## 고객이 읽는 핵심 문구 가이드

- 히어로: “신청 후 1시간 이내 도착을 목표로, 1시간 작업도 상담하는 빠른 스카이”
- 부연: “실제 도착 예상 시각은 지역별 기사·장비의 배정 가능 여부와 교통 상황을 확인한 후 안내합니다.”
- 요금: “1시간 작업도 반나절 요금 기준으로 견적을 협의합니다. 출동·세팅·작업·철수 기본비용을 함께 확인해 주세요.”
- 전국: “전국 상담 접수. 현장과 가까운 기사 배정을 우선 검토하지만 출동 가능 여부는 현장별로 확인합니다.”
- CTA: “작업 주소·높이·내용·예상 시간·현장 사진을 준비해 전화로 문의하세요.” (전용 번호 확인 후 `tel:` 바인딩)

원문 슬로건은 요청사항으로 보존하되, 방문자 화면에서는 무조건 1시간 도착 **보장 문구로 단독 노출하지 않음**.

## 저장된 실물

1. `sites/onehour-sky/site-spec.json`: V5 강제 사전 기획 필드와 단계별 차단 조건. 계획은 `approved=false`, `targetPageCount=null`이므로 배포/실제 빌드 승인으로 해석 금지.
2. `data/pools/onehour_sky_copy_pool.json`: 공통 9버킷×8=72개와 작업별 8유형×3=24개, **총 96개 문장**.
3. `sites/onehour-sky/drafts/seed-pages.json`: 3개 **원고 예시** (메인·안산·강남), 각 제목=H1, 본문 6/4/4섹션, FAQ 포함. 운영 사이트 빌드에 포함하지 않는 파일.

## Readback / 정적 초안 검수 결과

- GitHub 재조회에서 파일 3개 모두 확인.
- POOL 96개 중 완전 일치 중복 0개.
- 메인/안산/강남 제목과 H1 각각 일치.
- 각 본문 section paragraph 길이 80자 이상.
- 예시 3개 모두 기본요금 반나절 기준과 배차 상담 문구 포함.
- 보장형 도착 문구 및 구체적인 미확정 가격 숫자 없음.
- **실제 `python -m v5 plan-check`, 빌드/HTTP/이미지 시각·SEO/유사도 전량 검사는 아직 실행하지 않음.** 승인 전 게이트를 강제로 통과시키지 않음.

## 다음 실행 차례 (게이트 유지)

1. 공식 지역명 원장으로 전국 시군구 대상 실제 개수·중복·폐지명 검증, 방문자에게 가치 있는 최소 단위 선정. 허위 실적/지형 서술 방지.
2. 사용자의 전국 범위와 원하는 생성 단위를 반영해 **전체 targetPageCount**를 확정하고 `site-spec.json` plan-check를 통과시킨다. 예시 3개를 전체 목표로 취급하지 않는다.
3. 전용 연락번호와 실제 서비스/사진 권리를 확인한다. 승인된 경우에만 `site.json`·`pages.json`·`services.json`·`rates.json`·`regions.json`를 준비한다.
4. **요금 렌더러 수정 필요**: 기존 Daysky의 1시간 별도 숫자 요금표를 복사하지 않는다. Quicksky의 `pricingPolicy=consult-only` 흐름을 참조해 1시간 작업도 반나절 기준으로 비용을 협의하는 별도 표기 및 숨김 처리, 범위 분리 회귀 테스트.
5. 날짜/지역/톤수/가격/전화/비용/현장표현 QA 후 생성. 초기 preview는 `noindex,nofollow`, `robots.txt Disallow: /`, sitemap/IndexNow OFF.
6. QA 승인 후 **격리된 신규 Worker**를 만들고 DNS/Custom Domain 변경은 별도 확인/승인 범위에 따라 진행. 기존 domain-bound Worker의 보호 workflow를 우회해 재실행하지 않음.
7. 실측/운영 데이터가 없는 유사 지역 페이지를 한꺼번에 색인 공개하지 않는다. Google의 doorway/scaled content abuse 정책에 따라 실제 이용 가치와 지역 고유 정보를 갖춘 페이지부터 공개한다.

## 기술 선택

- 최저비용: **기존 V5 Python 표준 라이브러리 + Cloudflare Workers Static Assets 모듈 일부 재사용**. 신규 프레임워크/AI API/DB 도입 불필요.
- 관련 오픈소스 조사: [Cloudflare Workers 공식 템플릿](https://github.com/cloudflare/templates) (MIT 라이선스, Astro 정적 SEO·사이트맵 등), [Astro](https://github.com/withastro/astro) (콘텐츠 중심 프레임워크). 이번 프로젝트는 V5 엔진이 이미 존재하므로 도입/포크 불필요.
- 검색 품질 원칙: [Google 스팸 정책](https://developers.google.com/search/docs/essentials/spam-policies?hl=ko).

> 이 문서는 실제 생산 배포 완료 보고가 아니라 검증 가능하고 안전한 신규 사이트 제작 시작 기록이다.
