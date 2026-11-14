"""Deterministic 1% population-vs-full set-Jaccard similarity audit.

Never confuses finite statistical sampling with exhaustive semantic review.
"""
import argparse, hashlib, json, random, re, sys, time
from pathlib import Path


def encode_docs(data):
    grams={}; bits=[];sizes=[];names=[]
    for site,pages in data.items():
        for path,txt in pages.items():
            normalized=re.sub(r'\s+',' ',txt).strip()
            shingles=set(normalized[j:j+5] for j in range(len(normalized)-4))
            pagebytes=bytearray()
            for g in shingles:
                idx=grams.setdefault(g,len(grams))
                b=idx>>3
                if b>=len(pagebytes):pagebytes.extend(b'\x00'*(b+1-len(pagebytes)))
                pagebytes[b]|=1<<(idx&7)
            bits.append(int.from_bytes(pagebytes,'little'))
            sizes.append(len(shingles));names.append(site+path)
    return names,bits,sizes,len(grams)


def run(source:Path, threshold=0.49, sample_rate=0.01):
    data=json.loads(source.read_text(encoding='utf8'))
    names,bits,sizes,ng=encode_docs(data)
    count=len(names);assert count==15102,(count,'regional only')
    rng=random.Random(20261104)
    sample_ids=sorted(rng.sample(range(count),int(count*sample_rate+0.999999)))
    maximum=(-1,None,None)
    fail_count=0
    counts_by_site={}
    max_by_site={}
    comparisons=0
    exemplars=[]
    for i in sample_ids:
        left=bits[i];size=sizes[i]
        for j,right in enumerate(bits):
            if i==j:continue
            common=(left&right).bit_count()
            score=common/(size+sizes[j]-common)
            if score>maximum[0]:maximum=(score,names[i],names[j])
            site=names[i].split('/')[0]
            if score>max_by_site.get(site,(-1,None))[0]: max_by_site[site]=(score,names[j])
            if score>=threshold:
                counts_by_site[site]=counts_by_site.get(site,0)+1
                fail_count+=1
                if len(exemplars)<12:exemplars.append({'from':names[i],'to':names[j],'jaccard':round(score,6)})
            comparisons+=1
    result={'metric':'visible narrative+title+description char 5gram set Jaccard',
       'thresholdExclusive':threshold,'sourceDocuments':count,'sampleFraction':sample_rate,
       'sample':len(sample_ids),'comparisons':comparisons,'vocabulary5gram':ng,
       'maxScore':maximum[0],'maxPair':maximum[1:],
       'violations':fail_count,'violationsByFromSite':counts_by_site,'maximumByFromSite':max_by_site,'failureExamples':exemplars,'pass':fail_count==0}
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();begin=time.time()
    v=run(a.source);v['seconds']=round(time.time()-begin,3)
    a.output.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CLINIC_SIMILARITY_AUDIT',json.dumps(v,ensure_ascii=False))
    if not v['pass']:sys.exit(2)