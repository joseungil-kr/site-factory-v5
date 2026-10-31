"""Pinned 2026-10-22 official legal-code 읍·면·동 noindex expansion.

Requires the exact V4 source ZIP as an explicit build input. Never infer that
a region name establishes service availability. No network, publishing or auth.
"""
from __future__ import annotations
import argparse,csv,hashlib,html,io,json,shutil,zipfile
from collections import defaultdict
from pathlib import Path
import expand_nationwide

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist-all-localities'
EXPECTED_SHA='44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd'
IMAGE_FILES=['funeral-wreath.webp','celebration-wreath.webp','flower-detail.webp','ribbon-guide.webp','florist-preparation.webp']
ORDER_LINKS=[
 ('근조 3단 기본','B201','59,000'),('근조 3단 고급','B203','79,000'),('근조 3단 특대','B205','109,000'),
 ('축하 3단 화환','C205','149,000'),('축하 2단 오브제','C030','200,000')
]
def e(s):return html.escape(str(s),quote=True)
def render_index(title,intro,links):
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<meta name="robots" content="noindex,nofollow"><title>'+e(title)+'</title>'
      '<link rel="stylesheet" href="/assets/site.css"></head><body>'
      '<header><div class="wrap"><a href="/">알뜰화환 가격 안내</a></div></header>'
      '<main class="wrap"><section><h1>'+e(title)+'</h1><p>'+e(intro)+'</p>'
      '<ul>'+''.join('<li><a href="'+e(u)+'">'+e(n)+'</a></li>' for n,u in links)
      +'</ul></section></main></body></html>')
def main(archive):
    assert archive.is_file(), 'Pinned official ZIP missing, abort'
    blob=archive.read_bytes()
    assert hashlib.sha256(blob).hexdigest()==EXPECTED_SHA, 'Official archive hash mismatch'
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=z.namelist()
        assert len(names)==1
        txt=z.read(names[0]).decode('cp949')
    lines=list(csv.reader(io.StringIO(txt),delimiter=chr(9)))
    assert lines[0]==['법정동코드','법정동명','폐지여부'], lines[0]
    allactive=[r for r in lines[1:] if len(r)==3 and r[2].strip()=='존재']
    eligible=[r for r in allactive if r[1].split()[-1].endswith(('읍','면','동'))]
    upper=json.loads((ROOT/'verified-regions-nationwide.json').read_text())['entries']
    assert len(upper)==284
    upper_names=sorted(upper,key=lambda x:len(x['fullName']),reverse=True)
    provinces={x['fullName']:x for x in upper if x['level']=='province'}
    assert len(provinces)==16
    assert len(set(r[0] for r in eligible))==len(eligible)
    records=[];excluded=[]
    for code,name,status in eligible:
        parent=next((x for x in upper_names if name.startswith(x['fullName']+' ')),None)
        province=next((x for n,x in provinces.items() if name.startswith(n+' ')),None)
        if not parent or not province:
            excluded.append({'code':code,'name':name,'reason':'official upper-level parent not found'})
            continue
        records.append({'code':code,'name':name,'parentCode':parent['code'],'parentName':parent['fullName'],
            'provinceCode':province['code'],'province':province['fullName'],'suffix':name.split()[-1][-1]})
    assert not excluded, 'Unmatched official parent rows; investigate before broad publication'
    assert len(records)==len(eligible) and len(records)>3000
    expand_nationwide.build()
    if OUT.exists():shutil.rmtree(OUT)
    shutil.copytree(ROOT/'dist-nationwide',OUT)
    (OUT/'locality').mkdir(exist_ok=True)
    (OUT/'localities').mkdir(exist_ok=True)
    images=json.loads((ROOT/'image-manifest.json').read_text())['images']
    image_map={x['filename']:x for x in images}
    assert set(image_map)==set(IMAGE_FILES)
    figures=''.join(
      '<figure class="card"><img src="/assets/'+e(n)+'" alt="AI가 생성한 '+e(n.replace('.webp','').replace('-',' '))+
      ' 유형 안내 이미지. 실물 배송·상품사진 아님" width="'+str(image_map[n]['width'])+'" height="'+
      str(image_map[n]['height'])+'" loading="lazy" decoding="async"><figcaption>'
      'AI 안내 이미지. 실제 판매 상품·납품 사례가 아닙니다.</figcaption></figure>'
      for n in IMAGE_FILES)
    product_rows=''.join(
      '<tr><td>'+e(name)+'</td><td>'+e(price)+'원</td><td><a href="https://fwith.co.kr/shop/item.php?it_id='+
      e(sku)+'" rel="noopener noreferrer">상품 상세·주문 조건 확인</a></td></tr>'
      for name,sku,price in ORDER_LINKS)
    catalog_note=('근조 B201·B203·B205는 2026-10-22 상품 원장 기준이며, 축하 C205·C030은 '
      '2026-10-30 확인 기록 기준입니다. 현재 판매 가격·재고·실제 결제총액은 판매처에서 다시 확인해야 합니다.')
    by_province=defaultdict(list)
    for r in records:
        by_province[r['provinceCode']].append(r)
        name=r['name'];parent=r['parentName']
        # The source confirms the name/parent/type, not local delivery facts.
        # Practical questions vary only by verified administrative level.
        kind={'동':'동','읍':'읍','면':'면'}[r['suffix']]
        address_question=('수령 장소가 '+name+'에 있다면, 주문서의 도로명 주소와 시설명을 먼저 확인하셨나요?')
        schedule_question=('꽃 배송 접수 전에 정확한 수령지, 희망 날짜·시간, 시설의 반입 가능 시간 등을 판매처에 전달하셨나요?')
        additional_question=('해당 수령지의 배송 가능 여부, 추가 배송비, 리본 문구·제작비가 포함되는지 확인하셨나요?')
        admin_context=('2026-10-22에 확보한 법정동 코드 자료에 기록된 '+kind+' 지역명은 '+name+'이며, 상위 행정구역은 '+parent+'입니다. '
          '이 정보는 배송 지점의 존재나 배송 가능 여부를 확인한 자료가 아닙니다.')
        desc=(name+'의 화환 가격을 알아보는 고객에게 표시가와 주문 전 확인할 추가비를 구분해 안내합니다. '
              '지역명은 행정구역명이며 화환 제작·배송 지점, 실제 배송 가능 여부를 보증하지 않습니다.')
        pagestr=(
          '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<meta name="robots" content="noindex,nofollow"><title>'+e(name)+' 화환 가격, 근조·축하 상품과 최종 주문금액 | 알뜰화환</title>'
          '<meta name="description" content="'+e(desc[:145])+'">'
          '<link rel="stylesheet" href="/assets/site.css"></head><body><header><div class="wrap">'
          '<a href="/">알뜰화환</a></div></header><section class="hero"><div class="wrap">'
          '<h1>'+e(name)+' 화환 가격</h1><p>'+e(desc)+'</p></div></section><main class="wrap">'
          '<section><h2>실제 확인된 근조·축하 화환 상품 기준가</h2>'
          '<div class="overflow"><table><thead><tr><th>상품 유형</th><th>표시 기준가</th><th>실제 상품 확인</th></tr></thead>'
          '<tbody>'+product_rows+'</tbody></table></div><p>'+e(catalog_note)+'</p></section>'
          '<section><h2>근조 3단 상품끼리의 비교</h2>'
          '<p>근조 기본형(B201)은 59,000원, 고급형(B203)은 79,000원, 특대형(B205)은 109,000원입니다. '
          '표시 기준가의 차이는 각각 20,000원 및 30,000원입니다. 꽃의 종류·수량·높이는 '
          '실제 상품 상세 기준으로 확인해야 하며 가격 차이가 사양 차이와 같다는 뜻은 아닙니다.</p>'
          '<h2>축하 상품은 용도와 형태별로 선택</h2><p>축하 3단 화환(C205)과 2단 오브제(C030)는 '
          '형태가 서로 다릅니다. 근조 상품의 크기별 가격 등급에 섞어 비교하지 않고 행사 목적에 따라 선택합니다.</p></section>'
          '<section><h2>형태·리본·배송 준비 안내 이미지</h2><div class="cards">'+figures+'</div></section>'
          '<section><h2>주문 전 최종금액 확인</h2><p>최종 결제액은 실제 상품가 + 확인된 추가 배송비 + '
          '리본·옵션 비용(해당 시)입니다. 이 지역의 실제 배송 가능 여부, 추가 배송료, '
          '리본 기본 포함 여부는 현재 확인되지 않았습니다. 실제 시설명·배송지·희망 날짜를 '
          '판매처에 알려 상담한 뒤 결제 화면에서 총액을 확인하세요.</p>'
          '<p>현재 확인된 지역별 배송 가능 사례: 0건. '
          '지역명 목록이 전국 배송이나 최저가를 보장하지 않습니다.</p></section>'
          '<section><h2>지역명과 배송지 확인</h2><p>'+e(admin_context)+'</p>'
          '<p>같은 '+e(kind)+' 명칭이라도 결제 전에는 정확한 수령 시설명과 상세 주소를 별도로 전달해야 합니다.</p>'
          '<p><a href="/localities/'+e(r['provinceCode'])+'.html">해당 시·도 읍면동 목록</a> · '
          '<a href="/localities/">전국 읍면동 목록</a> · <a href="/regions/">시·군·구 목록</a></p>'
          '</section><section><h2>실제 주문 전 확인 질문</h2>'
          '<details><summary>'+e(address_question)+'</summary>'
          '<p>행정구역명만으로 배송지를 확정할 수 없습니다. 정확한 도로명 주소, 수령 시설명과 필요한 경우 빈소·행사장 정보를 판매처에 전달하세요. 개인정보는 이 안내 페이지에서 수집하지 않습니다.</p></details>'
          '<details><summary>'+e(schedule_question)+'</summary>'
          '<p>현재 이 지역의 배송 가능 시간이나 당일 배송 여부는 확인되지 않았습니다. 판매처에 정확한 날짜·시간을 알려 접수 가능 여부를 확인하세요.</p></details>'
          '<details><summary>'+e(additional_question)+'</summary>'
          '<p>표시 상품가는 최종 결제금액을 보장하지 않습니다. 실제 배송지에 적용되는 추가 운송비, 리본 문구와 옵션 금액을 확인한 뒤 주문서의 총액을 검토하세요.</p></details>'
          '<details><summary>근조 기본형과 고급형은 무엇이 다른가요?</summary>'
          '<p>확인된 기준가 차이는 20,000원입니다. 실제 꽃 구성·품종·크기를 가격만으로 추정하지 말고 두 상품 상세의 규격을 비교하세요.</p></details>'
          '</section></main></body></html>')
        (OUT/'locality'/f"{r['code']}.html").write_text(pagestr,encoding='utf-8')
    directory=[]
    for n,p in provinces.items():
        group=by_province[p['code']]
        if not group:continue
        href='/localities/'+p['code']+'.html'
        directory.append((n+' — '+str(len(group))+'개 지역명',href))
        text=render_index(n+' 읍면동 지역명 화환 가격 안내',
          '2026-10-22 확보 법정동 코드 원장의 이름 목록입니다. 각 읍면동의 화환 배송 가능 여부, 배송비, 배송시간은 확인되지 않았습니다.',
          [(r['name'],'/locality/'+r['code']+'.html') for r in group])
        (OUT/'localities'/f"{p['code']}.html").write_text(text,encoding='utf-8')
    assert len(directory)==16
    (OUT/'localities/index.html').write_text(render_index('전국 읍면동 지역명 화환 가격 안내',
      '법정동 코드 2026-10-22 확보 자료 기준 지역명 목록이며 실제 배송 가능 범위는 미확인입니다.',
      directory),encoding='utf-8')
    home=OUT/'ansan/index.html'
    text=home.read_text(encoding='utf-8')
    assert '</main>' in text
    text=text.replace('</main>',
        '<section><h2>읍·면·동 지역명 안내</h2><p>전국 법정동 코드에서 확인된 읍면동 지역명으로 '
        '화환 상품 기준가를 살펴보세요. 지역별 배송 가능 여부는 미확인입니다.</p>'
        '<a href="/localities/">전국 읍면동 목록 보기</a></section></main>')
    home.write_text(text,encoding='utf-8')
    report={'mode':'noindex-official-2026-10-22-archive','archiveSHA256':EXPECTED_SHA,
      'sourceRows':len(lines)-1,'activeRows':len(allactive),'eligibleEupMyeonDong':len(eligible),
      'verifiedParentLocalities':len(records),'unmatched':excluded,
      'upperRegions':284,'pilotPages':3,'upperNewPages':282,'provinceLocalityHubs':16,
      'localityDirectory':1,'grandTotalHTML':303+len(records),
      'verifiedDeliveryAreas':0,'regionalServiceClaims':False,'uniqueContentProven':False,'regionalShippingEvidenceCount':0,
      'copyReusedAcrossLocalities':True,'faqBasedOnVerifiedLocalityNameAndGeneralPurchaseQuestions':True,
      'indexable':False,'canonical':False,'sitemap':False,'localities':records}
    (OUT/'localities-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('WREATHPRICE_LOWER_OFFICIAL_BUILD_PASS '+json.dumps({k:v for k,v in report.items() if k!='localities'},ensure_ascii=False),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True)
    main(p.parse_args().archive)
