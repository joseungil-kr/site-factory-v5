# Site Factory V5 — Phone-lead services and optional site components

## Compatibility contract

One V5 engine handles either a product catalog (`businessModel` omitted) or a phone-first service (`businessModel: "service-lead"`). **These are data/content strategies, not mutually exclusive UI feature bundles.** Existing product sites with no `addOns` continue with exactly the same HTML renderer and output assets.

Reusable opt-in `addOns` work in **both** strategies:

- `phoneCTA`: an extra prominent call-to-action panel, not a replacement for an existing purchase button;
- `pricingTable`: independently managed, VAT-aware KRW numeric rate rows, separate from a shop's product prices;
- both components may appear together and can be limited to the home page, detail pages, or selected numbered pages.

No payment gateway, lead collection form or analytics is enabled by these components. Telephone links use the validated site `phone` and render as `tel:` URLs.

## Product site with phone and a service-rate table

Add the following to a product site’s existing `site.json` (do not remove its products or order origin):

```json
{
  "addOns": {
    "pricingTable": {
      "enabled": true,
      "title": "배송 및 설치 추가요금",
      "headers": ["기본", "확장"],
      "rows": [{"label": "설치 안내", "prices": [15000, 30000]}],
      "vatIncluded": false,
      "note": "실제 적용 조건은 상담 시 확정",
      "placements": ["home", "detail"],
      "pageNumbers": [1, 2]
    },
    "phoneCTA": {
      "enabled": true,
      "title": "상품 구매 전 상담",
      "description": "온라인 구매와 전화 상담을 함께 제공합니다.",
      "label": "전화 상담",
      "placements": ["home", "detail"],
      "pageNumbers": [1, 2]
    }
  }
}
```

The numbers above are fictional **configuration examples**, not the approved rates for any existing flower site. The user must supply actual business rates before enabling the example.

Omitting `pageNumbers` displays a component on every page covered by `placements`. Missing or disabled features generate no extra assets and do not change the legacy HTML. Price fields are positive or zero **integer KRW amounts**; supplied strings are always HTML-escaped. Unknown addon properties and nonexistent page numbers are rejected.

## Phone-first service site

`sites/daysky` demonstrates the phone-lead strategy using `services.json` plus one central `rates.json`, not `products.json` or `productSkus`. The initial scope is **29 numbered pages**: home + city/district 3 + Ansan 25 administrative dongs. All page phone links target `010-5322-1952`. The approved base prices are:

| Equipment | 1 hour | 4 hours | 8 hours |
|---|---:|---:|---:|
| 1t / 3.5t | ₩300,000 | ₩400,000 | ₩600,000 |
| 5t | ₩400,000 | ₩500,000 | ₩700,000 |

Prices exclude VAT. The engine never converts 24-hour **telephone consultation** into a guaranteed 24-hour dispatch commitment.

**Preview only**: site domain is `null`, desired host is recorded under `requestedDomain: https://daysky.nalmada.net` (informational only), `publishEnabled: false`, and both sitemap and IndexNow are disabled. No Cloudflare DNS/Worker binding is created by this feature branch. The three SVG drawings are intentionally **conceptual placeholders** and must not be represented as actual worksite photos.

## Local verification

```bash
python -m unittest discover -s tests -q
npm test
python -m v5 build --site daysky --mode preview
python -m v5 audit --site daysky
```

The V5 `audit` checks HTTP-page metadata, reference paths, content similarity (all 406 pairs for 29 pages), the 7-link numeric pager, and preview `noindex`. Existing flower-catalog regressions still execute. The `pages.json` numbering is immutable; future region append must not renumber these 29 pages.
