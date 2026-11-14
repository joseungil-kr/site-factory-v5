# Site Factory V5 — Clinic 3-host national static release

## Scope and restrictions

- Reuse exactly one existing Worker `sfv5-nalmada-domain` for the three new hosts `clinicflower.nalmada.net`, `clinicopen.nalmada.net`, `clinicpresent.nalmada.net`. All other `nalmada.net` sites and their Workers remain unchanged.
- Content: clinicflower = clinic opening plant selection; clinicopen = opening-day event plant handover; clinicpresent = opening celebration **wreath** (not a potted-plant recommendation).
- Source: **exact V5 Git blob** `data/regions/nationwide_locality_candidates_5034.json` SHA `525eb4b5c9f9f046ce2bcbd96a3dcfb343be399d` and original 720-block clinicflower pool.
- Region rows: **5,034 all included** even if 1,438 parent names do not match the pinned V4 parent table. No invented local business, florist branch, hospital, venue, shipping deadline, stock, or price. The locality inventory is a historic candidate-name list and is not contemporary legal/administrative status verification.
- Each site: 5,034 regional HTMLs at `/r/00001.html` to `/r/05034.html`, 250 district hubs, 17 province hubs, one home = **5,302 HTMLs**. Three sites combined = **15,906 HTMLs**; expected 15,924 static assets including shared CSS/WebP and per-host robots/sitemap/RSS/IndexNow key.
- Every document has inbound navigation from the district/province/home index; all site-local `href` targets and every sitemap canonical are checked. No `indexnow` POST before actual public HTTP readback.
- Uses original AI images from the already-deployed Clinicflower preview on the first two sites. Clinicpresent must not represent those potted-plant images as wreath product photos.

## Copy pool and audit semantics

- Historical original source: **720 blocks** (`sites/clinicflower-preview/clinicflower-copy-pool-720.json`), kept unchanged.
- Additional **6,080** deterministic **compositional variants** from hand-authored generalized medical-flower guidance cases, context-specific perspectives and discourse structure. This is NOT 6,080 independently researched local facts and not a search ranking guarantee. JSON saved as a build artifact, outside public Worker assets.
- Internal metric: `visible narrative + title + description`, five-character shingle **set Jaccard**. Seed-fixed 1% of **15,102** region details vs all 15,102 region details (including cross-site) with no self comparisons. Target `< 0.49` with observed maximum, fail count, sample population and exact method reported. First synthetic-region regression passed but **real region source is independently audited on CI**, so no public deploy until real audit PASS.
- Homepage and hub pages are checked for exact count, unique canonical, orphan status and actual sitemap membership, separately from numeric prose similarity sampling.
- Similarity is only an internal mechanical QA signal. Locale variants of generally similar pages can still be considered thin/doorway content. User has asked to publish; no guarantee of indexing, discoverability or ranking.

## Build in a checkout of the V5 branch

```sh
python sites/nalmada-shared3/build_national.py --root . \
 --output dist/clinic-national-20261104 --mode public \
 --audit-json reports/clinic-national-build.json
python sites/nalmada-shared3/qa_similarity.py \
 dist/clinic-national-20261104/narrative-only-audit-input.json \
 --output reports/clinic-national-similarity.json
# Build produces dist/clinic-national-20261104/{wrangler.json,worker.mjs,public/}.
# Actual Cloudflare deploy and IndexNow are limited to guarded GitHub Actions after all checks.
```

## Release gate

- Confirm the exact existing `sfv5-nalmada-domain` active version, and three custom domain bindings. Protect current Worker 100% deployment and forbid any change to other domain mappings.
- Full source-row count 5,034, province 17, district 250, parent match 3,596/unmatched 1,438, no lost rows.
- Full generated pages 15,906, all assets <= 18,000, no orphans or internal broken links.
- All 15,906 canonical/robots entries per host correct, exact `sitemap.xml` 5,302 URL per host and RSS 50 items per host, no fabricated publication times.
- Output Worker HTML routes are host-specific; workers.dev/unknown hosts return 404 + noindex.
- Inspect all images, telephone links and normal browser 390/1440 representative pages.
- Only after 3-host public HTTP 200, all sampled pages index/own canonical, sitemap/RSS/robots/IndexNow key 200, send one IndexNow POST per host (5,302 URLs each). Separate receipt for HTTP accepted vs search engine indexed (not equivalent).
- Retain previous Worker deployment ID and snapshot. Do not make a blanket domain/DNS/zone routes change or delete a Worker.