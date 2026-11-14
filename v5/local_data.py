"""Pinned repository-local inputs. No remote fallback or V4 checkout."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def resolve(dataset, root=ROOT):
    root=Path(root).resolve()
    manifest=json.loads((root/'data/local-data-manifest.json').read_text(encoding='utf-8'))
    spec=manifest['datasets'][dataset]
    if spec['status']!='available':
        raise ValueError('Dataset is not approved/available locally: '+dataset)
    path=(root/spec['path']).resolve()
    if root not in path.parents:
        raise ValueError('Dataset path escapes repository')
    raw=path.read_bytes()
    if len(raw)!=spec['bytes'] or hashlib.sha256(raw).hexdigest()!=spec['sha256']:
        raise ValueError('Pinned local dataset mismatch: '+dataset)
    return path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',choices=('official-legal-codes','official-parent-regions','locality-candidates','funeral-halls'))
    a=p.parse_args()
    names=[a.dataset] if a.dataset else ['official-legal-codes','official-parent-regions','locality-candidates']
    print(json.dumps({'verified':{name:str(resolve(name).relative_to(ROOT)) for name in names},
                      'remoteRequests':0,'scope':'listed local inputs only; legacy deployments unchanged'},ensure_ascii=False))

if __name__=='__main__':main()
