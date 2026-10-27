# 빠른스카이 V5 검증 결과 및 운영 도메인 연결 차단 기록 — 2026-10-27

## 현재 확인된 사실
- 최종 요청 도메인은 **quicksky.nalmada.com**. nalmada.net으로 변경하지 않는다.
- 기존 V4 GitHub Actions의 인증으로 **독립 `sfv5-quicksky-preview` Worker**는 실제 배포됨.
- 기존 Worker 미리보기 주소: https://sfv5-quicksky-preview.joseungil.workers.dev
- 배포/공개 HTTP 로그: https://github.com/joseungil-kr/site-factory-v4/actions/runs/40473426279
- V5 제작물: 1,733개 서비스 HTML + 404, 전체 1,744개 정적 파일; QA 0 errors, 이 결과는 원격 빌드 아티팩트 기준.
- `workers.dev` 샘플 경로 /, /2.html, /10.html, /1733.html → HTTP 200, 없는 경로 404, HTTP X-Robots-Tag 및 HTML noindex 확인.
- 미리보기 Worker는 V5 고정 커밋 `708063a151043e96fc62ffaaad219a2d8930bf6d` 기반이며 기존 당일스카이와 분리.

## 독립적인 Cloudflare/DNS 읽기 전용 조사
- 기존 Site Factory V4 인증: nalmada.com exact zone unavailable. https://github.com/joseungil-kr/site-factory-v4/actions/runs/40474016556
- 기존 fwith-site-factory 인증 대안: exact nalmada.com visible zones **0**. https://github.com/joseungil-kr/fwith-site-factory/actions/runs/40474251373
- Google 공개 DNS-over-HTTPS: nalmada.com NS = `ns1.afternic.com.` / `ns2.afternic.com.`, quicksky.nalmada.com A answer exists; HTTP 제공 주체는 검증하지 않음. https://github.com/joseungil-kr/site-factory-v4/actions/runs/40474822807
- 이 정보는 *사용자 소유권 없음*을 증명하지 않는다. 단, 현재 연결된 계정의 활성 `.com` Zone 접근성과 권한을 확인하지 못하므로 **Cloudflare Custom Domain 연결 및 도메인 DNS 변경을 중단**한다.

## 공개 및 색인 상태
- `quicksky.nalmada.com` 운영 공개 **미완료**. `workers.dev`에서만 noindex 미리보기.
- 운영 robots.txt `Allow: /`, sitemap 1,733건 및 IndexNow 키 파일 **아직 공개되지 않음**.
- IndexNow **미전송**, 응답 영수증 없음. 절대로 IndexNow 200/202나 색인 성공을 가정하지 않는다.
- Google/Naver 소유확인 및 사이트맵 제출은 별도 등록 담당자와 중복하지 않는다.
- 검색 허용 로직에 `quicksky.nalmada.com` exact host만 추가했으나, 사이트 설정은 여전히 noindex. 도메인 소유확인, 이미지 이용권, 본문 품질 게이트 모두 충족돼야 공개 빌드를 허용한다.

## 추가 승인·검증이 필요한 문제
1. **도메인 권한**: nalmada.com의 등록기관 계정 소유 또는 현재 DNS 관리자 확인. Cloudflare Zone을 추가/이전해야 한다면 할당 NS 및 기존 레코드 영향을 검토하고 명시된 권한으로 처리. 누가 소유하는지 확인 전 새 DNS/Zone 생성 금지.
2. **사진 권한**: `sites/quicksky/site.json`의 `imageLibrary=daysky`는 기존 사용자 보유 작업사진 출처를 재사용하지만, 새로운 브랜드에서의 권리 및 사진·캡션 적합성은 검증되지 않았다. `imageAssetsApproved=false` 유지.
3. **콘텐츠 품질**: 지역 문구 풀의 글자 5-gram 통계적 유사도 기준을 충족했지만 현지 차별 정보, 실제 서비스 제공 범위, 독자적 가치는 보장되지 않는다. `contentQualityApproved`는 설정하지 않았다.
4. **IndexNow**: 운영 HTTPS → 이미지/본문/robots/sitemap/404 확인 → 키 파일 공개 확인 → 1,733 URL batch POST → HTTP 200/202 증빙 별도 저장. 전송 결과는 색인 결과가 아니다.

## 자산과 변경 범위
- PR: https://github.com/joseungil-kr/site-factory-v5/pull/16 (draft, 미병합)
- 기존 Daysky 운영 Worker/도메인 및 V4 운영본 코드 변경하지 않음.
- 필요 없는 Secret 복사·신규 토큰 생성·OAuth·권한 변경을 실행하지 않음.
