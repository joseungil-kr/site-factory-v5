"""Offline-only shared Worker preview for explicitly opted-in new V5 sites."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from .config import ROOT, ConfigError, read_site
from .engine import build

ASSET_PREFIX = '/_sfv5/assets/'
PRIVATE_PREFIX = '/_sfv5/sites/'


def rewrite_assets(text, hostname, prefix):
    # Match the generator's quoted URLs/CSS url() without changing external order URLs.
    pattern = r'([\x22\x27(])(?:/assets/|https://' + re.escape(hostname) + r'/assets/)'
    return re.sub(pattern, lambda m: m[1] + prefix, text)


def assemble(entries, destination, *, limit=18000, production=False, worker_name=None):
    """Package already audited builds; never deploy or change source files."""
    destination = Path(destination).resolve()
    if destination.exists():
        raise ConfigError('Shared preview destination already exists')
    if not 1 <= limit <= 20000:
        raise ConfigError('Shared asset limit must be between 1 and 20000')
    hosts = {}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as work:
        out = Path(work) / 'bundle'
        assets = out / 'public'
        assets.mkdir(parents=True)
        for site_id, hostname, source in entries:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', site_id):
                raise ConfigError('Invalid shared site ID')
            if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}', hostname):
                raise ConfigError('Invalid shared hostname')
            if hostname in hosts or any(x['id'] == site_id for x in hosts.values()):
                raise ConfigError('Duplicate shared host or site ID')
            source = Path(source)
            files = sorted(p for p in source.rglob('*') if p.is_file())
            if any(p.is_symlink() or source.resolve() not in p.resolve().parents for p in files):
                raise ConfigError('Shared preview cannot include symlinks')
            if not (source / 'index.html').is_file() or not (source / '404.html').is_file():
                raise ConfigError('Missing home or custom 404')
            digest = hashlib.sha256()
            for p in files:
                if p.relative_to(source).parts[0] == 'assets':
                    raw = p.read_bytes()
                    if p.suffix.lower() in {'.css', '.js'}:
                        raw = rewrite_assets(raw.decode('utf-8'), hostname, '/__SHARED_BUNDLE__/').encode('utf-8')
                    digest.update(p.relative_to(source).as_posix().encode() + b'\0' + raw)
            prefix = ASSET_PREFIX + digest.hexdigest() + '/'
            allowed = []
            for p in files:
                name = p.relative_to(source).as_posix()
                if name.startswith('assets/'):
                    if p.suffix.lower() not in {'.css', '.js', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.woff', '.woff2'}:
                        raise ConfigError('Only public presentation assets may bypass the Worker')
                    target = assets / prefix.lstrip('/') / name[7:]
                    raw = p.read_bytes()
                    if p.suffix.lower() in {'.css', '.js'}:
                        raw = rewrite_assets(raw.decode('utf-8'), hostname, prefix).encode('utf-8')
                else:
                    if name.startswith('_') or p.name in {'_headers', '_redirects', '.assetsignore'}:
                        raise ConfigError('Reserved filename in shared site')
                    target = assets / PRIVATE_PREFIX.lstrip('/') / site_id / name
                    raw = p.read_bytes()
                    if p.suffix.lower() in {'.html', '.json', '.xml', '.txt'}:
                        raw = rewrite_assets(raw.decode('utf-8'), hostname, prefix).encode('utf-8')
                    allowed.append('/' + name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            hosts[hostname] = {'id': site_id, 'paths': allowed}
        if not hosts:
            raise ConfigError('At least one new site is required')
        (assets / '_headers').write_text(
            ('/_sfv5/sites/*' if production else '/*') + '\n  X-Robots-Tag: noindex, nofollow, noarchive\n'
            + ASSET_PREFIX + '*\n  Cache-Control: public, max-age=31536000, immutable\n', encoding='utf-8')
        count = sum(p.is_file() and p.name != '_headers' for p in assets.rglob('*'))
        if count > limit:
            raise ConfigError(f'Shared Worker asset limit exceeded: {count} > {limit}')
        shutil.copyfile(ROOT / 'worker/shared-static.js', out / 'shared-static.js')
        (out / 'hosts.json').write_text(json.dumps(hosts, ensure_ascii=False), encoding='utf-8')
        (out / 'worker.js').write_text("import {createSharedWorker} from './shared-static.js';\nimport hosts from './hosts.json';\nexport default createSharedWorker(hosts, {production: " + str(production).lower() + "});\n", encoding='utf-8')
        config = {
            'name': worker_name or 'sfv5-new-sites-shared-preview', 'compatibility_date': '2026-10-13',
            'main': 'worker.js', 'workers_dev': False, 'preview_urls': False,
            'assets': {'directory': './public', 'binding': 'ASSETS',
                       'html_handling': 'none', 'not_found_handling': 'none',
                       'run_worker_first': ['/*', '!' + ASSET_PREFIX + '*']}}
        (out / 'wrangler.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        report = {'mode': 'production-prepared' if production else 'preview-only', 'assetFileCount': count, 'hosts': hosts,
                  'productionReady': False, 'edgeInvocationSavingsVerified': False,
                  'htmlRequestsUseWorker': True, 'analyticsEnabled': False}
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        out.rename(destination)
    return report


def prepare(site_ids, destination):
    entries = []
    # Keep existing domains and release gates outside this experimental adapter.
    with tempfile.TemporaryDirectory(prefix='sfv5-shared-') as work:
        for site_id in site_ids:
            data = read_site(site_id)
            site = data['site']
            if (site.get('deliveryMode') != 'shared-static-preview' or site.get('workerName')
                    or site.get('publishEnabled') or site.get('publicIndexingApproved')
                    or not (ROOT / 'sites' / site_id / 'site-spec.json').is_file()):
                raise ConfigError('Only explicitly opted-in new unpublished sites may use shared preview')
            if site.get('analytics', {}).get('enabled'):
                raise ConfigError('Shared preview analytics must be disabled; events consume Worker requests')
            origin = urlsplit(site.get('domain') or '')
            if origin.scheme != 'https' or not origin.hostname or origin.netloc != origin.hostname or origin.path not in ('', '/') or origin.query or origin.fragment:
                raise ConfigError('New shared site requires an exact HTTPS hostname')
            plan = json.loads((ROOT / 'sites' / site_id / 'site-spec.json').read_text(encoding='utf-8'))
            if (plan.get('domain') or '').rstrip('/') != site['domain'].rstrip('/'):
                raise ConfigError('Shared site domain must match its approved site plan')
            for existing in (ROOT / 'sites').glob('*/site.json'):
                if existing.parent.name != site_id:
                    other = json.loads(existing.read_text(encoding='utf-8'))
                    if urlsplit(other.get('domain') or '').hostname == origin.hostname:
                        raise ConfigError('Hostname already belongs to another V5 site')
            output = Path(work) / site_id
            build(site_id, output=output, reports=Path(work) / (site_id + '-reports'), mode='preview', preserve_previous=False)
            entries.append((site_id, origin.hostname, output))
        return assemble(entries, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', action='append', required=True)
    parser.add_argument('--output', required=True, help='New directory under dist/')
    args = parser.parse_args()
    destination = Path(args.output).resolve()
    if not destination.is_relative_to(ROOT / 'dist') or destination == ROOT / 'dist':
        parser.error('Output must be a new directory under dist/')
    try:
        print(json.dumps(prepare(args.site, destination), ensure_ascii=False, indent=2))
    except ConfigError as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
