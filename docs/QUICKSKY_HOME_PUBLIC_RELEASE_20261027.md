# 빠른스카이 홈페이지 1 URL 검색 공개 실제 완료증거 — 2026-10-27

## 릴리스 경계
- 운영 URL: **https://quicksky.nalmada.net/**
- 사이트: 빠른스카이, 스카이차 이용·비용 전화 상담 (`010-5322-1952`)
- 기존 Worker: `sfv5-quicksky-preview` / 기존 custom-domain mapping 재사용; DNS 변경 없음
- V5 실제 배포 코드 commit: `2596531618e876921ab1d9fae587a390a561cb5f`
- V4 배포 워크플로 commit: `36709fd4c75ce7f0655e711255d743b6723780db`
- **GitHub Actions run [40514268818](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40514268818) `completed:success`**.
- 이전 Worker version, 소유권·바인딩 목록 및 live check 기록: [run artifact 12738835925](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40514268818/artifacts/12738835925). 기존 custom-domain mapping 전체 **82개 전후 완전 동일**.

## 실제 외부 HTTPS / SEO 검사 (SSL 검증 우회 없음)
| URL 또는 항목 | HTTP | index 상태/검사 |
| --- | ---: | --- |
| https://quicksky.nalmada.net/ | 200 | HTML meta index,follow / X-Robots noindex 없음 / 자기 URL canonical 정확히 1건 |
| https://quicksky.nalmada.net/2.html | 200 | meta noindex / X-Robots noindex / canonical 없음 |
| https://quicksky.nalmada.net/1733.html | 200 | meta noindex / X-Robots noindex / canonical 없음 |
| https://quicksky.nalmada.net/1734.html | 404 | HTTP X-Robots noindex |
| https://quicksky.nalmada.net/robots.txt | 200 | `User-agent: *`, `Allow: /`, sitemap 지시문 |
| https://quicksky.nalmada.net/sitemap.xml | 200 | **URL 1개만**: https://quicksky.nalmada.net/ |
| https://quicksky.nalmada.net/assets/images/skycar-hero.webp | 200 | RIFF/WEBP 실제 자산 확인 |
| https://sfv5-quicksky-preview.joseungil.workers.dev/ | 200 | X-Robots HTTP noindex, 미리보기 robots Disallow |
| workers.dev /2.html, /1733.html, /1734.html | 200,200,404 | 모두 HTTP noindex |

동일 정적 홈페이지 HTML에는 자기 canonical이 있으므로 workers.dev에서도 **HTTP noindex + robots Disallow**로 검색을 차단함. 공유 assets 때문에 preview HTML meta 자체는 index,follow일 수 있으나 noindex HTTP response가 우선 적용된다.
전체 **1,732개 지역 HTML 파일의 meta noindex 및 canonical 부재는 빌드 단계 전수 검수**; 운영 HTTPS는 `/2.html`, `/1733.html` 표본 검수. Worker의 `V5_HOME_ONLY=1` 경로 분기는 지역 번호 URL에서 강제로 X-Robots noindex를 적용하며 Node 테스트에서 확인했다. 모든 1,732개 URL을 live GET했다고 단정하지 않는다.

## 출처/사업 사실 품질 게이트
- 사용자 지정 브랜드/지역·상담번호/요금 문의 정책/승인한 특정 사진 원본 2장+파생 WebP 3개에만 한정해 홈페이지 내용을 검수함.
- 출처 및 홈 품질 범위: [docs/QUICKSKY_HOME_FACTS_QUALITY_EVIDENCE_20261027.json](QUICKSKY_HOME_FACTS_QUALITY_EVIDENCE_20261027.json).
- 실제 장비 보유/협력 배차 사양·전 동 출동 보장·실제 지역 작업 실적·고정 금액은 홈페이지에서 확정하지 않음. 실제 상담 가능 장비·배차·출동 일정은 통화와 현장 정보로 조건부 확인.
- `homeIndexingScope=quicksky-home-1-20261027` 하나만 활성. `publishEnabled=false` 서비스 모델 유지, `publicIndexingApproved=false` 지역 대량 승인 금지, `homeIndexingApproved=true`는 검수된 홈만 허용.

## 공식 지역자료의 현재 검수와 한계
- 정부 종로구 법정동 이름·코드 8건 대조 성공, 2026년 7월 안양시 행정동 변경 이름 2건 대조 성공, 총 10건. 나머지 1,722개 지역은 공식 코드/행정동 구분 미확인.
- [1,732개 지역명 대조 CSV 및 요약 JSON](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40506816704/artifacts/12734459596).
- [국토교통부 전국 법정동 2026-06-30 CSV 공식 소개](https://www.data.go.kr/data/15063424/fileData.do) — 전체 원문 CSV를 별도 확보하여 검증하기 전까지 나머지 1,722개를 공식 일치로 간주하지 않음.
- **행정구역 이름·코드 일치 ≠ 빠른스카이 실제 출장/시공 능력의 증거.** 지역 페이지 1,732개는 계속 noindex.

## 검색 등록 인계 상태
- 기술적으로 크롤링 허용 가능한 정확한 URL **1개**: https://quicksky.nalmada.net/
- robots: https://quicksky.nalmada.net/robots.txt
- sitemap: https://quicksky.nalmada.net/sitemap.xml (홈 1개)
- **IndexNow는 미전송**: 기존 `indexNow.key=null`, 정상 공개 키가 확인되지 않아 키/영수증을 만들어내지 않음.
- **Google Search Console / 네이버 서치어드바이저 소유확인·사이트맵 제출은 부모 담당**. 중복 제출하거나 외부 OAuth 권한 확대를 하지 않음.
- 성공한 배포는 검색엔진 색인 완료를 뜻하지 않음. 등록 담당은 위 한 URL만 검사·제출하고 지역 페이지의 색인을 요청하지 않을 것.

## QA에서 확인한 복구 이력
- 첫 릴리스는 Python 실행 import 경로 오류로 **배포 전 중단**. 다음 시도는 preview 공유 HTML meta/canonical 판정 오류로 검증기 실패, 이전 Worker version rollback 명령 성공. 이후 독립 GET-only 확인에서 기존 Worker가 noindex로 복구됨.
- 마지막 성공 run 40514268818은 **전체 검증 통과**, 롤백 실행 없음.
- 기존 V4/Others Worker·DNS·도메인 매핑에 변경 없음.
