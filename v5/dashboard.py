"""Multi-site status overview from local recorded builds."""
from __future__ import annotations
import json
from pathlib import Path
from .config import SITES,read_site,ROOT,ConfigError
from .engine import report_dir


def dashboard():
    rows=[]
    for child in sorted(SITES.iterdir()):
        if not child.is_dir():continue
        try:
            data=read_site(child.name);m=report_dir(child.name)/'manifest.json';a=report_dir(child.name)/'audit.json'
            manifest=json.loads(m.read_text(encoding='utf-8')) if m.exists() else None
            check=json.loads(a.read_text(encoding='utf-8')) if a.exists() else None
            rows.append({'site':child.name,'domain':data['site']['domain'],
              'pages':manifest['pageCount'] if manifest else 0,
              'files':manifest['assetFileCount'] if manifest else 0,
              'buildMode':manifest['mode'] if manifest else 'unbuilt',
              'audit':'pass' if check and not check['errors'] else 'unverified' if check is None else 'fail',
              'publiclyDeployed':False})
        except (ConfigError,ValueError,OSError) as err:
            rows.append({'site':child.name,'audit':'error','reason':str(err)})
    return {'siteCount':len(rows),'sites':rows,'note':'Local manifests only; no Cloudflare deployment or analytics API read'}
