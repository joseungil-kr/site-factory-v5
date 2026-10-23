"""Cloudflare worker configuration and hard production release gates."""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from .config import ROOT,ConfigError,read_site,assert_publish_ready
from .engine import report_dir,target_dir
from .audit import audit


def preflight(site_id):
    data=read_site(site_id)
    site=data['site']
    blockers=[]
    try:assert_publish_ready(site)
    except ConfigError as exc:blockers.append(str(exc))
    if not all(p.get('verifiedLive',False) for p in data['products']):
        blockers.append('All products require recent live stock/price/order destination validation')
    if not site.get('imageAssetsApproved',False):
        blockers.append('Shared image asset license/relevance/quality approval is missing')
    if any('예시' in (ROOT/'assets/library'/site.get('imageLibrary',site_id)/name).read_text(encoding='utf-8',errors='ignore') for name in site['imagePool'] if name.endswith('.svg')):
        blockers.append('Placeholder plant illustrations remain in image pool')
    if not site.get('cookiePrivacyReviewed',False):
        blockers.append('Customer-facing privacy/cookie and collection scope review not approved')
    if site.get('domain') and site.get('workerName'):
        if not re.fullmatch(r'[a-z0-9-]{3,63}',site['workerName']):
            blockers.append('Invalid Worker name')
        if urlsplit(site['domain']).hostname and not urlsplit(site['domain']).hostname.endswith('.kr'):
            # Non-.kr is not disallowed; domain review is a manual gate instead.
            pass
    if not blockers:
        current=report_dir(site_id)/'manifest.json'
        if not current.exists():blockers.append('No built manifest')
        else:
            manifest=json.loads(current.read_text(encoding='utf-8'))
            if manifest['mode']!='publish':blockers.append('A verified publish-mode build is required')
            else:
                result=audit(site_id)
                if result['errors']:blockers.append('Static audit did not pass')
    return {'site':site_id,'ready':not blockers,'blockers':blockers,'deployAttempted':False}


def worker_config(site_id):
    data=read_site(site_id);site=data['site']
    gate=preflight(site_id)
    if not gate['ready']:
        raise ConfigError('Production preflight blocked: '+'; '.join(gate['blockers']))
    config={
        'name':site['workerName'],
        'compatibility_date':'2026-10-24',
        'main':'../../worker/index.js',
        'workers_dev':False,
        'preview_urls':False,
        'keep_vars':True,
        'assets':{
            'directory':f'../../dist/{site_id}',
            'binding':'ASSETS',
            'not_found_handling':'404-page',
            'html_handling':'none',
            'run_worker_first':['/']+(['/__v5_event'] if site.get('analytics',{}).get('enabled',False) else [])
        }
    }
    if site.get('analytics',{}).get('enabled',False):
        config['analytics_engine_datasets']=[{'binding':'ANALYTICS','dataset':'v5_'+site_id.replace('-','_')}]
    return config


def write_worker_config(site_id):
    result=worker_config(site_id)
    target=ROOT/'deploy'/site_id/'wrangler.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return str(target)
