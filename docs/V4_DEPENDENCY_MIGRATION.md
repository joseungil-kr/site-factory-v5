# V4 잔존 의존성과 비배포 이관 준비
2026-11-08. 지침은 V5로 통합하되 **운영 의존 이관은 아직 미완료**다.

## 직접 확인한 SkyQuote 실행 경로
[원본 workflow](https://github.com/joseungil-kr/site-factory-v4/blob/97436e8f020f68d22cca8570b00bf567f6fe704f/.github/workflows/skyquote-navermeta-minimal.yml)
는 V4 checkout 이후 V5 `e0d0fabc6aca320e21b29c81792b0132a5a6d478`를 checkout한다.
V4 `data/regions/sources/official-codes.zip` 길이413481과 SHA256을 검사한 뒤 V5 지역 검사·빌드·QA를 실행한다.
이후 기존 Worker `sfv5-skyquote-preview`를 배포한다.
V4 `ops/v5-isolated-staging-20261024`의 해당 workflow 수정 push 자체가 배포 trigger다. **이 파일을 복사해 활성 workflow로 추가하거나 원본을 수정하지 않는다.**

확정 hash: `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`.
후속 비배포 재현 단계에서 GitHub fetch_file(base64)의 고정 ref 원본을 읽어 ZIP 실물 길이/hash를 확인했다. 고정 V5 원본 감사 스크립트 실행도 통과했다.
V5가 독립 배포 가능하다는 결론도 아니다.

## 함께 남은 경로 (후속 단계에서 workflow 원문 직접 확인)
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


## 2026-11-08 비배포 독립 입력 검증 결과
- SkyQuote: V4 ZIP 실물 413481 bytes, 고정 SHA256 일치. V5 e0d0fabc 원본 감사 코드와 지역 원장으로 53403행·활성20560·읍면동4632·상위284 및 부모 매핑4632 재현. 서비스 제공 범위 검증은 아니다.
- Todayflower: 올바른 V5 저장소 artifact13036248347을 공식 다운로드 도구로 수신. 84218864 bytes, 고정 digest 일치, 5070 콘텐츠 문서의 manifest5087파일 해시 전부 확인. ZIP은 읽기만 했으며 해제·재생성·배포하지 않았다. 원래 run41185803963. 추가 RSS 생성 소스01563363도 workflow가 참조하므로 manifest에 기록했다. 해당 RSS 생성 동작은 이번 재현 범위에서 제외한다.
- Clinic: baseline32484f02와 patch3ae08124의 실제 build/patch/RSS source4개를 읽고 SHA256 고정. 패치 ref의 test_clinic_rss_feed.py 5개 테스트 통과. 15906 HTML 전체 재생성이나 운영 적용은 하지 않았다.
- 실패/복구 기록: generic fetch는 binary UTF-8 제한400 → 문서화된 base64 파일 읽기 성공. 잘못된 V4 저장소 artifact 조회404 → workflow에서 실제 소유 V5를 확인하여 정상 조회. 파일 전송 도구32MiB 한도 → 동일 도구가 제공한 공식 서명 URL로 수신 성공. 인증·권한 거절이나 보안 우회는 없었다.

실측 결과는 [JSON 보고서](V4_DEPENDENCY_REPRODUCTION_20261108.json), 소스 ref/path/hash는 [manifest](v4-dependency-manifest.json) 참조.
재검사: `python scripts/verify_v4_dependency_inputs.py --inputs /approved/pinned-inputs --official-archive /approved/official-codes.zip --todayflower-artifact /approved/todayflower.zip`.
입력 디렉터리는 manifest의 localPath 구조를 사용하고 각 파일은 지정 repository/ref/path로 확보한다. 검사기는 네트워크·추출·쓰기·사이트 빌드·배포 기능이 없다. 원본 ZIP/artifact는 이번 커밋에 올리지 않았다. 지속 보관·V5 배포경로 전환·완전 독립 복구는 별도 미완료다.
