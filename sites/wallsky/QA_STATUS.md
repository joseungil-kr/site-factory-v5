# Wallsky review handoff — 2026-10-28

PLAN / POOL / GENERATED / LOCAL_QA were reported complete in the local worktree. The archive preserves the original outputs and local commits. DEPLOYED / LIVE_HTTP / INDEXNOW were not executed in the original handoff; this is not a claim of finished public launch.

## Checked in the supplied local reports

- 1,732 pinned Seoul/Gyeonggi region-name rows from the V4 `NAME_CANDIDATES` snapshot dated 2026-10-12 × three intents + home = 5,197 canonical URLs. These names have not all been independently classified as legal dong vs administrative dong and do not prove facility presence or dispatch availability. Numeric detail filenames reserve `404.html`; final detail is `5198.html`.
- Entire static HTML population: canonical, robots mode, one H1, regional title/intro retention, image existence/alt, phone links, forbidden copy and 46,748 internal link targets. No errors were reported in the public or preview build.
- Exact sitemap set equals all intended URLs. The 404 error asset is noindex and excluded from sitemap/population.
- Seed 20261028: 52 regional documents (1.00077%) compared against all 5,196 regional documents, 270,140 comparisons. Whitespace-free character-5gram Jaccard maximum 0.355586 (<0.49). Exact duplicate regional bodies 0. Scope is intro+four paragraphs, excluding title/navigation/shared conversion block. This is not full pairwise or semantic uniqueness proof. Home is separately inspected.
- Same 52 body samples against existing Daysky's 1,736 documents: maximum 0.182156. Other concurrent V5-2 sites were not included.
- Browser screenshots: home and building detail at 1440×900 and 390×844; factory at desktop and store at mobile. Existing screenshots inspected in the supplied archive. Viewport/scroll width matched, images loaded, CTA pointed to `tel:01053221952`. No calls/submissions were made.
- `node tests/wallsky-worker.mjs`: intended-host indexing isolation, preview robots, root translation and unknown-path 404 noindex were reported passed. Python compilation and plan-check were reported passed.
- HTTP readback script is intended to check all 5,197 HTML and four resources, plus missing URL 404. The saved report targets local server; actual Cloudflare behavior is not thereby verified.

## Supplied local evidence

`reports/wallsky/qa.json`, `qa-public.json`, `http.json`, `cross-daysky.json`, `manifest.json` and six PNGs are in the handoff ZIP. The ZIP deliberately excludes generated HTML and `reports/wallsky/pages.json`. These are historical local observations, not newly run tests in this chat.

## Known limitations / exact pending action

No Cloudflare account binding/route inspection or live production HTTP test is included. Need independent code review, merge coordination with other V5-2 sites, binding preflight, public deployment, live HTTP and IndexNow.

The prior automatic approval review denied the source-only push and a proposed workflow for continuous remote artifact upload before execution. The recorded reason was insufficient explicit authorization for sending the business phone/content to the named GitHub destination. No bypass was attempted. The user has now explicitly designated the repository and requested Wallsky creation/publication; the normal GitHub write path is being tested against that updated authorization. No alternate upload path, secret access or permission expansion is authorized.

The original local commits remain preserved in the handoff archive. This document does not claim that the local SHA is present on GitHub.
