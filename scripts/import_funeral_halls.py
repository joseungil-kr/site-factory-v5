"""Reconcile pinned local sources and build an offline facility DB and draft link plan."""
import argparse
from collections import Counter, defaultdict, deque
from contextlib import closing
import csv
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil
import sqlite3
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/funeral-halls'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PROVINCE_SLUGS = dict(zip(
    ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시',
     '울산광역시', '세종특별자치시', '경기도', '강원특별자치도', '충청북도', '충청남도',
     '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도'],
    ['seoul', 'busan', 'daegu', 'incheon', 'gwangju', 'daejeon', 'ulsan', 'sejong',
     'gyeonggi', 'gangwon', 'chungbuk', 'chungnam', 'jeonbuk', 'jeonnam', 'gyeongbuk',
     'gyeongnam', 'jeju']))
FIELD_MAP = {
    'name': ['시설명', 'name'], 'province': ['시도', 'sido'], 'district': ['시군구', 'sigungu'],
    'address': ['주소', 'address'], 'phone': ['전화번호', 'phone'], 'rooms': ['빈소수', 'rooms'],
    'coffins': ['안치가능구수', 'coffins'], 'parking': ['주차대수', 'parking'],
    'amenities': [['식당', '매점', '주차장', '유족대기실', '장애인편의시설'], 'extras'],
    'operation_type': [['공설/사설', '운영종류'], 'type']}


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def clean(value):
    if value is None or str(value).strip().lower() in ('', 'null'):
        return None
    return unicodedata.normalize('NFC', str(value)).strip()


def key(value):
    return re.sub(r'\s+', '', clean(value) or '')


def identity(prefix, *parts):
    return prefix + '-' + hashlib.sha256('\0'.join(parts).encode()).hexdigest()[:20]


def number(value):
    value = clean(value)
    if value is None:
        return None
    if re.fullmatch(r'\d+(?:\.0+)?', value):
        return int(float(value))
    raise ValueError('Unrecognized capacity: ' + value)


def worksheet_rows(path, sheet_name):
    """Read cached source cells with their real row numbers; no Excel package required."""
    with ZipFile(path) as book:
        shared = []
        if 'xl/sharedStrings.xml' in book.namelist():
            shared = [''.join(t.text or '' for t in x.findall('.//s:t', NS)) for x in
                      ET.fromstring(book.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        rels = {r.attrib['Id']: r.attrib['Target'] for r in
                ET.fromstring(book.read('xl/_rels/workbook.xml.rels'))}
        sheet = next(x for x in ET.fromstring(book.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS)
                     if x.attrib['name'] == sheet_name)
        target = rels[sheet.attrib['{' + REL + '}id']]
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        header = None
        for row in ET.fromstring(book.read(target)).findall('s:sheetData/s:row', NS):
            cells = {}
            for cell in row.findall('s:c', NS):
                col = re.match('[A-Z]+', cell.attrib['r']).group()
                value = cell.find('s:v', NS)
                value = value.text if value is not None else None
                if cell.attrib.get('t') == 's' and value is not None:
                    value = shared[int(value)]
                elif cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                cells[col] = clean(value)
            if not any(cells.values()):
                continue
            if header is None:
                header = cells
            else:
                yield int(row.attrib['r']), {name: cells.get(col) for col, name in header.items()}


def canonical(raw, legacy=False):
    if legacy:
        return dict(name=clean(raw['name']), province=clean(raw['sido']), district=clean(raw['sigungu']),
                    address=clean(raw['address']), phone=clean(raw['phone']), rooms=number(raw['rooms']),
                    coffins=number(raw['coffins']), parking=number(raw['parking']),
                    amenities=sorted((clean(raw['extras']) or '').split('·')) if clean(raw['extras']) else [],
                    operation_type=clean(raw['type']))
    operation = clean(raw['공설/사설'])
    kind = clean(raw['운영종류'])
    return dict(name=clean(raw['시설명']), province=clean(raw['시도']), district=clean(raw['시군구']),
                address=clean(raw['주소']), phone=clean(raw['전화번호']), rooms=number(raw['빈소수']),
                coffins=number(raw['안치가능구수']), parking=number(raw['주차대수']),
                amenities=sorted(name for name in FIELD_MAP['amenities'][0] if clean(raw[name]) == '설치'),
                operation_type=f'{operation}({kind})' if operation and kind else operation)


def region_hints(record):
    """Flag source/address disagreement without inventing an official jurisdiction."""
    words = record['address'].split()
    candidate = words[1] if len(words) > 1 else None
    if candidate and candidate.endswith('시') and len(words) > 2 and words[2].endswith('구'):
        candidate += ' ' + words[2]
    if record['district'] == record['province']:
        return dict(status='province_level_source_bucket', addressDistrictCandidate=None)
    if not candidate or not candidate.endswith(('시', '군', '구')):
        return dict(status='unparsed_address', addressDistrictCandidate=None)
    return dict(status='source_address_label_agrees' if key(candidate) == key(record['district'])
                else 'source_address_label_differs', addressDistrictCandidate=candidate)


def reconcile(primary, legacy):
    by_address = defaultdict(list)
    for row, raw in legacy:
        by_address[key(raw['address'])].append((row, raw))
    records, comparisons, issues, linked_csv = [], [], [], set()
    for row, raw in primary:
        record = canonical(raw)
        if not all(record[k] for k in ('name', 'province', 'district', 'address')):
            raise ValueError(('Missing identity or region', row))
        fid = identity('fh', key(record['name']), key(record['address']))
        matches = by_address[key(record['address'])]
        refs = [dict(sourceId='detail-xlsx', sheet='장례식장', row=row)]
        aliases = []
        state = 'unmatched'
        if len(matches) == 1:
            csv_row, csv_raw = matches[0]
            if csv_row in linked_csv:
                raise ValueError(('Ambiguous primary address; no automatic merge', record['address']))
            linked_csv.add(csv_row)
            secondary = canonical(csv_raw, legacy=True)
            refs.append(dict(sourceId='legacy-csv', row=csv_row))
            state = 'address_matched'
            for field, value in record.items():
                same = key(value) == key(secondary[field]) if field in ('address', 'phone') else value == secondary[field]
                result = 'agrees' if same else 'name_difference' if field == 'name' else 'conflict'
                comparisons.append(dict(facilityId=fid, field=field, result=result,
                                        primaryValue=value, csvValue=secondary[field]))
                if not same:
                    issues.append(dict(facilityId=fid, kind=result, field=field,
                                       primaryValue=value, csvValue=secondary[field]))
                    if field == 'name':
                        aliases.append(dict(name=secondary[field], sourceId='legacy-csv', row=csv_row,
                                            kind='legacy_transformed_label_not_official_name'))
        else:
            state = 'ambiguous_address' if matches else 'unmatched_address'
            issues.append(dict(facilityId=fid, kind=state, candidateCsvRows=[m[0] for m in matches]))
        hints = region_hints(record)
        if hints['status'] != 'source_address_label_agrees':
            issues.append(dict(facilityId=fid, kind=hints['status'], sourceDistrict=record['district'], **hints))
        record.update(id=fid, addressKey=key(record['address']), aliases=aliases, sources=refs,
                      regionId=identity('src-district', record['province'], record['district']),
                      verification=dict(sourceReconciliation=state, officialName='not_externally_verified',
                                        nameReviewRequired=bool(aliases), currentOperation='not_checked',
                                        currentAddress='not_checked', currentPhone='not_called',
                                        officiallyMappedRegion=False, externallyVerifiedAt=None), regionHints=hints)
        records.append(record)
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('Duplicate primary name+address; review raw rows instead of silently discarding')
    groups = defaultdict(list)
    for r in records:
        groups[key(r['name'])].append(r)
    for rs in groups.values():
        for r in rs:
            r['sameNameCount'] = len(rs)
            r['displayLabel'] = r['name'] + ' — ' + r['address'] if len(rs) > 1 else r['name']
    unmatched = [row for row, _ in legacy if row not in linked_csv]
    return sorted(records, key=lambda r: r['id']), comparisons, issues, unmatched


def draft_plan(records):
    pages = [dict(id='national', path='/', parent=None, role='national', label='전국 장례식장 근조화환')]
    provinces, districts = {}, {}
    for r in records:
        slug = PROVINCE_SLUGS.get(r['province'], identity('source-province', r['province']))
        pid = 'province:' + slug
        provinces[pid] = dict(id=pid, path=f'/regions/{slug}/', parent='national', role='province', label=r['province'])
        if r['district'] == r['province']:
            parent = pid
        else:
            parent = r['regionId']
            districts[parent] = dict(id=parent, path=f'/regions/{slug}/{parent}/', parent=pid,
                                     role='source_district_bucket', label=r['district'])
        pages.append(dict(id=r['id'], path=f'/funeral-halls/{r["id"]}/', parent=parent,
                          role='facility', label=r['displayLabel']))
    pages += list(provinces.values()) + list(districts.values())
    by_id = {p['id']: p for p in pages}
    for p in pages:
        p['links'] = sorted([c['id'] for c in pages if c['parent'] == p['id']] + ([p['parent']] if p['parent'] else []))
        chain, cursor = [], p['id']
        while cursor:
            chain.append(cursor)
            cursor = by_id[cursor]['parent']
        p['breadcrumbs'] = list(reversed(chain))
    plan = dict(schemaVersion=1,kind='funeral_wreath_facility_hubs', status='offline_draft_not_published',
                publicationAllowed=False, regionCoverage='source facility buckets; not an official complete region master',
                pages=sorted(pages, key=lambda p: p['id']))
    return plan


def validate_plan(plan, expected_facility_ids):
    pages = plan['pages']
    ids = {p['id']: p for p in pages}
    assert len(ids) == len(pages) and len({p['path'] for p in pages}) == len(pages)
    assert ids['national']['parent'] is None
    reached, queue = set(), deque(['national'])
    while queue:
        pid = queue.popleft()
        if pid in reached:
            continue
        reached.add(pid)
        p = ids[pid]
        for target in p['links']:
            assert target in ids, ('broken link', pid, target)
            queue.append(target)
        if p['parent']:
            assert p['parent'] in p['links'] and pid in ids[p['parent']]['links']
            assert p['breadcrumbs'] == ids[p['parent']]['breadcrumbs'] + [pid]
    assert reached == set(ids), 'Orphan pages'
    assert {p['id'] for p in pages if p['role'] == 'facility'} == set(expected_facility_ids)
    return dict(pages=len(pages), edges=sum(len(p['links']) for p in pages), orphanPages=0,
                brokenLinks=0, maxDepth=max(len(p['breadcrumbs']) - 1 for p in pages))


def build(base=BASE):
    manifest = json.loads((base/'sources/MANIFEST.json').read_text(encoding='utf-8'))
    sources = {s['id']: s for s in manifest['sources']}
    for s in sources.values():
        path = ROOT/s['path'] if base == BASE else base/'sources'/Path(s['path']).name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == s['sha256'], s['id']
    primary = list(worksheet_rows(base/'sources/facilities.xlsx', '장례식장'))
    with (base/'sources/legacy-facilities.csv').open(encoding='utf-8-sig', newline='') as f:
        legacy = list(enumerate(csv.DictReader(f), 2))
    records, comparisons, issues, unmatched = reconcile(primary, legacy)
    regions = {'national': dict(id='national', parent=None, level='country', name='대한민국', province=None, district=None)}
    for r in records:
        pid = 'province:' + PROVINCE_SLUGS.get(r['province'], identity('source-province', r['province']))
        regions[pid] = dict(id=pid, parent='national', level='province', name=r['province'], province=r['province'], district=None)
        regions[r['regionId']] = dict(id=r['regionId'], parent=pid, level='source_district_bucket', name=r['district'],
                                      province=r['province'], district=r['district'])
    for region in regions.values():
        region.update(officialCode=None, verificationStatus='source_labels_only_not_officially_mapped')
    plan = draft_plan(records)
    graph = validate_plan(plan, [r['id'] for r in records])
    report = dict(schemaVersion=1, importedOn=manifest['importedOn'], sourceRows=dict(primary=len(primary), csv=len(legacy)),
                  facilityCount=len(records), matchedAddressRows=sum(r['verification']['sourceReconciliation']=='address_matched' for r in records),
                  unmatchedCsvRows=unmatched, comparisons=dict(Counter(c['result'] for c in comparisons)),
                  issueCounts=dict(Counter(i['kind'] for i in issues)), provinceCount=len({r['province'] for r in records}),
                  sourceRegionBucketCount=len({r['regionId'] for r in records}),
                  sameNameGroups=[dict(name=rs[0]['name'],facilityIds=[r['id'] for r in rs],addresses=[r['address'] for r in rs])
                                  for name in sorted({key(r['name']) for r in records})
                                  if len(rs:=[r for r in records if key(r['name'])==name])>1],
                  graph=graph, externallyVerifiedFacilities=0, officialRegionCoverageComplete=False,
                  sourceIndependence='CSV is derived from the workbook; agreement is reconciliation, not independent verification')
    bundle = dict(schemaVersion=1, importedOn=manifest['importedOn'],fieldSources=FIELD_MAP,sources=manifest['sources'],
                  regions=sorted(regions.values(), key=lambda r:r['id']),facilities=records)
    for path, obj in [('facilities.json', bundle), ('RECONCILIATION.json', dict(summary=report,comparisons=comparisons,issues=issues)),
                      ('hub-plan.json', plan)]:
        (base/path).write_text(dump(obj), encoding='utf-8', newline='\n')
    database = base/'facilities.sqlite3'
    if database.exists():
        database.unlink()
    with closing(sqlite3.connect(database)) as db, db:
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript('''CREATE TABLE metadata(key TEXT PRIMARY KEY,value_json TEXT NOT NULL);
CREATE TABLE sources(id TEXT PRIMARY KEY,record_json TEXT NOT NULL);
CREATE TABLE regions(id TEXT PRIMARY KEY,parent_id TEXT REFERENCES regions(id),level TEXT NOT NULL,name TEXT NOT NULL,official_code TEXT,verification_status TEXT NOT NULL,record_json TEXT NOT NULL);
CREATE TABLE facilities(id TEXT PRIMARY KEY,name TEXT NOT NULL,address TEXT NOT NULL,phone TEXT,region_id TEXT NOT NULL REFERENCES regions(id),verification_status TEXT NOT NULL,record_json TEXT NOT NULL);
CREATE INDEX facility_name_address ON facilities(name,address);
CREATE INDEX facility_region ON facilities(region_id);
CREATE TABLE source_rows(source_id TEXT NOT NULL REFERENCES sources(id),row_number INTEGER NOT NULL,sheet TEXT,facility_id TEXT REFERENCES facilities(id),data_json TEXT NOT NULL,PRIMARY KEY(source_id,row_number));
CREATE TABLE aliases(facility_id TEXT NOT NULL REFERENCES facilities(id),name TEXT NOT NULL,source_id TEXT NOT NULL REFERENCES sources(id),row_number INTEGER NOT NULL,kind TEXT NOT NULL);
CREATE TABLE comparisons(facility_id TEXT NOT NULL REFERENCES facilities(id),field TEXT NOT NULL,result TEXT NOT NULL,primary_value_json TEXT,csv_value_json TEXT,PRIMARY KEY(facility_id,field));
CREATE TABLE issues(facility_id TEXT NOT NULL REFERENCES facilities(id),kind TEXT NOT NULL,detail_json TEXT NOT NULL);''')
        db.executemany('INSERT INTO metadata VALUES(?,?)', [('summary',dump(report)),('field_sources',dump(FIELD_MAP))])
        db.executemany('INSERT INTO sources VALUES(?,?)', [(s['id'],dump(s)) for s in manifest['sources']])
        for level in ('country','province','source_district_bucket'):
            db.executemany('INSERT INTO regions VALUES(?,?,?,?,?,?,?)', [(r['id'],r['parent'],r['level'],r['name'],None,r['verificationStatus'],dump(r)) for r in regions.values() if r['level']==level])
        db.executemany('INSERT INTO facilities VALUES(?,?,?,?,?,?,?)', [(r['id'],r['name'],r['address'],r['phone'],r['regionId'],r['verification']['sourceReconciliation'],dump(r)) for r in records])
        references = {(s['sourceId'],s['row']):r['id'] for r in records for s in r['sources']}
        db.executemany('INSERT INTO source_rows VALUES(?,?,?,?,?)', [(sid,n,'장례식장' if sid=='detail-xlsx' else None,references.get((sid,n)),dump(raw)) for sid, rows in [('detail-xlsx',primary),('legacy-csv',legacy)] for n,raw in rows])
        db.executemany('INSERT INTO aliases VALUES(?,?,?,?,?)', [(r['id'],a['name'],a['sourceId'],a['row'],a['kind']) for r in records for a in r['aliases']])
        db.executemany('INSERT INTO comparisons VALUES(?,?,?,?,?)', [(c['facilityId'],c['field'],c['result'],dump(c['primaryValue']),dump(c['csvValue'])) for c in comparisons])
        db.executemany('INSERT INTO issues VALUES(?,?,?)', [(i['facilityId'],i['kind'],dump(i)) for i in issues])
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    return report


def logical_database(path):
    """Compare SQL values, not SQLite headers that vary with the runtime version."""
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {t: sorted(db.execute('SELECT * FROM "' + t.replace('"','""') + '"').fetchall(), key=dump) for t in tables}


def check_current():
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        shutil.copytree(BASE/'sources', temp/'sources')
        report = build(temp)
        for name in ('facilities.json','RECONCILIATION.json','hub-plan.json'):
            assert (temp/name).read_bytes() == (BASE/name).read_bytes(), ('stale output',name)
        assert logical_database(temp/'facilities.sqlite3') == logical_database(BASE/'facilities.sqlite3'), 'stale SQL rows'
        return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='New empty isolated output directory; copies only V5 local inputs')
    args = parser.parse_args()
    if args.output_dir:
        if args.check:
            parser.error('--check and --output-dir are mutually exclusive')
        target = args.output_dir.resolve()
        if target.exists() and any(target.iterdir()):
            parser.error('--output-dir must be empty; existing outputs are not overwritten')
        target.mkdir(parents=True, exist_ok=True)
        shutil.copytree(BASE/'sources', target/'sources')
        result = build(target)
    else:
        result = check_current() if args.check else build()
    print(dump({k:v for k,v in result.items() if k!='sameNameGroups'}))
    if result['unmatchedCsvRows'] or any(k in result['issueCounts'] for k in ('conflict','unmatched_address','ambiguous_address')):
        raise SystemExit('Unresolved reconciliation; do not adopt or publish automatically')
