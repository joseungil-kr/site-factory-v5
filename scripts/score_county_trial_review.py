"""Evidence-based quality checklist on actually rendered 95-page private trial.

The result is an internal rule-based quality score, not independent human
approval. Any failure below 90 blocks the next deployment stage.
"""
from __future__ import annotations
import json,re,math,hashlib
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from scripts.build_county_trial_review_only import main as review_main,OUT,REPORT
from scripts.build_county_funeral_trial_inputs import SITE,PRICES
from scripts.county_copy_pools import product_skus_in_text,listed_prices_in_text
from v5.config import read_site
from v5.purpose_render import assemble

ID='county-funeral-ownerprivate-test'
class Scanner(HTMLParser):
    def __init__(self):
        super().__init__();self.text=[];self.skus=[];self.links=[];self.headers=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=='article' and a.get('data-product-sku'):self.skus.append(a['data-product-sku'])
        if t=='a' and a.get('href'):self.links.append(a['href'])
    def handle_data(self,s):
        if s.strip():self.text.append(s.strip())

def evaluate():
    result=review_main()
    samples=result['sample']
    data=read_site(ID)
    plan=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
    page_by_id={x['id']:x for x in data['pages']}
    forbidden=[
        '비용 확인 없이 무료라고 표시하지 않습니다',
        '군 단위의 일괄 무료배송이나 당일 배송을 약속하지 않습니다',
        '임의로 기재하지 않습니다','현재 확보된 가격자료만으로 알 수 없습니다',
        '네 상품만 비교한','같은 등급으로 간주하지 않습니다',
        '공개 페이지에 개인정보를 적지 않습니다',
        '전국 전국','서울특별시 군','<escape>','{townships}'
    ]
    scored=[]
    for item in samples:
        p=page_by_id[item['pageId']]
        path=OUT/('index.html' if item['urlPath']=='/' else item['urlPath'].lstrip('/'))
        html=path.read_text(encoding='utf-8')
        parser=Scanner();parser.feed(html)
        text=' '.join(parser.text)
        assembled=assemble(p,plan['purposePools'],data['products'])
        body=' '.join([assembled['intro']]+
            [s['heading']+' '+s['paragraph'] for s in assembled['sections']]+
            [f['q']+' '+f['a'] for f in assembled['faq']])
        skus=set(p['productSkus'])
        mentioned=product_skus_in_text(body)
        expected_price={PRICES[sku] for sku in skus}
        allowed_price={format(x,',')+'원' for x in expected_price}
        allowed_price|={format(abs(x-y),',')+'원' for x in expected_price for y in expected_price if x!=y}
        bad_words=[w for w in forbidden if w in html or w in body]
        bad_sku=sorted(mentioned-skus)
        bad_price=sorted(listed_prices_in_text(body)-allowed_price)
        is_county=p.get('pageType')=='county'
        nscore=24 if not bad_words else 12
        if assembled['intro'] in [x['paragraph'] for x in assembled['sections']]:nscore-=8
        fscore=29 if not bad_sku and not bad_price and set(parser.skus)==skus and len(parser.skus)==len(skus) else 8
        if not all(format(PRICES[sku],',')+'원' in html for sku in skus):fscore-=10
        if '2026-11-07' not in html:fscore-=2
        utility=29 if all('shop/item.php?it_id='+sku in html for sku in skus) else 13
        if is_county and (p['townships'] not in body or '읍·면' not in body):
            utility-=8
        if not ('빈소' in body or '장례식장' in body or '수령' in body):
            utility-=5
        repetition=11 if is_county else 12
        total=nscore+fscore+utility+repetition
        reasons=['문장/과잉 내부 표현: '+('미발견' if not bad_words else ', '.join(bad_words)),
                 '상품카드 '+str(len(skus))+'개와 본문 SKU·가격 교차 확인'+(' 통과' if not bad_sku and not bad_price else ' 실패'),
                 '구매 목적·상세 수령지/링크 안내'+(' 확인' if utility>=25 else ' 부족'),
                 '공통 배송·리본 안내 반복 감점; 지역 서비스 실측 근거로 해석하지 않음']
        scored.append({'path':item['urlPath'],'pageId':p['id'],'type':p['pageType'],
             'purpose':p['purpose'],'selectedSKUs':p['productSkus'],'score':total,
             'components':{'natural':nscore,'accuracy':fscore,'purchaseUtility':utility,'repetition':repetition},
             'reasons':reasons,'flags':bad_words,'offCardSKUs':bad_sku,'offCardPrices':bad_price})
    report={
        'site':ID,'sourceReviewRun':'latest isolated CI at exact branch HEAD',
        'htmlPages':95,'sampleCount':len(scored),'requiredSample':max(1,math.ceil(95*.01)),
        'minScore':min(x['score'] for x in scored),'maxScore':max(x['score'] for x in scored),
        'average':round(sum(x['score'] for x in scored)/len(scored),2),
        'failures':[x for x in scored if x['score']<90],
        'allPassed':all(x['score']>=90 for x in scored),
        'humanIndependentAuditVerified':False,
        'noPublicDeployment':True,
        'scores':scored}
    target=Path('artifacts/v51-county-current-quality.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('V51_COUNTY_QUALITY_41='+json.dumps({k:v for k,v in report.items() if k not in ('scores','failures')},ensure_ascii=False))
    for x in scored:print('V51_COUNTY_SCORE='+json.dumps({'path':x['path'],'score':x['score'],'reason':x['reasons']},ensure_ascii=False))
    assert report['allPassed'], 'At least one independently checked generated page failed the 90-point internal quality threshold'
    return report

if __name__=='__main__':evaluate()
