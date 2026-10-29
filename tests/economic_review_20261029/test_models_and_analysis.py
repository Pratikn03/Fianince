import itertools
import numpy as np
import pandas as pd
import pytest

from studies.economic_review_20261029.models import (
    box_admission, cumulative_drift, finite_peak_envelope, impulse, state_matrix, uniform_tail,
)
from studies.economic_review_20261029.experiments import (
    load_market_csv, market_features, real_data_experiment,
)


@pytest.mark.parametrize("eta", [.005,.1,.5,1.])
def test_drift_matches_independent_resolvent(eta):
    J=state_matrix(.4,1.,[.4],[eta])
    z=np.array([0.,.25])
    exact=(np.linalg.solve(np.eye(2)-J,z)-z)[0]
    assert cumulative_drift(.4,1.,[.4],[eta],0.,[.25]) == pytest.approx(exact)
    assert exact == pytest.approx(.5/eta)


def test_finite_envelope_attained_over_all_short_shock_paths():
    q,eta=np.array([.15,.25]),np.array([.2,.7])
    J=state_matrix(.4,1.,q,eta,.3);b=np.r_[1.,eta]
    H=4;envelope=finite_peak_envelope(.4,1.,q,eta,-.2,.25,.48,H,.3)
    largest=0.
    for mem in itertools.product([-.25,.25],repeat=2):
        for shocks in itertools.product([-.48,.48],repeat=H):
            z=np.r_[-.2,mem];peak=abs(z[0])
            for u in shocks:z=J@z+b*u;peak=max(peak,abs(z[0]))
            largest=max(largest,peak)
    assert largest==pytest.approx(envelope.max())


def test_box_is_safe_and_larger_level_eventually_breaches():
    alpha=box_admission(.4,1.,.4,1.,1.,.48,0.,.25)
    assert alpha==pytest.approx(.3)
    for eta in [.005,.1,1.]:
        p=finite_peak_envelope(.4,1.,[.4],[eta],0.,.25,.48,5000,alpha)
        assert p.max()<=1+1e-12
    assert finite_peak_envelope(.4,1.,[.4],[.5],0.,.25,.48,1000,.35).max()>1


def test_box_inconclusive_is_not_a_false_safe_action():
    assert box_admission(.4,1.,.4,1.,1.,.7,0.,.25) is None
    assert box_admission(.4,1.,.4,1.,1.,.48,0.,1.1) is None
    assert box_admission(.4,1.,0.,1.,1.,.48,0.,.25)==1


@pytest.mark.parametrize("eta", [.2,.3,.9,1.])
def test_uniform_tail_dominates_independent_long_sum(eta):
    h=impulse(.4,1.,[.4],[eta],10000)
    for H in [4,64,256]:assert h[H:].sum()<=uniform_tail(.4,1.,.4,.2,H)+1e-12


@pytest.mark.parametrize("q,eta", [([-.1],[.2]),([.1],[0]),([.1],[1.1]),([.1,.2],[.5])])
def test_invalid_contract_rejected(q,eta):
    with pytest.raises(ValueError):state_matrix(.4,1.,q,eta)


def fixture_market(n=900):
    rng=np.random.default_rng(12)
    return pd.DataFrame(dict(timestamp=pd.date_range('2020-01-01',periods=n,freq='h',tz='UTC'),
                             market='synthetic',price=np.exp(4+np.cumsum(rng.normal(0,.001,n))),
                             signed_flow=rng.normal(size=n)))


def test_features_do_not_use_future_prices():
    frame=fixture_market(300);changed=frame.copy();changed.loc[201:,'price']*=1.1
    first=market_features(frame,60,12);second=market_features(changed,60,12)
    cols=['volatility','finite_response_proxy','margin_proxy']
    np.testing.assert_allclose(first.loc[first.source_row<=200,cols],second.loc[second.source_row<=200,cols])


def test_real_csv_predictive_pipeline_and_bad_timestamps(tmp_path):
    frame=fixture_market();path=tmp_path/'market.csv';frame.to_csv(path,index=False)
    summary,predictions=real_data_experiment(path,np.random.default_rng(3),60,12)
    assert len(summary)==1 and len(predictions)>100
    assert np.isfinite(summary.delta_oos_R2_percentage_points).all()
    assert (predictions.target_end_row-predictions.source_row==12).all()
    frame.loc[1,'timestamp']=frame.loc[0,'timestamp'];frame.to_csv(path,index=False)
    with pytest.raises(ValueError,match='duplicate'):load_market_csv(path)


def test_zero_flow_and_singular_var_are_handled_without_fake_certification(tmp_path):
    frame=fixture_market();frame['signed_flow']=0
    path=tmp_path/'zero.csv';frame.to_csv(path,index=False)
    summary,_=real_data_experiment(path,np.random.default_rng(4),60,12)
    assert 'no structural' in summary.interpretation.iloc[0]
