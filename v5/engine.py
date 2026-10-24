"""Deterministic builder with full rebuild and per-page semantic content preservation."""
from __future__ import annotations
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from .config import ROOT, read_site, ConfigError
from . import markup


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def stable_hash(value)->str:
    return sha(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8'))


def files_in(path:Path):
    return sorted(p for p in path.rglob('*') if p.is_file())


def target_dir(site_id:str):
    return ROOT/'dist'/site_id


def report_dir(site_id:str):
    return ROOT/'reports'/site_id


def _write_file(out:Path,name:str,text:str):
    p=out/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8',newline='\n')


def _copy_static(site:dict,out:Path):
    shutil.copyfile(ROOT/'templates/themes/base.css',out/'assets/site.css')
    for theme in ('classic','modern','minimal'):
        shutil.copyfile(ROOT/f'templates/themes/{theme}.css',out/f'assets/theme-{theme}.css')
    shutil.copyfile(ROOT/'templates/calculator.js',out/'assets/calculator.js')
    if site.get('analytics',{}).get('enabled',False):
        shutil.copyfile(ROOT/'templates/analytics.js',out/'assets/analytics.js')
    for filename in site['imagePool']:
        shutil.copyfile(ROOT/'assets/library'/site.get('imageLibrary',site['id'])/filename,out/'assets/images'/filename)


def _manifest(data:dict,out:Path,mode:str)->dict:
    pages=data['pages'];site=data['site']
    all_files=files_in(out)
    record={'version':1,'siteId':site['id'],'domain':site['domain'],'mode':mode,
      'sourceDigest':stable_hash({k:v for k,v in data.items() if k!='root'}),
      'pageCount':len(pages),'specialPageCount':len([s for s in data['special'] if s.get('enabled',True)]),
      'assetFileCount':len(all_files),
      'contentHashes':{str(p['number']):stable_hash({'intro':p['intro'],'sections':p['sections'],'faq':p.get('faq',[]),'title':p['title'],'region':p['region'],'productSkus':p['productSkus']}) for p in pages},
      'pages':[{'id':p['id'],'number':p['number'],'filename':markup.filename(p['number']),'urlPath':markup.url_path(p['number'])} for p in pages],
      'files':{str(p.relative_to(out).as_posix()):sha(p.read_bytes()) for p in all_files}}
    record['releaseHash']=stable_hash({'sourceDigest':record['sourceDigest'],'files':record['files']})
    return record


def analyze_change(before:dict|None,after:dict)->dict:
    old=before.get('files',{}) if before else {}
    new=after['files'];old_content=before.get('contentHashes',{}) if before else {}
    now_content=after['contentHashes']
    changed=[p for p in new.keys()&old.keys() if new[p]!=old[p]]
    introduced=sorted(new.keys()-old.keys());removed=sorted(old.keys()-new.keys())
    changed_contents=sorted(p for p in now_content.keys()&old_content.keys() if now_content[p]!=old_content[p])
    return {'newFiles':introduced,'removedFiles':removed,'modifiedFiles':sorted(changed),
       'preservedContentPages':len(now_content.keys()&old_content.keys())-len(changed_contents),
       'changedContentPageNumbers':changed_contents,'newPageNumbers':sorted(now_content.keys()-old_content.keys()),
       'removedPageNumbers':sorted(old_content.keys()-now_content.keys())}


def build(site_id:str, *,output:Path|None=None,reports:Path|None=None,mode:str='preview',preserve_previous:bool=True):
    import tempfile
    from .audit import audit
    data=read_site(site_id);site=data['site']
    if site.get('status')=='draft' or not data['pages']:
        raise ConfigError('Draft site is not buildable until pages, products and images are approved')
    if mode not in ('preview','publish','public-indexing'):
        raise ConfigError('Mode must be preview, public-indexing, or publish')
    if mode=='public-indexing':
        if site['id']!='seoul-gyeonggi-plants' or site['domain']!='https://plants.nalmada.net' or not site.get('publicIndexingApproved',False):
            raise ConfigError('User-approved search indexing mode is limited to plants.nalmada.net')
    if mode=='publish':
        from .config import assert_publish_ready
        assert_publish_ready(site)
        if any(not p.get('verifiedLive',False) for p in data['products']):
            raise ConfigError('All production product destinations require renewed live verification')
        if not site.get('imageAssetsApproved',False):
            raise ConfigError('Production image pool has not been approved')
        if not site.get('cookiePrivacyReviewed',False):
            raise ConfigError('Privacy and click-measurement scope needs review before production')
    rendering_site={**site,'publishEnabled':mode=='publish','publicIndexingApproved':mode=='public-indexing'}
    out=(output or target_dir(site_id)).resolve()
    report=(reports or report_dir(site_id)).resolve()
    if out==ROOT or (ROOT in out.parents and not out.is_relative_to(ROOT/'dist')):
        raise ConfigError('Output must stay in dist/ unless using a separate external test directory')
    if any(out==x or x in out.parents for x in (ROOT/'sites',ROOT/'v5',ROOT/'assets',ROOT/'templates',ROOT/'tests',ROOT/'docs')):
        raise ConfigError('Cannot overwrite source files')
    report.mkdir(parents=True,exist_ok=True)
    old=None
    manifest_file=report/'manifest.json'
    if preserve_previous and manifest_file.exists():
        old=json.loads(manifest_file.read_text(encoding='utf-8'))
    out.parent.mkdir(parents=True,exist_ok=True)
    # Build to isolated staging; failure never touches the last checked output.
    with tempfile.TemporaryDirectory(prefix='v5-staging-',dir=out.parent) as work:
        tmp=Path(work)/'new-site'
        (tmp/'assets/images').mkdir(parents=True,exist_ok=True)
        _copy_static(rendering_site,tmp)
        for page in data['pages']:
            _write_file(tmp,markup.filename(page['number']), (markup.home if page['number']==1 else markup.detail)(rendering_site,page,data['pages'],data['products'],data['links']))
        if site.get('siteSearch',{}).get('enabled',False):
            shutil.copyfile(ROOT/'templates/search.js',tmp/'assets/search.js')
            _write_file(tmp,'search.html',markup.search_page(rendering_site,data['links']))
            entries=[{'title':p['title'],'description':p['intro'][:180], 'path':markup.url_path(p['number'])} for p in data['pages']]
            _write_file(tmp,'search-index.json',json.dumps(entries,ensure_ascii=False,separators=(',',':')))
        for item in data['special']:
            if item.get('enabled',True):
                _write_file(tmp,item['path'],markup.special_page(rendering_site,item,data['products'],data['links']))
        _write_file(tmp,'404.html',markup.error_page(rendering_site,data['links']))
        if mode=='preview':
            _write_file(tmp,'robots.txt','User-agent: *\nDisallow: /\n')
        else:
            _write_file(tmp,'robots.txt','User-agent: *\nAllow: /\nSitemap: '+site['domain'].rstrip('/')+'/sitemap.xml\n')
            all_pagepaths=[markup.url_path(p['number']) for p in data['pages']]
            all_pagepaths+=['/'+quote(s['path']) for s in data['special'] if s.get('enabled',True)]
            sitemap=('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              +''.join('<url><loc>'+markup.h(site['domain'].rstrip('/')+p)+'</loc></url>' for p in all_pagepaths)
              +'</urlset>')
            _write_file(tmp,'sitemap.xml',sitemap)
            if site.get('indexNow',{}).get('enabled',False):
                key=site['indexNow']['key']
                _write_file(tmp,key+'.txt',key+'\n')
        manifest=_manifest(data,tmp,mode)
        if len(manifest['files'])>site['staticAssetSoftLimit']:
            raise ConfigError('File count exceeds configured Worker asset soft limit')
        changes=analyze_change(old,manifest)
        if changes['removedPageNumbers']:
            raise ConfigError('Unexpected deletion of existing numbered pages; restore source ledger')
        if changes['removedFiles'] and preserve_previous:
            raise ConfigError('Removing existing deployment files requires explicit migration review: '+', '.join(changes['removedFiles'][:3]))
        inspection=audit(site_id,output=tmp,write_report=False)
        if inspection['errors']:
            raise ConfigError('Build quality gate rejected: '+ '; '.join(inspection['errors'][:4]))
        if out.exists() and preserve_previous and output is None and reports is None:
            # Keep the previous verified build as an immutable local recovery zip.
            from .release import archive
            archive(site_id,root=out,manifest=old)
        moved_backup=Path(work)/'previous'
        try:
            if out.exists():out.rename(moved_backup)
            tmp.rename(out)
        except Exception:
            if moved_backup.exists() and not out.exists():moved_backup.rename(out)
            raise
        manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (report/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (report/'audit.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if output is None and reports is None:
            from .release import archive
            archive(site_id,root=out,manifest=manifest)
    return {'manifest':manifest,'changes':changes,'output':str(out),'report':str(report),'audit':inspection}
