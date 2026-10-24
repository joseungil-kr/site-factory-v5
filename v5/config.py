"""Untrusted customer input validation. Never infer a production domain."""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
SITE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SAFE_FILENAME = re.compile(r"[^\\/\x00-\x1f<>:\"|?*]+\.html\Z")
THEMES = {"classic", "modern", "minimal"}

class ConfigError(ValueError):
    pass


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"Cannot read {path}: {exc}") from exc


def safe_filename(name: str):
    if not isinstance(name, str) or not SAFE_FILENAME.fullmatch(name) or name.startswith("."):
        raise ConfigError(f"Unsafe page filename: {name!r}")
    return name


def validate_site_id(site_id: str):
    if not isinstance(site_id, str) or not SITE_ID.fullmatch(site_id):
        raise ConfigError(f"Unsafe site identifier: {site_id!r}")
    return site_id


def unique_by(items, key, label):
    found = set()
    for item in items:
        value = item[key]
        if value in found:
            raise ConfigError(f"Duplicate {label}: {value}")
        found.add(value)


def check_https_url(url: str, label: str):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ConfigError(f"{label} must be an HTTPS URL without credentials or fragment")
    return parsed


def read_site(site_id: str):
    validate_site_id(site_id)
    root = (SITES/site_id).resolve()
    if root.parent != SITES.resolve() or not root.is_dir():
        raise ConfigError(f"Unknown site: {site_id}")
    site = read_json(root/'site.json')
    pages = read_json(root/'pages.json')
    products = read_json(root/'products.json')
    links = read_json(root/'links.json')
    special = read_json(root/'special-pages.json')
    regions = read_json(root/'regions.json')
    if site.get('regionalScale',{}).get('enabled',False):
        from .region_pages import expand
        pages,regions=expand(site,pages,regions,ROOT)
    if site['id'] != site_id:
        raise ConfigError('Site id mismatch')
    if site['theme'] not in THEMES:
        raise ConfigError('Unknown theme')
    if site['domain']:
        parsed=check_https_url(site['domain'], 'domain')
        if parsed.path not in ('','/') or parsed.query:
            raise ConfigError('Domain must be origin only')
        if parsed.netloc.lower() in ('example.com','localhost','127.0.0.1'):
            raise ConfigError('Demo domain cannot be used for a live site')
    if not isinstance(site['publishEnabled'],bool):
        raise ConfigError('publishEnabled must be boolean')
    if site['publishEnabled'] and not site['domain']:
        raise ConfigError('Cannot publish without a real domain')
    if not re.fullmatch(r'0\d{1,2}-\d{3,4}-\d{4}|1\d{3}-\d{4}',site['phone']):
        raise ConfigError('Invalid phone format')
    check_https_url(site['orderBaseUrl'],'orderBaseUrl')
    draft=site.get('status')=='draft'
    if not (0<len(pages)<=19970 or draft and not pages):
        raise ConfigError('Unexpected page count')
    unique_by(pages,'id','page id')
    unique_by(pages,'number','page number')
    numbers={x['number'] for x in pages}
    if (pages and 1 not in numbers) or any(not isinstance(n,int) or isinstance(n,bool) or n<=0 for n in numbers):
        raise ConfigError('Require page number 1 and strictly positive numbers')
    for p in pages:
        if len(p.get('sections',[]))<2 or not p.get('intro','').strip():
            raise ConfigError(f"Missing content in {p['id']}")
        if not p.get('title','').strip():
            raise ConfigError(f"Missing title in {p['id']}")
        if not isinstance(p['productSkus'],list) or not p['productSkus']:
            raise ConfigError(f"Page without products: {p['id']}")
    if not products and not draft:
        raise ConfigError('No products')
    unique_by(products,'sku','product SKU')
    by_sku={p['sku']:p for p in products}
    order_origin=check_https_url(site['orderBaseUrl'],'orderBaseUrl')
    for p in products:
        if not isinstance(p['sku'],str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',p['sku']):
            raise ConfigError('Unsafe product SKU')
        o=check_https_url(p['orderUrl'],'product.orderUrl')
        if o.netloc.lower()!=order_origin.netloc.lower():
            raise ConfigError('Product target outside approved order origin')
        if p.get('imageUrl'):
            img=check_https_url(p['imageUrl'],'product.imageUrl')
            if img.netloc.lower()!=order_origin.netloc.lower():
                raise ConfigError('Product image outside approved seller origin')
        if not isinstance(p['referencePrice'],int) or p['referencePrice']<=0:
            raise ConfigError('Invalid product reference price')
    for page in pages:
        if any(sku not in by_sku for sku in page['productSkus']):
            raise ConfigError(f"Missing SKU for page {page['id']}")
    library=site.get('imageLibrary',site_id)
    if not SITE_ID.fullmatch(library):
        raise ConfigError('Unsafe image library identifier')
    if site.get('analytics',{}).get('enabled') and not site.get('cookiePrivacyReviewed',False):
        raise ConfigError('Tracking requires prior privacy review')
    if (not site['imagePool'] and not draft) or len(set(site['imagePool']))!=len(site['imagePool']):
        raise ConfigError('Invalid shared image pool')
    for name in site['imagePool']:
        if not re.fullmatch(r'[a-z0-9-]+\.(?:svg|png|jpe?g|webp)',name):
            raise ConfigError(f'Unsafe image file name: {name}')
        if not (ROOT/'assets/library'/library/name).is_file():
            raise ConfigError(f'Missing shared asset: {name}')
    unique_by(special,'path','special page')
    unique_by(links,'id','link id')
    from .markup import filename as page_filename
    filenames={page_filename(n) for n in numbers}
    for s in special:
        safe_filename(s['path'])
        if s['path'] in filenames or s['path']=='404.html':
            raise ConfigError('Special page collides with numbered page')
        if s['type'] not in {'calculator','content'}:
            raise ConfigError('Unknown special page module')
    specials={s['path'] for s in special if s.get('enabled',True)}
    targets={'/'}|{'/'+page_filename(n) for n in numbers}|{'/'+s for s in specials}
    for item in site.get('navigation',[]):
        if not isinstance(item,dict) or not item.get('label') or item.get('href') not in targets:
            raise ConfigError('Site navigation must link to a real generated page')
    for link in links:
        if link['placement'] not in {'body','footer','both'} or link['scope'] not in {'all','region','selected'}:
            raise ConfigError('Bad global-link placement or scope')
        if link['target'] not in specials:
            raise ConfigError('Dangling global-link target: '+link['target'])
        if link['scope']=='region' and not link.get('regions'):
            raise ConfigError('Region-scoped link requires regions')
        if link['scope']=='selected' and not link.get('pageIds'):
            raise ConfigError('Selected-scoped link requires page ids')
    soft=site.get('staticAssetSoftLimit',18000)
    if not isinstance(soft,int) or not 10<=soft<=20000:
        raise ConfigError('Invalid asset limit')
    region_names={r['name'] for r in regions['regions']}
    for p in pages:
        if p['region'] not in region_names:
            raise ConfigError(f"Unverified region: {p['region']}")
    return dict(site=site,pages=sorted(pages,key=lambda p:p['number']),products=products,
                links=links,special=special,regions=regions,root=root)


def assert_publish_ready(site):
    if not site['domain'] or not site['publishEnabled'] or not site.get('workerName'):
        raise ConfigError('Missing approved production domain, publishEnabled, or workerName')
    if site.get('source') and 'demonstration' in site['source'].lower():
        raise ConfigError('Demo source not permitted for production')
    return True
