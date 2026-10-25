"""Check exactly one seeded-random 1% province-stratified sample vs all pages.

No deployment, no page changes and no indexing calls.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Usable as: python scripts/audit_daysky_copy_pool.py [--seed 20261025]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from v5.skycar_pool import QA_SEED, TARGET_SCORE, audit_random_one_percent


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=QA_SEED)
    parser.add_argument("--threshold",type=float,default=TARGET_SCORE)
    parser.add_argument("--report",type=Path,default=Path("reports/daysky/pool-random-1pct-qa.json"))
    options=parser.parse_args(argv)
    if not 0.0<options.threshold<1.0:
        parser.error("threshold must be between 0 and 1")
    result=audit_random_one_percent(options.seed,options.threshold)
    options.report.parent.mkdir(parents=True,exist_ok=True)
    options.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={k:v for k,v in result.items() if k not in ("samples","limitations")}
    print("DAYSKY_POOL_SAMPLE_QA="+json.dumps(summary,ensure_ascii=False))
    print("Saved report: "+str(options.report))
    return 0 if result["passesSample"] else 2


if __name__=="__main__":
    raise SystemExit(main())
