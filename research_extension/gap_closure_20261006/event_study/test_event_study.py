import numpy as np
import pandas as pd
from scipy import stats,linalg
from monthly_event_study import design,covariance,analyze

def panel(seed=701):
    rng=np.random.default_rng(seed);rows=[]
    assets=['BTCUSDT','A','B','C','D','E','F','G']
    for month in range(1,13):
        for day in [10,24]:
            for j,asset in enumerate(assets):
                effect=(month-6)*.01 if asset=='BTCUSDT' else 0
                rows.append({'date':f'2022-{month:02}-{day:02}','symbol':asset,'Q':j*.03+effect+rng.normal(scale=.01)})
    return pd.DataFrame(rows)

def test_monthly_FE_coefficients_equal_direct_monthly_gap_contrasts():
    d=analyze(panel(),'Q')
    assert d['design_rank']==42 and d['n']==192 and d['reference']==6
    assert d['manual_point_max_error']<1e-12
    for r in d['contrasts']:assert r['event_month']==int(r['period'])-7

def test_classical_covariance_matches_independent_QR_solution():
    f,X,names,event,ref=design(panel());y=f.Q.to_numpy();b,cov,df,e=covariance(y,X)
    Q,R=np.linalg.qr(X,mode='reduced');b2=linalg.solve_triangular(R,Q.T@y)
    error=y-X@b2;inverse=linalg.solve_triangular(R,np.eye(len(R)))
    cov2=error@error/df*(inverse@inverse.T)
    np.testing.assert_allclose(b,b2,atol=1e-12);np.testing.assert_allclose(cov,cov2,atol=1e-12)

def test_cluster_covariance_and_reference_do_not_depend_on_group_label_names():
    f,X,names,event,ref=design(panel());y=f.Q.to_numpy();a=covariance(y,X,f.date.to_numpy());labels=pd.factorize(f.date)[0];b=covariance(y,X,labels)
    np.testing.assert_allclose(a[1],b[1]);assert a[2]==b[2]==23

def test_date_saturated_cluster_precision_is_flagged_instead_of_reported_as_valid():
    r=analyze(panel(),'Q','date')
    d=r['fits']['date_cluster']['pretrend_joint_test']
    assert r['design_rank']==54 and d['F'] is None and d['p_F'] is None and d['rank']==0
    assert all(v['references']['date_cluster']['status']=='DEGENERATE_REFERENCE' for v in r['contrasts'])

def test_monthly_cluster_saturation_is_flagged_and_F_reference_uses_declared_df():
    r=analyze(panel(),'Q')
    assert r['fits']['month_cluster']['pretrend_joint_test']['rank']==0
    classical=r['fits']['classical'];indices=[i for i,name in enumerate(r['design_columns']) if name in ['treated_period:'+str(k) for k in range(1,6)]]
    coef=np.array(classical['coefficients'])[indices];V=np.array(classical['covariance'])[np.ix_(indices,indices)]
    F=coef@np.linalg.solve(V,coef)/5;test=classical['pretrend_joint_test']
    assert np.isclose(F,test['F']) and test['df_denominator']==150
    assert np.isclose(test['p_F'],stats.f.sf(F,5,150))


def test_date_cluster_covariance_matches_independent_QR_influence_construction():
    f,X,names,event,ref=design(panel());y=f.Q.to_numpy();b,cov,df,e=covariance(y,X,f.date.to_numpy())
    Q,R=np.linalg.qr(X,mode='reduced');influence=linalg.solve_triangular(R,Q.T)
    residual=y-X@linalg.solve_triangular(R,Q.T@y);labels=sorted(f.date.unique());scores=[]
    for label in labels:
        selected=(f.date==label).to_numpy();scores.append(influence[:,selected]@residual[selected])
    scores=np.array(scores);n,k=X.shape
    independently=(scores.T@scores)*len(labels)/(len(labels)-1)*(n-1)/(n-k)
    np.testing.assert_allclose(cov,independently,atol=1e-12)


def test_HC3_is_reported_unavailable_when_treated_dates_have_unit_leverage():
    result=analyze(panel(),'Q','date')
    assert result['fits']['HC3']['status']=='UNAVAILABLE_HIGH_LEVERAGE'
    assert result['fits']['HC3']['pretrend_joint_test']['p_F'] is None
    assert all(r['references']['HC3']['se'] is None for r in result['contrasts'])
