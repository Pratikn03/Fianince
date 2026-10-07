from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parents[1]))
from revise_evidence import series,summary,ols
from holdout_reanalysis import quote_ofi


def test_past_bins_do_not_depend_on_future_prices_or_flow():
    n=1000
    frame=pd.DataFrame({'sec':np.arange(n),'mid':np.exp(np.arange(n)*.0001),'flow':np.ones(n)})
    first=series(frame,10,60)
    changed=frame.copy();changed.loc[changed.sec>=800,'mid']*=2;changed.loc[changed.sec>=800,'flow']=900
    second=series(changed,10,60)
    pd.testing.assert_frame_equal(first[first.bin<80],second[second.bin<80])
    assert first.iloc[0].flow==10


def test_missing_bins_split_segments_instead_of_future_fill():
    seconds=np.r_[np.arange(1000),np.arange(1200,2200)]
    frame=pd.DataFrame({'sec':seconds,'mid':np.ones(len(seconds))*10,'flow':np.ones(len(seconds))})
    out=series(frame,10,60)
    assert out.segment.nunique()==2
    assert not out.bin.between(100,119).any()
    assert out.x.eq(0).all()


def test_same_date_segments_are_not_independent_days():
    rows=[dict(date='2021-01-01',n=10,Q=1,S=1,rho=1,Q30=1),
          dict(date='2021-01-01',n=30,Q=3,S=3,rho=3,Q30=3),
          dict(date='2021-01-02',n=40,Q=0,S=0,rho=0,Q30=0)]
    result=summary(rows)
    assert result['n_days']==2 and result['n_segments']==3
    assert result['Q']['mean']==1.25


def test_did_equals_manual_four_cell_difference():
    rng=np.random.default_rng(99)
    treat=np.tile([0,1],100);post=np.repeat([0,1],100)
    y=.5+.2*treat+.3*post+.1*treat*post+rng.normal(size=200)
    X=np.column_stack([np.ones(200),treat,post,treat*post])
    b,se,nu,cov=ols(y,X)
    manual=y[(treat==1)&(post==1)].mean()-y[(treat==1)&(post==0)].mean()-y[(treat==0)&(post==1)].mean()+y[(treat==0)&(post==0)].mean()
    assert abs(b[3]-manual)<1e-12
    assert nu==196 and np.all(se>0)


def test_cluster_covariance_is_invariant_to_group_label_names():
    rng=np.random.default_rng(100)
    X=np.column_stack([np.ones(80),rng.normal(size=80)])
    y=X@np.array([1.,2.])+rng.normal(size=80)
    groups=np.repeat(np.arange(8),10)
    a=ols(y,X,groups);b=ols(y,X,groups+31)
    np.testing.assert_allclose(a[3],b[3]);assert a[2]==7


def test_quote_ofi_chunk_boundaries_equal_one_batch():
    bp=np.array([100.,100.,101.,101.,100.]);ap=np.array([102.,102.,102.,103.,103.])
    bs=np.array([2.,4.,3.,1.,5.]);az=np.array([3.,1.,2.,4.,1.])
    full,_=quote_ofi(bp,bs,ap,az)
    part1,prev=quote_ofi(bp[:2],bs[:2],ap[:2],az[:2])
    part2,_=quote_ofi(bp[2:],bs[2:],ap[2:],az[2:],prev)
    np.testing.assert_array_equal(full,np.r_[part1,part2])
    # At unchanged quotes, net size changes include both sides.
    assert full[1]==4


def test_scalar_KL_bound_covers_finite_windows():
    c=.2
    for T in [1,2,5,50]:
        for s in [1-c/T,1,1+c/T]:
            variance=sum(sum(s**(2*j) for j in range(t-1)) for t in range(1,T+1))
            kl=(c/T)**2/2*variance
            assert kl<=c*c*np.exp(2*c)/4+1e-14


def test_fixed_spectrum_radius_exposes_worst_direction():
    r=json.loads((HERE/'results/transient_checks.json').read_text())
    for cell in r['rows']:
        J=np.array([[.85,cell['theta']],[0,.85]]);C=np.array([[1.,0.]])
        assert np.max(abs(np.linalg.eigvals(J)))==.85
        direction=(C@np.linalg.matrix_power(J,cell['peak_time'])).ravel()/cell['M_C']
        losses=[abs(float((C@np.linalg.matrix_power(J,t)@direction).item())) for t in range(200)]
        assert np.isclose(max(losses)*cell['safe_radius'],1)
        assert max(losses)*(cell['safe_radius']+1e-6)>1


def test_reanalysed_inference_uses_its_actual_covariance():
    d=json.loads((HERE/'results/fee_reanalysis.json').read_text())
    for dep in ['Q','S']:
        for name in ['classical','date_cluster','asset_cluster']:
            r=d[dep][name]
            assert np.isclose(r['p_t'],2*stats.t.sf(abs(r['beta']/r['se']),r['df']))
            half=stats.t.ppf(.975,r['df'])*r['se']
            np.testing.assert_allclose(r['ci95'],[r['beta']-half,r['beta']+half])


def test_repeated_shock_scalar_output_gain_is_attainable():
    # Independent finite-horizon construction with signed, nonnormal dynamics.
    J=np.array([[.6,2.],[-.02,.4]])
    D=np.array([[1.,.2],[.3,1.]])
    C=np.array([[1.,-.7]])
    T=30;radius=.25
    kernels=[C@np.linalg.matrix_power(J,k)@D for k in range(T)]
    gain=sum(np.linalg.norm(k) for k in kernels)
    z=np.zeros(2)
    for t in range(T):
        row=kernels[T-1-t].ravel()
        w=radius*row/np.linalg.norm(row)
        z=J@z+D@w
    assert abs(float((C@z)[0])-radius*gain)<1e-12
    rng=np.random.default_rng(341)
    for _ in range(30):
        z=np.zeros(2)
        for t in range(T):
            w=rng.normal(size=2);w=radius*w/np.linalg.norm(w)
            z=J@z+D@w
        assert abs(float((C@z)[0]))<=radius*gain+1e-12
    # A certified geometric tail contains a much longer independent sum.
    h=next(k for k in range(1,50) if np.linalg.norm(np.linalg.matrix_power(J,k),2)<1)
    q=np.linalg.norm(np.linalg.matrix_power(J,h),2)
    tail=np.linalg.norm(D,2)/(1-q)*sum(np.linalg.norm(C@np.linalg.matrix_power(J,T+j)) for j in range(h))
    longer=sum(np.linalg.norm(C@np.linalg.matrix_power(J,k)@D) for k in range(T,200))
    assert longer<=tail+1e-14
