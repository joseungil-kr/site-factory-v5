import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from v5.config import ConfigError,ROOT
from v5.engine import build
from v5.staging import staging_preflight,staging_config,staging_check,write_staging_config

SITE='ansan-promotion-plant'

class StagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build(SITE,mode='preview')

    def test_preview_only_and_isolated_worker(self):
        gate=staging_preflight(SITE)
        self.assertTrue(gate['ready'],gate)
        cfg=staging_config(SITE)
        self.assertTrue(cfg['workers_dev'])
        self.assertEqual(cfg['vars']['V5_STAGING'],'1')
        self.assertTrue(cfg['assets']['run_worker_first'])
        self.assertEqual(cfg['assets']['html_handling'],'none')
        self.assertIn('ansan-promotion-plant',cfg['name'])
        self.assertNotIn('flower-matrix-',cfg['name'])
        self.assertFalse(cfg['preview_urls'])

    def test_staging_config_written_outside_sources(self):
        path=Path(write_staging_config(SITE))
        self.assertTrue(path.is_file())
        self.assertTrue(path.is_relative_to(ROOT/'deploy'))
        self.assertNotIn('CLOUDFLARE_API_TOKEN',path.read_text())

    def test_reject_publish_or_modified_manifest(self):
        from v5.staging import staging_preflight
        from v5.engine import report_dir
        path=report_dir(SITE)/'manifest.json'
        old=path.read_bytes()
        try:
            import json
            d=json.loads(old);d['mode']='publish'
            path.write_text(json.dumps(d),encoding='utf-8')
            self.assertFalse(staging_preflight(SITE)['ready'])
        finally:path.write_bytes(old)

    def test_public_verifier_rejects_unrelated_origin_without_network(self):
        for url in ('http://other.workers.dev','https://google.com','https://evil.workers.dev',
                    'https://sfv5-ansan-promotion-plant-preview.account.workers.dev.evil.tld'):
            with self.assertRaises(ConfigError):staging_check(SITE,url)

    def test_reference_images_render_but_are_not_a_publish_approval(self):
        first=(ROOT/'dist'/SITE/'index.html').read_text(encoding='utf-8')
        self.assertIn('임시 시안',first)
        self.assertIn('판매처 참고사진',first)
        self.assertIn('noindex,nofollow',first)
        self.assertNotIn('rel="canonical"',first)

if __name__=='__main__':unittest.main()
