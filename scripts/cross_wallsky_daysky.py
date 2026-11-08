"""Re-run the preserved 52-page Wallsky sample against the current Daysky population."""
import json,math,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from v5.skycar_pool import _grams,_jaccard
from v5.config import read_site
from scripts.build_wallsky import pages,REPORT,write
def body(p):
    return ' '.join([p.get('intro','')]+[s.get('paragraph','') for s in p.get('sections',[])])
def main():
    wall=pages();days=read_site('daysky')['pages']
    if len(wall)!=5196 or len(days)!=1736:raise ValueError(f'Unexpected populations: Wallsky {len(wall)}, Daysky {len(days)}')
    samples=random.Random(20261028).sample(range(len(wall)),math.ceil(len(wall)*.01))
    daygrams=[_grams(body(p)) for p in days]
    out=[]
    for i in samples:
        grams=_grams(body(wall[i]))
        score,j=max((_jaccard(grams,g),j) for j,g in enumerate(daygrams))
        out.append({'wallskyPage':wall[i]['number'],'dayskyPage':days[j].get('number'),'maximumSimilarity':round(score,6)})
    maximum=max(x['maximumSimilarity'] for x in out)
    report={'populationWallsky':len(wall),'populationDaysky':len(days),'sampleWallsky':len(samples),
            'seed':20261028,'metric':'whitespace-free char-5gram Jaccard',
            'thresholdExclusive':0.49,'comparisons':len(samples)*len(days),
            'maximum':maximum,'passes':maximum<0.49,'samples':out,
            'limitation':'Seeded 1% Wallsky sample versus all Daysky pages; not all-pairs cross-site proof.'}
    write(REPORT/'cross-daysky.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False))
    raise SystemExit(0 if report['passes'] else 1)
if __name__=='__main__':main()
