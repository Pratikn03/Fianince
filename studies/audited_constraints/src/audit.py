"""Conditional implementation contracts; not security attestations."""
from __future__ import annotations
import math
import numpy as np


def tail_envelope(q_max:float, eta_floor:float, horizon:int)->float:
    if q_max<0 or not math.isfinite(q_max) or not 0<eta_floor<=1 or horizon<0 or int(horizon)!=horizon:
        raise ValueError('finite Q>=0, 0<eta<=1 and nonnegative integer horizon required')
    if horizon==0:return float(q_max)
    if eta_floor==1:return 0.
    return float(q_max*math.exp(horizon*math.log1p(-eta_floor)))


def norm_tail(b:float,c:float,r:float,horizon:int)->float:
    if min(b,c)<0 or not all(map(math.isfinite,[b,c,r])) or not 0<=r<1 or horizon<0 or int(horizon)!=horizon:
        raise ValueError('finite bounds, contractive r<1, nonnegative horizon required')
    return b*c*(r**horizon)/(1-r)


def make_contract(rates, source_sha256:str)->dict:
    return {'schema':'mm-audit-1','rates':list(map(float,rates)), 'q_total_cap':1.0, 'reset':'zero',
            'other_feedback_channels':[], 'observation':'exact_midprice',
            'update':'memory_next=(1-rate)*memory+rate*old_price',
            'source_sha256':source_sha256,'execution_regime':'unconstrained_linear',
            'scope':'adaptive-memory demand only; excludes account/execution feedback'}


def validate_contract(contract:dict,expected_digest:str)->dict:
    reasons=[];eta=np.asarray(contract.get('rates',[]),dtype=float)
    if eta.ndim!=1 or not len(eta) or not np.isfinite(eta).all() or np.any((eta<=0)|(eta>1)):reasons.append('invalid or missing rates')
    if contract.get('q_total_cap')!=1.0:reasons.append('gain cap not matched to source')
    if contract.get('schema')!='mm-audit-1':reasons.append('schema mismatch')
    if contract.get('reset')!='zero':reasons.append('reset not assured')
    if contract.get('other_feedback_channels')!=[]:reasons.append('unmodeled feedback channels')
    if contract.get('observation')!='exact_midprice':reasons.append('regressor observation error')
    if contract.get('source_sha256')!=expected_digest:reasons.append('source identity mismatch')
    if contract.get('execution_regime')!='unconstrained_linear':reasons.append('nonlinear or binding execution')
    if contract.get('update')!='memory_next=(1-rate)*memory+rate*old_price':reasons.append('update timing mismatch')
    return {'eligible':not reasons,'reasons':reasons,'tail_rate_floor':float(eta.min()) if len(eta) else None,
            'external_attestation':False}
