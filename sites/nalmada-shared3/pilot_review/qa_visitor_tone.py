"""Clinic 6-page buyer-first tone and national copy-pool gate, no deployment.

Checks literal regressions plus concepts/FAQ, and compares visible main content.
Human editorial review remains required: passing a regex does not make copy useful.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from collections import defaultdict
from importlib.machinery import SourceFileLoader
import hashlib,json,re

BANNED=[
    "않습니다","못합니다","단정하지","약속하지","보장하지","임의로",
    "가정하지","무조건","검증되지","미확인","달력상 개원일만",
    "현장 설치 인력이 반드시 포함","실제 배송 가능 여부",
    "해당 문구를 금지","AI 연출 이미지이며","특정 상품·배송 사례",
    "실제 시설·행사 일정","이 지역명은 배송 확정",
    "현장 배송 사례를 나타내지 않습니다","안알려주세요",
    "확인되지 않은 배송 약속","사진 속 결혼식 리본은",
    "병원 현장 배송 사진이 아닙니다","실제 수령 현장을 촬영한 사진"
]
HARD_EXACT=[
    "달력상 개원일만 보고 배송일을 정하지 않습니다",
    "현장 설치 인력이 반드시 포함된다고 약속하지 않습니다",
    "의료기관의 실제 시설·행사 일정·배송 가능 여부는 개별 확인이 필요합니다",
    "임의로 문 앞에 두지 않습니다",
    "개원 축하를 표현한 AI 연출 이미지이며 특정 상품·배송 사례를 나타내지 않습니다",
]
ROOT=Path(__file__).resolve().parents[3]
PILOT=Path(__file__).resolve().parent

class ReadBody(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth=0;self.reject=0;self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=='main':self.depth+=1
        if tag in ('script','style'):self.reject+=1
    def handle_endtag(self,tag):
        if tag=='main':self.depth-=1
        if tag in ('script','style'):self.reject-=1
    def handle_data(self,data):
        if self.depth>0 and self.reject==0 and data.strip():self.text.append(data.strip())

def all_shingles(text,n=5):
    clean=re.sub(r'\s+',' ',text).strip()
    return {clean[i:i+n] for i in range(max(0,len(clean)-n+1))}

def validate():
    pool=json.loads((ROOT/'sites/clinicflower-preview/clinicflower-copy-pool-720.json').read_text(encoding='utf-8'))
    assert len(pool['blocks'])==720
    assert len({x['id'] for x in pool['blocks']})==720
    assert len({x['body'] for x in pool['blocks']})==720
    for block in pool['blocks']:
        for k in ('body','title','question','answer'):
            v=block.get(k)
            if isinstance(v,str):
                assert not any(word in v for word in BANNED),(block['id'],k,'defensive expression')
        if block.get('category')=='업종 FAQ':
            assert block['body']==block['answer'],block['id']
    module=SourceFileLoader('clinic_builder_visitor',str(ROOT/'sites/nalmada-shared3/build_national.py')).load_module()
    extra=module.generate_extra_pool()
    for site,blocks in extra['items'].items():
        assert blocks
        assert all(not any(b in row['body'] for b in BANNED) for row in blocks),site
    originalLegacyCount=extra['count']
    assert originalLegacyCount>=3600
    manifest=json.loads((PILOT/'pilot-manifest.json').read_text(encoding='utf-8'))
    assert len(manifest['samplePages'])==6
    factReport=[]
    sections={}
    for row in manifest['samplePages']:
        raw=(PILOT/row['name']).read_text(encoding='utf-8')
        parser=ReadBody();parser.feed(raw)
        visible=' '.join(parser.text)
        for phrase in HARD_EXACT+BANNED:
            assert phrase not in visible,(row['site'],row['page'],'unfriendly visitor copy',phrase)
        assert ('<h1>' in raw and 'tel:1844-0644' in raw and
            'data-sku=' in raw and 'fwith.co.kr/shop/item.php?it_id=' in raw)
        assert 'noindex,nofollow,noarchive' in raw
        assert 'application/ld+json' not in raw
        if row['site']=='clinicpresent':
            assert '결혼식 리본' not in visible
            assert '축 개원' in visible
        sections[(row['site'],row['page'])]=visible
        factReport.append({'site':row['site'],'page':row['page'],
            'charactersVisible':len(visible),
            'paragraphPieces':len(parser.text),
            'headings':re.findall(r'<h[123][^>]*>(.*?)</h[123]>',raw,flags=re.S)[:20]})
    similarity={}
    for site in ('clinicflower','clinicopen','clinicpresent'):
        a=all_shingles(sections[(site,'ansan')]);b=all_shingles(sections[(site,'bono')])
        score=len(a&b)/len(a|b)
        similarity[site]=round(score,6)
    result={'pool720':len(pool['blocks']),'poolUniqueBody720':True,
            'compositionalPoolVariants':originalLegacyCount,
            'sixPages':len(factReport),'sitePairChar5gramJaccard':similarity,
            'zeroBannedVisitorSentences':True,'humanReviewStillRequired':True,
            'screenshotsNotProvenByThisTextAudit':True,
            'pageSummaries':factReport}
    out=ROOT/'pilot-qa'/'tone-and-content.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CLINIC_TONE_POOL_AND_SIX_HTML_PASS='+json.dumps(
        {k:v for k,v in result.items() if k!='pageSummaries'},ensure_ascii=False))

if __name__=='__main__':
    validate()
