# Public build preparation (not deployed)

Build from the repository root: `python -m scripts.build_webbuilder --mode public`.
Default `--mode preview` preserves the existing protected preview and its QA.
Both modes use the same 42 content pages, 404, copy and five WebP assets.
Public mode emits 42 self-canonical URLs and sitemap entries, and allows crawling.
404 stays noindex and is omitted from the sitemap.

The existing preview entry/config/workflows are unchanged. A later approved public
deployment must explicitly select `worker.public.js` and the public build assets.
The public handler indexes successful content only on `webbuilder.nalmada.net`;
other hosts strip canonical/index metadata, block robots and return 404 for sitemap.
Direct `/404.html` and unknown paths return HTTP 404. No DNS/routes are configured here.

Local checks: `python -X utf8 -m unittest tests.test_webbuilder tests.test_webbuilder_public`
and `node --test tests/webbuilder-worker.test.mjs tests/webbuilder-public-worker.test.mjs`.
Body equivalence, all five image hashes, 42 sitemap URLs and preview restoration
are covered. Existing build QA checks 614 internal links and pricing constraints.
VAT, contract and maintenance details remain consultation items; no new promise is added.

2026-11-01: browser navigation to local port 8768 failed with
`net::ERR_CONNECTION_TIMED_OUT`; fresh mobile visual verification is pending.
No deployment, DNS, Actions, credentials or billing changes were performed.
