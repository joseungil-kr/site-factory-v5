# Baekse RSS release

Base d254483ab8ec2292c2b63dbc9f0876ad0de38780 is the actual October 31 Naver-home verification source, not the older 96dc41f release clue. All 430 current HTML pages and five WebPs match after stripping only the new RSS discovery link. The existing homepage ownership meta and complete sitemap are preserved.

Public prepare step reuses v5/rss.py from 94db74d90e999fd19cf33716a6c2c7ee1a588d52, generating up to 50 full-content items, own-host URLs/guid and no fabricated publication dates. Public Worker serves RSS MIME only on the exact public host and blocks preview RSS/discovery. Existing public/preview/indexing policy, images, prices, and ownership files remain unchanged. Six Worker tests, source city tests and shared RSS XML test pass.

Existing Worker sfv54-baekse-city-preview version 46cbda0b-b86d-4956-8fb9-58eb74948820 will be guarded with an exact existing binding/settings snapshot before deployment; no new resource or credential is created.
