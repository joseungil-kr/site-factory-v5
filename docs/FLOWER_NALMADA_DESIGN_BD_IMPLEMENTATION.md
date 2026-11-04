# 날마다꽃 B 메인 / D 장례식장 서브 디자인 — 실제 구현 기록

## 구현본
- 테스트 사이트: `https://sfv5-nalmada-flower-preview.joseungil.workers.dev/` (NOINDEX 검수용. GitHub 러너의 외부 접근은 403으로 검증 실패)
- 실제 빌드 대상: 전국 장례식장 1,080개, 시설별 HTML + 메인/index.html + 검색 JSON + 404.
- 해당 운영 도메인 `flower.nalmada.net`은 아직 연결하거나 배포하지 않음.
- 코드 확정 체크아웃 SHA: `2aa26a244830a4e84921445d0875e6838a68fb92`.
- 디자인: 메인 **B안(녹색·연분홍 프리미엄, 실제 꽃바구니 히어로 사진)**, 서브 **D안(검증 전 시설 사진은 제외하고 공통 근조화환 상품 사진·상품카드·긴 본문·FAQ·상담 CTA)**.
- 전국 지역+상품 **C안은 이후 별도 유형용**으로 예정; 현재 시설 페이지 1,080개를 C형으로 가장하지 않음.

## 실제 구현 자산
- 공통 스타일: `templates/flower-nalmada/site.css`
- 실제 레이아웃 모듈: `scripts/flower_design.py`
- 시설 콘텐츠 레이아웃: `scripts/build_flower_funeral_national.py`
- 메인·장례식장검색·404: `scripts/prepare_flower_funeral_preview.py`
- 실제 사진: `assets/library/flower-nalmada/{B201,B203,B205,A160,D143}.jpg`
  - 사용 출처: 소유자 운영 V4 저장소 `joseungil-kr/site-factory-v4`, 브랜치 `feature/funeralflower-mini`.
  - 근조 3개 상품과 판매처 링크·2026-10-22 기준 참고가는 `data/flower/nalmada_funeral_product_reference.json`에 원본 파일/가격 출처와 함께 고정.
  - **2026-10-22 확인 가격은 현행 확정가격이나 특정 시설 배송비를 보장하지 않음.** 운영 공개 시 재검증 필요.
  - 시설 건물 전경·가상 주소 지도·시설별 AI 사진은 사용하지 않음.
- 전국 장례식장 원문 1,080개 및 600+48 문구 POOL과 유사도 검사 코드/원본 배정은 변경하지 않았음.

## QA / 검증
- 전수 유사도(실본문+정규화): **1,165,320 비교, 최대 29.6346%, 49% 이상 0쌍**.
- [검수용 1080 HTML 생성 CI](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40368219604): SUCCESS.
- [실제 Chromium PC1440 + 모바일390 UI 검사](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40368219590): SUCCESS.
  - PC·모바일 메인 및 시설 상세 각각 스크린샷 업로드.
  - 메인 검색의 '안산' 검색 13개 결과, 전체 이미지는 PC/모바일 메인 각 7개 및 시설 상세 각 4개 정상 로드.
  - 수평 넘침 없음(1440/390 정확), 상품 3카드·본문 6섹션·시설명 H1 검증.
- [검수용 Cloudflare 배포](https://github.com/joseungil-kr/fwith-site-factory/actions/runs/40368463684): Worker 배포 성공.
  - Worker: `sfv5-nalmada-flower-preview`, 배포된 활성 버전 `42b3c80e-bb54-49b2-84c5-139011a18e86`.
  - Cloudflare API가 활성 100% 확인. GitHub 러너 외부 확인은 HTTP 403이므로 사용자 브라우저 실제 접속은 별도 확인 필요.
  - V4 운영 Worker, DNS, Custom Domain, `flower.nalmada.net` 운영본 변경 없음.

## 최종 승인 전 배포 제한
1. V4 원장의 `publicationAllowed=false`·시설 주소/운영 여부 미검증.
2. 전문 문구 원장의 `readyForPublication=false`·최종 내용 사실성 검수 미완료.
3. 참고 상품 가격·상품 재고·배송 조건·사진 이용 범위의 운영 전 재확인.
4. 사용자의 최종 디자인 확인 전 `flower.nalmada.net` 정식 공개 및 IndexNow 금지.


## 2026-10-27 — 방문자 임시안내 삭제 및 이미지 프레임 최종 검수

- V5 공통 규칙 `AGENTS.md`, `SITE_CREATION_PROTOCOL.md`, `v5/visitor_copy.py` 추가·병합: [PR #15](https://github.com/joseungil-kr/site-factory-v5/pull/15), main merge `d4f58c660655afc5f8359fe0fa70b98fc7588309`.
- 방문자 화면에서 '보유 상품 사진 · 실제 상품 구성은 달라질 수 있습니다', '검수용', '상품 정보 준비 중', '미검증', '원장 기재', '참고 가격' 등 노출 문구 제거. 시설별 주소는 최신 검증 전까지 숨김. 가격은 2026.10.22 판매처 등록가격이라는 시점이 분명한 상품 카드로 표현하고, 판매처 상세 링크를 유지.
- 본문/시설·상품 원장 자체의 승인·진위 정보는 GitHub JSON/QA 문서에 계속 보존. noindex/robots/IndexNow 금지는 유지.
- 공통 CSS에서 히어로·카테고리·상품 이미지 `object-fit:cover`, 카드 이미지 정사각형 전체채움 및 잘림 완화 적용. 원본 사진은 공용 자산 그대로 사용.
- 소스/검사 고정 커밋: `30c8f5a2507df1da3073e9c236c0ba697c39962b`.
- [1,080페이지 생성 + 방문자 임시 문구 전수검사](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40436216138): SUCCESS. 1,082 HTML(시설 1,080 + 홈 + 404)에서 금지 문구 **0건**, 유사도 전수 최대 **29.3863%**, 초과 0쌍.
- [PC 1440px + 모바일 390px 브라우저 스크린샷 QA](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40436216038): SUCCESS. 홈 이미지 7개, 상세 이미지 4개 정상 표시, 전부 cover/full-frame, 가로 넘침 0.
- [독립 Cloudflare noindex Worker 재배포](https://github.com/joseungil-kr/fwith-site-factory/actions/runs/40436346450): SUCCESS. Worker `sfv5-nalmada-flower-preview`, provider-readback 버전 `92ed9a9f-2179-44c4-a223-8ff7a51a506a`.
- 별도 GitHub 러너의 외부 HTTPS 검사에는 **HTTP 403**이 남아 있으므로, 배포 API 성공과 실제 방문자 접근성 성공을 혼동하지 않는다.
- Custom Domain `flower.nalmada.net` 및 DNS, 공개 색인과 IndexNow는 변경하지 않음.
