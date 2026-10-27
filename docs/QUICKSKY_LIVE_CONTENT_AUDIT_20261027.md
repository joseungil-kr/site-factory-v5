# 빠른스카이 공개 색인 전 독립 검수 — 2026-10-27 11:18 UTC

## 원격 증거와 범위
- 대상 운영 URL: https://quicksky.nalmada.net; Cloudflare Worker `sfv5-quicksky-preview`에 기존 빌드(과거 소스 708063a1) 연결 상태.
- 사용자 지원 통보: 11:15 UTC Ego Lite 기존 CF UI에서 DNS·Zone Routes 충돌 확인 후 연결. 기존 daysky/flower/plants는 그대로 유지. 지원 통보와 독립 HTTP 확인을 구분한다.
- 자체 읽기 전용 Actions: [40495177458](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40495177458), source `528a3103b44da2d727cb842b7f5af0c25f29ca36`, 성공.
- Actions는 Cloudflare API/Secrets를 호출하지 않으며, TLS 인증서 검증을 끄지 않고 표준 SSL 컨텍스트로 요청했다.

## 실제 운영 HTTP 검사
| Path | HTTP | 핵심 판정 |
| --- | ---: | --- |
| `/` | 200 | 빠른스카이/010-5322-1952, HTML noindex, X-Robots noindex, canonical 없음, 이전 .com 문자열 없음 |
| `/2.html` | 200 | 위와 같음 |
| `/1733.html` | 200 | 위와 같음 |
| `/1734.html` | 404 | X-Robots noindex |
| `/robots.txt` | 200 | `Disallow: /`, X-Robots noindex |
| `/sitemap.xml` | 404 | 색인용 사이트맵 없음 |
| `/assets/images/skycar-hero.webp` | 200 | 실제 RIFF/WEBP 파일, 110316 bytes |
| `/assets/images/skycar-facade.webp` | 200 | 실제 RIFF/WEBP 파일, 178742 bytes |
| `/assets/images/skycar-truck.webp` | 200 | 실제 RIFF/WEBP 파일, 81078 bytes |

결론: **현재 DNS·HTTPS로 접속 가능한 공개 URL(접근성 의미)은 확인**, **검색 공개·색인 허용은 여전히 차단**. sitemap/canonical 부재는 현재 noindex 릴리스에 부합한다. 전체 1,733 URL의 운영 GET 검사는 하지 않았으며, 위는 정확히 검증한 표본이다.

## 이미지 SHA/출처 검증
- GitHub V5 `assets/library/daysky` WebP 3개 실제 바이트 SHA-256과 `docs/DAYSKY_PHOTO_PROVENANCE.json`의 output_sha256이 전부 일치. 출처 매핑 역시 코드 원장과 일치.
- 원본으로 기록된 파일 **2개**: `https://skycar1day.com/images/yjsky_01.jpg`, `https://skycar1day.com/images/yjsky_02.jpg`. WebP 3개는 그 크롭 변형이며 독립 사진 3개가 아니다.
- 연결된 `joseungil-kr/yungjin-skycar` 저장소의 `hugo.toml`에 `www.skycar1day.com`이 운영 URL로 기재되고, `data/company.yaml`과 홈페이지에 같은 전화 `010-5322-1952`와 스카이차 1톤/3.5톤/5톤이 안내된다. 이는 소스/사업 관계의 **간접 근거**이지, 원본 사진 저작권·초상권·차량 사진이 빠른스카이의 실제 보유 장비인지에 대한 독립 증거가 아니다.
- 실제 촬영자·사진 이용권·상표/차량번호판·인물/작업 현장 오인 여부 확인 자료는 없다. 브라우저의 이미지 화면을 사람이 직접 육안 판독한 증거도 없다. **이미지 승인 미완료**.

## 12주제 × 서울/경기 고정 표본 검수
- read-only run에서 12개 work topics(광고물, 세척, 통신, 외벽점검, 부착/철거, 유리/창호, 조명, 유지관리, 도장, 간판, 환기, 방수)를 확인하고 각 서울/경기 1개씩 총 **24개** 페이지의 구조/본문 생성값을 분석했다.
- 각 표본은 제목·지역명·작업 종류, 5개 섹션, 2,198~2,289자 규모의 일반적인 현장 진입/설치/안전/비용 상담 설명을 포함한다. 12주제의 존재와 기계적 구성은 검증했다.
- 생성기는 지역명과 주제에 따라 전역 POOL에서 문장을 해시로 선택한다. **특정 행정동에 대응하는 실제 작업기록, 접근 도로, 실제 시설, 가용 장비/배차, 현장 사진, 사용자 후기·가격표 등의 원장 링크는 없다.** `지역명+스카이차` 검색 의도에 대한 실질 지역 차별성을 24개 표본에서 확인하지 못했다.
- 과거 문자 5-gram 기준 통과는 실질적 원본성·차별성·SEO 가치를 입증하지 않는다. 1,733개 전량 색인 공개는 권장하지 않는다. 검증 가능한 서비스 가능 지역과 현장 자료를 모은 뒤 해당 지역부터 개별 공개하는 것이 합리적이다.
- 안전 안내 문구는 작업 전에 지면, 전선, 하중, 지상 통제, 장비 제원 확인을 권고하며 **특정 현장의 안전·출동 보장을 확정하지 않는 형태**다. 다만 현장 실제 안전성 검증과 법적 책임 면책의 증거는 아니다.
- 1톤/3.5톤/5톤과 전화번호는 사용자 제공 정보 및 같은 계정의 `yungjin-skycar` 공개 마케팅 원장에서도 확인되지만, 실제 보유·배차 계약·서울/경기 모든 동 출동 가능성은 별도 증빙이 없다.
- 기존 원본 사이트 일부 서술에는 `24시간`, `15년 무사고`, `20~30분` 등이 있으나 **빠른스카이에서 검증된 주장으로 전재하지 않는다**.

## 이번 추가 소스 품질 수정
- `v5/service_markup.py`의 가격 미검증 Quicksky(`pricingPolicy=consult-only`)에서만 '작업 요금표 보기' / '기본 요금' 대신 '비용 상담 안내' / '비용 상담'을 표시하도록 수정. 가격표가 없는 섹션을 가격표로 소개하는 UX 불일치를 방지.
- 검증 테스트 추가, `Quicksky isolated site preflight` 및 `V5 offline build and audit`의 완료 결과 확인 [run 목록](https://github.com/joseungil-kr/site-factory-v5/actions).
- 소스 변경 SHA `61f2c739bac2ee3c194b56683d10ade51e25627d`, 테스트 SHA `ae1b58737e194e9e0fb4e05766f28dd474b4292a`. **운영 Worker 미재배포**이므로 이 레이블 변경이 현재 사이트에 보인다고 주장하지 않는다.

## 남은 차단 조건과 책임 구분
1. 사진 2개에 대한 실제 촬영자·권리 소유·빠른스카이 브랜드 사용 허가 확인. 확인 불가능하면 실제 색인용 공개 빌드에서 해당 사진을 제거한 후 재검수.
2. 1·3.5·5톤 실제 장비 제원/보유 또는 제휴 배차 근거, `010-5322-1952` 연결되는 운영 주체와 서울·경기 실제 서비스·예약 가능 범위 확인.
3. 12주제별 고객이 얻는 실질 정보와 지역별 차별 근거를 조사하여 출처와 함께 페이지/원장에 반영하거나 검증 불가능한 1,732개 지역 페이지는 색인에서 제외할 전략 수립.
4. 사진·품질 독립 검증 후에만 indexable build 구성 검토. 현재 `imageAssetsApproved=false`, `publicIndexingApproved=false`, `publishEnabled=false`, `indexNow.enabled=false`, `indexNow.key=null` 유지. 승인을 통과용 플래그 조작으로 대체 금지.
5. 검색 공개 릴리스 후에는 실제 운영 `index,follow`, canonical, robots Allow, sitemap 1,733 URL, missing 404, 이미지를 별도로 HTTP 검사해야 한다.
6. IndexNow는 유효한 기존 키 파일 HTTP 200과 키 내용 일치를 먼저 검증하고 정식 응답 영수증을 기록할 것. 현재 key=null, 전송·영수증 없음. Google/Naver 등록은 별도 담당자가 수행하며 중복 제출 금지.

## 실행 제한
- 기존 Production Worker, Cloudflare DNS/Route/토큰/권한 변경을 일절 수행하지 않았음.
- 이전 성공 V4 Preview workflow는 이미 custom domain-bound Worker에 대한 거부 게이트가 있으므로 재실행하지 않았음.
- 기술 검수 완료는 '색인 준비 완료' 또는 '사업 실체 검증'과 다르다.
