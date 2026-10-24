import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from v5 import markup
from v5.config import ConfigError,read_site
from v5.operations import prepare_global_change,prepare_special_change,prepare_page_append,apply_change
from v5.engine import build,analyze_change
from v5.release import archive

class StageC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.inputs=read_site('ansan-promotion-plant')
    def test_global_edit_changes_configuration_only(self):
        original=copy.deepcopy(self.inputs)
        after,report=prepare_global_change(self.inputs,'phone','031-123-4567')
        self.assertEqual(report['scope'],'all generated HTML pages')
        self.assertEqual(self.inputs,original)
        self.assertEqual(after['site']['phone'],'031-123-4567')
        with self.assertRaises(ConfigError):prepare_global_change(self.inputs,'domain','https://foo.com')
    def test_special_page_link_reuse_and_validation(self):
        after,report=prepare_special_change(self.inputs,path='행사안내.html',title='승진 행사 안내',description='행사에서 확인할 일',kind='content',placement='both')
        self.assertEqual(after['links'][-1]['placement'],'both')
        self.assertEqual(after['special'][-1]['path'],'행사안내.html')
        with self.assertRaises(ConfigError):
            prepare_special_change(self.inputs,path='../unsafe.html',title='a',description='b')
    def test_page_append_keeps_previous_content_hashes_and_updates_links(self):
        after,changes=prepare_page_append(self.inputs,{**copy.deepcopy(self.inputs['pages'][0]),'id':'ansan-plant-011',
          'title':'안산시 승진화분 새 상담 시나리오',
          'intro':'새로운 직급의 업무환경을 고려해 선물의 크기와 수령 담당자를 함께 확인하는 신규 안내입니다.',
          'sections':[{'heading':'새 업무 일정','paragraph':'첫 근무지와 행사장 주소가 서로 다르다면 실제 받을 장소부터 구분해 주세요.'},
                      {'heading':'새 담당자 확인','paragraph':'부서 이동으로 수령인이 변경될 수 있으니 받는 분에게 연락 가능한 담당자를 확인해 주세요.'}],
          'faq':[]})
        self.assertEqual(changes['newNumber'],11)
        with tempfile.TemporaryDirectory() as t:
            a,b=Path(t)/'output',Path(t)/'reports'
            build('ansan-promotion-plant',output=a,reports=b)
            old=json.loads((b/'manifest.json').read_text(encoding='utf-8'))
            before=(a/'10.html').read_text(encoding='utf-8')
            with patch('v5.engine.read_site',return_value=after),patch('v5.audit.read_site',return_value=after):
                result=build('ansan-promotion-plant',output=a,reports=b)
            change=analyze_change(old,result['manifest'])
            self.assertEqual(change['preservedContentPages'],10)
            self.assertEqual(change['newPageNumbers'],['11'])
            self.assertIn('11.html',change['newFiles'])
            self.assertNotEqual(before,(a/'10.html').read_text(encoding='utf-8'))
            self.assertIn('href="/11.html"',(a/'10.html').read_text(encoding='utf-8'))
    def test_failed_quality_gate_keeps_previous_artifacts(self):
        with tempfile.TemporaryDirectory() as t:
            out,report=Path(t)/'public',Path(t)/'reports'
            original=build('ansan-promotion-plant',output=out,reports=report)
            before=(out/'index.html').read_bytes()
            old=markup.detail
            def bad(*a,**k):return old(*a,**k).replace('</main>','<a href="/missing.html">invalid</a></main>')
            with patch('v5.engine.markup.detail',side_effect=bad):
                with self.assertRaisesRegex(ConfigError,'quality gate'):
                    build('ansan-promotion-plant',output=out,reports=report)
            self.assertEqual((out/'index.html').read_bytes(),before)
    def test_cli_dry_run_has_no_side_effects(self):
        original=(self.inputs['root']/'site.json').read_bytes()
        answer=apply_change('ansan-promotion-plant','global',field='brand',value='가상업체',apply=False)
        self.assertFalse(answer['applied'])
        self.assertEqual((self.inputs['root']/'site.json').read_bytes(),original)

if __name__=='__main__':unittest.main()

class StageCRestore(unittest.TestCase):
    def test_a_local_snapshot_is_sha_checked_and_can_be_restored(self):
        from v5.config import ROOT
        from v5.engine import build, report_dir
        from v5.release import archive, restore_local
        from v5.engine import sha
        from unittest.mock import patch
        build('ansan-promotion-plant')
        old=(ROOT/'dist/ansan-promotion-plant/index.html').read_bytes()
        snapshot=archive('ansan-promotion-plant')
        self.assertEqual(snapshot['files'],27)
        target=ROOT/'dist/ansan-promotion-plant/index.html'
        target.write_text('LOCAL CORRUPTED TEST OUTPUT',encoding='utf-8')
        res=restore_local('ansan-promotion-plant',snapshot['revision'])
        self.assertEqual(target.read_bytes(),old)
        self.assertEqual(res['files'],27)
        self.assertEqual(sha(target.read_bytes()),sha(old))

class StageCArchiveIdentity(unittest.TestCase):
    def test_release_hash_changes_with_generated_html_even_if_inputs_same(self):
        from v5.engine import _manifest
        from v5.config import read_site
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'index.html').write_text('first',encoding='utf-8')
            data=read_site('ansan-promotion-plant')
            before=_manifest(data,root,'preview')
            (root/'index.html').write_text('second',encoding='utf-8')
            after=_manifest(data,root,'preview')
            self.assertEqual(before['sourceDigest'],after['sourceDigest'])
            self.assertNotEqual(before['releaseHash'],after['releaseHash'])
