# 빠른스카이 색인 공개 품질 판정 — 2026-10-27

## 요약 결론
- **기술 품질:** 1,733개 정적 HTML 생성 및 원본성 검사는 고정표본 조건에서 통과. 12개 주제 조사·CTA·요금/지역원장 표기를 실제 수정했고 새 테스트 검증 완료.
- **사진 재사용권:** 사용자가 정확한 원본 두 장에 대해 `직접 받은 사진이다. 사용권 허락받음`이라고 답변. WebP 3개 SHA/크롭 매핑 및 실제 사진 시각검수 완료. 장비톤수별 사진 연결 제거; `imageAssetsApproved=true`는 지정 자료의 중립적 홍보 용도에 한해 기록.
- **도메인 통제:** 기존 CF UI에서 사용자가 승인한 빠른스카이 전용 Custom Domain `quicksky.nalmada.net` 결합, 독립 무인증 HTTP GET/TLS 검증 통과. 소스에 소유·연결 증거 기재.
- **색인 공개 적합성:** **보류**. `contentQualityApproved` 및 `publicIndexingApproved`를 임의로 true로 바꾸지 않음.

## 실제 소스·QA 증거
- 신규 지역 문서 1,732개 + 홈 1개, ID/연속 번호 1..1733 유지. 지역 원장은 `V4 NAME_CANDIDATES` 기반 법정동/행정동 혼합 가능. 정확히 검증되지 않은 행정동으로 단정하지 않음.
- 12개 작업 유형: banner(현수막·광고물), cleaning(세척), communication(통신·전기), facade(외벽 점검), facility(부착·철거), glass(유리·창호), lighting(조명), maintenance(설비 유지관리), paint(도장), signage(간판), vent(환기·실외기), waterproof(방수·보수).
- 각 주제에서 서울·경기 1개씩 24개 표본을 독립 생성·본문 검수. 모든 표본은 5개 본문 섹션과 현장 접근·안전 확인·상담 정보가 있고 약 2,198~2,289자. 전수 사람검수 아님.
- 조사 결함: `외벽 방수·보수을 계획한다면` 같은 표현을 `외벽 방수·보수 관련 작업을 계획한다면`으로 12주제 공통 수정, 테스트 통과.
- CTA 결함: 미검증 숫자 요금표가 없음에도 `작업 요금표 보기`라고 표시하던 문제를 `비용 상담 안내 보기`/`비용 상담 안내`로 수정. 1톤·3.5톤·5톤 장비 카드는 이미지 대응이 사실 검증되지 않았으므로 빠른스카이에서 카드별 사진 노출 제거.
- Daysky 본문/기존 금액표/CTA/사진은 변경하지 않았으며 회귀 테스트 통과.
- QA: [V5 run 40496436375](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40496436375) Python 82 tests, Node Worker 6, Quicksky·Daysky 분리 검사 통과; 1% 고정 유사도, Daysky 원장 간 표본 최대 0.048499. 수치는 char-5gram Jaccard, **SEO 품질 점수가 아님**.
- 정확한 사진 권리 및 육안검수: [QUICKSKY_PHOTO_PERMISSION_20261027.json](QUICKSKY_PHOTO_PERMISSION_20261027.json) · [QUICKSKY_IMAGE_VISUAL_QA_20261027.md](QUICKSKY_IMAGE_VISUAL_QA_20261027.md). 실제 파일 3개는 원본 2장의 파생 이미지.
- 라이브 read-only 검증: [40495177458](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40495177458), 홈·2·1733 HTTP 200, 잘못된 번호 404, X-Robots noindex, meta noindex, robots Disallow, sitemap 404, 사진 3개 200. 이 URL은 검색 허용 공개 아님.

## 실질 품질 보류 근거
1. 현재 문구 생성 방식은 각 지역명과 12개 일반 작업 주제를 조합하고 공통 문구 버킷을 섞는다. 개별 1,732 지역의 진입로, 실제 수요, 현장 제약, 출장 가용 여부를 증명하는 사실 원장이 없다.
2. 유저가 검색하는 `특정 동 + 스카이차`에 필요한 **실제 출장 범위/시점/가용 차량/장비 제원/해당 지역 상담 차이**가 지역별로 확인되지 않았다. 외부 서비스의 전화와 서울·경기 문의 사실은 확인되지만 실시간 모든 동 배차 보장의 근거가 아니다.
3. 현장 안내 자체는 과장 보장 없이 유용할 수 있으나, 같은 문의번호로 모이는 수천 개 이름만 바꾼 페이지는 지역 타깃 doorway 또는 가치 낮은 scaled content로 해석될 위험이 있다. 정책 위반이라고 단정할 근거는 없지만 대량 색인 전에 사용자 가치를 검증해야 한다.
4. 본문 길이, 문자 중복률, 독립 사진 사용권의 확보를 **대량 색인 품질 합격으로 대체하지 않는다**.
5. 기존 https://www.skycar1day.com/areas/ 에는 서울 서남권 당일 지원, 그 외 서울은 사전 예약 광역 출동 등 지역별 조건이 언급된다. 해당 설명은 사업자 운영 페이지의 주장일 뿐 현재 가용 차량/계약의 독립 증거가 아니므로 Quicksky의 1,732개 동을 모두 동일 조건으로 홍보하면 부정확할 수 있다.

## 공개 전 필요한 구체적인 데이터
- 지역/시군구 단위의 **운영 근거 원장**: 운영자가 배차 가능한 서비스 권역, 당일 가능/사전예약/상담 후 확정 구분, 거점·이동/접근 예외, 근거 확인일.
- 실제 문의 또는 작업기록 중 공개 가능한 비개인정보 자료: 업종·작업분야·장비 제원·현장 조건 및 실제 사진(지역명은 확인되는 경우에만 사용). 개인 정보는 비식별 처리.
- 검증 가능한 안전·요금 조건: 현장별 도로점용·정차 가능성은 확정하지 않고 사전확인 안내, 장비별 실제 제조사/모델 사양은 확보되는 경우만 노출.
- 향후 HTML에는 지역별로 *실제 확인 가능한 차별 정보*를 추가. 그러기 전에는 모든 1,733 URL의 `index,follow`를 일괄 적용하지 않는 편이 합리적. 번호와 ID는 유지하고 검색에 적합한 페이지부터 단계적으로 출시할 수 있도록 별도 기획 필요.

## 정책 근거
- Google Search Central [Spam Policies - Doorway abuse, Scaled content abuse](https://developers.google.com/search/docs/essentials/spam-policies): 지역/도메인별 유사 문서가 단순 유입 경로가 되거나 새 사용자 가치 없이 대량 생성되면 위험.
- Google Search Central [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): 원본 경험·심도·기존 결과 대비 가치·사실 출처를 평가해야 함.

## 현재 릴리스 상태 (엄격히 구분)
- `publishEnabled=false` 서비스 모델 유지.
- 지정 2개 원본의 이용허락 확인 후 `imageAssetsApproved=true` 설정·증거 연결. 신규 이미지 자동 승인 안 함.
- `domainOwnershipVerified=true`: UI 바인딩 및 HTTPS 서비스 확인에 한정한 증거 연결.
- **`contentQualityApproved`는 미지정/false, `publicIndexingApproved=false`, `indexNow.enabled=false`, `indexNow.key=null`**.
- 운영 Cloudflare Worker 미재배포. 현재 실 서비스는 이전 noindex 릴리스이며 수정된 문구/사진카드가 실제 반영됐다고 주장하지 않는다.
- Canonical/robots-Allow/sitemap(1733 URL)·IndexNow 영수증은 **검색 공개 모드에서 아직 미생성/미전송**. Google/Naver 소유 확인 및 사이트맵 등록은 별도 담당.

