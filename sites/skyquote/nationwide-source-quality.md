# 전국 원장 정합성 주의 · Skyquote
Checked: 2026-10-31 KST.

The preliminary national noindex generator currently uses an Open Admin Data third-party snapshot dated 2026-09-08, with 17 provinces and 225 district records. This is NOT an official exhaustive, current national administrative-code ledger and not a source of business service areas.

**Confirmed discrepancy:** the snapshot contains only **24 Seoul districts** and omits **서울특별시 강서구**. A Seoul Metropolitan Council official district-area source lists 강서구 and the remaining Seoul districts (https://ms.smc.seoul.kr/attach/record/SEOUL/appendix/a11/A0063374.pdf?time=20260525162854). Do not label the 242 national administrative records as complete coverage, and do not publish them as searchable index pages before a full current official code reconciliation.

Current official legal-dong data example: https://www.data.go.kr/data/15063424/fileData.do (2026-06-30 snapshot, updated 2026-07-29, 20,561 rows including higher and lower levels). Its 20,561 raw rows are NOT all distinct active target 'dong' pages, and their site/business suitability is not yet established. The existing 1,732 Seoul/Gyeonggi rows are also not nationwide coverage.

**Scope of achieved work:** 268 unindexed informational HTML docs for QA (the 242 preliminary regions, national overview, 25 Ansan docs). Their city/district label sources may need correction; conditional questions are hypothetical and cannot claim local job history, rates, or national service. The existing 1536x1024 original AI WebPs and provenance are retained unchanged.

**Next gating step before public index:** obtain and normalize the dated official administrative-code snapshot; resolve renames/omissions and duplicate legal versus administrative codes, verify direct business service areas, then regenerate and recheck canonical, sitemap and public search policy. Until then use workers.dev noindex preview only; skyquote.nalmada.net binding requires separate explicit approval.
