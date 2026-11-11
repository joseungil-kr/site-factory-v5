# Worker6 official three locality text — independent artifact inspection and historical-price fix (2026-11-11)

## Independently downloaded artifact
- Original GitHub Actions run **43018630332 SUCCESS**, artifact **13854740235**.
- Downloaded ZIP bytes SHA256 **3e84fe105cb7f9cbd6106d8000fa7ae37e4e2337ed6c01c52d9c95ab727dca0f**; matches artifact digest.
- ZIP contains `index.html`, `guide.html`, `1.html`, `2.html`, `3.html`, `manifest.json`, eight full-page screenshots (`index/1/2/3` × `390/1440`) and `screenshots-qa.json`.
- Directly opened three HTML and their **actual 390px and 1440px screenshots**. 390px screenshots sizes 390×1449, 390×1475, 390×1528; 1440px sizes 1440×1040, 1440×1066, 1440×1066. Text legible, no observed horizontal overflow, but presentation is sparse and is **not** a finished consumer site.
- Artifact browser QA: 8 screenshots, HTTP 200, `scrollWidth == viewport`, `noindex=true`, imageCount=0. Image load has **not** been tested.

## All links and CTA targets
- Each of three detail pages has exactly 6 anchors:
  1. `/` local navigation (exists, 200 in Actions).
  2. `/guide.html` shared buyer guide (exists, 200).
  3. `https://fwith.co.kr/shop/item.php?it_id=D144` product CTA, `target=_blank`, `rel=noopener noreferrer`.
  4. One exact official municipality URL, `target=_blank`, `rel=noopener noreferrer`.
  5. D144 seller surcharge source URL, same D144 URL, `target=_blank`, `rel=noopener noreferrer`.
  6. `tel:18440644` phone CTA.
- Index has links to `/guide.html`, `/1.html`, `/2.html`, `/3.html`. Internal HTTP traversal run 43018630332: **5 pages HTTP 200 and 11 internal links HTTP 200**. External destinations were verified for exact href/target attributes from HTML, **not** re-fetched for current HTTP status.
- `noindex,nofollow` present on all. No canonical in preview, intentionally.

## Actual body differences and limitations
- 1.html: Paju Jeokseong industrial-complex location `가월리 1844번지 일원`; question to verify actual recipient company, building number and department. Seller D144 fee row 7 (10,000 KRW displayed).
- 2.html: Gapyeong Seorak community-center address `한서로 8`, **only when this facility is explicitly the destination**; organizer/recipient and admission time remain unknown. Seller rows 5/8 (10,000/20,000 displayed, precedence unknown).
- 3.html: Pocheon Idong office address `화동로 2048`, **only if the office is actual destination**; home recipient address must not be replaced with this office address. Official institution list basis `2026-01-01`. Seller rows 5/9 (10,000/20,000 displayed, precedence unknown).
- All share D144 53,000 KRW and generic unknown stock/arrival/call instruction. This is a **small, evidence-backed distinction**, not proof of national regional uniqueness.
- For additional diagnostic only, original artifact's main paragraph+list text (NOT exact V5 audit assembled-body input) 5-character Jaccard: 1↔2 **0.3859**, 1↔3 **0.3309**, 2↔3 **0.4481**. Do not treat these as official 49% gate PASS; no 5302 sample or editorial 85 score.

## Defect found and minimal correction
- Original price paragraph said `금전수 탁상용 53,000원 · 상품 가격 확인일 2026-11-09`. Although dated, readers could interpret the 53,000 KRW as current. Updated to explicitly state `2026-11-09 당시 확인 가격입니다. 현재 가격은 주문 전 판매처에서 다시 확인하세요.`.
- Added regression checks for historical price, current-price recheck, and unknown regional availability. No change to verified source quote, facility acceptance claim, seller fee rows, 49% or 85% thresholds.
- No other factual defect identified from the inspected artifact. Official URLs' **current** HTTP/content were not independently re-checked in this artifact audit; evidence ledger quotes remain source-attributed, not fresh verified present-day guarantees.

## Restrictions
- Image `403 scope_violation` files not accessed, retried, or bypassed.
- No existing operating HTML, production URL, redirect, deployment, index, DNS, secrets, permissions, security, or personal data changed.
- Text-only 3-page QA is **not** 5302 completion, 49% or 85% PASS, image load, or publication.
