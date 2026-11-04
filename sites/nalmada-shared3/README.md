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