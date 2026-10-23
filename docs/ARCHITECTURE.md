# Site Factory V5 — Architecture / 기능 명세

Updated: 2026-10-24 KST. Source is an independent LOCAL Git repository until remote repository creation is available.

## Purpose

- ChatGPT starts and describes each approved change; Python standard-library engine produces stable HTML, manifests and audit reports.
- Input is a per-customer set of JSON ledgers in `sites/<site-id>/`.
- M-castle-type detailed pages without geographical or product-category hub indexes; bottom numbering only.
- A site uses physical `index.html`, `2.html`, `3.html`... and only *existing* pages enter the seven-number pagination.
- Site-wide links, footer links and utility pages are declaratively configured; ordinary prose remains independent from presentation.
- Cloudflare Worker keeps exact `.html` paths with `assets.html_handling: none`; only `/` internally resolves to `/index.html`.
- Existence of a file or IndexNow HTTP acceptance is not equivalent to search indexing or ranking.

## Data model

`site.json`: brand, site id, order-origin, phone, topic, theme, image pool, cloudflare target, SEO and privacy gates.

`pages.json`: stable `id`, monotonically numbered `number`, verified region, manually reviewed topic and content blocks, SKU references. Raw content is kept separate from footer, navigation and layout.

`products.json`: supplier SKU, name, order URL, reference price/date and `verifiedLive`; all supplier order targets are constrained to configured origin.

`links.json`: source-independent link registry with `body` / `footer` / `both` placement and scoped page selectors.

`special-pages.json`: dedicated `content` or `calculator` page definitions. Page paths are strictly validated and can use Korean names.

`regions.json`: per-site region master. New sectors can add their own verified region inventory. V4 full current-dong dataset is not yet imported into the V5 repository.

## Modules

| Module | Responsibility |
|---|---|
| `config.py` | input whitelists, URL safety, cross-references, production domain guard |
| `markup.py` | deterministic detail/special/404 pages, links, pagination, theme styles |
| `engine.py` | atomic staging, image reuse, preview/publish modes, snapshot manifests and content SHA |
| `audit.py` | internal links, images, static artifacts, `noindex`, title/H1, content similarity |
| `operations.py` | opt-in global edit, special page creation and append-only page records |
| `release.py` | checked release archive and local restore |
| `deploy.py`, `cloudflare.py` | guarded Workers release config, previous active version, failed-readback rollback |
| `publiccheck.py` | live site HTTP and content/404 checks, read only |
| `indexnow.py` | verify public key, split URL batches and submit only after public readback |
| `dashboard.py`, `scaffold.py` | customer draft scaffolding and local overview |
| `analytics_report.py` | optional aggregate action counts; disabled until privacy review |

## Safe change sequence

1. Inspect site settings and previous manifest. Do not change V4 or other sites.
2. Create a proposed JSON change with a dry-run (`--apply` omitted).
3. Apply only the expected source ledger changes, then run tests.
4. Build a complete new static release in a temporary directory, audit it, compare old/new file SHA and prose SHA.
5. Only if all required gates pass, replace old local preview; retain recovery archive.
6. Release to Cloudflare **only** when public domain and other production gates are satisfied. Keep previous Worker version, read back public pages and attempt rollback on failed public check.
7. Submit IndexNow only after live readback and verified public ownership key. A notification failure is not a reason to roll back a valid site.

## Security boundaries

- Never read or copy V4 API token values into repository text; Cloudflare token and account id are environment secrets.
- No public deployment from a draft or missing domain, unchecked product or placeholder image.
- The user must review privacy and measurement arrangements before enabling Analytics Engine collection.
- Escaped content, strict local paths, controlled product hosts, immutable snapshots and 404 allow deterministic recovery.
- `preview` emits `robots.txt: Disallow: /`, page-level `noindex,nofollow`, no production canonical or sitemap.
- Worker telemetry only records an action category and path when explicitly enabled; never submit form text, names, phone numbers, IP addresses or URL queries.
- No background agent or AI API is needed for the build itself. The connected ChatGPT-GitHub tool currently cannot create a new repository or dispatch GitHub Actions, so production orchestration requires additional integration.

## Limits and nonclaims

- Offline tests confirm code behavior; Cloudflare remote deploy/rollback, automatic index requests, visual browser rendering, product availability, order processing and live measurement have not been verified.
- Python `unittest` and Node Worker tests are implemented; optional browser smoke requires permitted local Chromium and Playwright.
- Diff content SHA excludes generated navigation; the final HTML SHA includes navigation and is used for immutable release IDs.
- The 18,000 static file default is a *self-imposed* Free-plan safety budget; the published Cloudflare Free ceiling is 20,000 per Worker version.
