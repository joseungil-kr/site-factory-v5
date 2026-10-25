"""Optional, reusable content components for *both* product and service sites.

Everything is opt-in. Sites without `addOns` produce byte-identical legacy HTML.
Prices live in one site's configuration, not duplicated into individual pages.
"""
from __future__ import annotations
from html import escape


class AddOnError(ValueError):
    pass


def _str(value, field, limit=180):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise AddOnError(f'Invalid add-on text: {field}')
    return value


def validate(addons, page_numbers):
    """Validate a declarative feature set. Unknown knobs are rejected."""
    if addons is None:
        return
    if not isinstance(addons, dict) or set(addons) - {'phoneCTA', 'pricingTable'}:
        raise AddOnError('Unknown add-on feature')
    numbers = {p['number'] for p in page_numbers}
    for name, feature in addons.items():
        if not isinstance(feature, dict) or type(feature.get('enabled', False)) is not bool:
            raise AddOnError('Add-on must have boolean enabled: ' + name)
        if not feature.get('enabled', False):
            continue
        if set(feature) - ({'enabled','title','description','label','pageNumbers','placements'} if name=='phoneCTA' else
                           {'enabled','title','description','headers','rows','note','pageNumbers','placements','vatIncluded'}):
            raise AddOnError('Unknown add-on option: ' + name)
        _str(feature.get('title'), name+'.title')
        if feature.get('description') is not None:
            _str(feature['description'], name+'.description', 550)
        placements = feature.get('placements', ['home','detail'])
        if not isinstance(placements, list) or not placements or len(placements) != len(set(placements)) or any(p not in ('home','detail') for p in placements):
            raise AddOnError('Invalid add-on placements')
        chosen = feature.get('pageNumbers', [])
        if not isinstance(chosen, list) or len(chosen) != len(set(chosen)) or any(type(n) is not int or n not in numbers for n in chosen):
            raise AddOnError('Invalid add-on pageNumbers')
        if name == 'phoneCTA':
            _str(feature.get('label','전화 상담'), name+'.label')
        elif name == 'pricingTable':
            headers = feature.get('headers')
            rows = feature.get('rows')
            if not isinstance(headers, list) or not 1 <= len(headers) <= 8:
                raise AddOnError('Pricing table needs 1..8 columns')
            for ix, h in enumerate(headers): _str(h, f'headers[{ix}]', 80)
            if not isinstance(rows, list) or not 1 <= len(rows) <= 30:
                raise AddOnError('Pricing table needs 1..30 rows')
            for ix, r in enumerate(rows):
                if not isinstance(r, dict) or set(r) != {'label','prices'}:
                    raise AddOnError('Invalid pricing row')
                _str(r['label'], f'rows[{ix}].label', 120)
                v=r['prices']
                if not isinstance(v,list) or len(v)!=len(headers) or any(type(p) is not int or p < 0 or p > 50000000 for p in v):
                    raise AddOnError('Pricing amount must be KRW integer aligned to headers')
            if type(feature.get('vatIncluded', False)) is not bool:
                raise AddOnError('vatIncluded must be boolean')
            if feature.get('note') is not None:
                _str(feature['note'], name+'.note', 550)


def enabled(addons, name, page_number):
    feature = (addons or {}).get(name, {})
    if not feature.get('enabled'):
        return False
    placement='home' if page_number==1 else 'detail'
    return placement in feature.get('placements', ['home','detail']) and (
        not feature.get('pageNumbers') or page_number in feature['pageNumbers'])


def pricing_table(feature):
    """One generic tariff table for any industry; all untrusted text escaped."""
    h=lambda x: escape(str(x), quote=True)
    columns=''.join('<th scope="col">'+h(x)+'</th>' for x in feature['headers'])
    rows=''.join('<tr><th scope="row">'+h(r['label'])+'</th>'+
                 ''.join('<td>'+f'{value:,}원'+'</td>' for value in r['prices'])+'</tr>' for r in feature['rows'])
    note=feature.get('note','')
    vat=('부가세 포함' if feature.get('vatIncluded',False) else '부가세 별도')
    return ('<section class="v5-addon v5-pricing" aria-label="요금표"><h2>'+h(feature['title'])+'</h2>'+
            ('<p>'+h(feature['description'])+'</p>' if feature.get('description') else '')+
            '<div class="v5-price-scroll"><table><thead><tr><th scope="col">항목</th>'+columns+
            '</tr></thead><tbody>'+rows+'</tbody></table></div>'+
            '<p class="v5-price-note">'+vat+(' · '+h(note) if note else '')+'</p></section>')


def phone_cta(site,feature):
    h=lambda x: escape(str(x),quote=True)
    digits=''.join(ch for ch in site['phone'] if ch.isdigit())
    return ('<section class="v5-addon v5-phone-cta"><div><h2>'+h(feature['title'])+'</h2>'+
            ('<p>'+h(feature['description'])+'</p>' if feature.get('description') else '')+'</div>'+
            '<a data-track-event="phone" href="tel:'+digits+'">☎ '+h(feature.get('label','전화 상담'))+
            ' '+h(site['phone'])+'</a></section>')


def enhance_html(html, site, page_number):
    addons=site.get('addOns') or {}
    blocks=[]
    for key in ('pricingTable','phoneCTA'):
        if enabled(addons,key,page_number):
            blocks.append(pricing_table(addons[key]) if key=='pricingTable' else phone_cta(site,addons[key]))
    if not blocks:
        return html
    if '</main>' not in html:
        raise AddOnError('No main section to attach add-on features')
    html=html.replace('</main>',''.join(blocks)+'</main>',1)
    if '</head>' not in html:
        raise AddOnError('No head section to attach add-on stylesheet')
    html=html.replace('</head>','<link rel="stylesheet" href="/assets/addons.css"></head>',1)
    return html
