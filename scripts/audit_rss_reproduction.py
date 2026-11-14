"""Read-only file-level comparison of isolated pinned-source RSS reproductions."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

def snapshot(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def compare(before,after,added=(),changed=()):
    actual_added=set(after)-set(before)
    removed=set(before)-set(after)
    actual_changed={p for p in before.keys() & after.keys() if before[p]!=after[p]}
    if removed or actual_added!=set(added) or actual_changed!=set(changed):
        raise ValueError('Unexpected delta: '+repr((sorted(actual_added),sorted(removed),sorted(actual_changed))))
    return {'beforeFiles':len(before),'afterFiles':len(after),'added':sorted(actual_added),
            'changed':sorted(actual_changed),'unchangedFiles':len(before)-len(actual_changed),
            'unchangedHTML':sum(p.endswith('.html') and after.get(p)==sha for p,sha in before.items())}

def feed(path):
    data=path.read_bytes();items=ET.fromstring(data).findall('./channel/item')
    if len(items)!=50 or any(i.find('pubDate') is not None for i in items):
        raise ValueError('RSS item count or invented date')
    if any(not i.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') for i in items):
        raise ValueError('RSS full content missing')
    return {'items':50,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--todayflower-artifact',type=Path,required=True)
    p.add_argument('--todayflower-output',type=Path,required=True)
    p.add_argument('--clinic-before',type=Path,required=True)
    p.add_argument('--clinic-after',type=Path,required=True)
    a=p.parse_args()
    raw=a.todayflower_artifact.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='16b52597fe77b0b4311ea21ad5daf6c5193af94346f8dc8df9834e676003a180':
        raise ValueError('Unpinned Todayflower baseline artifact')
    with zipfile.ZipFile(a.todayflower_artifact) as z:
        before=json.loads(z.read('reports/todayflower-nalmada/manifest.json'))['files']
    today=compare(before,snapshot(a.todayflower_output),added=['rss.xml'])
    today['rss']=feed(a.todayflower_output/'rss.xml')
    paths=['sites/'+s+'/rss.xml' for s in ['clinicflower','clinicopen','clinicpresent']]
    clinic=compare(snapshot(a.clinic_before),snapshot(a.clinic_after),changed=paths)
    if clinic['beforeFiles']!=15925 or clinic['unchangedHTML']!=15906:
        raise ValueError('Unexpected Clinic population')
    clinic['feeds']={s:feed(a.clinic_after/s) for s in paths}
    print(json.dumps({'todayflower':today,'clinic':clinic,'comparisonScope':'isolated pinned sources, not current live HTTP',
                      'networkCalls':0,'deploymentPerformed':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
