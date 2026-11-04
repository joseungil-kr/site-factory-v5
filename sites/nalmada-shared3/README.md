# nalmada.net 공유 Worker — 3개 신규 Clinicflower 시안

- Worker: `sfv5-nalmada-domain` (신규 1개)
- 기존 17개 nalmada.net 운영 Worker 및 호스트 바인딩은 변경하지 않는다.
- 정확한 신규 호스트: `clinicflower.nalmada.net`, `clinicopen.nalmada.net`, `clinicpresent.nalmada.net`.
- `public/` 아래 정적 HTML 3개 + 공용 WebP 5개 + CSS 1개, Worker JS는 Host로 페이지 분기.
- 각 페이지는 title/description/H1/FAQ·설명 문구가 다르고, 720블록 POOL의 서로 다른 블록을 재사용한다.
- `tel:1844-0644` 8개씩. 사용자 입력 폼·쿠키·분석 없으며 사진은 실제 납품이 아닌 AI 연출.
- 샘플은 `noindex,nofollow,noarchive`; robots 전체 차단, sitemap/indexNow 없음.
- 이전 `sfv5-ansan-promotion-plant-preview` Worker는 원형 유지, 이 새 Worker로 재설정하지 않는다.
- Wrangler 실행은 GitHub Actions의 기존 Cloudflare 배포 자격에서만 진행한다. 계정 한도/호스트 충돌/DNS·Route 사전검사 실패 시 중단.
- Worker 재사용 범위: 신규 `nalmada.net` 호스트 3개. 기존 운영 17개 사이트 합산/재배포 금지.
- 동일 등록 도메인의 새 사이트는 이 Worker 버전에 모든 기존 허용 호스트/정적 자산을 포함해서 재배포해야 한다.
- 본 3페이지 샘플간 유사도 분석은 전국 5,302개 목표의 유사도 검사 통과 증명이 아니다.
## 전국 지역명 사용 지침 — 2026-11-04 사용자 수정

- **보유 원장의 지역명 전부 사용**. 기존 계획 후보 5,034개 중 상위 행정구역 연결 미확인 1,438개도 제거하거나 생성 대상에서 제외하지 않는다.
- 각 지역명은 원장 원문 그대로 HTML title/H1에 사용한다. 상위 시·군·구가 확인되지 않으면 허위 소속 지명을 붙이지 않는다. 이름이 같아도 원장 행 ID가 다르면 안정적 URL로 구분한다.
- 사이트별 전국 목표 5,302페이지(지역 후보 5,034 + 허브 268), 3개 합계 15,906페이지는 **계획 수량**이며 실제 생성·배포 완료 수량이 아니다. 전체 원장 행과 실제 파일 수를 대조한 다음 완료 판정한다.
- `clinicpresent.nalmada.net` 신규 표제는 **\`{지역명} 병원·치과·한의원 개업 축하화환 추천\`**으로 변경한다. 기존 배포 샘플 HTML은 이전 표제 상태이므로 페이지 재제작·검수 전에는 완료로 보고하지 않는다.
- 2026-11-04 19시 이후 사용자의 지시에 따라 제작과 관계없는 인포그래픽 이미지는 제작물에서 제외한다. HTML에 한글 텍스트를 실제 폰트로 렌더링하고 모바일/PC에서 글자 정상 출력 여부를 확인한다.
