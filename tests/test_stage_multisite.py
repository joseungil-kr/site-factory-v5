import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from v5.config import ConfigError,read_site
from v5.scaffold import scaffold
from v5.dashboard import dashboard

class MultiSite(unittest.TestCase):
    def test_new_customer_has_no_inherited_pages_products_or_domain(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            kwargs=dict(site_id='demo-skycar',brand='가상 스카이차',keyword='스카이차',region='안산시',phone='031-123-4567',sites_dir=root)
            r=scaffold(**kwargs)
            self.assertFalse(r['created'])
            self.assertFalse((root/'demo-skycar').exists())
            r=scaffold(**kwargs,apply=True)
            self.assertTrue(r['created'])
            p=root/'demo-skycar'
            self.assertEqual(json.loads((p/'pages.json').read_text()),[])
            self.assertEqual(json.loads((p/'products.json').read_text()),[])
            self.assertFalse(json.loads((p/'site.json').read_text())['publishEnabled'])
            with patch('v5.config.SITES',root):
                data=read_site('demo-skycar')
            self.assertEqual(data['site']['status'],'draft')
    def test_existing_customer_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            args=('duplicate-demo','브랜드','주제','지역','031-123-4567')
            scaffold(*args,apply=True,sites_dir=Path(t))
            with self.assertRaises(ConfigError):scaffold(*args,apply=True,sites_dir=Path(t))
    def test_id_escape_is_blocked(self):
        with self.assertRaises(ConfigError):scaffold('../escape','A','B','C','031-123-4567',apply=True)

if __name__=='__main__':unittest.main()
