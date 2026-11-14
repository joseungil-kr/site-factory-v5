# 사이트팩토리 V5 — 등록 도메인별 Worker 운영 규칙 (2026-11-04)

**사용자 승인 원칙:** 앞으로 등록 도메인(Cloudflare zone/등록 가능한 원 도메인)마다 기본적으로 Worker 1개를 유지하고, 루트와 모든 하위 서브도메인이 동일한 Worker를 공유한다. 서로 다른 루트 도메인의 사이트를 동일 Worker 묶음에 넣지 않는다. 기능적으로 해당 Worker를 공유할 수 없는 명확한 독립 실행·보안 격리 요구가 있을 때만 예외를 검토한다.

## 1. 기본 배치

| 루트 도메인(Zone) | 공유 Worker 명칭 예시 | 공유할 호스트 |
|---|---|---|
| nalmada.net | `sfv5-nalmada-domain` | `nalmada.net`, `clinicflower.nalmada.net`, `*.nalmada.net`의 검증된 하위 호스트 |
| fwith.kr | `sfv5-fwith-kr-domain` | `fwith.kr`, `*.fwith.kr` |
| baeksefood.com | `sfv5-baeksefood-com-domain` | `baeksefood.com`, `*.baeksefood.com` |

- **Worker 이름은 예시 및 등록 원장값**이다. 기존 계정에 이미 도메인 담당 Worker가 있으면 새 Worker를 만들지 않고 재사용·검증한다. 이름에 preview/test가 있다는 이유로 미사용이라고 판단하지 않는다.
- 실제 등록 도메인 경계는 `co.kr` 등 공공 접미사를 고려하여 **정확한 Cloudflare zone 식별값**으로 결정한다. 마지막 두 문자열만 잘라서 도메인을 추측하지 않는다.
- 사이트 입력 원장은 `workerZone`(예: `nalmada.net`), `workerName`, `hostname`, `siteId`, `deliveryMode`, `indexStatus`, `sourceSHA`를 식별한다. 새 기능의 실행형 검증이 완성되기 전에는 수동 사전검사로 강제한다.
- 도메인당 하나의 Worker 코드를 사이트별 환경변수로 덮어쓰지 않는다. **전체 호스트 등록표와 전체 정적 파일을 통합 패키징**한다. 기존 호스트·자산·SEO 정보를 유지한 채 해당 서브도메인만 추가한다.
- 신규 사이트 우선 `shared-static-preview` / `shared-static` 전달을 사용하며 기존 `v5.shared_static`, `v5.shared_release`, `worker/shared-static.js`를 가능한 한 재사용한다.

## 2. Cloudflare 연결과 충돌 안전

- 한 Worker가 다수의 호스트를 처리하는 것과, DNS/Route/Custom Domain을 그 Worker에 연결하는 것은 **다른 단계**다. 호스트 단위 허용 목록을 코드로 강제한다.
- Cloudflare **Custom Domain은 와일드카드가 아닌 정확한 호스트만 지원**한다. 와일드카드 Route를 사용하려면 해당 zone과 proxied DNS 레코드가 필요하며 루트 `domain.net/*`도 별도로 다룬다. 명시된 경로가 기존 Worker에 연결되어 있으면 우선순위·루트·세부 Route를 독립 확인한다.
- **사용자가 이미 분리해 운영 중인 Worker는 모두 그대로 유지하라고 확정했다(2026-11-04).** 자동·일괄 통합, 재바인딩, 삭제 또는 새 공용 Worker로의 이전을 하지 않는다. 매번 zone route 전체, custom domain 전체, DNS, 현재 100% 배포, 관련 cron/service binding을 조회하고 기존 설정을 스냅샷으로 보존한다. DNS/Route API가 403이면 그 검증을 못한 상태로 표시하고 광역 와일드카드 변경을 금지한다.
- 새 Worker를 만든다면 정확한 1개 이름으로 시도한다. 계정의 Worker 총수·권한·무료 한도를 먼저 확인하고 10037 등 생성 제한 시 **중복 생성·자동 삭제·무분별한 재시도를 하지 않는다**.
- 신규 호스트 연결은 해당 호스트의 소유·기존 DNS/도메인 충돌 검사를 거쳐서만 진행한다. 기존 호스트에 영향을 줄 수 있는 루트·와일드카드 Route 전면 연결은 하지 않는다. 신규 호스트를 정확한 개별 Custom Domain에 붙이는 경로를 우선 검증한다.
- 알려지지 않은 Host, 내부 경로, 비정상 인코딩, 없는 사이트/파일은 **404 + noindex**. Preview/Workers.dev는 noindex/nofollow, robots 차단, 공개 사이트로 리디렉션 금지. 공개 승인 호스트만 정확한 index/canonical/sitemap/RSS.

## 등록 도메인이 다른 두 사이트의 공유 가능성

- Cloudflare 기술적으로는 같은 계정의 관리 가능한 서로 다른 zone에서 **동일 Worker를 여러 정확한 Custom Domain/Route에 연결할 수 있다**. 다만 **V5 기본 정책은 등록 도메인별 1 Worker**이므로 `clinicflower.nalmada.net`과 `clinicflower.fwith.kr`은 서로 다른 zone Worker를 사용한다. 실제로 한 Worker를 공유하려면 사용자가 정책의 명시적 예외로 승인해야 하고, 계정·zone 접근 및 독립적인 호스트별 SEO/보안을 검사해야 한다.
- `clinicflower.nalmada.net`, `clinicopen.nalmada.net`, `clinicpresent.nalmada.net` 등 같은 `nalmada.net` 하위에 **신규로 만드는 세 사이트**는 하나의 `nalmada.net` Worker를 공유한다. 각 호스트의 HTML/CSS/이미지/canonical/robots/sitemap/RSS를 구분하고 다른 호스트의 파일에 접근하지 못하게 한다.
- 동일 또는 유사한 콘텐츠를 두 원 도메인에 공개할 경우, 중복 URL·색인을 피하도록 주 도메인 선택 및 canonical/301 또는 차별화된 콘텐츠 정책을 정한다. 검증 전 자동 복제·색인 제출 금지.

## 3. Worker 예외 분리

업종·키워드·이미지·디자인·본문·서브도메인이 다르다는 것만으로 별도 Worker를 만들지 않는다.

다음의 **객관적인 비호환성**이 검증됐을 때만 별도 Worker 예외 후보로 처리한다.

1. 독립 인증·보안·접근 정책과 Secret 분리 등 같은 Worker 안에서 안전하게 격리할 수 없는 요구.
2. Durable Object, 스트리밍, WebSocket, 복잡한 API, 별도 런타임 바인딩 등 공유 정적 라우터에 실질적으로 통합할 수 없는 기능.
3. 공유 Worker 변경으로 다른 호스트의 기능·안정성·운영비에 과도한 영향을 주며, 경로·서비스 분리로 해결할 수 없음이 검증된 경우.

**자산 파일 수 증가, 콘텐츠 양, 검색어 차이 자체는 우선 예외 사유가 아니다.** 정적 자산 중복 제거, 데이터/템플릿 압축, 페이지 생성/캐시, R2·KV 등 외부 스토리지와 비용·요청량을 먼저 비교한다. 비호환 증거·별도 Worker 수량·운영비·롤백 계획과 사용자 승인을 예외 기록에 남긴다.

## 4. 자산·요청 한도 및 서비스 보호

- 단일 공유 Worker의 정적 파일은 **전체 서브도메인 합산**으로 계산한다. V5 자체 안전 예산 18,000개, Cloudflare Free 한도 20,000개(2026-11-04 확인); 호스트 신규 추가 전 누적 자산·캐시 호환·script 번들 크기 확인 필수.
- Workers Free 계정 **100,000 요청/일은 계정 전체 한도**다. HTML host dispatch는 호출될 수 있다. 호출량 절약 효과는 Cloudflare 실제 지표로만 주장한다.
- 완전한 호스트 구성 원장, SHA256별 자산·원본 ZIP, 현재 배포 version ID, 이전 정상 버전과 site별 HTTP 검증서를 남긴다. 한 사이트 업데이트로 다른 사이트가 사라지지 않아야 한다.
- 검수: 대표 390/1440 화면, 전화 CTA, 이미지 provenance, 개인정보, 정확한 도메인별 robots/noindex/index/canonical/sitemap/RSS, 내부링크·404, 전체 URL 목록·문서 중복/유사도, 전체 기존 호스트 HTTP 상태. 검수 실패 시 배포 중단 또는 정확한 버전으로 롤백.
- 실제 URL 등록/IndexNow는 **정식 공개 승인 후 별도**로 진행한다. 프리뷰 1개를 사이트 전체 완성이나 색인 완료로 보고하지 않는다.

## 5. 2026-11-04 전환 상태 및 Clinicflower

- 당시 Cloudflare 조사: Worker 104개, Custom Domain 95개, `nalmada.net` 정확 호스트 매핑 17개가 **각기 다른 Worker**에 연결돼 있음. `sfv5-nalmada-domain`은 미존재. Root `nalmada.net` 및 `clinicflower.nalmada.net`은 Custom Domain으로 미연결.
- Zone 활성·소유 검증 완료, DNS records 및 zone route 관리 API는 HTTP 403으로 **조회 불가**. 이는 와일드카드 생성·전환 허가 근거가 아니다.
- Clinicflower는 `sites/clinicflower-preview/`의 정적 `index.html`, CSS, WebP 5장, 원문 POOL 720개로 만든 **1페이지 noindex 샘플**이며 현재 독립 테스트 Worker `sfv5-ansan-promotion-plant-preview`에서 HTTP 200으로 확인됐다. 기존 운영 17개 호스트를 다시 바인딩하지 않는다.
- 새 `sfv5-nalmada-domain` 준비·한도 확인 → 격리 HTTP 검증 → `clinicflower.nalmada.net` 등 **신규** 정확 호스트만 연결한다. 기존 17개는 **이전·통합하지 않고 각각의 현재 Worker를 유지**한다. 성공 증거가 없는 단계는 완료로 표시하지 않는다.
- 전국 Clinicflower 목표 5,302개는 후보 계획이며, 아직 공식 원장 1,438건 미검증, 전체 HTML 생성/페이지 간 5-gram Jaccard 유사도, 모바일/SEO 전체 QA, IndexNow가 완료되지 않았다. 이 검증 없이 전국 배포하지 않는다.

## 6. 보강할 코드 게이트

1. `v5.shared_release.prepare`에서 동일 `workerZone` 소속 여부와 등록 도메인별 Worker 이름 일치 강제.
2. 호스트 원장과 소유권·기존 바인딩 read-only 결과를 입력받아, 불명확하면 deploy abort.
3. 새로운 서브도메인 릴리스가 기존 호스트/자산/robots/SEO를 삭제하면 자동 FAIL하는 회귀 검사.
4. Cloudflare route/Custom Domain 전체 diff 및 배포 성공·실패·롤백 전후 HTTP 검증서 생성.
5. 자산 18,000/20,000 및 100,000/일 계정 총량 예측·경고. 단일 Worker가 용량을 초과하면 페이지 데이터+템플릿 압축 방식을 먼저 설계.

**참고 공식 문서 (2026-11-04 확인):**
- https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- https://developers.cloudflare.com/workers/configuration/routing/routes/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/
