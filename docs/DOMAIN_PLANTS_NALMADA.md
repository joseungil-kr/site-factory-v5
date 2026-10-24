# plants.nalmada.net — V5 서울·경기 사이트 연결 기록

검증일: 2026-10-24 KST

## 현 상태

- 사용자 구매 도메인: `nalmada.net`
- 연결된 정확한 호스트: `https://plants.nalmada.net/`
- 사이트: 서울·경기 1,732개 동, `축하화분` 및 `승진화분` 문서 총 3,464개
- 정적 사이트의 소스: V5 `main` `27a1599934b0a731cd846330b72bc9dbd5b6d852`
- 서비스 Worker: `sfv5-seoul-gyeonggi-plants-preview`
- Cloudflare 등록 방식: **Workers Custom Domain**, DNS/HTTPS Cloudflare 관리
- 사용자 운영 루트 도메인 `nalmada.net`은 변경하지 않음
- V4 운영 `main`은 변경하지 않음 (`223b9348f32b700af98645d034943772d590aaba`)

## 서버에서 직접 검증한 결과

- GitHub Actions 인증된 Cloudflare API를 통해 `plants.nalmada.net`이 정확한 V5 Worker에 등록된 사실을 재조회
- 실제 `https://plants.nalmada.net/` HTTP 200
- `/2.html` HTTP 200
- `/3465.html` HTTP 200
- `/page-404.html` HTTP 200 (404번 문서와 오류 404.html 충돌 회피)
- `/404-nalmada-probe.html` HTTP 404
- 위 모든 테스트에 `X-Robots-Tag: noindex` 및 HTML `<meta name="robots" content="noindex,nofollow">` 확인
- `rel="canonical"` 없음
- 수행 기록: https://github.com/joseungil-kr/site-factory-v4/actions/runs/40097594768

## 중요: 정식 색인용 운영 버전 아님

이 연결은 **검수용 Worker를 사용자 도메인에 바인딩한 상태**다.
`sites/seoul-gyeonggi-plants/site.json`의 `domain:null`, `publishEnabled:false`와
`V5_STAGING=1`을 유지한다. 이 설정을 제거하지 않고 `IndexNow`도 제출하지 않는다.

향후 검색 색인용 운영 출시 전 별도의 단계로 상품/재고/실제 배송정보 검증,
콘텐츠 중복·품질 검수, 이미지 사용 승인, 개인정보 설정 확인, 독립적인
production Worker 최초 안전 배포·복구 기준 설정, 정식 도메인/캐노니컬 설정 및
공개 HTTP 검사를 수행해야 한다. 기존 V4 또는 현재 임시 Worker를
무조건 `publish` 모드로 전환하지 말 것.

## 인증과 권한

Cloudflare API 토큰은 이 파일에 기록하지 않았으며 기존 V4 GitHub Actions secret을
사용해 Cloudflare API에 접근했다. 기존 토큰에는 DNS 및 zone routes 조회 권한이
없어 공개 DNS 조회와 Cloudflare의 Worker Domain API 충돌 검사를 사용했으며,
어떠한 DNS 레코드도 수동으로 생성·교체·삭제하지 않았다.
