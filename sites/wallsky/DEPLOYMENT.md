# Wallsky release plan — updated 2026-10-28

## Current state

- Dedicated source branch: `feature/v52-wallsky`.
- Target hostname: `wallsky.nalmada.net`.
- Intended dedicated Worker: `sfv52-wallsky`.
- V5 offline build/static QA run [40711586641](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40711586641) succeeded. The later cross-Daysky comparison is being checked separately.
- The source ZIP was verified by SHA-256 and its key files have been committed to the dedicated remote branch. No main merge, Cloudflare binding, DNS edit, production deployment or IndexNow submission has occurred.

## Reuse the existing successful V4 path

Use V4 branch `ops/v5-isolated-staging-20261024`, which already contains successful site-specific releases for Daysky and Quicksky and uses existing `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` secrets. Pin the exact reviewed V5 source commit. Do not create new Secrets, tokens, OAuth scopes or permissions.

## Required read-only preflight

1. Identify the existing Cloudflare account by matching the already authorized V4 proof Worker domains.
2. Confirm `nalmada.net` is active in that same account.
3. Check account-level custom-domain bindings for `wallsky.nalmada.net` and `sfv52-wallsky`; read existing Worker deployments.
4. Read DNS records and Worker routes for the target hostname. If DNS/Routes Read returns 403, do not infer absence from empty arrays; use the established public DNS fallback only where safe and stop if route conflict remains unknown.
5. If the hostname is attached to another Worker or any record/route conflicts, stop and report. Do not overwrite it.

## Dedicated public release

1. Pin the reviewed source SHA, run Python and Worker regressions, `python scripts/build_wallsky.py --public`, `python scripts/qa_wallsky.py`, `python scripts/cross_wallsky_daysky.py`, and local HTTP checks.
2. Build a Wrangler config for only `sfv52-wallsky`, `workers_dev:true`, `preview_urls:false`, static assets `html_handling:none`, `not_found_handling:404-page`, `run_worker_first:true`. Set `WALLSKY_PUBLIC=1` only for the exact `wallsky.nalmada.net` release. Do not modify V5 shared Worker routing or any other site's variables.
3. Capture the pre-deploy Worker version if it exists. Deploy the isolated Worker assets and attach only the exact hostname after preflight. If the new site has no prior version, rollback means withdraw only this new site's binding/release; preserve all existing bindings. If an existing site version is present, restore that captured version at 100%.
4. Live-check every canonical URL (5,197), four supporting resources, robots, sitemap, exact canonical/robots meta, phone links, image status, unknown path 404/noindex, error asset noindex, and workers.dev noindex. Also inspect desktop/mobile screenshots from live HTML. Save an immutable run/readback report.
5. Only after live HTTP success, validate an existing authorized IndexNow key file by HTTPS 200 and exact body, submit the intended canonical URLs once, and save the actual response. Do not claim Google/Naver indexing; parent registration owner handles their submissions.

## Truth boundaries

The 1,732 inputs are V4 `NAME_CANDIDATES` region-name rows as of 2026-10-12, not independently verified legal/administrative classifications or proof of facility presence. Pages describe equipment access consultation, not completed work, professional waterproofing/painting or guaranteed dispatch. No guessed local case studies, fleet counts, rates or arrival times.
