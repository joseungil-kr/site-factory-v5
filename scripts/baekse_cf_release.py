#!/usr/bin/env python3
"""Baekse isolated Cloudflare release companion for proven Site Factory V4 Actions.

Actions only. Subcommands:
- preflight: GET-only target Worker/domain collision and exact owned zone check
- preview: GET-only workers.dev 430-page, noindex and 5 WebP readback
- attach: one exact Custom Domain PUT, then HTTPS and unchanged-other-domain readback
- indexnow: ONE audited bulk POST after full 430 live URL and key validation
No DNS-record API writes, no Workers Route API writes, no other Worker updates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/baekse"
HOST="baekse.nalmada.net"
ORIGIN="https://"+HOST
WORKER="sfv54-baekse-city-preview"
PREVIEW="https://"+WORKER+".joseungil.workers.dev"
KEY=(ROOT/"sites/baekse/indexnow-key.txt").read_text(encoding="utf-8").strip()
BEFORE=REPORT/"cloudflare-before.json"
PREVIEW_FILE=REPORT/"cloudflare-preview.json"
ATTACHED=REPORT/"cloudflare-attached.json"
INDEXNOW=REPORT/"indexnow-receipt.json"
HEADER={"User-Agent":"Baekse-V4-Exact-Release/1"}
IMAGE_MANIFEST=ROOT/"sites/baekse/images-manifest.json"
CONTENT=ROOT/"reports/baekse/public-release.json"

def save(path:Path,data:dict):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def env():
    token=os.environ.get("CLOUDFLARE_API_TOKEN")
    account=os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    assert token and re.fullmatch(r"[A-Fa-f0-9]{32}",account or ""), "Existing V4 Cloudflare secret/account unavailable"
    return token,account

def cf(method,path,data=None):
    token,_=env()
    body=json.dumps(data).encode("utf-8") if data is not None else None
    hdr={"Authorization":"Bearer "+token,"Accept":"application/json"}
    if body is not None:hdr["Content-Type"]="application/json"
    req=urllib.request.Request("https://api.cloudflare.com/client/v4"+path,
                               data=body,headers=hdr,method=method)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            response=json.load(r)
            status=r.status
    except urllib.error.HTTPError as e:
        raise RuntimeError("Cloudflare "+method+" "+path.split("?")[0]+" HTTP "+str(e.code)) from None
    if status!=200 and not (method=="PUT" and status in (200,201)):
        raise RuntimeError("Cloudflare unexpected HTTP "+str(status))
    if response.get("success") is not True:
        raise RuntimeError("Cloudflare "+method+" errors "+
                           str([(x.get("code"),x.get("message")) for x in response.get("errors",[])]))
    if (response.get("result_info") or {}).get("total_pages",1)>1:
        raise RuntimeError("Cloudflare inventory paginated; fail closed")
    return response.get("result")

def domains():
    rows=cf("GET","/accounts/"+env()[1]+"/workers/domains?per_page=100")
    assert isinstance(rows,list)
    return rows

def proof(rows):
    original={"flower-a.fwith.kr":"flower-matrix-a-prod","flower-b.fwith.kr":"flower-matrix-b-prod"}
    assert all(any(x.get("hostname")==host and x.get("service")==worker for x in rows)
               for host,worker in original.items()),"Existing V4 account ownership evidence mismatch"

def zones():
    _,account=env()
    options=cf("GET","/zones?name=nalmada.net&per_page=50")
    found=[z for z in options if z.get("name")=="nalmada.net" and
           z.get("status")=="active" and (z.get("account") or {}).get("id")==account]
    assert len(found)==1,"nalmada.net zone not owned by existing authorized account"
    return found[0]

def scripts():
    rows=cf("GET","/accounts/"+env()[1]+"/workers/scripts?per_page=100")
    assert isinstance(rows,list)
    return rows

def public_dns(host=HOST):
    responses={}
    for kind in ("A","AAAA","CNAME","TXT"):
        url="https://dns.google/resolve?name="+urllib.parse.quote(host,safe="")+"&type="+kind
        req=urllib.request.Request(url,headers={"Accept":"application/dns-json"})
        with urllib.request.urlopen(req,timeout=18) as r:data=json.load(r)
        assert data.get("Status") in (0,3),"Unexpected DNS resolver status"
        answers=data.get("Answer",[])
        responses[kind]={"rcode":data["Status"],"answers":len(answers)}
    return responses

def get(host,path,limit=1000000):
    req=urllib.request.Request(host+path,headers=HEADER)
    try:
        with urllib.request.urlopen(req,timeout=28,context=ssl.create_default_context()) as resp:
            return resp.status,resp.headers,resp.read(limit)
    except urllib.error.HTTPError as e:
        return e.code,e.headers,e.read(limit)

def same_domains(before,after,addition=None):
    old={(x["hostname"],x.get("service")) for x in before}
    new={(x["hostname"],x.get("service")) for x in after}
    assert not old-new,"Cloudflare changed an existing Custom Domain binding"
    expected={(HOST,WORKER)} if addition else set()
    assert new-old==expected,("Unexpected Custom Domain delta",sorted(new-old),sorted(expected))

def verify_noindex(h):
    assert "noindex" in h.get("X-Robots-Tag","").lower(), "Missing HTTP noindex"

def preflight():
    rows=domains();proof(rows)
    zone=zones()
    matches=[x for x in rows if x.get("hostname")==HOST]
    assert not matches,"Baekse custom hostname already bound; refuse overwrite"
    script=scripts()
    assert not [s for s in script if s.get("id")==WORKER],"Target Worker already exists; refuse overwrite"
    dns=public_dns()
    assert all(x["answers"]==0 for x in dns.values()), "Existing public DNS record; refuse attachment"
    account_sub=cf("GET","/accounts/"+env()[1]+"/workers/subdomain")
    assert account_sub.get("subdomain")=="joseungil", "Preview hostname differs from pinned Worker host"
    report={"site":"baekse","status":"GET_ONLY_PRE_DEPLOY_PASS","zoneId":zone["id"],
       "domainsBefore":sorted([{"hostname":x["hostname"],"service":x.get("service")} for x in rows],
                              key=lambda x:x["hostname"]),
       "workerAbsent":True,"customDomainAbsent":True,"publicDns":dns,
       "expectedNewWorker":WORKER,"previewHost":PREVIEW,
       "manualDNSWrites":False,"routeWrites":False}
    save(BEFORE,report)
    print("BAEKSE_CF_PRE_DEPLOY_PASS "+json.dumps({"domainBindings":len(rows),"zoneActive":True,
          "workerAbsent":True,"publicDnsEmpty":True}))
    return report

def verify_preview():
    prior=json.loads(BEFORE.read_text(encoding="utf-8"))
    assert prior["status"]=="GET_ONLY_PRE_DEPLOY_PASS"
    assert [s for s in scripts() if s.get("id")==WORKER],"Worker not created by Wrangler"
    manifest=json.loads((REPORT/"manifest.json").read_text(encoding="utf-8"))
    samples=["/", "/m/dakhanmari.html", "/m/sundaeguk.html"]
    city=next(route for route,rec in manifest["pages"].items() if rec["pageType"]=="city-hub")
    menu=next(route for route,rec in manifest["pages"].items() if rec["pageType"]=="city-menu")
    samples.extend([city,menu])
    tested=[]
    for path in samples:
        status,h,body=get(PREVIEW,path)
        assert status==200,(path,status)
        verify_noindex(h)
        html=body.decode("utf-8","replace")
        assert '<meta name="robots" content="noindex,nofollow">' in html,(path,"robots")
        assert 'rel="canonical"' not in html,(path,"canonical leaked")
        assert 'tel:0314070103' in html
        tested.append({"path":path,"http":200,"noindex":True})
    images=json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))["assets"]
    for x in images:
        status,h,body=get(PREVIEW,"/assets/baekse/"+x["filename"])
        assert status==200
        verify_noindex(h)
        assert body[:4]==b"RIFF" and body[8:12]==b"WEBP"
        assert len(body)==x["bytes"] and hashlib.sha256(body).hexdigest()==x["sha256"]
    status,h,body=get(PREVIEW,"/robots.txt")
    assert status==200 and b"Disallow: /" in body
    verify_noindex(h)
    for p in ("/sitemap.xml","/"+KEY+".txt"):
        status,h,_=get(PREVIEW,p)
        assert status==404
        verify_noindex(h)
    status,h,_=get(PREVIEW,"/baekse-absent-test.html")
    assert status==404
    verify_noindex(h)
    before=prior["domainsBefore"]
    after=sorted([{"hostname":x["hostname"],"service":x.get("service")} for x in domains()],
                 key=lambda x:x["hostname"])
    assert after==before, "Preview changed some existing Custom Domains"
    data={"site":"baekse","status":"LIVE_NOINDEX_PREVIEW_PASS","origin":PREVIEW,
          "assetCount":len(images),"htmlSamples":tested,
          "robotsDisallow":True,"sitemapHidden":True,"keyHidden":True,
          "customDomainsUnchanged":True,"indexNowSent":False}
    save(PREVIEW_FILE,data)
    print("BAEKSE_PREVIEW_HTTPS_VERIFIED "+json.dumps(data))
    return data

def verify_public():
    receipt=json.loads(CONTENT.read_text(encoding="utf-8"))
    pages=receipt["urls"]
    assert len(pages)==430 and len(set(pages))==430
    manifest=json.loads((REPORT/"manifest.json").read_text(encoding="utf-8"))
    firstCity=next(path for path,info in manifest["pages"].items() if info["pageType"]=="city-hub")
    firstMenu=next(path for path,info in manifest["pages"].items() if info["pageType"]=="city-menu")
    lastMenu=next(path for path,info in reversed(list(manifest["pages"].items())) if info["pageType"]=="city-menu")
    samplePaths=["/","/m/dakhanmari.html","/m/dak-kalguksu.html",firstCity,firstMenu,lastMenu]
    sample=[]
    for p in samplePaths:
        code,h,body=get(ORIGIN,p)
        assert code==200,(p,code)
        assert "noindex" not in h.get("X-Robots-Tag","").lower(),(p,"HTTP index")
        text=body.decode("utf-8","replace")
        assert '<meta name="robots" content="index,follow">' in text
        assert '<link rel="canonical" href="'+ORIGIN+p+'">' in text
        assert "tel:0314070103" in text
        sample.append({"path":p,"status":code,"robots":"index,follow"})
    status,h,site=get(ORIGIN,"/sitemap.xml")
    assert status==200
    listed=[x.text for x in ET.fromstring(site).iter() if x.tag.endswith("loc")]
    assert listed==pages and len(listed)==430
    status,h,robots=get(ORIGIN,"/robots.txt")
    assert status==200 and b"Allow: /" in robots and b"Disallow: /" not in robots
    status,h,keyBytes=get(ORIGIN,"/"+KEY+".txt")
    assert status==200 and keyBytes==(KEY+"\n").encode(), "IndexNow ownership file does not match"
    images=json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))["assets"]
    for item in images:
        status,h,data=get(ORIGIN,"/assets/baekse/"+item["filename"])
        assert status==200 and len(data)==item["bytes"] and hashlib.sha256(data).hexdigest()==item["sha256"]
    status,h,_=get(ORIGIN,"/baekse-unknown-page.html")
    assert status==404
    verify_noindex(h)
    status,h,body=get(PREVIEW,"/")
    assert status==200
    verify_noindex(h)
    assert b'noindex,nofollow' in body and b'rel="canonical"' not in body
    status,h,body=get(PREVIEW,"/robots.txt")
    assert status==200 and b"Disallow: /" in body
    assert get(PREVIEW,"/sitemap.xml")[0]==404
    assert get(PREVIEW,"/"+KEY+".txt")[0]==404
    return {"sample":sample,"sitemapCount":len(listed),"imageSHA256Verified":len(images),
      "indexNowPublicKeyHTTP200":True,"robotsAllow":True,"previewNoindex":True,
      "indexNowSubmitted":False,"sitemapURLs":pages}

def attach():
    before=json.loads(BEFORE.read_text(encoding="utf-8"))
    preview=json.loads(PREVIEW_FILE.read_text(encoding="utf-8"))
    assert before["status"]=="GET_ONLY_PRE_DEPLOY_PASS"
    assert preview["status"]=="LIVE_NOINDEX_PREVIEW_PASS"
    current=domains();proof(current)
    assert not [x for x in current if x.get("hostname")==HOST],"Host already bound; stop before any write"
    assert len([x for x in scripts() if x.get("id")==WORKER])==1
    assert all(x["answers"]==0 for x in public_dns().values()),"Unexpected pre-attach public DNS record"
    actualZones=zones()
    assert actualZones["id"]==before["zoneId"]
    old={(x["hostname"],x.get("service")) for x in before["domainsBefore"]}
    assert {(x["hostname"],x.get("service")) for x in current}==old, "Other domain inventory changed after preflight"
    state={"site":"baekse","host":HOST,"worker":WORKER,
           "attachmentStatus":"PUT_ATTEMPT_NOT_YET_CONFIRMED","putAttemptCount":1,
           "dnsApiWrites":False,"routeApiWrites":False,"priorDomainCount":len(current),
           "publicPages":430,"key":KEY}
    save(ATTACHED,state)
    bound=cf("PUT","/accounts/"+env()[1]+"/workers/domains",
             {"hostname":HOST,"service":WORKER,"zone_id":actualZones["id"],"enabled":True})
    assert bound.get("hostname")==HOST and bound.get("service")==WORKER,"Unexpected Cloudflare attachment result"
    state["attachmentStatus"]="BOUND_NEEDS_HTTPS_VERIFY"
    save(ATTACHED,state)
    after=domains()
    same_domains(current,after,True)
    state["cloudflareReadback"]=True
    state["otherDomainMappingsPreserved"]=True
    state["domainCountAfter"]=len(after)
    save(ATTACHED,state)
    last=None
    for i in range(1,17):
        try:
            tests=verify_public()
            state.update({"attachmentStatus":"PUBLIC_430_LIVE_VERIFIED",
                          "httpsVerified":True,"httpsAttempt":i,**tests})
            # Retain only sampled URLs in receipt: full 430 listed in separate manifest.
            state.pop("sitemapURLs",None)
            save(ATTACHED,state)
            print("BAEKSE_430_CUSTOM_DOMAIN_LIVE_VERIFIED "+json.dumps(state,ensure_ascii=False))
            return state
        except (AssertionError,urllib.error.URLError,OSError,ValueError) as e:
            last=type(e).__name__+": "+str(e)[:150]
            state["httpsPendingError"]=last
            save(ATTACHED,state)
            if i<16:time.sleep(10)
    raise RuntimeError("Bound domain but HTTPS validation failed: "+str(last))

def indexnow(endpoint:str):
    # A fresh GitHub Actions runner must independently re-prove the ownership
    # and current bound Worker: never rely on a receipt from a previous runner.
    existing=domains()
    proof(existing)
    exact=[x for x in existing if x.get("hostname")==HOST]
    assert len(exact)==1 and exact[0].get("service")==WORKER, "Baekse host is not bound to the expected Worker"
    assert len([s for s in scripts() if s.get("id")==WORKER])==1
    assert zones().get("name")=="nalmada.net"
    live=verify_public()
    urls=live["sitemapURLs"]
    assert len(urls)==430 and all(url.startswith(ORIGIN+"/") for url in urls)
    assert endpoint in ("https://api.indexnow.org/indexnow","https://www.bing.com/indexnow","https://searchadvisor.naver.com/indexnow"),"Unapproved submission endpoint"
    assert not INDEXNOW.exists(),"Previous IndexNow receipt exists. Refuse duplicate submission."
    payload={"host":HOST,"key":KEY,"keyLocation":ORIGIN+"/"+KEY+".txt","urlList":urls}
    wire=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    receipt={"site":"baekse","targetHost":HOST,"endpoint":endpoint,
             "attemptCount":1,"submittedURLCount":len(urls),
             "payloadSHA256":hashlib.sha256(wire).hexdigest(),
             "keyLocation":payload["keyLocation"],
             "state":"ATTEMPT_STARTED_RESPONSE_UNKNOWN",
             "httpStatus":None,"indexingConfirmed":False}
    save(INDEXNOW,receipt)
    req=urllib.request.Request(endpoint,data=wire,method="POST",
          headers={"Content-Type":"application/json; charset=utf-8",
                   "User-Agent":"Baekse-IndexNow-430-OneShot/1"})
    try:
        with urllib.request.urlopen(req,timeout=65,context=ssl.create_default_context()) as r:
            status=r.status;body=r.read(1500).decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        status=e.code;body=e.read(1500).decode("utf-8","replace")
    except Exception as e:
        receipt["state"]="RESPONSE_UNKNOWN";receipt["errorType"]=type(e).__name__
        save(INDEXNOW,receipt)
        raise
    receipt["httpStatus"]=status
    receipt["providerResponse"]=body[:900]
    receipt["state"]={200:"RECEIVED_BY_PROVIDER",202:"RECEIVED_KEY_VERIFICATION_PENDING"}.get(status,"REJECTED_NO_AUTOMATIC_RETRY")
    save(INDEXNOW,receipt)
    print("BAEKSE_INDEXNOW_430_RESPONSE "+json.dumps(receipt,ensure_ascii=False))
    assert status in (200,202),"IndexNow provider returned "+str(status)
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("task",choices=("preflight","preview","attach","indexnow"))
    p.add_argument("--endpoint",default="https://api.indexnow.org/indexnow")
    args=p.parse_args()
    if args.task=="preflight":preflight()
    elif args.task=="preview":verify_preview()
    elif args.task=="attach":attach()
    elif args.task=="indexnow":indexnow(args.endpoint)

if __name__=="__main__":main()
