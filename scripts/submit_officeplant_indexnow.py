"""Single-shot IndexNow submission guarded by live public SEO proof and prior receipt artifacts."""
from __future__ import annotations
import json,os
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="https://officeplant.nalmada.net"
PREVIEW="https://sfv52-officeplant.joseungil.workers.dev"
HOST="officeplant.nalmada.net"
REPORT=ROOT/"reports/officeplant"
RECEIPT=REPORT/"indexnow-receipt.json"
REPO="joseungil-kr/site-factory-v4"

def get(url,limit=6_000_000,headers=None):
    req=Request(url,headers={"User-Agent":"Officeplant-IndexNow-OneShot/1",**(headers or {})})
    try:
        with urlopen(req,timeout=45) as r:return r.status,r.headers,r.read(limit)
    except HTTPError as e:return e.code,e.headers,e.read(limit)

def ensure_no_prior_receipt():
    current=os.environ.get("GITHUB_RUN_ID","")
    status,_,body=get("https://api.github.com/repos/"+REPO+"/actions/workflows/v5-officeplant-public-release.yml/runs?per_page=50",limit=1_500_000,headers={"Accept":"application/vnd.github+json"})
    if status!=200:raise RuntimeError("Cannot read public release history; fail closed before IndexNow")
    runs=json.loads(body).get("workflow_runs",[])
    for run in runs:
        if str(run.get("id"))==current:continue
        run_id=run.get("id")
        status,_,body=get("https://api.github.com/repos/"+REPO+"/actions/runs/"+str(run_id)+"/artifacts?per_page=100",limit=1_500_000,headers={"Accept":"application/vnd.github+json"})
        if status!=200:raise RuntimeError("Cannot inspect prior release receipts; fail closed")
        artifacts=json.loads(body).get("artifacts",[])
        if any(a.get("name","").startswith("officeplant-indexnow-receipt-") and not a.get("expired") for a in artifacts):
            raise RuntimeError("Prior IndexNow receipt artifact exists; refusing duplicate submission")

def main():
    if os.environ.get("GITHUB_ACTIONS")!="true" or os.environ.get("GITHUB_REPOSITORY")!=REPO:
        raise SystemExit("IndexNow may only run inside the existing V4 public-release workflow")
    if os.environ.get("GITHUB_RUN_ATTEMPT","1")!="1":
        raise SystemExit("Workflow rerun is blocked; inspect the previous receipt instead")
    if RECEIPT.exists():raise SystemExit("Local receipt exists; refusing duplicate submission")
    ensure_no_prior_receipt()
    key=(ROOT/"sites/officeplant/indexnow-public-key.txt").read_text(encoding="utf-8").strip()
    if len(key)!=32 or any(c not in "0123456789abcdef" for c in key):raise SystemExit("Invalid site-scoped public key")
    status,headers,body=get(ORIGIN+"/robots.txt");robots=body.decode("utf-8","replace")
    if status!=200 or "Allow: /" not in robots or "Disallow: /" in robots or "Sitemap: "+ORIGIN+"/sitemap.xml" not in robots:
        raise SystemExit("Live robots.txt is not public")
    status,headers,body=get(ORIGIN+"/sitemap.xml")
    if status!=200:raise SystemExit("Live sitemap is not HTTP 200")
    urls=[x.text for x in ET.fromstring(body).findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if len(urls)!=3468 or len(set(urls))!=3468 or urls[0]!=ORIGIN+"/" or urls[-1]!=ORIGIN+"/moran.html":
        raise SystemExit("Live sitemap does not contain exactly 3468 unique URLs")
    status,headers,body=get(ORIGIN+"/"+key+".txt")
    if status!=200 or body.decode("utf-8","replace").strip()!=key:raise SystemExit("Public IndexNow key file mismatch")
    for path in ("/","/r/1-opening.html","/r/1732-gift.html","/moran.html"):
        status,headers,body=get(ORIGIN+path);html=body.decode("utf-8","replace")
        if status!=200 or "noindex" in headers.get("X-Robots-Tag","").lower() or '<meta name="robots" content="index,follow">' not in html:
            raise SystemExit("Public page failed live indexing check: "+path)
        if '<link rel="canonical" href="'+ORIGIN+path+'">' not in html:raise SystemExit("Canonical mismatch: "+path)
    status,headers,body=get(PREVIEW+"/")
    if status!=200 or "noindex" not in headers.get("X-Robots-Tag","").lower():raise SystemExit("Preview host is not protected by noindex")
    status,headers,body=get(PREVIEW+"/robots.txt")
    if status!=200 or b"Disallow: /" not in body:raise SystemExit("Preview robots.txt is not disallow")
    REPORT.mkdir(parents=True,exist_ok=True)
    receipt={"site":"officeplant","host":HOST,"urlCount":len(urls),"keyLocation":ORIGIN+"/"+key+".txt",
             "sourceSHA":os.environ.get("OFFICEPLANT_SOURCE_SHA"),"runId":os.environ.get("GITHUB_RUN_ID"),
             "runAttempt":os.environ.get("GITHUB_RUN_ATTEMPT"),"attemptedAt":datetime.now(timezone.utc).isoformat(),
             "outcome":"uncertain","indexingProven":False}
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    payload=json.dumps({"host":HOST,"key":key,"keyLocation":receipt["keyLocation"],"urlList":urls},ensure_ascii=False).encode("utf-8")
    # get() is a GET helper; submit the exact single batch with one POST, never a retry.
    req=Request("https://api.indexnow.org/indexnow",data=payload,headers={"Content-Type":"application/json; charset=utf-8","User-Agent":"Officeplant-IndexNow-OneShot/1"},method="POST")
    try:
        with urlopen(req,timeout=90) as r:
            status=r.status;response=r.read(3000).decode("utf-8","replace")
    except HTTPError as exc:
        status=exc.code;response=exc.read(3000).decode("utf-8","replace")
    except (URLError,OSError) as exc:
        receipt.update(outcome="uncertain",transportError=str(exc)[:500])
        RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        raise SystemExit("IndexNow transport outcome uncertain; receipt saved; never auto-retry")
    receipt.update(httpStatus=status,response=response,outcome={200:"accepted",202:"received-pending-key-verification"}.get(status,"rejected"))
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("OFFICEPLANT_INDEXNOW_RECEIPT "+json.dumps({"count":len(urls),"httpStatus":status,"outcome":receipt["outcome"]}))
    if status not in (200,202):raise SystemExit("IndexNow rejected; receipt preserved; no retry")
    return 0

if __name__=="__main__":raise SystemExit(main())
