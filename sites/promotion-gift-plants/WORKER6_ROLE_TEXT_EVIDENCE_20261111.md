# Worker6 2026-11-11 role-separated D144 source preview evidence

## Actual CI
- Workflow run 43012314467: success; 4 unittest PASS, 6 isolated local HTTP routes and their internal links 200.
- Artifact 13851197414: `index.html`, `guide.html`, `1.html` to `4.html`, `manifest.json`.
- Only a text/link preflight, not 5302 regional HTML, 49% Jaccard, editorial 85, screenshot, or image PASS.

## Source and scope
- Source candidate `data/regions/nationwide_locality_candidates_5034.json`: 5034 names, flag=0 means parent unmatched to V4 upper code master, not invalid locality.
- V4 `data/regions/master.json` comes from `code.go.kr` official legal-region code export (retrieved 2026-10-22), but it retains **active upper levels only** and does not provide a safe exact current lower 읍면동 key for all 1480 unresolved seller alias matches.
- 1480 `jurisdiction-unresolved` from the earlier shipping lookup is a seller-province-alias match failure, **not equivalent** to 1438 V4 parent-unmatched source flags. These sets must not be conflated. No province aliases inferred and no fuzzy matching performed. Existing official master cannot by itself justify resolving all 1480; a verified current exact key mapping would be required.
- Seller `seller-shipping-raw-rows.json` is a **D144 product-page** shipping table, checked 2026-11-09. `worker6_shipping_render.lookup()` already distinguishes `district-display-only` (776 candidates), `exact-locality-display` (87), `overlap-unknown-priority` (10), and other unknown states. These are source-match states, not delivery coverage. New preview displays the actual raw row text and its ID, SKU D144, checkedAt, product name/price/order URL. It never states the final surcharge, precedence, local inventory or same-day guarantee.
- Non-D144 SKU gets `sku-source-unverified` and **no D144 fee rows**, even if the SKU appears in the shared product catalog. A product catalog entry is not a shipping-policy license.
- Page roles: common buyer guide at `guide.html`, region navigation at `index.html`, four evidence-specific region detail pages `1.html`–`4.html`. This avoids representing identical generic buyer guidance as thousands of locality-specific facts.
- No images, external file access, Cloudflare, deployment, DNS, security, production pages or indexed content modified.

## Diff
- `scripts/worker6_role_text_preview.py` isolated renderer (not production).
- `tests/test_worker6_role_text_preview.py` 4 unit regressions.
- `.github/workflows/worker6-role-text-preview.yml` local HTTP link traversal and artifact.
- Original 5302 generator and 49%/85% gates unchanged.
