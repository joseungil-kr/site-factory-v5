# V5 local-data independence, 2026-11-08

## Directly checked and changed

Base: V5 f85b9c0bebc67c16acf8ed5cfcd933a424390183. All 52 source blobs under v5/, scripts/, .github/workflows/ were inspected. No V4 repository runtime download was found in this main-tree code. Historical origin strings, region matching metadata, and daysky bound-host safety guards are preserved.

Existing V5 region ZIP and parent/candidate JSON copies are reused, not needlessly imported again. `data/local-data-manifest.json` pins bytes and SHA-256. `v5/local_data.py` verifies local inputs and fails on missing/tampered files without any network fallback. The dependency checker and readiness checker now default to the existing V5 ZIP rather than require an externally supplied V4 copy. Official input counts: 53,403 rows, 20,560 live rows, 4,632 locality records, 284 parents; historical candidate file: 5,034.

Funeral sources and importer/tests are copied from V4 5448bd5f000f1049f9e28b7a56195eca3fa2b74e with explicit sanitization. Five homepage cells containing six unverified contact-like substrings were cleared; all other cell values were compared equal. Original V4 workbook remains untouched and is not uploaded into V5. The derivative is 332,696 bytes, SHA-256 10b9ce07ea1af16938403b494ea39328394f19767fadc79516afdeeb8ff966be. CSV original SHA-256 bc085c0de54b22d649dea260602ef9a95639f46f3a549d26cb16558f7398bb1c is retained exactly. Official license-page receipts support unrestricted use; collection recency and contact ownership are separate unknowns.

The importer creates a local SQLite database and JSON exports from committed V5 inputs in a new empty isolated directory. It creates no HTML and performs no deployment. Eleven targeted tests passed, including network-disabled builds, 1,080 facilities, 2,160 source rows, 229 aliases, 10,571 agreeing comparisons, 229 name differences, SQLite integrity and logical rebuild. The 1,338-node draft graph has 2,674 edges and no orphans/broken links. This is data reproducibility, not approval of public pages or current facility facts.

## Not global V4 dependency zero

The new V5 offline data/reproduction path needs no V4 network access. Existing V4 ops workflows remain unchanged and still control legacy production deployments. Skyquote's old workflow consumes a V4 ZIP; Todayflower/Clinic use fixed V5 source/artifact inputs from V4 workflow control; Hallflower already reads a frozen V5 dataset but its release workflow is V4. These are not migrated by this commit. Production migration needs a separate explicitly scoped operation. No existing site, Worker, DNS, credentials, permissions, or active workflow was changed.

Evidence: data/local-data-manifest.json; data/funeral-halls/SANITIZATION.json; data/funeral-halls/sources/MANIFEST.json; data/source-rights/20261108/*.json; docs/V5_LOCAL_DEFAULT_READINESS_20261108.json; tests/test_local_data.py; tests/test_funeral_halls.py.
