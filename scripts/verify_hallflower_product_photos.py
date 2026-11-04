"""Check actual seller product photos, never substitute another SKU image."""
from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib
SKUS=('B200','B203','B205','B212','B214')
OUT=Path('dist/hallflower-preview/photo-verification.json')
def main():
    results=[]
    for sku in SKUS:
        url=f'https://fwith.co.kr/data/item/flower379/{sku}/main_pc.jpg'
        req=Request(url,headers={'User-Agent':'Mozilla/5.0 Hallflower-product-image-QA'})
        with urlopen(req,timeout=25) as response:
            data=response.read(12_000_000)
            kind=response.headers.get('Content-Type','')
            status=response.status
        valid=(data.startswith(bytes.fromhex('ffd8ff')) or data.startswith(bytes.fromhex('89504e470d0a1a0a')) or data.startswith(b'RIFF') and data[8:12]==b'WEBP')
        if status!=200 or not valid: raise RuntimeError(f'Product image invalid {sku}: status={status}, type={kind}')
        results.append({'sku':sku,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'http':status})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('HALLFLOWER_PRODUCT_IMAGE_PASS',len(results))
if __name__=='__main__':main()
