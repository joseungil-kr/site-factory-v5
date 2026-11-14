# V5 local funeral-hall inputs (sanitized derivative)

This is not a byte-identical copy of the V4 workbook. Original V4 files are unchanged.
`SANITIZATION.json` pins the original and derivative hashes and the five removed homepage cells. The six phone-like substrings in those cells have unverified business ownership. No original raw workbook is published here. All other worksheet cell values were compared and retained. The CSV is byte-identical to the pinned source. Collection time and current facility operation remain unknown.

Official provider pages identify unrestricted use; timestamped source receipts are in `../source-rights/20261108/`. This does not verify individual contacts, current operation, prices, or delivery promises. The workbook and CSV are related sources, not independent corroboration.

## Reproduce without V4 or network

From the V5 repository root, using Python standard library only:

```sh
python scripts/import_funeral_halls.py --output-dir /tmp/v5-funeral-new-run
python -m unittest discover -s tests -p test_funeral_halls.py -v
python -m unittest discover -s tests -p test_local_data.py -v
```

Use a new empty output directory. The first command creates facilities.json, facilities.sqlite3, RECONCILIATION.json and hub-plan.json there, never production pages. Large generated databases are not duplicated in Git. Tests reconstruct them in a temporary directory and check SQLite integrity, logical regeneration, 1,080 facilities, source rows and graph consistency. `--check` applies only after outputs have been generated in the script's default local data directory; use the tests for a clean checkout.

The draft hub plan has `publicationAllowed: false`. Its 241 source buckets are not verified nationwide administrative coverage. Source labels require further checking (52 address-label differences and 6 province-only buckets). Original V4 references in source metadata are provenance, not runtime downloads.

## Original recovery

The unmodified original remains at V4 commit `5448bd5f000f1049f9e28b7a56195eca3fa2b74e`, with SHA-256 `c195065efa2bfb686cd56984a86c3d0576a2f8241014515b98be05bd7f69c560`. A separate private Library backup of that raw workbook is not created by this change. If approved later, keep its access private, verify the original hash after restore, and do not substitute this sanitized workbook for an exact-original recovery test.
