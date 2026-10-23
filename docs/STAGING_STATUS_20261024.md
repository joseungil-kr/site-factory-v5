# V5 noindex staging — 2026-10-24 actual execution record

## Implemented and independently checked here

- Current V5 local source only. GitHub remote not created; Cloudflare staging Worker **not deployed**.
- Separate candidate Worker: `sfv5-ansan-promotion-plant-preview`; `workers_dev=true` and no production Worker names.
- `worker/index.js` attaches `X-Robots-Tag: noindex, nofollow, noarchive` to **every static response** when `V5_STAGING=1`, including missing pages, and keeps regular mode behavior.
- Preview HTML emits `<meta name="robots" content="noindex,nofollow">`; preview `robots.txt` disallows crawling; no canonical or sitemap/IndexNow; review banner appears on generated pages.
- Five V4 catalog reference thumbnail URLs added to V5 products as preview references (not downloaded and not independently image-tested); three shared SVG hero illustrations are still placeholders.
- `python -m v5 prepare-staging` validates preview manifest byte hashes before creating a separate staging Wrangler config; forbids publish-mode HTML and analytics in staging.
- `python -m v5 staging-check --origin https://...workers.dev` verifies live noindex header, preview HTML and 200/404 **only once deployed**. No output from this check is claimed yet.
- GitHub Actions manual staging workflow prepared; secrets must be supplied via GitHub repo settings. It must discover actual workers.dev account subdomain and report successful live URL only after readback.
- The GitHub new-repo action is not exposed in this conversation's installed GitHub connector. `scripts/create-private-repo.sh` uses the documented GitHub CLI creation endpoint **if run in a separately authenticated environment**; it has not been run here.

## Verified / not verified

| Check | Status |
|---|---|
| Python offline tests | PASS — 36 |
| Node Worker tests | PASS — 4 |
| HTML build + static audit | PASS — 10 detail pages, 2 utility pages, 22 files; zero local audit errors |
| Per-file preview hash consistency | PASS — staging_preflight |
| noindex edge header behavior | PASS — mock Workers response unit test |
| Exact pages and CTA links | PASS — static link and local HTTP tests |
| Real Github private repo | NOT DONE — no create_repo connected action, no authenticated CLI/network |
| Cloudflare staging workers.dev deployment | NOT DONE — no credential/network path |
| Remote HTTP readback | NOT DONE — no deployed URL |
| Browser PC/mobile visual | NOT DONE — local Chromium ERR_BLOCKED_BY_ADMINISTRATOR |
| Actual product image load/stock | UNVERIFIED except two product pages text seen on current web search |

## External prerequisites, no code changes needed

1. A connected GitHub repository-creation action or an authenticated `gh` CLI session to create `joseungil-kr/site-factory-v5` as **PRIVATE** and push this checked commit; GitHub's documented REST `POST /user/repos` capability exists but is not exposed as an action here.
2. V5 repository-level GitHub Secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`; do not paste secrets into chat, code, commits or artifacts.
3. A workflow dispatch to `V5 noindex staging deploy` (does **not** publish V4 or any production site), with live readback. If Cloudflare account's workers.dev subdomain is not enabled, its activation is a separate account change requiring the owner's authorization.

Once a real URL exists, it can be inspected in a browser before deciding on product images, prices, design and full-scale release.
