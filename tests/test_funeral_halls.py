import copy
import shutil
import tempfile
from unittest.mock import patch
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import import_funeral_halls as halls


class FuneralHallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_base = halls.BASE
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.addClassCleanup(setattr, halls, 'BASE', cls.original_base)
        halls.BASE = Path(cls.temp.name)
        shutil.copytree(cls.original_base/'sources', halls.BASE/'sources')
        with patch('socket.socket', side_effect=AssertionError('Network prohibited')):
            halls.build(halls.BASE)
        cls.bundle = json.loads((halls.BASE/'facilities.json').read_text(encoding='utf-8'))
        cls.records = cls.bundle['facilities']
        cls.plan = json.loads((halls.BASE/'hub-plan.json').read_text(encoding='utf-8'))

    def test_all_source_rows_preserved_and_db_matches_export(self):
        with closing(sqlite3.connect(halls.BASE/'facilities.sqlite3')) as db:
            self.assertEqual('ok',db.execute('PRAGMA integrity_check').fetchone()[0])
            self.assertEqual([],db.execute('PRAGMA foreign_key_check').fetchall())
            self.assertEqual(1080,db.execute('SELECT count(*) FROM facilities').fetchone()[0])
            self.assertEqual([('detail-xlsx',1080),('legacy-csv',1080)],
                             db.execute('SELECT source_id,count(*) FROM source_rows GROUP BY source_id ORDER BY source_id').fetchall())
            self.assertEqual(229,db.execute('SELECT count(*) FROM aliases').fetchone()[0])
            self.assertEqual(self.records,[json.loads(row[0]) for row in db.execute('SELECT record_json FROM facilities ORDER BY id')])
        self.assertEqual(1080,len({r['id'] for r in self.records}))
        for r in self.records:
            self.assertEqual('address_matched',r['verification']['sourceReconciliation'])
            self.assertEqual('not_checked',r['verification']['currentOperation'])
            self.assertFalse(r['verification']['officiallyMappedRegion'])
            self.assertIsNone(r['verification']['externallyVerifiedAt'])

    def test_same_names_never_merge_across_addresses(self):
        groups = {}
        for r in self.records:
            groups.setdefault(halls.key(r['name']),[]).append(r)
        duplicate_groups = [rs for rs in groups.values() if len(rs)>1]
        self.assertEqual(21,len(duplicate_groups))
        self.assertEqual(51,sum(map(len,duplicate_groups)))
        for rs in duplicate_groups:
            self.assertEqual(len(rs),len({r['addressKey'] for r in rs}))
            self.assertEqual(len(rs),len({r['id'] for r in rs}))
            for r in rs:
                self.assertIn(r['address'],r['displayLabel'])

    def test_source_hashes_and_capacity_zero(self):
        for source in self.bundle['sources']:
            self.assertEqual(source['sha256'],hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest())
        self.assertEqual(0,halls.number('0.0'))
        self.assertIsNone(halls.number('null'))
        with self.assertRaises(ValueError):
            halls.number('확인 필요')

    def test_reconciliation_refuses_ambiguous_address_and_keeps_name_alias(self):
        primary=list(halls.worksheet_rows(halls.BASE/'sources/facilities.xlsx','장례식장'))[:1]
        import csv
        with (halls.BASE/'sources/legacy-facilities.csv').open(encoding='utf-8-sig',newline='') as f:
            original=list(csv.DictReader(f))[0]
        a=dict(original,name='CSV에서 변경한 명칭')
        records,comparisons,issues,unmatched=halls.reconcile(primary,[(2,a)])
        self.assertEqual(primary[0][1]['시설명'],records[0]['name'])
        self.assertEqual('CSV에서 변경한 명칭',records[0]['aliases'][0]['name'])
        self.assertTrue(any(c['result']=='name_difference' for c in comparisons))
        records,_,issues,unmatched=halls.reconcile(primary,[(2,original),(3,original)])
        self.assertEqual('ambiguous_address',records[0]['verification']['sourceReconciliation'])
        self.assertEqual([2,3],unmatched)
        self.assertTrue(any(i['kind']=='ambiguous_address' for i in issues))

    def test_hub_reachability_and_failure_cases(self):
        result=halls.validate_plan(self.plan,[r['id'] for r in self.records])
        self.assertEqual(0,result['orphanPages'])
        self.assertEqual(3,result['maxDepth'])
        self.assertFalse(self.plan['publicationAllowed'])
        sejong=[r for r in self.records if r['province']=='세종특별자치시']
        pages={p['id']:p for p in self.plan['pages']}
        self.assertTrue(all(pages[r['id']]['parent']=='province:sejong' for r in sejong))
        broken=copy.deepcopy(self.plan)
        broken['pages'][0]['links'].append('does-not-exist')
        with self.assertRaises(AssertionError):
            halls.validate_plan(broken,[r['id'] for r in self.records])
        duplicate=copy.deepcopy(self.plan)
        duplicate['pages'][1]['path']=duplicate['pages'][0]['path']
        with self.assertRaises(AssertionError):
            halls.validate_plan(duplicate,[r['id'] for r in self.records])

    def test_rebuild_needs_only_v5_local_inputs(self):
        report=halls.check_current()
        self.assertEqual(1080,report['matchedAddressRows'])
        self.assertEqual({'agrees':10571,'name_difference':229},report['comparisons'])
        self.assertEqual(52,report['issueCounts']['source_address_label_differs'])
        self.assertFalse(report['officialRegionCoverageComplete'])

    def test_graph_validation_is_industry_neutral(self):
        for industry in ('flower-delivery','leak-detection','mobile-car-wash'):
            plan=dict(pages=[
                dict(id='national',path='/',parent=None,role='national',links=['province'],breadcrumbs=['national']),
                dict(id='province',path='/regions/sample/',parent='national',role='province',links=['national','district'],breadcrumbs=['national','province']),
                dict(id='district',path='/regions/sample/district/',parent='province',role='service_region',links=['province'],breadcrumbs=['national','province','district'])])
            self.assertEqual(0,halls.validate_plan(plan,[])['orphanPages'],industry)
            orphan=copy.deepcopy(plan)
            orphan['pages'][0]['links']=[]
            with self.assertRaises(AssertionError):
                halls.validate_plan(orphan,[])


if __name__=='__main__':
    unittest.main()
