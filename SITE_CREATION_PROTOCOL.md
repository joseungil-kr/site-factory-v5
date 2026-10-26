# 사이트 제작 사전기획 게이트 (Preflight Planning Gate)

## 대상
Site Factory에서 **새로 생성하는 사이트**. 기존 운영 사이트의 배포/빌드 기능을 소급 차단하지 않는다.

## 순서
1. 기존 저장소, 유사 오픈소스, 디자인·콘텐츠·상품 및 배포 성공 사례를 조사한다.
2. 도메인·브랜드·전화, 대상 고객과 비즈니스 모델, 지역과 시설 범위, 페이지 타입별 생성 수량, URL/제목 샘플, 이미지와 실제 상품 근거, 텍스트 POOL, 표절·중복 기준, 검색/공개 상태를 정리한다.
3. **누락된 정보만 질문**한다. 사용자에게 결정받기 전에는 임의의 축소 페이지 수를 완료 목표로 정의하지 않는다.
4. 메인/히어로 페이지 디자인 및 히어로 이미지(출처·사용권한 포함)를 제작해 실제 시안으로 보여준다. 모바일·데스크톱 구성, 색상·메뉴·CTA·이미지 등을 검수받고 수정 후 **사용자의 최종 승인**을 기록한다. 승인 전에는 실제 본문 대량 생성·빌드·배포를 진행하지 않는다. 디자인 변경 시 재승인을 받는다.
5. `site-spec.json`에 확정된 계획을 저장하고 `python -m v5 plan-check --site <id>`를 실행한다.
6. 승인 후 승인된 디자인을 템플릿에 반영 → 생성 → 목표 수 검증 → 지역·시설/상품 의도 점검 → 최소 1% 시드 고정 표본의 전체 모수 대조 → SEO/HTTP/이미지 → 커밋 → 배포 → IndexNow로 진행한다. 유사도 49%는 **측정 지표를 명시**하고 각 문서 특성도 독립 검수한다.
7. 가격, 배송 보장, 전용 주소, 실적을 근거 없이 창작하지 않는다.

## 필수 필드
`domain`, `brand`, `businessModel`, `serviceScope`, `pageTypes`, `targetPageCount`, `titlePattern`, `urlPattern`, `keywordGroups`, `copyPoolPlan`, `similarityAudit`, `conversion`, `images`, `designReview`, `publishPolicy`, `approved`.

`approved=true`라도 검증할 값이 없으면 FAIL. 검사는 `v5/site_plan.py`에서 수행한다.

## 단계별 완료 판정
PLAN / DESIGN_DRAFT / DESIGN_APPROVED / POOL / GENERATED / QA / COMMITTED / DEPLOYED / LIVE_HTTP / INDEXNOW를 별도 기록한다. 단계 하나가 성공해도 전체 프로젝트 완료로 부르지 않는다.
