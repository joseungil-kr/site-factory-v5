"""IndexNow API submitter guarded by independent successful live readback."""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit,quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from .config import read_site,ConfigError
from .engine import report_dir


def submission(site_id,key,*,submit=False):
    data=read_site(site_id);site=data['site']
    if not site['domain'] or not site['publishEnabled']:
        raise ConfigError('IndexNow requires a real approved domain')
    if not site.get('indexNow',{}).get('enabled',False) or site['indexNow'].get('key')!=key:
        raise ConfigError('Key must match the stable IndexNow site configuration')
    if not re.fullmatch(r'[a-f0-9]{32,64}',key):
        raise ConfigError('Invalid stable IndexNow key format')
    report=report_dir(site_id)
    path=report/'public-check.json'
    if not path.exists():raise ConfigError('Successful live readback is a hard prerequisite')
    check=json.loads(path.read_text(encoding='utf-8'))
    if check['site']!=site_id or check['errors'] or not check['public404Verified']:
        raise ConfigError('Live readback has errors or missing 404 verification')
    # Stable key file must have been added to the published asset bundle and verified publicly.
    origin=site['domain'].rstrip('/')
    key_url=origin+'/'+key+'.txt'
    from .publiccheck import request_url
    status,body=request_url(key_url)
    if status!=200 or body.strip()!=key:
        raise ConfigError('IndexNow public key verification failed')
    manifest=json.loads((report/'manifest.json').read_text(encoding='utf-8'))
    urls=[origin+p['urlPath'] for p in manifest['pages']]
    urls += [origin+'/'+quote(x['path']) for x in data['special'] if x.get('enabled',True)]
    chunks=[urls[i:i+10000] for i in range(0,len(urls),10000)]
    results=[]
    if submit:
        for chunk in chunks:
            payload={'host':urlsplit(origin).hostname,'key':key,'keyLocation':key_url,'urlList':chunk}
            req=Request('https://api.indexnow.org/indexnow',data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),headers={'Content-Type':'application/json; charset=utf-8'},method='POST')
            try:
                with urlopen(req,timeout=90) as r:code=r.status;body=r.read(1000)
            except HTTPError as exc:code=exc.code;body=exc.read(1000)
            results.append({'count':len(chunk),'status':code})
            if code not in (200,202):raise ConfigError(f'IndexNow HTTP {code}: {body[:150]!r}')
    return {'ready':True,'submitted':submit,'urlCount':len(urls),'batches':list(map(len,chunks)),'responses':results,'indexingProven':False}
