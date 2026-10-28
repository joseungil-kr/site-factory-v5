# Officeplant review and release handoff

Branch: `feature/v52-officeplant`; base `d4f58c660655afc5f8359fe0fa70b98fc7588309`.

## Reproduce

```sh
python -m v5 plan-check --site officeplant
python scripts/build_officeplant.py
python scripts/build_officeplant.py --public
python scripts/audit_officeplant.py
node --test worker/worker.test.mjs tests/officeplant-worker.test.mjs
```

Outputs: preview `dist/officeplant`, candidate public `dist/officeplant-public`; evidence `reports/officeplant`. Building public files does not deploy or submit URLs. Build is deterministic and uses no remote generation API. Whole-corpus paragraph combination constraint is independent of QA sampling: any two regional documents share no more than four of ten selected blocks. QA independently measures actual rendered text, including chrome; report is not all-pairs proof.

82 original topical blocks / 164 sentences cover recipient, placement, budget, ribbon, receiving and seller order flow. Regional pages select ten and preserve topical ordering. No regional shop, equipment, delivery time or transaction history is invented. All pages are reachable from the region directory; regional pages link to the sibling intent and next region. Full target 3,468 content URLs; 404 is an additional file.

## Parent-coordinated deployment only

1. Independently review this branch, evidence, homepage, regional document and helper. Merge order belongs to parent. Shared code was not edited.
2. In the existing authorized V4 Actions context, GET account Worker custom domains and scripts. Match exact candidate hostname and `sfv52-officeplant`. If either belongs to another service, stop and select another owned candidate. NXDOMAIN is insufficient. Do not alter existing bindings or secrets.
3. Use the existing V4 success pattern to checkout the reviewed exact V5 commit. Rebuild and audit. Preview configuration: `sites/officeplant/wrangler.preview.json`; public configuration: `sites/officeplant/wrangler.public.json`. These configs deliberately contain **no routes or custom-domain writes**. Existing Worker stays untouched.
4. First establish this new isolated Worker's noindex baseline and record its deployment/version ID. Then attach only the approved new custom domain after collision check using the existing authorized path. Never use another site's deployment as rollback target.
5. After parent public approval, deploy the public assets to the same new Worker. Record prior version; run live HTTPS validation for every sitemap URL, 404, canonical, robots, images and order destinations. If the new deployment fails, restore the recorded version at 100% and verify provider state and HTTP noindex.
6. Only the exact hostname with `OFFICEPLANT_PUBLIC=1` can be indexable. workers.dev, other hosts and 404 remain noindex. Worker tests cover this. Candidate public sitemap contains 3,468 URLs. Preview has no sitemap and disallows crawling.
7. IndexNow and Naver/Google submission are separate parent steps after public validation. No key or verification tag borrowed from plants/flower/Quicksky. Existing authorized key or parent-approved site key setup is needed; do not fabricate registration success.

## Boundaries

The order helper stores nothing and makes no network request. Only explicit copy writes to the user's clipboard. Recipient data is not put in a URL. External links point to verified seller product pages; customer completes checkout there. Browser tests used synthetic entries and did not call, order or pay.

The generated site has no LocalBusiness address or fake reviews. Region coverage is a consultation/navigation scope, not guaranteed fulfillment. Prices were checked on 2026-10-28 and should be refreshed when the catalogue changes.

## Region ledger serialization reconciliation (2026-10-28)

- The frozen local handoff reports sourceRegionSHA256 `e7788fd6d7fa3fab10699991d82af714c5215967217c2d96bf6650beaf40310f` for its local serialization.
- The actual V5 checkout file `data/regions/seoul_gyeonggi_current_dong.json` is unchanged between main and `feature/v52-officeplant` (Git blob `6de6e5751b26a13a2132238f13633df3de0cd2aa`) and its checkout-byte SHA-256 is `48fb6a7cef914a4ef784478b7284761a84e1dd7dc9d7663215880c3a23a67e18`.
- The 1,732-row ordered list was compared against the frozen handoff's generated regional titles; normalized row-sequence FNV-1a64 matches exactly: `a47540b27d784155`. First and last rows also match. No region ledger was edited.
- The build pin now uses the exact V5 checkout SHA-256, while the frozen local handoff report remains preserved unchanged in the original Library ZIP.
