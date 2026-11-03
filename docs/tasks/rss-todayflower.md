# Todayflower RSS preserving the actual runtime public view

Current Worker sfv56-todayflower-preview uses the exact 0ca5705aa12950da571f089b2d4ac7256111f77e preview artifact and converts metadata only on todayflower.nalmada.net. GET inventory confirmed active 79e425cf-2592-40ec-a55b-7ad383d132f1, assets-only ASSETS binding and existing preview flags true. All 5070 current public HTML plus ten image assets matched the exact original runtime rendering before RSS changes.

Original GitHub artifact 13036248347 was downloaded through the supported GitHub connector; ZIP SHA-256 16b52597fe77b0b4311ea21ad5daf6c5193af94346f8dc8df9834e676003a180. Existing 5087-file manifest hashes and 5070-page preview scope are enforced on every build. The adapter is copied from the existing V4 public-release workflow and never regenerates national content or modifies preview source HTML, plan flags, images or prices.

Automatic RSS generation uses a separate public-rendering mirror, then copies only RSS XML to the deployed preview assets. The existing public-only Worker inserts discovery in the public head and serves RSS MIME; preview RSS is 404 and preview HTML remains byte-for-byte original/noindex with no discovery. Shared v5/rss.py is reused from 5717b1297ed0efc8ff569d8a2ecde21a925ea228. Feed has 50 complete bodies, 2123436 bytes, stable own-host guid/URLs and no fabricated dates. Three XML/full-body/implicit-head tests and the real runtime metadata/RSS/preview Worker test passed. Final full artifact/public-view build and XML field verification passed.

Existing V4 Todayflower controller and its existing permissions/credential path are retained; no new secret, role, service, Worker or DNS change. Public sitemap and homepage Naver tag d970eeb70abc7b36cbcc02fadd9362c5c57fcb46 are preserved.
