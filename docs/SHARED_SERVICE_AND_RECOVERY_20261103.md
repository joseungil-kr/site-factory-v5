# 서비스 문의형 지원과 복구 ZIP 검증 보완

이 단계는 기존 별도 브랜치의 후속 구현이다. 기존 운영 사이트, Worker, DNS, 보안 및 권한 설정은 변경하지 않았다.
신규 service-lead(스카이차 등)와 상품 주문형을 같은 공유 Worker 산출물에 함께 넣을 수 있다.
HTML 1회·이미지/CSS 0회는 앞선 **로컬** 진입 로그 결과이며 실제 edge 비용 절감 주장이 아니다.

## 기존 서비스 생성기 재사용

기존 서비스 validator·engine·renderer를 수정하지 않는다. 신규 서비스 입력은 기존 서비스 규칙에 따라
`publishEnabled: false`, `publicIndexingApproved: false`를 유지한다. 새 공유 방식의
`deliveryMode: "shared-static"`, 승인된 `site-spec.json`의 publish 계획 및 정확한 phone 문의 값,
`servicePublicationApproved`, `serviceFactsApproved`, 이미지·개인정보 검토가 필요하다.
실제 신규 사이트 자료의 승인을 임의로 생성하지 않았으며 테스트의 승인 플래그와 출처 mock은 가상 자료 전용이다.

기존 `build(..., mode='preview')`로 만든 서비스 원본과 manifest를 그대로 보관한다.
파생본에서만 기존 noindex 메타를 승인된 정확한 호스트의 index/canonical로 바꾸고 robots·sitemap·RSS를 준비한다.
404는 noindex를 유지한다. Naver 검증 값이 있으면 기존과 같은 40자리 hex 형식을 검사하고 홈페이지에만 넣는다.
문의 전화·서비스 본문·요금표·페이지 번호·기존 내부 링크는 바꾸지 않는다.
기존 audit를 파생본에도 실행하고 이후 호스트별 SEO·RSS를 검사한다.

실제 서비스 생성기를 사용한 테스트에서 `<body>` 전체가 자산 URL 변환 외에 동일함을 확인했다.
상품형의 기존 publish 출력과 서비스형의 기존 preview 원본을 하나의 묶음에 넣어 호스트별 SEO·RSS와
원본 manifest 모드(publish / preview)가 구분되는 것도 검사했다. 기존 Daysky 운영 자료는 수정하지 않았다.

## 복구 검증의 실제 공백과 수정

[재현 결과](shared-zip-gap-reproduction-20261103.json): 이전 verify는 ZIP 삭제 후에도 성공했고
`release.zip`을 `not a zip`으로 바꿔도 성공했다. 일반 파일 해시만 확인하고 ZIP을 제외했기 때문이다.
이 지적은 실제 결함으로 확인했다.

지금은 `snapshot.json`에 ZIP SHA-256와 releaseHash를 보관하고 다음을 필수 확인한다.

- ZIP과 hash record 존재 및 전체 ZIP 바이트 해시 일치.
- ZIP의 release manifest가 폴더의 manifest와 일치.
- ZIP 내부 파일 목록의 완전 일치, 중복·추가 항목 없음, 모든 내부 파일의 SHA-256 일치.
- 복원 결과에 **동일한 ZIP과 hash record** 보존.
- 복원한 결과를 `--previous`로 사용해도 이전 ZIP 해시가 실제 값으로 이어짐.

ZIP 파일 자체를 manifest 안에 넣는 순환 해시는 피하고 별도 record를 사용한다.
그 record를 공격자가 바꿔 ZIP 해시를 맞춰도 ZIP 내부 파일 변조를 잡는 회귀 검사를 추가했다.
누락·깨짐·위조·경로 이탈 거부와 복원 후 업데이트 이력을 검사했다.

[새 가상 혼합 패키지·복구 증거](shared-service-zip-proof-20261103.json)에는 원래 ZIP, 복원 ZIP,
다음 릴리스의 previousSnapshotSHA256가 같음을 기록했다. 로컬 산출물은 다음과 같다.

- `dist/shared-mixed-service-release-20261103/`: 서비스+상품 혼합 가상 패키지와 ZIP/hash record.
- `dist/shared-mixed-service-restored-20261103/`: ZIP에서 복원한 동일 패키지.
- `dist/shared-mixed-service-next-20261103/`: 복원한 패키지를 previous로 사용한 다음 릴리스.

## 기존 테스트 Worker 재사용 조사

이전 보고와 달리 기존 Wrangler OAuth 세션이 이미 있어 관리 API를 읽을 수 있었다.
새 로그인·권한 추가 없이 Worker 목록, custom domains, 모든 조회 가능한 zone routes,
테스트/preview 이름 후보의 settings·cron·현재 배포 버전을 조회했다.
[요약 증거](shared-worker-reuse-evidence-20261103.json)의 관리 API GET은 66회, 방문자 URL 요청과 변경 요청은 0회다.
스크립트 105개가 반환됐지만 요금제별 한도 판정이나 Worker 추가·삭제는 하지 않았다.

우선 검토할 기존 후보는 **`sfv5-ansan-promotion-plant-preview`**다.

- custom domain 없음, zone route 없음, cron 없음.
- bindings: ASSETS, V5_STAGING(plain_text). 비밀값을 보고서에 쓰지 않았다.
- 현재 100% 버전: `fe4f22ee-20d7-4790-b637-da35e9f4bea2`.
- 현재 코드 응답 백업 SHA-256: `054f9ef6aa6931a7e734ca0ba411221c1c96e846b00ad22be400ba6c836fa41f`.
- 원본 코드 백업은 `reports/private-worker-backups/`에만 보관하며 Git에 올리지 않았다.

**재사용 확정은 아니다.** ASSETS 전체 파일의 복구가 확인되지 않았고 workers.dev 사용 여부 및
다른 Worker의 역방향 service binding 참조도 확인하지 않았다. 버전 ID와 코드만으로 완전 복구라고 판단하지 않는다.
따라서 기존 후보를 덮어쓰거나 새 Worker를 만들지 않았다.

`sfv5-daysky-preview`, `sfv5-seoul-gyeonggi-plants-preview` 등은 실제 운영 도메인이 연결돼 있어 제외했다.
`ansan-flower-guide-test`도 ansan.fwith.kr에 연결돼 있다. 이름에 test/preview가 있어도 미사용으로 취급하지 않는다.

재사용을 진행하려면 ASSETS 파일·설정·바인딩·배포 원본의 완전한 복구 자료와 미사용 여부를 먼저 확인해야 한다.
확인 전에는 덮어쓰지 않는다. 실제 edge 시험과 로그·통계 비교는 여전히 미실행이다.

## 검사

Python 전체 100개 통과, 신규 release 검사 13개 통과. 서비스 실제 renderer 및 혼합 패키지,
ZIP 누락·위조·복원·다음 이력 연속성 검사를 포함한다. 운영 변경 없이 오프라인 준비만 완료했다.
