# V5.1 신규 군 근조화환 시험사이트 — 작업자5 문구·실제 HTML 재검수 (2026-11-08)

> **범위:** `county-funeral-ownerprivate-test` 신규 비공개 시험사이트. 기존 운영 사이트·Worker·DNS·인증·검색등록·공개 배포 **변경 없음**. 본문은 localhost/정적 ZIP 검수 증거이며 ChatGPT Sites의 실제 owner-private URL과는 다르다.

## 이번 검수의 소스·커밋

- 기존 인계 HEAD `7aac26643ec227753393391e5d0433462974a046`; 최종 생성·QA **콘텐츠 SHA `fde38872fa1c52ace93dbaf3937a175beca16658`**.
- 변경 커밋: [1c5d8ec](https://github.com/joseungil-kr/site-factory-v5/commit/1c5d8ecb282f9c1f079b68a7a8c00afffd0cfffc) → [20c08f2](https://github.com/joseungil-kr/site-factory-v5/commit/20c08f28730bcb0fec7309490d0902b67007aa17) → [8afaeb1](https://github.com/joseungil-kr/site-factory-v5/commit/8afaeb1fd0d59bdf21de3336a2d54000a7ef2205) → [fde3887](https://github.com/joseungil-kr/site-factory-v5/commit/fde38872fa1c52ace93dbaf3937a175beca16658).
- [인계 이후 소스 전체 diff](https://github.com/joseungil-kr/site-factory-v5/compare/7aac26643ec227753393391e5d0433462974a046...fde38872fa1c52ace93dbaf3937a175beca16658): **4개 파일만 수정** — `scripts/county_copy_pools.py`, `scripts/build_county_funeral_trial_inputs.py`, `scripts/verify_county_independent_html.py`, `tests/test_v51_county_selected_skus.py`.
- 반복적 배송비·상품 규격 고지 및 AI식 면피성 표현 개선. 고객이 불필요하게 보는 원장 증빙 시각, 내부 검증 상태, 비실재 이미지 지칭 삭제. 필요한 불확실성(실제 배송 가능·추가비·반입 조건)은 고객의 **상품 주문 화면/시설 확인 순서**로 안내.
- FAQ 답변을 상품 선택·반입/리본/배송·구매 단계에 연결. 중간 CI #42438799534에서 전국 배송비 FAQ 질문과 답변 불일치가 발생해 자동 84점으로 **FAIL**; `8afaeb1`에서 해당 질문 분기를 수정한 뒤 최신 콘텐츠 SHA로 전부 재실행.
- 리본 설명 반복이 많은 일부 페이지에 조의 문구 실례, 회사·단체 약칭 결정, 빈소 변경시 문의 방법, SKU별 비교라는 실제 구매 행동을 보강. 기존 여섯 `/26,67,69,73,77,86.html`의 '아래 도형' 오류 수정은 **보존**.

## 최종 오프라인 CI — 모두 `fde38872fa1c52ace93dbaf3937a175beca16658`

| 실행 | 상태·주요 근거 |
|---|---|
| [빌드/95페이지/정적 ZIP #42439168716](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42439168716) | SUCCESS, 95 HTML, 103파일, 독립 실제 HTML 파서 오류 0 |
| [오프라인 95 HTML 검토 #42439168655](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42439168655) | SUCCESS, 페이지 링크·고립 페이지·robots/noindex 검사 |
| [회귀·점수·Chromium #42439168610](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42439168610) | SUCCESS, Python **38 tests**, 본문 95/95 검사, 규칙 보조 평가 **49/95**, 최저 **93**, 최고 **94**, 평균 **93.27**, 자동 90점 미만 0, **19경로×390/1440=38** 로컬 화면, 상품 카드 110개 검사 |

**점수 출처 주의:** 위의 49개 점수는 실제 생성 HTML을 입력으로 사용한 **규칙 보조 평가**이며 독립 인간 심사가 아니다. 아래 표는 이번 작업에서 실제 정적 ZIP 페이지의 제목·본문·상품 카드·FAQ를 읽고 판단한 별도의 편집 평가. 같은 사실을 여러 차례 반복하는 정도에 따라 점수를 더 엄격하게 조정했으며 가중치/검증 기준을 낮추지 않았다.

## 실제 최종 HTML 직접 읽기 — 10/95 페이지(10.53%)

평가기준: 자연스러움·고객 존중 **25**, 사실·SKU·가격 **30**, 구매자 정보 효용 **30**, 중복·면피 표현 배제 **15**. 각 표본 90 이상이어야 통과. 점수는 본 작업자의 문서 편집 판단으로서 자동·인간 독립심사와 구분.

| 정적 경로 | 직접 읽은 정보 및 차별화된 구매 도움 | 자연 | 사실 | 효용 | 반복 | 총점 |
|---|---|---:|---:|---:|---:|---:|
| `/` | 전국 군별 탐색, 상품 기준가·수령지 배송비 확인, 판매처 직접 주문 | 23 | 29 | 28 | 12 | **92** |
| `/2.html` | 광역 소속 군 17개 링크, 해당 군 선택 후 시설명·빈소·주소 주문 | 23 | 29 | 28 | 12 | **92** |
| `/7.html` | 경기도의 3개 군 구분과 상품·주문 경로 | 23 | 29 | 28 | 12 | **92** |
| `/26.html` 영광군 | B201/B202 각 59,000원, 조의 문구 실례·발신인 약칭·영광군 읍면 11곳 | 23 | 29 | 28 | 12 | **92** |
| `/67.html` 의령군 | B202 59,000원/B205 109,000원, 고인·빈소 정보 및 변경 문의, 읍면 13곳 | 23 | 29 | 28 | 12 | **92** |
| `/69.html` 창녕군 | B201/B205, 가격차 50,000원, 배송료·리본 비용 별도 확인과 읍면 14곳 | 22 | 29 | 28 | 12 | **91** |
| `/73.html` 산청군 | B201/B202/B205/B206 네 카드, 실제 구성·상품별 상세 선택, 읍면 11곳 | 23 | 29 | 28 | 12 | **92** |
| `/77.html` 홍천군 | B202 59,000원/B206 149,000원, 3단 반입·설치 장소 및 대체형 문의 | 23 | 29 | 28 | 12 | **92** |
| `/86.html` 고성군 | B201/B202 각 59,000원, 상품번호별 상세 비교 및 수령 장소·리본 준비 | 23 | 29 | 28 | 12 | **92** |
| `/95.html` 부안군 | 장례식장 반입 조건·희망일·대체상품 상담, B202/B206 선택 | 23 | 29 | 28 | 12 | **92** |

**최저 편집 판단 91점**, 자동 평가 결과와 별개. 단, 95페이지 전체에 비슷한 배송/리본 안전 안내의 반복 가능성이 남아 있어 반복 점수는 만점으로 표시하지 않았다. 군별 실제 배송 가능 여부/시설 반입 허용/최종 가격·재고는 구매 시점 확인이 필요하며 근거 없이 단정하지 않았다.

## 정적 패키지 및 검사 증거

- [최신 ZIP artifact **13600304748**](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42439168716/artifacts/13600304748), 실제 내장 `county-funeral-ownerprivate-95-pages.zip`.
- **SHA256 `1fe8c92b157678dedde921b14dc5f298706b225a58507ab46dcc15c2e996780a`**, 콘텐츠 `fde38872fa1c52ace93dbaf3937a175beca16658`. 총 103파일 = 95콘텐츠 HTML + 404 HTML + CSS 4 + SVG 1 + JS 1 + robots 1. **103개 파일의 실제 SHA256과 manifest 전부 일치**.
- 생성 전체 HTML 실제 파싱: **95개 페이지, 231개 판매 상품 카드**. 각 카드의 SKU B201/B202/B205/B206, 표시가 **59,000/59,000/109,000/149,000원**, 해당 `https://fwith.co.kr/shop/item.php?it_id=...` 링크 일치. 오류 0건. `robots.txt` Disallow, HTML noindex/nofollow, canonical 없음, 사이트맵·RSS·IndexNow 미생성.
- HTML 전수 검색: '아래 도형', '형태 안내 이미지는', '재확인한 법정동 코드', '현재 보유한 가격 원장', '이 명단은 배송 가능 여부의 확인 자료가 아니라', '지역 안내 페이지에서는 결제정보를 받지 않습니다' **본문 0건**.
- [최신 브라우저 캡처 artifact **13601030632**](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42439168610/artifacts/13601030632): Chromium localhost 19경로×390/1440 검증, 38장. `/26.html` PC·모바일 원본 화면을 직접 열어 본문, 상품 카드, CTA를 시각 확인했으며 가로잘림·상품 링크 접근 오류 없음.

## 배포 상태 / 관리자 후속

- **실제 owner-private 배포: 미실행·미확인.** 현 Chat에서 ChatGPT Sites 새 프로젝트 생성/정적 파일 업로드/소유자·비인가 사용자 세션 비교를 수행할 연결 액션이 없음. 이는 Sites 제품의 지원 여부에 대한 일반 결론이 아니라 현재 연결에서의 실행 불가.
- **비인가 접근 차단을 noindex로 대체하지 않음.** 관리자 별도 owner-private 경로에서 103개 파일 업로드 후 본인 접근 성공/비인가 접근 거부를 각각 확인해야 한다.
- 기존 운영 사이트·Worker·DNS·보안·권한·인증·Secret·결제·검색등록 수정 없음. 이번 작업은 새 정적 패키지와 브랜치상의 한정 소스만 변경.
