# Todayflower: AI 고해상도 이미지 5장 교체 인수 증거 (2026-10-30)

## 범위와 완료 판정
- 기존 독립 브랜치 `site/todayflower-nalmada-pilot-20261030`만 수정. 최초 96×141px 이미지를 동일한 장면의 기존 생성 원본(가로 1448px)에서 변환한 WebP로 대체.
- **이미지 원격 5종·원본 크기·적응형 표시·대표 3페이지 QA·미리보기 HTTP 성공.** 다른 사이트, 전국 생성, 도메인, DNS, 인증, 권한, 신규 Secret, IndexNow는 변경하지 않음.
- `todayflower.nalmada.net` 후보 도메인 연결 없음. `workers.dev` noindex 유지. 실제 판매처 사진은 `fwith.co.kr` 원본 경로를 따로 사용하고, 생성 이미지는 실납품 증거가 아닌 연출 이미지임을 계속 표시함.

## 원격 5종 원본 파일
WebP 각 파일은 원래 ImageGen 생성 결과가 1448×1086px인 것을 변환했으며 **이전 96×141px 파일을 단순 확대하지 않았음**. 생성 원본 참조(gen_id)와 각 Git blob SHA는 `sites/todayflower-nalmada/site-spec.json`의 `images.provenance`에 보존.

| 파일 (공통 `assets/library/todayflower/`) | 원본 및 원격 WebP 해상도 | 원격 바이트 | Git blob SHA |
|---|---|---:|---|
| gift-bouquet.webp | 1448×1086 | 167,766 | 8f5ba2ca41b69aa792994a13ab652ae81cf0e182 |
| opening-plant.webp | 1448×1086 | 140,286 | 01ee6245cb69ca69625c111243055f2d034846d4 |
| celebration-wreath.webp | 1448×1086 | 272,178 | d54ef1dc3cb09e5d974810f6607cd18521e12b91 |
| condolence-wreath.webp | 1448×1086 | 149,518 | 4fe700902582071e03bad8f06c73646b7a875cf6 |
| flower-wrapping.webp | 1448×1086 | 135,190 | 82a5ddbf3fcb61de5e99fe3262359bdd0f310d5a |

- Binary 교체 커밋 `e5e9aa825ec9c359573c1d42507893d802ae29da` (이미 교체된 gift 1장과 합산 5장 원격 트리 readback 확인)
- 렌더링 개선 `v5/todayflower_markup.py` 커밋 `f672e64ef7d6731ab04a2a805317e3c88b55928b`: 데스크톱 3+2 가운데 정렬, 태블릿 2열, 모바일 1열 화면폭, HTML 고유 크기 1448×1086, width 100%, lazy-load·alt 유지, 96px 고정 제거
- 원장 `site-spec.json` 커밋 `b76cd8563e7a95b8add0694856925472f8be38b8`, `site.json` 커밋 `d858a5c2effc006fa4670da7d1d413e086466d16`
- 페이지당 실제 *내부* 이미지 7개 = AI 5개 + 나머지 편집 이미지 2개. 라이브러리 저장 자산 10개. 별도의 판매처 상품카드는 홈 8·단원구 7·고잔동 6개(기존 설정 유지).

## 검수
- V5 고정 검수 SHA `9c983dab6b69a724ae46dbff4a17a0c16f24eeed`
- Workflow: https://github.com/joseungil-kr/site-factory-v5/actions/runs/41029442885 (성공)
- 아티팩트 `12965067290`; digest `sha256:b1f06b959f6b7c1d8be3fc33c2dc51b8fa55aec1a3676436615b135582e17011`
- Python 단위테스트: 5개 WebP 실제 VP8 헤더(1448×1086)·Git blob SHA·7/5/2 카운트·대표 3개 콘텐츠/판매처 상품/noindex 검사 통과.
- 정적 빌드·감사: HTML 4개(대표 3개 + 404), 총 파일 20, 링크 참조 140, 오류 0·경고 0, sitemap 없음, robots Disallow.
- Chromium `390px`, `1440px` 각각 `/`, `/2.html`, `/3.html` = **총 6개 실제 화면 스크린샷** 및 `reports/todayflower-nalmada/large-image-qa.json` 저장 확인.
- 각 화면 5개: `naturalWidth 1448`·`naturalHeight 1086` 모두 통과, 실제 CSS 표시 너비 모바일 **332px**, PC **330px**, 가로 넘침 **없음**, 모바일 CSS 1열·데스크톱 3+2. 검사에서 원래 lazy 속성 보존 확인 후 이미지만 디코딩.
- 이 기록은 3개 대표 페이지만의 검수이며 전국 문서/배송 가능 지역 전수를 증명하지 않음.

## 기존 성공 noindex Worker만 갱신
- V4 Workflow 변경 커밋 `077b3165770805a2b04270d3f0943b698ef672db`
- 실행 https://github.com/joseungil-kr/site-factory-v4/actions/runs/41029861948 — **success**
- 대상: `sfv56-todayflower-preview` (기존 버전 `768f6f2f-abd8-4e3a-a0a7-e933b20e1df4`를 사전 확인하고 정확히 같은 Worker에만 배포)
- 새 Worker 버전: `b571636a-4aba-4756-9793-02e5233c5e14`
- 실제 URL: https://sfv56-todayflower-preview.joseungil.workers.dev
- 실서버 검사: **11개 응답 검사 모두 통과** (홈, 구, 동 3페이지 200 / 5개 큰 WebP 200·원본 바이트·1448×1086 대조 / robots.txt 200·Disallow / sitemap.xml 404 / 없는 경로 404). 모든 HTTP 응답 `X-Robots-Tag: noindex` 확인.
- 배포 검수 아티팩트 `12965048043`, digest `sha256:12ac28f24e2a05f043f0687e964168efd861ffd3fc3686cba59ec8fee942ee04` (실행 로그 확인; 첨부 ZIP 다운로드는 이번 세션에서 시간초과).
- `todayflower.nalmada.net`의 DNS·custom-domain을 추가하거나 수정하지 않았으며, 다른 Worker·Secret·권한 변경 없음.

## 후속
부모가 최신 미리보기의 실제 시각 품질을 수락한 다음, 공개 도메인/검색 등록/전국 확장은 별도의 검토·승인 범위로 유지한다.
