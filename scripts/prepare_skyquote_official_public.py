"""Prepare Skyquote public HTML from the pinned official 2026 upper-level source.
Must run only after scripts/skyquote_audit_official.py validated the exact official ZIP.
No DNS changes. Does not alter original 1536x1024 WebP/provenance.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,shutil,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/"dist/skyquote-official-preview"
OUT=ROOT/"dist/skyquote-public"
HOST="skyquote.nalmada.net"
ORIGIN="https://"+HOST
class CheckMeta(HTMLParser):
    def __init__(self):
        super().__init__();self.robots=[];self.canonicals=[]
    def handle_starttag(self,t,a):
        attrs=dict(a)
        if t=="meta" and attrs.get("name")=="robots":self.robots.append(attrs.get("content"))
        if t=="link" and attrs.get("rel")=="canonical":self.canonicals.append(attrs.get("href"))
def main():
    m=json.loads((IN/"national-manifest.json").read_text(encoding="utf-8"))
    assert m["totalContentPages"]==310 and m["nationalInfoPages"]==284 and m["ansanPreserved"]==25
    assert m["sourceArchiveSHA256"]=="44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
    assert m["noIndex"] and m["noSitemap"]
    region=json.loads((ROOT/"sites/skyquote/official-upper-regions-20261022.json").read_text(encoding="utf-8"))
    assert len(region["entries"])==284
    manifest=json.loads((ROOT/"sites/skyquote/assets-manifest.json").read_text(encoding="utf-8"))
    if OUT.exists():shutil.rmtree(OUT)
    shutil.copytree(IN,OUT)
    urls=[]
    for p in sorted(m["paths"]):
        page=OUT/p
        text=page.read_text(encoding="utf-8")
        assert text.count('name="robots" content="noindex,nofollow"')==1,p
        assert '<html lang="ko">' in text,p
        assert text.count('<img ')==5,p
        assert 'href="//' not in text,p
        text=text.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"',1)
        uri=ORIGIN+("/" if p=="index.html" else "/"+p)
        # Root page remains slash canonical, other pages retain their file paths.
        canonical='<link rel="canonical" href="'+uri+'">'
        if "</head>" in text:
            text=text.replace("</head>",canonical+"</head>",1)
        elif "<main>" in text:
            text=text.replace("<main>",canonical+"<main>",1)
        else:raise RuntimeError("Cannot insert canonical into "+p)
        page.write_text(text,encoding="utf-8")
        check=CheckMeta();check.feed(text)
        assert check.robots==["index,follow"] and check.canonicals==[uri],p
        urls.append(uri)
    assert len(urls)==310 and len(set(urls))==310
    # sitemap is constructed exclusively from content-page paths, excluding verification/static/404.
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+u+'</loc></url>\n' for u in urls)+'</urlset>\n'
    (OUT/"sitemap.xml").write_text(sitemap,encoding="utf-8")
    (OUT/"robots.txt").write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n',encoding="utf-8")
    # Content hashes preserve the independently generated illustrations.
    for img in manifest["assets"]:
        f=OUT/"assets"/Path(img["path"]).name
        assert hashlib.sha256(f.read_bytes()).hexdigest()==img["sha256"],f
    (OUT/"public-manifest.json").write_text(json.dumps({
        "publicHost":HOST,"sourceArchiveSHA256":m["sourceArchiveSHA256"],
        "sitePages":len(urls),"sitemapUrls":len(urls),"correctedOfficialUpperRecords":284,
        "ansanPages":25,"officialRawActiveRowsAreNotServiceCoverage":True,
        "serviceAvailabilityGuaranteed":False,"imageHashes":[x["sha256"] for x in manifest["assets"]],
        "paths":m["paths"],"indexMode":"index,follow on exact public host only",
        "sourceReviewedDate":"2026-10-22","userApprovedDomain":True},ensure_ascii=False,indent=2),encoding="utf-8")
    print("SKYQUOTE_PUBLIC_CANDIDATE_PASS pages=310 sitemap=310 images=5 host="+HOST)
if __name__=="__main__":main()
