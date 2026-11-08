# V4 잔존 의존성과 비배포 이관 준비
2026-11-08. 지침은 V5로 통합하되 **운영 의존 이관은 아직 미완료**다.

## 직접 확인한 SkyQuote 실행 경로
[원본 workflow](https://github.com/joseungil-kr/site-factory-v4/blob/97436e8f020f68d22cca8570b00bf567f6fe704f/.github/workflows/skyquote-navermeta-minimal.yml)
는 V4 checkout 이후 V5 `e0d0fabc6aca320e21b29c81792b0132a5a6d478`를 checkout한다.
V4 `data/regions/sources/official-codes.zip` 길이413481과 SHA256을 검사한 뒤 V5 지역 검사·빌드·QA를 실행한다.
이후 기존 Worker `sfv5-skyquote-preview`를 배포한다.
V4 `ops/v5-isolated-staging-20261024`의 해당 workflow 수정 push 자체가 배포 trigger다. **이 파일을 복사해 활성 workflow로 추가하거나 원본을 수정하지 않는다.**

확정 hash: `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`.
이 hash는 workflow 원문에 적힌 기대값을 확인한 것이며, 이번 단계에서 ZIP 바이너리 실물을 읽어 검증했다는 뜻이 아니다.
V5가 독립 배포 가능하다는 결론도 아니다.

## 함께 남은 경로 (관리자 조사 보고)
- Todayflower RSS: V5 고정 소스 `0ca5705aa12950da571f089b2d4ac7256111f77e` 및 artifact13036248347 의존. artifact 보존기간/실물 해시/복원성 검증 전 이관 완료 불가.
- Clinic RSS: V5 baseline `32484f02e3c12e6bfcf057702041b70f66fdafe5` + patch `3ae081242743fb8d8bbdd498a44e3855782752ad`.
- V4 ops branch 조사 HEAD `ce4051221fc4c12e2c9c051a109d81a2b224a70b`. main만 조사하면 이 의존성을 놓친다.
- `docs/provenance.json`의 역사적 출처 링크는 현재 런타임 의존성과 별도로 분류한다.

## 안전한 다음 단계
1. 승인된 소스에서 원본 ZIP을 확보하고 아래 비배포 checker로 길이/hash를 검증한다. 파일을 옮기기 전 출처·사용조건을 기록한다.
2. V5의 별도 데이터 경로에 정확한 원본을 보존하고, 고정된 V5 source에서 읽도록 하는 빌드 전용 어댑터를 마련한다. 배포 코드·credential 설정은 복제하지 않는다.
3. 기존 source와 후보 source의 지역 ID/개수/생성 산출물 manifest를 비교한다. 기존 운영본을 생성·갱신하지 않고 분리된 시험 산출물만 사용한다.
4. Todayflower artifact와 Clinic patch도 원본→해시→재현 가능한 V5 입력 순서로 별도 검증한다.
5. 독립 입력·빌드·복구 검증과 사용자 배포 승인이 있을 때만 운영 경로 전환을 별도 수행한다. 이번 통합에서 5단계는 실행하지 않는다.
6. 전환 검증 전 V4 repo, 브랜치, 파일, Worker, 기존 운영 URL을 유지한다.

## 준비한 도구
`python scripts/check_v5_integration.py`는 문서 링크/원장/manifest를 읽기 전용 검사한다.
`python scripts/check_v5_integration.py --official-archive /approved/path/official-codes.zip`는 실물이 있으면 길이/hash만 검사한다.
네트워크 다운로드·비밀키 접근·배포·변경 기능이 없다. ZIP 옵션 없이 통과한 결과는 데이터 이관 완료가 아니다.
