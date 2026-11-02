# 오늘꽃배달 — 전국 5,070개 문서 공개·실서버 검수 인수 기록

확인 기준일: **2026-10-31 KST**. 사용자가 승인한 도메인 연결과 공개 전환 범위. 다른 사이트·새 Secret·권한·소유확인·결제 변경 없음.

## 공개 결과와 경계
- 공개 호스트: **https://todayflower.nalmada.net/**
- Search 공개: 해당 호스트에서만 HTML `<meta name="robots" content="index,follow">`, 페이지별 자기 canonical, `robots.txt` Allow, **5,070개 URL sitemap.xml** 200.
- 별도 비노출 호스트: https://sfv56-todayflower-preview.joseungil.workers.dev/ — HTTP `X-Robots-Tag: noindex`, HTML noindex, canonical 없음, robots.txt Disallow, sitemap.xml 404.
- 기존 Worker **`sfv56-todayflower-preview`**만 갱신. 최종 활성 Worker 버전 **`4b35c279-adfb-41e7-96f8-a82cd71e2442`**. 기존 모든 다른 Custom Domain 바인딩 변화 없음.
- 공개는 **Cloudflare Worker의 정확한 Host 분기**로 처리함. 생성 아티팩트의 HTML 원본과 `site.json.publishEnabled=false`는 SHA 검증·비노출 기본 상태로 유지하며, `todayflower.nalmada.net` 요청에 한해서 index·canonical을 부여함. workers.dev, 알 수 없는 Host, 404는 검색 차단.
- 사이트맵은 2026-10-22 고정 법정동 원장으로 생성된 **5,070개 실제 문서 경로**만 열거한다. 404번은 지역 문서가 아닌 HTTP 404: 번호 1~403, 405~5071.
- **Search Console/Naver Search Advisor 소유확인·사이트 등록, IndexNow 제출, 실제 검색엔진 색인·순위는 이번 작업에서 하지 않았으며 확인되지 않음.** 기술적 index 허용은 색인 완료가 아님.

## GitHub 저장·빌드·배포 증거
- 기존 Todayflower 브랜치: `site/todayflower-nalmada-pilot-20261030`.
- 최신 빌드·QA 소스 SHA: **`0ca5705aa12950da571f089b2d4ac7256111f77e`**. 이전 SHA `0392fd39fd8a1aadd08a34d8ef96b645db7b337e` 대비 전국 메뉴를 꽃 종류/상품·가격/주문 상담 앵커로 수정했으며 기존 이미지 5장·주문 SKU를 보존.
- V5 QA 실행: https://github.com/joseungil-kr/site-factory-v5/actions/runs/41185803963 — **success**.
- 5,070 페이지 검수 아티팩트: ID **`13036248347`**, SHA256 **`16b52597fe77b0b4311ea21ad5daf6c5193af94346f8dc8df9834e676003a180`**. V5 정적 HTML 5,071개(404 포함), 정적 파일 5,087개에 대한 SHA256 매니페스트 확인. 고해상도 AI WebP 5종(1448×1086) 유지.
- Cloudflare 도메인 연결: V4 run https://github.com/joseungil-kr/site-factory-v4/actions/runs/41185837366 — **success**; 이전 noindex 버전 상태에서 승인된 정확한 호스트를 검증하고 바인딩. Cloudflare HTTPS 응답 7건 확인.
- 공개 분기 Workflow: `joseungil-kr/site-factory-v4`, `.github/workflows/todayflower-public-release.yml`.
- 최종 Workflow 커밋: **`0afab9b58ff97f1b4196883125c2c2245e3c6f57`**.
- 공개 배포: V4 run https://github.com/joseungil-kr/site-factory-v4/actions/runs/41186459796 — **success**. 이전 Worker 100% 버전 확인, Cloudflare 업로드, 공개/비노출 분기, 실서버 SEO 검증, 최종 Worker 100% 버전 readback 모두 통과. 실제 롤백 단계는 **skip**.
- 공개 배포 검수 아티팩트: **`13037275596`**, ZIP SHA256 **`58b6b4054c63996ed99230b69c8108f2adf99fb1d0c1eb2676115b72b875455b`**. 실제 다운로드 ZIP·JSON·스크린샷 별도 확인.
- 스테이징까지의 실패는 모두 동일 Worker의 이전 버전으로 자동 롤백했음. 마지막 성공 실행은 host-specific index 배포 버전 `4b35c279-adfb-41e7-96f8-a82cd71e2442`이며 noindex 프리뷰 보존.

## 독립 실서버 검증 내용
- Public HTTPS HTML 표본 **18개**(1/2/3/4/10/28/29/33/34/100/1000/1999/403/405/730/2500/4060/5071). 모두 HTTP 200, 메타 `index,follow`, 올바른 자기 canonical 1개, 실제 판매처 상품 직접 링크 존재 및 검증된 원본과 일치.
- HTML 바이트 동일성: **18/18은 바이트 단위로는 원본과 다름**. 원본과 실서버의 **방문자 표시 문구 및 SKU 구매 링크는 18/18 일치**. 이는 공개 호스트 전달 계층의 추가·변형 가능성이 있어 원본 바이트 동일성을 주장하지 않고 별도 판정한 결과.
- `robots.txt` HTTP 200·Allow, `sitemap.xml` HTTP 200·유일 URL 5,070개·404번 제외, 별도 오류 URL HTTP 404.
- 판매처 상품과 별도의 AI 이미지 WebP 5개 실제 200·원본 바이트 일치. 그 외 상품별 현재 재고/배송 가능성은 미확인.
- workers.dev HTTP 표본 7개: 사이트 200·robots Disallow·sitemap 404·기타 404, 전부 noindex.
- 실제 Chromium 공개/비노출 호스트 각각 4경로 × 390/1440px = **16개 화면**: HTTP 200, 가로 넘침 없음, 제목 1개, 실제 SKU 주문 링크, 메뉴 앵커, 1448×1086 AI WebP 5장 정상 디코딩. 모바일 및 데스크톱 원본 스크린샷 `13037275596`에 보존.
- 디자인 육안 확인: 공개 홈 PC/모바일과 마지막 전국 페이지 PC/모바일을 직접 확인했으며 이미지·메뉴·본문이 표시됨. 긴 지역명은 모바일에서 여러 줄로 정상 줄바꿈됨.

## 품질·출처의 한계(확인 사실과 구분)
- 지리 근거는 **V4에 저장된 2026-10-22 고정 공식 법정동 ZIP** SHA256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`. 최신 공식행정구역을 재조회하지 않았고 행정동과 법정동을 혼용하지 않음.
- 지역별 당일배송 가능 여부·실제 마감·추가요금·재고·현지 꽃집 지점은 독립적으로 검증하지 않았고, 페이지는 상품별 최종 판매처 확인을 요구한다.
- 5,070개 페이지의 본문 **전체 동일 해시 검사**를 적용했으나 의미 유사도는 **고정 1% 표본 51개 / 1,275쌍의 최대 Jaccard 약 43.18%**, 경고 1건. **5,070개 의미·지역 차별성 전수 사람 검수**가 아니라는 한계. 대규모 유사 페이지의 검색 품질/미색인 위험이 있으며 실제 검색엔진 수록을 약속할 수 없다.
- 새 Secret, 권한, 도메인 소유권 인증, 기존 다른 사이트, 별도 도메인 설정, 결제는 변경하지 않았다.

## 향후 별도 작업
실제 검색수록/유입·전환 측정, Search Console/Naver 사이트 등록(기존 소유확인 계정·인증 자료 필요), 지역별 배송 가능 조건의 증거 확보와 5,070페이지 문서 품질 점검.


---

## 2026-11-02 후속2 인계 독립 점검 — 마지막 운영 배포 추가 확인

이 항목은 **2026-11-02 KST 후속2 인계 시점에 GitHub를 새로 조회한 결과**다. 위 2026-10-31 초기 공개 배포의 당시 버전과 혼동하지 않는다. 저장·검수 이외 운영 변경은 없다.

### 마지막 성공 운영 배포

- **V4 Actions 최신 확인 성공:** [run #41209263178](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41209263178), 2026-10-31 **23:16 KST** 완료, workflow source SHA `9aeeed9f1aac5da45f3b771a6ffd610db7b83ecd`.
- **최신 성공 Worker 활성 버전 기록:** `79e425cf-2592-40ec-a55b-7ad383d132f1` (run job `124560625584` Cloudflare 100% 활성 버전 GET 영수증). 위 원래 기록의 `4b35c279-...`는 직전 역사적 버전이다.
- 운영 호스트 `https://todayflower.nalmada.net/` 홈 `<head>`에 네이버 태그 `<meta name="naver-site-verification" content="d970eeb70abc7b36cbcc02fadd9362c5c57fcb46" />` 정확히 **1개**, 대표 비홈 페이지에는 **0개**를 배포 Workflow의 실제 실서버 HTMLParser 검사로 확인. 공개는 `index,follow`·자기 canonical·sitemap 5,070 URL, 별도 `workers.dev`는 계속 noindex·robots Disallow·sitemap 404.
- 동일 V4 Workflow에서 공개 HTML 18개·이미지 5개·비공개 7 HTTP 검사 PASS(`TODAYFLOWER_PUBLIC_INDEX_5070_CANONICAL_SITEMAP_PASS 18 5 7`), Chromium 390/1440px 합계 16개 화면 PASS(`TODAYFLOWER_PUBLIC_16_SCREEN_390_1440_PASS 16`). 새 Worker/DNS/Secret/권한 생성 없음.
- Artifact ID `13045292821`, 업로드 ZIP digest `sha256:417e0ab5c260838cd55c1827f39c6a98afefcb64c37843d74d99844463f6b631`.
- **한계:** 이 인계 환경에서 현재 도메인 DNS 해석이 실패해 2026-11-02의 신규 라이브 HTTP 재조회는 하지 못했다. 위 정보는 2026-10-31 성공 Actions의 실제 실행 로그와 SHA를 직접 재조회한 범위이다. 네이버 Search Advisor `statz`의 실제 소유확인 버튼·사이트맵 등록 성공, 실제 검색엔진 색인은 확인되지 않았다.

### 이미지 5개 독립 GitHub 원격 바이너리 검증

2026-11-02 브랜치 커밋 `7365337804f0f366b8c0e4c32573c51ef03d8e73`에서 각 파일의 GitHub 원격 base64 바이트의 RIFF/WEBP/VP8 frame header를 개별 확인. 다섯 장 모두 실제 **1448×1086 픽셀**, 원격 blob SHA와 RIFF 전체 바이트 길이가 `site-spec.json`의 기록에 맞는다. 대상은 `gift-bouquet.webp` (167,766B), `opening-plant.webp` (140,286B), `celebration-wreath.webp` (272,178B), `condolence-wreath.webp` (149,518B), `flower-wrapping.webp` (135,190B). **96×141px 단순 업스케일이 아니라는 과거 원본 사용 기록과 별도로, 최종 파일의 실제 해상도를 이번에 직접 확인**했다.

생성 원본의 정확한 `image_gen` 호출 프롬프트·생성 UTC 타임스탬프는 `site-spec.json images.provenance`에 없다. gen_id와 원격 바이너리 존재만으로 V5 `main`의 신규 이미지 출처 검증 규칙을 충족했다고 말하지 않는다. 원본 프롬프트/UTC를 추측으로 보완하거나 출처 정책을 우회하지 않는다.

### 소스/운영 상태 정합성 — 후속 체크 항목

- 해당 V5 브랜치는 2026-11-02 기준 `main`과 diverged: **ahead 101 / behind 2**, merge-base `d4f58c660655afc5f8359fe0fa70b98fc7588309`; 작업자1용 PR은 확인되지 않음. 운영은 V4의 고정 V5 소스 `0ca5705aa12950da571f089b2d4ac7256111f77e`를 인출해 배포한 별도 루틴.
- `site.json.publishEnabled=false` 및 `site-spec.json.publishPolicy.production=false`, `rollout.publicReleaseApproved=false`는 **미리보기 정적 아티팩트의 기본 차단/이전 승인 상태**로 남아 있다. 실운영은 V4 Worker의 정확한 hostname 분기로 index이며, 단순히 false 값을 모두 true로 바꾸면 원본 noindex 안전망을 훼손할 수 있다. 원장과 운영 이중 상태를 명시적으로 모델링하기 전 값 변경 금지.
- 전체 5,070페이지의 실질 정보 가치 검수는 기존 고정 1% **51페이지 / 1,275쌍** 수준. 유사도 최고 약 **43.18%**와 경고 1건만 검증됐으며 5,070개 전체 문서의 실지역 배송 가능성을 검증한 것이 아님. 중복 문서/저품질 SEO 위험 모니터링 필요.
- 2026-10-31 성공 QA: [V5 run #41185803963](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41185803963). 새 배포·IndexNow/Google 재제출·전체 재생성·신규 이미지 교체는 불필요하므로 수행하지 않음.

### 이어서 처리할 순서

1. Naver Search Advisor(기존 `statz`)의 **소유확인 및 사이트맵 실제 성공 영수증** 확인. 메타 삽입 성공만으로 등록 완료를 주장하지 않기.
2. 이미지 생성 원기록의 정확한 프롬프트·생성 시각 회수 또는 출처 미완료를 그대로 유지. 출처검증 우회·가공 금지.
3. 도메인 HTTP가 가능한 환경에서 현재 운영 `index`·대표 canonical·sitemap/robots·workers.dev `noindex` 재검증.
4. 실제 검색 수록·전환과 지역별 서비스 조건을 소규모로 검증한 뒤 전국 5,070페이지 문서 가치/품질 개선 여부 판단. 전국 재발행을 먼저 반복하지 않음.

이번 인계 기록 자체는 **문서만 수정**하며, 운영 Worker/도메인/비밀키/검색 설정/상품 가격과 주문 링크는 건드리지 않는다.
