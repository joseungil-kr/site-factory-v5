"""Planning gate for newly scaffolded sites. Legacy sites remain unaffected."""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from .config import ConfigError, ROOT, validate_site_id

REQUIRED = ("domain","brand","businessModel","serviceScope","pageTypes",
            "targetPageCount","titlePattern","urlPattern","keywordGroups",
            "copyPoolPlan","similarityAudit","conversion","images","publishPolicy")

def initial_spec(site_id,brand,keyword,region,phone):
    return {
        "version":1,"siteId":site_id,"approved":False,
        "domain":None,"brand":brand,"businessModel":None,
        "serviceScope":{"region":region,"granularity":None,"facilities":None},
        "pageTypes":[],"targetPageCount":None,
        "titlePattern":None,"urlPattern":None,
        "keywordGroups":{"primary":[keyword],"secondary":[]},
        "copyPoolPlan":{"industry":None,"source":None,"sentenceTarget":None},
        "similarityAudit":{"metric":"char-5gram-jaccard","thresholdExclusive":0.49,"sampleFraction":0.01,"seed":20261026},
        "conversion":{"phone":phone,"orderUrl":None,"mode":None},
        "images":{"source":None,"approved":False},
        "publishPolicy":{"mode":None,"indexNow":None}
    }

def validate_plan(data, site_id=None):
    errors=[]
    if not isinstance(data,dict):
        raise ConfigError("site-spec.json must be a JSON object")
    for key in REQUIRED:
        value=data.get(key)
        if value is None or value=="" or value==[]:
            errors.append("missing "+key)
    if site_id is not None and data.get("siteId")!=site_id:
        errors.append("siteId mismatch")
    if data.get("approved") is not True:errors.append("plan not approved")
    domain=data.get("domain")
    if isinstance(domain,str):
        p=urlsplit(domain)
        if p.scheme!="https" or not p.hostname or p.path not in ("","/") or p.query or p.fragment:
            errors.append("invalid domain")
    scope=data.get("serviceScope")
    if not isinstance(scope,dict) or not scope.get("region") or not scope.get("granularity"):
        errors.append("serviceScope missing region/granularity")
    if not isinstance(data.get("pageTypes"),list) or not data.get("pageTypes") or not all(isinstance(x,str) and x.strip() for x in data["pageTypes"]):
        errors.append("invalid pageTypes")
    count=data.get("targetPageCount")
    if type(count) is not int or count<1 or count>19970:errors.append("invalid targetPageCount")
    for key in ("titlePattern","urlPattern","businessModel"):
        if not isinstance(data.get(key),str) or len(data[key].strip())<3:errors.append("invalid "+key)
    for key in ("keywordGroups","copyPoolPlan","conversion","images","publishPolicy"):
        if not isinstance(data.get(key),dict) or not data[key]:errors.append("invalid "+key)
    audit=data.get("similarityAudit")
    if not isinstance(audit,dict) or audit.get("metric") not in ("char-5gram-jaccard","char-3gram-cosine"):
        errors.append("invalid similarity metric")
    else:
        t=audit.get("thresholdExclusive");f=audit.get("sampleFraction")
        if not isinstance(t,(float,int)) or not 0<t<1 or not isinstance(f,(float,int)) or not 0<f<=1:
            errors.append("invalid similarity threshold/sample")
    return {"ready":not errors,"errors":errors,"site":data.get("siteId"),"approved":data.get("approved") is True}

def check_site(site_id):
    validate_site_id(site_id)
    path=ROOT/"sites"/site_id/"site-spec.json"
    if not path.exists():
        return {"site":site_id,"ready":True,"errors":[],"legacy":True}
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise ConfigError("Invalid site-spec.json: "+str(exc)) from exc
    return validate_plan(data,site_id)

def require_site_plan(site_id):
    result=check_site(site_id)
    if not result["ready"]:
        raise ConfigError("Site creation preflight failed: "+"; ".join(result["errors"]))
    return result
