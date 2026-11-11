# Clinic official-evidence purchase pilots — 2026-11-11 offline audit

## Scope and non-release rules
- Isolation branch: `prototype/clinic-evidence-regions-20261111`.
- CI run: https://github.com/joseungil-kr/site-factory-v5/actions/runs/43019793138; workflow HEAD `73003578c76c323a35338685681639e02c758f9a`; **success**.
- Generated exactly **three** separate regional buyer HTMLs plus one navigation index, all `noindex,nofollow`, no canonical/sitemap, never deployed.
- No changes to operational Clinicflower/Clinicopen/Clinicpresent, existing URL, redirect, DNS, secrets, permissions or IndexNow.
- The specific health institutions below are **existing location reference examples**. There is NO evidence that those named institutions have just opened, moved, permit gift deliveries, or host a flower-wreath celebration. Inference is expressly prohibited.

## Official evidence, carefully scoped
| Pilot | Purchase purpose | Public facility reference | Official facts actually used | Verification |
|---|---|---|---|---|
| `ansan-opening.html` | New-clinic event plant | Ansan Danwon Public Health Center | Hwarang-ro 250 location; 1F civil/clinic spaces vs 2F dental/education spaces | Ansan city public health center indexed pages [location](https://ansan.go.kr/health/common/cntnts/selectContents.do?cntnts_id=C0001633), [floor](https://ansan.go.kr/health/common/cntnts/selectContents.do?cntnts_id=C0001637), consulted 2026-11-11 |
| `seoul-relocation.html` | Medical practice relocation gift plant | Seoul National University Hospital | Daehak-ro 101; several identified buildings; B1 connectors in Daehan Oerae | [Official campus map](https://www.snuh.org/content/E003002007.do), [floor descriptions](https://www.snuh.org/content/E003011.do), consulted 2026-11-11 |
| `suwon-celebration.html` | Opening celebration wreath | Ajou University Hospital | HIRA registered World Cup-ro 164 address; official website provides separate directions, parking and floor-navigation menus | [HIRA facility entry](https://www.hira.or.kr/ra/hosp/hospInfoAjax.do?isNewWindow=Y&isPopupYn=Y&ykiho=JDQ4MTYyMiM1MSMkMSMkMCMkODkkMzgxMzUxIzExIyQxIyQzIyQ2MiQzNjE4MzIjNTEjJDEjJDYjJDgz), [hospital website](https://hosp.ajoumc.or.kr/), consulted 2026-11-11 |

These are official facts about location or navigation, **not** official permissions for third-party delivery or facility-specific event restrictions. Content uses only public facility details and no personal medical data.

## SKU provenance and stale/current distinction
- Historical seller source: `sites/nalmada-shared3/clinic-retail-candidate-ledger-20261111.json` based on seller read-only audit run 41875442755 on **2026-11-05**.
- D144/금전수 탁상용 ₩53,000; D149/녹보수 소형 ₩65,000; C200/축하 3단 화환 ₩59,000; C206/축하 4단 화환 ₩120,000. These are historical recorded seller-listed amounts **not verified current prices**.
- Original SKU links follow `https://fwith.co.kr/shop/item.php?it_id={SKU}`. Never assert current availability, extra shipping cost, or appointment time.
- 2026-11-11 search results displayed D144 and C206 seller pages, but direct verified current HTTP for all four SKU pages was not obtained; D149/C200 latest price and current purchase state remain unconfirmed. No invented price or facility policy.

## Same-locality reproduced legacy comparisons
The previous set of 324 unique HTMLs (108 per site) in artifact 13851895408 was preserved, byte-unchanged. None of the **exact three** paths below was among those archived 324 samples. For a correct locality-to-locality comparison, the pinned previous candidate generator was therefore used to reproduce 3 additional legacy HTMLs offline, without network writes:
| Old candidate route (not touched) | New private prototype | Old fact blocks | New official source IDs |
|---|---|---:|---|
| `clinicopen.nalmada.net/r/00620.html` (Ansan Danwon-gu Choji-dong) | `ansan-opening.html` | 3 generic buying topics | A-LOCATION, A-FLOOR |
| `clinicflower.nalmada.net/r/03222.html` (Seoul Jongno-gu Yeongeon-dong) | `seoul-relocation.html` | 3 generic buying topics | S-ADDRESS, S-MAP, S-ROUTE |
| `clinicpresent.nalmada.net/r/00542.html` (Suwon Yeongtong-gu Woncheon-dong) | `suwon-celebration.html` | 3 generic buying topics | W-HIRA, W-SITE |

The artifact includes old candidate HTMLs, new HTMLs, SHA-256 hashes, source IDs, and a before/after JSON comparison. This compares pinned generator output, **not current operating-page bytes**.

## Browser verification (Playwright)
- Test: `prototypes/clinic-evidence-regions-20261111/test_browser.py`; 390x844 mobile and 1440x900 desktop.
- 6/6 region-purpose page interactions passed; 6 full-page screenshots saved; 3 distinct purpose flows and a shared navigation index.
- Headings, official inline source links (2/3/2), product SKU targets (2 per case), telephone `tel:1844-0644`, intra-pilot navigation, page width, Korean fonts, and noindex passed.
- **No checkout, orders, or telephone call placed**. Browser did not click through to external seller sites; this verifies href integrity only.
- CI result does **not** replace human editorial SEO judgment. Three official-info examples are a feasibility test, not representative evidence for all 5,034 localities.

## Unresolved before any future release proposal
- Direct latest official facility access can change; source timestamps and source scope must be refreshed before editorial approval.
- No source identifies a specific current opening/relocation event at the named reference facilities, actual recipient, permissible flower-installation area, loading access permission, or real-time shipment.
- No proof of up-to-date SKU prices, stock, delivery fees, coverage, item composition or direct seller URL responses across all four products.
- Existing 15,906 operating HTMLs have not been byte-diffed against these new candidates. This pilot does not imply their removal, redirection, replacement or indexing policy.
- Human editorial review, legality of publishing factual facility-use examples, and any operational migration remain separate decisions.

**Status: 3 evidence-grounded sample HTMLs and 6 browser screenshots PASS in isolated non-deploy CI; production editorial approval PENDING.**
