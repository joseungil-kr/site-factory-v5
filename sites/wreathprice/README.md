# 알뜰화환 — 지역 화환 가격 비교 (V5 작업자2 독립 프로젝트)

현재 상태(2026-10-30): **대표 시안 3페이지 / GitHub 실이미지 5장 검수 / 격리된 workers.dev noindex 미리보기 검증 성공. 커스텀 도메인 공개 배포 없음.** 도메인 후보: `wreathprice.nalmada.net` (DNS/충돌 사전 확인 전 연결 금지).

## 독립성과 포지셔닝
- 기존 `sites/wreath-region`, Wallsky, 꽃배달 운영 사이트, Secrets, 인증 파일, IndexNow 접수 상태 변경 금지
- 검색 의도: `{지역명} 화환 가격`, 근조/축하 상품 **확인된 표시 가격 + 최종결제 확인**
- 대표 지역: `안산시`(시) / `안산시 상록구`(구) / `안산시 상록구 본오동`(동)
- 제목: `{지역명} 화환 가격, 근조·축하 상품과 최종 주문금액 | 알뜰화환`
- 흐름: 답변 → 실상품 가격표 → 등급/꽃 구성 비교 → 배송·리본 추가금 확인 → 주문 정보 → 지역 배송 조건/FAQ
- 고객정보·결제정보 수집 없음. 상품 주문은 fwith.co.kr 직접 링크만 제공.

## 가격 근거
| 용도 | SKU | 상품 | 기준가 | 근거 |
|---|---|---|---:|---|
| 근조 | B201 | 근조 3단 화환 | 59,000원 | V4 `data/funeral-products/CATALOGUE.json` (2026-10-22) |
| 근조 | B203 | 근조 고급 3단 화환 | 79,000원 | 동일 |
| 근조 | B205 | 근조 특대 3단 화환 | 109,000원 | 동일 |
| 축하 | C205 | 축하 특특대 3단 화환 | 149,000원 | fwith.co.kr SKU 상세 (2026-10-30 재조회) |
| 축하 | C030 | 축하 2단 오브제 | 200,000원 | fwith.co.kr SKU 상세 (2026-10-30 재조회) |

※ 위 숫자는 **표시상품가**이고 **최종금액 아님**. 추가 배송비·리본 포함 여부는 확인되지 않은 경우 `미확인/주문 전 확인` 처리. 재고·도착·전국 무료배송·최저가 단정 금지.

## 이미지(실제 생성된 래스터 시안 5개)
- `assets/funeral-wreath.webp` — 근조화환 형태
- `assets/celebration-wreath.webp` — 축하화환 형태
- `assets/flower-detail.webp` — 꽃 구성 확대
- `assets/ribbon-guide.webp` — 리본 배치 모형
- `assets/florist-preparation.webp` — 포장 준비 연출

다섯 장 모두 ImageGen 생성 사진형 예시를 1024px 폭 WebP로 잘라 압축한 **동일 공용 풀**. 상품 실사진·납품/배송 실적 아님. 생성 공용 이미지 5개는 현재 GitHub `sites/wreathprice/assets/`의 실제 WebP 바이너리로 저장되었고 `image-manifest.json` 해시·치수와 원격 HTTP 검증을 통과했다. 원 ImageGen 호출에서 최종 각 WebP까지의 생성·편집 이력은 ZIP과 코드의 증빙 범위 내에서만 확인 가능하며 원본 기여 이미지에 대한 별도 영구 출처 ID·독립 편집 이력은 완전히 확인되지 않았다.

## 현재 QA 및 미리보기
- GitHub 실이미지 5개 저장 및 해시·실제 치수 검증: V5 [run 41018200247](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41018200247), 빌드·검증 3 tests 통과.
- 독립 noindex Worker `sfv52-wreathprice-preview`: [미리보기](https://sfv52-wreathprice-preview.joseungil.workers.dev/ansan/), V4 [run 41019185898](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41019185898) 에서 실제 HTML 3개 HTTP 200, 각 페이지 이미지/상품링크 5개, WebP 5개 HTTP 200/해시 일치, robots Disallow, sitemap/없는경로 404 통과.
- 로컬 Chromium 직접 `browser.goto`는 관리자 차단. HTML·CSS·WebP를 전달한 `set_content` 방식으로 390px 및 1440px 렌더링, 5/5 이미지 로딩·overflow 없음 확인; 실제 클라우드 브라우저의 시각 스크린샷 검수는 별도 확인 대상.
- 도메인 후보 `wreathprice.nalmada.net`의 Custom Domain 연결 없음(배포 사전 읽기); DNS 및 Workers Route 읽기 검증은 별도 미확인. 연결·공개 index 전환 금지.
- **역사적 상태:** 2026-10-30 초기 ZIP 인계 당시 GitHub 바이너리/preview가 없었으나 이후 완료됨. 기존 메모의 '업로드 미완료'는 현재 상태가 아님.
- 지역 확장은 V4 공식 코드 상위 지역 원장을 근거로 검증 범위를 한정하여 noindex 단계부터 수행.
- 기존 Wreath 네이버 인증 후속 상황과 IndexNow 접수는 별도 작업으로 보존하고 이번 프로젝트에서 변경하지 않음.


## 공식 상위 행정구역 원장 대조 및 1차 지역 확장 (2026-10-30)
- V4 원장: `joseungil-kr/site-factory-v4/data/regions/master.json`, Blob `13d43fc3f2492b29b1680858235fe0ac0cd10580`. 원 출처 `https://www.code.go.kr/stdcode/regCodeL.do`, 공식 코드 전체 다운로드 `https://www.code.go.kr/etc/codeFullDown.do`, 수집일 2026-10-22, 원본 ZIP SHA-256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`. 상위 지역 284건(시·도 16 / 시·군·구 229 / 일반구 39), 법정동 코드 `존재` 기준; 원본 적용일 `sourceEffectiveDate`는 미확인. 법정동 코드 최신성 및 개별 배송 가능성은 이 자료만으로 확정할 수 없음.
- 기존 Wreath 별도 보조 원장 `sites/wreath-region/regions.json`: 5,034개 하위 지역명(2025년 출처), 상위명 3,596건 일치·1,438건 미일치. 화분 전용 1,732건 수치를 신규 화환 가격 지역 근거로 사용하지 않음.
- `verified-regions.json`: 공식 원장으로 확인된 경기권 18개 상위지역 중 기존 시·구 대표 2개를 제외한 **추가 16개**만 추려 원장 코드·부모코드·출처행까지 고정.
- `expand.py`: 기존 `build.py`의 3페이지/실제 이미지 자산을 재사용하여 **독립 `dist-expansion/`에 16개 추가 noindex 문서, 총 19개**를 생성. 서비스 지역 16개가 확인됐다는 뜻이 아님(배송 확인 지역 0).
- 고유 내용은 코드/행정계층 정보 외에 16개의 편집 주제와 같은 용도 근조 3단 SKU(B201/B203/B205)의 공통 가격 비교 1종, 별도 축하·오브제 유형 안내 및 주문 확인 절차를 넣음. 지명만 바꾼 허위 배송 정보, 가짜 매장/리뷰, 최저가·배송 확약 없음. 다만 공통 가격표·사진·FAQ 재사용 구조이므로 검색 색인용 고유 품질이 별도로 검증되었다는 주장은 하지 않음.
- <https://github.com/joseungil-kr/site-factory-v5/actions/runs/41031299548> (성공): Python syntax, 5개 WebP 실제 해시/치수, 대표 3페이지 및 확장 16페이지의 테스트 3+3개 통과. 산출물 artifact `12966760028`. Sitemap 없음 / noindex 유지 / 공개 배포하지 않음.
- 이미지 출처: `image-provenance.json`에 기존 대화에서 생성된 원본 PNG의 SHA-256, generation ID, 크롭 좌표와 WebP 인코딩을 기록. 원본 PNG에서 5개 WebP를 바이트 단위로 재현하여 일치 확인. 원본 PNG를 GitHub에 추가하지 않았으며, 원본 접근 불가 환경에서는 해당 연결을 별도 재검증할 수 없다는 제한을 유지.

## 공식 자료 및 시장 비교
- https://fwith.co.kr/shop/item.php?it_id=B201
- https://fwith.co.kr/shop/item.php?it_id=B203
- https://fwith.co.kr/shop/item.php?it_id=B205
- https://fwith.co.kr/shop/item.php?it_id=C205
- https://fwith.co.kr/shop/item.php?it_id=C030
- https://flowername.co.kr/guide/wreath-price/
- https://xn--9m1bt77dma.com/price
- https://www.imflower.co.kr/prices.php
- https://www.dogus.co.kr/life/wreath-cost

외부 타사 가격과 배달 조건은 본 사이트의 사실/보장 문구로 사용하지 않는다.

## 2026-10-30 문구 교정 및 19페이지 미리보기 재검증 (최신)
- **수정 코드:** `sites/wreathprice/expand.py` — 고객용 본문에서 `municipality`, `ward`, 코드 등 내부 원장 표현 제거. 공식 코드·분류 등 증거는 `verified-regions.json`과 `dist-expansion/expansion-report.json`에만 유지. 'B205은' 등 조사 오류 제거.
- **비교 기준:** 동일 용도 근조 3단 B201 59,000원 / B203 79,000원 / B205 109,000원의 **공통 비교 1종**. 축하 3단 C205와 축하 오브제 C030은 가격순위에 혼합하지 않고 서로 다른 용도·형태로 소개. 기존 초안의 `combinations(5,3)`은 총 10개 비교 조합이 16페이지 중 6번 반복되었음; '16개 독립 비교 조합' 주장은 잘못된 기록이었음.
- **차별화의 한계:** 지역별 상세 실사·배송 조건·추가요금 자료가 없어 16개의 편집 초점은 각각 다르지만 같은 공통 가격/이미지/FAQ를 사용. HTML 해시가 다르다는 이유로 지역 고유 콘텐츠의 검색 품질을 보장하지 않음. 실제 확인된 배송 가능 지역은 **0개**.
- **V5 성공 QA:** [run 41035612269](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41035612269) 문법, 이미지 해시, 19페이지/고객 문구 회귀 테스트 통과.
- **V4 미리보기 배포 및 운영 URL 검증:** [run 41035787113](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41035787113) 성공. Worker `sfv52-wreathprice-preview`, 활성 배포버전 `e8bbac15-aec5-4d90-bf58-18669346af20`, 소스 SHA `9c27e766d47cf10ab32cbe84a0855cf5f1f0f142`. 19페이지 모두 HTTP200 및 noindex, WebP 5개 HTTP200/원장 해시 일치, robots Disallow, Sitemap 404 및 누락 페이지 404. 영수증 artifact `12968555792`. 새 도메인/DNS/인증/Secret/권한, public index 전환 없음.
- **실제 미리보기:** https://sfv52-wreathprice-preview.joseungil.workers.dev/region/4111000000.html
- **원장 확인 시점:** 2026-10-22 다운로드한 법정동 코드 상위 행정구역 자료; 원본의 법적 적용일(`sourceEffectiveDate`)은 미확인. 오늘 행정구역 재조회나 지역 배송 실측으로 오인시키지 않음.

- **브라우저 실렌더 검증:** [V4 run 41036075172](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41036075172) 성공. 기존 preview URL에서 안산·수원·장안구·단원구 × 데스크톱/모바일 = 8개 Chromium screenshot 생성, 실제 WebP 5/5 로딩·수평 넘침 없음·잘못된 문구 없음. Artifact `12967189850`.
