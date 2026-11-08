# 외벽스카이 V5-2

전용 브랜치 `feature/v52-wallsky`. 기존 운영 사이트와 공용 생성기 수정 없음.

목표: V5 고정 지역명 원장 1,732개 × 빌딩외벽/공장외벽/상가외벽 3개 의도 = 5,196 지역 문서 + 홈 1 = 5,197 URL. 원장은 V4 `NAME_CANDIDATES` 스냅샷(2026-10-12)이며 모든 행이 법정동 또는 행정동으로 공식 분류되었다고 주장하지 않는다. 지역 시설의 존재나 출동 완료를 주장하지 않는다. 읍·면은 원장에 없으므로 포함하지 않는다.

전화 010-5322-1952와 서비스 범위는 `sites/daysky/site.json`, 사진은 `docs/DAYSKY_PHOTO_PROVENANCE.json`에서 재사용한다. 장비 작업 지원과 전문 시공의 역할을 분리한다. 가격·보유 대수·지점·즉시 출동 보장은 생략한다.

빌드: `python scripts/build_wallsky.py`. QA: `python scripts/qa_wallsky.py`. 기본 결과는 noindex. 공개 빌드는 독립 QA와 Cloudflare binding preflight 후 `--public`으로 수행한다.

배포 후보: wallsky.nalmada.net / 신규 전용 Worker sfv52-wallsky. 기존 DNS/Worker 바인딩 확인 전 연결하거나 덮어쓰지 않는다. main 병합, 배포, live HTTP, IndexNow는 별도 단계이다.
