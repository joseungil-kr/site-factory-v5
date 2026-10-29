# Hallflower — 장례식장별 화환 주문 안내 (작업자 3)
Status: isolated preview source committed; NOT deployed; NOT indexed.

## Scope and evidence (2026-10-29)
- Approved target hostname (user 2026-10-29): `hallflower.nalmada.net`. Cloudflare custom-domain collision **not yet checked**; no DNS/Worker binding performed.
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

## Independent QA correction / current release blocker (2026-10-29)
- Confirmed dedicated workflow run **40810612603**, job **123239762913**: Python sample build PASS, Chromium widths 390/1440 and JS-disabled privacy PASS; full audit FAIL: **11 fixed samples x 1,079 = 11,869** comparisons, maximum **0.969006**, worst pair 875/485. No threshold/scope changes are allowed.
- Corrected `actions/upload-artifact@v4` by moving `if: always()` to step level, so failed jobs preserve generated preview and audit JSON.
- Disabled the invalid `i % 3` content-recycling nationwide path, explicitly failing before any claim of a valid 1,080-page release; 1,080 frozen facility records remain available for an editorially verified rewrite. This is an **unfinished development gate**, not a passing expansion.
- Verified the seller-owned public product detail image **B205** at `https://fwith.co.kr/data/item/flower379/B205/main_pc.jpg` via the exact image link on `https://fwith.co.kr/shop/item.php?it_id=B205`. Added that actual observed URL to the B205 card. Download/hash verification was blocked by network access, so SHA-256 is **not recorded** and release image integrity gate remains open. Other SKU photo paths are not guessed or fabricated.
- Real photos for remaining products, substantive independent per-facility copy, refreshed whole-corpus similarity and successful isolated workflow artifact run remain outstanding. Preserve noindex, no DNS/public release, no IndexNow.

## User-approved nationwide start (2026-10-29)
- User confirmed hostname and instructed nationwide construction/deployment start. This is authorization to proceed with an isolated deployment after collision checks, not evidence of completed Cloudflare binding.
- `scripts/build_hallflower_full.py` now creates 1,080 **noindex inspection pages only** from the frozen 1,080-row source, without modifying the V4 ledger. Similarity and facility verification still block public indexing. The script explicitly reports `publicReleaseBlocked: true`.
- Full QA intentionally fails if repetitive three-template bodies exceed the existing strict `<0.49` rendered-body char-5gram requirement. Do not reduce thresholds or skip the check to publish.


## Read-only live QA and public candidate (2026-10-29)
- Parent-confirmed read-only QA run `40830621043` succeeded: HTTPS home and index, real facility page, CSS, JS and robots returned 200 with noindex; unknown path returned 404; five seller image URLs returned HTTP 200; Chromium at 390px and 1440px verified five loaded images per viewport; no-JS order-note control remained disabled. This is a reported run result, not a public release.
- Existing preview remains `https://sfv53-hallflower.joseungil.workers.dev` on the same `sfv53-hallflower` Worker. Do not redeploy merely because an earlier run had a stale fixed-path 404.
- V4 read-only account inventory at Run `40820814630` reported the target custom hostname was unbound before the Worker inspection, and `sfv53-hallflower` was created `2026-10-29T04:29:59.730063Z` / modified `2026-10-29T04:30:22.685127Z`; two Wrangler deployments occurred `04:30:07.643095Z` and `04:30:20.844839Z`. This is a point-in-time result only; before any domain binding, rerun read-only inventory to catch later changes.
- Added `scripts/prepare_hallflower_public_candidate.py` to produce a separate, non-deployed candidate with 1,080 facility pages + homepage, self-canonical URLs, index/follow meta, robots Allow and sitemap with 1,081 URLs. The candidate manifest deliberately retains `publicReleaseBlocked: true`.
- Preview directory and Worker remain noindex with robots Disallow and sitemap 404. Public candidate config has `workers_dev: false` and no routes or custom-domain bindings. `worker.public.js` permits indexing only when `HALLFLOWER_PUBLIC=1` and request hostname is exactly `hallflower.nalmada.net`; 404 always noindex. This candidate does not attach the domain or enable public mode.
- Parent authorization covers preparation and nationwide content, but actual custom-domain binding/public indexing remains gated on current collision inventory, public asset/404/canonical/sitemap tests, rollback version selection, and coordinated release. No new secrets, permissions, or DNS writes have been made.
