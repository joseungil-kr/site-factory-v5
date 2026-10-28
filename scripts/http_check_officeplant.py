"""Read-only all-URL HTTP check; local evidence is explicitly not public release evidence."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.error import HTTPError
import argparse,hashlib,json

ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--origin',default='http://127.0.0.1:8894');parser.add_argument('--public',action='store_true');args=parser.parse_args()
    manifest=json.loads((ROOT/'reports/officeplant'/('manifest-public.json' if args.public else 'manifest.json')).read_text(encoding='utf-8'))
    out=ROOT/'dist'/('officeplant-public' if args.public else 'officeplant')
    def check(page):
        path=page['path']
        try:
            with urlopen(args.origin+path,timeout=25) as res:
                data=res.read();status=res.status
            expected=(out/('index.html' if path=='/' else path.lstrip('/'))).read_bytes()
            return {'path':path,'status':status,'matchesBuild':hashlib.sha256(data).digest()==hashlib.sha256(expected).digest()}
        except Exception as exc:return {'path':path,'error':str(exc)}
    with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(check,manifest['pages']))
    try:
        with urlopen(args.origin+'/not-a-real-officeplant-url.html',timeout=25) as res:missing=res.status
    except HTTPError as exc:missing=exc.code
    failures=[x for x in results if x.get('status')!=200 or not x.get('matchesBuild')]
    report={'origin':args.origin,'scope':'public' if args.public else 'local preview','checked':len(results),'failures':failures,'missingStatus':missing,'pass':not failures and missing==404,'results':results}
    (ROOT/'reports/officeplant/http.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))
    raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()