# 알뜰화환 — 지역 화환 가격 비교 (V5 작업자2 독립 프로젝트)

상태: **대표 시안 3페이지 / 로컬 HTTP 검증. 운영·Cloudflare 배포 없음.** 도메인 후보: `wreathprice.nalmada.net` (DNS/충돌 사전 확인 전 연결 금지).

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

다섯 장 모두 ImageGen 생성 사진형 예시를 1024px 폭 WebP로 잘라 압축한 **동일 공용 풀**. 상품 실사진·납품/배송 실적 아님. 시안 제작물은 별도 ZIP으로 인계하며, **GitHub 바이너리 업로드는 미완료**이므로 배포하지 않는다.

## 검증·대기
- 로컬 Python HTTP 시안 3 HTML + 이미지 5 + robots 200; HTML 페이지당 `img` 5개/파일 존재/alt/width/height/noindex 검사 통과.
- Chromium 실행파일 부재로 실제 시각 브라우저 QA 미완료. `workers.dev` URL 없음. 도메인 충돌 검사 미실행.
- 다음 단계: GitHub 실이미지 저장 → V5 고정 소스 빌드 → 샘플 QA → 별도 noindex Worker/도메인 충돌 read-only → 부모 검수.
- 기존 Wreath 네이버 인증 후속 상황과 IndexNow 10,336 URL HTTP200 접수는 별도 작업으로 보존하고 이번 프로젝트에서 변경하지 않음.

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
