"""Guarded Cloudflare publish with prior-version readback and tested rollback path.

The account/provider integration is NOT verified until a real Worker and domain exist.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from .config import ConfigError,read_site
from .deploy import preflight,write_worker_config
from .engine import report_dir

VERSION=re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z')


def stable_version(payload):
    if not payload.get('success') or not isinstance(payload.get('result',{}).get('deployments'),list):
        raise ConfigError('Unexpected Cloudflare deployments response')
    entries=payload['result']['deployments']
    if not entries:raise ConfigError('First deployment has no previous version for safe rollback')
    live=entries[0]['versions']
    if len(live)!=1 or live[0]['percentage']!=100:
        raise ConfigError('Split deployment requires manual reconciliation')
    version=live[0].get('version_id','')
    if not VERSION.fullmatch(version):raise ConfigError('Malformed active Worker version ID')
    return version


def latest_version(site_id,account,token):
    name=read_site(site_id)['site']['workerName']
    if not re.fullmatch('[a-z0-9-]+',name or ''):
        raise ConfigError('Bad Worker name')
    if not re.fullmatch('[a-f0-9]{32}',account):
        raise ConfigError('Bad Cloudflare account ID')
    req=Request(f'https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{name}/deployments',
                headers={'Authorization':'Bearer '+token,'Accept':'application/json'})
    try:
        with urlopen(req,timeout=30) as resp:
            payload=json.load(resp)
    except HTTPError as exc:
        raise ConfigError(f'Cloudflare deployment lookup failed HTTP {exc.code}') from None
    return stable_version(payload)


def guarded_deploy(site_id):
    gate=preflight(site_id)
    if not gate['ready']:
        raise ConfigError('Refusing deployment: '+'; '.join(gate['blockers']))
    account=os.environ.get('CLOUDFLARE_ACCOUNT_ID','')
    token=os.environ.get('CLOUDFLARE_API_TOKEN','')
    if not account or not token:
        raise ConfigError('Missing Cloudflare account configuration or API token')
    previous=latest_version(site_id,account,token)
    conf=write_worker_config(site_id)
    report=report_dir(site_id)
    outcome={'site':site_id,'previousVersion':previous,'deployed':False,'readbackPassed':False,
             'rolledBack':False,'checkedAt':datetime.now(timezone.utc).isoformat()}
    command=['npx','--yes','wrangler@4.148.0','deploy','--config',conf]
    rollback=['npx','--yes','wrangler@4.148.0','versions','deploy',previous+'@100%','--yes','--config',conf]
    try:
        subprocess.run(command,check=True,timeout=3600)
        outcome['deployed']=True
        from .publiccheck import check
        verified=check(site_id)
        if verified['errors'] or not verified['public404Verified']:
            raise ConfigError('Public readback failed after deploy; rolling back')
        outcome['readbackPassed']=True
        site=read_site(site_id)['site']
        if site.get('indexNow',{}).get('enabled',False):
            try:
                from .indexnow import submission
                outcome['indexNow']=submission(site_id,site['indexNow']['key'],submit=True)
            except Exception as index_error:
                # Do not roll back a verified-good deployment merely because an
                # optional search notification was delayed or rejected.
                outcome['indexNowPending']=True
                outcome['indexNowError']=str(index_error)
        return outcome
    except Exception as exc:
        outcome['error']=str(exc)
        # Attempt restoration of the exact previous active version, never an ungrounded run ID.
        try:
            subprocess.run(rollback,check=True,timeout=300)
            after=latest_version(site_id,account,token)
            if after!=previous:
                raise ConfigError('Cloudflare rollback version readback mismatch')
            outcome['rolledBack']=True
        except Exception as rb_error:
            outcome['rollbackError']=str(rb_error)
        raise ConfigError('Production publish failed; rollback='+str(outcome['rolledBack'])+
            '; details in guarded-deploy.json; '+str(exc)) from None
    finally:
        report.mkdir(parents=True,exist_ok=True)
        (report/'guarded-deploy.json').write_text(json.dumps(outcome,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
