"""Fail-closed rendered text similarity audit for Hallflower full preview."""
from pathlib import Path
from html.parser import HTMLParser
import json, random, math, re, unicodedata
ROOT=Path(__file__).resolve().parents[1]/'dist/hallflower-full-preview'
class Visible(HTMLParser):
    def __init__(self):super().__init__();self.skip=0;self.t=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','head'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','head'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if self.skip==0:self.t.append(data)
def grams(s):
    return {s[i:i+5] for i in range(max(0,len(s)-4))}
def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    files=sorted((ROOT/'halls').glob('*.html'))
    assert len(files)==manifest['count']==1080
    texts=[];gs=[];errors=[]
    for p in files:
        html=p.read_text(encoding='utf-8')
        parser=Visible();parser.feed(html)
        txt=unicodedata.normalize('NFC',re.sub(r'\s+',' ',' '.join(parser.t))).strip()
        texts.append(txt);gs.append(grams(txt))
        if not all(x in html for x in ('noindex,nofollow','href="tel:18440644"','name="빈소"','id="make-note"','disabled','fwith.co.kr/shop/item.php?it_id=')):errors.append(p.name)
    indices=random.Random(20261029).sample(range(len(files)),math.ceil(len(files)*.01))
    max_score=0;worst=None
    for i in indices:
        for j in range(len(files)):
            if i==j:continue
            a,b=gs[i],gs[j];score=len(a&b)/len(a|b) if a|b else 1
            if score>max_score:max_score=score;worst=(files[i].name,files[j].name)
    report={'count':len(files),'seed':20261029,'sampleCount':len(indices),'comparisons':len(indices)*(len(files)-1),'thresholdExclusive':.49,'max':round(max_score,6),'worstPair':worst,'errors':errors,'pass':max_score<.49 and not errors,'scope':'NFC collapsed visible full body, 11 fixed samples against all 1080; NOT all pairs'}
    (ROOT/'similarity-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if not report['pass']:raise SystemExit('FAIL: similarity gate or content gate; do not publish')
if __name__=='__main__':main()
