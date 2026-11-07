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
from scripts.verify_county_independent_html import validate_one, scan_tree
import os

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
    independent=scan_tree(OUT)
    assert independent['pagesChecked']==95 and independent['failedCount']==0
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
        independent_page=validate_one(path,p['productSkus'])
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
        if independent_page['errors']:
            bad_words.append('실제 HTML 독립 검사 불합격: '+repr(independent_page['errors']))
        bad_price=sorted(listed_prices_in_text(body)-allowed_price)
        is_county=p.get('pageType')=='county'
        nscore=24 if not bad_words else 12
        if assembled['intro'] in [x['paragraph'] for x in assembled['sections']]:nscore-=8
        fscore=29 if not bad_sku and not bad_price and not independent_page['errors'] and set(parser.skus)==skus and len(parser.skus)==len(skus) else 8
        if not all(format(PRICES[sku],',')+'원' in html for sku in skus):fscore-=10
        if '2026-11-07' not in html:fscore-=2
        utility=29 if all('shop/item.php?it_id='+sku in html for sku in skus) else 13
        if is_county and (p['townships'] not in body or '읍·면' not in body):
            utility-=8
        if not ('빈소' in body or '장례식장' in body or '수령' in body):
            utility-=5
        # Actual rendered FAQ answers must address their own question.
        qa_checks=[]
        for faq in assembled['faq']:
            question=faq['q']
            answer=faq['a']
            if '예산' in question:
                required=('가격','상품','예산')
            elif '리본' in question or '보낸 사람' in question:
                required=('리본','명의','문구')
            elif '반입' in question:
                required=('장례식장','시설','반입')
            elif '배송비' in question or '배송' in question:
                required=('배송비','금액','수령지')
            else:
                required=('상품','수령','장례식장','군')
            aligned=any(token in answer for token in required)
            qa_checks.append({'question':question,'aligned':aligned,'answer':answer})
            if not aligned:
                utility-=10
                bad_words.append('FAQ 답변이 질문을 설명하지 않음: '+question)
        if is_county and p.get('townships') and p['townships'] not in body:
            utility-=8
        repetition=11 if is_county else 12
        if independent_page['errors']:
            fscore=min(fscore,8)
        total=nscore+fscore+utility+repetition
        reasons=[
             '주제: '+p['purpose']+' · 핵심 문단: '+', '.join(x['heading'] for x in assembled['sections'][-2:]),
             '실제 HTML 상품 카드 '+', '.join(independent_page['cards'])+
                  ' / 표시가 '+', '.join(str(independent_page['cardPrices'].get(sku))+'원' for sku in p['productSkus'])+
                  ' / 본문 불일치 '+str(independent_page['errors'] or '없음'),
             'FAQ 실제 질문·답변 '+str(len(qa_checks))+'건: '+
                  ', '.join(q['question']+' → '+('관련 답변' if q['aligned'] else '불일치') for q in qa_checks),
             ('읍면 '+str(p.get('townshipCount'))+'곳의 공식 명칭 확인; 실제 배송 가능성·읍면 배송비는 미확인' if is_county
                  else '전국/광역 허브: 포함 군 선택과 주문 링크 확인'),
             '반복·훈계·내부 표현: '+('해당 없음' if not bad_words else '; '.join(bad_words))+
                  ' / 공통 배송·리본 설명 반복 감점 '+str(15-repetition)+'점'
        ]
        scored.append({'path':item['urlPath'],'pageId':p['id'],'type':p['pageType'],
             'purpose':p['purpose'],'selectedSKUs':p['productSkus'],'score':total,
             'components':{'natural':nscore,'accuracy':fscore,'purchaseUtility':utility,'repetition':repetition},
             'reasons':reasons,'flags':bad_words,'offCardSKUs':bad_sku,'offCardPrices':bad_price,
             'independentHTML':{'sha256':independent_page['htmlSHA256'],
                               'errors':independent_page['errors'],
                               'cards':independent_page['cards']},
             'faqAssessment':qa_checks,
             'excerpt':{'intro':assembled['intro'],
                        'sections':[{'heading':v['heading'],'paragraph':v['paragraph']} for v in assembled['sections']],
                        'faq':assembled['faq']}})
    report={
        'site':ID,'sourceReviewRun':os.environ.get('GITHUB_RUN_ID') or 'LOCAL',
        'sourceSHA':os.environ.get('GITHUB_SHA') or 'LOCAL',
        'method':'Actual 95 HTML independent card/prose contract + intent-dependent FAQ and 42+ editorial samples; not independent human approval',
        'htmlPages':95,'sampleCount':len(scored),'requiredSample':max(1,math.ceil(95*.01)),
        'minScore':min(x['score'] for x in scored),'maxScore':max(x['score'] for x in scored),
        'average':round(sum(x['score'] for x in scored)/len(scored),2),
        'failures':[x for x in scored if x['score']<90],
        'allPassed':all(x['score']>=90 for x in scored),
        'humanIndependentAuditVerified':False,
        'reviewIteration':2,'previousFailure':{'runId':42364589632,'failedPaths':['/16.html','/22.html','/25.html','/77.html'],'score':81},
        'noPublicDeployment':True,
        'scores':scored}
    target=Path('artifacts/v51-county-current-quality.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('V51_COUNTY_QUALITY_REVIEW='+json.dumps({k:v for k,v in report.items() if k not in ('scores','failures')},ensure_ascii=False))
    for x in scored:print('V51_COUNTY_SCORE='+json.dumps({'path':x['path'],'score':x['score'],'reason':x['reasons']},ensure_ascii=False))
    assert report['allPassed'], 'At least one independently checked generated page failed the 90-point internal quality threshold'
    return report

if __name__=='__main__':evaluate()
