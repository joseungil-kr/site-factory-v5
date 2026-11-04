# Clinicflower — 꽃이랑 병원·치과·한의원 개원축하화분

**2026-11-04 샘플 릴리스 후보** (운영 미배포 / `noindex` 미리보기)

- 대상 도메인(계획): `clinicflower.nalmada.net` · 전화 상담 `tel:1844-0644`
- 전국 발행 계획: 5,034 상세후보 + 268 허브 = **5,302 HTML 최대 계획 수량**. 지역 후보 중 **1,438개는 상위 지역명 검증 전**이며 실제 검증·생성·발행을 마치지 않았다.
- 이 디렉터리에는 **안산시 통합 샘플 1페이지**만 있다. 병원/치과/한의원 업종별 별도 SEO URL을 만들지 않는다.
- `clinicflower-copy-pool-720.json`: 병원 100/치과 100/한의원 100/공통 실무 320/허브 40/FAQ 60, 실무 안내용 복합 문구. 고유 본문 720개(문자열 일치 기준), **49% 미만 유사도·색인 성공을 뜻하지 않음**.
- `index.html`: 사이트 본문. 샘플 `noindex,nofollow,noarchive`, 자기 canonical 없음, 지역 실제 배송 또는 상품 가격·당일 보장 주장 없음.
- `assets/images/*.webp`: 5개의 원본 생성 PNG를 실제 픽셀에서 WebP 변환. 상세 출처·해시는 `image-provenance.json`. 이 이미지들은 **연출 이미지**이며 실제 고객 배송/상품 촬영 증거가 아님.
- `assets/style.css`: 반응형 390px/1440px CSS, 모바일 하단 고정 전화 주문 링크.
- `reports/qa-browser.json`: 390px/1440px 렌더링, 전화 링크 8개, 5이미지 브라우저 로드, overflow 0, 샘플 FAQ, 로컬 HTTP 200 테스트 보고.

## 검수 및 사용

정적 HTML 빌드이며 별도 외부 JS 패키지·쿠키·폼·추적기 없음. 루트의 `index.html`을 로컬 브라우저로 열거나 디렉터리에서 HTTP 서버로 열 수 있다. 파일의 이미지 주소는 상대경로다. 별도 `clinicflower-preview-single.html`은 이미지 내장 단일 HTML로 사용자 검수용이다.

```sh
python create_clinicflower.py
python test_preview.py
```

**중요 배포 경계**

기존 V5 공유 Worker 코드는 재사용 후보이나, 2026-11-04 조회 기준 계정에 기존 Worker 105개가 있고, 도메인·바인딩이 모두 비어 있는 preview/test 후보는 확인되지 않았다. 2026-11-03 별도 검증 자료의 `sfv5-ansan-promotion-plant-preview` 또한 ASSETS 전체 복구 증거가 없어 임의 덮어쓰기가 불가하다. 실서비스 Worker·DNS·권한·계정 Secret에는 변경을 하지 않는다. 신규 공개 이미지의 실제 `generatedAt` 값은 생성 도구가 제공하지 않아 원본 provenance에 `null`로 기록한다. 출처 검증 게이트 미통과를 '통과'로 표기하지 않는다.

추후 배포 조건: 기존 Worker 전체 자산·버전 복구 검증 및 비사용 확인 → 해당 공유 패키지 합산 파일 수 검증 → noindex 공개 샘플 배포 및 HTTPS readback → 본발행 시 원장·품질·상품·이미지 출처 검수 후 승인된 범위만 공개 색인.