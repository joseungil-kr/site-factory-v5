# 날마다꽃 전국 장례식장 — 문구 POOL 선행 구축 및 QA

## 원본 자료
- V4 branch: joseungil-kr/site-factory-v4 / feature/funeralflower-mini
- 1,080개 시설: data/flower/v4_facilities_1080.snapshot.json
- 600개 독립 전문 문구: data/pools/flower_funeral_professional_600.v4.json
- 48개 추가 상황별 문장: data/pools/flower_funeral_sample_pool.json
- 1,080개 시설별 원문 배정: data/flower/v4_facility_assignments_1080.snapshot.json
- 주제 그룹, 부적합 시나리오 제외 정책: data/flower/v4_assignment_policy.snapshot.json

## 반드시 지킬 제작 순서
1. 시설 원장 1080건·전문 POOL 600개·시설별 배정표 1080개·원본 지문을 검사한다.
2. 확정 배정된 원문을 우선 사용하고 별도 전문 문구/상황별 문장을 섞어 1080개 본문을 **메모리에서 먼저** 만든다.
3. 3개 난수 시드마다 무작위 1%(11개)를 나머지 1079페이지 전체와 비교한다. 실제 원문과 시설명·지역명 정규화 원문을 별도 검사한다.
4. 추가로 모든 1080페이지 쌍 582,660건을 실제/정규화 양쪽으로 **전수** Jaccard 비교한다.
5. 49% 이상 한 쌍이라도 있으면 HTML 생성 중단. 전체 본문 완전 중복, 지역 포함 제목 중복 및 본문 길이 2500~3200자를 점검한다.
6. 모두 통과한 뒤에만 noindex 미리보기 1080개 HTML 및 QA 보고서를 생성·저장한다.

## 명령 및 산출물
- 사전 유사도 감사만: python scripts/build_flower_funeral_national.py --audit-only
- 사전 감사 통과 후 HTML 생성: python scripts/build_flower_funeral_national.py
- 결과 JSON: reports/flower-funeral/pool-1080-1pct-audit.json
- GitHub Actions: .github/workflows/flower-v4-1080-preview.yml

## 공개 제한 및 검수
- 원본 V4 시설 원장은 publicationAllowed=false이며 위치/운영상태 검증이 완료되지 않았다.
- 전문 600문장과 추가 48문장은 콘텐츠 품질 검토 단계 자료이며 상업조건 검증을 대체할 수 없다.
- 확정되지 않은 종류별 가격은 '상담 확인'으로 유지한다.
- **49% 유사도 검사는 SEO 순위나 독창성/전문성의 보장이 아니다.**
- 최종 디자인 승인 전 flower.nalmada.net 운영 배포, 공개 색인, IndexNow 제출 금지.
- V4 운영 도메인/배포 연결과 V5 다른 사이트는 변경하지 않는다.

## 실측 QA 결과 (2026-10-27 KST, CI readback)

근거: [GitHub Actions run #40361533995](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40361533995) — `Flower 1080 funeral content-first similarity QA and preview build`.

- 복합 문구 POOL: V4 전문 문구 **600개 단위** + 추가 문장 **48개 단위**, 기존 1080 시설별 원문 배정표 사용
- 본문 길이: 최소 **2,555자**, 최대 **2,937자**, 중앙값 **2,751자**
- 장례식장 1080곳 각각 텍스트/HTML 미리보기 생성 성공
- 문자 5-그램 Jaccard **실제 본문 582,660쌍 전수검사**: 최대 **28.7784%**, 49% 이상 **0쌍**
- 시설명·지역명·주소 정규화한 본문 **582,660쌍 전수검사**: 최대 **29.6346%**, 49% 이상 **0쌍**
- 전수 합계 **1,165,320회**, 3개 난수 시드의 1% 표본 검사 **71,214회**
- 본문 완전 동일 중복 **0건**, 지역 구분 제목 **1,080개 모두 고유**
- 기존 레거시 미리보기 CI의 `numberOfHalls` 필드 가정은 `pageCount`로 수정. [수정 후 독립 검사](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40361534013) 성공
- 제공 산출물: GitHub Actions artifact `flower-1080-funeral-reviewed-noindex-artifacts` (유효기간 14일)

**판정**: 이 지표에서 49% 미만을 충족하여 검수용 HTML 생성 완료. **운영 배포 허용 판정은 아님.**

### 배포 전 별도 보류 사유

1. 원본 V4 시설 데이터의 `publicationAllowed=false`; 시설 주소·현행 운영상태 미검증.
2. 기존 전문 문구 원본의 `readyForPublication=false`; 일부 표현의 맥락과 사실성에 대한 사람의 검수 필요.
3. 상품별 실제 판매가격·배송 범위/비용, 이미지 사용권한 검증 필요.
4. 날마다꽃의 최종 디자인 승인 미완료. 사이트는 계속 `noindex` 상태로 보존.



## 검수용 Cloudflare Worker 배포 (2026-10-27 KST)

- 최종 검수용 소스 커밋: `7b588d4ea596cf70e5d8adcdab7c967c33a6ad84`
- 기존 V4 저장소에 독립 배포 워크플로 등록: [PR #455](https://github.com/joseungil-kr/fwith-site-factory/pull/455)
- 검증/배포 기록: [Actions run #40363527688](https://github.com/joseungil-kr/fwith-site-factory/actions/runs/40363527688)
- Cloudflare Worker: `sfv5-nalmada-flower-preview`, 활성 버전 `f2c2baec-a9ff-45b3-a3c5-e4efda8cac9e`
- Workers URL: https://sfv5-nalmada-flower-preview.joseungil.workers.dev/
- 생성 파일: 장례식장 본문 1080개 + `index.html` 검색 홈 + `halls.json` + `404.html`
- 전수 Jaccard 검사 최대 29.6346%, 기준 49% 미만. 원본/정규화 비교 총 1,165,320쌍, 실패 0쌍.
- 미리보기는 `noindex,nofollow`, HTTP Worker `X-Robots-Tag: noindex, nofollow, noarchive`, `robots.txt: Disallow: /`, 사이트맵/IndexNow 없음.
- Cloudflare API에서 `flower.nalmada.net` 기존 Custom Domain binding 없음 확인. 운영 DNS, Custom Domain은 **추가/변경하지 않음**.
- 배포 성공 후 GitHub runner에서 Workers URL 외부 HTTP 확인 시 **403**. 이 상태는 계정의 Cloudflare 활성 버전 확인과 구분하며 일반 방문자 접속은 추가 검증 필요.
- 본 페이지 자료는 여전히 `publicationAllowed=false`, `readyForPublication=false` 및 최종 디자인 미승인. `flower.nalmada.net` 운영 공개·색인은 승인 전에 실행하지 않는다.
