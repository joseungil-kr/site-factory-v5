"""Safe, explicit input-ledger operations. Uncommitted modifications remain local."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from .config import ConfigError,read_site,safe_filename,validate_site_id

FIELDS={'phone','brand','theme','siteTitle'}


def prepare_global_change(data,field,value):
    if field not in FIELDS:
        raise ConfigError('Global field not in safe whitelist')
    new=copy.deepcopy(data)
    old=new['site'][field]
    new['site'][field]=value
    if field=='theme' and value not in ('classic','modern','minimal'):
        raise ConfigError('Theme must be classic/modern/minimal')
    if not value or not isinstance(value,str):
        raise ConfigError('Global replacement must be nonempty text')
    return new,{'field':field,'before':old,'after':value,'scope':'all generated HTML pages'}


def prepare_special_change(data,*,path,title,description,kind='content',placement='footer',scope='all'):
    safe_filename(path)
    if kind not in ('content','calculator'):
        raise ConfigError('Unrecognized special page kind')
    if placement not in ('footer','body','both') or scope!='all':
        raise ConfigError('Unsupported placement or scope for simplified special page creation')
    if any(x['path']==path for x in data['special']):
        raise ConfigError('Special page already exists')
    if not title or not description:
        raise ConfigError('Special page needs title and description')
    new=copy.deepcopy(data)
    new['special'].append({'path':path,'title':title,'description':description,'type':kind,'enabled':True})
    new['links'].append({'id':'link-'+str(len(new['links'])+1),'label':title,'target':path,
                         'placement':placement,'scope':'all','enabled':True})
    return new,{'specialPage':path,'placement':placement,'scope':scope}


def prepare_page_append(data,page):
    new=copy.deepcopy(data)
    latest=max(x['number'] for x in new['pages'])
    if any(x['id']==page.get('id') for x in new['pages']):
        raise ConfigError('Duplicate page ID')
    item=copy.deepcopy(page)
    item['number']=latest+1
    if not item.get('title') or not item.get('intro') or len(item.get('sections',[]))<2:
        raise ConfigError('Incomplete page content')
    new['pages'].append(item)
    return new,{'newNumber':latest+1,'filename':f'{latest+1}.html','id':item['id']}


def apply_change(site_id,operation,*,apply=False,**kwargs):
    data=read_site(site_id)
    if operation=='global':
        result,details=prepare_global_change(data,kwargs['field'],kwargs['value'])
        targets=['site']
    elif operation=='special':
        result,details=prepare_special_change(data,**kwargs)
        targets=['special','links']
    elif operation=='page':
        result,details=prepare_page_append(data,kwargs['page'])
        targets=['pages']
    else:
        raise ConfigError('Unknown operation')
    if apply:
        directory=data['root']
        names={'site':'site.json','special':'special-pages.json','links':'links.json','pages':'pages.json'}
        originals={}
        for kind in targets:
            path=directory/names[kind]
            originals[path]=path.read_bytes()
        try:
            for kind in targets:
                path=directory/names[kind]
                tmp=path.with_suffix('.tmp')
                tmp.write_text(json.dumps(result[kind],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                tmp.replace(path)
            # Source must pass every validation before this operation is accepted.
            read_site(site_id)
        except Exception:
            for path,contents in originals.items():
                path.write_bytes(contents)
            raise
    return {'operation':operation,'applied':apply,'details':details,'changedLedgers':targets}
