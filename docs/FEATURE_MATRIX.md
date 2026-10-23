# Site Factory V5 12 features: implementation status

Status: 2026-10-24 local source/build verification. No GitHub remote nor production Worker.

| No | Requested function | Code available | Independently tested | Live production |
|---|---|---|---|---|
| 1 | Global modification engine | Yes, controlled config + rebuild | Yes | No |
| 2 | Utility pages and calculators | Yes, static content and browser calculator | Python/static checks | No |
| 3 | Body/footer link manager | Yes, scoped declarative links | Yes | No |
| 4 | Append pages and preserve existing prose | Yes, append-only ledger and content hash | Yes, including 499 simulated numbering | No |
| 5 | Preview and file diff | Yes, noindex preview and manifest diff | Yes | No |
| 6 | Automated faults and recovery | Local atomic build/zip restore; provider rollback code | Local actual restore + mocked provider | No |
| 7 | Site-specific settings | Yes, independent ledgers and validation | Yes | No |
| 8 | SEO and indexing control | Internal checks, preview SEO guard, sitemap and IndexNow gate | Local only | No |
| 9 | Shared image library | Yes, 3 reusable placeholder SVGs | Yes, physical count and paths | Real photos not yet approved |
| 10 | Phone/shop/calculator behavior analytics | Privacy-gated Worker event and report code | Mocked, disabled by default | No |
| 11 | Multi-site management | Local dashboard and blank-draft scaffold | Yes | No |
| 12 | A/B/C design variation | Three CSS themes, unchanged prose hashes | Yes | Browser visual check blocked |
| Extra | Site-local search | Optional static search index/client | Yes, client bundle inspection | No |

Functional baseline: 10 real generated detail pages, 2 utility pages, 3 shared illustrative SVGs, 22 deployable static files. Body similarity 45 page pairs, maximum 0.02703 (intro+main paragraphs only); this is not a claim about all visible text, search ranking, or meaning diversity.

Known blockers for production: no domain, no remote repo creation action, unverified product inventory, provisional images, privacy settings, missing actual Cloudflare Worker first-release/prod rollback verification. Security-first gating is intentional.
