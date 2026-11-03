import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
from v5.config import ConfigError
from v5.engine import sha
from v5.site_plan import initial_spec
from v5 import shared_release as release


class SharedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.worker = 'sfv5-new-sites-fixture'
        self.image_marker = 'v1'
        self.ids = ['new-a', 'new-b']
        self.data = {}
        for site_id in self.ids:
            source = self.root / 'sites' / site_id
            source.mkdir(parents=True)
            domain = 'https://' + site_id + '.example.test'
            site = {'id': site_id, 'siteTitle': site_id + ' flowers', 'domain': domain,
                    'workerName': self.worker, 'deliveryMode': 'shared-static', 'publishEnabled': True,
                    'imagePool': ['photo.svg'], 'analytics': {'enabled': False}}
            spec = initial_spec(site_id, 'Brand', 'flower', 'Seoul', '1844-0644')
            spec.update(domain=domain, approved=True, businessModel='webshop',
                        serviceScope={'region': 'Seoul', 'granularity': 'city'}, pageTypes=['city'],
                        targetPageCount=2, titlePattern='{region} flower', urlPattern='/{number}.html',
                        publishPolicy={'mode': 'publish'})
            for name, value in [('site.json', site), ('site-spec.json', spec)]:
                (source / name).write_text(json.dumps(value), encoding='utf-8')
            self.data[site_id] = {'site': site, 'root': source, 'pages': [
                {'number': 1, 'title': site_id + ' home', 'intro': 'home text'},
                {'number': 2, 'title': site_id + ' detail', 'intro': 'detail text'}]}
        self.patches = [patch.object(release, 'ROOT', self.root),
                        patch.object(release, 'read_site', side_effect=lambda key: self.data[key]),
                        patch.object(release, 'build', side_effect=self.fake_publish_build),
                        patch('scripts.check_image_origin.load_registered', return_value={}),
                        patch('scripts.check_image_origin.check_explicit_release_assets', return_value=[])]
        for p in self.patches:
            p.start(); self.addCleanup(p.stop)

    def fake_publish_build(self, site_id, *, output, reports, mode, preserve_previous):
        self.assertEqual(mode, 'publish')
        self.assertFalse(preserve_previous)
        output.mkdir(); (output / 'assets').mkdir()
        (output / 'assets/photo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><!--' + self.image_marker + '--></svg>')
        origin = self.data[site_id]['site']['domain']
        for name, path in [('index.html', '/'), ('2.html', '/2.html')]:
            (output / name).write_text('<html><head><meta name="robots" content="index,follow"><link rel="canonical" href="' + origin + path + '"></head><body><a href="tel:18440644">Call</a><a href="https://fwith.co.kr/assets/order">Order</a><img src="/assets/photo.svg"></body></html>', encoding='utf-8')
        (output / '404.html').write_text('<html><head><meta name="robots" content="noindex,nofollow"></head><body>Page not found</body></html>')
        (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + origin + '/sitemap.xml\n')
        (output / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + origin + '/</loc></url><url><loc>' + origin + '/2.html</loc></url></urlset>')
        return {'manifest': {'mode': mode, 'files': {p.relative_to(output).as_posix(): sha(p.read_bytes()) for p in output.rglob('*') if p.is_file()}}}

    def prepare(self, name, previous=None, ids=None):
        target = self.root / name
        release.prepare(ids or self.ids, target, self.worker, previous=previous)
        return target

    def test_production_preparation_seo_rss_source_preservation_and_restore(self):
        target = self.prepare('first')
        manifest = release.verify_release(target)
        config = json.loads((target / 'wrangler.json').read_text())
        self.assertFalse(config['workers_dev'])
        self.assertNotIn('routes', config)
        plan = json.loads((target / 'deployment-plan.json').read_text())
        self.assertFalse(plan['productionDeploymentExecuted'])
        self.assertFalse(plan['accountWorkerNameAvailabilityVerified'])
        self.assertEqual(len(plan['proposedCustomDomains']), 2)
        for site_id in self.ids:
            original = target / 'source-builds' / site_id
            saved = json.loads((target / 'source-inputs' / site_id / 'build-manifest.json').read_text())
            self.assertEqual(saved['files'], {p.relative_to(original).as_posix(): sha(p.read_bytes()) for p in original.rglob('*') if p.is_file()})
            self.assertNotIn('application/rss+xml', (original / 'index.html').read_text())
            packed = (target / 'public/_sfv5/sites' / site_id / 'index.html').read_text()
            self.assertIn('application/rss+xml', packed)
            self.assertIn('https://fwith.co.kr/assets/order', packed)
        restored = self.root / 'restored'
        release.restore(target / 'release.zip', restored)
        self.assertEqual(release.verify_release(restored)['releaseHash'], manifest['releaseHash'])
        with self.assertRaises(ConfigError):
            release.restore(target / 'release.zip', restored)

    def test_tamper_and_unsafe_snapshot_are_rejected(self):
        target = self.prepare('first')
        (target / 'worker.js').write_text('tampered')
        with self.assertRaises(ConfigError):
            release.verify_release(target)
        snapshot = self.root / 'unsafe.zip'
        with ZipFile(snapshot, 'w') as archive:
            archive.writestr('release.json', json.dumps({'files': {'../outside.txt': 'x'}}))
            archive.writestr('../outside.txt', 'bad')
        with self.assertRaises(ConfigError):
            release.restore(snapshot, self.root / 'unsafe-restore')
        self.assertFalse((self.root / 'outside.txt').exists())

    def test_updates_preserve_hosts_and_old_assets(self):
        first = self.prepare('first')
        old_paths = {p.relative_to(first / 'public').as_posix() for p in (first / 'public/_sfv5/assets').rglob('*') if p.is_file()}
        self.image_marker = 'v2'
        second = self.prepare('second', previous=first)
        self.assertTrue(all((second / 'public' / path).is_file() for path in old_paths))
        self.assertGreater(len(list((second / 'public/_sfv5/assets').glob('*/photo.svg'))), len(old_paths))
        with self.assertRaises(ConfigError):
            self.prepare('missing-host', previous=first, ids=['new-a'])

    def test_collision_and_image_provenance_fail_before_build(self):
        collision = self.root / 'sites/existing'; collision.mkdir()
        (collision / 'site.json').write_text(json.dumps({'domain': self.data['new-a']['site']['domain']}))
        with self.assertRaises(ConfigError):
            self.prepare('collision')
        (collision / 'site.json').write_text('{}')
        with patch('scripts.check_image_origin.check_explicit_release_assets', return_value=['missing proof']):
            with self.assertRaisesRegex(ConfigError, 'provenance'):
                self.prepare('unapproved-images')

    def test_standard_per_site_release_cannot_overwrite_shared_worker(self):
        from v5.deploy import preflight, worker_config
        from v5.config import read_site
        data = read_site('ansan-promotion-plant')
        data['site']['deliveryMode'] = 'shared-static'
        with patch('v5.deploy.read_site', return_value=data):
            self.assertTrue(any('overwrite the shared Worker' in x for x in preflight('new-a')['blockers']))
            with self.assertRaisesRegex(ConfigError, 'shared_release'):
                worker_config('new-a')

    def test_feed_path_collision_cannot_overwrite_original(self):
        source = self.root / 'source'; source.mkdir()
        (source / 'rss.xml').write_text('original')
        with self.assertRaises(ConfigError):
            release.add_feed(source, self.data['new-a'])
        self.assertEqual((source / 'rss.xml').read_text(), 'original')

    def test_existing_publish_generator_is_reused_with_original_html_preserved(self):
        from copy import deepcopy
        from v5.config import read_site
        from v5.engine import build as real_build
        data = deepcopy(read_site('ansan-promotion-plant'))
        images = data['site']['imagePool'][:]
        site_id = 'new-a'
        data['root'] = self.data[site_id]['root']
        data['site'].update(self.data[site_id]['site'])
        data['site'].update(source='Synthetic local regression fixture only', imageAssetsApproved=True,
                            cookiePrivacyReviewed=True, imagePool=images)
        # The legacy demo has draft price prose; this synthetic new-site fixture uses only clean pages.
        data['pages'] = data['pages'][:2]
        data['special'] = []; data['links'] = []
        data['site']['navigation'] = [{'label': 'Home', 'href': '/'}]
        for product in data['products']:
            product['verifiedLive'] = True  # Test fixture only; no real product approval is recorded.
        self.data[site_id] = data
        spec_path = data['root'] / 'site-spec.json'
        spec = json.loads(spec_path.read_text()); spec['targetPageCount'] = len(data['pages'])
        spec_path.write_text(json.dumps(spec))
        (self.data['new-b']['root'] / 'site.json').write_text(json.dumps({'workerName': 'sfv5-new-sites-other'}))
        with patch.object(release, 'build', side_effect=real_build), patch('v5.engine.read_site', return_value=data), patch('v5.audit.read_site', return_value=data):
            target = self.prepare('real-generator', ids=[site_id])
        self.assertEqual(len(release.verify_release(target)['hosts']), 1)
        original = target / 'source-builds' / site_id / 'index.html'
        self.assertIn('https://new-a.example.test/', original.read_text())

    def test_probe_is_unbound_noindex_and_availability_is_not_claimed(self):
        target = self.prepare('first')
        probe = self.root / 'probe'
        report = release.prepare_probe(target, probe)
        config = json.loads((probe / 'wrangler.json').read_text())
        self.assertFalse(report['workerNameAvailabilityVerified'])
        self.assertFalse(report['deploymentExecuted'])
        self.assertEqual(report['candidateWorkerName'], config['name'])
        self.assertNotIn('routes', config)
        self.assertTrue(config['workers_dev'])
        self.assertIn('noindex', (probe / 'public/_headers').read_text())
        self.assertNotIn('X-SFV5-Probe-Host', (target / 'worker.js').read_text())
