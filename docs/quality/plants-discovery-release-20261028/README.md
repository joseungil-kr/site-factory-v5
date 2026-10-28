# Plants production discovery release — 2026-10-28

Status: successfully deployed and verified after explicit user approval for the pending deployment.

- V5 source: `fd1cb9c150db47f86212024ebde94bcf78f60732` (fix/plants-discovery), based on exact old operating source `7776376adde782f78fd127dfb9b8377aa32f657d`.
- V4 deployment controller: `ee0c28b367cad259207d667ba5cdf7f2b3990fc6`, branch ops/v5-isolated-staging-20261024.
- Only .github/workflows/v5-plants-naver-index.yml changed in that controller commit: source pin and existing-body/sitemap/static-link assertions.
- Run https://github.com/joseungil-kr/site-factory-v4/actions/runs/40710560235 — success.
- Worker: sfv5-seoul-gyeonggi-plants-preview; version `8128e97b-c37f-4576-aaf4-a6c2f2fa6429`.
- Exact-host indexing remains on plants.nalmada.net; workers.dev remains noindex. publishEnabled remains false; DNS and secrets/permissions unchanged.
- Deployment tests: 50 Python tests plus existing Worker tests and audit passed.
- All 3,465 contentHashes (home plus 3,464 details: intro/sections/FAQ/title/region/product SKUs) match the previous successful production manifest. Same file inventory; every non-HTML asset hash and sitemap hash preserved.
- Sitemap: 3,467 URLs; SHA256 `d01cc639726959f955846216c1e0da4a3af9fd445da892b812e5cf6466aad7b4` unchanged.
- Independent public full readback: all 3,482 normal files returned 200 and matched deployed manifest SHA after recognized edge-beacon normalization. Every normal HTML canonical/index-follow was checked. The error-document file is excluded from the normal-200 count; a fresh missing URL separately returned 404/noindex. Zero failures.
- Home static list contains all 3,464 existing detail URLs. Home normalized SHA256 `7f84b8efa411bba5338854a18bb40536ee5747ab3a1c92b2c10bc239a3395502`.
- No IndexNow or sitemap resubmission was performed for plants. Search indexing/ranking not confirmed.

Separate V4 foundation run 40710560242 failed on the historical substantive-QA `.gitattributes hash mismatch`. Its immediately previous run 40679664005 failed with the same assertion before this one-file workflow change. This is not a passing check and was not weakened; the dedicated deployment, V5 tests/audit, and public readback all passed.

The earlier local-only/pending-deployment notes are historical. This evidence records the subsequent authorized production release.
