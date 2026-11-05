> **현행화 (2026-10-27 11:18 UTC):** 이 문서는 11:15 UTC의 실제 도메인 연결 전에 작성된 이전 상태 기록입니다. 현재 `quicksky.nalmada.net`에 기존 `sfv5-quicksky-preview` Worker가 연결됐으며 HTTP 200/404·noindex가 독립 검증됐습니다. 최신 사실·12주제×서울/경기 24개 표본·사진 SHA와 미해결 검수는 [QUICKSKY_LIVE_CONTENT_AUDIT_20261027.md](QUICKSKY_LIVE_CONTENT_AUDIT_20261027.md)를 우선 참조하세요. **검색 공개, IndexNow, 사진 권리/서비스 제공 실체는 미검증입니다.** 아래 DNS/Route 403 기록은 연결 *이전* API 사전검사 결과이며, 현재 운영 연결 실패를 의미하지 않습니다.

# 빠른스카이 V5 — 2026-10-27 운영 배포 준비·검증 현황

## 최종 도메인 정정
- 최종 사용자 지정 도메인: **https://quicksky.nalmada.net**. 이전 `.com` 요청과 보고는 폐기. `nalmada.com` DNS·Zone 결과는 현 작업에 적용하지 않는다.
- 동일 프로젝트/PR: `joseungil-kr/site-factory-v5` PR #16, `feature/quicksky-nalmada-com-20261027` (브랜치명은 과거 이름으로 유지). 신규 사이트를 중복 생성하지 않는다.
- V5 정정 source: `51ae28a7ccd0a49d01ac5440417bab2b5cf04c86`.

## 검증된 완료 내용
- 1,733개 빠른스카이 HTML + 오류 문서 및 정적 파일 생성. site.json, site-spec, canonical 대상, 허용 호스트 및 테스트가 정확한 `.net`으로 변경됨.
- V5 run [40490190217](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40490190217): Python 78개, Worker 6개, preview 생성·QA 오류 0. 빌드는 성공했지만 V5 자체 Cloudflare Secrets가 없어서 배포 단계 skipped. **새 `.net` 운영 배포 성공 증거 아님**.
- 기존 독립 preview: https://sfv5-quicksky-preview.joseungil.workers.dev, 배포 run [40473426279](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40473426279)에서 실제 200/404 및 noindex 확인. 이 preview는 과거 source 708063a1 기반; 현재 `.net` 정정 커밋이 반영되었다고 가정하지 않는다.
- V4 기존 성공 인증 및 fwith 기존 인증 모두 새 Secret 복사나 새 토큰 없이 검증 경로로 활용.

## nalmada.net Cloudflare 읽기 전용 preflight
- V4 [run 40490896302](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40490896302), source `d785040dcbdf399b142db242a4d0602307d663f2`.
- 정확한 `nalmada.net` Zone 조회 가능·active, customDomain 목록 조회 가능, `quicksky.nalmada.net`에 연결된 기존 Worker 없음.
- **DNS 레코드 조회 403, Workers Route 조회 403**. 따라서 비어 보이는 DNS/Route 목록은 충돌 없음의 증거가 아니며 `safeToAttach=false`.
- fwith 대안 [run 40490480290](https://github.com/joseungil-kr/fwith-site-factory/actions/runs/40490480290)에서도 정확한 .net Zone이 보이나 DNS/Routes 각각 403.
- Cloudflare 관리 UI 접근 검증은 별도 지원 담당자가 진행 중이므로 이 파일 갱신은 중복 DNS 수정/Worker 연결을 실행하지 않는다.

## 사진·내용 실제 검증 상태
- `docs/DAYSKY_PHOTO_PROVENANCE.json`: Quicksky에서 현재 참조하는 사진 3개는 **원본 JPG 2개에서 만들어진 3개 WebP 변형**이다. 원본 URL·SHA·crop·결과 SHA 이력은 확인할 수 있지만 이는 Quicksky 브랜드로 **재사용할 권리**를 자동 증명하지 않는다.
- `sites/quicksky/site.json`의 `imageAssetsApproved=false` 유지. 원본 사진 원소유자·상표 노출·차량번호판·인물/동의 여부를 실제 자료로 확인하거나 부적합한 이미지를 제거해야 한다.
- `v5/quicksky_pages.py`: 지역명과 작업 종류를 중심으로 문구 POOL을 선택하므로 **실제 각 행정동의 작업 이력, 지형, 관할 제한, 장비/출장 가능 여부**를 검증한 데이터가 본문에 포함됐다는 근거는 없다. 문자 5-gram 유사도 통과는 검색 품질이나 실질적 지역 정보의 고유성을 증명하지 않는다.
- `contentQualityApproved`를 근거 없이 true로 바꾸지 않는다. 지역별 실질 차별 정보를 확보하거나 공개 페이지 수·본문을 확인 가능한 범위로 조정하는 것이 정석이다.
- 요금은 `pricingPolicy=consult-only`, 근거 없는 숫자 요금표는 출력하지 않는다.

## 운영 배포·검색등록 게이트
- 현재 `publishEnabled=false`, `publicIndexingApproved=false`, `imageAssetsApproved=false`, `indexNow.enabled=false`, `indexNow.key=null`. 서비스 모델의 `publishEnabled=false` 정책은 유지한다.
- 사용자 공개 요청과 **사실의 독립 검증**은 별개. 도메인과 콘텐츠/사진 검증 조건을 승인 플래그로 대체하지 않는다.
- **운영 quicksky.nalmada.net 공개 HTTP·canonical·robots Allow·sitemap 1733 URL·404는 미검증**. `.net` 운영 공개 완료로 보고하지 않는다.
- Zone/Route/DNS 충돌을 조회할 최소 권한 또는 관리 UI에서 검증 가능한 사실을 확보한 뒤, 기존 V4/Fwith CF 인증을 재사용해 전용 Worker의 운영 연결을 검증할 수 있다.
- IndexNow는 정상 키를 확인하고 key 파일 HTTP 200 및 본문 일치를 검증한 뒤 제출해야 하며, **현재 미전송·영수증 없음**. HTTP 200/202는 색인 완료 증명이 아니다.
- 네이버/구글 소유확인·사이트맵 제출은 별도 부모 담당. 중복 제출 금지.

## 출처/증거
- [V5 PR #16](https://github.com/joseungil-kr/site-factory-v5/pull/16)
- [V4 실행 결과](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40490896302)
- [fwith 대안 실행](https://github.com/joseungil-kr/fwith-site-factory/actions/runs/40490480290)
- [빠른스카이 V5 QA](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40490190217)
- 파일 원장: `sites/quicksky/site.json`, `sites/quicksky/site-spec.json`, `docs/DAYSKY_PHOTO_PROVENANCE.json`, `v5/quicksky_pages.py`.
