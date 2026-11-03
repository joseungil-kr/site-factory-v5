"""Bounded localhost-only Wrangler probe; no Cloudflare login, API or deployment."""
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from v5.config import ROOT
from v5.shared_static import assemble


def run():
    results = []
    with tempfile.TemporaryDirectory(prefix='sfv5-local-', ignore_cleanup_errors=True) as t:
        base = Path(t)
        entries = []
        for site, host in [('ansan', 'ansanwreath.fwith.kr'), ('seoul', 'seoulwreath.fwith.kr'), ('funeral', 'seoulfuneral.fwith.kr')]:
            source = base / site
            (source / 'assets').mkdir(parents=True)
            (source / 'assets/site.css').write_text('body{color:red}')
            (source / 'assets/photo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            for name in ['index.html', '2.html', '404.html']:
                (source / name).write_text(f'<h1>{site} {name}</h1><link href="/assets/site.css">')
            (source / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://' + host + '/sitemap.xml\n')
            (source / 'sitemap.xml').write_text('<urlset><url><loc>https://' + host + '/</loc></url></urlset>')
            (source / 'rss.xml').write_text('<rss version="2.0"><channel><link>https://' + host + '/</link></channel></rss>')
            entries.append((site, host, source))
        bundle = base / 'bundle'
        assemble(entries, bundle)
        # Instrument a temporary copy only: one marker per actual local handler entry.
        worker = bundle / 'shared-static.js'
        worker.write_text(worker.read_text(encoding='utf-8').replace(
            'async fetch(request, env) {', 'async fetch(request, env) { console.log("SFV5_HANDLER_ENTRY");'), encoding='utf-8')
        config_file = bundle / 'wrangler.json'
        config = json.loads(config_file.read_text())
        public_asset = next((bundle / 'public/_sfv5/assets').glob('*/site.css'))
        path = '/' + public_asset.relative_to(bundle / 'public').as_posix()
        env = {**os.environ, 'WRANGLER_SEND_METRICS': 'false', 'BROWSER': 'none', 'CI': 'true'}
        # A fixed local port keeps the subprocess command reviewable; fail if occupied.
        import socket
        with socket.socket() as s:
            s.bind(('127.0.0.1', 18787))
        logfile = base / 'wrangler.log'
        with logfile.open('w', encoding='utf-8') as log:
            process = subprocess.Popen([shutil.which('npm.cmd') or shutil.which('npm'), 'exec', '--yes', '--package=wrangler@4.148.0', '--',
                'wrangler', 'dev', '--local', '--ip', '127.0.0.1', '--port', '18787', '--inspector-port', '0',
                '--config', str(config_file)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            try:
                def get(host, route):
                    req = Request('http://127.0.0.1:18787' + route, headers={'Host': host})
                    try:
                        response = urlopen(req, timeout=3)
                    except HTTPError as exc:
                        response = exc
                    with response:
                        return response.status, response.read().decode(), dict(response.headers)
                deadline = time.monotonic() + 50
                while True:
                    if process.poll() is not None:
                        raise RuntimeError('Wrangler stopped: ' + logfile.read_text(encoding='utf-8')[-4000:])
                    try:
                        get('ready.example.test', '/')
                        break
                    except (URLError, TimeoutError):
                        if time.monotonic() >= deadline:
                            raise RuntimeError('Local Wrangler startup timeout: ' + logfile.read_text(encoding='utf-8')[-4000:])
                        time.sleep(.25)
                def count():
                    time.sleep(.3)
                    return logfile.read_text(encoding='utf-8').count('SFV5_HANDLER_ENTRY')
                for host, route, status, expected, invocations in [
                    ('ansanwreath.fwith.kr', '/', 200, 'ansan index.html', 1),
                    ('seoulwreath.fwith.kr', '/', 200, 'seoul index.html', 1),
                    ('seoulfuneral.fwith.kr', '/', 200, 'funeral index.html', 1),
                    ('ansanwreath.fwith.kr', '/2.html', 200, 'ansan 2.html', 1),
                    ('seoulwreath.fwith.kr', '/missing', 404, 'seoul 404.html', 1),
                    ('ansanwreath.fwith.kr', '/_sfv5/sites/seoul/index.html', 404, 'Not found', 1),
                    ('wreath.fwith.kr', '/', 404, 'Not found', 1),
                    ('preview.workers.dev', '/', 404, 'Not found', 1),
                    ('ansanwreath.fwith.kr', '/robots.txt', 200, 'Disallow: /', 1),
                    ('ansanwreath.fwith.kr', '/sitemap.xml', 404, 'Not found', 1),
                    ('ansanwreath.fwith.kr', path, 200, 'body{color:red}', 0),
                    ('seoulwreath.fwith.kr', path, 200, 'body{color:red}', 0),
                    ('ansanwreath.fwith.kr', path.replace('site.css', 'photo.svg'), 200, '<svg', 0),
                    ('ansanwreath.fwith.kr', '/_sfv5/assets/not-present.png', 404, '', 0),
                    ('ansanwreath.fwith.kr', '/__v5_event', 404, 'Not found', 1),
                ]:
                    before = count()
                    actual, body, headers = get(host, route)
                    delta = count() - before
                    assert (actual, expected in body, delta) == (status, True, invocations), (host, route, actual, body, delta)
                    assert 'noindex' in {k.lower(): v for k, v in headers.items()}.get('x-robots-tag', ''), (host, route, headers)
                    results.append({'host': host, 'path': route, 'status': actual, 'localHandlerEntries': delta})
                # Negative control: without Worker dispatch, a root asset is identical on both hosts.
                (bundle / 'public/index.html').write_text('same root for every hostname')
                config['assets']['run_worker_first'] = False
                config['assets']['html_handling'] = 'auto-trailing-slash'
                config_file.write_text(json.dumps(config))
                for _ in range(40):  # Bounded local config reload only.
                    time.sleep(.25)
                    if get('ansanwreath.fwith.kr', '/')[1] == 'same root for every hostname':
                        break
                before = count()
                a = get('ansanwreath.fwith.kr', '/')
                b = get('seoulwreath.fwith.kr', '/')
                assert a[0] == b[0] == 200 and a[1] == b[1] == 'same root for every hostname'
                assert count() == before
                results.append({'negativeControl': 'asset-first same / on two hosts', 'sameBody': True, 'localHandlerEntries': 0})
                # Re-enable host dispatch in production mode, still only on localhost.
                (bundle / 'public/index.html').unlink()
                (bundle / 'public/_headers').write_text('/_sfv5/sites/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n')
                entrypoint = bundle / 'worker.js'
                entrypoint.write_text(entrypoint.read_text().replace('production: false', 'production: true'))
                config['assets'].update(run_worker_first=['/*', '!/_sfv5/assets/*'], html_handling='none')
                config_file.write_text(json.dumps(config))
                for _ in range(40):
                    time.sleep(.25)
                    status, body, headers = get('ansanwreath.fwith.kr', '/')
                    if status == 200 and 'ansan index.html' in body and not any(k.lower() == 'x-robots-tag' for k in headers):
                        break
                for host, route, expected, invocation in [
                    ('ansanwreath.fwith.kr', '/', 'ansan index.html', 1),
                    ('seoulwreath.fwith.kr', '/', 'seoul index.html', 1),
                    ('ansanwreath.fwith.kr', '/robots.txt', 'Allow: /', 1),
                    ('ansanwreath.fwith.kr', '/sitemap.xml', 'https://ansanwreath.fwith.kr/', 1),
                    ('seoulwreath.fwith.kr', '/rss.xml', 'https://seoulwreath.fwith.kr/', 1),
                    ('ansanwreath.fwith.kr', path, 'body{color:red}', 0),
                ]:
                    before = count(); status, body, headers = get(host, route); delta = count() - before
                    assert status == 200 and expected in body and delta == invocation, (host, route, status, body, delta)
                    assert not any(k.lower() == 'x-robots-tag' for k in headers), headers
                    results.append({'mode': 'production-prepared-local-only', 'host': host, 'path': route,
                                    'status': status, 'localHandlerEntries': delta})
            finally:
                # Windows npm is a process tree; stop only this exact process tree.
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
                else:
                    process.terminate()
                process.wait(timeout=10)
                time.sleep(.5)
        report = {'runtime': 'Wrangler 4.148.0 --local', 'productionRequests': 0,
                  'edgeBillingVerified': False, 'transformRuleOrderVerified': False, 'checks': results}
        destination = ROOT / 'reports/shared-static-local.json'
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
