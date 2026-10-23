import unittest
from unittest.mock import patch
from v5.config import ConfigError
from v5.cloudflare import stable_version,guarded_deploy

GOOD='12345678-1234-1234-1234-123456789abc'

def response(versions):
    return {'success':True,'result':{'deployments':[{'versions':versions}]}}

class StageH(unittest.TestCase):
    def test_stable_provider_version_only(self):
        self.assertEqual(stable_version(response([{'percentage':100,'version_id':GOOD}])),GOOD)
        with self.assertRaises(ConfigError):stable_version(response([{'percentage':50,'version_id':GOOD},{'percentage':50,'version_id':GOOD}]))
        with self.assertRaises(ConfigError):stable_version({'success':True,'result':{'deployments':[]}})
        with self.assertRaises(ConfigError):stable_version(response([{'percentage':100,'version_id':'nonsense'}]))
    def test_guarded_deploy_does_not_execute_when_blocked(self):
        with patch('v5.cloudflare.subprocess.run') as run:
            with self.assertRaises(ConfigError):guarded_deploy('ansan-promotion-plant')
            run.assert_not_called()

if __name__=='__main__':unittest.main()

class StageHProviderRollback(unittest.TestCase):
    def test_failed_public_readback_tries_known_version_and_checks_it(self):
        import tempfile,json
        from pathlib import Path
        from unittest.mock import patch
        from v5.cloudflare import guarded_deploy
        with tempfile.TemporaryDirectory() as t:
            with patch('v5.cloudflare.preflight',return_value={'ready':True,'blockers':[]}), \
                 patch('v5.cloudflare.latest_version',side_effect=[GOOD,GOOD]), \
                 patch('v5.cloudflare.write_worker_config',return_value='deploy/demo/wrangler.json'), \
                 patch('v5.cloudflare.report_dir',return_value=Path(t)), \
                 patch('v5.cloudflare.subprocess.run') as run, \
                 patch('v5.publiccheck.check',return_value={'errors':['404 mismatch'],'public404Verified':False}), \
                 patch.dict('os.environ',{'CLOUDFLARE_API_TOKEN':'mock-test-token','CLOUDFLARE_ACCOUNT_ID':'1'*32}):
                with self.assertRaisesRegex(ConfigError,'rollback=True'):
                    guarded_deploy('ansan-promotion-plant')
            self.assertEqual(run.call_count,2)
            self.assertTrue(json.loads((Path(t)/'guarded-deploy.json').read_text())['rolledBack'])
