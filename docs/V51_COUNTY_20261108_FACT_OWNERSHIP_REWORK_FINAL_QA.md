# V5.1 county fact-ownership rework: latest offline evidence (2026-11-08)

## Situation and restrictions
- Independent reviewer scored /59 Cheongdo 88 and /28 Wando 87 (FAIL): acceptance notice appears in intro/choice/FAQ, and a price already shown on the card reappears in prose.
- Only the trial branch `site/v51-county-funeral-ownerprivate-20261107` was modified; no main/production/Todayflower deployment, DNS, authentication/authorization or index submission.
- Earlier governance-first SHA: `352646f8fb2d437df99f9269459746db4a9a7aaa`.

## Verified commits in order
1. Facts: `3a9754cb7ba5b720c7aa5406a32973335e1d958f`, `docs/evidence/v51-county-restricted-fact-ownership-20261108.json`. The original evidence recorded the date but not the clock time: `checked_at=unrecorded`, rather than inventing a timestamp. The all-venue notice is county-scoped; B211 directly accessed detail remains unconfirmed.
2. Generator editorial roles: `4d4286debc4366fb396d526934e2ea2893b073b1`. The rice/rice-basket intro has no acceptance claims, choice answers sender/ribbon instead of restating B054/price; FAQ answers a different question. Existing notice and B054 card/CTA retained.
3. Copy pool gate: `b8ece1899adb976ab113323656b11b54237c7734`. `validate_restricted_ownership` rejects repeated acceptance/price/SKU within those two restrictions.
4. Generator gate integration: `20ec297402f6fe6fb7abaf21f4fdea18ce31a1e8`.
5. Final regression test: `091c2d19a3d9fd2a97baa9094eea9e8fd923ac83`. Assembled HTML and both restrictions checked, price is owned once on the product card, 18 generic customer purposes retain their SKU/CTA/title and their own variants.

## Latest Actions (all SUCCESS, no deploy)
- Build 95: https://github.com/joseungil-kr/site-factory-v5/actions/runs/42465185351 , static ZIP artifact **13610938888**.
- 95 HTML review: https://github.com/joseungil-kr/site-factory-v5/actions/runs/42465185334 , artifact **13611740648**.
- 35 paths x (390px mobile + 1440px desktop): https://github.com/joseungil-kr/site-factory-v5/actions/runs/42465185435 , screenshots artifact **13611163316**.
- The static site ZIP's recorded SHA256 is **d6acc5094a02fadd6c0e93a37c8d627f0be37c7adcf5400d2028506f31678ba4** (identical at content SHA `9c0cb095` and test-only SHA `091c2d19`).
- ZIP unpacked and HTML files inspected: **95 page HTML + 404 page**. Offline parser: **95 checked, 0 failures**. HTML purchase CTAs, selected SKU, noindex and noncanonical preserved; neither public sitemap nor publishing was performed.
- Browser original `qa.json` from `9c0cb095`: **70/70** screenshots, 35 paths, 390/1440 widths, horizontal overflow **0**; both /59 and /28 included at both widths. Latest screen workflow `091c2d19` also SUCCESS, content bytes unchanged.

## Actual editorial reading: not an independent approver score
Manually extracted and read headlines, introductions, product cards, descriptions, FAQs and CTA from 17 actual pages: **/ (home), /2, /7, /12, /14, /24, /26, /28, /37, /42, /55, /59, /60, /77, /78, /86, /95**. Read /28 and /59 original 390 and 1440 PNGs directly; no horizontal clipping or broken fonts observed.
- /59: notice 1, B054 card 1 with 90,000 won once, choice addresses condolence ribbon, order addresses venue/room/date, FAQ addresses delivery enquiry. No second acceptance-condition statement in those sections.
- /28: notice 1 with seller basket-category link, B054 card 1 with 90,000 won once, choice addresses sender name, order addresses receiving details, FAQ addresses post-order lookup. No repeated acceptance statement in intro/choice/FAQ.
- Other previously failed cases kept their card/SKU, regional navigation, and buyer-purpose sections in this reviewed artifact. Mechanistic and editor self-review are not independent acceptance; **the reviewer must still assign >=90 to every demanded fixed regression sample**.

## Non-claims and follow-up
- Neither a semantic rule nor a screenshot proves live delivery, current stock, final checkout price, SEO position or conversion.
- The 18-intent contract and both rice restrictions are covered by regression tests; broad semantic equivalence is not universally decidable by keyword checks. Independent editorial review remains necessary.
- No owner-private authenticated deployment or searchable URL is claimed.
