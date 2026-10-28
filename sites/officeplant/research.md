# Officeplant research and source ledger

Observed 2026-10-28, approximately 09:19–09:35 UTC (browser session; exact per-request timestamps were not exported). Query: **모란시장 사무실 개업꽃집**. Actual Google and Naver search pages were opened through the browser. Supplemental web search also used **분당 정자동 사무실 개업화분 리본문구**; that supplemental search is not claimed as a measured Google/Naver ranking.

## Search observations

- Google: first observed organic web result was `https://www.hwabun.com/seongnam-opening-plant/`, title “성남 개업화분 선물 가이드, 판교·정자동·모란시장 상권별 12선”. Second: Naver rusiy blog “모란역꽃집 추천! 성남꽃배달과 분당꽃배달까지 가능한”; third: Naver eqenoch blog “모란꽃집 아울렛! 모란역꽃집모란시장…”. Second/third exact destination URLs were not exported and their originals were not analyzed. No ad or map pack was observed in the returned Google search state; this does not establish universal absence.
- Naver: advertisement block, in displayed order: narflower.com, 7flower.net, fmflowermall.com. Not clicked or treated as organic results. No map pack observed in returned state.
- Naver organic documents, observed order after ads: (1) 그린다이닝 꽃집, `https://yeogilife.com/business/MA010120220810073274`; (2) 부산 모란꽃집 directory on life114.co.kr, exact URL not exported, not read; (3) “◆모란꽃집 갤러리>모란사거리 모란역꽃집 화원,콤팩타 화분 꽃배달 가게”, `https://blog.naver.com/sisfamfa/224426423235`; (4) eqenoch blog, not read; (5) Tiffany flower blog, not read. Later shopping block was separate, not counted as organic web rankings.

## Originals actually accessed and analyzed

1. **hwabun.com/seongnam-opening-plant/**: article DOM text length 5,292 characters. H1 reframes a region as recipient-space choice. Sections: four space types; 12 product cards; comparison table; order checklist; budget; related links; FAQ. Outbound seller links carry the ordering step. Adopt the decision sequence (space → suitable product → budget → recipient details), not its copy, regional statistics, product catalogue or delivery claims.
2. **blog.naver.com/sisfamfa/224426423235**: full post read inside mainFrame. Approximately 2,000 Korean characters excluding navigation/blank paragraphs (estimate, not an exact DOM count). Structure: specific delivery example → photo/map → shop link → plant care explanation → long surrounding-place list → tags/video. Adopt clear recipient detail and product identity; do not reuse claimed deliveries, phone, local affiliate network or keyword stuffing.
3. **yeogilife.com/business/MA010120220810073274**: full visible document read; main entry is brief, followed by transport, parking, map, community and related-region sections. Exact length not measured. Business address is prominent, no product checkout. This is a local-directory intent, distinct from an office-gift selector. Do not imply our brand has this store or address.

Only these three are analyzed originals. Search snippets and unvisited pages remain unverified.

## Existing business facts verified

Repository input: `sites/seoul-gyeonggi-plants/products.json` and `site.json` at V5 `d4f58c660655afc5f8359fe0fa70b98fc7588309`. Live seller pages below were opened on 2026-10-28. Each showed product name, price, buy/cart controls, and seller contact 1844-0644. No buy/cart action was taken.

| SKU | Product | Observed price | Actual source/order page |
|---|---|---:|---|
| D144 | 금전수 탁상용 | 53,000 KRW | https://fwith.co.kr/shop/item.php?it_id=D144 |
| D158 | 스투키 탁상용 | 50,000 KRW | https://fwith.co.kr/shop/item.php?it_id=D158 |
| D149 | 녹보수 소형 | 65,000 KRW | https://fwith.co.kr/shop/item.php?it_id=D149 |

Photos: `https://fwith.co.kr/data/item/flower379/{SKU}/thumb-1_500x500.jpg`. D144 natural image dimensions were observed as 500×500 in the browser. All three downloaded successfully and displayed in our local browser. User delegated reuse of verified existing images. Do not substitute generated plants or claim the pictured pot is a guaranteed shipment configuration. Product price is not a total delivered price; checkout handles address-based charges. No guaranteed delivery window, stock, exact dimensions, store address or local branch is asserted.

Region input: `data/regions/seoul_gyeonggi_current_dong.json`, 1,732 distinct district/dong rows, original as-of 2026-10-12; file SHA256 `e7788fd6d7fa3fab10699991d82af714c5215967217c2d96bf6650beaf40310f`. It contains legal/administrative naming variants and is reused unchanged as requested; it is not a count of local stores or unconditional delivery areas.

## Reused operating path

V5 shared planning validation `v5/site_plan.py`; region and product ledgers as above; static HTML/Cloudflare asset adapter pattern. Separate script/template/assets/pool/Worker avoids shared-file collision.

V4 checkout default main `223b9348f32b700af98645d034943772d590aaba` is older than operational refs. Read operational commit `4526b53cb0e75c1fd1590bb41c2425298f4d9e18`, workflow `.github/workflows/v5-quicksky-one-home-public.yml`, successful run https://github.com/joseungil-kr/site-factory-v4/actions/runs/40642326046. It checks out an exact V5 SHA, uses existing V4 GitHub Actions Cloudflare secrets, checks binding/version before deploy, and restores the prior version after failed HTTP checks. Do not reuse Quicksky's Worker or verification token.

`AGENTS.md` and `SITE_CREATION_PROTOCOL.md` read. No `.agents/skills` directory found in either cloned repo or the checked task directories; available ponytail/caveman skills read. Existing protocols are not modified.

Domain `officeplant.nalmada.net`: Windows DNS lookup returned name does not exist. This alone does not prove absence of a Cloudflare Worker custom-domain binding. Authenticated domain inventory remains a parent release prerequisite. No domain, route, DNS, credential or security setting changed.

## Region ledger serialization reconciliation (2026-10-28)

- The frozen local handoff reports sourceRegionSHA256 `e7788fd6d7fa3fab10699991d82af714c5215967217c2d96bf6650beaf40310f` for its local serialization.
- The actual V5 checkout file `data/regions/seoul_gyeonggi_current_dong.json` is unchanged between main and `feature/v52-officeplant` (Git blob `6de6e5751b26a13a2132238f13633df3de0cd2aa`) and its checkout-byte SHA-256 is `48fb6a7cef914a4ef784478b7284761a84e1dd7dc9d7663215880c3a23a67e18`.
- The 1,732-row ordered list was compared against the frozen handoff's generated regional titles; normalized row-sequence FNV-1a64 matches exactly: `a47540b27d784155`. First and last rows also match. No region ledger was edited.
- The build pin now uses the exact V5 checkout SHA-256, while the frozen local handoff report remains preserved unchanged in the original Library ZIP.
