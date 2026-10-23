"""Read-only production HTTP verification; never claims indexing or orders."""
from __future__ import annotations
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from urllib.parse import quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from .config import read_site,ConfigError
from .engine import report_dir


def request_url(url,timeout=35):
    req=Request(url,headers={'User-Agent':'SiteFactoryV5-Audit/0.3','Accept':'text/html'})
    try:
        with urlopen(req,timeout=timeout) as r:
            return r.status,r.read(800_000).decode('utf-8',errors='replace')
    except HTTPError as err:
        return err.code,err.read(100_000).decode('utf-8',errors='replace')


def check(site_id):
    data=read_site(site_id);site=data['site']
    if not site.get('domain') or not site.get('publishEnabled'):
        raise ConfigError('Public readback requires configured domain and publishEnabled')
    origin=site['domain'].rstrip('/')
    manifest_file=report_dir(site_id)/'manifest.json'
    manifest=json.loads(manifest_file.read_text(encoding='utf-8'))
    if manifest['mode']!='publish':raise ConfigError('Cannot check a preview build as production')
    pages=manifest['pages']
    from .markup import url_path
    targets=[(p['urlPath'],p['number']) for p in pages]
    specials=[('/'+quote(x['path']),None) for x in data['special'] if x.get('enabled',True)]
    targets+=specials+[('/missing-v5-confirmation.html',None)]
    def probe(item):
        path,number=item
        status,body=request_url(origin+path)
        expected=404 if path=='/missing-v5-confirmation.html' else 200
        errs=[]
        if status!=expected:errs.append(f'HTTP {status}, expected {expected}')
        if expected==200:
            if 'noindex,nofollow' in body and path!='/search.html':errs.append('Unexpected public noindex')
            if number is not None and f'href="{origin+path}"' not in body:
                errs.append('Canonical mismatch')
            if f'tel:{site["phone"].replace("-","")}' not in body:errs.append('Phone CTA missing')
        return {'url':origin+path,'status':status,'errors':errs}
    with ThreadPoolExecutor(max_workers=12) as pool:
        rows=list(pool.map(probe,targets))
    result={'site':site_id,'checkedAt':datetime.now(timezone.utc).isoformat(),'tested':len(rows),
            'errors':[x for x in rows if x['errors']],
            'public404Verified':next((x['status']==404 for x in rows if 'missing-v5-confirmation.html' in x['url']),False),
            'mode':'live-readback','indexingVerified':False,'ordersPlaced':False}
    report=report_dir(site_id);report.mkdir(parents=True,exist_ok=True)
    (report/'public-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
