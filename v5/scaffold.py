"""Create a second independent client site without cloning live pages or claims."""
from __future__ import annotations
import json
from pathlib import Path
from .config import ConfigError,ROOT,validate_site_id


def scaffold(site_id,brand,keyword,region,phone,*,apply=False,sites_dir=None):
    validate_site_id(site_id)
    if not all(isinstance(v,str) and v.strip() for v in (brand,keyword,region,phone)):
        raise ConfigError('Business name, keyword, region and phone are required')
    from .config import re
    if not re.fullmatch(r'0\d{1,2}-\d{3,4}-\d{4}|1\d{3}-\d{4}',phone):
        raise ConfigError('Invalid phone format')
    root=sites_dir or ROOT/'sites'
    target=(root/site_id)
    if target.exists():raise ConfigError('Site already exists')
    data={
        'site.json':{
            'id':site_id,'status':'draft','brand':brand,'siteTitle':keyword+' '+region,
            'domain':None,'workerName':None,'locale':'ko-KR','phone':phone,
            'keyword':keyword,'region':region,'theme':'classic','imageLibrary':site_id,
            'imagePool':[],'orderBaseUrl':'https://example.com','publishEnabled':False,
            'imageAssetsApproved':False,'cookiePrivacyReviewed':False,
            'analytics':{'enabled':False},'siteSearch':{'enabled':False},
            'staticAssetSoftLimit':18000,'source':'Unverified draft; requires actual products and source facts'
        },
        'products.json':[],
        'pages.json':[],
        'links.json':[],
        'special-pages.json':[],
        'regions.json':{'source':'unverified draft','regions':[{'name':region,'code':None,'level':'unverified'}]}
    }
    from .site_plan import initial_spec
    data['site-spec.json']=initial_spec(site_id,brand,keyword,region,phone)
    if apply:
        target.mkdir(parents=True,exist_ok=False)
        try:
            for name,obj in data.items():
                (target/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        except Exception:
            import shutil
            shutil.rmtree(target)
            raise
    return {'site':site_id,'created':apply,'status':'draft','configFiles':sorted(data),
            'note':'No product/data/page text copied from any other customer site.'}
