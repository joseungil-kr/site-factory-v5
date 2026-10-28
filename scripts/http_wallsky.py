"""Read-only HTTP checks; never call tel links or submit a lead."""
import argparse,json,sys,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Meta(HTMLParser):
    def __init__(self):super().__init__();self.robots=[];self.canonical=[];self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content'))
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
def fetch(origin,path):
    req=urllib.request.Request(origin+path,headers={'User-Agent':'Wallsky-ReadOnly-QA/1'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:return r.status,r.headers,r.read()
    except urllib.error.HTTPError as e:return e.code,e.headers,e.read()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--origin',default='http://127.0.0.1:8768');args=parser.parse_args()
    assert args.origin in ('http://127.0.0.1:8768','https://wallsky.nalmada.net')
    root=ROOT/'dist/wallsky'
    urls=ET.parse(root/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    paths=[x.text.removeprefix('https://wallsky.nalmada.net') for x in urls]+['/style.css','/facade.webp','/sitemap.xml','/robots.txt']
    assert len(paths)==5201 and len(urls)==5197 and '/' in [x.text.removeprefix('https://wallsky.nalmada.net') for x in urls]
    def check(path):
        try:
            status,headers,data=fetch(args.origin,path)
            if status!=200 or not data:return [path,status,'empty or non-200']
            if args.origin=='https://wallsky.nalmada.net' and path.endswith('.html') or path=='/' and args.origin=='https://wallsky.nalmada.net':
                meta=Meta();meta.feed(data.decode('utf-8','replace'))
                if meta.robots!=['index,follow']:return [path,status,'robots meta '+str(meta.robots)]
                canonical='https://wallsky.nalmada.net'+('/' if path=='/' else path)
                if meta.canonical!=[canonical]:return [path,status,'canonical '+str(meta.canonical)]
                if 'noindex' in headers.get('X-Robots-Tag','').lower():return [path,status,'HTTP noindex on public page']
            if args.origin=='https://wallsky.nalmada.net' and path=='/robots.txt':
                text=data.decode('utf-8','replace')
                if 'Allow: /' not in text or 'Disallow: /' in text:return [path,status,'robots directives']
            if args.origin=='https://wallsky.nalmada.net' and path=='/sitemap.xml':
                locs=ET.fromstring(data).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if len(locs)!=5197:return [path,status,'sitemap URL count '+str(len(locs))]
            return None
        except Exception as e:return [path,str(e)]
    with ThreadPoolExecutor(max_workers=8) as pool:errors=[x for x in pool.map(check,paths) if x]
    missing_status,missing_headers,missing_body=fetch(args.origin,'/not-a-wallsky-page')
    missing_ok=missing_status==404
    if args.origin=='https://wallsky.nalmada.net':
        if 'noindex' not in missing_headers.get('X-Robots-Tag','').lower():errors.append(['/not-a-wallsky-page',missing_status,'missing X-Robots-Tag noindex'])
        code,headers,body=fetch(args.origin,'/404.html')
        if code!=200:errors.append(['/404.html',code,'expected static error asset to exist'])
        else:
            meta=Meta();meta.feed(body.decode('utf-8','replace'))
            if meta.robots!=['noindex,nofollow']:errors.append(['/404.html',code,'error asset robots'])
    result={'origin':args.origin,'checked':len(paths),'htmlURLs':5197,'errors':errors,'missingStatus':missing_status,'missing404':missing_ok,'leadSubmitted':False,'limitation':'HTTPS origin verifies actual Worker behavior; local origin verifies files/status only. This is not a Google/Naver index-status check.','passes':not errors and missing_ok}
    report=ROOT/'reports/wallsky/http.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False));sys.exit(0 if result['passes'] else 1)
if __name__=='__main__':main()
