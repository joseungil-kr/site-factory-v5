# Plants discovery repair — 2026-10-28

Production source: `7776376adde782f78fd127dfb9b8377aa32f657d`, deployed by V4 run 40106955448 (success). The run's manifest root SHA256 `f67564830d2cf81ae0a8a0ec4648cbc2a1f64a548b095db1e11e45d1dfd81864` matches the current public root after removing the known provider beacon.

This isolated branch starts at that exact production source, not the later main branch or any Quicksky source.

Changes:
- Add a bottom, native-details directory to the existing plants homepage. It links all 3,464 existing detail documents, grouped by existing region. No new hub or URL.
- Related documents prefer the current region and nearby document numbers instead of always selecting the first documents. Existing card design and seven-position pagination remain.
- No publication, preview, domain, DNS, account or privacy settings changed.

Validation:
- Python 3.12: all 50 unit tests pass, including two discovery tests.
- Public-indexing build: 3,465 regular pages, 3,483 total files.
- Audit: 3,468 HTML files; 124,804 internal references; zero errors.
- All previous contentHashes match the successful production manifest.
- Same file inventory and exact sitemap SHA256: `d01cc639726959f955846216c1e0da4a3af9fd445da892b812e5cf6466aad7b4` (3,467 URL entries).
- Eight unchanged text assets differ only by Windows CRLF checkout conversion; their LF-normalized hashes match production. Linux deployment should reproduce original asset bytes.

Not deployed. Existing deployment path is V4 `ops/v5-isolated-staging-20261024`, `.github/workflows/v5-plants-naver-index.yml`; it pins a reviewed V5 SHA and targets only `sfv5-seoul-gyeonggi-plants-preview` at `plants.nalmada.net`. Production publishing needs a separately approved exact update to that pin. Browser visual review and post-deployment full HTTP readback remain.
