# Winterbbang RSS release

Base 3434a0e447d3d35c08c3db911cf88a327b103335 matched every current public HTML page (1804) and five original WebPs. Initial readback had a transport timeout; all 1809 comparisons passed on bounded read-only retry. Existing Worker sfv54-winterbbang-preview active c3438c1a-89ff-4ffa-bd85-88c7fa5c1151 is guarded before deployment.

Existing public prepare automatically generates RSS from rendered whole bodies, including hero headings/introductions. Shared v5/rss.py from V5 94db74d90e999fd19cf33716a6c2c7ee1a588d52 is adapted only with explicit body-tag support and title from source H1; two XML/content tests cover this. RSS 50 entries / 874129 bytes / no fabricated dates. Exact public host has RSS MIME; preview feed 404 and discovery stripped. Full content/prices/images, 1804 sitemap entries, all indexing flags and the already-published Naver ownership file are preserved.

Tests: five national unit tests, seven Worker tests, two RSS tests, original full-quality audit max 0.417056 over 31158 sample-versus-population comparisons, final public preparation all passed. Release must preserve existing Naver file naverf6f2cf7c98cc3b3483ccc524379d2605.html byte-for-byte in the same stage where the original controller added it. No new ownership, DNS, key or service is created.
