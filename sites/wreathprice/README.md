# 알뜰화환 — 지역 화환 가격 비교 (V5 작업자2 독립 프로젝트)

**최신 콘텐츠 품질 판정(2026-10-31):** 읍면동 4,632개는 청운동·신교동과 같은 공통 본문·FAQ를 재사용하므로 지역별 고유 SEO 콘텐츠로 인정하지 않습니다. 배송 가용성 근거 0건으로 **index 승격 대상 0페이지**, 모든 4,935 HTML의 기존 noindex 유지. [콘텐츠 검수 기록](CONTENT_REVIEW_20261031.md). 수정 FAQ는 QA 통과했으나 운영 반영 확인 전까지 기존 Worker 배포본과 구분합니다.

현재 상태(2026-10-31 KST): **공식 ZIP에서 추출한 읍·면·동 4,632개 + 기존 상위 지역·허브 303개 = 전체 HTML 4,935개. 기존 Worker noindex 배포 및 승인된 wreathprice.nalmada.net Custom Domain 연결, 실제 HTTPS·모바일 검증 완료. 검색 색인은 미전환(지역별 실배송 검증 0건/공통 내용 중복).** 현재 연결 호스트: `wreathprice.nalmada.net` (2026-10-31 사용자 승인으로 연결, 여전히 noindex).

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
- **이전 미리보기 당시 기록:** 도메인 연결 전에는 Custom Domain이 없었음. 현재는 2026-10-31 연결 완료 및 HTTPS 검증 완료; 공개 index 전환은 여전히 보류.
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

## 2026-10-31 전국 상위 행정구역 확장 (최신)
- **원장 출처/범위:** V4 `data/regions/master.json` blob `13d43fc3f2492b29b1680858235fe0ac0cd10580`, 2026-10-22 확보 자료. `verified-regions-nationwide.json`에 284개 상위 행정구역(시·도 16, 시군구 229, 일반구 39) 정확히 고정. 원 출처의 실제 적용일은 미확인; 읍면동 전체 또는 배송 가능 범위 자료가 아님.
- **중복 배제:** 기존 안산시/상록구 2개 상위 코드 제외 후 신규 282개. 기존 본오동까지 대표 3페이지 + 282 + 전국목록 허브 = **총 286개 HTML**.
- **엔진:** 기존 `build.py`, `expand.py`와 이미지 5개, 가격·문의·실상품 링크를 재사용하는 `expand_nationwide.py`. 16개의 공통 편집 주제를 순환하고 근조 3단 SKU 비교는 공통 1종임. 지역명과 해시 차이는 독립적인 고유 콘텐츠 품질의 근거가 **아님**.
- **링크:** 기본 홈 `/ansan/`은 최초 16개 신규 페이지 및 전국목록 `/regions/`로 연결됨. 허브는 284개 상위 코드 각각의 문서로 연결하며 기존 2개는 대표 URL로 이동. 모든 내부 링크 대상·중복 코드 검사 완료.
- **빌드 QA:** [V5 run 41094905895](https://github.com/joseungil-kr/site-factory-v5/actions/runs/41094905895) success, artifact `12996141154`. HTML 286개, 이미지5 실제 SHA/치수, 284코드 중복0, 내부링크·noindex·원장 비교 통과.
- **기존 Worker에 noindex 배포:** [V4 run 41095222881](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41095222881) success, artifact `12995952552`. Worker `sfv52-wreathprice-preview` 버전 `7be165ca-d1dc-4d20-9226-5ae0ea6bbc5a`, V5 배포 소스 `d23a603f74290f245bda613271bf2ac6d2bc94ac`. 실제 HTML **286/286 HTTP200**, X-Robots-Tag 및 meta noindex, 상품 링크/이미지 5개, WebP 원격 바이트 해시, robots Disallow, sitemap/없는 페이지 404, canonical 없음 검증. 사용 도메인은 기존 `*.workers.dev`만 해당. 롤백 불필요.
- **가용성:** 실제 배송 가능 지역 확인 0건, 배송 추가금·리본 비용 미확인; 상품 표시는 실거래 총액이 아님. 전국 모든 지역에 배송된다고 주장하거나 최저가, 지점명, 후기 조작 없음.
- **비공개/공개 구분:** 신규 `wreathprice.nalmada.net` 도메인/DNS/소유확인/Secret·권한 변경 없음, 공개 index 미전환. 공개 URL의 자기 canonical·index sitemap은 커스텀 도메인 승인 및 배송 가용성 검증 후 별도 단계.

## 2026-10-31 현재 공개 호스트 및 전국 읍면동 후속 (최신 확정)
- **운영 호스트:** https://wreathprice.nalmada.net/ · https://wreathprice.nalmada.net/localities/ · 예시 https://wreathprice.nalmada.net/locality/1111010100.html (서울특별시 종로구 청운동). HTTPS 확인. 내부 홈↔전국 읍면동 허브↔16개 광역 허브↔4,632개 읍면동 경로는 전수 링크 검사 통과.
- **코드 원본:** V4 `data/regions/sources/official-codes.zip`, SHA-256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`, 2026-10-22 수집. ZIP의 53,403 자료행 중 `존재` 20,560행, 그 중 이름 끝이 `동·읍·면`인 4,632코드(상위 코드 부모 일치 4,632건, 미일치 0). **리 등 다른 수준/명칭은 포함하지 않으며, 현재 날짜의 공식 재수집 자료가 아님.**
- **산출물:** V5 `expand_lower.py --archive <approved-V4-ZIP>`, `test_lower.py`; 실제 빌드 4,935 HTML = 기존 대표 3 + 기존 상위 신규 282 + 상위 목록 1 + 신규 읍면동 4,632 + 광역 읍면동 허브 16 + 전국 읍면동 허브 1. 공식 검증은 **지역명과 코드뿐**이며 배송 가능 지역 0건. 기존 이미지 5개와 실상품 주문 링크 5개 재사용.
- **오프라인 검수:** [V4 run 41186127429](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41186127429) 성공. 4,935 HTML 코드 중복·깨진 링크 0, 이미지 해시, 가격·고객문장, noindex 검증.
- **미리보기 배포:** [V4 run 41186242257](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41186242257) 성공. 동일 Worker `sfv52-wreathprice-preview`, 100% 버전 `c5f7b9c6-3198-4996-8776-6bf287cb510f`, V5 배포 소스 SHA `37ec80f703be8fda5388e0777238b53bf0427306`. 대표 57개 실제 HTTP 응답, robots·이미지·noindex 확인, rollback 미실행.
- **승인된 Custom Domain:** [V4 run 41186379115](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41186379115) 성공. 기존 계정/zone/Worker/미리보기 버전 확인 후 `wreathprice.nalmada.net` 정확한 호스트 **1개만** Cloudflare Workers Custom Domain API로 연결. 수동 DNS API 쓰기 0, 신규 Secret/권한 변경 0. HTTPS는 두 번째 재검사 성공.
- **공개 호스트 검증:** [V4 run 41186449493](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41186449493) 성공. 운영 호스트 11개 HTTP 표본과 390px·1440px Chromium 화면 12개, 이미지 로딩·넘침·링크·robots 및 noindex 확인. 증거 artifact `13037185824`.
- **공개 색인 정책:** Custom Domain은 접속 가능하지만 전역 **noindex,nofollow** 및 `robots.txt` Disallow. `sitemap.xml` HTTP 404, noindex 페이지 canonical 없음. 이는 현재 검증된 품질에 맞는 의도적 설정이며 공개 index·사이트맵·검색등록 완료 상태가 아님. 기존 4,632개는 공통 가격표/설명과 지명 위주로 구성되고 실배송·지역별 추가금/현장 차별 정보는 미확인이므로, HTML·해시 차이를 고유 검색 콘텐츠로 간주하지 않음.
- **추가 실증 필요:** 지역 배송 가용성·시간·배송비·리본 포함·상품 실물 사양을 판매처 근거로 확보하고 대표 지역의 독립적인 페이지 품질을 개선·검증한 뒤 공개 색인 범위를 별도로 결정.

## 2026-10-31 대표 읍면동 콘텐츠 공개 전 재검수 (최신)
- **대표 사례:** `/locality/1111010100.html` 청운동과 `/locality/1111010200.html` 신교동. 지역명 치환 전후의 본문·FAQ가 실질적으로 동일했으며, 이름만 바꾼 페이지를 '고유 지역 콘텐츠'로 인정하지 않음.
- **원격 소스 수정:** `expand_lower.py`는 법정동 ZIP이 확인한 지역명·상위 지역만 문장에 사용하고, 실제 주문자가 확인할 구체적인 질문(도로명 주소 및 수령 시설, 희망 날짜·시간, 배송비·리본 비용, 근조 3단 상품 사양)을 제시함. 이는 지역별 독립 현장 정보를 확보했다는 뜻이 아니며 **공통 문구·FAQ 반복 구조를 명시적으로 유지/공개**.
- **동일 용도 가격 비교:** B201/B203/B205 59,000/79,000/109,000원, 근조 기본·고급 기준가 차이 20,000원. 축하 C205/C030은 근조 등급과 혼합 비교하지 않고 별도 유형 안내. 주문 상세 5개 링크/AI 안내 WebP 5개 그대로 보존.
- **품질 게이트:** `test_lower.py`는 청운동·신교동에서 지역명 정규화 후 공통 본문이 완전히 같은 사실을 검사하고, 배송 가능성 근거 0·공개 index 불가·canonical/sitemap 부재를 명시적으로 강제한다. 공식 ZIP의 코드 4,632개는 지명·상위 행정구역만 검증하며 배송·지역별 가격, 실제 추가 배송료는 미확인.
- **공개 적합성 판단:** 현재 승인된 정상 호스트 `wreathprice.nalmada.net` 연결 자체는 완료됐지만 4,632개 읍면동의 **공개 색인 적합성 충족 수는 0개**. 따라서 허위 지역 정보/중복 템플릿을 공개 index 전환하지 않음. 전체 noindex 및 robots Disallow, sitemap 404, canonical 부재를 유지. 지역별 확인 데이터가 확보된 페이지만 별도 후속 심사.

**최신 배포 판정(2026-10-31 11:30 UTC):** 사용자 1회 재승인 후 전용 V4 Workflow를 수정·배포했고 [run 41197038256](https://github.com/joseungil-kr/site-factory-v4/actions/runs/41197038256)이 성공했습니다. Worker 버전 `e3f6df1e-15dc-4289-ac19-c3429407b13e`; 배포 전용 V5 source `4a58d2a14b7c65707484bd313c614205e03d2aaf`. 청운동/신교동 질문 수정 및 공통 템플릿 중복 검사는 기존 `workers.dev` 원격에서 통과했습니다. 정식 도메인의 최신 본문은 이번 재시도에서 별도 독립 HTTP 확인이 안 됐으므로 동일하다고 단정하지 않습니다. 지역 고유 서비스 정보 확인 0, 공개 색인 대상 0, 전역 noindex 유지. [상세 증거](CONTENT_REVIEW_20261031.md).
