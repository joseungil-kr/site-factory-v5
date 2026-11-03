# Wallsky RSS release

Base 5d4dda2d0e387ce0548e62d618097587add0424f matches every current public HTML page (5197) and the facade WebP. Existing Worker sfv52-wallsky active version 3332fd5c-95ae-436b-a028-6faed2eb4753 must match again before release.

RSS reuses v5/rss.py from 94db74d90e999fd19cf33716a6c2c7ee1a588d52, generates on the existing public build, includes 50 complete main bodies (1326963 bytes), absolute own-host URLs and stable guid. All undated pubDate fields are omitted. Full sitemap, prices, content, images, ownership files and indexing policies are preserved. Preview RSS is 404 and discovery is stripped; public RSS receives RSS MIME.

Validation: 73 Python regressions and 6 common Worker tests; extended Wallsky adapter/RSS/preview test; full 5197-page static audit and 46748 internal links; preserved 270140 internal and 90272 cross-Daysky comparisons passed (maximum 0.352691 / 0.220314). No audit thresholds were changed. Deploy only through guarded existing V4 release credentials, snapshot and exact-host readback.
