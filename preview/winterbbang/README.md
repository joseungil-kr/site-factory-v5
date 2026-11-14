# Winterbbang 대표 HTML 미리보기

- 전용 렌더러: `scripts/winterbbang_render.py`. 원문: `docs/site-plans/winterbbang/copy-pool.seed.json` (64개 자체 작성 문단).
- 홈 1 + 서울 2 + 경기 4 = **대표 HTML 7개**. 실제 공개 또는 전체 지역 확장 완료 상태가 아닙니다.
- 미리보기는 모두 `noindex,nofollow`이고 실제 운영 주소에 대한 canonical을 넣지 않습니다.
- 공통 생성형 WebP 5개는 이미 `assets/library/winterbbang/*.webp`에 Git 커밋되었으며 각 SHA-256은 `docs/site-plans/winterbbang/images-manifest.json`에 고정합니다.
- `python scripts/winterbbang_render.py --output-dir preview/winterbbang --regions 6`을 실행하면 이미지 다섯 개의 SHA와 RIFF/WEBP 헤더·크기를 점검하고 `preview/winterbbang/assets/images/`로 복사합니다.
- 보고서 `preview/winterbbang/render-report.json`에서 실제 사용한 이미지 해시를 확인할 수 있습니다.
- 지역 이름은 기존 V5 역사 원장의 대표 후보와 대조한 것입니다. 현행 읍면동 전수 검증이나 실제 매장·상권 실적을 뜻하지 않습니다.
- 영업상 민감한 계약·초도비용·거래 세부조건은 공개하지 않습니다. 예상 60~70%는 매출에서 **재료비만** 차감한 매출총이익률이며 순이익률이 아닙니다.
- 이 PR은 DNS 변경·운영 배포·IndexNow 제출을 실행하지 않습니다. `winterbbang.nalmada.net` 및 기존 `.com` 호스트는 소유·충돌 검증 전 미확정입니다.
