"""Evidence-limited WreathPrice customer wording normalizer, reused by live generator.

This module updates source HTML copy only. It never changes product URLs, prices,
image files, administrative names, robots headers or publishing eligibility.
"""
from __future__ import annotations
import hashlib,html,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
POOL=json.loads((ROOT/'customer-copy-pool.json').read_text(encoding='utf-8'))
IMAGES=POOL['imageDescriptions']
GUARD=('B201','B203','B205','C205','C030')
def copy_for_page(body:str,relative:str)->str:
    original_links=tuple(re.findall(r'https://fwith.co.kr/shop/item.php\?it_id=([A-Z0-9]+)',body))
    original_images=tuple(re.findall(r'<img[^>]+src="([^"]+)"',body))
    original_numbers=tuple(re.findall(r'(?<![\d])(?:59,000|79,000|109,000|149,000|200,000)원',body))
    for old,new in POOL['replacements']:
        body=body.replace(old,new)
    body=body.replace('AI 이미지로 살펴보는 형태와 옵션','상품 형태와 리본 안내')
    body=body.replace('AI 안내 이미지','형태 참고 이미지')
    body=body.replace('AI 이미지','형태 참고 이미지')
    body=body.replace('AI 생성','형태 안내')
    body=body.replace('AI로 생성한','안내용')
    body=body.replace('AI가 생성한','참고용')
    body=body.replace('근조·축하와 상품 코드를 선택하세요.','근조 또는 축하 상품의 종류와 가격')
    body=body.replace('배송지·시설 반입 규정과 희망 시각을 확인하세요.','받는 시설과 배송지·희망 도착시간')
    body=body.replace('배송 추가비가 있는지 확인하세요.','실제 배송지에 적용되는 배송비')
    body=body.replace('리본문구 포함 및 추가비를 확인하세요.','리본 문구와 추가 옵션 비용')
    body=body.replace('주문 화면의 실결제 총액을 확인한 뒤 결제하세요.','판매처 주문서에 표시되는 최종 결제금액')
    body=body.replace('당일 도착 가능이나 추가금 면제를 이 페이지가 보장하지 않습니다.','당일 접수와 추가금은 판매처 주문 상담에서 안내됩니다.')
    def fix_image(m):
        tag=m.group()
        src=re.search(r'src="([^"]+)"',tag)
        if not src:return tag
        asset=src.group(1).split('/')[-1]
        if asset not in IMAGES:return tag
        val=html.escape(IMAGES[asset],quote=True)
        if re.search(r'\balt="[^"]*"',tag):
            tag=re.sub(r'\balt="[^"]*"',f'alt="{val}"',tag,count=1)
        else:
            tag=tag[:-1]+f' alt="{val}">'
        return tag
    body=re.sub(r'<img\b[^>]*>',fix_image,body)
    def fix_figure(m):
        figure=m.group()
        src=re.search(r'<img[^>]+src="([^"]+)"',figure)
        if src:
            asset=src.group(1).split('/')[-1]
            if asset in IMAGES:
                caption=html.escape(IMAGES[asset],quote=False)
                figure=re.sub(r'<figcaption>.*?</figcaption>',
                              '<figcaption>'+caption+'</figcaption>',figure,flags=re.DOTALL)
        return figure
    body=re.sub(r'<figure\b[^>]*>.*?</figure>',fix_figure,body,flags=re.DOTALL)
    if relative.startswith(('locality/','region/','ansan/')):
        digest=int(hashlib.sha256(relative.encode()).hexdigest()[:8],16)
        context=POOL['buyerQuestions'][digest%len(POOL['buyerQuestions'])]
        section=('<section class="customer-choice"><h2>'+html.escape(context['title'])+'</h2>'
                 '<p>'+html.escape(context['question'])+'</p>'
                 '<p>'+html.escape(context['detail'])+'</p></section>')
        body=body.replace('</main>',section+'</main>',1)
    # The only intentional caution is about the exact purchase, never a fake delivery promise.
    assert 'AI' not in body
    assert tuple(re.findall(r'https://fwith.co.kr/shop/item.php\?it_id=([A-Z0-9]+)',body))==original_links
    assert tuple(re.findall(r'<img[^>]+src="([^"]+)"',body))==original_images
    assert tuple(re.findall(r'(?<![\d])(?:59,000|79,000|109,000|149,000|200,000)원',body))[:len(original_numbers)]==original_numbers
    return body

def apply_to_tree(root:Path)->dict:
    counts={'html':0,'updated':0}
    for p in sorted(root.rglob('*.html')):
        rel=p.relative_to(root).as_posix()
        text=p.read_text(encoding='utf-8')
        amended=copy_for_page(text,rel)
        if amended!=text:
            p.write_text(amended,encoding='utf-8')
            counts['updated']+=1
        counts['html']+=1
    return counts
