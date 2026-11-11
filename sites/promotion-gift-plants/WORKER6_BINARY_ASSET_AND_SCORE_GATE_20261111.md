# Worker6 2026-11-11 approved raster transfer and review gate evidence

## Local verified original assets
- `/mnt/data/a_bright_softly_lit_modern_office_desk_still_lif.png`: SHA256 `e6072f37dfd7e05957ae3421cb7cc11aa6f6b1b9100a908e374724549414f872`
- `/mnt/data/a_bright_softly_lit_indoor_desk_office_scene_in_a.png`: SHA256 `f0773b3dacf36405d2c0d2765c6f456cc4002646a14ccc109b15259dcbe5bd84`
- `/mnt/data/promotion-gift-plants/a_bright_softly_lit_modern_office_desk_still_lif.webp`: SHA256 `6c75e9c0f5b31c200812187276f59370ea1d59d441ca3bfed1810843636a2482`
- `/mnt/data/promotion-gift-plants/a_bright_softly_lit_indoor_desk_office_scene_in_a.webp`: SHA256 `5d9e359054e9aba0241cd8d7413099a81477e3305d6198eaebde7091caa8011f`
- ZIP `/mnt/data/worker6-generated-raster-handoff.zip` includes two WebPs (44,880 and 41,926 bytes) and manifest. These match `illustration-provenance.json` recorded hashes.
- Previous user permission applies to the two original generated images as **non-product** illustrations only; visible caption `연출 이미지 · 실제 판매 상품 사진 아님`. No permission to substitute product images.

## Binary transport blocker
- Connected GitHub `create_file` / `update_file` accept **UTF-8 text** only, internally encoding it to base64. Passing a pre-encoded WebP string would store ASCII base64, **not a WebP**.
- GitHub `create_blob` supports `encoding=base64` and is the correct binary object API, followed by `create_tree`, `create_commit`, and `update_ref`. However the connected GitHub action accepts an in-memory string only; it has no `container_path`, `file_uri`, or local byte-stream parameter. The original 44,880+41,926-byte binaries are available in the local container but not as a tool binding inside that GitHub action. No binary transfer was attempted with altered bytes or an unapproved external upload.
- Therefore **no new binary blob, tree, commit, remote image, HTML image element, HTTP image-load or image screenshot PASS is claimed**. Image count remains zero until exact binary upload succeeds. New `worker6_illustration_integrity.py` fails closed on missing/mismatched exact SHA and on zero-img or missing disclosure HTML. Its fixture unit tests are not a real asset-load test.
- Supported next path requires a GitHub binary upload bridge that can read the verified local file and send base64 to `create_blob`, or authorized git push from a local checkout. Never use a re-encoded or unrelated image to meet the check.

## Worker6-specific editorial minimum
- Original worker6 handoff message `036f5fa5-a3c0-4e02-8671-cd23bfac8dab` explicitly sets 85-point PASS and 1% purpose sample. `v5/review_gate.py` now uses 85 only when `site.id == promotion-gift-plants` and `targetPageCount == 5302`. All other sites stay at 90. Tests cover 84.99/85/89.99/90 and boolean scores. 49% Jaccard audit unchanged.
- Passing tests proves guard structure, not actual 5302-page editorial quality or source truth. Preview noindex and no canonical remain intended. No production release.
