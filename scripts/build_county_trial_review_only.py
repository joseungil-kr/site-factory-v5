"""Local-only, explicitly NON-RELEASABLE review rendering for county trial.

This keeps the mandatory V5.1 similarity gate intact. When the strict normal
build fails, this creates only offline HTML evidence for human editorial review.
It never deploys or produces an indexable sitemap.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict,deque
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import hashlib,json,shutil,xml.etree.ElementTree as ET
from v5.config import read_site, ROOT
from v5 import markup
from v5.purpose_render import assemble,render,regional_index
from v5.audit import similarity

ID='county-funeral-ownerprivate-test'
OUT=ROOT/'dist'/('unreleased-'+ID)
REPORT=ROOT/'reports'/ID/'review-only.json'
class LinkScan(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.meta=[];self.title=0;self.h1=0;self.products=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='a' and d.get('href'):self.links.append(d['href'])
  if t=='meta' and d.get('name')=='robots':self.meta.append(d.get('content'))
  if t=='title':self.title+=1
  if t=='h1':self.h1+=1
  if t=='article' and d.get('data-product-sku'):self.products.append(d.get('data-product-sku'))
def write(path,text):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(text,encoding='utf-8')
def main():
 data=read_site(ID)
 site=data['site']
 assert site['id']==ID and site['domain'] is None and site['publishEnabled'] is False
 pages=data['pages']
 assert len(pages)==95
 index=regional_index(pages)
 plan=json.loads((ROOT/'sites'/ID/'site-spec.json').read_text())
 assert plan['publishPolicy']['mode']=='owner-private-preview-only'
 assert plan['similarityAudit']=={'metric':'char-5gram-jaccard','thresholdExclusive':0.49,'sampleFraction':0.01,'seed':20261107}
 catalog=data['products'];sets=set(p['id'] for p in pages)
 assert len(sets)==95 and len(set(p['number'] for p in pages))==95
 enriched=[assemble(p,plan['purposePools'],catalog) for p in pages]
 assert all(len(p['sections'])>=5 for p in enriched)
 if OUT.exists():shutil.rmtree(OUT)
 (OUT/'assets'/'images').mkdir(parents=True)
 theme_dir=ROOT/'templates/themes'
 shutil.copyfile(theme_dir/'base.css',OUT/'assets'/'site.css')
 for theme in ('classic','modern','minimal'):
  shutil.copyfile(theme_dir/(theme+'.css'),OUT/'assets'/('theme-'+theme+'.css'))
 shutil.copyfile(ROOT/'assets/library'/ID/'county-wreath.svg',OUT/'assets/images/county-wreath.svg')
 rendered=[]
 targets=set()
 for p in pages:
  html=render(site,p,pages,catalog,[],plan['purposePools'],index)
  assert 'noindex,nofollow' in html and 'rel="canonical"' not in html
  assert not any(k in html for k in ('{county}','{province}','{parentRegion}','{region}'))
  destination=markup.filename(p['number'])
  write(OUT/destination,html);targets.add('/' if p['number']==1 else '/'+destination)
  rendered.append({'id':p['id'],'purpose':p['purpose'],'path':'/' if p['number']==1 else '/'+destination,
                   'region':p['region'],'body':assemble(p,plan['purposePools'],catalog)['intro']+' '+' '.join(x['paragraph'] for x in assemble(p,plan['purposePools'],catalog)['sections'])})
 write(OUT/'robots.txt','User-agent: *\nDisallow: /\n')
 counts=Counter(p['purpose'] for p in rendered)
 links={}
 for page in rendered:
  file=OUT/('index.html' if page['path']=='/' else page['path'].lstrip('/'))
  s=LinkScan();s.feed(file.read_text())
  assert s.title==1 and s.h1==1 and s.meta==['noindex,nofollow']
  assert len(s.products)==4 and set(s.products)=={'B201','B202','B205','B206'}
  internal={v for v in s.links if v.startswith('/')}
  assert internal<=targets|{'#main'},(page['path'],internal-targets)
  links[page['path']]=internal&targets
 reached=set();q=deque(['/'])
 while q:
  p=q.popleft()
  if p in reached:continue
  reached.add(p);q.extend(links.get(p,set())-reached)
 # Controlled review evidence only; no public sitemap gets written.
 private_sitemap=ET.Element('urlset')
 for page in rendered:
  node=ET.SubElement(private_sitemap,'url')
  ET.SubElement(node,'loc').text='https://owner-private.invalid'+page['path']
 XML=ET.tostring(private_sitemap,encoding='unicode')
 ET.fromstring(XML)
 assert len(private_sitemap)==95 and not (OUT/'sitemap.xml').exists()
 # A private audit record, not a feed or submitted URL.
 max_pair=(0.0,None,None)
 for i,a in enumerate(rendered):
  for b in rendered[i+1:]:
   score=similarity(a['body'],b['body'],'char-5gram-jaccard')
   if score>max_pair[0]:max_pair=(score,a['path'],b['path'])
 sample_paths=['/','/2.html','/3.html']+[x['path'] for x in rendered if x['purpose'].startswith('budget-') and x['id'].startswith('county-')][:2]+[x['path'] for x in rendered if x['purpose'].startswith('venue-') and x['id'].startswith('county-')][:2]+[x['path'] for x in rendered if x['purpose'].startswith('ribbon-') and x['id'].startswith('county-')][:2]
 assert len(sample_paths)==9 and len(set(sample_paths))==9
 sample=[]
 for p in sample_paths:
  row=next(x for x in rendered if x['path']==p)
  selected=next(x for x in pages if x['id']==row['id'])
  sample.append({'urlPath':p,'pageId':row['id'],'type':selected.get('pageType'),'purpose':row['purpose'],
    'region':row['region'],'sections':[{'heading':x['heading'],'paragraph':x['paragraph']} for x in assemble(selected,plan['purposePools'],catalog)['sections']],
    'intro':assemble(selected,plan['purposePools'],catalog)['intro']})
 report={'siteId':ID,'mode':'OFFLINE_REVIEW_ONLY_NOT_DEPLOYABLE','htmlCount':95,'countyCount':82,
  'provinceCount':12,'byPurpose':dict(counts),'pagesReachableFromHome':len(reached),
  'orphanCount':len(targets-reached),'missingInternalLinks':0,
  'allNoindex':True,'publicSitemapProduced':False,'rssProduced':False,'indexNowSubmitted':False,
  'privateSitemapAuditCount':95,'qualityGateApproved':False,
  'strictThreshold':0.49,'maxSimilarity':max_pair,
  'sample':sample,'draftOnly':True}
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('V51_COUNTY_OFFLINE_REVIEW='+json.dumps({k:v for k,v in report.items() if k!='sample'},ensure_ascii=False))
 for row in sample:
  print('V51_REVIEW_CONTENT='+json.dumps(row,ensure_ascii=False))
 return report
if __name__=='__main__':main()
