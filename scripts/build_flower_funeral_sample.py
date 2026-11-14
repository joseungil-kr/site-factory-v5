"""Generate one noindex, text-heavy Nalmada Flower funeral sample with a reusable phrase pool."""
import json,random,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POOL=json.loads((ROOT/'data/pools/flower_funeral_sample_pool.json').read_text(encoding='utf-8'))['groups']
HALL='안산제일장례식장'
ADDRESS='경기도 안산시 상록구 수인로 1222 (일동)'
PHONE='1844-0644'
SEED=20261027
def compose():
    rng=random.Random(SEED)
    sections=[]
    for title,key in [('처음 부고를 접했을 때','intro'),('장례식장과 빈소 정보 확인','facility'),('근조화환 종류를 선택하는 기준','product'),('리본 문구와 보내는 사람 표기','ribbon'),('제작과 장례식장 배송 상담','delivery'),('조문 예절과 위로의 마음','etiquette'),('전화 주문을 준비하는 순서','order')]:
        lines=POOL[key].copy()
        rng.shuffle(lines)
        sections.append((title,' '.join(lines)))
    return sections
def build():
    rows=compose()
    text=' '.join(p for _,p in rows)
    rates=[('근조화환 기본형','59,000원'),('근조화환 고급형','79,000원'),('근조화환 특대형','99,000원')]
    css="""*{box-sizing:border-box}body{margin:0;font-family:system-ui,'Malgun Gothic',sans-serif;color:#193d32;background:#fbfaf7;line-height:1.9}a{color:inherit}.wrap{max-width:1080px;margin:auto;padding:0 20px}.top{background:#fff;border-bottom:1px solid #e2e8e3}.topin{display:flex;justify-content:space-between;align-items:center;gap:22px;min-height:70px}.brand{font-size:25px;font-weight:900;color:#14573e}.brand em{color:#ec497c;font-style:normal}.nav{display:flex;gap:18px;font-size:13px;flex-wrap:wrap}.btn{display:inline-block;padding:12px 19px;background:#125d44;color:white;border-radius:10px;text-decoration:none;font-weight:700}.hero{background:linear-gradient(115deg,#eff7ee,#fef3f0);padding:48px 0}.hero-inner{display:grid;grid-template-columns:1.35fr .65fr;align-items:center;gap:36px}.eyebrow{font-size:12px;color:#4d866b}.hero h1{line-height:1.35;font-size:clamp(27px,4vw,43px);margin:12px 0}.hero p{color:#53685b}.hero-img{border:1px solid #e3e8df;background:#fff;min-height:260px;border-radius:20px;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;padding:22px}.hero-img strong{font-size:75px;color:#d6e7d8}.layout{display:grid;grid-template-columns:minmax(0,1fr) 240px;gap:30px;margin-top:36px}.section{margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid #e2e9e2}.section h2{font-size:23px;line-height:1.4}.section p{color:#405448;font-size:15px}.aside{position:sticky;top:22px;height:max-content;border-radius:16px;background:#edf5ec;padding:20px}.price{width:100%;border-collapse:collapse;background:white}.price th,.price td{text-align:left;border-bottom:1px solid #e5e8e5;padding:12px}.price th{background:#e9f2ec}.price td:last-child{color:#bb3357;font-weight:800}.notice{color:#9b4454;font-size:12px}.footer{background:#173c31;color:white;padding:34px 0;margin-top:30px}.faq{border:1px solid #dce6dd;border-radius:10px;padding:14px;background:white;margin:12px 0}@media(max-width:700px){.topin{flex-wrap:wrap;padding:10px 0}.nav{gap:10px}.hero-inner,.layout{grid-template-columns:1fr}.hero-img{min-height:120px}.aside{position:static}.hero{padding:34px 0}}"""
    sections=''.join('<section class="section"><h2>'+html.escape(title)+'</h2><p>'+html.escape(para)+'</p></section>' for title,para in rows)
    table='<section class="section" id="prices"><h2>근조화환 종류별 가격 안내</h2><p class="notice">아래 금액은 디자인 검수용 임시 예시이며 실제 날마다꽃 판매가격이 아닙니다.</p><table class="price"><thead><tr><th>상품 구분</th><th>예시 금액</th></tr></thead><tbody>'+''.join('<tr><td>'+html.escape(a)+'</td><td>'+html.escape(b)+'</td></tr>' for a,b in rates)+'</tbody></table><p>실제 금액과 배송비, 상품 구성은 상담 시 확인해 주세요.</p></section>'
    sections=sections.replace('</section>', '</section>'+table,1)
    out=ROOT/'design-previews/flower-nalmada/ansan-funeral-sample.html'
    out.parent.mkdir(parents=True,exist_ok=True)
    body='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+HALL+' 근조화환 주문 가격안내 | 날마다꽃</title><style>'+css+'</style></head><body><header class="top"><div class="wrap topin"><span class="brand">✿ 날마다<em>꽃</em></span><nav class="nav">근조화환 · 축하화환 · 꽃바구니 · 관엽식물</nav><a class="btn" href="tel:18440644">☎ '+PHONE+'</a></div></header><div class="hero"><div class="wrap hero-inner"><div><span class="eyebrow">경기도 안산시 · 장례식장 근조화환</span><h1>'+HALL+' 근조화환 주문 가격안내</h1><p>'+ADDRESS+'</p><p>장례식장·빈소·희망 전달일을 확인하고 근조화환 종류와 주문 절차를 살펴보세요.</p><a class="btn" href="#prices">근조화환 종류별 가격 보기</a></div><div class="hero-img" role="img" aria-label="업종 공통 근조화환 이미지 자리"><strong>✿</strong><p>공통 근조화환 이미지 영역<br>승인된 상품 사진 연결 예정</p></div></div></div><main class="wrap layout"><article>'+sections+'<section><h2>자주 묻는 질문</h2><div class="faq"><b>당일 배송이 가능한가요?</b><p>지역별 제작 및 배송 여건에 따라 다르므로 주문 전에 확인해 주세요.</p></div><div class="faq"><b>빈소 호실을 모르는데 주문할 수 있나요?</b><p>확인 중이라면 상담 시 알려 주시고, 최종 전달 전에 정확한 빈소 정보를 확정해 주세요.</p></div></section></article><aside class="aside"><h3>날마다꽃 전화 주문</h3><p>장례식장명 · 빈소 · 희망일 · 리본 문구를 준비해 주세요.</p><a class="btn" href="tel:18440644">☎ '+PHONE+'</a><p class="notice">실제 상품·배송 조건은 상담 후 확정합니다.</p></aside></main><footer class="footer"><div class="wrap">날마다꽃 · '+PHONE+' · 디자인 및 콘텐츠 검수용 샘플 (검색 제외)</div></footer></body></html>'
    out.write_text(body,encoding='utf-8')
    assert 2500<=len(text)<=5000,(len(text),'sample prose length')
    assert 'noindex,nofollow' in body and '장례식장 건물' not in body
    print(json.dumps({'path':str(out),'textChars':len(text),'sections':len(rows),'sentences':sum(len(x) for x in POOL.values()),'seed':SEED},ensure_ascii=False))
if __name__=='__main__':build()
