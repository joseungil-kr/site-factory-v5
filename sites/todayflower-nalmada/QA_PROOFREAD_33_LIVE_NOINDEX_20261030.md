# 오늘꽃배달 33페이지 문장 전수교정 · noindex 배포 검수 (2026-10-30)

## 최종 판정
**33페이지의 조사·문장 완결성·중복 교정과 기존 독립 noindex 미리보기 배포·HTTP/Chromium 검수 통과.**
`todayflower.nalmada.net` 도메인 DNS·소유확인, 신규 Worker·Secret·권한, 검색 공개/index 및 IndexNow는 변경하지 않았다.

### 실제 소스 수정
- 사용자 발견: `/33.html`의 `화분와`, `화분를`, `화정동라는`, 마침표 누락.
- 원문 전수 확인에서 신규 30페이지의 조사 오류·미완성 명사구·접속 문장 누락·중복된 안내/FAQ를 확인하고 실본문에 수정. 이전 승인된 대표 3개 콘텐츠 해시는 보존.
- 데이터 교정 SHA: `eb17bb713cc3e70fe56a1c7e13d4746372cadaf9`, `6aa0284f3a467f9a572165665b03d73d630981b3`, `743eeeb25c6e69cab8aa258f03722b3900194fa0`.
- 추가 HTML 검사에서 `/5.html` `꽃다발와`, `/8.html` `화분와`, `/23.html` `화환와`, `/33.html` `화분와`를 섹션 소개문에서도 찾아 수정.
- 제목 디자인: `v5/todayflower_markup.py`의 데스크톱 긴 한국어 제목 자간·최대 글꼴 크기·`word-break: keep-all` 적용. 모바일·PC에서 글자 중간 줄바꿈을 줄이고 스크린샷 확인.
- 총 **33페이지 × 19개 데이터 필드 = 627개** 및 실 HTML 33개 표시 텍스트 QA. 문단 전체 **264개 중 동일문단 0개**. 그램 유사도는 문장 표절/검색가치 독립 평가를 대체하지 않는다.

### 전수 검증 — V5 GitHub Actions
- 최종 고정 소스 SHA: `5461da731fe2e316ae511cf59d313fd2821bd704`
- V5 실행: https://github.com/joseungil-kr/site-factory-v5/actions/runs/41038355570 — **success**
- V5 결과물 `12968394931`, ZIP SHA256: `d7b624366ee8ac93a1fe76cdd24131f0b18f4a8af0dfa71b7c4fbdf71353c36b`
- 별도 교정 테스트 `tests/test_todayflower_copy_quality.py` 및 기존 `tests/test_todayflower_pilot.py` 성공. 33개 페이지 로컬 HTML+404 총 **34개**, 전체 정적 **50파일의 매니페스트 SHA-256 전수 일치**.
- `v5 audit` 내부 참조 **2462**, 오류 **0**, 경고 **0**, 전수 **528쌍** 문자 5-gram Jaccard 최고 **0.27416**.
- `reports/todayflower-nalmada/copy-qa.json`에 **627 필드, 33개 완성 HTML, 264문단, 동일문단0, 비교528** 영수증 저장.
- 모바일 390px / 데스크톱 1440px 각 6개 로컬 경로, 합계 **12개 실제 Chromium 화면**. 5개 AI WebP는 1448×1086이며 파일 실제 바이트·크기를 유지. 화면별 가로 넘침·내부 이미지 누락 없음.
- 원본 3페이지 `contentHashes` 그대로 보존. 기존 `fwith.co.kr` 판매처 8종의 상품명·참조 가격·SKU 직접 주문 링크 변경 없음.

### 기존 noindex Worker에만 배포
- V4 ops Workflow 파일: `.github/workflows/todayflower-isolated-preview-deploy.yml`
- 업데이트 커밋 `bba5cc2c05fdfe79d9d874c1d51dd3a483ed5c76` — 고정 V5 산출물만 사용, HTML 재생성 없음
- V4 실행: https://github.com/joseungil-kr/site-factory-v4/actions/runs/41038687704 — **success**
- 대상 Worker **`sfv56-todayflower-preview`**, 기존 버전 `cc424a15-1fd7-408c-b912-3c6147d66406`의 100% 활성 여부를 GET 확인한 다음 변경. 신규 버전 `85e3bb72-605c-4b50-9973-5bf233cba92e`.
- 미리보기 주소: https://sfv56-todayflower-preview.joseungil.workers.dev
- 실서버 **41건**: 콘텐츠 33 URL 모두 HTTP 200 및 원본 HTML 바이트 일치, 편집 WebP 5장 HTTP 200/VP8 해시·크기 검사, robots.txt 200 및 `Disallow: /`, sitemap.xml 및 없는 경로 404. **모든 응답 X-Robots-Tag: noindex** 확인. 생성된 모든 콘텐츠 HTML 자체도 `noindex,nofollow`이며 canonical 없음.
- Chromium 실서버 화면 `/`, `/4.html`, `/33.html` × 모바일390/PC1440 = **6개 실제 화면**. 모두 HTTP200/noindex, H1 1개, 가로 넘침 없음, AI 이미지 naturalWidth 1448 확인. 긴 H1 워드 브레이크 `keep-all` 검증.
- 실서버 검수 아티팩트 `12968912853`, ZIP digest SHA256 `1f3e9f1a4ec861733ff3c7993eda31f6285b64033d2560d1e163239c2ca169e3`.
- 배포 새 Secret/권한, 다른 사이트/Worker, DNS/custom domain 변경 없음. V4 ops 브랜치의 자동 foundation-check 실패 여부는 이 **독립 Todayflower Workflow의 성공 여부와 별도**.

### 역사 자료·생성 이미지 검증 범위
- 지역 명칭/코드 근거는 **V4 2026-10-22 공식 원장 스냅샷** 및 당시 Flowershop 고정 산출물. 이번 실행에서 행정표준코드 관리기관 최신 등록 현황을 다시 조회한 것이 아니다.
- `V4/site/data/service-facts.json`에 적힌 2026-10-21 사용자 보고 전국 협력 꽃집 배송 구조는 **일부 주소의 당일도착 보장·접수마감·요금·재고의 직접 검증이 아니다.**
- 원본 생성 실행은 부모의 접근 제한 때문에 원본까지 직접 열람했다고 주장하지 않는다. `site-spec.json images.provenance`의 이미지 생성 기록과, 공개 아티팩트/WebP의 SHA·VP8 치수·실제 브라우저 표시 확인은 별도의 증거 수준이다.

## 남은 일
공개 전환이나 전국 지역 확대는 별도 작업이다. 신규 30페이지의 실제 지역별 배송 가능 조건 및 개별 상품 판매조건은 필요 시 판매처에서 다시 확인한다.
