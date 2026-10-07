import numpy as np
from scipy import linalg
from covariance_audit import parameters
from predictive_diagnostics import rows,fit,evaluate

def test_stationary_parameterization_covers_stable_matrix_with_diagonal_above_one():
    J=np.array([[1.1,.8],[-.4,.1]]);Sigma=np.array([[1.,.2],[.2,.7]])
    assert max(abs(np.linalg.eigvals(J)))<1
    G=linalg.solve_discrete_lyapunov(J,Sigma);value,vector=np.linalg.eigh(G)
    sqrt=(vector*np.sqrt(value))@vector.T;inv=(vector/np.sqrt(value))@vector.T
    K=inv@J@sqrt;U,s,Vt=np.linalg.svd(K);assert max(s)<1
    M=(U*(s/np.sqrt(1-s*s)))@Vt;L=np.linalg.cholesky(G)
    p=np.r_[M.ravel(),np.log(L[0,0]),L[1,0],np.log(L[1,1])]
    target,J2,Sigma2,G2=parameters(p)
    np.testing.assert_allclose(J2,J,atol=1e-12);np.testing.assert_allclose(Sigma2,Sigma,atol=1e-12);np.testing.assert_allclose(G2,G,atol=1e-12)
    expected=np.r_[G[0,0],G[0,1],G[1,1],(J@G).ravel(),(J@J@G).ravel()]
    np.testing.assert_allclose(target,expected,atol=1e-12)

def test_parameterized_covariance_satisfies_lyapunov_and_stability_for_signed_nonnormal_cases():
    rng=np.random.default_rng(103)
    for _ in range(30):
        p=rng.normal(size=7)*np.array([2,2,2,2,.5,.5,.5]);target,J,Sigma,G=parameters(p)
        assert max(abs(np.linalg.eigvals(J)))<1 and min(np.linalg.eigvalsh(Sigma))>0
        np.testing.assert_allclose(G-J@G@J.T,Sigma,atol=1e-10)

def test_lag_design_never_bridges_separate_segments():
    chunks=[{'z':np.ones((8,2))*1000},{'z':np.zeros((8,2))}]
    X,Y,groups=rows(chunks,6)
    assert X.shape==(4,12)
    np.testing.assert_array_equal(X[2:],0);np.testing.assert_array_equal(Y[2:],0)
    np.testing.assert_array_equal(groups,[0,0,1,1])

def test_later_date_changes_do_not_change_prior_backtest_folds():
    rng=np.random.default_rng(104);chunks=[]
    for day in range(9):chunks.append({'date':f'2021-01-{day+1:02}','segment':day,'z':rng.normal(size=(80,2))})
    a=evaluate(chunks,['price','flow'],[0],'ema')
    changed=[dict(c,z=c['z'].copy()) for c in chunks];changed[-1]['z']*=1000
    b=evaluate(changed,['price','flow'],[0],'ema')
    # A global/full-data scaler or future fitting would alter these earlier folds.
    early_a=[r for r in a['folds'] if r['test_date']<'2021-01-09'];early_b=[r for r in b['folds'] if r['test_date']<'2021-01-09']
    assert early_a==early_b

def test_var_forecaster_recovers_known_joint_lag_coefficients_in_raw_units():
    rng=np.random.default_rng(105);J=np.array([[.7,.2],[-.1,.4]]);z=np.zeros((20001,2))
    noise=rng.normal(size=(20000,2))
    for t in range(20000):z[t+1]=J@z[t]+noise[t]
    fitted=fit([{'z':z[1000:],'date':'test'}],1,'VAR');scale=fitted['scale'];raw=fitted['B'][1:].T*scale[:,None]/scale[None,:]
    np.testing.assert_allclose(raw,J,atol=.025)
