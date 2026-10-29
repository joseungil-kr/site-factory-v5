# Hallflower — 장례식장별 화환 주문 안내 (작업자 3)
Status: isolated preview source committed; NOT deployed; NOT indexed.

## Scope and evidence (2026-10-29)
- Proposed hostname: `hallflower.nalmada.net` — candidate only; DNS and Cloudflare Worker custom-domain collision **not checked**.
- Site source of record: `joseungil-kr/site-factory-v5`, branch `feature/v53-hallflower-order`.
- Existing V4 facilities source (read only): `joseungil-kr/site-factory-v4`, `feature/funeralflower-mini/data/funeral-halls/facilities.json`, Git blob `b950e7bf2cde7b247447fbe670c976363e4e1a7e`; parsed count **1,080**.
- Facility records carry `verification.currentAddress=not_checked`, `currentOperation=not_checked`, `officialName=not_externally_verified` for selected samples; historical name/address only, not independent operating-status confirmation.
- Three seed facilities in generated script: 서울대학교병원장례식장 / 삼성서울병원장례식장 / 서울아산병원 장례식장. The ids and addresses are carried over verbatim from the frozen V4 registry.
- fwith.co.kr product pages observed: B205 근조 특대 3단 화환 109,000원; B214 장례식장 근조 서양란 200,000원. Product prices are snapshots and may change; additional delivery charges need seller confirmation. Photographs have **not** been bundled in prototype; obtain original seller image URLs/hash before adding images.
- Benchmark references (structure only, no copied text): https://www.kotjumun.com/shop/faq.html?page=4 ; https://icfp.thegardenflora.co.kr/about/ ; https://xn--9m1bt77dma.com/blog/condolence-wreath-guide .
- User specifies title template: `{장례식장명} 빠른 장례식화환 주문방법`. No claimed funeral-hall partnership, live room data or guaranteed delivery window.

## Build and review
```bash
python -m py_compile scripts/build_hallflower.py
python scripts/build_hallflower.py
python -m http.server 8896 --directory dist/hallflower-preview
```
Review `/`, three `/halls/*.html` pages, responsive 390px/1440px, actual product links and phone link. Generated preview is `noindex,nofollow`, robots Disallow, with no sitemap or production domain binding. No API or JavaScript network access is needed. No HTML form is used; order memo is local-only, disabled until JS initializes, and **not** automatically submitted or copied.

## Expansion acceptance gates
1. Import the frozen V4 registry by pinned blob SHA using an authorized reproducible source access path; never alter upstream. Build an inclusion log for every facility, preserving name/address and source verification flags. For names with `nameReviewRequired`, quarantine from public release pending review.
2. Confirm current existence/name/address against a qualified source. Do not infer current operation from legacy listings, and do not invent room or mourner data. Exclude/flag unconfirmed entries for review instead of confidently calling them open.
3. Verify fwith current product/price/image/stock/checkout path and jurisdiction-specific wreath restrictions before publication.
4. Audit every canonical URL and sitemap URL, 404, reciprocal/internal linking, mobile, JS-off/JS-error, tracking privacy, image hashes, and preview/public robots. Run actual rendered-body char-5gram Jaccard sample vs entire corpus with maximum **strictly below 0.49** and publish measurement scope/seed; do not claim current three-page prototype proves nationwide uniqueness.
5. Only after test and parent release approval: verify Cloudflare account-owned domain/Worker inventory, preserve prior Worker version (rollback), deploy preview to an isolated Worker with noindex and inspect HTTPS. Parent handles public custom domain and indexable deployment, IndexNow once after proven HTTP coverage, Google and Naver property registration. Do not reuse Officeplant's IndexNow key or receipts.
6. Consent-safe analytics: only page-level aggregate conversions or tel/checkout clicks, no form values, phone, user names or URLs with private details. Tag production conversion only after user-approved measurement configuration.

## Known limitations
Prototype generator and GitHub QA workflow are committed, but an independent successful Actions run, real browser screenshot, live HTTP test and deployment evidence were not available in this session. No public release is claimed.

## Follow-up implementation (2026-10-29)
- Verified seller category `https://fwith.co.kr/shop/list.php?ca_id=20` lists B200 59,000, B203 79,000, B205 109,000, B212 60,000 and B214 200,000 KRW; all point to their own `/shop/item.php?it_id=SKU`. Delivery fees or facility restrictions vary.
- Frozen, minimized identity + status flags of **all 1,080** V4 records at `sites/hallflower/facilities-frozen.json`; **229** are marked `nameReviewRequired`. This snapshot is not verification of present operation.
- `python scripts/build_hallflower_full.py` produces a separate **noindex** 1,080-page candidate, not a public release.
- `python scripts/audit_hallflower_full.py` performs seeded 1% sample-versus-all rendered char-five-gram audit; nonpassing similarity must block publication. This is a test implementation, **not yet a PASS report**.
- `python tests/hallflower-browser-smoke.py` checks real Chromium 390/1440 layout, five product links, no-JS disabled control and no personally identifying query-string submission. Workflow includes that test before full-corpus build.
- Product photo assets still **missing**: correct product-image URL and original hashes must be verified from fwith and included; never fabricate an image path. This currently blocks visual approval and public release.
- CI using GitHub's existing generic V5 offline workflow is not evidence that the new Hallflower-specific Chromium/similarity workflow completed.
