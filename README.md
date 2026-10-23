# Site Factory V5 — 독립 반자동 사이트 제작 엔진

**작업일:** 2026-10-24 KST

V4(기존 꽃배달 운영 사이트)를 보존하면서, 고객·업종·사이트별로 구분된 정적 HTML을 생성하고 GitHub Actions/Cloudflare Workers에 연결하기 위한 독립 코드입니다.

- **첫 대상:** 안산시 × 승진화분
- **주문:** 전화 `1844-0644` + 기존 `fwith.co.kr`의 개별 상품페이지
- **주소:** `index.html`, `2.html`, `3.html` … 실제 생성된 번호만 하단 7개 링크
- **구조:** 지역·상품 허브 없는 독립 상세페이지
- **공통 이미지:** 업종별 N개 이미지 경로를 모든 페이지에서 재사용 (현재 3개는 예시 SVG)
- **특수 페이지:** `견적계산기.html`, `배송안내.html`; 필요하면 다른 페이지·링크 추가
- **공개 상태:** 운영 도메인 미정, 운영 배포 금지. 독립 `workers.dev` 임시 검토용 `noindex` 배포 구성은 별도 준비
- **AI API:** 사용하지 않음. 빌드와 테스트는 Python 3.11+ 표준 라이브러리.

## 빠른 실행

```bash
python -m unittest discover -s tests -v
npm test                  # Node 22+ 필요; Worker 단위 테스트만 진행
python -m v5 build --site ansan-promotion-plant
python -m v5 audit --site ansan-promotion-plant
python -m v5 dashboard
python -m http.server 8000 --directory dist/ansan-promotion-plant
```

로컬 브라우저에서 `http://127.0.0.1:8000/`을 열 수 있습니다. 미리보기 HTML의 CSS/이미지는 절대 경로이므로 `file://`로 직접 열지 않는 편이 정확합니다.

## 추후 채팅에서 사용하는 변경 명령의 예시

`--apply`가 **없으면 입력 JSON을 수정하지 않습니다.** 먼저 작업 결과와 변경 범위를 검토하는 방식입니다.

```bash
python -m v5 change-global --site ansan-promotion-plant --field phone --value 031-123-4567
python -m v5 add-special --site ansan-promotion-plant --path 이벤트.html --title '이벤트' --description '행사 정보' --placement footer
python -m v5 add-page --site ansan-promotion-plant --json-file drafted-new-page.json
python -m v5 scaffold-site --id client-002 --brand '가상상호' --keyword '스카이차' --region '안산시' --phone '031-123-4567'
```

위 명령 뒤에 `--apply`를 붙이면 설정 원장을 변경합니다. 이후 `build`, `audit`, `reports/.../changes.json`을 확인하여 예상한 HTML만 달라졌는지 검사합니다.

## 운영 제한

- 기존 V4 저장소나 `flower-a`, `flower-b`를 건드리는 명령은 없습니다.
- 2026-10-24 현재 `joseungil-kr/site-factory-v5` **원격 GitHub 저장소는 아직 생성되지 않았습니다.** 이 패키지는 별도 로컬 Git 저장소입니다.
- 자동화용 `.github/workflows/` 파일은 준비되어 있지만 GitHub Actions에서 실행한 증거는 없습니다.
- 사용자 운영 도메인, 실제 상품 현재성, 이미지 승인 및 개인정보 검토가 없으면 **운영 배포**를 차단합니다. 검색 제외된 독립 임시 시안은 외부 검토용으로 분리합니다.
- Cloudflare rollback은 실제 계정이 아닌 모의 테스트만 수행했습니다. 새 Worker 최초 배포는 복구 기준 버전이 없으므로 별도 기초 배포 절차가 필요합니다.
- 로컬 브라우저 시각 검사는 실행 환경의 관리자 차단(`ERR_BLOCKED_BY_ADMINISTRATOR`)으로 수행되지 못했습니다. 다만 HTTP/HTML 기반 시험은 통과했습니다.
- ImageGen 등으로 생성된 상품 실사진은 포함하지 않습니다. 공용 SVG 3개는 시범 구성용입니다.

## 작업 자료

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — 실행 구조
- [`docs/FEATURE_MATRIX.md`](docs/FEATURE_MATRIX.md) — 승인받은 12가지 기능의 상태
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — 공개 전 안전 조건
- [`docs/STAGE_REPORT.md`](docs/STAGE_REPORT.md) — 단계별 결과
- [`docs/provenance.json`](docs/provenance.json) — V4에서 참조한 원본 파일과 SHA

## 기술 조건

Cloudflare Workers Static Assets의 `html_handling: none`, `not_found_handling: 404-page`, 루트 요청 `/index.html` 내부 재작성, GitHub Actions 검사, 폴더별 독립 사이트 설정을 사용합니다. 고정 파일 수가 아니라 실제 현재 릴리스 파일 수를 검사하며 기본 자체 경고 한도는 18,000개입니다. Workers Free의 공식 정적 파일 상한은 Worker 버전당 20,000개입니다.

기존 운영 URL의 SEO 결과, 실제 결제·주문·문의 전환, 색인 등록과 순위 상승은 본 프로젝트의 **현재 완료 증거가 아닙니다.**


## 독립 Cloudflare 임시 시안 배포 준비

```bash
python -m v5 build --site ansan-promotion-plant --mode preview
python -m v5 audit --site ansan-promotion-plant
python -m v5 prepare-staging --site ansan-promotion-plant
# Cloudflare 인증·네트워크가 있는 환경에서만 실제 실행:
npx --yes wrangler@4.148.0 deploy --config deploy/ansan-promotion-plant/staging.wrangler.json
```

임시 Worker 이름은 `sfv5-ansan-promotion-plant-preview`이며 기존 flower-a/b Worker와 격리합니다. 임시 HTML에는 `noindex,nofollow`와 미검증 안내문을 넣었고 Worker는 응답에 `X-Robots-Tag: noindex, nofollow, noarchive`를 강제합니다. 단, noindex는 접속 비밀번호가 아닙니다. 실제 URL을 받은 뒤 `python -m v5 staging-check --site ansan-promotion-plant --origin https://<actual>.workers.dev`로 HTTP 200·404와 noindex를 독립 확인해야 합니다.

비공개 원격 GitHub 저장소 생성/푸시용 `scripts/create-private-repo.sh`는 GitHub CLI에 로그인된 환경에서만 동작하며, 이 환경에서는 외부 연결·인증이 없어 실행하지 않았습니다. 정확한 단계/제약은 [임시 배포 검수 기록](docs/STAGING_STATUS_20261024.md)을 보세요.