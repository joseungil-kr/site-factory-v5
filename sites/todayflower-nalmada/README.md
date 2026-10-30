# 오늘꽃배달 — 안산시 지역 확장 (noindex)

> 현재 저장본: **안산시 1 + 일반구 2 + 법정동 30 = 총 33개 지역 안내 문서**. 원래 승인·검수된 3개 페이지 번호(1~3)는 고정했으며, 30개만 번호 4~33으로 추가했다. 이것은 전국 공개나 개별 주소의 당일배송 승인과 다르다.

## 2026-10-30 확장 최종 검증

- **완료:** source-verified 안산시 33페이지 noindex 오프라인 빌드, 내용 HTML 33 + 404 1, 정적 50파일 해시 전수 검증, 528쌍 최대 유사도 35.578%, 오류·경고 0.
- **검수 실행:** [GitHub Actions run 41033421847](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41033421847), 고정 소스 SHA `166d9853a699534095888bc82068ac9ca083bf1f`.
- **결과물:** 아티팩트 `12966946765`, ZIP SHA256 `8c4fee9d6ea204d851b29d2f851ca0c5419008c360777ccc9c16c6f37454d4bb`; 390px/1440px × 6경로 화면 12장.
- **주의:** 기존 noindex `workers.dev`는 앞선 **3페이지 운영본**이다. 이번 33페이지 빌드는 **배포하지 않았다**. 30개 추가 페이지의 배송서비스 실제 가능 여부는 미확인.
- **검수 증거 원문:** [QA_ANSAN33_NOINDEX_20261030.md](QA_ANSAN33_NOINDEX_20261030.md).

## 제작·검수 상태
- 운영 도메인 후보: `todayflower.nalmada.net`. **DNS / custom domain 변경 없음**, `publishEnabled=false`, IndexNow 비활성화.
- 기존 noindex Worker `sfv56-todayflower-preview.joseungil.workers.dev`에는 앞선 **대표 3페이지의 성공본**이 유지되며, 이번 33페이지는 오프라인 빌드와 검수 대상이다. 새 아티팩트 배포 여부는 별도 추적한다.
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
