"""Read-only SEO and reachability gate for the existing 4,935-page WreathPrice build.

Produces an evidence report, never a public sitemap/RSS or IndexNow submission.
The complete HTML set is re-created from the preapproved immutable V4 ZIP.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import expand_lower

BASE=Path(__file__).resolve().parent
OUT=BASE/"dist-all-localities"
HOST="https://wreathprice.nalmada.net"
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.hrefs=[];self.images=[];self.meta={};self.canonicals=[];self.title=[];self.h1=[];self._tag=None
    def handle_starttag(self,t,attrs):
        d=dict(attrs)
        if t=="a":self.hrefs.append(d.get("href",""))
        if t=="img":self.images.append(d.get("src",""))
        if t=="meta" and d.get("name"):self.meta[d["name"].lower()]=d.get("content","")
        if t=="link" and d.get("rel")=="canonical":self.canonicals.append(d.get("href",""))
        if t in ("title","h1"):self._tag=t
    def handle_endtag(self,t):
        if t==self._tag:self._tag=None
    def handle_data(self,s):
        if self._tag=="title":self.title.append(s)
        if self._tag=="h1":self.h1.append(s)
def norm(href):
    p=urlsplit(href)
    if p.scheme and (p.scheme not in ("http","https") or p.netloc!="wreathprice.nalmada.net"):
        return None
    if not href.startswith("/") and not p.scheme:return None
    v=unquote(p.path or "/")
    if not v.startswith("/"):return None
    if v.endswith("/"):v+="index.html"
    return v
def audit(archive):
    created=expand_lower.main(archive)
    pages=sorted(OUT.rglob("*.html"))
    assert len(pages)==4935
    paths={"/"+p.relative_to(OUT).as_posix():p for p in pages}
    # Original Worker aliases: '/' serves the approved Ansan pilot.
    aliases={"/":"/ansan/index.html"}
    title_seen=collections.Counter();desc_missing=[];orphan_links=[];broken_local=[]
    noindex_missing=[];canonicals=[];image_missing=[];missing_titles=[];duplicate_h1=[]
    headings=set();unique_external=collections.Counter()
    adjacency=collections.defaultdict(set);incoming=collections.Counter()
    for key,p in paths.items():
        data=p.read_text(encoding="utf-8")
        d=Links();d.feed(data)
        title="".join(d.title).strip();h1="".join(d.h1).strip()
        if not title:missing_titles.append(key)
        if not h1:duplicate_h1.append(key)
        if d.meta.get("robots")!="noindex,nofollow":noindex_missing.append(key)
        if d.canonicals:canonicals.append(key)
        if "description" not in d.meta:desc_missing.append(key)
        title_seen[title]+=1
        for src in d.images:
            image=norm(src)
            if image and not (OUT/image.lstrip("/")).is_file():image_missing.append((key,src))
        for href in d.hrefs:
            target=norm(href)
            if target is None:
                if href.startswith("https://"):unique_external[urlsplit(href).netloc]+=1
                continue
            resolved=aliases.get(target,target)
            if resolved not in paths and (OUT/resolved.lstrip("/")).is_file():continue
            if resolved not in paths:broken_local.append((key,href));continue
            adjacency[key].add(resolved);incoming[resolved]+=1
    visited=set(); queue=collections.deque([aliases["/"]])
    while queue:
        item=queue.popleft()
        if item in visited:continue
        visited.add(item);queue.extend(adjacency.get(item,set())-visited)
    unreachable=sorted(set(paths)-visited)
    no_inbound=[x for x in paths if incoming[x]==0 and x!=aliases["/"]]
    assert len(paths)==4935
    status={
      "domain":HOST,"sourceType":"verified 2026-10-22 official legal-code ZIP",
      "sourceArchiveSHA256":created["archiveSHA256"],
      "htmlTotal":len(pages),"localityPages":created["eligibleEupMyeonDong"],
      "entry":"/","uniqueInternalPaths":len(paths),
      "reachableFromHome":len(visited),"unreachableFromHome":len(unreachable),
      "unreachableExamples":unreachable[:30],"noInboundInternalLinkCount":len(no_inbound),
      "noInboundExamples":sorted(no_inbound)[:30],
      "brokenInternalLinksCount":len(broken_local),"brokenInternalExamples":broken_local[:30],
      "missingImageFileCount":len(image_missing),"missingImageExamples":image_missing[:15],
      "noindexMissingCount":len(noindex_missing),"canonicalsFoundCount":len(canonicals),
      "missingTitleCount":len(missing_titles),"duplicateTitleGroups":sum(n>1 for n in title_seen.values()),
      "missingMetaDescriptionsCount":len(desc_missing),
      "missingMetaDescriptionExamples":desc_missing[:15],
      "externalLinkHosts":dict(unique_external),
      "publicSitemapEligibleURLs":0,"publicRSSItemsEligible":0,
      "indexNowEligibleURLs":0,"indexNowSubmitted":False,
      "indexabilityReasons":[
        "Original Worker adds X-Robots-Tag noindex,nofollow,noarchive",
        "All HTML has meta robots noindex,nofollow",
        "robots.txt disallows crawling",
        "No approved indexable page cohort: repeated locality templates and unverified purchase facts"
      ],
      "sitemapPolicy":"do not publish an indexable sitemap for noindex site",
      "rssPolicy":"do not invent a dated article feed for static geographic price templates",
      "canonicalPolicy":"deliberately absent while noindex",
      "passedGraphAudit":len(unreachable)==0 and len(broken_local)==0 and len(image_missing)==0 and len(noindex_missing)==0
    }
    report=BASE/"SEO_AUDIT_RESULT.json"
    report.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("WREATHPRICE_SEO_GRAPH_AUDIT="+json.dumps({k:v for k,v in status.items() if not isinstance(v,list) and k not in ("externalLinkHosts",)},ensure_ascii=False),flush=True)
    assert status["passedGraphAudit"],"Critical internal-link, reachability, image, or index-policy failure"
    return status

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--archive",type=Path,required=True)
    audit(parser.parse_args().archive)
