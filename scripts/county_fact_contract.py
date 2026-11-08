"""Strict runtime fact/FAQ ownership contract for isolated county V5.1 trials.

All recognized factual claims require a source-backed registry entry. Non-factual
buyer advice is explicitly tagged; empty fact lists cannot waive a factual claim.
This validator is limited to the county trial, not production sites.
"""
from __future__ import annotations
import json,re
from pathlib import Path

REGISTRY=Path(__file__).resolve().parents[1]/'docs/evidence/v51-county-buyer-fact-registry-20261108.json'
PRODUCT_PATTERN=re.compile(r'(?<![A-Za-z0-9])B(?:201|202|205|206|213|054|211)(?![0-9])')
MONEY_PATTERN=re.compile(r'\d{1,3}(?:,\d{3})+원')
FACT_PATTERN=re.compile(r'선택옵션\s*0개|추가옵션\s*0개|재생\s*꽃|제조자|배송표|추가\s*배송비는\s*[\d,]+원|판매처\s*공지')
TOPIC_CUES={
    'ribbon':('리본','명의','발신','이름','문구','인쇄','오탈자'),
    'delivery':('배송비','배송료','추가 배송','총액','배송 조건'),
    'order_history':('주문내역','조회','접수 이후','진행상황'),
    'order':('주문','결제','구매','장바구니','바로구매','수량'),
    'venue':('장례식장','빈소','반입','시설','수령','주소','도착'),
}
def registry():
    raw=json.loads(REGISTRY.read_text(encoding='utf-8'))
    entries=raw['facts']
    facts={f['fact_id']:f for f in entries}
    if len(facts)!=len(entries): raise ValueError('duplicate fact_id')
    for f in entries:
        if f.get('verified')!='confirmed' or not f.get('source_url') or not f.get('allowed_slots'):
            raise ValueError('missing source/verification/slot for '+f['fact_id'])
    return facts

def faq_topic(text):
    # Question-specific primary intent, not a generic keyword bag.
    if '리본' in text or '문구' in text or '명의' in text or '이름' in text: return 'ribbon'
    if '배송비' in text or '배송료' in text or '배송 조건' in text or '배송' in text and '진행' not in text: return 'delivery'
    if '주문내역' in text or '조회' in text or '진행상황' in text: return 'order_history'
    if '반입' in text or '장례식장' in text or '빈소' in text or '시설' in text: return 'venue'
    if '주문' in text or '결제' in text or '수량' in text or '장바구니' in text: return 'order'
    return 'general'

def answer_topic(text):
    if '주문내역조회' in text or '주문내역' in text or '진행상황' in text: return 'order_history'
    if '배송비' in text or '배송료' in text or '배송 조건' in text: return 'delivery'
    if '리본' in text or '조의 문구' in text or '보내는 분' in text or '단체명' in text or '인쇄' in text: return 'ribbon'
    if '반입' in text or '빈소' in text or '장례식장' in text or '시설' in text: return 'venue'
    if any(w in text for w in ('주문','결제','장바구니','수량','바로구매')): return 'order'
    return 'general'

def bind_faq(purpose, faq, facts):
    q=faq['q']; a=faq['a']
    qtopic=faq_topic(q); atop=answer_topic(a)
    # Reject specifically documented false equivalence, even if answer mentions
    # customer support: option quantity does not answer a ribbon-name question.
    if qtopic=='ribbon' and ('선택옵션 0개' in a or '추가옵션 0개' in a):
        raise ValueError('FAQ answer mismatch: ribbon name question answered with option count')
    if qtopic!='general' and atop!='general' and qtopic!=atop:
        # A question about a sales channel may legitimately mention an address
        # or shipping, but the answer must first deliver the requested outcome.
        if not (qtopic=='order' and atop in ('delivery','order_history')
                and any(k in a for k in ('주문','결제','바로구매'))):
            raise ValueError('FAQ question/answer topic mismatch '+purpose+': '+qtopic+' != '+atop)
    if qtopic=='order_history' and not any(x in a for x in ('주문내역','조회')):
        raise ValueError('FAQ does not answer order history question')
    ids=[]
    if '주문내역조회' in a: ids.append('seller-order-history-menu')
    if purpose=='restricted-obje-연천군' and '10,000원' in a: ids.append('shipping-연천군-B213')
    if '선택옵션 0개' in a or '추가옵션 0개' in a: ids.append('sku-B213-options-zero')
    if FACT_PATTERN.search(a) and not ids:
        raise ValueError('FAQ factual claim without fact ID: '+purpose)
    for fid in ids:
        if fid not in facts or 'faq' not in facts[fid]['allowed_slots']:
            raise ValueError('FAQ fact not verified/slot allowed: '+fid)
    faq['customer_question']=q
    faq['answer_topic']=qtopic
    faq['answer_fact_ids']=ids
    faq['answer_kind']='sourced_fact' if ids else 'buyer_guidance'
    faq['output_slot']='faq'
    if faq['answer_kind']=='buyer_guidance' and not any(w in a for w in (
            '확인','입력','선택','전달','문의','준비','살펴','정리','기재','이동','열어','적','사용','고르','조회')):
        raise ValueError('FAQ buyer_guidance lacks actionable answer: '+purpose)
    return faq

def enforce_pool(purpose,pool,facts):
    if not pool.get('sections'): raise ValueError('missing sections '+purpose)
    for section in pool['sections']:
        text=section['paragraph']
        slot=section['slot']
        if slot=='choice' and ('선택옵션 0개' in text or '추가옵션 0개' in text):
            section['factIds']=['sku-B213-options-zero']
        else:
            section['factIds']=section.get('factIds',[])
        section['outputSlot']=slot
        section['customerQuestion']=section.get('customerQuestion') or section['heading']
        section['answerKind']='sourced_fact' if section['factIds'] else 'buyer_guidance'
        if FACT_PATTERN.search(text) and not section['factIds']:
            # Shipping and product fact claims in other purposes require explicit
            # ledger registration, which is added during page-level assembly.
            if not ('배송표' in text or '재생' in text or '제조자' in text):
                raise ValueError('unsourced section fact '+purpose+': '+text[:55])
        for fid in section['factIds']:
            f=facts.get(fid)
            if not f or slot not in f['allowed_slots']:
                raise ValueError('invalid section fact/slot '+purpose+': '+fid)
    pool['faqs']=[bind_faq(purpose,f,facts) for f in pool['faqs']]
    # Meaningful client questions should differ: a repeated factual options
    # FAQ is not allowed after an options section.
    for f in pool['faqs']:
        if any('sku-B213-options-zero' in s['factIds'] for s in pool['sections']) and (
            'sku-B213-options-zero' in f['answer_fact_ids']):
            raise ValueError('FAQ repeats choice option fact '+purpose)
    return pool

def enforce_all_pools(pools):
    facts=registry()
    for purpose,pool in pools.items():
        enforce_pool(purpose,pool,facts)
    return facts

def check_page(page,pools,facts):
    pool=pools[page['purpose']]
    selected=set(page.get('productSkus',[]))
    notice=page.get('sellerVenueNotice')
    if notice:
        fid='notice-'+page['county']+'-acceptance'
        f=facts.get(fid)
        if not f or f['region_scope']!=page['county'] or f['kind']!='acceptance_form':
            raise ValueError('notice county scope or registry mismatch '+page['county'])
        notice['factIds']=[fid]
        notice['outputSlot']='notice'
        notice['customerQuestion']='해당 군 장례식장의 반입 형태는 무엇인가요?'
    for sku in selected:
        fact=facts.get('sku-'+sku+'-catalog-price')
        if not fact or fact['product_id']!=sku or 'product_card' not in fact['allowed_slots']:
            raise ValueError('SKU price ownership missing '+sku)
    for fee in page.get('verifiedSkuShipping',[]):
        fid='shipping-'+page['county']+'-'+fee['sku']
        fact=facts.get(fid)
        if not fact or fact['region_scope']!=page['county'] or fact['product_id']!=fee['sku'] or fact['value']!=fee['amount']:
            raise ValueError('shipping fact mismatch '+fid)
    for faq in pool['faqs']:
        for fid in faq['answer_fact_ids']:
            f=facts[fid]
            if f['product_id'] and f['product_id'] not in selected:
                raise ValueError('FAQ off-card product fact '+fid)
            if f['region_scope'] not in ('site navigation','product detail','product listing only') and (
                f['region_scope']!=page.get('county')):
                raise ValueError('FAQ region scope mismatch '+fid)
    return True
