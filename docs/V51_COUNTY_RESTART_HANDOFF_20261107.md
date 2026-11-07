# V5.1 전국 군 근조화환 신규 비공개 시험사이트 — 2026-11-07 복구·검수 인계

## 대상/격리
- Site ID: `county-funeral-ownerprivate-test`
- 작업 브랜치: `site/v51-county-funeral-ownerprivate-20261107`
- 기준 main: `8ca5de9ce0dcdb769bdc855afee26392999c654d`; 해당 main은 변경/배포하지 않음.
- 신규 입력 스크립트: `scripts/build_county_funeral_trial_inputs.py`, 공통 목적 풀 `scripts/county_copy_pools.py`, 오프라인 렌더 `scripts/build_county_trial_review_only.py`.
- 공통 V5.1 모듈: `v5/purpose_render.py`(기존 선택/주문 외 모든 slot 보존, 허용 변수 `region/county/province/parentRegion`, 전체 breadcrumb), `v5/audit.py`(char-5gram Jaccard strict 49%).
- Github 비교: 기준 main으로부터 해당 브랜치는 별도 작업/테스트/문구/자체 SVG만 추가·수정, 기존 사이트 폴더나 main/기존 운영 Worker는 덮어쓰지 않음.
- **중요:** public GitHub repository의 branch와 artifact는 인증된 소유자 전용 홈페이지가 아니다. 실제 외부 URL은 발행하지 않았다.

## 시스템 오류와 재개
- 대화 UI의 `systemError` 내부 원인은 이 대화 기록에 정확한 시스템 로그가 없어 **확인 불가**. GitHub 빌드 오류와 별개.
- 재개 확인 HEAD `17b123dd5516bc3c83ce78a4c633f9d02df79342`, Actions 20건 내 진행 중 작업 없음.
- 이전 CI [run 42359779127](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42359779127) 실패: Body similarity **61.1494%**, 문서 42/94.
- 95개 범위·18개 실제 목적 적용 후 잠시 **49.5327%**, 문서8/13으로 실패. 광역 12개에 원장 내 실제 군 목록과 서로 다른 상품선택 절차를 추가.
- 이후 전체 95문서×4,465쌍 char-5gram Jaccard **46.0550%**(문서 35/89)까지 감소: 49% 미만 기준 유지, 임계값 완화·검사 제외 없음.
- 오프라인 검수기의 과거 99개 가정과 상품 4개 고정 가정을 실제 95문서·목적별 SKU 2–4개로 수정. 검증된 V5.1 변수·breadcrumb·section 보존 회귀는 되돌리지 않음.

## 최신 행정/상품 증거
- 2026-10-22 스냅샷에서 현존 군 82개와 이를 포함하는 광역 12개가 확인됨. 서울·대전·세종·제주는 하위 군 0이므로 허위 광역군 페이지를 만들지 않음.
- [2026-11-07 10:01 UTC 공식 재다운로드 run 42362139861](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42362139861): 공식 `https://www.code.go.kr/etc/codeFullDown.do` ZIP HTTP200, SHA256 `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`, 기존 고정 ZIP과 완전 동일, 현존 군 82코드/명칭 추가·삭제·변경 0.
- 군별 페이지와 실제 출력 경로는 `county-plan-evidence.json`과 `reports/county-funeral-ownerprivate-test/manifest.json` 대조: 전국1 + 군이 있는 광역12 + 군82 = **95페이지**, `/`, `/2.html`…`/95.html`. 군별 고유 코드 82개.
- [실제 판매처 readback run 42361620276](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42361620276): `https://fwith.co.kr/shop/item.php?it_id=B201` 및 B202/B205/B206에 대해 2026-11-07 09:53 UTC HTTP200, SKU·표시가격 각각 59,000/59,000/109,000/149,000원, 배송비 결제 "주문시 결제" 문구 확인. 상품 실사진/실재고/판매후 고객사례/최종 결제값은 별도 입증 안 됨.
- B201 페이지의 군별 배송료 표에서 읍·면 예외 및 SKU 간 적용 차이가 미확인이므로 군 전체의 고정 배송총액은 출력하지 않음.
- 상품 이미지 사용권 미확인 → 외부 판매자 사진을 복사하지 않고 `assets/library/county-funeral-ownerprivate-test/county-wreath.svg` 자체 제작 도형만 사용. 4개 실제 판매처 상품 주문 URL 보존.

## 페이지 생성·기술 QA
- [run 42361880642](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42361880642) 전체 95 HTML 빌드/평가 통과, 최대 Jaccard **46.0550%**, 기준 49%.
- [run 42361880687](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42361880687) 오프라인 렌더 95개, 홈에서 95개 전부 도달, **고아 0/끊긴 링크 0**, robots 전면 Disallow, 95개 모두 noindex, canonical 없음, 공개 sitemap·RSS·IndexNow 없음.
- [run 42362282710](https://github.com/joseungil-kr/site-factory-v5/actions/runs/42362282710): V5.1 회귀 **27개 PASS**, localhost 전용 Chromium 390/1440 PC·모바일에서 **26개 스크린샷**, 정확한 상품가·선택 SKU 및 82개 상품 링크 요소·breadcrumb·가로 넘침 확인 통과. Artifact **13569868580**.
- 본 시험사이트는 `mode=preview`만 생성했으며 `mode=publish`, `public-indexing` 및 Cloudflare API 배포는 **실행하지 않음**. 공개용 URL·index sitemap·RSS 발행·검색 제출 없음.

## 콘텐츠 편집 검수
- [41개 원문·목적/지역별 100점 평가표](../docs/V51_COUNTY_41_SAMPLE_EDITORIAL_REVIEW_20261107.md).
- 표본 41개(전국1·군 포함 광역12·군28), 18개 구매 목적 모두 포함. 담당 AI가 실제 생성 문서/목적 풀 원문을 검토한 편집 점수 **91~93점, 평균 91.59, 90점 미달 0**. 단 이 점수는 인간 제3자 QA나 SEO 고유성의 증명은 아님.
- 고객용 문구의 "비용 확인 없이 무료라고 표시하지 않습니다", "일괄 무료배송·당일 배송 약속하지 않습니다", "임의로 기재하지 않습니다" 등을 판매처 상품 선택/수령 주소/옵션 비용 설명으로 바꿈. 광역 제목 "서울특별시 군"과 홈 "전국 전국" 방지.
- 상품 가격, 리본 문구, 받는 장례식장·빈소, 배송비·접수 가능 시간의 조건부 상담을 구분. 사실이 없는 군 지점·납품 후기·상품 치수·무료배송 약속 없음.
- 미해결: 군별 고유 배송정보/시설 반입 조건과 실제 상업적 상담 전환의 질은 아직 독립적으로 검증되지 않음.

## 실제 owner-private 배포 차단과 필요한 다음 승인
- `site-factory-v5` 저장소는 **public**이며, 생성 계획의 `site.domain`, `workerName`은 모두 null. 지금까지 확인한 V5 staging은 공개 workers.dev + noindex 방식이라 실제 비공개 접근제어로 사용할 수 없음.
- 특정 시험 호스트의 Cloudflare Access 앱·owner identity 허용 정책 및 기존 인증서/도메인 연결 중 이번 사이트에 사용할 수 있다고 검증된 경로가 없음.
- **따라서 실제 Cloudflare 시험 배포·비공개 검증 링크 없음.** 새로운 Access/인증·보안 정책 및 필요한 도메인 연결 범위를 승인·검증받기 전에는 Worker를 노출하지 않는다. 새 권한/Secret/DNS/결제 변경 요청을 임의 실행하지 않는다.
- 격리된 빌드·검수는 완료되어 본 범위를 넘는 승인 없이 독립 진행 가능한 소스 작업은 종료. 공개·IndexNow·검색등록은 별도 승인 사항.

## 범위 밖 변경 여부
기존 WreathPrice/Todayflower/SkyQuote/Webbuilder/타 사이트 생성·배포·DNS·Secret·권한 변경 없음. 오프라인 시험 입력은 새 사이트 ID에만 기록. GitHub 저장소 main은 기준 HEAD 그대로 두고 시험 브랜치에만 커밋함. 사용자의 로컬 PC 미커밋 변경은 현재 연결된 GitHub 원격만으로 직접 볼 수 없어 **미확인**, 로컬 파일을 수정하지 않음.
