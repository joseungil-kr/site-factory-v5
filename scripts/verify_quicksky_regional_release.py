"""Read-only live checks for the 1733-URL release; never submits to search engines."""
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from scripts.verify_quicksky_home_release import read, PUBLIC, PREVIEW
from v5.markup import url_path


def verify():
    checks = []
    for origin in (PUBLIC, PREVIEW):
        for path in ('/', '/2.html', '/867.html', '/1733.html', '/1734.html'):
            status, headers, body = read(origin, path)
            error = path == '/1734.html'
            assert status == (404 if error else 200), (origin, path, status)
            text = body.decode('utf-8')
            blocked = error or origin == PREVIEW
            assert ('noindex' in headers.get('X-Robots-Tag', '').lower()) == blocked, (origin, path)
            if error:
                assert 'noindex,nofollow' in text and 'rel="canonical"' not in text
            else:
                assert 'name="robots" content="index,follow"' in text
                assert text.count(f'<link rel="canonical" href="{PUBLIC}{path}">') == 1
                assert '빠른스카이' in text and '010-5322-1952' in text
                assert text.count('naver-site-verification') == (1 if path == '/' else 0)
                if path == '/':
                    assert '8d0599110182e1196f9a95e23c1957df88b6fd37' in text
            checks.append({'url':origin+path, 'http':status, 'httpNoindex':blocked})
    status, headers, body = read(PUBLIC, '/sitemap.xml')
    assert status == 200 and 'noindex' not in headers.get('X-Robots-Tag', '').lower()
    urls = [e.text for e in ET.fromstring(body).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    expected = [PUBLIC+url_path(n) for n in range(1, 1734)]
    assert len(urls) == 1733 and set(urls) == set(expected)
    assert read(PUBLIC, '/robots.txt')[2].decode() == 'User-agent: *\nAllow: /\nSitemap: '+PUBLIC+'/sitemap.xml\n'
    assert 'Disallow: /' in read(PREVIEW, '/robots.txt')[2].decode()
    key = (Path(__file__).resolve().parents[1]/'sites/quicksky/home-indexnow-key.txt').read_text().strip()
    status, _, body = read(PUBLIC, '/'+key+'.txt')
    assert status == 200 and body.decode().strip() == key
    return {'status':'regional-public-http-verified','publicSitemapUrls':1733,
            'regionalHtmlBuildCheck':'all 1732; live HTTP representative sample only',
            'previewNoindex':True,'checks':checks,'searchEngineSubmitted':False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = verify()
    args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
