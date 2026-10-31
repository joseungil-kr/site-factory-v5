# Quicksky 홈페이지 한정 검색 공개 기능 / 공식 지역명 표본 매칭 — 2026-10-27

## 결론: 기능 구현 및 테스트 완료, 실제 공개는 **미실행**
- 정확한 대상: https://quicksky.nalmada.net, 기존 `sfv5-quicksky-preview` Worker와 커스텀 도메인 매핑 유지. 기존 noindex 실서비스 배포 `a2cb065d4e8c98d60e27daf2f37dae146ea26470` / [V4 run 40498377315](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40498377315)에서 검증됨. 이후 소스 코드 수정은 기존 Worker에 자동 반영되지 않음.
- V5 `home-indexing` 빌드 모드 신규 구현: 서비스모델 `publishEnabled=false` 유지, 메인 홈페이지 `/`에만 `index,follow` + 자기 도메인 Canonical, sitemap 1 URL, 나머지 1732 지역페이지와 404는 noindex + canonical 없음. 기존 URL 번호와 ID 모두 유지.
- `robots.txt`는 Allow:/ (지역의 noindex 메타를 크롤러가 읽도록 해야 함), sitemap은 1개의 정식 홈 주소만. `workers.dev`는 Worker의 별도 강제 noindex 헤더/robots Disallow 조건을 지켜야 함.
- `homeIndexingScope=quicksky-home-1-20261027`, `homeIndexingApproved=false`, `homeBusinessFactsVerified=false`, `homeContentQualityApproved=false`, `publicIndexingApproved=false`. 지역 대량 공개 플래그와 상호 배타적. 이미지 지정권리 `imageAssetsApproved=true`, 도메인 연결 증거 `domainOwnershipVerified=true`는 별도 유지.
- **실제 운영에서 위 3개 홈 공개 게이트는 승인되지 않았으므로 `python -m v5 build --site quicksky --mode home-indexing`은 차단된다.** 테스트는 내부 메모리에서 가상의 승인된 설정을 구성해 실행했으며 실제 승인을 기록한 것이 아니다.

## 소스 및 독립 회귀 테스트
- 변경: `v5/service_model.py`, `v5/service_markup.py`, `v5/engine.py`, `v5/audit.py`, `v5/__main__.py`.
- 테스트: `tests/test_quicksky_home_index.py`. 전제조건 개별 미충족 시 차단, 일괄 `public-indexing` 거부, 홈 1개 외 1,732개 모두 noindex, 404 noindex, 정확한 sitemap과 canonical, 잘못된 sitemap 변조시 감사 실패 등.
- [Actions 40506439983](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40506439983): 초기 수정 반영 빌드·전체 회귀 성공(88 Python tests). 실제 site.json의 공개플래그 false와 시뮬레이션 분리 확인.
- `scripts/verify_quicksky_home_release.py`: 나중에 실제 정식 배포된 홈에 대해 public HTTP index meta/header/canonical, 지역 noindex, sitemap 1 URL, robots Allow, preview noindex, 404, 히어로 이미지의 실제 HTTP 200 검증에 사용할 **read-only** 검사 도구. 현재 운영에 대해 실행하면 실패해야 정상(noindex).
- IndexNow 키는 `null`, 새로운 키·Secret/OAuth/권한을 발급하지 않음. Google/Naver 등록은 부모 전담과 중복 금지.

## 행정동·법정동 지역명 실제 공식 매칭, 전체 원장 1732개 구분
- **공식 원문1:** [행정표준코드관리시스템 법정동 코드 조회](https://www.code.go.kr/stdcode/regCodeL.do). 2026-10-27에 노출된 서울 종로구 이름·10자리 코드 8건을 기록.
- **공식 원문2:** [행정안전부 2026-07-01 행정동 개편](https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=127039). 안양8/9동 폐지 및 **명학동/병목안동** 신설 명칭 확인. 정확한 10자리 행정동 코드는 이 원문에 노출되지 않아 미확인으로 유지.
- [입력 원장](../data/regions/quicksky_official_government_match_sample_20261027.json)과 [대조 스크립트](../scripts/match_quicksky_official_regions.py): 원본 1,732 URL 번호·ID 불변, 정부 8개 법정동 코드/명칭 일치 + 2개 행정동 명칭만 일치 = 10건 실제 대조. **나머지 1,722건은 불일치가 아니라 아직 조사하지 않음.**
- [Actions 40506816704](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40506816704)에서 1,732행 CSV 및 Summary JSON 아티팩트 생성·검증 완료. 정확한 작업근거가 없는 지역은 공식 명칭만 일치해도 색인 근거가 아님.
- 공식 데이터 포털의 [국토교통부 전국 법정동 2026-06-30 CSV](https://www.data.go.kr/data/15063424/fileData.do)는 전수 매칭 후보. 현재 세션에 전체 공식 원본 CSV가 검증 가능한 상태로 확보되지 않아 1,722개를 추정 매칭하거나 코드를 만들어 넣지 않았음.

## 정상 홈페이지 공개를 위한 운영자 확인 사항 (승인과 별개인 사실 검증)
1. Quicksky 상담번호 `010-5322-1952`가 실제 회사/상담 담당자에게 연결되는지 독립 확인. 사용자가 연락처 표기는 승인했지만 수신·영업실체 검사는 별도.
2. 서울·경기 전체가 아니라 **실제 문의·예약 가능한 권역**, 당일/예약/불가 조건을 운영자 근거로 확인. 현재 본문은 상담 안내 중심이며 **모든 동 실시간 배차 약속 아님**.
3. 1톤·3.5톤·5톤이 실제 협력 배차/보유 가능한 선택지인지 차량/협력 근거와 함께 확인. 사진 3개는 지정 사용 허락이 확인됐지만 각 톤수의 장비를 뜻하지 않도록 카드 이미지를 이미 제거함.
4. 홈페이지 원고 자체의 구체적 사용자 가치(견적 준비 항목, 절차, 불명확한 사업자 표기 정리)를 실제 사업 증거와 대조하여 **홈페이지에만 적용하는 품질 승인**. 이 승인은 1,732개 지역 콘텐츠 품질의 자동 승인이 아님.

## 결과 상태표
| 단계 | 상태 |
| --- | --- |
| 현재 Quicksky noindex 운영 접속 | 이전 검증된 배포 유지 |
| Home-only 색인 빌드 코드 | 구현됨 |
| Home-only 임시 승인 시뮬레이션 빌드 | 테스트 통과 |
| 실제 운영 홈 index | 보류(사업사실/홈콘텐츠 검증 필요) |
| 1732 지역 색인 | 보류(운영 근거 없음) |
| 공식 정부 지역명 10개 표본 대조 | 완료 (8개 코드·명칭, 2개 명칭만) |
| 지역 1722개 공식 전수 대조 | 미완료(최신 공식 전체 파일 확보 필요) |
| IndexNow/Google/Naver 제출 | 미실행 |
