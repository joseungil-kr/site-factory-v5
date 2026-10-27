"""Read-only verification of an independently approved future homepage-only public release.

This script is deliberately not invoked by existing noindex deployment workflows.
It makes HTTPS GET requests only; does not alter DNS, Workers, Google/Naver, IndexNow.
"""
from __future__ import annotations
import argparse,json,ssl,urllib.request,urllib.error
from pathlib import Path
from xml.etree import ElementTree as ET

PUBLIC="https://quicksky.nalmada.net"
PREVIEW="https://sfv5-quicksky-preview.joseungil.workers.dev"

def read(origin,path):
    req=urllib.request.Request(origin+path,headers={"User-Agent":"Quicksky-V5-HomeOnly-Release-Readback/1"})
    try:
        with urllib.request.urlopen(req,context=ssl.create_default_context(),timeout=30) as res:
            status=res.status;headers=res.headers;body=res.read(350000)
    except urllib.error.HTTPError as exc:
        status=exc.code;headers=exc.headers;body=exc.read(120000)
    return status,headers,body

def verify():
    checks=[]
    checks_expected=[
        (PUBLIC,"/",200,"index"),
        (PUBLIC,"/2.html",200,"noindex"),
        (PUBLIC,"/1733.html",200,"noindex"),
        (PUBLIC,"/1734.html",404,"noindex"),
        (PREVIEW,"/",200,"noindex"),
        (PREVIEW,"/2.html",200,"noindex"),
        (PREVIEW,"/1733.html",200,"noindex"),
        (PREVIEW,"/1734.html",404,"noindex"),
    ]
    for base,path,expected,robots in checks_expected:
        status,headers,body=read(base,path)
        if status!=expected:raise RuntimeError(f"{base}{path}: HTTP {status}, expected {expected}")
        text=body.decode("utf-8","replace")
        if path not in ("/1734.html",):
            wanted='name="robots" content="'+("index,follow" if robots=="index" else "noindex,nofollow")+'"'
            if wanted not in text:raise RuntimeError(f"Meta robots wrong {base}{path}")
            if "빠른스카이" not in text or "010-5322-1952" not in text:
                raise RuntimeError("Brand/phone mismatch")
        canonical='<link rel="canonical" href="'+PUBLIC+'/">'
        if robots=="index":
            if text.count(canonical)!=1 or 'noindex' in headers.get("X-Robots-Tag","").lower():
                raise RuntimeError("Home public canonical or robots header wrong")
        elif 'rel="canonical"' in text:
            raise RuntimeError("Preview or region incorrectly canonicalized")
        if base==PREVIEW and 'noindex' not in headers.get("X-Robots-Tag","").lower():
            raise RuntimeError("workers.dev missing noindex response header")
        checks.append({"url":base+path,"http":status,"scope":robots})
    pub_robots=read(PUBLIC,"/robots.txt")
    if pub_robots[0]!=200:raise RuntimeError("No public robots")
    robots=pub_robots[2].decode("utf-8","replace")
    if 'Allow: /' not in robots or 'Disallow: /' in robots or ('Sitemap: '+PUBLIC+'/sitemap.xml') not in robots:
        raise RuntimeError("Unexpected public robots directives")
    pre_robots=read(PREVIEW,"/robots.txt")
    if pre_robots[0]!=200 or "Disallow: /" not in pre_robots[2].decode("utf-8","replace"):
        raise RuntimeError("Preview robots indexable")
    sitemap=read(PUBLIC,"/sitemap.xml")
    if sitemap[0]!=200:raise RuntimeError("Public sitemap missing")
    urls=[x.text for x in ET.fromstring(sitemap[2]).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    if urls!=[PUBLIC+"/"]:raise RuntimeError("Public sitemap contains non-home URL")
    bad_sitemap=read(PREVIEW,"/sitemap.xml")
    if bad_sitemap[0]!=200 and bad_sitemap[0]!=404:raise RuntimeError("Unexpected preview sitemap status")
    if bad_sitemap[0]==200 and b"<url>" in bad_sitemap[2]:
        # Can be public XML behind noindex/robots blocked; still not a submitted sitemap.
        pass
    photo=read(PUBLIC,"/assets/images/skycar-hero.webp")
    if photo[0]!=200 or photo[2][:4]!=b'RIFF' or photo[2][8:12]!=b'WEBP':
        raise RuntimeError("Exact reviewed image unavailable")
    return {"status":"home-only-public-http-verified","homeIndexable":True,
            "regionsIndexable":False,"regionCountRetained":1732,"previewNoindex":True,
            "publicSitemapUrls":1,"indexNowSubmitted":False,"googleOrNaverSubmitted":False,
            "checks":checks}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=verify()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
