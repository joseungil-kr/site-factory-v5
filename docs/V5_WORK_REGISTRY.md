# V5 작업자·사이트 원장
2026-11-08 UTC 조회. 아래 branch SHA는 GitHub 원격 직접 조회. 대화 인계와 품질 결과는 관리자의 이전 조사/작업자 보고이며 이 원장 작성 시 재실행하지 않았다. 행의 계획은 작업지시 전송 완료를 뜻하지 않는다. 모든 저장소는 별도 표기 없으면 `joseungil-kr/site-factory-v5`.

| 담당 / 최근 대화 | 사이트 / 소스 브랜치 / 조회 SHA | 확인 범위 및 남은 일 |
|---|---|---|
| 1 [후속5](https://chatgpt.com/c/6aefe617-c380-83ee-90b1-8e88ca63dc5f) | Todayflower / `site/todayflower-nalmada-pilot-20261030` / `950d3485cb6d3a769515b5da0de0e3045c804797` | 원격 SHA 확인. 기존 QA3 run 42441187025 실패 보고. 군 시험을 중복 재개하지 말고 담당5로 연결. 기존 운영본 재생성·재배포 금지. |
| 2 [후속2](https://chatgpt.com/c/6aefe57b-d490-83ee-8192-916e0064bf6e) | WreathPrice / `feature/v52-wreathprice-20261030` / `2071a3347f8ecdb39f6c628ae64efc4d7bdc2166` | 대표3 화면 QA 보고와 전국4935 문서 편집 승인 구분. 전국1% 최소50개 미승인. 군 시험 이전 인계 혼동 해소 필요. |
| 3 [최근 대화](https://chatgpt.com/c/6aefe2d0-4178-83ec-a12b-42d929af6de1) | SkyQuote / `rss/skyquote-production-20261103` / `4e7ff1f179270c7be316007a422103d4c5cc209a` | V4 run42211148402의 과거 배포 경로 확인. 현재 운영 HTTP는 이번 검증 대상 아님. worker2 오인 인계 뒤 worker3로 정정된 이력. |
| 4 [후속2](https://chatgpt.com/c/6aefe651-5454-83ee-815d-b132c320d82d) | Clinicflower·clinicopen·clinicpresent / `fix/clinic-rss-full-content-20261105` / `aa3efe4b1c686512b38a0f240db5aeeac70ab394` | RSS CI와 전체 문서 편집 품질은 별개. 사이트당5302는 이전 보고 수량. 운영소스 연결 및 품질 검증 미완. 기존 사이트 수정·배포 금지. |
| 5 [기존 작업 창구](https://chatgpt.com/c/6ae713bb-de70-83e8-9f3c-316a979aec53) | 신규 전국 군 근조화환 / `site/v51-county-funeral-ownerprivate-20261107` / `1812a4aa1f12f9104d19fbad57fedad5a1697dfe` | 내용 기준 `ceb3c53a8d804d4103cb3d244098564a7da2dfe6`. 95HTML·103파일·38화면·10표본90–93은 작업자 보고. run42442541265/42442541272/42442541305 성공과 독립 편집검수는 구분. 비공개 실제 배포·owner200/비인가401·403 미확인. 생성 규칙 개선→재생성→동일/신규 표본 검수 담당. |

## 배포·외부 의존
- Todayflower: V4 RSS 배포 경로는 V5 `0ca5705aa12950da571f089b2d4ac7256111f77e`와 artifact13036248347 사용. 새 브랜치 HEAD가 배포본이라는 뜻이 아니다.
- SkyQuote: 기존 Worker `sfv5-skyquote-preview`, V4 workflow, V4 공식지역 ZIP과 V5 고정 소스 조합. [상세](V4_DEPENDENCY_MIGRATION.md).
- Clinic 계열: V4 RSS 경로는 baseline V5 `32484f02e3c12e6bfcf057702041b70f66fdafe5` + patch `3ae081242743fb8d8bbdd498a44e3855782752ad` 소비(관리자 조사 보고). HEAD와 운영본을 동일시하지 않는다.
- WreathPrice의 현재 Worker/운영 소스 일치, 군 시험의 private endpoint는 미확인이다.

## 인계 시 갱신 필수 항목
사이트 ID, 현재 대화, 원격 branch/HEAD, 실제 배포 SHA와 run, 입력·자산·V4 의존성, 다음 작업, 금지 작업, 직접검증/보고/미확인, 확인시각.
인계 때 기존 문서를 새 채팅에 복사했다고 수신·실행을 완료 처리하지 않는다. 정책 거절을 우회 전송하지 않는다.
