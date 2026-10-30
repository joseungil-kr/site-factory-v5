> **과거 대표 3페이지 시점 기록**입니다. 최신 1448×1086 이미지 및 33페이지 확장 결과는 [현재 README](README.md), [이미지 검수](IMAGE_REPLACEMENT_REVIEW_20261030.md)를 우선하세요. 아래 96×141 서술은 당시의 과거 화면만 가리킵니다.

# 오늘꽃배달 대표 3페이지 인수·검수 보고 — 2026-10-30

## 판정
**대표 시·구·동 3페이지 / noindex 임시 공개 / HTTP·자동 화면검수 PASS.**
정식 `todayflower.nalmada.net` DNS 연결·index·검색 등록·전국 확장은 수행하지 않음.

## 저장 소스
- V5 브랜치: `site/todayflower-nalmada-pilot-20261030`
- 검증 소스 커밋: `f6f71a763bdf68ab8ee5b49db355e95e492a5d93`
- 메인 디렉터리: `sites/todayflower-nalmada/`
- 전용 마크업: `v5/todayflower_markup.py` (V5 정적 엔진 재사용)
- 테스트: `tests/test_todayflower_pilot.py`
- 이미지: `assets/library/todayflower/`의 WebP 10개 (새 이미지 5개 + 재사용 고해상도 5개)
- 대표 문서: `/`=안산시, `/2.html`=안산시 단원구, `/3.html`=단원구 고잔동

## 원본 상품 및 표시 금액
2026-10-30 판매처 페이지 확인 기록. 오늘의 재고, 마감, 배송 가능 여부의 약속 아님.

| SKU | 상품 | 표시 가격 | 원본 |
|---|---|---:|---|
| G067 | 가을산책 꽃다발 | 60,000원 | https://fwith.co.kr/shop/item.php?it_id=G067 |
| G073 | 시크릿가든 꽃다발 | 66,000원 | https://fwith.co.kr/shop/item.php?it_id=G073 |
| D144 | 금전수 탁상용 | 53,000원 | https://fwith.co.kr/shop/item.php?it_id=D144 |
| D149 | 녹보수 소형 | 65,000원 | https://fwith.co.kr/shop/item.php?it_id=D149 |
| C200 | 축하 3단 화환 | 59,000원 | https://fwith.co.kr/shop/item.php?it_id=C200 |
| C206 | 축하 4단 화환 | 120,000원 | https://fwith.co.kr/shop/item.php?it_id=C206 |
| B201 | 근조 3단 화환 | 59,000원 | https://fwith.co.kr/shop/item.php?it_id=B201 |
| B205 | 근조 특대 3단 화환 | 109,000원 | https://fwith.co.kr/shop/item.php?it_id=B205 |

모든 가격은 주문 단계에서 재확인. **당일배송 무조건 가능·마감시각·배송비 고정·재고 확인**을 주장하지 않음.

## 검증 증거
- V5 GitHub Actions: https://github.com/joseungil-kr/site-factory-v5/actions/runs/41006700365
- 아티팩트 `12955163898`; SHA-256 `2ba0b180c4ca245b18437a4059b7739a159a9ca5825b6d57aeb394fb1790d7bf`
- `python -m v5 plan-check`, 신규 5개 단위검사, 엔진 빌드, `python -m v5 audit` 성공
- HTML 4개(대표3+404), 정적 파일20개, 내부 참조140개, 오류0·경고0
- 3개 본문 3쌍의 문자 5-gram Jaccard 최대 0.02884. 이 값은 전국 품질 검증 아님.
- Playwright Chromium 390px/1440px × 3페이지 = 6개 전 화면. H1 1개, 내부 WebP 7개/페이지, 그 중 신규 ImageGen WebP 5개, 가로 넘침 없음.
- 같은 브라우저에서 판매처 상품 이미지 디코딩 성공: 홈 8/8, 단원구 7/7, 고잔동 6/6 (각 화면 크기에서 동일)
- 실제 390px/1440px 화면 확인: 모바일 이미지 카드 캡션 줄바꿈 문제와 카테고리 불일치 이미지 수정 후 치명적 레이아웃 문제 발견되지 않음
- ImageGen 새 WebP 5종: 꽃다발 선물, 개업화분, 축하화환, 근조화환, 꽃 포장. 전용 작은 카드 크기 96×141; **판매처 상품 실사진이나 납품 증빙으로 표기하지 않음**.

## 격리된 공개 미리보기
- 배포 담당: V4 ops Workflow `.github/workflows/todayflower-isolated-preview-deploy.yml`
- V4 ops 워크플로 저장 커밋: `3fec819d0d8b19e1e15a66110f1e41a5d33fb39d`
- 실제 실행: https://github.com/joseungil-kr/site-factory-v4/actions/runs/41007069477
- 작업 소스: 고정 V5 SHA + 아티팩트, **새 페이지 생성 없음**
- Worker: `sfv56-todayflower-preview`
- 배포 시점 버전: `768f6f2f-abd8-4e3a-a0a7-e933b20e1df4`
- URL: https://sfv56-todayflower-preview.joseungil.workers.dev
- 실서버 GET 9건: 루트/2/3/이미지 WebP/robots.txt/없는 경로/사이트맵 (200·404 기대값, HTTP `X-Robots-Tag: noindex`) 통과.
- 검수 영수증 아티팩트 `12955547938`. 새 Cloudflare Secret·권한·DNS·custom-domain 바인딩·IndexNow 없음.
- Cloudflare API 사전검사 당시 새 Worker 이름 부재와 후보 `todayflower.nalmada.net` 미바인딩 확인 (배포 전 read-only). 추후 연결 시 다시 충돌 확인.

## 독립적인 남은 작업
1. 부모가 공개 미리보기의 실제 화면과 3페이지 문구/가격/배송 안내를 승인할 것.
2. 넓은 지역 원장/행정동 비교, 지역별 실제 배송 범위, 문서별 차별성을 검증하고 전국 확장 수량 결정할 것.
3. 후보 도메인 연결·서치콘솔 소유확인·index/canonical/sitemap/IndexNow는 별도 실행 계획과 승인 후 진행할 것.
4. 검색 노출, 수요, 지역별 전환 및 수익은 아직 측정되지 않음.
