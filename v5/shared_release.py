"""Prepare and recover new-site production artifacts offline. Never deploy or bind domains."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile
from .config import ROOT, ConfigError, read_site
from .engine import build
from .markup import url_path, h
from .shared_static import assemble
from .site_plan import validate_plan


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def file_hashes(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in sorted(root.rglob('*'))
            if p.is_file() and p.relative_to(root).as_posix() not in {'release.json', 'release.zip', 'snapshot.json'}}


def verify_snapshot(root, manifest):
    snapshot = root / 'release.zip'
    sidecar = root / 'snapshot.json'
    if not snapshot.is_file() or not sidecar.is_file():
        raise ConfigError('Shared release requires its recovery ZIP and snapshot hash record')
    expected = {'releaseHash': manifest['releaseHash'], 'sha256': file_sha(snapshot)}
    if json.loads(sidecar.read_text(encoding='utf-8')) != expected:
        raise ConfigError('Recovery ZIP SHA-256 mismatch')
    try:
        with ZipFile(snapshot) as archive:
            names = list(manifest['files']) + ['release.json']
            if len(archive.namelist()) != len(set(archive.namelist())) or set(archive.namelist()) != set(names):
                raise ConfigError('Recovery ZIP has unexpected or duplicate members')
            if json.loads(archive.read('release.json')) != manifest:
                raise ConfigError('Recovery ZIP release identity mismatch')
            for name, expected_hash in manifest['files'].items():
                if sha(archive.read(name)) != expected_hash:
                    raise ConfigError('Recovery ZIP member hash mismatch: ' + name)
    except (BadZipFile, OSError, RuntimeError, KeyError) as exc:
        raise ConfigError('Recovery ZIP content verification failed: ' + str(exc)) from exc


def add_feed(output, data):
    if (output / 'rss.xml').exists():
        raise ConfigError('Generated RSS path already exists; refusing to overwrite source output')
    site = data['site']; origin = site['domain'].rstrip('/')
    root = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(root, 'channel')
    for key, value in [('title', site['siteTitle']), ('link', origin + '/'),
                       ('description', site['siteTitle']), ('language', 'ko-KR')]:
        ET.SubElement(channel, key).text = value
    for page in sorted(data['pages'], key=lambda x: x['number'], reverse=True)[:50]:
        item = ET.SubElement(channel, 'item')
        for key, value in [('title', page['title']), ('link', origin + url_path(page['number'])),
                           ('description', page['intro'])]:
            ET.SubElement(item, key).text = value
        ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = origin + url_path(page['number'])
    (output / 'rss.xml').write_bytes(ET.tostring(root, encoding='utf-8', xml_declaration=True))
    tag = '<link rel="alternate" type="application/rss+xml" title="' + h(site['siteTitle']) + '" href="' + h(origin + '/rss.xml') + '">'
    for page in output.glob('*.html'):
        text = page.read_text(encoding='utf-8')
        if text.count('</head>') != 1:
            raise ConfigError('Unexpected generator HTML head: ' + page.name)
        page.write_text(text.replace('</head>', tag + '</head>'), encoding='utf-8')


def promote_service(output, data):
    """Add approved host SEO to a derivative of the unchanged service preview output."""
    site = data['site']; origin = site['domain']
    if (output / 'sitemap.xml').exists():
        raise ConfigError('Service source already has a sitemap; refusing to overwrite it')
    sitemap = ET.Element('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    for page in data['pages']:
        from .markup import filename
        target = output / filename(page['number'])
        text = target.read_text(encoding='utf-8')
        old = '<meta name="robots" content="noindex,nofollow">'
        if text.count(old) != 1 or 'rel="canonical"' in text:
            raise ConfigError('Service preview SEO differs from the existing renderer contract')
        location = origin + url_path(page['number'])
        metadata = '<meta name="robots" content="index,follow"><link rel="canonical" href="' + h(location) + '">'
        if page['number'] == 1 and site.get('naverSiteVerification'):
            token = site['naverSiteVerification']
            if not isinstance(token, str) or not re.fullmatch(r'[0-9a-fA-F]{40}', token):
                raise ConfigError('Invalid service Naver verification token')
            metadata += '<meta name="naver-site-verification" content="' + token + '">'
        text = text.replace(old, metadata)
        target.write_text(text, encoding='utf-8')
        ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = location
    (output / 'sitemap.xml').write_bytes(ET.tostring(sitemap, encoding='utf-8', xml_declaration=True))
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + origin + '/sitemap.xml\n', encoding='utf-8')


def verify_seo(root, hosts):
    """Check packaged host-specific SEO and feed URLs without network requests."""
    for hostname, site in hosts.items():
        origin = 'https://' + hostname
        directory = root / 'public/_sfv5/sites' / site['id']
        sitemap = ET.parse(directory / 'sitemap.xml')
        locations = [x.text for x in sitemap.findall('.//{*}loc')]
        if not locations or len(locations) != len(set(locations)):
            raise ConfigError('Missing or duplicate sitemap URLs')
        for location in locations:
            parsed = urlsplit(location)
            if parsed.scheme != 'https' or parsed.netloc != hostname or parsed.query or parsed.fragment:
                raise ConfigError('Cross-host sitemap URL')
            path = unquote(parsed.path)
            name = 'index.html' if path == '/' else path.lstrip('/')
            if '/' + name not in site['paths']:
                raise ConfigError('Sitemap points outside host files')
            text = (directory / name).read_text(encoding='utf-8')
            if ('<link rel="canonical" href="' + h(location) + '">') not in text or '<meta name="robots" content="index,follow">' not in text:
                raise ConfigError('Production canonical/robots mismatch: ' + location)
        if (directory / 'robots.txt').read_text(encoding='utf-8') != 'User-agent: *\nAllow: /\nSitemap: ' + origin + '/sitemap.xml\n':
            raise ConfigError('Production robots mismatch')
        for name in ('404.html', 'search.html'):
            if (directory / name).is_file() and '<meta name="robots" content="noindex,nofollow">' not in (directory / name).read_text(encoding='utf-8'):
                raise ConfigError('404/search must remain noindex')
        rss = ET.parse(directory / 'rss.xml')
        if rss.findtext('./channel/link') != origin + '/':
            raise ConfigError('RSS channel host mismatch')
        guids = []
        for item in rss.findall('./channel/item'):
            link, guid = item.findtext('link'), item.findtext('guid')
            if link not in locations or guid != link:
                raise ConfigError('RSS item is outside canonical sitemap')
            guids.append(guid)
        if not guids or len(guids) != len(set(guids)):
            raise ConfigError('Missing or duplicate RSS GUID')


def verify_release(root):
    root = Path(root)
    manifest = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    if file_hashes(root) != manifest['files']:
        raise ConfigError('Shared release file integrity mismatch')
    expected = sha(json.dumps(manifest['files'], sort_keys=True, separators=(',', ':')).encode())
    if expected != manifest['releaseHash']:
        raise ConfigError('Shared release manifest integrity mismatch')
    config = json.loads((root / 'wrangler.json').read_text(encoding='utf-8'))
    if (config['name'] != manifest['workerName'] or config.get('routes')
            or json.loads((root / 'hosts.json').read_text(encoding='utf-8')) != manifest['hosts']):
        raise ConfigError('Release identity or unbound deployment configuration mismatch')
    verify_seo(root, manifest['hosts'])
    verify_snapshot(root, manifest)
    return manifest


def restore(snapshot, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ConfigError('Restore requires a new directory; previous artifacts are never overwritten')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as work:
        staged = Path(work) / 'restored'; staged.mkdir()
        with ZipFile(snapshot) as archive:
            manifest = json.loads(archive.read('release.json'))
            names = list(manifest['files']) + ['release.json']
            if len(archive.namelist()) != len(set(archive.namelist())) or set(archive.namelist()) != set(names):
                raise ConfigError('Unexpected or duplicate snapshot members')
            for name in names:
                path = PurePosixPath(name)
                if path.is_absolute() or any(x in ('..', '.') for x in path.parts) or '\\' in name or ':' in name:
                    raise ConfigError('Unsafe snapshot member')
                target = staged / name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
        shutil.copyfile(snapshot, staged / 'release.zip')
        (staged / 'snapshot.json').write_text(json.dumps({'releaseHash': manifest['releaseHash'], 'sha256': file_sha(snapshot)}), encoding='utf-8')
        verify_release(staged)
        staged.rename(destination)
    return {'restored': manifest['releaseHash'], 'output': str(destination)}


def prepare_probe(release_directory, destination):
    """Write an isolated edge-test candidate; existence and deployment remain unverified."""
    release_directory = Path(release_directory)
    manifest = verify_release(release_directory)
    destination = Path(destination).resolve()
    if destination.exists():
        raise ConfigError('Probe requires a new directory')
    destination.parent.mkdir(parents=True, exist_ok=True)
    name = 'sfv5-new-sites-probe-' + manifest['releaseHash'][:12]
    with tempfile.TemporaryDirectory(dir=destination.parent) as work:
        probe = Path(work) / 'probe'; probe.mkdir()
        shutil.copytree(release_directory / 'public', probe / 'public')
        (probe / 'public/_headers').write_text('/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n', encoding='utf-8')
        shutil.copyfile(release_directory / 'shared-static.js', probe / 'shared-static.js')
        shutil.copyfile(release_directory / 'hosts.json', probe / 'hosts.json')
        (probe / 'worker.js').write_text(
            "import {createSharedWorker} from './shared-static.js';\nimport hosts from './hosts.json';\n"
            "const adapter = createSharedWorker(hosts, {production: true});\n"
            "export default {async fetch(request, env) {\n"
            "  const host = request.headers.get('X-SFV5-Probe-Host');\n"
            "  const headers = {'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Cache-Control': 'no-store'};\n"
            "  if (!host || !Object.hasOwn(hosts, host)) return new Response('Not found', {status:404, headers});\n"
            "  const url = new URL(request.url); url.hostname = host;\n"
            "  const response = url.pathname === '/robots.txt'\n"
            "    ? new Response('User-agent: *\\nDisallow: /\\n')\n"
            "    : await adapter.fetch(new Request(url, request), env);\n"
            "  const result = new Headers(response.headers);\n"
            "  for (const [key,value] of Object.entries(headers)) result.set(key,value);\n"
            "  return new Response(response.body, {status:response.status,headers:result});\n"
            "}};\n", encoding='utf-8')
        config = json.loads((release_directory / 'wrangler.json').read_text(encoding='utf-8'))
        config.update(name=name, workers_dev=True, preview_urls=False, observability={'enabled': True, 'head_sampling_rate': 1})
        (probe / 'wrangler.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        report = {'candidateWorkerName': name, 'sourceReleaseHash': manifest['releaseHash'],
                  'workerNameAvailabilityVerified': False, 'deploymentExecuted': False,
                  'domainChanges': [], 'productionRoutes': [],
                  'requiredBeforeDeployment': ['Read-only account inventory must prove this exact name absent; stop if present',
                                               'Explicit authorization for this new isolated Worker only',
                                               'No secrets/bindings/cron/custom domains and no existing Worker edits',
                                               'At most 12 bounded probe requests; never follow page links or submit IndexNow',
                                               'Compare Worker invocation logs and account statistics separately; local results do not prove edge billing']}
        (probe / 'probe-plan.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        probe.rename(destination)
    return report


def prepare(site_ids, destination, worker_name, *, previous=None):
    """Use existing publish build gates, retain exact source outputs, prepare a reviewable release."""
    if not re.fullmatch(r'sfv5-new-sites-[a-z0-9-]{1,45}', worker_name):
        raise ConfigError('Use a dedicated sfv5-new-sites-* Worker name, never an existing legacy Worker')
    destination = Path(destination).resolve()
    if destination.exists():
        raise ConfigError('Production artifact destination already exists')
    prior = verify_release(previous) if previous else None
    if prior and prior['workerName'] != worker_name:
        raise ConfigError('Cannot move a previous shared release to another Worker')
    entries = []; builds = []; inputs = {}
    with tempfile.TemporaryDirectory(prefix='sfv5-release-') as work:
        work = Path(work)
        for site_id in site_ids:
            data = read_site(site_id); site = data['site']
            spec_path = ROOT / 'sites' / site_id / 'site-spec.json'
            if site.get('deliveryMode') != 'shared-static' or not spec_path.is_file():
                raise ConfigError('Production sharing requires an explicitly opted-in new site and approved plan')
            spec = json.loads(spec_path.read_text(encoding='utf-8'))
            check = validate_plan(spec, site_id)
            if not check['ready'] or spec.get('publishPolicy', {}).get('mode') != 'publish':
                raise ConfigError('Shared production requires an approved publish site plan')
            if spec['targetPageCount'] != len(data['pages']):
                raise ConfigError('Production page count differs from approved site plan')
            if site.get('workerName') != worker_name:
                raise ConfigError('Shared Worker name must match')
            service = site.get('businessModel') == 'service-lead'
            if service:
                conversion = spec.get('conversion', {})
                if (not site.get('servicePublicationApproved') or not site.get('serviceFactsApproved')
                        or not site.get('imageAssetsApproved') or not site.get('cookiePrivacyReviewed')
                        or site.get('publishEnabled') is not False or conversion.get('mode') != 'phone'
                        or conversion.get('phone') != site['phone']):
                    raise ConfigError('Service publication requires approved facts, images, privacy and the exact phone conversion plan')
            if site.get('analytics', {}).get('enabled') or site.get('publicIndexingApproved'):
                raise ConfigError('Shared release disables analytics and legacy indexing-review mode')
            origin = urlsplit(site.get('domain') or '')
            if origin.scheme != 'https' or origin.netloc != origin.hostname or origin.path or origin.query or origin.fragment:
                raise ConfigError('Production domain must be an exact HTTPS origin without trailing slash')
            if spec.get('domain') != site['domain']:
                raise ConfigError('Production domain differs from approved plan')
            for existing in (ROOT / 'sites').glob('*/site.json'):
                if existing.parent.name not in site_ids:
                    other = json.loads(existing.read_text(encoding='utf-8'))
                    if urlsplit(other.get('domain') or '').hostname == origin.hostname or other.get('workerName') == worker_name:
                        raise ConfigError('Domain or Worker already belongs to a site outside this release')
            # Reuse the full image-governance release gate, including unchanged images.
            from scripts.check_image_origin import load_registered, check_explicit_release_assets
            image_paths = ['assets/library/' + site.get('imageLibrary', site_id) + '/' + name for name in site['imagePool']]
            image_manifest = work / (site_id + '-images.json')
            image_manifest.write_text(json.dumps({'assets': image_paths}), encoding='utf-8')
            image_errors = check_explicit_release_assets(image_manifest, load_registered(ROOT), ROOT)
            if image_errors:
                raise ConfigError('Release image provenance rejected: ' + '; '.join(image_errors[:3]))
            original = work / (site_id + '-original')
            result = build(site_id, output=original, reports=work / (site_id + '-reports'), mode='preview' if service else 'publish', preserve_previous=False)
            from .visitor_copy import require_clean_html
            require_clean_html(original)
            prepared = work / (site_id + '-prepared'); shutil.copytree(original, prepared)
            if service:
                promote_service(prepared, data)
            add_feed(prepared, data)
            if service:
                from .audit import audit
                publication_audit = audit(site_id, output=prepared, write_report=False)
                if publication_audit['errors']:
                    raise ConfigError('Prepared production audit rejected: ' + '; '.join(publication_audit['errors'][:3]))
            entries.append((site_id, origin.hostname, prepared))
            builds.append((site_id, original, result['manifest']))
            inputs[site_id] = data
        bundle = work / 'bundle'
        report = assemble(entries, bundle, production=True, worker_name=worker_name)
        hosts = report['hosts']
        if prior:
            for hostname, old in prior['hosts'].items():
                current = hosts.get(hostname)
                if not current or current['id'] != old['id'] or not set(old['paths']).issubset(current['paths']):
                    raise ConfigError('Shared update cannot remove or reassign previous hosts/URLs')
            # Keep cached old HTML's public asset URLs valid until separately reviewed retirement.
            old_assets = Path(previous) / 'public/_sfv5/assets'
            for old in old_assets.rglob('*'):
                if old.is_file():
                    target = bundle / 'public/_sfv5/assets' / old.relative_to(old_assets)
                    if target.exists() and target.read_bytes() != old.read_bytes():
                        raise ConfigError('Existing immutable asset path changed')
                    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(old, target)
        for site_id, original, manifest in builds:
            shutil.copytree(original, bundle / 'source-builds' / site_id)
            source = bundle / 'source-inputs' / site_id
            source.mkdir(parents=True)
            for name in ('site.json', 'pages.json', 'products.json', 'services.json', 'rates.json',
                         'regions.json', 'links.json', 'special-pages.json', 'site-spec.json'):
                original_input = inputs[site_id]['root'] / name
                if original_input.is_symlink():
                    raise ConfigError('Source ledger symlink is not allowed')
                if original_input.is_file():
                    shutil.copyfile(original_input, source / name)
            (source / 'validated-input.json').write_text(json.dumps({k: v for k, v in inputs[site_id].items() if k != 'root'}, ensure_ascii=False, indent=2), encoding='utf-8')
            (source / 'build-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        asset_count = sum(p.is_file() and p.name != '_headers' for p in (bundle / 'public').rglob('*'))
        if asset_count > 18000:
            raise ConfigError('Shared asset soft limit exceeded after retaining old assets')
        verify_seo(bundle, hosts)
        plan = {'workerName': worker_name, 'productionDeploymentExecuted': False,
                'edgeBillingVerified': False, 'accountWorkerNameAvailabilityVerified': False,
                'proposedCustomDomains': [{'pattern': host, 'custom_domain': True} for host in hosts],
                'pending': ['Read-only account inventory: Worker name and all hosts unused or owned by prior shared release',
                            'Review generated exact-host bindings separately; no wildcard or legacy hostname binding',
                            'Cloudflare isolated edge probe and script upload size verification',
                            'Record prior deployed version ID and asset-complete artifact before an update'],
                'rollback': {'previousReleaseHash': prior['releaseHash'] if prior else None,
                             'previousSnapshotSHA256': file_sha(Path(previous) / 'release.zip') if prior else None,
                             'cloudflareVersionID': None, 'firstReleaseRequiresUnusedWorker': prior is None}}
        (bundle / 'deployment-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
        report.update(mode='production-prepared', assetFileCount=asset_count, productionReady=False,
                      deploymentPrepared=True, sourceBuildsPreserved=True)
        (bundle / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        files = file_hashes(bundle)
        manifest = {'version': 1, 'workerName': worker_name, 'hosts': hosts, 'files': files,
                    'releaseHash': sha(json.dumps(files, sort_keys=True, separators=(',', ':')).encode())}
        (bundle / 'release.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        with ZipFile(bundle / 'release.zip', 'w', ZIP_DEFLATED) as archive:
            for name in list(files) + ['release.json']:
                archive.write(bundle / name, name)
        (bundle / 'snapshot.json').write_text(json.dumps({'releaseHash': manifest['releaseHash'], 'sha256': file_sha(bundle / 'release.zip')}), encoding='utf-8')
        verify_release(bundle)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as staging:
            staged = Path(staging) / 'release'
            shutil.copytree(bundle, staged)
            staged.rename(destination)
    return {'releaseHash': manifest['releaseHash'], 'assetFileCount': asset_count,
            'output': str(destination), 'deploymentPrepared': True, 'deploymentExecuted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('prepare')
    command.add_argument('--site', action='append', required=True)
    command.add_argument('--worker', required=True)
    command.add_argument('--output', required=True)
    command.add_argument('--previous')
    command = commands.add_parser('verify'); command.add_argument('directory')
    command = commands.add_parser('restore'); command.add_argument('snapshot'); command.add_argument('--output', required=True)
    command = commands.add_parser('probe'); command.add_argument('directory'); command.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'verify':
            result = verify_release(args.directory)
            result = {'releaseHash': result['releaseHash'], 'verified': True}
        else:
            output = Path(args.output).resolve()
            if not output.is_relative_to(ROOT / 'dist') or output == ROOT / 'dist':
                raise ConfigError('CLI output must be a new directory under dist/')
            if args.command == 'prepare':
                result = prepare(args.site, output, args.worker, previous=args.previous)
            elif args.command == 'probe':
                result = prepare_probe(args.directory, output)
            else:
                result = restore(args.snapshot, output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ConfigError, OSError, ValueError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
