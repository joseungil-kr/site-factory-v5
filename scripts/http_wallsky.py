"""Read-only HTTP checks; never call tel links or submit a lead."""
import argparse,json,sys,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
PUBLIC='https://wallsky.nalmada.net'
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
    parser=argparse.ArgumentParser();parser.add_argument('--origin',default='http://127.0.0.1:8768');parser.add_argument('--mode',choices=['auto','local','preview','public'],default='auto');args=parser.parse_args()
    mode=args.mode
    if mode=='auto':
        mode='public' if args.origin==PUBLIC else 'preview' if 'workers.dev' in args.origin else 'local'
    assert mode=='local' and args.origin=='http://127.0.0.1:8768' or mode=='public' and args.origin==PUBLIC or mode=='preview' and args.origin.startswith('https://') and 'workers.dev' in args.origin
    root=ROOT/'dist/wallsky'
    urls=ET.parse(root/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    paths=[x.text.removeprefix(PUBLIC) for x in urls]+['/style.css','/facade.webp','/sitemap.xml','/robots.txt']
    assert len(paths)==5201 and len(urls)==5197 and '/' in [x.text.removeprefix(PUBLIC) for x in urls]
    expected_robots='index,follow' if mode=='public' else 'noindex,nofollow'
    def check(path):
        try:
            status,headers,data=fetch(args.origin,path)
            if status!=200 or not data:return [path,status,'empty or non-200']
            if path.endswith('.html') or path=='/':
                meta=Meta();meta.feed(data.decode('utf-8','replace'))
                if meta.robots!=[expected_robots]:return [path,status,'robots meta '+str(meta.robots)]
                canonical=PUBLIC+('/' if path=='/' else path)
                if meta.canonical!=[canonical]:return [path,status,'canonical '+str(meta.canonical)]
                if meta.h1!=1:return [path,status,'H1 count '+str(meta.h1)]
                if mode=='public' and 'noindex' in headers.get('X-Robots-Tag','').lower():return [path,status,'HTTP noindex on public page']
                if mode=='preview' and 'noindex' not in headers.get('X-Robots-Tag','').lower():return [path,status,'preview missing HTTP noindex']
            if path=='/robots.txt':
                text=data.decode('utf-8','replace')
                if mode=='public' and ('Allow: /' not in text or 'Disallow: /' in text):return [path,status,'public robots directives']
                if mode!='public' and 'Disallow: /' not in text:return [path,status,'preview/local robots directives']
            if path=='/sitemap.xml':
                locs=ET.fromstring(data).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if len(locs)!=5197 or len({x.text for x in locs})!=5197:return [path,status,'sitemap URL count/uniqueness '+str(len(locs))]
                if mode=='preview' and 'noindex' not in headers.get('X-Robots-Tag','').lower():return [path,status,'preview sitemap missing HTTP noindex']
            if path=='/facade.webp' and (data[:4]!=b'RIFF' or data[8:12]!=b'WEBP'):return [path,status,'invalid WebP']
            return None
        except Exception as e:return [path,str(e)]
    with ThreadPoolExecutor(max_workers=8) as pool:errors=[x for x in pool.map(check,paths) if x]
    missing_status,missing_headers,missing_body=fetch(args.origin,'/not-a-wallsky-page')
    if missing_status!=404:errors.append(['/not-a-wallsky-page',missing_status,'expected 404'])
    if mode in ('public','preview') and 'noindex' not in missing_headers.get('X-Robots-Tag','').lower():
        errors.append(['/not-a-wallsky-page',missing_status,'missing X-Robots-Tag noindex'])
    error_status,error_headers,error_body=fetch(args.origin,'/404.html')
    if error_status!=200:errors.append(['/404.html',error_status,'static error asset'])
    else:
        meta=Meta();meta.feed(error_body.decode('utf-8','replace'))
        if meta.robots!=['noindex,nofollow']:errors.append(['/404.html',error_status,'error asset robots'])
    result={'origin':args.origin,'mode':mode,'checked':len(paths),'htmlURLs':5197,'errors':errors,'missingStatus':missing_status,'missing404':missing_status==404,'leadSubmitted':False,'limitation':'Public/preview mode performs live HTTP; local mode checks files/status. None of these results proves Google/Naver indexing.','passes':not errors}
    report=ROOT/'reports/wallsky/http.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False));sys.exit(0 if result['passes'] else 1)
if __name__=='__main__':main()
