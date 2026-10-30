# 오늘꽃배달 — 안산시 지역 확장 (noindex)

> 현재 저장본: **안산시 1 + 일반구 2 + 법정동 30 = 총 33개 지역 안내 문서**. 원래 승인·검수된 3개 페이지 번호(1~3)는 고정했으며, 30개만 번호 4~33으로 추가했다. 이것은 전국 공개나 개별 주소의 당일배송 승인과 다르다.

## 2026-10-30 19시 의미 오류 수정 — 최신 완료본

- 지역명 + '구 단위 주소 비교 관련 꽃', '수령자 부재 관련 꽃', '추가 배송비 관련 꽃' 등 주문 조건을 상품처럼 소개하던 템플릿 표현을 30개 신규 지역 도입·FAQ에서 교정했다. 16개 관련 제목·소제목도 배송·수령·결제 의미에 맞게 수정. 대표 3개는 내용 해시 보존.
- 최종 고정 V5 소스 SHA `c46741b1404621fb5bcb7f4b676fe0bdbb286efc`, [V5 run 41043082525](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41043082525) **success**; artifact `12970777802`, SHA256 `f593da71626c47c6c1e1499a693710a794ae47e8976889e6713c7fbf355822be`. 전체 HTML 33 + 404, 파일 50개 해시 전수 일치, 627필드·264문단·528쌍 전수 검사 통과, 최댓값 25.768% (내용 차별성/현재 배송 가능 여부 별개).
- 기존 noindex Worker `sfv56-todayflower-preview` **전용 배포만 성공**: [V4 run 41043488953](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41043488953), 현재 버전 `79324ecd-8100-495b-8c65-620fbdc146b7`. [미리보기](https://sfv56-todayflower-preview.joseungil.workers.dev/) 실제 41 URL HTTP 검사 및 모바일/PC 10개 실제 화면 통과. `robots.txt` Disallow, 전체 `X-Robots-Tag: noindex`, sitemap404 보존.
- 작업상세·재현 증거: [QA_SEMANTIC_INTENT_NOINDEX_20261030.md](QA_SEMANTIC_INTENT_NOINDEX_20261030.md). 아래 과거 교정 기록은 이전 실행 당시 상태를 보존한 역사 자료로 취급한다.

## 최신 교정·실서버 검증 (2026-10-30 최종)

- **33개 페이지 문장 전수교정 완료:** 신규 30페이지 조사·마침표·미완성 구·FAQ 반복 수정, 원래 3페이지 보존. 사이트 데이터 627필드 + 실제 완성 HTML 33개에서 한국어 조사를 검수했고 264개 전체 문단의 동일문단 0개, 전수 528쌍 최대 유사도 27.416%.
- **V5 최종 산출물:** [run 41038355570](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41038355570), 소스 SHA `5461da731fe2e316ae511cf59d313fd2821bd704`, 아티팩트 `12968394931`. 정적 파일 50개 해시 전수검수, 오류·경고 0건, 로컬 Chromium 390px/1440px 12개 화면 성공.
- **기존 noindex Worker에 33개 전부 배포 완료:** [V4 run 41038687704](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41038687704), 현재 버전 `85e3bb72-605c-4b50-9973-5bf233cba92e`. [33페이지 noindex 미리보기](https://sfv56-todayflower-preview.joseungil.workers.dev/) 실제 41건 HTTP 및 6개 브라우저 화면 검사 통과.
- **검색은 여전히 차단:** workers.dev `X-Robots-Tag: noindex`, HTML `noindex,nofollow`, robots.txt `Disallow: /`, sitemap.xml 404. 별도 도메인/DNS/인증/Secret/권한 변경이나 index 전환은 하지 않음.
- **최종 인수 기록:** [QA_PROOFREAD_33_LIVE_NOINDEX_20261030.md](QA_PROOFREAD_33_LIVE_NOINDEX_20261030.md). 아래 3페이지 시점 기록/33페이지 오프라인 초안 기록은 역사 자료이며 현재 최종 상태가 아니다.

## 2026-10-30 확장 최종 검증

- **완료:** source-verified 안산시 33페이지 noindex 오프라인 빌드, 내용 HTML 33 + 404 1, 정적 50파일 해시 전수 검증, 528쌍 최대 유사도 35.578%, 오류·경고 0.
- **검수 실행:** [GitHub Actions run 41033421847](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41033421847), 고정 소스 SHA `166d9853a699534095888bc82068ac9ca083bf1f`.
- **결과물:** 아티팩트 `12966946765`, ZIP SHA256 `8c4fee9d6ea204d851b29d2f851ca0c5419008c360777ccc9c16c6f37454d4bb`; 390px/1440px × 6경로 화면 12장.
- **당시 기록:** 이 단락은 최초 33페이지 오프라인 QA 시점에 쓰였고 그때는 3페이지 운영본이었다. 현재는 위 최종 검수에 따라 33페이지가 noindex 미리보기로 배포되었다. 개별 주소 당일배송 가능 여부는 여전히 미확인.
- **검수 증거 원문:** [QA_ANSAN33_NOINDEX_20261030.md](QA_ANSAN33_NOINDEX_20261030.md).

## 제작·검수 상태
- 운영 도메인 후보: `todayflower.nalmada.net`. **DNS / custom domain 변경 없음**, `publishEnabled=false`, IndexNow 비활성화.
- 기존 noindex Worker `sfv56-todayflower-preview.joseungil.workers.dev`에 **교정한 대표 33페이지**가 반영되었다. 대상·버전·HTTP 원문 검사는 상단 최종 QA 보고서를 참조한다.
- 검증된 원래 3페이지의 증거: V5 run [41029442885](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41029442885), 고해상도 이미지 산출물 `12965067290`, SHA `9c983dab6b69a724ae46dbff4a17a0c16f24eeed`.
- 독립 noindex 실제 배포(이전 3페이지): V4 run [41029861948](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41029861948), Worker 버전 `b571636a-4aba-4756-9793-02e5233c5e14`. 11개 HTTP 검증에 성공했으나 **이번 33페이지 배포를 의미하지 않음**.
- 5개 ImageGen 이미지의 **생성원본 접근·생성 과정**은 원본 생성 당시의 기록(gen_id)으로 추적한다. 부모가 해당 생성 원본을 직접 열람하지 못했으므로 원본 생성 과정의 독립 확인으로 주장하지 않는다. 별도로 GitHub WebP 바이트 SHA·내장 VP8 1448×1086·실제 Chromium 표시/HTTP 응답은 검증된 범위다.
- 이미지 5개는 **연출용**으로 상품·납품·수령 사진처럼 표시하지 않는다. `assets/library/todayflower/` 총 10개 파일 중 실제 HTML에 각 페이지당 AI 5장 + V5 기존 편집 이미지 2장 = 내부 이미지 7장. 별도 `fwith.co.kr` 상품 사진 링크를 그대로 유지.
- 새로운 30개 페이지의 본문은 수령상황과 선택 기준을 달리한 가이드이며, 해당 동에 특정 점포·시설·배송시간·수요가 실제 있다는 뜻이 아니다.

## 지역 원장: 출처와 확인 범위
- 공식 계통: [행정표준코드관리시스템](https://www.code.go.kr/stdcode/regCodeL.do). V4 `data/regions/sources/official-codes.zip` 2026-10-22 다운로드 기록, 고정 SHA256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`.
- V4 `data/regions/master.json`은 **시도16·시군구229·일반구39 = 총284건**만 담는다. 하위 읍면동의 직접 공식 원장으로 취급하지 않았다.
- Ansan 30개 법정동 코드는 **기존 Flowershop V5 artifact `12874109256`의 고정 SHA 원장/HTML 내 코드·지역명을 대조하여 추출**했다. 원본 ZIP을 이번 작업에서 직접 재다운로드·재파싱한 것으로 주장하지 않는다.
- V5 `seoul_gyeonggi_current_dong.json`의 **1,732개는 별도 후보 동명 자료**다. 안산에서 확인된 44개 후보를 이번의 30개 법정동과 혼용하지 않았다.
- 법정동 원장 기록: [ansan-legal-regions-evidence.json](ansan-legal-regions-evidence.json). 행정동 코드·최신 법적 시행일·실제 주소별 배송 조건은 아직 독립 확정하지 않았다.

## 실제 판매처 서비스 범위
- V4 `site/data/service-facts.json`은 **2026-10-21 사용자 보고**로 전국 협력 꽃집 제작·배송 구조를 기록한다. 이는 업체 내부 설명을 기록한 것이며 개별 법정동별 **당일배송·특정 시간·무조건 가능·무료배송·전 SKU 현행 재고**를 입증하지 않는다.
- 상품·가격·구매 경로는 앞서 실제 판매처 `fwith.co.kr`에서 확인한 **2026-10-30 기준 기록**이다. 주문 전 현재 표시가격·추가배송비·선택 옵션·가능 시간을 다시 확인하도록 명시한다.
- 대부남동·대부동동·대부북동은 일부 상품의 추가요금 안내를 참조하지만 적용 대상·금액을 전체 상품에 일반화하지 않는다.

## 재현·검수 명령
```sh
python -m unittest discover -s tests -p test_todayflower_pilot.py -v
python -m v5 plan-check --site todayflower-nalmada
python -m v5 build --site todayflower-nalmada --mode preview
python -m v5 audit --site todayflower-nalmada
```
목표: 33개 내용 HTML + 404 1개, sitemap 생성 안 함, robots.txt Disallow /, 33페이지 전수 noindex/canonical 없음, 528쌍 문자 5-gram 유사도 49% 미만, 상품군 4종의 원본 SKU 주문 링크·가격 보존, 내부 연결·이미지 실파일 검사. CI는 해당 사이트만 좁게 실행하고 화면은 대표 3개 + 확장 지역 표본만 캡처한다.

과거 기록: [3페이지 릴리스 보고](RELEASE_REPORT_20261030.md), [고해상도 이미지 증거](IMAGE_REPLACEMENT_REVIEW_20261030.md), [기획·연구 기준](RESEARCH_AND_RELEASE_GATES.md).
