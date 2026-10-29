# Wallsky handoff receipt

Original Library file: `wallsky-handoff-d5351e3.zip`
- Size: 1,519,243 bytes
- SHA-256: `b31656dce752bd4052399c858afee1981720e33865d16c1a9312d66d5ae8d951`
- ZIP entries: 26 (25 files plus MANIFEST.json)
- Local branch SHA recorded in HANDOFF.md: `d5351e36d95d231a7d853ef19756b357c2551753`
- Local implementation SHA recorded in HANDOFF.md: `089b2175bf96a402045ab448f46c626956d64a2e`
- These two local SHAs are provenance only and are not claimed to exist on remote GitHub.

Important archive file hashes independently recomputed:
| Path | Bytes | SHA-256 |
|---|---:|---|
| `HANDOFF.md` | 1,918 | `a24a938c7ec65a8c5d39cf3007beadc1fbc36bec249976fd08c19f8d6cf9f41d` |
| `sites/wallsky/site-spec.json` | 1,955 | `605955f37346a07584db9eb762516c514f34afad99bb96eeb5520a887c49d446` |
| `sites/wallsky/copy-pool.json` | 28,312 | `f06fad395c36b6f1ffeb3d4887b51f7e6cf1706f7e9a4a8bcb1792e288b0de52` |
| `sites/wallsky/regions.json` | 122,581 | `a34fa05560d3a0567adf895e91a8de002969288277b85aa879944e226864e23c` |
| `scripts/build_wallsky.py` | 13,558 | `e0d05182387920e56eb6dcedea379393ab337dbd7bf411e039211e6e8fae68dc` |
| `scripts/qa_wallsky.py` | 4,339 | `b6d7262d1eb0fef887a9971cdaac3d84a6f7315a2dcd93605dc494b2d23f60a0` |
| `scripts/http_wallsky.py` | 1,784 | `9f1bdf2a264c062bdc9d1b9e56c6c02a8c3ce5cc863278ad965686f275e12220` |
| `reports/wallsky/qa-public.json` | 5,620 | `11b209b565a601b761dc935cb8cabe2173c321063e73b32ec8a9e7c114d4807c` |
| `reports/wallsky/http.json` | 290 | `b246f79cb656f9d55f100e8aa51add7f94b425cff04bdf6c8c9ab67a775ed689` |

The original source tree excluded `.git`, credentials, generated HTML and `reports/wallsky/pages.json`. The remote branch stores the generator and source inputs rather than committing 5,197 generated HTML files. The exact source code in this branch has been adapted to consume the pinned V5 region ledger directly and avoid duplicating its 122 KB data; the original ZIP remains preserved in Library.
