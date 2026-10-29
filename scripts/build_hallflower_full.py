"""Preview-only nationwide expansion; STOP if the three-sample gate has not passed."""
from pathlib import Path
import importlib.util, json, argparse, re
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('hallflower_preview',ROOT/'scripts/build_hallflower.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def build():
    source=json.loads((ROOT/'sites/hallflower/facilities-frozen.json').read_text(encoding='utf-8'))
    rows=source['facilities']
    assert source['sourceBlob']=='b950e7bf2cde7b247447fbe670c976363e4e1a7e'
    assert len(rows)==1080 and len({f['id'] for f in rows})==1080
    sample_root=ROOT/'dist/hallflower-preview'
    # Enforce representative build; tests and human/mobile review are separate release gates.
    h.build()
    assert len(list((sample_root/'halls').glob('*.html')))==3
    assert (sample_root/'robots.txt').read_text().splitlines()==['User-agent: *','Disallow: /']
    h.OUT=ROOT/'dist/hallflower-full-preview'
    (h.OUT/'assets').mkdir(parents=True,exist_ok=True)
    (h.OUT/'halls').mkdir(exist_ok=True)
    for asset in (sample_root/'assets').iterdir():
        (h.OUT/'assets'/asset.name).write_bytes(asset.read_bytes())
    unique=[]
    for i,f in enumerate(rows):
        # All facilities remain explicit historic-source records, not operationally verified.
        slug=h.page(i%3,f['id'],f['name'],f['address'])
        old=h.OUT/'halls'/slug
        new=f'{i+1}-{f["id"]}.html'
        if slug!=new:old.rename(h.OUT/'halls'/new)
        unique.append((f,new))
    assert len(unique)==1080 and len(set(s for _,s in unique))==1080
    links=''.join(f'<li><a href="/halls/{slug}">{h.escape(f["name"])} 빠른 장례식화환 주문방법</a> — {h.escape(f["province"]+" "+f["district"])}</li>' for f,slug in unique)
    (h.OUT/'index.html').write_text(h.layout('장례식장별 빠른 장례식화환 주문방법','<h1>장례식장별 빠른 장례식화환 주문방법</h1><p>과거 장례식장 원장을 바탕으로 한 검색 제외 시안입니다. 현재 시설 운영과 명칭 및 주소를 확인한 목록이 아닙니다.</p><ul>'+links+'</ul>','목록'),encoding='utf-8')
    (h.OUT/'404.html').write_text((sample_root/'404.html').read_text(),encoding='utf-8')
    (h.OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    (h.OUT/'manifest.json').write_text(json.dumps({'previewOnly':True,'count':1080,'originalV4Blob':source['sourceBlob'],'unverifiedOperation':sum(f['verification']['currentOperation']=='not_checked' for f in rows),'nameReviewRequired':sum(f['verification'].get('nameReviewRequired',False) for f in rows),'publicReleaseBlocked':True,'urls':['/halls/'+slug for _,slug in unique]},ensure_ascii=False,indent=2),encoding='utf-8')
    print('FULL_PREVIEW_BUILT',len(unique),'release blocked until independent similarity and live tests')
if __name__=='__main__': build()
