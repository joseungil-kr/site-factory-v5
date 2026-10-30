# 오늘꽃배달 — 2026-10-30 근거 및 개발 결정

## 운영 경계
- 원본 운영: https://fwith.co.kr
- 신규 도메인 **후보**: https://todayflower.nalmada.net (DNS/Worker/소유확인 미변경)
- 별도 브랜치 `site/todayflower-nalmada-pilot-20261030`; Flowershop·Signsky·V4 운영본 변경 금지
- 승인·검수된 1차 납품은 안산시(/), 단원구(/2.html), 고잔동(/3.html) 3개 대표 페이지이며 변경 금지. 2026-10-30 후속 범위는 안산시 상록구와 공식 법정동 29개를 추가해 총33개 noindex 문서
- 검색 차단: `preview` robots Disallow, meta noindex, canonical/sitemap 없음. IndexNow 꺼짐.

## 근거
1. 시·구 공식 코드: V4 `data/regions/master.json`, 2026-10-22 스냅샷. 안산시 4127000000, 단원구 4127300000.
2. 동: V5 `data/regions/seoul_gyeonggi_current_dong.json`의 `경기도 안산시 단원구` + `고잔동`. 2026-10-12 스냅샷. 해당 동의 **행정동 최신 코드 검증을 의미하지 않음**.
3. 실제 판매처 직접 확인: https://fwith.co.kr/shop/item.php?it_id=G067 (60,000원), G073 (66,000원), D144 (53,000원), D149 (65,000원), C200 (59,000원), C206 (120,000원), B201 (59,000원), B205 (109,000원). 2026-10-30 판매처의 품명·가격·바로구매 UI 확인. 당시 가격과 현재성은 구분.
4. 실제 사진 출처: V4 `reference/legacy-data/product-sources.json`에 G067·G073 등 판매처 원본 thumbnail URL 기록. 기타 6종은 V4/V5 원장의 판매처 이미지 URL 기록. 이 URL의 현재 이미지 응답·핫링크 가능 여부는 별도 실HTTP 검수 필요.
5. 배송비 특이사항: [G067 판매처 상품안내](https://fwith.co.kr/shop/item.php?it_id=G067)에 안산시 단원구 **대부남동·대부동동·대부북동 30,000원 추가 배송비** 표기. 다른 주소나 모든 SKU의 자동 적용을 확정하지 않음.
6. 경쟁 검색 의도 사례: https://cflower.kr/flowerdelivery/delivery/ (당일 가능시간·상품·배송 변수 설명), https://flowerich.co.kr/shopinfo/guide.html (지역별 차등 조건). 문장/디자인 복사 금지.

## GitHub 선행 조사
- https://github.com/withastro/astro — MIT License(공식 README), TypeScript/Node, 2026-10-29 push 확인, 약 63.6k stars/3.9k forks. 새로운 Astro 의존성을 들이기보다 현재 Python V5 빌드 재사용.
- https://github.com/cloudflare/workers-sdk — Apache-2.0, TypeScript/Node, 2026-10-29 push 확인, 약 4.7k stars/1.6k forks. Cloudflare 배포 기반은 기존 성공한 V4 isolated workers.dev 경로 재사용.
- https://github.com/joseungil-kr/site-factory-v5 — Python 3.12 stdlib, 정적 HTML/검증/manifest/rollback. 신규 독립 사이트 원장과 렌더러만 추가하고 `v5.engine.build` 재사용.

## 사용자 화면/상품 정책
- 주제: 꽃다발/개업화분/축하화환/근조화환을 별도 섹션으로 분리
- 지역별 내용은 실제 주소 준비·수령·행사장·빈소가 주제이며 미검증 로컬 점포·후기·배송 마감 보장 없음
- 카드는 판매처 SKU/사진 URL/2026-10-30 표시가/개별 상품 직접 주문 버튼
- 화면의 5장 편집 이미지와 판매처 상품 사진을 구분하며, AI 이미지를 배송 실적처럼 말하지 않음
- 본문용 새 AI 생성 장면 5종: 꽃다발·개업화분·축하화환·근조화환·포장 장면. 고유 장면을 공용 이미지 풀로 재사용
- 2026-10-30 ImageGen 생성 기록을 가진 AI 연출 이미지 5종을 독립 1448×1086 WebP로 교체하고 로컬 원본 파일/원격 Git blob 해시를 검사했다. 부모가 생성 원본을 직접 열람하지 못했으므로 생성 과정은 기록된 메타데이터, WebP 원격 바이트·치수·모바일/PC 렌더링 검수는 독립 확인으로 구분한다. 데스크톱 3+2·모바일 1열, 실제 표시 332/330px이며 판매 상품 사진·납품 실적과 혼동 금지.

## 다음 게이트
`python -m v5 plan-check --site todayflower-nalmada`
`python -m unittest discover -s tests -p test_todayflower_pilot.py -v`
`python -m v5 build --site todayflower-nalmada --mode preview`
`python -m v5 audit --site todayflower-nalmada`
생성물에서 33 HTML+404, 5 편집 콘텐츠 이미지/페이지, 상품카드·링크/가격, HTML noindex·robots Disallow, 모바일 390/PC 1440 실화면 검수. 그 후 별도 noindex preview Worker와 부모 검수.
