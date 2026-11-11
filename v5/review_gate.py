"""V5.1 publication review: pinned sample and score tied to the exact inputs."""
from __future__ import annotations
from collections import defaultdict
from math import ceil
import hashlib
import json
import re
from pathlib import Path
from .config import ConfigError


def review_digest(data,plan):
    plan_without_review={k:v for k,v in plan.items() if k!='qualityReview'}
    selected={k:v for k,v in data.items() if k not in ('root','v51Plan')}
    root=Path(__file__).resolve().parents[1]
    paths=['v5/purpose_render.py','v5/markup.py','v5/service_markup.py','v5/engine.py',
           'v5/shared_release.py','v5/review_gate.py','v5/audit.py','v5/config.py',
           'templates/themes/base.css','templates/themes/classic.css','templates/themes/modern.css',
           'templates/themes/minimal.css','templates/service.css']
    site=data.get('site',{})
    library=site.get('imageLibrary',site.get('id',''))
    paths += ['assets/library/'+str(library)+'/'+str(name) for name in site.get('imagePool',[])]
    inputs={path:hashlib.sha256((root/path).read_bytes()).hexdigest() if (root/path).is_file() else None for path in paths}
    raw=json.dumps({'data':selected,'plan':plan_without_review,'rendererFiles':inputs},ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def sample_ids(pages):
    groups=defaultdict(list)
    for page in pages:groups[page.get('purpose','')].append(page['id'])
    chosen=[]
    for purpose,ids in sorted(groups.items()):
        if not purpose:raise ConfigError('review sample requires page purpose')
        ordered=sorted(ids,key=lambda x:hashlib.sha256(('v51-review-v1:'+x).encode()).digest())
        chosen.extend(ordered[:max(1,ceil(len(ordered)*0.01))])
    return sorted(chosen)


def minimum_review_score(data,plan):
    # Explicitly approved Worker6 exception only; all other sites remain 90.
    if data.get('site',{}).get('id') == 'promotion-gift-plants' and plan.get('targetPageCount') == 5302:
        return 85
    return 90


def assert_review(data,plan):
    review=plan.get('qualityReview')
    if not isinstance(review,dict) or review.get('approved') is not True:
        raise ConfigError('V5.1 publication requires an approved 1% quality review')
    if review.get('inputDigest')!=review_digest(data,plan):
        raise ConfigError('V5.1 quality review does not match current inputs')
    if not isinstance(review.get('reviewer'),str) or not review['reviewer'].strip():
        raise ConfigError('V5.1 quality review requires reviewer')
    if not isinstance(review.get('evidence'),str) or not review['evidence'].strip():
        raise ConfigError('V5.1 quality review requires evidence')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(review.get('reviewedOn',''))):
        raise ConfigError('V5.1 quality review requires reviewedOn')
    rows=review.get('samples')
    if not isinstance(rows,list) or not all(isinstance(row,dict) for row in rows):
        raise ConfigError('V5.1 quality review requires sample scores')
    ids=[row.get('id') for row in rows]
    if any(not isinstance(i,str) or not i for i in ids):
        raise ConfigError('V5.1 quality review has invalid sample IDs')
    all_ids={p['id'] for p in data['pages']}
    if len(ids)!=len(set(ids)) or any(i not in all_ids for i in ids):
        raise ConfigError('V5.1 quality review has duplicate or unknown sample IDs')
    if not set(sample_ids(data['pages'])).issubset(set(ids)):
        raise ConfigError('V5.1 quality review must cover the pinned 1% sample')
    threshold=minimum_review_score(data,plan)
    if any(type(row.get('score')) not in (int,float) or not threshold<=row['score']<=100 for row in rows):
        raise ConfigError(f'V5.1 quality review sample scored below {threshold} or is invalid')
