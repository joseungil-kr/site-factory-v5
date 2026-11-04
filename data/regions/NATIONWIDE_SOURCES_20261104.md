# Site Factory V5 전국 지역명 원장 — 원본 및 인계 (2026-11-04)

## 지역명 후보의 정확한 출처와 용도

- **기본 후보 5,034건:** `data/regions/nationwide_locality_candidates_5034.json`
- V5 원본: `feature/v52-wreath-region:sites/wreath-region/regions.json`
- 원본과 신규 파일 모두 Git blob SHA **`525eb4b5c9f9f046ce2bcbd96a3dcfb343be399d`**. 텍스트 재구성이 아닌 **동일 Git blob을 새 경로에 연결**했으므로 바이트·순서·표현이 같다.
- V5 Wreath 원본 출처 기록: `Guk0/KoreanAddressJson/address2.json`, upstream blob SHA `4abcacdac79d20ca84bd232ab1f0a346c3aecf69`; 원본의 정확한 최종 업데이트 시점은 미확인(원장에는 2025 source라고 기록).
- 데이터 구조: `records`의 각 행 `[시도 이름, 시군구 이름, 지역명, V4 상위 지역명 매칭 플래그(0/1)]`.
- 원본에 기록된 건수는 시도명 **17종**, 시군구 조합 **250종**, 지역명 전체 조합 **5,034건**이다. 전체 `(시도, 시군구, 지역명)` 조합은 중복 없음. 상위 명칭 플래그 **1=3,596건**, **0=1,438건**.
- **0인 1,438건도 모두 사용**한다. 플래그는 V4 코드 원장과의 상위 이름 대조 여부이지 해당 지역명이 존재하지 않는다거나 배송을 할 수 없다는 뜻이 아니다.
- 최신 법정동·행정동 여부, 개별 지역의 상세 관할, 꽃집 영업·당일배송 가능 여부는 이 후보 원장만으로 확인되지 않는다. 웹페이지에 단정하여 쓰지 않는다.

## V4 공식 원장과 병렬 보존 (원본 덮어쓰기 금지)

- `data/regions/v4_official_parent_regions_20261022.json` — V4 `ops/v5-isolated-staging-20261024:data/regions/master.json` 원본 Git blob SHA **`13d43fc3f2492b29b1680858235fe0ac0cd10580`**. 법정동 코드 상위 레벨 284행(시도16·시군구229·일반구39); 데이터 기준 2026-10-22.
- `data/regions/v4_official_legal_codes_20261022.zip` — V5 기존 `site/flowershop-nalmada-initial:data/regions/flowershop_official_codes_20261022.zip`의 **동일 Git blob** SHA `105e3084be32a116b7c3c8361edaacd0ea40b110`. 원본 ZIP SHA256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`. V4 공식 `code.go.kr` 확보 자료(2026-10-22).
- 과거 Flowershop의 공식 코드 기반 추출은 **5,067 법정동명**으로 보고되어 있다. 이는 2025 지역명 후보 5,034건과 **서로 다른 목록**이며 동일 레코드의 검증 결과로 대체하지 않는다.
- V5 기존 `data/regions/seoul_gyeonggi_current_dong.json` **1,732 서울·경기 후보**도 별도 체계다. 전국 5,034명단에 합치거나 삭제하지 않는다.

## Clinic 3개 사이트 생성 연결

- `clinicflower.nalmada.net`, `clinicopen.nalmada.net`, `clinicpresent.nalmada.net`: 원본 후보 5,034건 **각각 모두 포함**.
- `python -m v5.region_candidates --input data/regions/nationwide_locality_candidates_5034.json --output reports/clinic-region-selection.json --expected-count 5034`
- `python -m unittest tests.test_region_candidates -v`
- 안정적인 원장 순번 및 전체 원본 명칭을 `/r/00001.html`부터 `/r/05034.html`까지 사용. 동일 지역명 부분(예: '교동')이 다수 있어도 세 부분 이름과 순번으로 구분하고 상위코드 0도 절대 제외하지 않는다.
- 원장에 기록된 상위 이름은 그대로 표현할 수 있지만 **현재 행정구역 일치 확인**을 의미하지 않는다. 소스의 부모 코드가 없는 경우 새 공식 코드를 만들어 넣지 않는다.
- 계획: 각 사이트 지역명 상세 5,034 + 시도 탐색 17 + 시군구 탐색 250 + 홈 1 = 5,302개, 3개 합계 15,906개. 이는 단지 **생성 계획**이고 아직 실제 15,906 HTML이 생성·검수·배포된 것은 아니다.
- 기존 공유 Worker `sfv5-nalmada-domain`, 다른 서브도메인의 별도 운영 Worker와 DNS는 보존. 검색 공개 승인 전에는 noindex.
- 고정 1% 표본을 전체 후보 페이지와 5-gram Jaccard 비교해 49% 미만 내부 게이트를 확인하되, 수치만으로 검색엔진이 유사/도어웨이 페이지로 판단하지 않는다는 보장은 없다.

## 검증 출처
- `https://github.com/joseungil-kr/site-factory-v5/blob/feature/v52-wreath-region/sites/wreath-region/regions.json`
- `https://github.com/joseungil-kr/site-factory-v4/blob/ops/v5-isolated-staging-20261024/data/regions/master.json`
- `https://github.com/joseungil-kr/site-factory-v5/blob/site/flowershop-nalmada-initial/data/regions/flowershop_official_codes_20261022.zip`
