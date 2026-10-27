"""Cloudflare GET-only identity, previous-version and binding conservation.

Used with existing V4 GitHub Secrets on a pinned, reviewed V5 release.
No DNS/route/domain writes. No secret values in reports.
"""
from __future__ import annotations
import argparse,json,os,re,ssl,urllib.request,urllib.error
from pathlib import Path
HOST='quicksky.nalmada.net'
WORKER='sfv5-quicksky-preview'


def get(path):
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:raise RuntimeError("Existing V4 Cloudflare credential absent")
    req=urllib.request.Request("https://api.cloudflare.com/client/v4"+path,headers={
        "Authorization":"Bearer "+token,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=30,context=ssl.create_default_context()) as r:data=json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError("Cloudflare GET "+path.split("?")[0]+" status "+str(e.code)) from None
    if data.get("success") is not True:raise RuntimeError("Cloudflare read failed "+path.split("?")[0])
    if (data.get("result_info") or {}).get("total_pages",1)>1:
        raise RuntimeError("Cloudflare multi-page response must be handled before deployment")
    return data["result"]

def inventory():
    aid=os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if aid:
        if not re.fullmatch(r"[a-fA-F0-9]{32}",aid):raise RuntimeError("Malformed existing account ID")
        candidates=[aid]
    else:
        candidates=[a["id"] for a in get("/accounts")]
    matches=[]
    for account in candidates:
        domains=get("/accounts/"+account+"/workers/domains")
        selected=[x for x in domains if x.get("hostname")==HOST]
        if len(selected)==1 and selected[0].get("service")==WORKER:
            matches.append((account,domains))
    if len(matches)!=1:raise RuntimeError("Exact Quicksky Worker binding not uniquely established")
    aid,domains=matches[0]
    inventory=sorted([[x.get("hostname"),x.get("service")] for x in domains])
    for hostname in (HOST,"daysky.nalmada.net","plants.nalmada.net","flower.nalmada.net"):
        if not any(row[0]==hostname for row in inventory):
            raise RuntimeError("Expected existing host mapping missing: "+hostname)
    return aid,inventory

def preflight(output, *, existing_home_public=False):
    aid,domains=inventory()
    deployments=get("/accounts/"+aid+"/workers/scripts/"+WORKER+"/deployments")
    rows=deployments.get("deployments",[])
    if not rows:raise RuntimeError("No existing deployment for Worker")
    versions=rows[0].get("versions",[])
    if len(versions)!=1 or versions[0].get("percentage")!=100:
        raise RuntimeError("Existing Worker is not on single stable 100% version")
    previous=versions[0]["version_id"]
    subdomain=get("/accounts/"+aid+"/workers/subdomain")["subdomain"]
    if not re.fullmatch(r"[a-z0-9-]+",subdomain):raise RuntimeError("Unexpected workers.dev suffix")
    if existing_home_public:
        from scripts.verify_quicksky_home_release import verify
        verify()  # Reconcile the existing one-home release before adding a public key.
    else:
        # Refuse duplicate launch if homepage is already indexable. Only roll forward from audited noindex.
        req=urllib.request.Request("https://"+HOST+"/",headers={"User-Agent":"Quicksky-Bound-Home-Preflight/1"})
        with urllib.request.urlopen(req,timeout=30,context=ssl.create_default_context()) as response:
            html=response.read(200000).decode("utf-8","replace")
            if response.status!=200 or "noindex" not in response.headers.get("X-Robots-Tag","").lower():
                raise RuntimeError("Quicksky is not currently verified noindex; manual reconcile required")
            if '<meta name="robots" content="noindex,nofollow">' not in html:
                raise RuntimeError("Quicksky previous homepage is not noindex")
            if '비용 상담 안내 보기' not in html:
                raise RuntimeError("Old verified Quicksky homepage is not the expected prior release")
    record={"previousVersion":previous,"bindingsBefore":domains,
        "site":HOST,"worker":WORKER,"previousNoindexVerified":not existing_home_public,
        "previousHomeOnlyPublicVerified":existing_home_public}
    output.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print("QUICKSKY_EXISTING_WORKER_PREFLIGHT_PASS",len(domains))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("account="+aid+"\nversion="+previous+"\nsubdomain="+subdomain+"\n")

def after(before_path,output):
    prior=json.loads(before_path.read_text(encoding="utf-8"))
    aid,domains=inventory()
    if domains!=prior["bindingsBefore"]:
        raise RuntimeError("Existing custom-domain inventory changed: do not claim release complete")
    result={"worker":WORKER,"host":HOST,"allCustomDomainMappingsPreserved":True,
            "bindingCount":len(domains),"previousVersionStored":True}
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("QUICKSKY_DOMAIN_BINDINGS_PRESERVED",len(domains))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("before","after"))
    p.add_argument("--existing-home-public", action="store_true")
    p.add_argument("--before",type=Path,default=Path("quicksky-home-before.json"))
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.action=="before":preflight(args.out, existing_home_public=args.existing_home_public)
    else:after(args.before,args.out)
