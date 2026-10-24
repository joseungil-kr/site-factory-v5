"""Separate Cloudflare workers.dev preview; never share the production Worker name.

Staging must use preview HTML and advertise noindex at HTTP-response level.
A first staging deployment intentionally requires no prior production version.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .config import ROOT, ConfigError, read_site
from .engine import target_dir, report_dir, sha, stable_hash


STAGING_PREFIX = 'sfv5-'


def staging_worker_name(site_id: str) -> str:
    name = f'{STAGING_PREFIX}{site_id}-preview'
    if len(name)>63 or not re.fullmatch(r'[a-z0-9-]{3,63}',name):
        raise ConfigError('Site ID too long for an isolated staging Worker')
    if any(v in name for v in ('flower-matrix-a-prod','flower-matrix-b-prod')):
        raise ConfigError('Refusing V4 production Worker target')
    return name


def staging_preflight(site_id: str):
    data=read_site(site_id)
    site=data['site']
    errors=[]
    if site.get('analytics',{}).get('enabled',False):
        errors.append('Staging must not collect analytics events')
    manifest_path=report_dir(site_id)/'manifest.json'
    out=target_dir(site_id)
    if not manifest_path.is_file():
        errors.append('No preview manifest; run build --mode preview')
    else:
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('mode')!='preview':
            errors.append('Refusing publish-mode HTML on staging Worker')
        if manifest.get('siteId')!=site_id:
            errors.append('Staging manifest has wrong site ID')
        if manifest.get('sourceDigest')!=stable_hash({k:v for k,v in data.items() if k!='root'}):
            errors.append('Staging manifest does not match current source')
        expected=manifest.get('files',{})
        actual={p.relative_to(out).as_posix():sha(p.read_bytes()) for p in out.rglob('*') if p.is_file()} if out.is_dir() else {}
        if expected!=actual:
            errors.append('Staging file content differs from reviewed preview manifest')
        for filename in actual:
            if filename.lower().endswith('.html'):
                content=(out/filename).read_text(encoding='utf-8')
                if '<meta name="robots" content="noindex,nofollow">' not in content or 'rel="canonical"' in content:
                    errors.append('Unsafe indexable staging HTML: '+filename)
                    break
        if 'sitemap.xml' in actual or any(f.startswith('sitemap') for f in actual):
            errors.append('A staging preview must not publish any sitemap')
        robots=out/'robots.txt'
        if not robots.is_file() or 'Disallow: /' not in robots.read_text(encoding='utf-8'):
            errors.append('Staging robots.txt must disallow crawling')
        if '404.html' not in actual:
            errors.append('Staging must ship its own 404 page')
    return {'site':site_id,'ready':not errors,'errors':errors,'workerName':staging_worker_name(site_id),'target':'workers.dev staging only','productionWorkerTouched':False}


def staging_config(site_id: str):
    gate=staging_preflight(site_id)
    if not gate['ready']:
        raise ConfigError('Preview staging blocked: '+'; '.join(gate['errors']))
    return {
        'name':gate['workerName'],
        'compatibility_date':'2026-10-21',
        'main':'../../worker/index.js',
        'workers_dev':True,
        'preview_urls':False,
        'keep_vars':False,
        'vars':{'V5_STAGING':'1'},
        'assets':{
            'directory':f'../../dist/{site_id}',
            'binding':'ASSETS',
            'html_handling':'none',
            'not_found_handling':'404-page',
            'run_worker_first':True,
        },
    }


def write_staging_config(site_id:str):
    config=staging_config(site_id)
    path=ROOT/'deploy'/site_id/'staging.wrangler.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return str(path)


def staging_check(site_id:str,origin:str):
    """Check a real HTTPS *.workers.dev URL; do not treat local simulations as public."""
    parts=urlsplit(origin)
    if (parts.scheme!='https' or not parts.hostname or
        not parts.hostname.endswith('.workers.dev') or
        parts.username or parts.password or parts.query or parts.fragment or parts.path not in ('','/')):
        raise ConfigError('Staging public check requires an HTTPS workers.dev origin')
    expected_name=staging_worker_name(site_id)
    if parts.hostname.split('.',1)[0]!=expected_name:
        raise ConfigError('Staging hostname does not match the isolated Worker')
    origin=origin.rstrip('/')
    paths=['/','/2.html','/10.html','/'+quote('견적계산기.html'),'/404-auditor-sentinel.html']
    if len(read_site(site_id)['pages'])>300:
        from .markup import filename
        paths+=['/'+filename(404),'/'+filename(max(p['number'] for p in read_site(site_id)['pages']))]
    checks=[]
    for path in paths:
        req=Request(origin+path,headers={'User-Agent':'SiteFactoryV5-Staging-Audit/0.4'})
        try:
            with urlopen(req,timeout=35) as res:
                status=res.status;headers=res.headers;body=res.read(400_000).decode('utf-8',errors='replace')
        except HTTPError as exc:
            status=exc.code;headers=exc.headers;body=exc.read(100_000).decode('utf-8',errors='replace')
        expected=404 if path.endswith('sentinel.html') else 200
        errs=[]
        if status!=expected:errs.append(f'HTTP {status} expected {expected}')
        if 'noindex' not in headers.get('X-Robots-Tag','').lower():errs.append('Missing live X-Robots-Tag noindex')
        if '<meta name="robots" content="noindex,nofollow">' not in body:errs.append('Missing live HTML noindex')
        if 'rel="canonical"' in body:errs.append('Unexpected live canonical')
        checks.append({'path':path,'status':status,'errors':errs})
    result={'site':site_id,'origin':origin,'checkedAt':datetime.now(timezone.utc).isoformat(),
            'checks':checks,'errors':[e for row in checks for e in row['errors']],
            'indexable':False,'productAccuracyVerified':False,'productionWorkerTouched':False}
    path=report_dir(site_id)/'staging-readback.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
