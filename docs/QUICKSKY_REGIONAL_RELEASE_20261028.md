# Quicksky regional release

The owner's 2026-10-28 05:31 UTC instructions replace the temporary home-only
publication criterion: publish documents passing the existing similarity rule,
and correct administrator-controlled non-security search restrictions.
Do not add an unmeasured regional-utility veto. Correct concrete factual errors.
The existing phone, Seoul/Gyeonggi consultation scope, exact photo permissions,
and custom-domain ownership evidence remain applicable.

Direct AM02 execution against source 01a01c65b26ae3cc85568da88b9fec51a2e3990e:
1733 documents, 19 seeded Seoul/Gyeonggi stratified samples compared to every
other document (32,908 comparisons), maximum 0.44809, exclusive threshold 0.49,
zero exact body duplicates and zero threshold violations. This is the existing
1% sample-versus-all rule, not exhaustive all-pairs and not a Daysky comparison.
Metric: whitespace-stripped, lowercased character-5gram set Jaccard over intro
and section paragraphs. FAQ/navigation/template text are outside this metric.

`python -m scripts.prepare_quicksky_regional_release` reruns this audit, validates
existing home factual evidence, then creates the explicitly scoped public build.
The checked-in home-only configuration is retained for regression/rollback;
temporary release config is restored even if the build fails. Product checkout
publishing stays disabled. No security permission or DNS change is involved.

Every generated content page must have index/follow and one self-canonical;
sitemap must contain exactly 1733 unique expected URLs. 404 remains noindex.
Only the homepage has the existing Naver verification tag. The existing public
IndexNow key file is preserved without submitting URLs. Existing bound Worker
uses V5_HOME_ONLY=0, while workers.dev and error responses remain blocked.
Live checks sample home, first/middle/last regional pages and missing page,
and verify sitemap, robots and key. Search engine indexing is not guaranteed.
