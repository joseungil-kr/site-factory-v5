# Wallsky 운영본과 독립적인 작업자2 신규 꽃배달 사이트 QA — 2026-10-29

| 단계 | 확인 상태 | 증거 |
|---|---|---|
| PLAN | 완료 | 승인된 `site-spec.json` |
| PRODUCT / REGION | 고정 | `regions.json` 5,034 지역, `products.json` 6 SKU |
| REPRESENTATIVE | 완료 | run 40810124055, 대표 6지역 23 HTML |
| NATIONAL GENERATED | 완료 | run 40810543208, **10,336 URL** |
| STATIC HTML / LINKS | 완료 | HTML 10,337개(404 포함), 링크 103,077, 오류 0 |
| SIMILARITY | 완료 | 118 표본 vs 10,068 본문, 1,187,906쌍, 최고 47.3684% |
| PRODUCT LIVE | 완료 | run 40810652440, 6 상품 + 6 사진 HTTPS 200 |
| PUBLIC CANDIDATE | 완료 (오프라인만) | run 40810797144, sitemap/Canonical 10,336 URL |
| CF HOST PREFLIGHT | 읽기 제한 | V4 run 40810342800: Zone active, custom domain 없음, DNS/Route 403 |
| DEPLOYED | **미실행** | 실제 운영 연결 부모 조율 필요 |
| INDEXNOW / GSC / NAVER | **미실행** | 공개 후 별도 확인·등록 |

### 수정 이력
첫 전국 검수의 최고 유사도 **61.435%, 49% 초과 167쌍**으로 FAIL 판정. 독립 문장 48개를 추가하고 동일 검사 실행하여 최고 **47.3684%, 위반 0**으로 통과. 기존 검사값을 삭제·합격으로 변조하지 않음.

### 핵심 한계
2025년 외부 보조 읍면동 자료와 2026년 V4 상위 코드 마스터의 불일치 1,438건은 행정동 이름의 최신성 문제일 수 있어 확정 현행 지명이라고 주장하지 않는다. 지역명은 위치 탐색을 돕고 지역 꽃집·장례시설·당일 배송 실적의 증거가 아니다. 상품 가격은 2026-10-22 기준가이며 최종 실판매가 보장이 아니다. V4 기존 공식 코드 원본ZIP은 아직 이 브랜치로 이관·전수 파싱되지 않음.

### 운영 배포 차단
`wreath.nalmada.net` DNS 및 Workers Route 조회 권한 HTTP403. 읽기 실패한 배열을 충돌 없음으로 취급하면 안 된다. 기존 UI에서 exact hostname / route / record 중복과 사용 가능한 별도 Worker를 검증해 부모가 공개 연결을 조율해야 한다. 운영 사이트·보안 설정을 임의 변경하지 않는다.
