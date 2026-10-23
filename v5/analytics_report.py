"""Optional privacy-reviewed anonymous aggregate event query for the site dashboard."""
from __future__ import annotations
import json
import os
from urllib.request import Request,urlopen
from .config import read_site,ConfigError


def read_counts(site_id,days=7):
    cfg=read_site(site_id)['site']
    if not cfg.get('analytics',{}).get('enabled') or not cfg.get('cookiePrivacyReviewed'):
        raise ConfigError('Anonymous behavior measurement is not privacy-approved/enabled for this site')
    if not isinstance(days,int) or not 1<=days<=90:
        raise ConfigError('Reporting window must be 1..90 days')
    token=os.getenv('CLOUDFLARE_API_TOKEN')
    account=os.getenv('CLOUDFLARE_ACCOUNT_ID')
    if not token or not account or len(account)!=32:
        raise ConfigError('Missing approved Cloudflare API credentials for aggregate read-only query')
    dataset='v5_'+site_id.replace('-','_')
    # One site per dataset, no identity fields, no visitor IDs, no query strings.
    query=(f'SELECT blob1 AS action, SUM(_sample_interval) AS actions FROM {dataset} '
           f"WHERE timestamp > NOW() - INTERVAL '{days}' DAY "
           'GROUP BY blob1 ORDER BY actions DESC LIMIT 10')
    req=Request(f'https://api.cloudflare.com/client/v4/accounts/{account}/analytics_engine/sql',
        data=query.encode('utf-8'),headers={'Authorization':'Bearer '+token,'Content-Type':'text/plain'},method='POST')
    with urlopen(req,timeout=30) as resp:
        body=resp.read(500_000).decode('utf-8')
    return {'site':site_id,'days':days,'rawAggregates':body,'scope':'anonymous action totals, no conversions confirmed'}
