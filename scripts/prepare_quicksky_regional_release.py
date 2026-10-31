"""Build the user-authorized regional release only after the actual internal audit.

The checked-in home-only configuration remains a rollback fixture. Release approval
is scoped to this command and its freshly generated evidence, never a blanket bypass.
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from v5.config import read_site
from v5.quicksky_pages import audit_one_percent
from v5.quicksky_home_evidence import validate_home_evidence
from v5.engine import build
from v5.markup import filename, url_path

ROOT = Path(__file__).resolve().parents[1]


def verify_assets(root):
    expected = ['https://quicksky.nalmada.net'+url_path(n) for n in range(1, 1734)]
    urls = [e.text for e in ET.parse(root/'sitemap.xml').findall(
        './/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(urls) == 1733 and set(urls) == set(expected)
    for n, url in enumerate(expected, 1):
        html = (root/filename(n)).read_text(encoding='utf-8')
        assert '<meta name="robots" content="index,follow">' in html, n
        assert html.count(f'<link rel="canonical" href="{url}">') == 1, n
        assert html.count('naver-site-verification') == (1 if n == 1 else 0), n
    error = (root/'404.html').read_text(encoding='utf-8')
    assert 'noindex,nofollow' in error and 'rel="canonical"' not in error
    assert (root/'robots.txt').read_text() == 'User-agent: *\nAllow: /\nSitemap: https://quicksky.nalmada.net/sitemap.xml\n'


def main():
    data = read_site('quicksky')
    validate_home_evidence(data['site'], data['pages'], data['rates'])
    result = audit_one_percent(data['pages'])
    report = ROOT/'reports/quicksky'
    report.mkdir(parents=True, exist_ok=True)
    (report/'regional-similarity.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    assert result['passes'] and result['population'] == 1733 and result['sample'] >= 18, result
    path = ROOT/'sites/quicksky/site.json'
    original = path.read_bytes()
    site = dict(data['site'])
    site.update(homeIndexingApproved=False, publicIndexingApproved=True,
                contentQualityApproved=True,
                publicIndexingScope='quicksky-seoul-gyeonggi-1733-20261027')
    try:
        path.write_text(json.dumps(site, ensure_ascii=False, indent=2), encoding='utf-8')
        build('quicksky', mode='public-indexing')
    finally:
        path.write_bytes(original)
    root = ROOT/'dist/quicksky'
    verify_assets(root)
    key = (ROOT/'sites/quicksky/home-indexnow-key.txt').read_text().strip()
    assert re.fullmatch(r'[a-f0-9]{32}', key)
    (root/(key+'.txt')).write_text(key+'\n', encoding='utf-8')
    cfg = {'name':'sfv5-quicksky-preview', 'compatibility_date':'2026-10-21',
           'main':'../../worker/index.js', 'workers_dev':True, 'preview_urls':False,
           'keep_vars':False,
           'vars':{'V5_STAGING':'1','V5_PUBLIC_HOST':'quicksky.nalmada.net','V5_HOME_ONLY':'0'},
           'assets':{'directory':'../../dist/quicksky','binding':'ASSETS',
                     'html_handling':'none','not_found_handling':'404-page','run_worker_first':True}}
    dest = ROOT/'deploy/quicksky/staging.wrangler.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(cfg, indent=2)+'\n', encoding='utf-8')
    print('QUICKSKY_REGIONAL_RELEASE_PASS', json.dumps(result), 'sitemap=1733; IndexNow not submitted')


if __name__ == '__main__':
    main()
