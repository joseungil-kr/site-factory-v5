"""Read-only live seller integrity gate: independent response-derived price and image SHA."""
import hashlib, html, json, re, ssl, sys, urllib.request
from pathlib import Path

CATALOG=Path('sites/wreath-region/products.json')
REPORT=Path('reports/wreath-seller-live.json')

def live_price(markup):
    # Product detail price fields, not a price copied from the local catalogue.
    s=html.unescape(markup)
    patterns=[
        r'<meta[^>]+(?:property|name)=["\'](?:product:price:amount|og:price:amount)["\'][^>]+content=["\']([0-9,]+)',
        r'<meta[^>]+content=["\']([0-9,]+)["\'][^>]+(?:property|name)=["\'](?:product:price:amount|og:price:amount)',
        r'<[^>]+itemprop=["\']price["\'][^>]+content=["\']([0-9,]+)',
        r'<[^>]+(?:id|class)=["\'][^"\']*(?:it_price|item_price|sale_price)[^"\']*["\'][^>]*>\s*(?:<[^>]*>\s*)*([0-9,]+)',
        r'(?:판매가격|판매가|판매\s*가격)\s*(?:</?[^>]+>\s*|[:：]\s*){0,8}([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})\s*원?'
    ]
    for pattern in patterns:
        m=re.search(pattern,s,re.I|re.S)
        if m:
            return int(m.group(1).replace(',',''))
    # Structured JSON-LD Product offers, if supplied by seller.
    for block in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',s,re.I|re.S):
        try: data=json.loads(block)
        except ValueError: continue
        stack=[data]
        while stack:
            v=stack.pop()
            if isinstance(v,list): stack.extend(v)
            elif isinstance(v,dict):
                if 'price' in v and ('priceCurrency' in v or 'availability' in v):
                    try: return int(float(str(v['price']).replace(',','')))
                    except (ValueError,TypeError): pass
                stack.extend(v.values())
    raise ValueError('LIVE_PRICE_NOT_FOUND')

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; WreathSellerLinkQA/2.0)'})
    with urllib.request.urlopen(req,timeout=25,context=ssl.create_default_context()) as response:
        if response.status!=200: raise ValueError('HTTP_'+str(response.status))
        return response.read(),response.headers.get('Content-Type','')

def check(products, getter=fetch):
    rows=[]
    for p in products:
        row={'sku':p['id'],'referencePrice':p['referencePriceKRW'],'expectedImageSHA256':p['imageSHA256']}
        try:
            item,itype=getter(p['orderUrl'])
            if 'html' not in itype.lower(): raise ValueError('ITEM_NOT_HTML')
            text=item.decode('utf-8','replace')
            row['livePrice']=live_price(text)
            row['priceMatches']=row['livePrice']==p['referencePriceKRW']
            row['skuFound']=p['id'] in text
            row['buyControlFound']=bool(re.search('바로구매|구매하기|장바구니',text))
            image,imgtype=getter(p['imageUrl'])
            row['imageSHA256']=hashlib.sha256(image).hexdigest()
            row['imageMatches']=row['imageSHA256']==p['imageSHA256']
            row['jpegValid']=image.startswith(b'\\xff\\xd8\\xff') and ('jpeg' in imgtype.lower() or 'jpg' in imgtype.lower())
            row['passed']=all(row[k] for k in ('priceMatches','skuFound','buyControlFound','imageMatches','jpegValid'))
        except Exception as exc:
            row['passed']=False
            row['error']=type(exc).__name__+': '+str(exc)
        rows.append(row)
    return {'seller':'fwith.co.kr','noOrderSubmitted':True,'rows':rows,'passes':len(rows)==6 and all(x['passed'] for x in rows)}

def main():
    products=json.loads(CATALOG.read_text(encoding='utf-8'))['list']
    result=check(products)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
    print('WREATH_SELLER_LIVE_CHECK='+json.dumps(result,ensure_ascii=False))
    if not result['passes']: sys.exit(1)

if __name__=='__main__':main()
