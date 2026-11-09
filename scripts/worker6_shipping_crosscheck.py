"""Conservative seller surcharge lookup against candidate localities. Never infer coverage."""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def run():
 raw=json.loads((ROOT/'sites/promotion-gift-plants/seller-shipping-raw-rows.json').read_text(encoding='utf-8'))
 source=json.loads((ROOT/'data/regions/nationwide_locality_candidates_5034.json').read_text(encoding='utf-8'))
 # Seller's historical/marketing province names are not automatically official.
 aliases={'강원':'강원도','경기':'경기도','경남':'경상남도','경북':'경상북도',
          '대구':'대구광역시','울산':'울산광역시','인천':'인천광역시',
          '전북':'전라북도','제주':'제주특별자치도','충남':'충청남도','충북':'충청북도'}
 provinces={r[0] for r in source['records']}
 district_index={(r[0],r[1]) for r in source['records']}
 locality_index={(r[0],r[1],r[2]) for r in source['records']}
 locality_flags={(r[0],r[1],r[2]):r[3] for r in source['records']}
 matched=[];unknown=[];ambiguous=[]
 for row in raw['rows']:
  label=row['provinceLabel']
  province=aliases.get(label)
  if not province or province not in provinces:
   unknown.append({'row':row['row'],'reason':'province-label-unmatched','sourceProvince':label})
   continue
  districts=[x.strip() for x in row['districtText'].split(',')]
  localities=[] if row['localityText']=='-' else [x.strip() for x in row['localityText'].split(',')]
  if row['districtText']=='전체':
   unknown.append({'row':row['row'],'reason':'province-wide-scope-not-mapped-to-localities'})
   continue
  for district in districts:
   if (province,district) not in district_index:
    unknown.append({'row':row['row'],'reason':'district-not-in-candidate-source','district':province+' '+district})
    continue
   if not localities:
    # A district-wide table row does not prove every locality is serviced.
    matched.append({'row':row['row'],'region':province+' '+district,'scope':'district-display-only','extraKRW':row['extraKRW'],'deliveryConfirmed':False,'candidateParentFlag':None,'officialAddressValidated':False})
   else:
    for locality in localities:
     if (province,district,locality) in locality_index:
      matched.append({'row':row['row'],'region':province+' '+district+' '+locality,'scope':'exact-locality-name-match','extraKRW':row['extraKRW'],'deliveryConfirmed':False,'candidateParentFlag':locality_flags[(province,district,locality)],'officialAddressValidated':False})
     else:
      unknown.append({'row':row['row'],'reason':'locality-not-in-candidate-source','region':province+' '+district+' '+locality})
 # Conflicting district and locality entries remain unresolved rather than
 # applying a guessed specificity/priority rule.
 for m in matched:
  if m['scope']=='exact-locality-name-match':
   parents=[x for x in matched if x['scope']=='district-display-only' and m['region'].startswith(x['region']+' ')]
   if parents:ambiguous.append({'region':m['region'],'localityRow':m['row'],'parentRows':[x['row'] for x in parents]})
 out={'sourceUrl':raw['sourceUrl'],'checkedAt':raw['checkedAt'],'sourceRows':len(raw['rows']),
      'candidateLocalities':len(source['records']),'matchedReferences':matched,'unknown':unknown,
      'overlaps':ambiguous,'unmatchedCandidateStatus':'unknown; absence from surcharge table is not free delivery',
      'finalPriceConfirmed':False,'deliveryCoverageConfirmed':False,
      'candidateFlagZeroMeaning':'parent match unverified, not proof of nonexistent locality',
      'provinceAliasMeaning':'text normalization only, not authoritative jurisdiction validation',
      'counts':{'matchedReferences':len(matched),'unknown':len(unknown),'overlaps':len(ambiguous)}}
 return out
if __name__=='__main__':
 out=run()
 target=ROOT/'reports/promotion-gift-plants/shipping'
 target.mkdir(parents=True,exist_ok=True)
 (target/'seller-surcharge-crosscheck.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out['counts'],ensure_ascii=False))
