# Hallflower RSS release

Base e6cc9b4e4dd53e3d50d0381211f3e7be092c242e matched every current public page (1081). Actual approved Worker is sfv53-hallflower-public, not the separate noindex preview Worker; GET-only inventory confirmed active e6bfa164-9cc1-4152-9f61-2973f7cd9d0b with HALLFLOWER_PUBLIC=1 and workers.dev/preview URLs disabled.

Public prepare reuses shared v5/rss.py with body/H1 support, generating full-body RSS (hero included), 50 items / 1038394 bytes / all undated dates omitted. Explicit repository import path supports the original direct-script entry point. RSS MIME is exact public host only; preview RSS blocked and discovery removed. Existing facilities/content, pictures, prices, 1081 sitemap URLs, all policy flags and current Naver file remain unchanged.

Tests: original full build; full 1080-facility audit sampled 11 against population (11869 comparisons, max 0.477302); public candidate preparation; four Worker/RSS tests; two XML/full-hero-body tests. Existing ownership file naver4baf44c5d229746418407a0ad78a8363.html is preserved byte-for-byte after build exactly as the original controller; no new ownership or DNS binding is created. Existing candidate block metadata remains untouched; this is maintenance of the already-public site under explicit user RSS authorization.
