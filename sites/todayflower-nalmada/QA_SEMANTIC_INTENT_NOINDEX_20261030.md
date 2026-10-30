# Todayflower 의미 오류 교정 · 독립 noindex 미리보기 검증 (2026-10-30)

## 최종 상태
**완료:** 상품 목적이 아닌 주소 비교·수령 부재·배송비·배송 경로·공동주문·상담 등을 꽃 상품의 종류처럼 치환한 도입·FAQ 표현 교정, 본문 이외의 제목·소제목 16개 개선, 전수 자동 QA 및 기존 Worker 실서버 검증 성공.

**변경 금지 범위 유지:** `sites/todayflower-nalmada`의 원본 대표 3페이지, 고해상도 AI 이미지 5장·편집 이미지 2장, 원본 상품 8종·표시가격·직접 주문 링크, 2026-10-22 지역 원장 스냅샷, noindex. 전국 확대·DNS/도메인 연결·새 Secret·권한 변경·공개 index 전환 없음.

## 실제 수정 및 GitHub 커밋
- `sites/todayflower-nalmada/pages.json`
  - `abdf6ee7be8c310251b33703d7022f9eb9969884`: 신규 30페이지 도입 첫 문장 30개, FAQ 질문 60개, FAQ 답변 끝맺음 60개 상황별 의미 수정.
  - `47926b0fcbfcf0d2ba271047a13975a754aedd4e`: 법정동 뒤의 부자연스러운 `동로` 조사 19건, /4·/28·/29·/30·/32 문답 맞물림 수정.
  - `88aaee98e9b754d8f6830fa588578389e5884abd`: '추가 배송비 선택', '수령자 부재 선택', '구 단위 주소 비교 선택'처럼 잘못된 제목과 1번 소제목을 **16페이지에 한정**하여 자연스러운 배송·수령 조건으로 수정.
- `tests/test_todayflower_copy_quality.py`: `f85a4d2d308135ac0db506fb31e645b5242325c0`에서 33페이지 문구 전수 테스트 및 15개 의미 사례, `tests/`의 다른 사이트 QA 추가 없음.
- `.github/workflows/todayflower-pilot-qa.yml`: `c46741b1404621fb5bcb7f4b676fe0bdbb286efc` 최종 검사 고정 SHA. 대상 사이트만 `preview` 빌드, 16개 화면 표본.

## 교정 예시
- **/4.html 상록구:** '구 단위 주소 비교 관련 꽃' → 구·동·도로명 주소를 먼저 확인하는 배송지 안내. FAQ는 주소 정보·상품을 고르는 기준을 분리.
- **/28.html 대부동동:** '수령자 부재 관련 꽃' → 실제 수령자 부재 시 대리 인계·문앞 보관 가능 여부 안내. FAQ도 배송·인계 조건 질문과 답변으로 수정.
- **/29.html 대부북동:** '추가 배송비 관련 꽃' → SKU별 추가배송비·최종 결제금액 확인. 원장의 옛 추가요금 안내를 모든 주문의 현행 고정 조건이라고 주장하지 않음.
- 기존 임의의 상호·배송 약속·추가비·후기·현재 영업 상태는 창작하지 않음.

## V5 원장·HTML·이미지·링크 검수
- [GitHub Actions V5 run 41043082525](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41043082525): **success**, 고정 소스 SHA `c46741b1404621fb5bcb7f4b676fe0bdbb286efc`.
- ZIP artifact `12970777802`; SHA256 `f593da71626c47c6c1e1499a693710a794ae47e8976889e6713c7fbf355822be`. ZIP을 독립 내려받아 SHA256 직접 비교.
- Manifest `pageCount=33`, **정적 파일50개 각각의 SHA256 전수 일치**, 내용 HTML33개 + 404 1개.
- copy-qa.json: 전체 33개 페이지 방문자 표시 문구 검사, 데이터필드 627개, 문단 264개 중 완전 동일 0개, 관련 오류 문구 0개, 특정 의미 구분용 16개 제목·소제목 사례 검사.
- `v5 audit`: 내부 참조 2,462건, **오류 0·경고 0**, 528쌍 전수 Jaccard 최대 **0.25768**, 원본 대표 3페이지 콘텐츠 해시 보존.
- 기존 이미지·SKU 개별 주문 링크 및 가격 보존, 전체 사이트 `noindex,nofollow`, robots `Disallow: /`, sitemap 없음. 390px/1440px × 8 표본 경로 = **16개** 로컬 Chromium 스크린샷·자산 디코딩·가로 넘침 검사 성공.

## V4 기존 Worker에만 배포
- 기존 전용 Workflow `.github/workflows/todayflower-isolated-preview-deploy.yml`, 최소 수정 `47f1ab3c892d27919b806cb82f020c4cdb570493`; 다운로드 크기 한도만 보정한 최종 실행용 커밋 `230781a19391089704dd205a0ed1ecf68b343b14`.
- 첫 실행 `41043363069`은 아티팩트가 약 39MB인데 읽기 한도가 30MB라 ZIP SHA 검사 실패. **Cloudflare에 배포하기 전 중단**됐으며 새 ZIP 생성/권한변경 없었음.
- [최종 V4 run 41043488953](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41043488953): **success**. 기존 Worker `sfv56-todayflower-preview`의 활성버전 `85e3bb72-605c-4b50-9973-5bf233cba92e` 확인 후 정확히 같은 Worker만 업데이트.
- 새 Worker 버전 `79324ecd-8100-495b-8c65-620fbdc146b7`.
- <https://sfv56-todayflower-preview.joseungil.workers.dev/>
- Live HTTP **41건**: 33개 HTML의 HTTP200 및 고정 artifact 바이트 일치, 이미지5개 원본 WebP와 바이트 일치, `robots.txt` 200·Disallow /, `sitemap.xml`/없는 경로는 HTTP404, 전 응답 `X-Robots-Tag: noindex`.
- 실제 Chromium 화면: `/`, `/4.html`, `/28.html`, `/29.html`, `/33.html` × 390px/1440px = **10개 성공**. 확인된 5장 AI 편집이미지 naturalWidth 1448px, 가로 넘침 없음. /4·/28·/29의 화면 상단 육안 확인 시 제목·도입 내용과 카드 흐름에 치명적인 레이아웃 결함 발견되지 않음.
- 실서버 QA artifact `12971866018`, ZIP SHA256 `9d65fb3b1343c00dafe13a8a53ee7edd3fb8b02fcb5a72356bce034336726ed9`; 직접 다운로드 및 해시 검사.
- 이번 회차는 **다른 Cloudflare Worker/사이트·새 도메인 연결·DNS·API Key/Secret·권한·IndexNow·검색 공개** 변경하지 않음.

## 근거·미확인 범위
- 지역명/코드는 과거 V4 공식 법정동 다운로드 원장 **2026-10-22 고정 자료**와 기존 검증된 Flowershop 관련 코드 기반. 정부 최신 재조회 및 법적 시행일 확인을 새로 완료했다고 주장하지 않음.
- 전국 협력 꽃집 배송 구조는 V4 `site/data/service-facts.json`의 **2026-10-21 사용자 보고**. 오늘 특정 주소 당일배송 가능 여부·접수 마감·추가 배송비·재고 보장은 독립 확인되지 않음. 각 SKU 판매처에서 결제 전 확인.
- ImageGen 5장의 **생성 시점 원본 실행**은 부모가 직접 접근하지 못해 제작 기록(gen_id)과 GitHub WebP 바이트·치수·실서버 이미지 응답을 증거 수준별로 구분.
- 자동 문장 규칙 및 16개 사례검사는 한국어 의미 전체를 대체하는 사람의 완전한 검수는 아님.
