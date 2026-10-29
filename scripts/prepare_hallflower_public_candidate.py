"""Prepare an indexable candidate without changing the noindex preview or live Worker."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/'dist/hallflower-full-preview'
PUBLIC=ROOT/'dist/hallflower-public-candidate'
DOMAIN='https://hallflower.nalmada.net'
def main():
    manifest=json.loads((PREVIEW/'manifest.json').read_text(encoding='utf-8'))
    audit=json.loads((PREVIEW/'similarity-audit.json').read_text(encoding='utf-8'))
    assert manifest['count']==1080 and audit['pass'] and audit['max']<.49
    if manifest.get('publicReleaseBlocked') is not True:
        raise RuntimeError('Expected frozen source manifest; refusing to guess release policy')
    PUBLIC.mkdir(parents=True,exist_ok=True)
    # Copy all static artifacts, then replace host policy only in the separate candidate.
    import shutil
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
        PUBLIC.mkdir(parents=True)
    for item in PREVIEW.iterdir():
        if item.name in ('robots.txt','manifest.json','similarity-audit.json','sitemap.xml'):continue
        dest=PUBLIC/item.name
        if item.is_dir():shutil.copytree(item,dest)
        else:shutil.copy2(item,dest)
    urls=[]
    for page in sorted(PUBLIC.rglob('*.html')):
        rel=page.relative_to(PUBLIC).as_posix()
        if rel=='404.html':continue
        path='/' if rel=='index.html' else '/'+rel
        text=page.read_text(encoding='utf-8')
        text=text.replace('<meta name="robots" content="noindex,nofollow">','<meta name="robots" content="index,follow">')
        # Existing preview HTML has no canonical. Insert one on public candidate only.
        marker='<meta name="robots" content="index,follow">'
        text=text.replace(marker,marker+f'<link rel="canonical" href="{DOMAIN+path}">',1)
        page.write_text(text,encoding='utf-8')
        urls.append(DOMAIN+path)
    assert len(urls)==1081, f'Expected 1 homepage + 1080 facility pages, got {len(urls)}'
    (PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n',encoding='utf-8')
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+u+'</loc></url>\n' for u in urls)+'</urlset>\n'
    (PUBLIC/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    # Keep explicit block: creating candidate files is not authorization to bind or publish.
    report={'candidateOnly':True,'publicReleaseBlocked':True,'hostname':DOMAIN,'pages':len(urls),'sourceCount':manifest['count'],'sourceAudit':audit,'previewUnchanged':True,'sitemapUrls':len(urls),'sha256':{p.relative_to(PUBLIC).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (PUBLIC/'index.html',PUBLIC/'robots.txt',PUBLIC/'sitemap.xml')}}
    (PUBLIC/'public-candidate-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PUBLIC_CANDIDATE_PASS',json.dumps({'pages':len(urls),'canonical':len(urls),'sitemap':len(urls),'publicReleaseBlocked':True,'sha256':report['sha256']},ensure_ascii=False))
if __name__=='__main__':main()
