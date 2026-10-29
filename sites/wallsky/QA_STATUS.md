# Wallsky review handoff — updated 2026-10-28

## Source and provenance

- Original archive: `wallsky-handoff-d5351e3.zip`, 1,519,243 bytes, SHA-256 `b31656dce752bd4052399c858afee1981720e33865d16c1a9312d66d5ae8d951`.
- Local original commit in archive: `d5351e36d95d231a7d853ef19756b357c2551753`; implementation commit: `089b2175bf96a402045ab448f46c626956d64a2e`. Neither is claimed to be a remote commit.
- Remote main baseline: `d4f58c660655afc5f8359fe0fa70b98fc7588309`.
- Current remote Wallsky branch: `feature/v52-wallsky`. It now contains the dedicated spec, benchmark, source pool/ledger manifests, isolated Worker/config, build/QA/HTTP scripts and tests. No main merge or Cloudflare change yet.

## Actual GitHub Actions evidence

- [Run 40711586641](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40711586641), completed success at commit `35a13510123e5c5f0d352ac85668d7ff53ffe7eb`.
- Built 5,197 URLs (5,196 region-intent pages plus home); reserved `404.html`; final detail `5198.html`.
- Static QA checked all 5,197 sitemap HTML URLs, all canonical/robots/H1/title retention/image existence+alt/phone links/forbidden copy and 46,748 internal links; errors 0.
- Seed 20261028: 52 sampled Wallsky pages versus all 5,196 Wallsky pages, 270,140 comparisons, whitespace-free character-5gram Jaccard maximum 0.355586 (<0.49), exact duplicate bodies 0. This is seeded 1% sample-to-population QA, **not all-pairs proof**.
- Worker isolation tests passed; Python 72 tests and Node Worker 6 tests passed.
- Local HTTP test: 5,201 resources checked, errors 0, missing route 404. This is a local static server, not production Cloudflare HTTP.

## Source scope / truth boundaries

- Region input is the pinned V4 `NAME_CANDIDATES` snapshot from 2026-10-12. It contains 1,732 names but is not independently classified as all legal/administrative dongs. It does not establish that each facility exists or that a vehicle can dispatch there.
- Site purpose is equipment access support for building/factory/store exterior tasks. It does not claim professional waterproofing or painting, completed regional jobs, specific fleet ownership, or guaranteed dispatch time.
- Existing user-provided phone `010-5322-1952`, Seoul/Gyeonggi consultation scope and approved shared worksite image are reused from V5. CTA is tel-only; no call or lead submission was performed.
- Benchmark sources and observations are in `sites/wallsky/BENCHMARK.md`; competitor wording/photos/prices/vehicle claims were not copied.

## Still not done

- Current live Cloudflare binding/zone/DNS/routes preflight for `wallsky.nalmada.net`.
- Production Worker deployment, all-5,197-URL live HTTPS/canonical/robots/sitemap checks and public visual readback.
- IndexNow submission. It must use an existing authorized key only after public HTTP checks; do not create a new key or Secret.
- Google/Naver submission belongs to the parent registration owner; do not duplicate it.

## Safety

The existing dedicated Worker defaults to noindex and only enables indexing for exact host `wallsky.nalmada.net` when `WALLSKY_PUBLIC=1`; workers.dev and 404 responses remain noindex. No DNS, Secret, OAuth, permission or existing site/Worker mutation has occurred in the V5 branch work so far.

## Actual remote preview update — 2026-10-28 15:23 UTC

- Latest Wallsky source HEAD: `8d5e316732b40cd385ea24575a73860602654f3a`.
- V5 run [40714749737](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40714749737): passed after fixing the Worker to forward non-root asset requests unchanged; Python 72 and Node Worker 6 passed. Artifact [12826224590](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40714749737/artifacts/12826224590), 10,590,531 bytes, includes the 5,197 review HTML files and QA reports. ZIP SHA-256: `04b6822eebc558a9e062422b0977bd6d97ef5cd82f423c4a039f6d8aeebe192c`.
- Existing V4 success-path run [40715062374](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40715062374): dedicated Worker `sfv52-wallsky` deployed to `https://sfv52-wallsky.joseungil.workers.dev`; all **5,201 live resources** passed, errors 0, missing route 404, noindex headers/meta and preview robots verified. Existing 84 custom-domain bindings were unchanged.
- Preview live report artifact [12827483600](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40715062374/artifacts/12827483600), 10,584,021 bytes. ZIP SHA-256: `e505679d6186e30a2badf728d3a73b1e93e8b55c990080b16b8fa0d695ce534a`. It contains `dist/wallsky`, `reports/wallsky/qa-public.json`, `cross-daysky.json`, `http.json` and the read-only binding snapshot.
- Current preview URL: https://sfv52-wallsky.joseungil.workers.dev. This is **noindex preview**, not the requested production hostname.
- Domain preflight: `nalmada.net` zone active in existing account; no `wallsky.nalmada.net` custom-domain binding in the account; DNS/Worker route read returned HTTP 403 for routes, so route collision remains unproven. No DNS, route, custom-domain or permission changes were made. Do not attach production domain until the route conflict check is readable.
- A prior preview run failed because the Worker wrapped every request in `new Request(url, request)`, causing the static-assets adapter to return 404. The proven V5 adapter was adopted: root is rewritten to `/index.html`, non-root requests pass through unchanged. Updated Worker test asserts both paths; latest preview run confirms the fix.
- V4's separate foundation check failed at `scripts/verify_substantive_qa.py` with `.gitattributes hash mismatch`. It did not block the isolated preview workflow and was not modified as part of Wallsky.
