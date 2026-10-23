import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from v5.config import ConfigError,read_site
from v5.engine import build
from v5.audit import audit
from v5.deploy import worker_config

class Analytics(unittest.TestCase):
    def test_disabled_by_default_no_server_or_browser_collection(self):
        p=read_site('ansan-promotion-plant')
        self.assertFalse(p['site']['analytics']['enabled'])
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'site'
            build('ansan-promotion-plant',output=out,reports=Path(t)/'reports')
            self.assertFalse((out/'assets/analytics.js').exists())
            self.assertNotIn('src="/assets/analytics.js"',(out/'index.html').read_text(encoding='utf-8'))
    def test_opt_in_event_hook_requires_reviewed_site(self):
        base=read_site('ansan-promotion-plant');data=copy.deepcopy(base)
        data['site']['analytics']['enabled']=True
        data['site']['cookiePrivacyReviewed']=True
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'site'
            with patch('v5.engine.read_site',return_value=data),patch('v5.audit.read_site',return_value=data):
                build('ansan-promotion-plant',output=out,reports=Path(t)/'report')
                report=audit('ansan-promotion-plant',output=out,write_report=False)
            self.assertEqual(report['errors'],[])
            self.assertTrue((out/'assets/analytics.js').is_file())
            self.assertIn('data-track-event="phone"',(out/'index.html').read_text(encoding='utf-8'))
        data['site']['workerName']='v5-sample'
        with patch('v5.deploy.read_site',return_value=data),patch('v5.deploy.preflight',return_value={'ready':True}):
            cfg=worker_config('ansan-promotion-plant')
        self.assertEqual(cfg['analytics_engine_datasets'][0]['binding'],'ANALYTICS')
        self.assertIn('/__v5_event',cfg['assets']['run_worker_first'])

if __name__=='__main__':unittest.main()

class AggregateMetrics(unittest.TestCase):
    def test_disabled_aggregate_metrics_cannot_query_private_data(self):
        from v5.analytics_report import read_counts
        with patch('v5.analytics_report.urlopen') as read:
            with self.assertRaises(ConfigError):read_counts('ansan-promotion-plant')
            read.assert_not_called()
