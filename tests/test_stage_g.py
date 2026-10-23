import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from v5.config import read_site
from v5.engine import build
from v5.audit import audit
from v5.operations import prepare_global_change


class StageG(unittest.TestCase):
    def test_three_designs_share_content_and_use_separate_styles(self):
        data=read_site('ansan-promotion-plant')
        fingerprints=[]
        with tempfile.TemporaryDirectory() as t:
            for theme in ('classic','modern','minimal'):
                modified,_=prepare_global_change(data,'theme',theme)
                out=Path(t)/theme
                with patch('v5.engine.read_site',return_value=modified), patch('v5.audit.read_site',return_value=modified):
                    result=build('ansan-promotion-plant',output=out,reports=Path(t)/(theme+'-reports'))
                self.assertIn(f'theme-{theme}.css',(out/'index.html').read_text(encoding='utf-8'))
                fingerprints.append(result['manifest']['contentHashes'])
        self.assertEqual(fingerprints[0],fingerprints[1])
        self.assertEqual(fingerprints[1],fingerprints[2])
    def test_optional_local_site_search_index(self):
        data=read_site('ansan-promotion-plant')
        custom=copy.deepcopy(data);custom['site']['siteSearch']['enabled']=True
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'built';reports=Path(t)/'reports'
            with patch('v5.engine.read_site',return_value=custom),patch('v5.audit.read_site',return_value=custom):
                result=build('ansan-promotion-plant',output=out,reports=reports)
                check=audit('ansan-promotion-plant',output=out,write_report=False)
            self.assertEqual(check['errors'],[])
            self.assertTrue((out/'search.html').exists())
            self.assertTrue((out/'assets/search.js').exists())
            idx=json.loads((out/'search-index.json').read_text(encoding='utf-8'))
            self.assertEqual(len(idx),10)
            self.assertNotIn('window.location', (out/'assets/search.js').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
