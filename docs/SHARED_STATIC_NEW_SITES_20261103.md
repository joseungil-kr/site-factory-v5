# V5 신규 사이트 공유 정적 전달 검증

기존 운영 사이트는 그대로 유지한다. V6를 만들지 않고 기존 `v5.engine.build`의
생성·기획·이미지·품질 검사를 재사용하는 **별도 신규 사이트 미리보기 어댑터**를 추가했다.
운영 배포 완료나 일일 호출 절감 실측을 의미하지 않는다.

## 확인된 제약과 구현

Cloudflare Static Assets는 호스트별 디렉터리가 아니라 경로 기반 자산 컬렉션이다.
같은 Worker에 여러 호스트를 연결하고 `/index.html`을 정적으로 제공하면 같은 파일을 받는다.
로컬 Wrangler 대조 검사에서 자동 루트 매칭을 켜고 두 호스트의 `/`에 같은 본문이 나오는 것을 확인했다.

이번 구현은 HTML을 미리 생성하되 HTML 요청마다 허용된 호스트를 Worker가 구분한다.
이미지·CSS·JS는 자산 묶음의 SHA-256 경로 `/_sfv5/assets/<digest>/...`에서 정적 자산 우선으로 제공한다.
따라서 **HTML 호출 0 구현이 아니다.** HTML, robots, 검색 인덱스, 없는 주소, 잘못된 요청과
기타 라우트는 Worker 실행을 사용할 수 있다. 로컬에서 제외 패턴 아래의 정적 파일 누락은 핸들러 실행 없이 404였다.
내부 `ASSETS.fetch`는 HTML 응답을 얻는 바인딩 호출이며
요청마다 추가 외부 HTTP 요청을 보내는 구현은 아니다. 실제 과금 집계는 별도 확인해야 한다.

사이트 HTML은 `/_sfv5/sites/<site-id>/...` 아래 저장하지만 외부에서 그 경로를 직접 요청하면 404다.
다른 사이트의 `/2.html`이나 내부 경로가 노출되지 않게 호스트별 경로 목록으로 제한한다.
`/`, `/index.html`, `/2.html`, 한글 파일명 규칙을 보존하고 알 수 없는 경로에는 해당 호스트의
404 HTML을 404 상태로 반환한다. 공개 이미지·스타일·스크립트는 모든 호스트에서 같은 해시 경로로
접근 가능한 **의도적인 공용 자산**이다. 비공개 파일·사이트 HTML을 이 자산 경로에 넣어서는 안 된다.

기본 합산 자산 한도는 18,000개, 허용 상한은 20,000개다. 개별 사이트가 아닌 공유 Worker 전체를 센다.
동일한 자산 묶음은 중복 저장하지 않는다. 호스트별 경로 목록은 환경변수 크기 제한을 피하려고
Worker 모듈에 포함하며, 대규모 운영 전 Wrangler dry-run으로 스크립트 업로드 크기도 검사해야 한다.
100,000회/일은 Worker 하나마다 별도로 받는 용량으로 가정하면 안 된다.

## 안전한 사용 범위

이 어댑터는 다음 조건을 모두 만족하는 새 사이트만 받는다.

- `site-spec.json`을 작성·승인하고 기존 build 검사를 통과한다.
- `site.json`에 `deliveryMode: "shared-static-preview"`를 명시한다.
- 계획과 설정의 HTTPS 도메인이 일치하고 다른 V5 사이트가 사용 중인 도메인이 아니다.
- 기존 `workerName`이 없고 `publishEnabled`, `publicIndexingApproved`, analytics가 꺼져 있다.

예시 호스트 `ansanwreath.fwith.kr`, `seoulwreath.fwith.kr`, `seoulfuneral.fwith.kr`는
로컬 검증의 Host 헤더로만 사용했다. 실제 사이트·DNS·Worker를 생성하지 않았다.
기존 `wreath.fwith.kr`는 이 어댑터에 추가하지 않는다.

Python 3.12 이상에서, 승인된 신규 사이트 자료가 준비된 후 실행한다.

```console
python -m v5.shared_static --site <new-site-id> --site <another-new-site-id> --output dist/shared-new-preview
npm exec --yes --package=wrangler@4.148.0 -- wrangler dev --local --config dist/shared-new-preview/wrangler.json
```

실제 가상 호스트를 로컬 주소로 보내는 Host 헤더로 검사한다. 기존 폴더를 덮어쓰지 않는다.
생성 설정에는 DNS/routes, credentials, analytics binding, deploy 명령이 없고
`workers_dev: false`, `preview_urls: false`다. 이는 로컬 검증용이며 운영 배포를 위한 자동 경로가 아니다.
최상위 `_headers`와 Worker 응답에서 noindex를 강제하고 robots는 전체 차단한다.
미리보기 sitemap은 제공하지 않는다. 기존 생성기의 canonical·sitemap 정책과 전화·주문 URL은 변경하지 않았다.
향후 운영 모드는 publish 사전검사, sitemap/canonical, 색인 허용, 호스트 연결, 한도·복구 검증을 통합해야 한다.

analytics 이벤트를 켜면 POST마다 Worker 요청이 추가된다. 현재 새 어댑터는 이를 거부한다.
계산기·검색 UI의 브라우저 실행 자체는 Worker 실행이 아니지만 검색 인덱스 HTTP 요청은 Worker를 사용한다.

## 검증 명령과 증거

```console
python -m unittest discover -s tests -p test_shared_static.py -v
npm test
python -m scripts.verify_shared_static_local
python -m unittest discover -s tests -q
```

Windows에서는 UTF-8 기본 인코딩과 Python 3.12를 사용한다 (`python -X utf8 ...`).
로컬 소켓을 차단하는 sandbox에서는 localhost 검사만 허용된 실행 환경이 필요하다.
로컬 검증 스크립트는 임시 코드에 핸들러 진입 로그를 추가하고 요청 전후의 로그 수를 비교한다.
운영 도메인을 네트워크로 호출하지 않으며 `127.0.0.1`에만 요청한다.
산출물 `reports/shared-static-local.json`에는 요청별 상태와 로컬 핸들러 진입 횟수가 담긴다.
실제 edge 호출 통계나 청구 내역이 아니므로 `edgeBillingVerified: false`를 명시한다.
임시 런타임의 지원 날짜에 맞춰 새 설정에만 compatibility date `2026-10-13`을 사용했다.
기존 Worker의 날짜나 설정은 바꾸지 않았다.

## Transform Rules 후보와 미검증 사항

[Cloudflare 공식 설명](https://blog.cloudflare.com/transform-rules-requests-transform-and-roll-out/)은
URL Rewrite가 Worker 코드 전에 처리된다고 설명하지만 Static Assets 매칭 전에 적용되는지와
해당 요청이 일일 Worker 실행으로 집계되지 않는지를 이 설명만으로 입증하지 못한다.
로컬 Wrangler는 실제 zone Transform Rules 실행 순서를 재현하지 않는다.
따라서 호스트를 경로로 바꾸면 HTML도 0회라는 가정을 코드나 배포에 넣지 않았다.

[Transform Rules 제약](https://developers.cloudflare.com/rules/transform/)은 현재 Free 활성 규칙 10개,
정규식 미지원, 프록시 DNS 필요다. 향후 격리 테스트에서는 허용 호스트만 정확히 매칭하고
내부 경로 직접 접근·리다이렉트·중복 색인·canonical·404를 함께 검증해야 한다.
zone 규칙, 보안, DNS 변경은 이번 작업 범위에서 금지되어 실행하지 않았다.
HTML 호출 0까지 요구하면 이 단계가 남아 있으며 현재 패키지를 운영용 완성품으로 취급하지 않는다.

## 참고 구현과 라이선스

- [Cloudflare Workers SDK](https://github.com/cloudflare/workers-sdk): MIT OR Apache-2.0,
  공식 Wrangler/Miniflare 구현. 2026-11-03 조사에서 최근 릴리스·활동을 확인했다.
  저장소가 이미 사용하는 Wrangler 4.148.0을 임시 CLI로 재사용했다. 새 npm 의존성이나 소스 복사 없음.
- [Worker script routing](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/),
  [설정](https://developers.cloudflare.com/workers/static-assets/binding/),
  [요금·한도](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/):
  정적 자산 우선 및 선택적 Worker 실행의 공식 근거다. 로컬 결과와 실제 과금은 구분한다.
- [Workers for Platforms 공식 템플릿](https://github.com/cloudflare/templates/tree/main/workers-for-platforms-template):
  공유 플랫폼 후보로 조사했지만 여러 Worker를 dispatch하는 별도 상품이라 단일 Worker·무료 운영 조건에 부적합하다.
  [템플릿 자체 라이선스](https://raw.githubusercontent.com/cloudflare/templates/main/workers-for-platforms-template/LICENSE)는
  Apache-2.0이며 상위 templates 저장소는 MIT다. 공식 templates 저장소에서 현재 템플릿이 유지되는 것은 확인했지만
  이 하위 템플릿의 최근 수정일은 독립 확인하지 못했다. 채택하거나 setup/token 생성 코드를 실행하지 않았다.

## 기존 작업과 배포 격리

시작 기준 main: `a466473`. 원격 feature/RSS 브랜치들이 있으므로 해당 작업을 병합하거나 덮어쓰지 않았다.
기존 publish/staging은 수동 트리거다. Daysky 운영 배포는 main의 특정 경로 변경에서 실행될 수 있으므로
`v5/engine.py`, 기존 `worker/index.js`, 사이트 자료, workflows를 수정하지 않았다.
새 feature 브랜치 push는 확인한 운영 워크플로의 push 조건에 해당하지 않는다.
자동 GitHub 외부 연동의 대시보드 설정은 접근·변경하지 않았다.

## 이번 실행 결과

- Python 3.12.10 UTF-8 전체 회귀 86개 통과. 이후 호스트별 CSS 해시 충돌 방지 보완을 포함한 신규 전용 검사 7개 통과.
- Node 24에서 기존·신규 Worker 검사 9개 통과.
- 로컬 Wrangler 16개 결과: HTML 홈 3개는 각 1회 진입, CSS 2개와 SVG 1개는 각 0회 진입,
  호스트별 404·robots·이벤트 비활성화·내부 HTML 차단 확인. 자산 우선 루트 대조는 두 호스트에 같은 내용과 0회 진입.
- [저장한 로컬 증거](shared-static-local-evidence-20261103.json). 운영 사이트 요청 및 실제 배포 없음.
- 실제 edge 과금 통계, zone Transform Rules 순서, 계정별 route/custom-domain 수용 한도와 복구 절차는 미검증.
  운영 전 새 사이트 전용 배포 경로와 색인 허용 검증도 남아 있다.
