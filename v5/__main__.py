"""CLI for local-first generation, audits and dashboards."""
from __future__ import annotations
import argparse
import json
import sys
from .config import ConfigError


def main(argv=None):
    parser=argparse.ArgumentParser(prog='python -m v5')
    cmds=parser.add_subparsers(dest='command',required=True)
    for name in ('build','audit'):
        cmd=cmds.add_parser(name)
        cmd.add_argument('--site',required=True)
        if name=='build':cmd.add_argument('--mode',choices=['preview','home-indexing','public-indexing','publish'],default='preview')
    cmds.add_parser('dashboard')
    planning=cmds.add_parser('plan-check')
    planning.add_argument('--site',required=True)
    metrics=cmds.add_parser('analytics-report')
    metrics.add_argument('--site',required=True)
    metrics.add_argument('--days',type=int,default=7)
    add_page=cmds.add_parser('add-page')
    add_page.add_argument('--site',required=True)
    add_page.add_argument('--json-file',required=True)
    add_page.add_argument('--apply',action='store_true')
    create=cmds.add_parser('scaffold-site')
    create.add_argument('--id',required=True)
    create.add_argument('--brand',required=True)
    create.add_argument('--keyword',required=True)
    create.add_argument('--region',required=True)
    create.add_argument('--phone',required=True)
    create.add_argument('--apply',action='store_true')
    gate=cmds.add_parser('publish-check')
    gate.add_argument('--site',required=True)
    worker=cmds.add_parser('prepare-worker')
    worker.add_argument('--site',required=True)
    staging=cmds.add_parser('prepare-staging')
    staging.add_argument('--site',required=True)
    stage_check=cmds.add_parser('staging-check')
    stage_check.add_argument('--site',required=True)
    stage_check.add_argument('--origin',required=True)
    live=cmds.add_parser('guarded-deploy')
    live.add_argument('--site',required=True)
    public=cmds.add_parser('public-check')
    public.add_argument('--site',required=True)
    indexnow=cmds.add_parser('indexnow')
    indexnow.add_argument('--site',required=True)
    indexnow.add_argument('--key',required=True)
    indexnow.add_argument('--submit',action='store_true')
    update=cmds.add_parser('change-global')
    update.add_argument('--site',required=True)
    update.add_argument('--field',required=True)
    update.add_argument('--value',required=True)
    update.add_argument('--apply',action='store_true')
    add=cmds.add_parser('add-special')
    add.add_argument('--site',required=True)
    add.add_argument('--path',required=True)
    add.add_argument('--title',required=True)
    add.add_argument('--description',required=True)
    add.add_argument('--kind',choices=['content','calculator'],default='content')
    add.add_argument('--placement',choices=['body','footer','both'],default='footer')
    add.add_argument('--apply',action='store_true')
    rollback=cmds.add_parser('restore-snapshot')
    rollback.add_argument('--site',required=True)
    rollback.add_argument('--revision',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='plan-check':
            from .site_plan import check_site
            result=check_site(args.site)
            print(json.dumps(result,ensure_ascii=False,indent=2))
            if not result['ready']:return 3
        elif args.command=='build':
            from .engine import build
            data=build(args.site,mode=args.mode)
            print(json.dumps({'status':'ok','site':args.site,'pages':data['manifest']['pageCount'],'files':data['manifest']['assetFileCount'],'indexable':args.mode in ('publish','public-indexing'),'output':data['output']},ensure_ascii=False,indent=2))
        elif args.command=='audit':
            from .audit import audit
            data=audit(args.site)
            print(json.dumps(data,ensure_ascii=False,indent=2))
            if data['errors']:
                return 1
        elif args.command=='publish-check':
            from .deploy import preflight
            result=preflight(args.site)
            print(json.dumps(result,ensure_ascii=False,indent=2))
            if not result['ready']:return 3
        elif args.command=='guarded-deploy':
            from .cloudflare import guarded_deploy
            print(json.dumps(guarded_deploy(args.site),ensure_ascii=False,indent=2))
        elif args.command=='public-check':
            from .publiccheck import check
            result=check(args.site)
            print(json.dumps(result,ensure_ascii=False,indent=2))
            if result['errors']:return 1
        elif args.command=='indexnow':
            from .indexnow import submission
            print(json.dumps(submission(args.site,args.key,submit=args.submit),ensure_ascii=False,indent=2))
        elif args.command=='prepare-worker':
            from .deploy import write_worker_config
            print(json.dumps({'config':write_worker_config(args.site)},ensure_ascii=False,indent=2))
        elif args.command=='prepare-staging':
            from .staging import write_staging_config,staging_preflight
            conf=write_staging_config(args.site)
            print(json.dumps({'config':conf,'gate':staging_preflight(args.site)},ensure_ascii=False,indent=2))
        elif args.command=='staging-check':
            from .staging import staging_check
            result=staging_check(args.site,args.origin)
            print(json.dumps(result,ensure_ascii=False,indent=2))
            if result['errors']:return 1
        elif args.command=='change-global':
            from .operations import apply_change
            print(json.dumps(apply_change(args.site,'global',field=args.field,value=args.value,apply=args.apply),ensure_ascii=False,indent=2))
        elif args.command=='add-special':
            from .operations import apply_change
            print(json.dumps(apply_change(args.site,'special',path=args.path,title=args.title,description=args.description,kind=args.kind,placement=args.placement,scope='all',apply=args.apply),ensure_ascii=False,indent=2))
        elif args.command=='restore-snapshot':
            from .release import restore_local
            print(json.dumps(restore_local(args.site,args.revision),ensure_ascii=False,indent=2))
        elif args.command=='add-page':
            from .operations import apply_change
            from pathlib import Path
            page=json.loads(Path(args.json_file).read_text(encoding='utf-8'))
            print(json.dumps(apply_change(args.site,'page',page=page,apply=args.apply),ensure_ascii=False,indent=2))
        elif args.command=='scaffold-site':
            from .scaffold import scaffold
            print(json.dumps(scaffold(args.id,args.brand,args.keyword,args.region,args.phone,apply=args.apply),ensure_ascii=False,indent=2))
        elif args.command=='analytics-report':
            from .analytics_report import read_counts
            print(json.dumps(read_counts(args.site,args.days),ensure_ascii=False,indent=2))
        elif args.command=='dashboard':
            from .dashboard import dashboard
            print(json.dumps(dashboard(),ensure_ascii=False,indent=2))
        return 0
    except (ConfigError,ValueError,OSError) as exc:
        print(f'FAIL: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
