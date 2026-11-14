"""Read-only Cloudflare preflight, public HTTP readback and one-shot IndexNow.

Exact Onehour V5 custom domain and already-bound Worker only.
Existing V4 Cloudflare Actions credentials; never mutate DNS/routes/custom domains.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json,os,re,ssl
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from xml.etree import ElementTree as ET

HOST="1hrsky.nalmada.net"
WORKER="sfv5-onehour-sky-preview"
ORIGIN="https://"+HOST
PREVIEW="https://sfv5-onehour-sky-preview.joseungil.workers.dev"
NAVER="24640409f1b53459210054eec4e83176009a0a84"
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/onehour-sky"
KEY=(ROOT/"sites/onehour-sky/indexnow-public-key.txt").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"[0-9a-f]{32}",KEY):
    raise ValueError("Existing public IndexNow key is malformed")

def record(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def api_get(path):
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:raise RuntimeError("Existing V4 Cloudflare credential is absent")
    request=Request("https://api.cloudflare.com/client/v4"+path,
                   headers={"Authorization":"Bearer "+token,"Accept":"application/json"})
    try:
        with urlopen(request,timeout=35,context=ssl.create_default_context()) as response:
            obj=json.load(response)
    except HTTPError as e:
        raise RuntimeError("Cloudflare GET "+path.split("?")[0]+" HTTP "+str(e.code)) from None
    if obj.get("success") is not True or (obj.get("result_info") or {}).get("total_pages",1)>1:
        raise RuntimeError("Cloudflare exact GET failed or pagination was not handled")
    return obj["result"]

def inventory():
    configured=os.environ.get("CLOUDFLARE_ACCOUNT_ID","")
    candidates=[configured] if configured else [row["id"] for row in api_get("/accounts")]
    matches=[]
    for aid in candidates:
        if not re.fullmatch(r"[0-9a-fA-F]{32}",aid):
            continue
        try: domains=api_get("/accounts/"+aid+"/workers/domains")
        except RuntimeError:
            if configured:raise
            continue
        selected=[x for x in domains if x.get("hostname")==HOST]
        if len(selected)==1 and selected[0].get("service")==WORKER:
            matches.append((aid,sorted((x.get("hostname"),x.get("service")) for x in domains)))
    if len(matches)!=1:raise RuntimeError("Exact bound Onehour Worker not uniquely identified")
    return matches[0]

def request(origin,path,*,limit=1500000):
    req=Request(origin+path,headers={"User-Agent":"SiteFactoryV5-Onehour-ReleaseCheck/1"})
    try:
        with urlopen(req,timeout=35,context=ssl.create_default_context()) as response:
            return response.status,response.headers,response.read(limit)
    except HTTPError as err:
        return err.code,err.headers,err.read(limit)

def preflight():
    aid,bindings=inventory()
    deployed=api_get("/accounts/"+aid+"/workers/scripts/"+WORKER+"/deployments")
    rows=deployed.get("deployments",[])
    if not rows:raise RuntimeError("No live Onehour Worker version available for recovery")
    versions=rows[0].get("versions",[])
    if len(versions)!=1 or versions[0].get("percentage")!=100:
        raise RuntimeError("Worker version not stable at 100 percent")
    previous=versions[0]["version_id"]
    for path in ("/","/2.html","/5436.html"):
        status,headers,body=request(ORIGIN,path)
        if status!=200 or "noindex" not in headers.get("X-Robots-Tag","").lower():
            raise RuntimeError("Expected previous noindex domain state missing: "+path)
        if b'<meta name="robots" content="noindex,nofollow">' not in body:
            raise RuntimeError("Previous HTML is not a protected preview")
    status,_,robots=request(ORIGIN,"/robots.txt")
    if status!=200 or b"Disallow: /" not in robots:
        raise RuntimeError("Previously protected robots.txt missing")
    status,_,_=request(ORIGIN,"/sitemap.xml")
    if status!=404:raise RuntimeError("Existing indexable sitemap detected; reconcile before redeploy")
    data={"host":HOST,"worker":WORKER,"bindingsBefore":bindings,"previousVersion":previous,
          "state":"previous-noindex-verified","checkedAt":datetime.now(timezone.utc).isoformat()}
    record(REPORT/"release-before.json",data)
    output=os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output,"a",encoding="utf-8") as f:
            f.write("account="+aid+"\nversion="+previous+"\n")
    print("ONEHOUR_PRE_RELEASE_OK previousNoindex=true worker="+WORKER)
    return data

def live():
    good=[];result={"host":HOST,"worker":WORKER,"sampleChecks":[],"passed":False,
                     "indexableUrls":None,"previewNoindex":False}
    try:
        for path in ("/","/2.html","/286.html","/5436.html"):
            code,headers,payload=request(ORIGIN,path)
            text=payload.decode("utf-8","replace")
            if code!=200:raise RuntimeError("HTTP "+str(code)+" "+path)
            if "noindex" in headers.get("X-Robots-Tag","").lower():
                raise RuntimeError("Public host still has HTTP noindex: "+path)
            if '<meta name="robots" content="index,follow">' not in text:
                raise RuntimeError("Indexable HTML meta missing: "+path)
            if '<link rel="canonical" href="'+ORIGIN+path+'">' not in text:
                raise RuntimeError("Incorrect canonical: "+path)
            if "010-5322-1952" not in text or "한시간스카이" not in text:
                raise RuntimeError("Incorrect brand or owner-approved contact")
            naverCount=text.count('name="naver-site-verification"')
            if naverCount!=(1 if path=="/" else 0):
                raise RuntimeError("Unexpected Naver verification tag count: "+path)
            if path=="/" and text.count('content="'+NAVER+'"')!=1:
                raise RuntimeError("Wrong homepage verification token")
            if path!="/" and NAVER in text:
                raise RuntimeError("Naver homepage token duplicated on detail")
            good.append({"path":path,"http":code,"indexable":True,"canonical":True})
        for path in ("/5437.html","/not-an-actual-onehour-page.html"):
            code,headers,payload=request(ORIGIN,path)
            if code!=404 or b'content="noindex,nofollow"' not in payload:
                raise RuntimeError("Incorrect 404 or unprotected error page "+path)
            good.append({"path":path,"http":code,"indexable":False})
        status,_,robots=request(ORIGIN,"/robots.txt")
        r=robots.decode("utf-8","replace")
        if status!=200 or "Allow: /" not in r or "Disallow: /" in r or ("Sitemap: "+ORIGIN+"/sitemap.xml") not in r:
            raise RuntimeError("robots.txt not public")
        status,_,sitemap=request(ORIGIN,"/sitemap.xml",limit=6000000)
        if status!=200:raise RuntimeError("sitemap.xml HTTP "+str(status))
        tree=ET.fromstring(sitemap)
        urls=[e.text for e in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        if (len(urls)!=5436 or len(set(urls))!=5436
            or urls[0]!=ORIGIN+"/" or urls[-1]!=ORIGIN+"/5436.html"
            or any(not x.startswith(ORIGIN+"/") for x in urls)):
            raise RuntimeError("Sitemap scope, host, count or uniqueness mismatch")
        status,_,keybody=request(ORIGIN,"/"+KEY+".txt")
        if status!=200 or keybody.decode("utf-8","replace").strip()!=KEY:
            raise RuntimeError("IndexNow public key file not verifiable")
        for path in ("/","/robots.txt"):
            code,headers,body=request(PREVIEW,path)
            if code!=200 or "noindex" not in headers.get("X-Robots-Tag","").lower():
                raise RuntimeError("workers.dev preview host not noindex: "+path)
            if path=="/robots.txt" and b"Disallow: /" not in body:
                raise RuntimeError("workers.dev robots not blocked")
        aid,bindings=inventory()
        before=json.loads((REPORT/"release-before.json").read_text(encoding="utf-8"))
        if bindings!=[tuple(x) for x in before["bindingsBefore"]]:
            raise RuntimeError("Cloudflare custom-domain inventory drift after deployment")
        result.update(passed=True,indexableUrls=len(urls),previewNoindex=True,
                      publicRobotsAllow=True,keyFileVerified=True,bindingsUnchanged=True,
                      accountVerified=True,sampleChecks=good,
                      checkedAt=datetime.now(timezone.utc).isoformat())
        print("ONEHOUR_PUBLIC_LIVE_PASS pages=5436 sitemap=5436 naver-home=1 key=verified preview=noindex")
    except Exception as exc:
        result.update(sampleChecks=good,error=str(exc),checkedAt=datetime.now(timezone.utc).isoformat())
        record(REPORT/"release-live.json",result)
        raise
    record(REPORT/"release-live.json",result)
    return result

def submit_once():
    proof=json.loads((REPORT/"release-live.json").read_text(encoding="utf-8"))
    if not proof.get("passed") or proof.get("indexableUrls")!=5436 or not proof.get("keyFileVerified"):
        raise RuntimeError("Public live verification is required before IndexNow")
    receipt=REPORT/"indexnow-receipt.json"
    if receipt.exists():
        raise RuntimeError("Existing IndexNow receipt detected; inspect, never blindly resubmit")
    if os.environ.get("GITHUB_RUN_ATTEMPT","1")!="1":
        raise RuntimeError("IndexNow POST forbidden on workflow rerun")
    # Require exact 5,436 reviewed URLs from live sitemap, not synthetic guesses.
    status,_,payload=request(ORIGIN,"/sitemap.xml",limit=6000000)
    if status!=200:raise RuntimeError("Sitemap changed before IndexNow")
    urls=[e.text for e in ET.fromstring(payload).findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if len(urls)!=5436 or len(set(urls))!=5436 or urls[0]!=ORIGIN+"/":
        raise RuntimeError("Sitemap changed before IndexNow")
    status,_,keybody=request(ORIGIN,"/"+KEY+".txt")
    if status!=200 or keybody.decode("utf-8","replace").strip()!=KEY:
        raise RuntimeError("IndexNow key proof changed")
    data={"host":HOST,"urlCount":5436,"keyLocation":ORIGIN+"/"+KEY+".txt",
          "runId":os.environ.get("GITHUB_RUN_ID"),"attemptedAt":datetime.now(timezone.utc).isoformat(),
          "outcome":"uncertain","indexingProven":False}
    record(receipt,data)
    body=json.dumps({"host":HOST,"key":KEY,"keyLocation":data["keyLocation"],"urlList":urls},
                    ensure_ascii=False).encode("utf-8")
    req=Request("https://api.indexnow.org/indexnow",data=body,
                headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
    try:
        with urlopen(req,timeout=90,context=ssl.create_default_context()) as resp:
            code=resp.status;response=resp.read(2000).decode("utf-8","replace")
    except HTTPError as err:
        code=err.code;response=err.read(2000).decode("utf-8","replace")
    # Transport errors retain an 'uncertain' receipt; never retry automatically.
    data.update(httpStatus=code,response=response,
                outcome={200:"accepted",202:"received-pending-key-verification"}.get(code,"rejected"))
    record(receipt,data)
    if code not in (200,202):
        raise RuntimeError("IndexNow rejected HTTP "+str(code)+"; receipt written, no automatic retry")
    print("ONEHOUR_INDEXNOW_RECEIVED count=5436 http="+str(code))
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("before","live","indexnow"))
    a=p.parse_args()
    if a.command=="before":return preflight()
    if a.command=="live":return live()
    return submit_once()

if __name__=="__main__":
    main()
