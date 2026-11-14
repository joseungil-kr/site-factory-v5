> **현행 안내 (2026-11-08):** [V5 통합 작업 창구](V5_CONTROL_INDEX.md)를 먼저 읽는다. 아래 본문에는 과거 시점의 상태와 제한이 보존되어 있다. “원격 저장소 미생성”, “병합 보류”, 초기 SVG/독립 페이지 구성은 현행 운영 전체의 상태가 아니다. 현재 공통 생성기 기준은 V5 main의 V5.1이며 사이트별 상태·브랜치·검증 여부는 통합 원장이 기준이다. 과거 승인 거절 기록은 삭제하거나 무효로 해석하지 않는다. 기존 사이트 재생성·배포는 이번 통합 범위가 아니다.

# V5 공유 전달 main 통합 확인

## 현재 상태: 병합 보류

개선 코드는 별도 브랜치에 업로드됐고 [draft PR #28](https://github.com/joseungil-kr/site-factory-v5/pull/28)을 만들었다.
main 병합·푸시 명령은 프로세스 실행 전에 자동 승인 검토에서 거절됐다. 로컬 병합과 원격 main 푸시는 실행되지 않았다.
거절 이유는 일반 GitHub 커밋·푸시 승인 외에 기본 main 브랜치 병합·푸시 자체의 명시적 사용자 승인이 확인되지 않았고,
main 변경이 외부 자동화나 배포를 유발할 수 있다는 것이었다. 이 거절을 우회하지 않는다.
원격 main은 아래 기준 SHA에 그대로 있으며 사용자의 해당 main 병합 승인 전까지 PR은 draft로 유지한다.

기준 main은 `a466473c86e485baa9752ba0c2f74b058dd2ac9a`이며 최신 fetch에서 바뀌지 않았다.
사이트 입력, 기존 Worker 파일, engine, 서비스 validator/renderer, templates, workflow는 수정하지 않는다.
기존 배포 코드 변경은 shared-static 및 shared-static-preview만 개별 배포를 거부하는 조건이다.
기존 사이트에 새 deliveryMode를 넣거나 운영 경로를 이동하지 않는다.

신규 scaffold에는 `shared-static-preview`가 기본값이다. publish 준비는 명시적으로 shared-static으로 전환해
공유 release 명령을 사용한다. README와 사전기획 프로토콜에도 이 경로와 제약을 넣었다.

## 실제 파일 입력 검사

신규 서비스형 `site.json`, `site-spec.json`, pages, services, rates, regions, links, special-pages JSON을
임시 사이트 폴더에 쓰고 config.SITES만 그 폴더로 지정해 실제 `read_site` 경로를 실행했다.
어댑터·engine·audit의 입력 reader를 mock하지 않고 서비스 패키지를 준비·검증했다.
가상 자료와 이미지 출처 검사 mock을 사용하는 테스트이며 실제 사업 승인이나 공개 사이트를 만든 것은 아니다.

analytics, IndexNow, siteSearch 또는 special-pages를 실제 입력 파일에서 켜면 기존 service validator가 거부한다.
잘못된 전화와 전화가 아닌 문의 방식도 거부한다. 지원하지 않는 기능은 조용히 생략하지 않는다.
서비스형은 현재 전화 문의 방식이고 외부 폼·동적 검색·이벤트 수집은 지원하지 않는다.

전체 Python 검사 101개와 Node 검사 10개 통과. 새 기본 scaffold, 기존 제작·배포 검사, 파일 기반 서비스형 입력,
미지원 기능 거부, ZIP 누락·위조·복원 후 이력 연결을 포함한다.

## 배포 트리거 확인 범위

- GitHub main push의 일반 workflow는 `check.yml`의 오프라인 테스트·미리보기 build/audit다.
- 자동 운영 Daysky 배포는 sites/daysky/site.json, v5/service_model.py, v5/engine.py 및 해당 workflow 변경만 해당한다.
  이번 diff에는 이 경로가 없다.
- live SEO/visual/staging 진단은 각 workflow 파일이 바뀔 때 실행되며 이번에 수정하지 않았다.
- publish 및 staging 배포는 workflow_dispatch이며 호출하지 않는다.
- 기존 main의 최근 Actions run도 오프라인 검사만 성공했다.
- Cloudflare Pages 관리 API에서 이 저장소를 연결한 프로젝트는 발견하지 않았다.
- 별도 Workers Builds 목록은 기존 OAuth로 HTTP 403이었다. 권한 추가나 재로그인은 하지 않았다.
  기존 브라우저 읽기 fallback도 `window id 131750 no longer belongs to Naver_Whale; current owner is Naver_Whale`
  바인딩 오류가 한 번 재시도 후 반복돼 중단했다. 이 외부 설정은 확인 완료로 주장하지 않는다.

실제 배포 명령이나 공개 URL 호출은 하지 않았다. 명시된 저장소 트리거와 경로 검토는 완료했지만 main push는 거절로 미실행이다.
대신 draft PR의 오프라인 Actions와 원격 브랜치 SHA를 읽기 전용으로 재확인한다.
HTML 1회·이미지/CSS 0회는 로컬 증거이며 실제 edge 호출량 절감 검증은 여전히 별도다.
