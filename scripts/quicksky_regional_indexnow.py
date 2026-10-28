"""One-shot notification of newly public regions; no deployment or homepage resubmit."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from scripts.quicksky_home_indexnow import key_and_scope
from scripts.verify_quicksky_home_release import PUBLIC, read
from v5.markup import url_path


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.robots = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'bingbot', 'googlebot'):
            self.robots.append(attrs.get('content', '').lower())


def validate_page(url, status, headers, body):
    head = Head()
    head.feed(body.decode('utf-8'))
    assert status == 200 and head.canonicals == [url], url
    assert not any('noindex' in value or 'none' in value.split(',') for value in head.robots), url
    assert 'index,follow' in head.robots, url
    assert 'noindex' not in headers.get('X-Robots-Tag', '').lower(), url


def regional_urls(body):
    urls = [x.text for x in ET.fromstring(body).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    expected = [PUBLIC + url_path(n) for n in range(1, 1734)]
    assert len(urls) == len(set(urls)) == 1733 and set(urls) == set(expected)
    return [url for url in urls if url != PUBLIC + '/']


def prepare(output):
    key = key_and_scope()  # Reuse the existing key and immutable service scope.
    status, _, body = read(PUBLIC, '/' + key + '.txt')
    assert status == 200 and body.decode().strip() == key
    status, _, body = read(PUBLIC, '/sitemap.xml')
    assert status == 200
    urls = regional_urls(body)
    assert read(PUBLIC, '/robots.txt')[2].decode() == 'User-agent: *\nAllow: /\nSitemap: ' + PUBLIC + '/sitemap.xml\n'

    def check(url):
        validate_page(url, *read(PUBLIC, url[len(PUBLIC):]))

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(check, urls))
    report = {'verifiedAt': datetime.now(timezone.utc).isoformat(), 'urlCount': len(urls),
              'urlList': urls, 'keyLocation': PUBLIC + '/' + key + '.txt',
              'allPagesHttpCanonicalIndexVerified': True, 'homepageExcluded': True}
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def submit(proof_path, receipt):
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    assert 0 <= (datetime.now(timezone.utc) - datetime.fromisoformat(proof['verifiedAt'])).total_seconds() < 1800
    urls = proof['urlList']
    assert len(urls) == len(set(urls)) == 1732
    assert set(urls) == {PUBLIC + url_path(n) for n in range(2, 1734)}
    assert proof['allPagesHttpCanonicalIndexVerified'] and proof['homepageExcluded']
    key = key_and_scope()
    location = PUBLIC + '/' + key + '.txt'
    assert proof['keyLocation'] == location
    status, _, body = read(PUBLIC, '/' + key + '.txt')
    assert status == 200 and body.decode().strip() == key
    payload = {'host': 'quicksky.nalmada.net', 'key': key, 'keyLocation': location, 'urlList': urls}
    data = json.dumps(payload).encode()
    report = {**proof, 'attemptedAt': datetime.now(timezone.utc).isoformat(),
              'payloadSha256': hashlib.sha256(data).hexdigest(), 'outcome': 'uncertain',
              'http': None, 'response': None, 'indexingProven': False,
              'priorHomepageReceiptRun': 40545319383}
    # Exclusive creation before POST: even uncertain transport outcomes forbid reruns.
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
    request = Request('https://api.indexnow.org/indexnow', data=data,
                      headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
    try:
        with urlopen(request, timeout=90) as response:
            code, body = response.status, response.read(2000).decode('utf-8', 'replace')
    except HTTPError as error:
        code, body = error.code, error.read(2000).decode('utf-8', 'replace')
    report.update(http=code, response=body, completedAt=datetime.now(timezone.utc).isoformat(),
                  outcome={200: 'received', 202: 'received-key-validation-pending'}.get(code, 'rejected'))
    receipt.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return {k: report[k] for k in ('http', 'outcome', 'urlCount', 'keyLocation', 'completedAt', 'indexingProven')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'submit'))
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        result = prepare(args.proof)
        print(json.dumps({k: v for k, v in result.items() if k != 'urlList'}))
    else:
        assert args.receipt is not None
        print(json.dumps(submit(args.proof, args.receipt)))
