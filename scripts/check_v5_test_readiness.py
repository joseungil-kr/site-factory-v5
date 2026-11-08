"""Read-only readiness gate for isolated recovery tests. Does not build or deploy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

from verify_v4_dependency_inputs import verify_digest, verify_sources, verify_official, verify_todayflower
from audit_rss_reproduction import snapshot, compare, feed

ROOT=Path(__file__).resolve().parents[1]

def require_isolated_paths(paths):
    resolved=[p.resolve() for p in paths]
    if len(resolved)!=len(set(resolved)):
        raise ValueError('Baseline and candidate must use separate directories')
    for i,path in enumerate(resolved):
        for other in resolved[i+1:]:
            if path in other.parents or other in path.parents:
                raise ValueError('Baseline and candidate must not be nested')

def check_page(path, canonical_required):
    text=path.read_text(encoding='utf-8')
    if not re.search(r'<html\b',text) or not re.search(r'<main\b',text) or not re.search(r'<h1\b',text):
        raise ValueError('Core HTML structure missing: '+str(path))
    has_canonical='rel="canonical"' in text
    if has_canonical!=canonical_required:
        raise ValueError('Unexpected canonical state: '+str(path))
    return {'file':path.name,'main':True,'h1':True,'canonical':has_canonical}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','official-archive','todayflower-artifact','todayflower-root','clinic-before','clinic-after'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    require_isolated_paths([args.todayflower_root,args.clinic_before,args.clinic_after])
    manifest=json.loads((ROOT/'docs/v4-dependency-manifest.json').read_text())
    deps={d['id']:d for d in manifest['dependencies']}
    verified_sources=0
    for key in ('skyquote-official-regions','clinic-rss-composite'):
        verified_sources+=verify_sources(args.inputs,deps[key])['sourceFilesVerified']
    today_inputs=json.loads((ROOT/'docs/V5_TODAYFLOWER_RSS_INPUTS_20261108.json').read_text())
    for item in today_inputs:
        verify_digest(args.todayflower_root/item['path'],item['sha256'],item['bytes'])
    official=verify_official(args.official_archive,deps['skyquote-official-regions'],args.inputs/'skyquote/sites/skyquote/official-upper-regions-20261022.json')
    artifact=verify_todayflower(args.todayflower_artifact,deps['todayflower-artifact'])
    before=snapshot(args.clinic_before);after=snapshot(args.clinic_after)
    rss_paths=['sites/'+s+'/rss.xml' for s in ('clinicflower','clinicopen','clinicpresent')]
    delta=compare(before,after,changed=rss_paths)
    if delta['unchangedHTML']!=15906 or delta['beforeFiles']!=15925:
        raise ValueError('Unexpected Clinic population')
    feeds={p:feed(args.clinic_after/p) for p in rss_paths}
    today=args.todayflower_root/'dist/todayflower-nalmada'
    with zipfile.ZipFile(args.todayflower_artifact) as archive:
        original=json.loads(archive.read('reports/todayflower-nalmada/manifest.json'))['files']
    today_delta=compare(original,snapshot(today),added=['rss.xml'])
    feeds['todayflower/rss.xml']=feed(today/'rss.xml')
    pages=[check_page(today/'index.html',False),check_page(today/'5071.html',False)]
    for site in ('clinicflower','clinicopen','clinicpresent'):
        pages.append(check_page(args.clinic_after/'sites'/site/'index.html',True))
        pages.append(check_page(args.clinic_after/'sites'/site/'r/05034.html',True))
    report={'scope':'read-only local test preparation, not live or deployment validation',
            'pinnedSourceFilesVerified':verified_sources+len(today_inputs),
            'official':official,'artifact':artifact,'clinicDelta':delta,'todayflowerDelta':today_delta,
            'rssFeeds':feeds,'htmlSmokeSamples':pages,'readyForOfflineTest':True,
            'readyForDeployment':False,'networkCalls':0,'siteFilesWritten':0,
            'remaining':['clean-environment restore from external sources',
                         'actual private HTTP endpoint and owner/unauthorized responses',
                         'deployment credentials and rollback exercise not in this scope']}
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
