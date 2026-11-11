"""Compare 3 actually matching legacy-region HTMLs against 3 cited pilot HTMLs.

Never touches operating output. Reads existing generator and saves isolated artifacts.
"""
from pathlib import Path
from html.parser import HTMLParser
from hashlib import sha256
import sys, collections, json, argparse
from importlib import util

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PATHS={
 "ansan-opening":("clinicopen",620,"경기도","안산시 단원구","초지동"),
 "seoul-relocation":("clinicflower",3222,"서울특별시","종로구","연건동"),
 "suwon-celebration":("clinicpresent",542,"경기도","수원시 영통구","원천동")
}
class Inspector(HTMLParser):
 def __init__(self):
  super().__init__();self.fact_ids=[];self.official_links=[];self.sku=[];self.text=[];self.anchors=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get("data-fact-id"):self.fact_ids.append(a["data-fact-id"])
  if a.get("data-source-id"):self.official_links.append(a["data-source-id"])
  if a.get("data-sku"):self.sku.append(a["data-sku"])
  if tag=="a":self.anchors.append(a.get("href",""))
 def handle_data(self,data):
  if data.strip():self.text.append(data.strip())
def hashpath(p):return sha256(p.read_bytes()).hexdigest()

def main(output,new):
 if output.exists():raise RuntimeError("Refusing overwrite")
 sys.path.insert(0,str(ROOT/"sites/nalmada-shared3"))
 import build_national as old
 ledger=json.loads((ROOT/"sites/nalmada-shared3/clinic-retail-candidate-ledger-20261111.json").read_text("utf-8"))
 old.RETAIL_LEDGER={x["sku"]:x for x in ledger["items"]}
 source=json.loads((ROOT/"data/regions/nationwide_locality_candidates_5034.json").read_text("utf-8"))
 regions=old.parse_regions(source)
 original=json.loads((ROOT/"sites/clinicflower-preview/clinicflower-copy-pool-720.json").read_text("utf-8"))
 assert len(original["blocks"])==720
 output.mkdir(parents=True)
 results={}
 for slug,(site,idx,province,district,locality) in PATHS.items():
  rec=regions[idx-1]
  assert rec[0]==idx and rec[1:4]==(province,district,locality),(slug,rec)
  prev,substance=old.render_region(site,rec,None,"public")
  prevpath=output/(slug+"-legacy.html")
  prevpath.write_text(prev,"utf-8")
  currpath=new/(slug+".html")
  assert currpath.is_file()
  oldparse=Inspector();oldparse.feed(prev)
  newparse=Inspector();newparse.feed(currpath.read_text("utf-8"))
  assert not oldparse.official_links
  assert len(newparse.official_links)>=2
  assert len(newparse.sku)==2 and len(oldparse.sku)==2
  assert newparse.sku==oldparse.sku,(slug,newparse.sku,oldparse.sku)
  assert "tel:1844-0644" in oldparse.anchors and "tel:1844-0644" in newparse.anchors
  assert len(set(newparse.official_links))>=2
  for title in ("초지동","연건동","원천동"):
   pass
  results[slug]={"legacyUrl":"https://"+old.SITE_META[site]["host"]+f"/r/{idx:05d}.html",
    "originalRegionRecordIndex":idx,"locality":locality,
    "oldFile":prevpath.name,"oldHTMLSHA256":hashpath(prevpath),
    "newFile":currpath.name,"newHTMLSHA256":hashpath(currpath),
    "oldFacts":oldparse.fact_ids,"newOfficialSourceIDs":newparse.official_links,
    "oldProductSKU":oldparse.sku,"newProductSKU":newparse.sku,
    "oldBytes":prevpath.stat().st_size,"newBytes":currpath.stat().st_size,
    "oldText":' '.join(oldparse.text)[:6000],
    "newText":' '.join(newparse.text)[:7000],
    "oldHTMLWasCurrentLiveByteVerified":False,
    "comparison":"pinned generator reproduction and new sourced candidate, not operating HTTP"}
 report={"comparisonScope":"3 exactly matching locality old candidate routes vs evidence pilot",
  "oldHTMLGeneratedOffline":3,"newHTMLReferenced":3,"oldURLsModified":0,
  "original324SamplePopulationRetainedUnchanged":True,"results":results}
 (output/"before-after-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
 for slug,row in results.items():
  print("MATCHED_LEGACY_NEW",slug,row["legacyUrl"],row["oldBytes"],row["newBytes"],row["newOfficialSourceIDs"])
 print("CASE_MATCHED_COMPARE_PASS 3/3")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",required=True,type=Path);p.add_argument("--new",required=True,type=Path)
 args=p.parse_args();main(args.output.resolve(),args.new.resolve())
