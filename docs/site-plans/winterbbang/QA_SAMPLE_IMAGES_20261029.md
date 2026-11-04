# 작업자 4 · Winterbbang 공통 이미지 5종 및 대표 HTML 7페이지 QA

검사일: 2026-10-29 KST  
대상: `feature/v54-winterbbang-preflight-20261029` / PR #23  
발행 범위: **오프라인 미리보기 전용. 운영 배포·DNS·IndexNow 실행 없음.**

## 1. 원격 이미지 원본 확인

부모가 기존 원본 5개만 저장한 커밋: `77710946d8111fd7d77eb07814e2f7825edbc6f1`.  
이번 후속에서는 이미지 재생성/재업로드하지 않음.

| 파일명 | Git Blob SHA | SHA-256 검수 | 바이트 | 디코딩 크기 |
|---|---|---|---:|---|
| hero.webp | 9d785b650e586425176a5291e0888f46c2983bf5 | 9ece3fbcfe2c973e74e814a2beee1a3c57f2b4bb105aa1e9f8f04477844adc41 | 22556 | 800×350 |
| shop-in-shop.webp | 2920c622f5603fd8d2a24393a99f2af48c35d68f | 2faccc9eeca968c3e02db91aceb62caf63cf597d81ccb735fa71efa0fe34d69d | 17496 | 600×450 |
| menu.webp | adba99e249d2c5c7fb06bd687890a22699a6e2dc | a0ec8d32e53bd8b6aae1477b3fd79191adec62606e85024b1a212d2d1ac6ec5a | 27056 | 600×250 |
| street.webp | 0d7bc3d8b688b4bf5379313fb3897d66172f2dda | 6c4d232d054070563351d32c53536ee95bb1011cbdfefdc33df9824544a40cae | 19372 | 600×400 |
| ingredients.webp | ee6c2af8d7b66db4479d2dbc7871f48015b3a2d4 | cf33a58a4707aa0bc4d4b1b0e206d077743edd11a1a1cbf0d99aa205beb4126e | 15138 | 800×333 |

독립 확인:
- GitHub 연결 `fetch_file(encoding=base64)` readback에서 5개 Blob SHA를 확보.
- 같은 원본의 로컬 파일에서 `git hash-object`, SHA-256, 파일 크기와 PIL WebP 픽셀 디코딩·치수 검사를 실행하여 모두 일치.
- 5개 모두 실제 매장·판매점·납품 사진이 아닌 **생성형 이미지**.

## 2. 렌더러 및 CI

- 렌더러 `scripts/winterbbang_render.py`에 `copy_verified_assets` 추가. 기존 `assets/library/winterbbang/*.webp`를 검증하여 미리보기 출력의 `assets/images/*.webp`에 복사.
- SHA-256, 파일 크기 및 RIFF/WEBP signature 확인 실패 시 즉시 중단.
- `.github/workflows/winterbbang-render-qa.yml`에서 생성 후 다시 복사본 5개를 SHA-256 검사.
- [GitHub Actions run #40831936963](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40831936963): 성공. 7개 고유 title, 7개 HTML noindex, 전화 `tel:0314070103`, 매출총이익·순이익 구분 및 금지 계약 조건 검수 통과. 로그: `assetStatus=VERIFIED_AND_BUNDLED`.
- 같은 SHA에서 V5 기존 회귀검사 [run #40831936940](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40831936940) 성공.
- 문서 POOL [run #40831936900](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40831936900) 성공.

## 3. PC·모바일 실제 렌더 검수 (로컬 Chromium)

- 기존 서울·경기 대표 7개 HTML을 오프라인 검토용 샘플 디렉터리에 구성하고, GitHub와 해시 일치하는 이미지 5개를 사용.
- Chromium 1440×900 및 390×844, 총 **14개 페이지·뷰포트 검사** 통과.
- 모든 샘플에서 이미지 5개가 디코딩·표시됐고, 가로 넘침 0. 전화 CTA 최소 2개 `tel:0314070103`, 지역 탐색 링크 6개, `noindex,nofollow`, 공개 금지 금액 문구 부재, 60~70%의 **판매가−재료비 매출총이익률** 설명을 확인.
- 로컬 HTTP 방문은 브라우저 정책 `net::ERR_BLOCKED_BY_ADMINISTRATOR`에 의해 차단됐으므로, **Chromium `set_content`와 동일 WebP bytes의 data URL로 실제 화면·디코딩 검사** 수행. 따라서 오프라인 렌더 검수 성공이며, 실제 HTTP 200, Workers route, URL 접근 검수 성공이라고 주장하지 않음.
- 스크린샷 및 독립 샘플 ZIP은 ChatGPT 대화 첨부로 제공 (GitHub에 이미지 스크린샷을 중복 저장하지 않음).
- 화면 샘플에는 지역 탐색 링크가 추가되어 있음. 운영 원격 렌더러와 모든 화면의 바이트 동등성을 주장하지 않음. 검색 공개 전 콘텐츠/지역 차별성, 링크·UI QA 별도.

## 4. 아직 완료하지 않은 것

1. 사이트 `site-spec.json` 사전 승인 및 최종 페이지 목표 확정 (현재 Draft `approved=false`).
2. 서울·경기 확대용 현행 법정/행정동 자료·지역 고유 상권 사실 검증. 대표 6개는 실제 매장 실적 주장 아님.
3. 운영 도메인 소유권·DNS/Workers 충돌 확인. 후보 `winterbbang.nalmada.net`이 우선 검토 대상이나 현재 확정 또는 연결되지 않음.
4. 실제 HTTP 및 모바일 원격 브라우저 QA, 공개형 canonical/robots/sitemap, 배포·색인 제출.
5. 매출총이익률의 실제 원가표/판매가 실증은 별도. 현재 수치 60~70%는 운영자 제시 예상치이며 순이익 보장 아님.
