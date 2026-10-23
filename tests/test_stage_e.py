import json
import unittest
from pathlib import Path
from unittest.mock import patch
from v5.config import read_site,ConfigError
from v5.deploy import preflight,worker_config
from v5.engine import build

class StageE(unittest.TestCase):
    def test_live_publish_guard_blocks_unreviewed_site(self):
        gate=preflight('ansan-promotion-plant')
        self.assertFalse(gate['ready'])
        self.assertGreaterEqual(len(gate['blockers']),3)
        with self.assertRaises(ConfigError):worker_config('ansan-promotion-plant')
        with self.assertRaises(ConfigError):build('ansan-promotion-plant',mode='publish')
    def test_conditional_worker_config_exact_html_and_404(self):
        state=read_site('ansan-promotion-plant')
        state['site']['workerName']='v5-demo-site'
        with patch('v5.deploy.read_site',return_value=state), patch('v5.deploy.preflight',return_value={'ready':True}):
            conf=worker_config('ansan-promotion-plant')
        self.assertEqual(conf['assets']['html_handling'],'none')
        self.assertEqual(conf['assets']['not_found_handling'],'404-page')
        self.assertEqual(conf['assets']['run_worker_first'],['/'])
        self.assertEqual(conf['assets']['directory'],'../../dist/ansan-promotion-plant')
        self.assertNotIn('api_token',json.dumps(conf).lower())

if __name__=='__main__':unittest.main()
