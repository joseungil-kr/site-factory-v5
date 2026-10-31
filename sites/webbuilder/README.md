# Webbuilder (작업자5) — 업종별 검색 홈페이지 제작 안내

- 후보 도메인: https://webbuilder.nalmada.net
- 브랜드 및 푸터: 사업자 인터피아드 / https://interpiad.com
- 전화: 010-2490-0555
- 현재 단계: GitHub 원격 소스 저장 → 오프라인 noindex 빌드·QA. **운영 배포, 도메인 연결, 색인, IndexNow 미실행.**
- **작업자5의 제작 대상은 홈페이지 제작 서비스를 홍보하는 B2B 광고 사이트**다. 실제 고객의 웹사이트를 제작·배포하거나 업종 도메인 자동 구매/배정 시스템을 지금 구축하는 업무가 아니다. 누수·청소·운송 사업주에게 제작 상품을 설명하고 전화 상담으로 전환한다.
- 고객이 보게 될 도메인 혜택 문구: **"업종별 맞춤 도메인을 확보하고 관리해 드립니다. 고객 전용 홈페이지 주소와 서버비까지 포함됩니다."**
- `*.leak119.net`, `*.skycar24hr.com`, `leak119.nalmada.net` 등 후보 주소·미구매 상태와 DNS/Route/Worker 세부 사항은 내부 원장에만 남기며 방문자용 HTML에 노출하지 않는다. 다른 지역 업체를 실제 서비스 제공자인 것처럼 가장하지 않는다.

## 실제 데이터

| 파일 | 내용 |
| --- | --- |
| site-spec.json | V5 기획 원장: 월 1,000원/페이지, 최소 10페이지, 다중 업종 도메인 모델 |
| domain-policy.json | 고객별 서브도메인 배정, 업종별 도메인 후보·검증·라우팅 정책 |
| keyword-pool.json | 38개 업종, 10개 홈페이지 제작 의뢰 템플릿, 업종별 3개 소비자 검색 키워드 구조. 총 494개 후보 |
| copy-pool.json | 업종별 고유 문구 50개와 공통 변주·FAQ·CTA를 포함한 원본 문구/문단 128개 |
| industry-expansion-a.json, industry-expansion-b.json | 새 28개 업종의 독립 설명 본문 140개와 업체 상담 체크리스트 |
| illustrations/*.svg + provenance.json | 생성 기반 WebP 일러스트 5개, 출처·사용정책 기록 |
| site.css | 독립 반응형 웹 디자인, 외부 폰트·CDN·추적 호출 없음 |
| worker.preview.js | 200/404 응답 모두 noindex 헤더를 강제하는 격리형 Worker |
| wrangler.preview.json | 기존 Worker와 분리된 sfv55-webbuilder-preview 설정 |

키워드 494개는 **실제 검색량, 노출 순위, 성과를 검증한 숫자가 아니라 조사 후보 수**이다.
buyer 키워드는 webbuilder.nalmada.net 자체의 제작 의뢰 유치용이다.
customer_example은 장차 실제 고객사의 서비스 가능 지역·작업 범위 검증을 마친 후 사용할 수 있는 고객사 SEO 예시이며, 웹빌더 자체 URL 타깃으로 사용하지 않는다.

## 페이지 구성 / 생성과 QA

정적 콘텐츠 42페이지: 홈 1, 기존 업종 10 보존 + 신규 업종 28, 비용·제작절차·FAQ 3. 별도의 404 파일을 포함한다.

- /
- /industry/leak/
- /industry/drain/
- /industry/moving/
- /industry/small-freight/
- /industry/mobile-carwash/
- /industry/washer-clean/
- /industry/dryer-clean/
- /industry/vacant-clean/
- /industry/office-clean/
- /industry/dawn-carwash/
- /guide/pricing/, /guide/process/, /guide/faq/

명령(저장소 루트에서 실행):

~~~sh
python -m v5 plan-check --site webbuilder
python -m unittest discover -s tests -p test_webbuilder.py -v
node --test tests/webbuilder-worker.test.mjs
python -m scripts.build_webbuilder
python -m v5.visitor_copy dist/webbuilder
python -m http.server 8000 --directory dist/webbuilder
~~~

- 생성 HTML/CSS/robots는 dist/webbuilder.
- 검수 요약은 reports/webbuilder/qa.json.
- 494개 후보 CSV는 reports/webbuilder/keyword-candidates.csv (UTF-8 BOM).
- 38개 업종 독립 설명 본문의 문자 5-gram Jaccard를 모든 703쌍 비교하며 최대치는 0.49 미만이어야 한다.
- 제목 14개 고유성, 내부 링크, 사업자 푸터·전화, noindex, sitemap 미생성을 검증한다.
- GitHub Actions webbuilder-preview.yml는 미리보기와 검수 결과를 일시 보관하며 Cloudflare 배포 작업을 포함하지 않는다.

## 확정된 상품과 업종별 맞춤 도메인 운영 정책

- **최소 계약 10페이지** × 페이지당 월 **1,000원** = **월 10,000원부터**.
- 월 이용료에 기본 홈페이지 제작·운영사가 확보/구매하는 업종별 상위 도메인 사용·고객 전용 서브도메인 배정·서버 호스팅을 포함한다.
- 고객이 최상위 도메인을 직접 구입·소유하는 형태가 아님. 인터피아드가 다수의 업종별 도메인을 확보하고 고객별 서브도메인을 발급한다.
- `nalmada.net`은 가능한 하나의 상위 도메인일 뿐이며, **업종 도메인을 nalmada.net으로 제한하지 않는다**.
- 시 전체 동을 무조건 20~30페이지로 발행한다고 보장하지 않는다. 관련성·실제 제공지역·독립적 소비자 효용을 우선한다.

| 페이지 | 월 이용료 |
| ---: | ---: |
| 10 | 10,000원 (최소) |
| 20 | 20,000원 |
| 30 | 30,000원 |
| 50 | 50,000원 |
| 100 | 100,000원 |

### 업종 맞춤 도메인 예시 (실제 구매·배정 검증 전)

| 업종/용도 | 주소 패턴 | 검증 상태 |
| --- | --- | --- |
| 공통·기존 운영 도메인 예시 | `leak119.nalmada.net` | 사용자 예시, 고객에게 배정된 주소 아님 |
| 누수·배관 | `*.leak119.net` | 새로 확보할 업종 도메인 후보, 구매 미검증 |
| 스카이차 | `*.skycar24hr.com` | 새로 확보할 업종 도메인 후보, 구매 미검증 |
| 다른 업종 | `{고객명}.{해당 업종별 운영사 도메인}` | 수요·상표·소유권·DNS 확인 후 확장 |

기존에 실소유한 상위 도메인과 향후 신규 구매하는 도메인을 구분하고, 구매·배정·HTTPS/SSL·검색 공개를 각각 검증한다. 구체적 후보 원장과 라우팅 제한은 `sites/webbuilder/domain-policy.json`을 참조한다.

Cloudflare 공식 문서상 Workers **Custom Domain은 wildcard hostname 등록을 지원하지 않는다**. 여러 업종·고객 서브도메인 공유 운영에서는, 이용 중인 Zone에 맞는 wildcard proxied DNS와 wildcard Worker Routes / 독립 바인딩을 구분하여 사용하고 운영 충돌·SSL·현재 활성 버전을 읽기 전용 확인해야 한다. DNS/Zone에 대한 실제 변경은 별도 승인 없이 진행하지 않는다.

### 미확정 조건 / 공개 차단
- 부가세 포함 여부, 계약 기간과 해지 처리
- 홈페이지 문서·원본의 소유 및 이전 조건
- 월별 수정/관리 횟수, 장애대응과 도메인 이용 중지 시 URL 처리
- 신규 업종별 도메인 구매 금액과 실제 확보 여부, Cloudflare Zone 및 Route/SSL 상태

`pricing.baseOfferConfirmed=true`이지만 `pricing.fullContractTermsConfirmed=false`; PR은 noindex 미리보기 전용이다. 계약이 확정되기 전 유료 청구나 운영 배포 금지.

동일 조건의 경쟁가격 조사가 없으므로 '전국 최저가'와 검색 순위 보장은 주장하지 않는다.

## 안전 격리 및 재사용

- V4, Daysky, Flowershop, Wreath, Hallflower, Winterbbang, Baekse 등 기존 사이트·Worker 수정 없음.
- DNS, 인증·권한, 비밀 키, 실제 배포, IndexNow 발행 없음.
- 전용 preview는 HTML meta noindex, robots Disallow, 사이트맵 없음, Worker X-Robots-Tag noindex를 사용한다.
- 문의폼 및 개인정보 수집 없음; 전화 CTA만 제공한다.
- 기존 V5 site_plan, visitor_copy, GitHub Actions 성공 패턴 일부 재사용. 외부 LLM API·추가 라이브러리·새 서비스 프레임워크를 사용하지 않는다.

## 조사 및 검증 출처 (2026-10-30)

- V5 AGENTS.md / SITE_CREATION_PROTOCOL.md / v5/ / 기존 CI.
- 네이버 콘텐츠: https://searchadvisor.naver.com/guide/content-basic
- 네이버 SEO: https://searchadvisor.naver.com/guide/report-seo
- Google 검색 스팸 정책: https://developers.google.com/search/docs/essentials/spam-policies?hl=ko
- Cloudflare Static Assets 요금과 제한: https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/
- Cloudflare wildcard DNS: https://developers.cloudflare.com/dns/manage-dns-records/reference/wildcard-dns-records/
- Cloudflare Custom Domain은 wildcard 불가: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- Cloudflare wildcard Route: https://developers.cloudflare.com/workers/configuration/routing/routes/
- GitHub 비교: MadhavShankar/pseo-engine (MIT, JS, Stars1, 최근 push 2026-08), m0ntydad0n/pseo-engine-oss (Apache-2.0, Python, Stars4, 최근 push 2026-07), esaHak/prSeoAstro (MIT, TypeScript, Stars0, 최근 push 2026-01). 해외 소규모 오픈소스는 운영성 검증이 부족하고 별도 프레임워크·서비스 의존성이 증가하므로, V5 일부 재사용을 선택했다.

## 2026-10-31 잔여 업종 페이지 제작 (작업자5)
- 이전 14개 콘텐츠 문서 및 10개 업종 원고를 보존하고, 업종별 새 콘텐츠 문서 28개를 추가해 **총 42개 콘텐츠 URL**을 오프라인 생성한다. 404 오류 페이지는 별도이다.
- 38개 업종은 설비·수리 / 운송·이사 / 차량관리 / 가전청소 / 공간청소 / 생활설치 / 현장장비 7개 분야로 분류한다.
- 이전 129개 원고/FAQ·일반 문구에 새 업종 독립 본문 140개를 추가했고, FAQ 및 상담 체크리스트는 별도로 취급한다.
- 이미지 파일은 **생성 래스터 WebP 일러스트 5개**이며 실제 시공·고객 운영 사진, AI 생성 실사 사진, 매출/순위 실적을 주장하는 이미지가 아니다. 허위 작업사진은 금지한다.
- Python 원장·이미지 무결성·업종당 고유 설명·실제 내부링크·42개 URL을 검증하고, PC1440/모바일390의 실제 Chromium 화면에서 SVG 로딩·전화 CTA·사업자 푸터·가로 넘침/404를 확인하도록 전용 QA를 추가했다.
- 이 변경은 기존 PR #26의 독립 preview 소스만 수정한다. Cloudflare 배포, 사용자 도메인 연결, Google/Naver 검색 공개 및 IndexNow는 **미실행**이다.

## 2026-10-31 이미지 생성 원본·래스터 교체 검수
- 기존 SVG 5개는 재사용하지 않고 소스에 비활성으로 보존하며, 사이트 빌드는 `illustrations/generated/*.webp`의 5개 이미지로 교체한다.
- 3건의 실제 OpenAI image_gen 원본 PNG(모두 1536×1024)를 출처로 사용했다. Webbuilder 메인 1개는 원본을 WebP로 변환했고 나머지 4개는 생성 장면을 편집·합성한 파생 이미지다. **5개를 독립적으로 생성했다고 주장하지 않는다.**
- 각 WebP의 실제 파일, Git Blob SHA, SHA-256, 가로·세로 치수, 생성 출처는 `illustrations/generated/provenance.json`에 기록.
- Canva 기존 1개 원본은 정상 다운로드되지 않아 재생성·썸네일 확대 없이 별도 기록을 보존한다.
- 본 변경은 `webbuilder.nalmada.net` 홍보 홈페이지 42페이지와 확정 월 요금을 보존하며 실제 운영 배포·DNS·검색등록은 진행하지 않는다.
