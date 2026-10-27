# 한시간스카이 — Site Factory V5(V4 지역원장 재사용) 실제 구현

작업일: 2026-10-27 KST

## 작동 경로 (계획 문서만 만든 것이 아님)

- 새로운 사이트 ID: `onehour-sky`; 도메인: `https://1hrsky.nalmada.net`.
- **기존 V5 실행 엔진:** `python -m v5 plan-check --site onehour-sky` → `python -m v5 build --site onehour-sky --mode preview` → `python -m v5 audit --site onehour-sky`.
- 지역 입력은 V4 `joseungil-kr/site-factory-v4/data/regions/master.json` (2026-10-22 행정안전부 법정지역코드 자료)에서 **광역 16 + 시군구 229 + 비자치구 39 = 284개** 추출. 읍면동은 미포함.
- V5 `v5/onehour_sky_pages.py`가 메인 1페이지 + 지역 284페이지 = **285개 실제 HTML을 번호 순서에 맞춰 생성**. 결과 경로: `dist/onehour-sky/index.html` 및 `2.html`~`285.html` (CI 빌드 산출물).
- 사이트별 입력: `sites/onehour-sky/site.json`, `pages.json`, `services.json`, `rates.json`, `regions.json`, `links.json`, `special-pages.json`, `site-spec.json`.
- 독립 문장 풀: `data/pools/onehour_sky_copy_pool.json`, **152개 고유 문장** (공통72·작업별24·심화56), 작업유형 8개, 지역별 해시 고정 선별.
- 기존 서비스 렌더러 `v5/service_markup.py`에서 한시간스카이만 별도 요금 안내. **1시간만 이용해도 반나절 기준요금 협의**. 금액·부가세 미확인으로 숫자 요금표는 출력하지 않는다.
- 기존 Daysky 가격표와 1,736페이지 검사 경로는 유지, 새 Onehour만 추가된다.

## 사용자 요청 사실과 운영상 보류

- 요청한 제목: `{지역명} 스카이차 1시간 작업, 반일작업 전문 '한시간스카이'`.
- 요청한 슬로건 원문은 사이트 기획 원장에 보존한다. 고객용 히어로에는 '1시간 이내 도착을 목표로 신속 배차, 실제 도착 시각은 확인 후 안내'를 표시한다.
- 1시간 작업은 상담 가능하되 출동·세팅·작업 및 철수 기본비 때문에 반나절 기준으로 견적 상담.
- 전국 상담을 받는 방향으로 구성했지만 실제 기사 배정·전국 1시간 도착 보장을 입증하지 않으며 관련 과장 표현을 만들지 않는다.
- 전용 번호가 없으므로 현재 V5의 다른 스카이차 사이트에서 사용 중인 `010-5322-1952`를 **검토용 프리뷰에 한해 잠정 적용**했다. 새 브랜드 대표번호로 확정된 것은 아니다.
- 기존 Daysky 사진 3개 WebP는 원본 사진 2개에서 나온 구성으로, 새 브랜드 재사용 권리 확인 전이다. 사용 승인 플래그 `imageAssetsApproved=false`를 유지한다.
- SEO 실질 가치 측정은 지역별 작업·장비·상담 이력 등 추가 정보 확보 전이며, **전체 285페이지 자동 색인 공개를 승인한 것은 아니다.**

## 검수/배포 안전장치

- `site-spec.json`의 `approved=true`는 **V5 비색인 프리뷰 생성 범위만** 승인; 배포/검색 공개와 구분.
- `publicIndexingApproved=false`, `publishEnabled=false`, `indexNow.enabled=false`, `imageAssetsApproved=false`, `analytics.enabled=false`.
- 프리뷰는 `noindex,nofollow`, `robots.txt Disallow: /`, canonical·sitemap·IndexNow 생성하지 않음.
- GitHub Actions: `.github/workflows/onehour-sky-preview.yml`에서 V5 단위 회귀 검사 → 실제 사이트 빌드 → V5 HTML·링크·중복감사 → 결과 HTML 수·404·robots 검증 → 미리보기 아티팩트 업로드.
- **실제 Cloudflare DNS, Worker, Custom Domain 및 검색엔진 제출은 아직 실행하지 않음.**
- 신규 사이트 페이지 285개는 메인에 병합하기 전 PR 검토 브랜치에서만 생성.

## 기존 구현 재사용의 경제성

독립 신규 엔진/플랫폼/AI API 없이 검증된 V5 Python 정적 HTML + Cloudflare Workers Static Assets 방식을 사용한다. V4 법정 지역명 원장만 재사용하며 기존 꽃배달/당일스카이/빠른스카이 소스와 공개 도메인은 수정하지 않는다.

## 후속 조건

1. CI 녹색 실행과 HTML 아티팩트에서 V5 최종 검수 기록 확보.
2. 1시간 기준요금/출장·설치·철수 포함범위와 전용 전화번호 확인.
3. 실제 사진의 한시간스카이 브랜드 재사용 승인과 배차 범위 검증.
4. 격리된 새 Worker에 **noindex** 프리뷰만 배포하고 HTTPS·404·이미지를 읽어 검증.
5. 사이트 검색 공개는 별도 SEO 품질·기사 배정 현실성·사진 권리 검토 후 대상 지역부터 순차 진행.

`SITE_CREATION_PROTOCOL.md`에 따라 메인 병합·상용 배포·IndexNow는 별도 단계이며, 이 문서는 빌드 가능한 V5 실물 구현 근거를 기록한다.
