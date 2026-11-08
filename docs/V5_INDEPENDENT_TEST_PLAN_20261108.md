# V5 독립 빌드·복구 테스트 준비
작성: 2026-11-08 UTC. 준비 기준: `1455a19eaebe58a5fffe2402ff3a6297268063ac` 및 각 의존 manifest의 고정 소스.
사용자 지시: 테스트 진행 준비. 이번 준비에서는 기존 운영 사이트 변경·재생성·재배포, Worker/DNS/보안/권한 변경, 공개 처리·검색 등록을 하지 않는다.

## 이번에 실제 실행한 범위
기존에 만든 **격리 시험 출력**만 읽어서 재검사했다. 새 사이트 생성·배포 또는 운영본 수정은 없다.
- source/input 40개 hash·크기 확인.
- 공식 ZIP과 Todayflower Library 복구본의 고정 hash·전체 manifest 확인.
- Todayflower 기존5087파일 불변, RSS1개 추가인 상태 확인.
- Clinic baseline15925파일 대비 RSS3개만 변경, HTML15906개 불변 확인.
- Todayflower 시작/마지막 문서와 Clinic3사이트 각각 시작/마지막 지역문서: HTML8개 구조·canonical 상태 스모크.
- RSS4개 각50항목·full content·pubDate 미생성 확인.
- 결과: [준비 검사 JSON](V5_TEST_READINESS_RESULT_20261108.json).
이는 DOM 스모크이며 디자인/편집 품질90점 검수나 실제 HTTP 접근보호 시험이 아니다.

## 고정 입력과 복구물
[의존 원장](v4-dependency-manifest.json), [Todayflower 입력 목록](V5_TODAYFLOWER_RSS_INPUTS_20261108.json)에 repository/ref/path/hash가 있다.
- 공식 ZIP413481 bytes: `44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd`.
- Todayflower 코드 `0ca5705a`, RSS코드 `01563363`, Library `libfile_036e72dc9e4481919d1742e1cd416804` 버전0, artifact SHA256 `16b52597fe77b0b4311ea21ad5daf6c5193af94346f8dc8df9834e676003a180`.
- Clinic baseline `32484f02`, patch `3ae08124`. 최신 branch HEAD로 바꾸지 않는다.
- SkyQuote 고정 검사 source `e0d0fabc`.
세부 전체 SHA는 각 원장을 따른다. Library 접근은 승인된 동일 사용자 경로로만 한다. 거절 시 다른 저장 경로로 우회하지 않는다.

## 테스트 단계와 통과 조건
| 단계 | 실행 범위 | 통과 조건 | 현재 |
|---|---|---|---|
| T0 입력 잠금 | source·manifest·backup 검사 | 모든 source/digest 일치 | 이번 준비에서 PASS |
| T1 데이터 복구 | 공식 ZIP·Library 복구 | 크기/hash·파일5087개 일치 | 직접 및 독립 담당 PASS |
| T2 격리 재현 | 이전 별도 출력의 변경범위 검사 | Today RSS1추가, Clinic RSS3변경, 기존HTML 전부 동일 | 이번 읽기전용 재검사 PASS |
| T3 무배포 스모크 | 문서8개·RSS4개 | main/h1/canonical 의도, full-content50개, 임의날짜 없음 | PASS |
| T4 깨끗한 환경 재연습 | 새 임시 디렉터리에 pinned 입력 재확보·복구 | 기존 디렉터리/운영본 없이 T0–T3 재현 | 다음 시험 |
| T5 비공개 HTTP/복구 | 명시된 승인 범위의 private endpoint | owner200·비인가401/403·실제 복구 | 현재 범위 밖, 미확인 |
| T6 실제 운영 전환 | 별도 사용자 배포 지시 후 | credential/route/rollback/live readback | 금지, 실행하지 않음 |

이번 단계의 PASS는 T4–T6를 포함하지 않는다. 기존 county 신규 시험의 담당5·비공개 배포/편집검수는 이 재현 시험과 별개다.

## 읽기 전용 재실행
지원 Python3 표준라이브러리만 사용하며 네트워크/설치/인증/배포 명령이 없다.
```bash
python scripts/check_v5_test_readiness.py \
  --inputs /test/pinned-inputs \
  --official-archive /test/official-codes.zip \
  --todayflower-artifact /test/restored-todayflower.zip \
  --todayflower-root /test/todayflower \
  --clinic-before /test/clinic-baseline/public \
  --clinic-after /test/clinic-patched/public
python -m unittest discover -s tests -p 'test_v5_test_readiness.py' -v
```
각 경로는 위 manifest의 실제 입력 구조와 일치해야 한다. Clinic before/after 및 Todayflower는 서로 다른 비중첩 디렉터리여야 한다. 이 검사기는 파일을 만들거나 overwrite하지 않으며 실행 결과 JSON은 호출자가 새 보고서로 보존한다.

## T4 준비물과 실패 처리
- Library 접근 가능한 사용자 소유 환경, 고정 GitHub source 읽기, Python3, 충분한 임시 디스크(최소2GB 권장).
- 현재 실측 데이터/산출물 약690MB. 시험 결과는 서비스 디렉터리에 복사하지 않는다.
- 원격 ref/file 부재, Library 권한/만료, digest 차이, 파일 수/변경범위 차이가 있으면 해당 단계 실패로 기록한다. 원본을 추정·재생성해서 부족분을 덮지 않는다.
- 인증·권한 설정 변경은 이번 준비에서 필요하지 않았고 실행하지 않았다.
- 실제 private endpoint와 배포 credential/rollback 조건은 아직 미확인이다. 여기에는 사용자 조치 없이 가능한 정적 시험을 먼저 끝낸다.
