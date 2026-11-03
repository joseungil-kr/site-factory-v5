# Officeplant RSS

Isolated base 2706fcdf61a7e977ccec2a5a0d3077a80ebca231 matches all 3468 current public pages and three original seller-photo hashes. Existing hostname officeplant.nalmada.net remains on sfv52-officeplant; baseline version d3306f41-6e6f-4194-ae8d-423970a05696 will be guarded again before deployment.

Existing public build generates 50 full-content RSS entries using v5/rss.py reused from 94db74d90e999fd19cf33716a6c2c7ee1a588d52. Feed 534746 bytes; undated pubDate omitted. Main bodies, prices, photos, disabled-before-JS privacy flow and all 3468 sitemap entries remain unchanged; only RSS discovery is added to public head. Worker sends RSS MIME only on approved host/flag, preview feed is 404 and discovery is removed.

Tests: 73 Python regressions, six Officeplant Worker/RSS tests, original preview and public builds, original exhaustive audit 41600 internal links/3468 unique titles, sample-versus-population similarity 0.397965 passed. Windows local raw-ledger verification used exact Git blob LF bytes to reproduce the unchanged Linux source hash; no ledger content change is adopted. Missing seller images were restored only by original prepare script with frozen public-photo SHA-256 verification; binaries are not added to Git.

Release reuses V4 existing credentials and same Worker, checks current exact source/settings/version/domain, retains before snapshot, verifies RSS/sitemap/feed URLs and preserves prior browser/filter/privacy gates. No new credential, resource, DNS or privilege.
