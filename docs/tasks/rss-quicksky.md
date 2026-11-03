# Quicksky RSS

Base 70df954716795796843e93bf1d206f4284453978 was matched to all 1733 current public HTML pages and three source images. Existing Worker is sfv5-quicksky-preview (the similarly named bound-update string is a concurrency group), active version 59b3d663-04b2-4812-ac56-295d3d40548e. The real current release is regional/indexable, with V5_STAGING=1, V5_PUBLIC_HOST=quicksky.nalmada.net and V5_HOME_ONLY=0, not the historical home-only fixture.

Public engine build reuses v5/rss.py from 94db74d90e999fd19cf33716a6c2c7ee1a588d52. RSS 50 complete bodies / 1373228 bytes / all undated pubDate omitted; exact own-host links and stable guid. Only HTML head discovery is added; 1733 sitemap URLs, existing prices/images/ownership meta and all indexing flags remain unchanged. Preview RSS is blocked and public feed gets RSS MIME.

Tests: 96 Python regressions, nine Worker tests, original regional sample-versus-population audit max 0.44809 and cross-brand audit max 0.048499 passed; final engine audit checked 1734 HTML files and 36400 references, errors zero. Local original baseline assets are preserved separately because the original release script adds a verification key after the engine archive manifest; a clean build avoids that preexisting repeated-build archive mismatch without changing integrity checks.

Release must preserve existing Worker binding, exact prior version, all three variables and runtime/subdomain settings with snapshot and guarded rollback. No DNS/resource/credential/privilege changes.
