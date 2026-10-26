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
