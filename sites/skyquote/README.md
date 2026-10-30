# 바른견적스카이 · 사이트팩토리 V5 작업자 3
Status: 3-page local noindex prototype. NO production deployment, NO DNS or Worker mutation.

## Keyword and title
- Focus: `{지역명} 스카이차 견적 최저가`. No measured keyword search volume; previous `스카이차 비용` 340 is **not** interchangeable.
- Title: `{지역명} 스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이`.
- Domain candidate `skyquote.nalmada.net` ONLY; account DNS/custom-domain inventory collision NOT checked.
- Purpose: enable consistent-condition quotes, not a claim of guaranteed/lowest market price or a fake third-party comparison.
- Verified business destination: `https://www.skycar1day.com/`; current business telephone `010-5322-1952`. No invented branches, contractors, cases, prices, comparison samples or direct form submissions.

## Three representative locations (source ledger)
Source `data/regions/seoul_gyeonggi_current_dong.json` git blob `6de6e5751b26a13a2132238f13633df3de0cd2aa`, sample record `경기도 안산시 단원구 / 고잔동`.
- `/` — 안산시 (시)
- `/danwon.html` — 안산시 단원구 (구)
- `/gojan.html` — 안산시 단원구 고잔동 (동)

## Useful page flow
Quote intent answer → precise jobsite and height/outreach/load → equipment and work hours → mobilization, relocation, waiting, night, tax and cancellation inclusions → identical-terms quote checklist → operator and ground/traffic safety → verified telephone and operator website → FAQ.

## Research sources checked (2026-10-30)
- Existing company: https://www.skycar1day.com/ — operator telephone and current publicly shown rate table, 1t/3.5t/5t, half-day/full-day; not evidence for competitor-lowest quote.
- Competitor: https://www.cheonggusky.com/pricing/ — differentiates hours, night, standby, callout and individual model limits.
- Local SEO page: https://wormsz2.store/pages/%EA%B2%BD%EA%B8%B0-%EC%95%88%EC%82%B0%EC%8B%9C-%EB%8B%A8%EC%9B%90%EA%B5%AC-%EA%B3%A0%EC%9E%94%EB%8F%99 — region and cost-style structure, not proof of our services.
- Local competitor: https://xn--ok0b43td6gz6eda833etje.store/%EA%B2%BD%EA%B8%B0/%EC%95%88%EC%82%B0%EC%8B%9C/ — public tonnage/time price matrix but incomparable without matching conditions.
- Official static assets docs: https://developers.cloudflare.com/workers/framework-guides/web-apps/astro/
- Open source reusable reference: https://github.com/cloudflare/templates/tree/main/astro-blog-starter-template (check current LICENSE and maintenance before copying). The existing V5 standard-library static generator + isolated Cloudflare Workers Assets workflow is preferable; no new app framework needed. Avoid copying competitor price claims.
- GitHub repo exploration: no trustworthy ready-made Korean sky-lift quotation service found in focused repository search. Structural reference only; use V5.

## AI image pool — five genuine raster images, not SVG/placeholder
Five generated WebP images:
`city-crane.webp` (urban truck), `facade-safety.webp` (façade work), `sign-work.webp` (signage), `work-height.webp` (height and reach), `outrigger-access.webp` (ground and outrigger).
Each page references all five exactly once with real width/height, eager hero, lazy noncritical images, descriptive alt and explicit AI illustrative-not-real-project labels.
Local build/export in this conversation: `skyquote-preview.zip` containing `build.py`, `assets/5x.webp`, `dist/index.html`, `dist/danwon.html`, `dist/gojan.html`, CSS, robots and manifest. Original image files not yet committed to GitHub: a file-transfer path is required to upload the verified binary bytes; do not fabricate image commit SHA.
Local test reports 3 HTML pages, 5 embedded images per page, noindex robots preview.

## Existing project safety
V5 Site Factory existing officeplant/hallflower branches and V4 deployed Worker unchanged. GitHub branch `feature/v5-skyquote-three-samples` is isolated. Do not deploy/create Custom Domain or use new secrets. Verify actual Worker-domain inventory before a future preview deploy. Call existing company by tel link only: no form values or user privacy sent.
