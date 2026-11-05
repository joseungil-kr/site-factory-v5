# Quicksky homepage-only IndexNow receipt — 2026-10-27

- V5 deployed source: `14380e4359d823a97bded89c9433c48fcea1c031`.
- V4 workflow: `6431585f128a4478ce7a310a6b8a067eaba8bd15`.
- [Run 40545319383](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40545319383): completed/success.
- [Live receipt and binding evidence](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40545319383/artifacts/12751508303), including `quicksky-home-indexnow-receipt.json`.
- [Build evidence](https://github.com/joseungil-kr/site-factory-v4/actions/runs/40545319383/artifacts/12751683108).
- Public verification file: https://quicksky.nalmada.net/aa9e721adc0a465c9e244cb64db948b9.txt — checked HTTP 200 and exact key content before submission.
- Submitted exactly once: `https://quicksky.nalmada.net/`.
- Actual response at 2026-10-27T16:55:02Z: **HTTP 202, received-key-validation-pending**. This is not HTTP 200 confirmation, completed ownership validation, or evidence of search indexing. No automatic retry was performed.
- Homepage index/canonical, sitemap exactly one URL, representative regional HTTP/meta noindex, preview noindex and 404 all passed the existing live verifier. Build checked all 1,732 regional pages remain noindex.
- All **83** custom-domain mappings before/after this run were identical. The earlier 82 count predates a separate Onehour binding; this run did not add or change bindings.
- `publishEnabled=false`, `publicIndexingApproved=false`, general `indexNow.enabled=false,key=null` unchanged. A separate explicit home-only script owns the public key and one-URL request.
- Six local safety tests passed; release ran full Python/Worker regression tests successfully.
- Prior run 40544837117 stopped before deployment because the original preflight only accepted noindex homes. Explicit existing-public-home verification resolved that mismatch without weakening regional checks.
- Naver browser verification and sitemap submission remain separate and uncompleted here due to the tab session ownership conflict.
