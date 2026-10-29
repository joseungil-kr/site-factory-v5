"""Preview-only nationwide expansion; STOP if the three-sample gate has not passed."""
from pathlib import Path
import importlib.util, json, argparse, re
from html import escape
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
    pool=[line.split('|',1) for line in (ROOT/'sites/hallflower/order-copy-pool.txt').read_text(encoding='utf-8').splitlines() if line.strip()]
    assert len(pool)==81
    def gf_add(a,b):
        return ((a%3+b%3)%3)+3*(((a//3+b//3)%3))
    def gf_mul(a,b):
        a0,a1=a%3,a//3
        b0,b1=b%3,b//3
        return ((a0*b0-a1*b1)%3)+3*((a0*b1+a1*b0)%3)
    def pick(n):
        coefficients=[(n//9**i)%9 for i in range(4)]
        result=[]
        for group,x in enumerate(range(9)):
            y=coefficients[3]
            for term in (coefficients[2],coefficients[1],coefficients[0]):
                y=gf_add(gf_mul(y,x),term)
            result.append(group*9+y)
        return result
    # MDS codebook, at most 3/9 paragraph blocks shared by any two distinct facilities.
    selection=[pick(i) for i in range(len(rows))]
    assert len(set(map(tuple,selection)))==len(rows)
    assert max(len(set(a)&set(b)) for i,a in enumerate(selection) for b in selection[:i])<=3
    unique=[]
    for i,f in enumerate(rows):
        name,address=f['name'],f['address']
        slug=f'{i+1}-{f["id"]}.html'
        paragraphs=''.join('<section><h2>'+escape(pool[x][0])+'</h2><p>'+escape(pool[x][1])+'</p></section>' for x in selection[i])
        # Common ordering instructions and product cards are transactional, not fabricated facility-specific facts.
        products=h.cards()
        intro='<h1>'+escape(name)+' 빠른 장례식화환 주문방법</h1><p class="muted">시설 원장 기록 주소: '+escape(address)+'. 현 주소·운영 상태·빈소는 주문 전에 다시 확인하세요.</p>'
        intro+='<p>빠른 주문 순서: 빈소 확인 → 상품·가격 선택 → 리본문구·보내는 분 → 전달 일정 상담 → 주문·배송 확인</p>'
        order='<section><h2>꽃이랑 실제 상품 선택과 주문</h2><p>상품은 주문 시점의 가격 및 반입 가능 조건을 상담한 뒤 선택하세요. 배송비와 일정은 결제 전 확인해야 합니다.</p>'+products+'</section>'
        memo='<section><h2>주문 메모 준비</h2><p>빈소와 보내는 분, 리본문구, 희망 전달시간을 정리하세요. 메모는 서버로 전송되지 않습니다.</p><div id="memo" role="group"><label>빈소 호실<input name="빈소" autocomplete="off"></label><label>보내는 분<input name="보내는분" autocomplete="off"></label><label>리본 문구<input name="추모문구"></label><label>희망 전달시간<input name="희망시간"></label></div><button type="button" id="make-note" disabled aria-disabled="true">메모 정리</button><p id="memo-status">메모 도구 준비 중입니다.</p><pre id="note-output" hidden></pre></section>'
        tail='<section><h2>접수와 배송 확인</h2><p>실제 판매처에서 주문번호와 접수 여부를 확인하세요. 몇 시간 내 도착 또는 당일 배송은 보장하지 않습니다. 빈소 변경이나 배송 이슈는 전화로 상담하세요.</p><a class="cta" href="tel:18440644">1844-0644 전화 상담</a></section>'
        page=h.layout(name+' 빠른 장례식화환 주문방법',intro+paragraphs+order+memo+tail,name)
        (h.OUT/'halls'/slug).write_text(page,encoding='utf-8')
        unique.append((f,slug))
    assert len(unique)==1080 and len(set(s for _,s in unique))==1080
    links=''.join(f'<li><a href="/halls/{slug}">{h.escape(f["name"])} 빠른 장례식화환 주문방법</a> — {h.escape(f["province"]+" "+f["district"])}</li>' for f,slug in unique)
    (h.OUT/'index.html').write_text(h.layout('장례식장별 빠른 장례식화환 주문방법','<h1>장례식장별 빠른 장례식화환 주문방법</h1><p>과거 장례식장 원장을 바탕으로 한 검색 제외 시안입니다. 현재 시설 운영과 명칭 및 주소를 확인한 목록이 아닙니다.</p><ul>'+links+'</ul>','목록'),encoding='utf-8')
    (h.OUT/'404.html').write_text((sample_root/'404.html').read_text(),encoding='utf-8')
    (h.OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    (h.OUT/'manifest.json').write_text(json.dumps({'previewOnly':True,'count':1080,'originalV4Blob':source['sourceBlob'],'unverifiedOperation':sum(f['verification']['currentOperation']=='not_checked' for f in rows),'nameReviewRequired':sum(f['verification'].get('nameReviewRequired',False) for f in rows),'publicReleaseBlocked':True,'urls':['/halls/'+slug for _,slug in unique]},ensure_ascii=False,indent=2),encoding='utf-8')
    print('FULL_UNINDEXED_INSPECTION_BUILT',len(unique),'public release remains blocked until editorial/verification/similarity gates')
if __name__=='__main__': build()
