# Site Factory V5 verified execution report

Date: 2026-10-24 KST.

| Stage | Output | Result | Limit |
|---|---|---|---|
| A | independent local Git baseline, site configuration, source provenance | Pass: foundation tests | GitHub remote not created |
| B | Ansan promotion plant 10 numbered pages + estimate/delivery utilities | Pass: QA and 45 pairwise source prose checks | reference product prices/images only |
| C | global edit, additional pages, footer links, local snapshot and restore | Pass: old source content SHA preserved | site files not published |
| D | immutable release naming and failure quarantine | Pass: regression test caught collision, fixed by release-file hashes | local only |
| E | Workers exact `.html` routes, missing file 404 and publish gates | Pass: Node + Python test, official config referenced | no live domain |
| F | guarded provider version/rollback, readback and IndexNow | Mock-tested + guards working | no remote integration; first release blocked |
| G | site search, 3 designs, site-specific scaffolding, opt-in aggregated telemetry | Pass: isolated local tests | analytics off, no browser screenshot |

## Latest code verification

Verified local Python tests: 31 passed; Node Worker route/aggregate tests: 3 passed.

Run `python -m unittest discover -s tests -q` and `node --test worker/*.test.mjs` after checkout. Separate localhost HTTP test is in `tests/test_stage_http.py` and runs as part of the Python suite.

`python -m v5 audit --site ansan-promotion-plant` stores file and link validation evidence in ignored `reports/`.

Attempted local browser visual smoke using Playwright and installed Chromium did **not** pass because browser navigation to localhost was blocked by the execution environment (not a site-generated 404). The test remains optional in `tests/browser_smoke.py` for later execution in an allowed environment.

## No changes outside V5

The `site-factory-v4` repository was only read through the connected GitHub connector and not modified. No Cloudflare API write, production deploy, DNS change or IndexNow submission was attempted.

## Next autonomous step when external connection is available

Create a private `site-factory-v5` repository in the owner's GitHub installation, push/import this reviewed source bundle, enable only the non-deploying check workflow, read back commit SHA and Actions outcome. Keep preview noindex until valid domain and real-product assets are approved. Actual release automation is intentionally fail-closed.

At 2026-10-24 (public page read only), D144 금전수 탁상용 was individually verified to show SKU D144, 53,000 KRW and purchase button. Other SKU records still await independent current validation.
