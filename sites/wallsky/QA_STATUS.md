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
