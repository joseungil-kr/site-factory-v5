# V5 deployment, staging and independent recovery

## First site state

- Site id `ansan-promotion-plant`, domain **NULL**, Worker name **NULL**, `publishEnabled=false`.
- Stock/current price and actual order links on `fwith.co.kr` require a final live check. Existing prices are reference data.
- The 3 graphics are shared SVG demonstration illustrations, **not approved product images**.
- Privacy and actual call-to-action measurement require separate review before activation.
- Original V4 production Cloudflare Worker names, versions, IndexNow keys and secrets must not be reused implicitly.

## Local steps

```bash
python -m unittest discover -s tests -v
npm test
python -m v5 build --site ansan-promotion-plant --mode preview
python -m v5 audit --site ansan-promotion-plant
python -m v5 dashboard
python -m http.server 8000 --directory dist/ansan-promotion-plant
```

Open `http://127.0.0.1:8000/` locally in a permitted browser. A directly opened `file://` preview is **not** reliable because URLs are root-relative.

The preview must have `noindex` and `Disallow: /`; no production sitemap and no authorized domain are assumed.

## ChatGPT-led updates after a remote repository exists

1. ChatGPT updates per-site ledger files with its GitHub write tool or a controlled pull request.
2. A push to `main` triggers `.github/workflows/check.yml`, producing the preview artifact.
3. The resulting SHA, audit report and changed file manifest are reviewed.
4. A release request triggers the guarded production workflow. The current connector cannot directly dispatch a workflow; the manual dispatch in GitHub is a fallback, not something this chat has already done.

Example dry-runs (no source change without `--apply`):

```bash
python -m v5 change-global --site ansan-promotion-plant --field phone --value 031-123-4567
python -m v5 add-special --site ansan-promotion-plant --path 이벤트.html --title '새 행사' --description '행사 공지' --placement footer
python -m v5 add-page --site ansan-promotion-plant --json-file drafted-new-page.json
python -m v5 scaffold-site --id new-site --brand '가상상호' --keyword '스카이차' --region '안산시' --phone '031-123-4567'
```

Use `--apply` only after changes are accepted for the relevant site. Only validated new pages get a URL. Never fake 500+ for absent pages.

## Production blockers

Configure a real domain/Worker, correct current product links/prices, replace demonstration images and record rights/approval, and review anonymous behavior tracking scope. Then production-specific `build --mode publish`, `audit`, `publish-check`, `prepare-worker` must all pass.

First Cloudflare deployment is explicitly blocked by guarded-deploy because it has no previous version to recover to. Establish an initial validated baseline with an explicitly reviewed first-release procedure before enabling production automation. Do **not** use V4's active Workers as the baseline or restoration target.

After the initial baseline exists, `guarded-deploy`:

- reads the currently active Worker version through Cloudflare's official API;
- refuses a split deployment;
- deploys only the configured Worker via Wrangler;
- reads back public HTML and checks the expected 404;
- on failure tries the exact previous version at 100% traffic, then re-reads the provider version;
- does not claim rollback success without provider confirmation.

This provider flow has local mocking tests but no live V5 Cloudflare verification. API token and account ID come only from GitHub Actions secrets.

## IndexNow

IndexNow is disabled until a domain has a stable key, the public `key.txt` file is accessible and post-deploy readback passes. HTTP 200 or 202 is an API response, **not** search index success. Keep the original accepted URLs in the release manifest and rerun only the missing notification, never automatically redeploy verified HTML solely to retry IndexNow.

## External confirmation still required

- GitHub remote `joseungil-kr/site-factory-v5` did not exist and the connected GitHub tool lacks repository creation. Independent local Git source is bundled for later upload.
- The real Cloudflare V5 Worker/domain and token/account settings are not yet established.
- Browser UI visual inspection could not run in this execution environment: local Chromium returned `ERR_BLOCKED_BY_ADMINISTRATOR`. Local HTTP smoke tests succeeded.

## V5 noindex staging (2026-10-24 addendum)

**The public staging release is separate from production.** Source/test readiness does not imply a Cloudflare deploy occurred.

For the approved Ansan sample only:

```sh
python -m v5 build --site ansan-promotion-plant --mode preview
python -m v5 audit --site ansan-promotion-plant
python -m v5 prepare-staging --site ansan-promotion-plant
npx --yes wrangler@4.148.0 deploy --config deploy/ansan-promotion-plant/staging.wrangler.json
python -m v5 staging-check --site ansan-promotion-plant --origin https://<actual-worker>.<actual-account>.workers.dev
```

The URL in the last line is a **placeholder**, not a verified or deployed URL. Derive the real URL from the authenticated account's Workers subdomain after deployment; do not invent it.

The isolated staging Worker is named `sfv5-ansan-promotion-plant-preview` and has `workers_dev=true`, `assets.html_handling=none` and `assets.run_worker_first=true`. `V5_STAGING=1` forces **HTTP `X-Robots-Tag: noindex, nofollow, noarchive` for all static responses including 404**, alongside HTML `<meta name="robots" content="noindex,nofollow">`, `robots.txt: Disallow: /`, no canonical, no sitemap and no IndexNow. These controls are **not** a password and do not restrict who can read a URL. Do not expose private customer data in staging.

For unattended CI, `.github/workflows/staging.yml` builds, audits, deploys only the staging Worker, discovers the true account-owned workers.dev URL and confirms HTTP 200/404 and noindex headers. It requires GitHub repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. Never copy secrets from V4 into code or chat; configure credentials through GitHub settings/OAuth securely. The first staging deploy is allowed without an earlier Worker version because it is a separate disposable Worker, but production `guarded-deploy` remains blocked until its own safe baseline is established.

For the review surface we now show image URLs from V4's product catalogue as **seller reference thumbnails**, and the three shared SVG hero images are still temporary. Image delivery, permissions, current prices, inventory and usability must be visually checked before any production release. A visible staging warning is rendered on every preview HTML page. External shop links can lead to real order forms; reviewers should not place orders merely to test the UI.

**Current blocker in this runtime:** connected GitHub tools have no `create_repository` action, local execution has no GitHub/Cloudflare credentials and no outbound DNS/network. Therefore remote repository creation, Actions invocation and real staging deployment remain unperformed. A matching create endpoint exists in GitHub's REST API, but that does not grant this chat an authenticated POST action.
