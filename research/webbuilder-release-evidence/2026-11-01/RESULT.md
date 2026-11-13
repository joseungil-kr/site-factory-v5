# Webbuilder public release

- Public URL: https://webbuilder.nalmada.net/
- Reused Worker: generic-skycar-shadow, existing account unchanged.
- Source: f7e836c2c5c4c6d482523e92045a3f66b4fce335.
- Workflow commit: f296cc832 (V4 ops/v5-isolated-staging-20261024).
- Deployment run: https://github.com/joseungil-kr/site-factory-v4/actions/runs/41267538884.
- Deployed version: 097936ef-00b1-457c-a247-1539a8efab94.
- Run status is failure: deploy succeeded, but immediate GitHub runner HTTP probe received 403. No repeat deployment was performed.
- Independent AM02 HTTP verification passed: all 42 sitemap URLs return 200/index/self-canonical; five WebP hashes match approved files; robots allows crawling; explicit and missing 404 pages return 404/noindex; workers.dev remains noindex with disallowed robots and 404 sitemap.
- Actual 390px mobile and 1440px desktop homepage rendered correctly without horizontal overflow. Phone href remains tel:01024900555. Price remains 1,000 KRW/page/month, minimum 10 pages / 10,000 KRW/month.
- Cloudflare Domains UI readback: webbuilder.nalmada.net, Production, zone nalmada.net. HTTPS served successfully without certificate warning.
- Old version backup: a75d5a85-d2fb-445a-8699-37577c3c4c62. Read-only backup run 41267419040 succeeded. Version/settings/deployment and restore command saved in ../generic-skycar-shadow-backup-20261101/api/. Retained old version URL content matched local backup SHA256. Actual rollback was not executed.
- Search registration was not performed during this release; Naver remains awaiting user login.

## Separate regional Worker read-only findings

- Dashboard Workers-only filter: 108 Workers. All applications: 121 (includes Pages), not 121 Workers.
- Account Requests today displayed 1,045 / 100,000 on November 1; not regional-only traffic.
- goyang.fwith.kr currently maps to goyang-flower-guide-qa, plus one additional route indicated; request metric shown as dash, not zero.
- Ten directly observed mappings: damyang, gwangju-gwangsan, gwangju-bukgu, gwangju-namgu, gwangju-seogu, gwangju-donggu, gwangyang, naju, suncheon, yeosu .fwith.kr each map to the matching <prefix>-flower-guide Worker. Their list metrics were dashes.
- Remaining regional full mapping/count, historical registry name comparison, and per-region traffic/static delivery verification were not completed. No regional configuration was changed.
