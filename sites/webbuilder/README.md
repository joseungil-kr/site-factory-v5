# Webbuilder (작업자5) — 업종별 검색 홈페이지 제작 안내

- 후보 도메인: https://webbuilder.nalmada.net
- 브랜드 및 푸터: 사업자 인터피아드 / https://interpiad.com
- 전화: 010-2490-0555
- 현재 단계: GitHub 원격 소스 저장 → 오프라인 noindex 빌드·QA. **운영 배포, 도메인 연결, 색인, IndexNow 미실행.**
- 핵심 목표: 지역 서비스업 사업주에게 업종별 홈페이지 제작을 설명하고 전화 상담을 유도하는 B2B 사이트. 지역 누수업체 등 실제 서비스 제공자를 가장하지 않음.

## 실제 데이터

| 파일 | 내용 |
| --- | --- |
| site-spec.json | V5 필수 기획·승인 게이트, 가격/도메인 검토 상태 |
| keyword-pool.json | 38개 업종, 10개 홈페이지 제작 의뢰 템플릿, 업종별 3개 소비자 검색 키워드 구조. 총 494개 후보 |
| copy-pool.json | 업종별 고유 문구 50개와 공통 변주·FAQ·CTA를 포함한 원본 문구/문단 128개 |
| site.css | 독립 반응형 웹 디자인, 외부 폰트·CDN·추적 호출 없음 |
| worker.preview.js | 200/404 응답 모두 noindex 헤더를 강제하는 격리형 Worker |
| wrangler.preview.json | 기존 Worker와 분리된 sfv55-webbuilder-preview 설정 |

키워드 494개는 **실제 검색량, 노출 순위, 성과를 검증한 숫자가 아니라 조사 후보 수**이다.
buyer 키워드는 webbuilder.nalmada.net 자체의 제작 의뢰 유치용이다.
customer_example은 장차 실제 고객사의 서비스 가능 지역·작업 범위 검증을 마친 후 사용할 수 있는 고객사 SEO 예시이며, 웹빌더 자체 URL 타깃으로 사용하지 않는다.

## 페이지 구성 / 생성과 QA

정적 콘텐츠 14페이지: 홈 1, 핵심 업종 10, 비용·제작절차·FAQ 3. 별도의 404 파일을 포함한다.

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
- 10개 업종 독립 설명 본문의 문자 5-gram Jaccard를 모든 45쌍 비교하며 최대치는 0.49 미만이어야 한다.
- 제목 14개 고유성, 내부 링크, 사업자 푸터·전화, noindex, sitemap 미생성을 검증한다.
- GitHub Actions webbuilder-preview.yml는 미리보기와 검수 결과를 일시 보관하며 Cloudflare 배포 작업을 포함하지 않는다.

## 가격 문구의 출고 차단

사용자 요청에 페이지당 1,000원, 도메인·서버 비용 포함, 시 전체 동 월 2~3만원이 있지만 다음 조건은 아직 명확하지 않다.

1. 1,000원이 월 구독요금인지 1회 제작비인지
2. 최소 제작 페이지 수 및 시 단위 지역의 실제 페이지 개수
3. 도메인 등록 및 매년 연장 비용, SSL, 호스팅 사용량과 비용 상한
4. VAT 포함 여부, 수정 횟수, 계약 기간·해지·도메인/소스 소유권

따라서 현재 preview 화면은 페이지당 1,000원부터라는 제안 단가와 20/30페이지 산술 합계만 보여주고, 월 결제 금액이나 시 전체 동을 같은 금액으로 확약하지 않는다. 과금 주기 및 비용 포함 범위가 확정되기 전에는 광고용 public 릴리스 금지다.

**전국 최저가**는 동일 범위의 경쟁업체 가격 비교 자료 없이는 사용하지 않는다. 검색 상위노출 보장도 하지 않는다. 도어웨이 및 유사 문서 대량생성을 금지하고 실제 사업 서비스 내용이 풍부한 문서만 고객사 홈페이지에 발행한다.

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
- GitHub 비교: MadhavShankar/pseo-engine (MIT, JS, Stars1, 최근 push 2026-08), m0ntydad0n/pseo-engine-oss (Apache-2.0, Python, Stars4, 최근 push 2026-07), esaHak/prSeoAstro (MIT, TypeScript, Stars0, 최근 push 2026-01). 해외 소규모 오픈소스는 운영성 검증이 부족하고 별도 프레임워크·서비스 의존성이 증가하므로, V5 일부 재사용을 선택했다.
