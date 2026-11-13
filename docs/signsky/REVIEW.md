# 간판스카이 검수 인계 — 2026-10-28

## 범위와 결과

`feature/v52-signsky`, V5 main `d4f58c660655afc5f8359fe0fa70b98fc7588309` 기준. 공통 파일 수정 없이 전용 사이트·문장 풀·생성기·Worker 래퍼·검수 workflow만 추가했다.

69개 시·구 × 간판교체/현수막설치 2목적 + 홈 = **139 URL**. 기존 원장 1,732동을 모두 시·구 안내에 포함한다. 이는 동별 3,464 문서 생성이 아니다. 지역명 원장은 법정동·행정동 혼합 가능성이 있어 개별 분류를 새로 검증했다고 주장하지 않는다. 읍·면 등 원장 밖의 지역을 추가하지 않았다.

차별점: 장비 가격표 중심의 기존 사이트와 달리 간판 철거/교체 공정, 현수막 양 끝 고정점, 작업팀 일정, 진입 사진, 목적별 상담 체크리스트를 중심으로 구성했다. 고객이 체크한 항목은 브라우저 내 기본 checkbox 상태일 뿐 서버에 제출하지 않는다. 실제 상담·주문·전화는 실행하지 않았다.

## 실제 검색 조사

2026-10-28 UTC, 비로그인 IAB. Google 결과 URL의 관측 타임스탬프는 09:19:30 UTC(1793179170601ms), Naver는 이어진 같은 조사 세션이며 정확한 초 단위 시각은 저장하지 않았다. 검색 순위는 당시 화면의 관측이며 재현 가능한 고정 순위를 보장하지 않는다.

1. Google `오산 간판교체 스카이차`.
   - 관측 웹문서 순서: bros-m.shop 「오산시 스카이차 - 오산 안전하고 전문적인 고공 작업 서비스」 → Naver 탐색 「오산스카이차 고층 간판 작업 현장」 → wormsz.tistory.com 「오산 궐동 스카이차 완벽 가이드」 → 「오산 스카이차 임대」 → Naver dsln0414 「흑석동 간판 설치 작업 현장 후기」.
   - 관측 범위에서 광고/지도 블록은 확인되지 않았다. 검색 스니펫은 원문 분석으로 계산하지 않았다.
   - 실제 클릭한 4번째 원문: https://ace-wooseungsky.com/local/오산_스카이차/ . `ERR_HTTP_RESPONSE_CODE_FAILURE`, **미분석**. 나머지 미방문 문서의 원문 URL은 확정하지 않았으며 검색결과 제목/호스트만 기록했다.
2. Naver `수원 현수막설치 스카이차`.
   - 광고: 창조스카이(changjosky.imweb.me), 송스카이(sky2151.com), 숨고. 광고 클릭하지 않음.
   - 웹문서 1: https://xn--9t4b21ghxefvc.kr/작업/경기-수원시팔달구-간판-스카이차
   - 웹문서 2: https://xn--9t4b93dk7a19nnlj.com/작업/경기-수원시-간판-스카이차 — 원문 미방문.
   - 웹문서 3: allynai.co.kr 수원시 영통구 간판·현수막 문서 — 원문 미방문.
   - 이어 블로그 2건, 플레이스 「우리사다리차」, 추가 웹/블로그와 쇼핑 영역. 쇼핑 표시가격은 사용자 가격으로 가져오지 않았다.
   - **분석 완료 원문은 웹문서 1의 1건**. 제목은 지역+간판·현수막+스카이차+비용·견적, 가시문자 2,166자(접힌 FAQ 포함 여부에 따라 달라짐), 이미지 요소 8개, 전화 링크 5개. 지역/목적 H1 → 작업 범위 및 기사·시공 역할 구분 → 접근/장비/비용 섹션 → 사진 → 인근지역/다른 작업 → FAQ → 전화 CTA. 실제 예약 폼이나 결제 흐름은 관측하지 않았다.

벤치마크에서 구조만 채택했다. 경쟁사의 즉시출동·인증·경력·장비높이·무료견적 주장은 새 사이트에 옮기지 않았다. 저장된 원문/검색 상태는 `evidence/benchmark-source.txt`, `evidence/naver-serp.txt`.

## 출처 및 운영 경로 재사용

- 전화 `010-5322-1952`: V5 `sites/daysky/site.json`.
- 1톤·3.5톤·5톤 상담 범위: V5 `sites/daysky/services.json`. 보유·도달높이를 새로 보증하지 않는다. 숫자 가격은 노출하지 않는다.
- 사진: `assets/library/daysky/skycar-hero.webp`, `skycar-truck.webp`. 출처/해시: `docs/DAYSKY_PHOTO_PROVENANCE.json`. 사용자 기존 운영 자료 재사용 위임에 따라 사용, 새 촬영이나 간판스카이의 특정 현장 완료 사례로 표현하지 않음.
- 지역: `data/regions/seoul_gyeonggi_current_dong.json`, V4 NAME_CANDIDATES 유래 SHA256 `057679a9a6312dbb4dd284d2ca42856d40a828239b2483540a7000b630fc30eb`.
- 일반 작업 문장: V5 `data/pools/daysky_work_pool.json` 중 signage/advertising, shared pool 중 가격 제외 9그룹을 전용 `sites/signsky/copy-pool.json`에 복사해 고정. 기존 페이지 전체 복제는 없음. 풀 재사용은 숨기지 않으며 교차 유사도 별도 측정.
- V5 검증 성공: https://github.com/joseungil-kr/site-factory-v5/actions/runs/40643531356 (Daysky 1736-page build).
- V4 clone main `223b9348f32b700af98645d034943772d590aaba`, README/AGENTS/STATUS/PROJECT 읽음. 운영 성공 경로는 main보다 `ops/v5-isolated-staging-20261024` 브랜치가 최신.
- V4 실제 성공: https://github.com/joseungil-kr/site-factory-v4/actions/runs/40642326046 , source `4526b53cb0e75c1fd1590bb41c2425298f4d9e18`, `.github/workflows/v5-quicksky-one-home-public.yml`. V4 Actions의 기존 자격증명으로 V5 특정 SHA checkout → 기존 Worker 신원/이전버전 GET → Wrangler 4.148.0 → 공개 HTTP/404/preview noindex 확인 → 실패 시 이전버전 100% 원복 구조를 확인했다. 다른 사이트의 Worker를 이 사이트 대상으로 사용하지 않는다.
- V5 main과 Quicksky 브랜치, V4 main의 `.agents/skills`는 Git tree에서 발견되지 않았다. 파일을 읽었다고 주장하지 않는다. V5 AGENTS 및 SITE_CREATION_PROTOCOL은 읽고 plan-check를 통과했다.

## 검증 증거

- `python -m v5 plan-check --site signsky` PASS.
- `python scripts/signsky.py build --mode public` 및 `audit` PASS: canonical/robots/sitemap 139, 제목 H1/전화/내부 링크/이미지 경로 전수 확인. 이어 preview 재생성으로 noindex 복원.
- 고정 seed 20261028, 지역문서 138개 중 ceil(1%)=2, 표본 대 전체 274회. 추가 지역문서 전체 9,453쌍: 본문 최대 0.314394, 전체 가시본문 최대 0.450342. 기준은 공백 제거/소문자화 char-5gram Jaccard <0.49.
- Daysky 전체 1,736문서 대비 같은 2표본 3,472회, 최대 0.200870. 이 수치를 모든 사이트 교차 전수 통과로 해석하지 않는다. Quicksky/Onehour 전체문서 교차 검사는 수행하지 않았다.
- 로컬 HTTP 139 URL 모두 200, 누락 URL 404. `evidence/local-http.json`. 공개 HTTP 확인은 아님.
- PC 1440×1000: 홈, 수원 팔달구 현수막 상세. 모바일 390×844: 홈, 오산 간판교체, 수원 현수막 상세와 상담 체크리스트. 가로 넘침 없음, 이미지 naturalWidth>0/object-fit cover, 체크박스 반응과 목적 링크 이동 확인. 전화 href 확인, 실제 통화하지 않음. 스크린샷 `evidence/*.png`.
- `node --test sites/signsky/worker.test.mjs` PASS: 정확한 공개호스트만 index 허용, preview sitemap 차단, 404 noindex.

## 배포 전 부모 확인 / 원복

희망 호스트 `signsky.nalmada.net`, 독립 Worker `sfv52-signsky`. Cloudflare DoH A 조회 HTTP200 / Status3 NXDOMAIN (2026-10-28). DNS 한 종류의 부재가 Worker/route 미사용을 입증하지는 않는다. 실제 zone DNS·routes·workers/domains 및 Worker 이름 충돌을 기존 인증된 운영 경로에서 **GET으로 먼저 확인**해야 한다. 충돌 시 중단하고 다른 보유 서브도메인 선택. 기존 레코드 덮어쓰기 금지.

현재 config `SIGNSKY_PUBLIC=0`, routes 없음, 배포 workflow 없음. 검수 artifact workflow만 추가했다. 공개 빌드는 로컬 파일 생성만 수행하며 권한이나 배포를 부여하지 않는다. 부모 검수·병합순서 조율 이후 기존 V4 Actions 경로를 통해 독립 Worker 첫 noindex baseline 배포 → 버전 ID 기록 → 요청 호스트만 연결 → 공개 build/flag 설정 → 139 URL 및 404/robots/sitemap/이미지 읽기 검수 순으로 진행한다. 기존 안정 버전이 없을 때 기존 사이트 Worker를 원복 대상으로 삼지 않는다. 실패 시 Signsky baseline 버전 100% 복원, HTTP noindex 확인. first baseline 생성 전은 배포 전 상태이며 되돌릴 기존 서비스 변경이 없다.

IndexNow는 공개 HTTP 확인 뒤 사이트 독립키로 부모가 처리한다. 기존 사이트 키를 무단 재사용하지 않으며 현재 제출 0건. Naver/Google 소유권 인증을 새로 확대하지 않았다.

단계: PLAN/POOL/GENERATED/QA 완료, COMMITTED는 인계 SHA 참조, DEPLOYED/LIVE_HTTP/INDEXNOW 미실행.

한 차례 `0.0.0.0` 검수 서버는 미공개 자료 외부 노출 위험으로 자동승인 검토 거부(미실행). 더 안전한 127.0.0.1 자동할당 포트 서버로 화면 검수 완료. 해당 거부를 우회하거나 네트워크 보안 설정을 변경하지 않았다.


## 2026-10-28 — Public-candidate metadata/audit improvements and Cloudflare preflight

Latest source candidate: `141e7e2ff913e6cd1b218dbbebada25257a91160`.

- Replaced repeated small intro-only meta descriptions with region + work-purpose + intro + intent-specific task checklist. CI verifies **138/138 regional descriptions unique**.
- `scripts/signsky.py audit` now verifies exact robots contents for public/preview, each canonical and robots directive, unique 139 manifest URLs, and that the sitemap's complete unique URL set exactly matches all 139 canonical public URLs. Preview must have `Disallow: /` and no sitemap. 404 stays noindex.
- `signsky-review.yml` builds/audits both public and preview modes without deploying, archives the public candidate separately, then rebuilds preview and tests host isolation. [Latest CI run](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40667348714): **SUCCESS** at SHA `141e7e2ff913e6cd1b218dbbebada25257a91160`; artifact `signsky-review`.
- Same existing V4 Actions credential context, read-only preflight [run #40668271943](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40668271943) confirms:
  - active `nalmada.net` zone/account identity and existing Flower binding match,
  - `signsky.nalmada.net` has no existing Worker Custom Domain binding,
  - Worker script name `sfv52-signsky` does not exist,
  - public A/AAAA/CNAME lookups return NXDOMAIN.
  - **DNS-record API GET returned HTTP 403 Authentication error; Workers Routes GET returned HTTP 403 “No access to the specified resource.”** Thus we cannot certify there are no hidden existing DNS records or route entries from the Cloudflare inventory.
- No Cloudflare writes, DNS/routes/custom-domain changes, Secrets, token changes, OAuth, ownership tags, or production deploy were performed by the preflight.
- Read-only scope needed to finish collision inspection: existing Cloudflare API token needs Zone-scoped `DNS Read` and `Workers Routes Read` for `nalmada.net`. Custom Domain creation/deployment also requires `Workers Routes Write` for that zone (and existing Worker Scripts write permission, already demonstrated by prior V5 deployments). No permission has been added.
- Public-candidate build and quality gate are ready, but **production custom-domain attachment is intentionally blocked** until these permissions are separately approved and the read-only inventory confirms no conflict. We can deploy an isolated `noindex` `workers.dev` preview without DNS/route changes while this is unresolved.
- Cross-site comparison limitation remains: full within-site 9,453-pair audit passed; Daysky was sampled against 1,736 pages (3,472 comparisons), while full cross-site comparisons against Quicksky/Onehour were not run. This is disclosed, not claimed as a pass.
