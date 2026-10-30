# 바른견적스카이 · 사이트팩토리 V5 작업자 3
Status: five 768x640 WebP assets committed and three noindex pages built/tested in Actions. Production domain and DNS unchanged; isolated workers.dev preview configuration prepared, live deployment not yet independently confirmed.

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
Reviewed source ZIP: `skyquote-preview-reviewed-768.zip`. AM02 helper committed all five WebP binaries to `sites/skyquote/assets/`. Their remote Git blob SHA-1 values match locally computed Git blobs from the reviewed ZIP exactly (see assets-manifest.json for SHA-256 of each 768x640 image).
GitHub isolated QA Run `41019416398` succeeded: 5 asset hash/image checks, 3 HTML noindex/15 image references, 390px+1440px Chromium screenshot for every page (6 screens), no horizontal overflow. Artifact `12960459598` contains generated preview HTML and screenshots. This proves local Action-rendered output, not deployed HTTPS.
Isolated workers.dev noindex Worker source `sites/skyquote/worker.js` and config `sites/skyquote/wrangler.preview.json` added with `workers_dev=true`, no custom domain or routes. V4 deployment workflow `site-factory-v4` branch `ops/v5-isolated-staging-20261024` file `.github/workflows/skyquote-isolated-preview.yml` contains collision preflight, static asset build and HTTPS verification; live run has not yet been independently confirmed.

## Existing project safety
V5 Site Factory existing officeplant/hallflower branches and V4 deployed Worker unchanged. GitHub branch `feature/v5-skyquote-three-samples` is isolated. Do not deploy/create Custom Domain or use new secrets. Verify actual Worker-domain inventory before a future preview deploy. Call existing company by tel link only: no form values or user privacy sent.
