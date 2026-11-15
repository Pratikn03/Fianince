"""Offline proof counterexamples, regression checks, and immutable registration checks."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import zipfile

import mpmath as mp
import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

HERE = Path(__file__).resolve().parent.parent

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

candidate = module(HERE/'candidate_p1f_executor.py', 'candidate')
registered = module(HERE/'source/ceiling_suite/p1_empirics/p1f_executor_A1.py', 'registered')
hp = module(HERE/'validation/high_precision_information.py', 'hp')

@pytest.mark.parametrize('name', ['P1F_forecast_irrelevance_spec.md', 'P1F_amendment_A1.md', 'p1f_executor_A1.py', 'P1F_A1_Colab.ipynb'])
def test_registered_hash_unchanged(name):
    root = HERE/'source/ceiling_suite/p1_empirics'
    record = json.loads((root/'P1F_A1_spec.json').read_text())
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == record['sha256'][name]

def test_replacement_unlock_unopened():
    obj = json.loads((HERE/'source/ceiling_suite/p1_empirics/P1F_A1_unlocks.json').read_text())
    assert obj['opens'] == 0

@pytest.mark.parametrize('k', [2, 3])
@pytest.mark.parametrize('delta', ['.2', '.02', '.002'])
def test_moment_cancellation_and_taylor_bound(k, delta):
    with mp.workdps(70):
        x, w, y, v = hp.pair(k)
        assert all(a > 0 for a in w+v)
        for j in range(2*k-1):
            assert abs(sum(a*z**j for a,z in zip(w,x))-sum(a*z**j for a,z in zip(v,y))) < mp.mpf('1e-60')
        d = mp.mpf(delta); h = mp.mpf('1.2'); W = mp.mpf('.2')
        fa = W*sum(a*mp.exp(h*(mp.mpf('.5')+d*z)) for a,z in zip(w,x))
        fb = W*sum(a*mp.exp(h*(mp.mpf('.5')+d*z)) for a,z in zip(v,y))
        envelope = h**(2*k-1)*mp.exp(h*(mp.mpf('.5')+d))
        bound = 2*W*envelope*d**(2*k-1)/mp.factorial(2*k-1)
        assert 0 < abs(fa-fb) <= bound

def test_smoothness_does_not_imply_identification():
    # A parameter-independent rule has identical fixed-mass aggregate responses.
    histories = np.linspace(-2, 2, 50)
    assert np.array_equal(.2*np.tanh(histories), (.05+.15)*np.tanh(histories))

@pytest.mark.parametrize('delta', [.05, .02, .001])
def test_targeted_decision_differs_common_action_succeeds(delta):
    r0 = .5+delta*np.array([-1/np.sqrt(3), 1/np.sqrt(3)])
    r1 = .5+delta*np.array([-1, 1/3])
    q0 = np.array([.1,.1])/(1-r0); q1 = np.array([.05,.15])/(1-r1)
    assert .3+.5*q0.sum() < 1 and .3+.5*q1.sum() < 1
    assert .3+.5*(q0.sum()-q0.max()) > .375
    assert .3+.5*(q1.sum()-q1.max()) < .375
    assert .3+.5*q0.sum()/3 < .375 and .3+.5*q1.sum()/3 < .375

@pytest.mark.parametrize('distance', [.01, .2, 1.0, 3.0])
def test_decision_loss_gaussian_example(distance):
    risk = norm.cdf(-distance/2)
    tv = 2*norm.cdf(distance/2)-1
    kl = distance**2/2
    assert abs(risk-(1-tv)/2) < 1e-14
    assert risk+1e-14 >= max(0, (1-np.sqrt(kl/2))/2)
    assert risk <= .5*np.exp(-distance**2/8)+1e-14

def test_unknown_initial_state_remains_in_finite_history():
    rng = np.random.default_rng(3)
    r = .9; x = rng.normal(size=12); u,v = 3.,0.
    for i, xt in enumerate(x, 1):
        u = r*u+(1-r)*xt; v = r*v+(1-r)*xt
        assert abs((u-v)-3*r**i) < 1e-13
    assert abs(u-v) > .8

def test_noisy_price_signal_counterexample():
    rho, ve, vf = .8, 1., 2.
    p = 1.
    for _ in range(300):
        prior = rho*rho*p+ve
        p = vf*prior/(prior+vf)
    assert p > 0 and rho*rho*p > .5
    assert rho*rho*p+ve+vf > ve+vf

def test_extra_tag_has_positive_precision_value():
    assert (2.+2.)/4 == 1. < 2.

def arrays(T=720, S=2):
    rng = np.random.default_rng(53)
    return (rng.normal(size=(T,S)), rng.normal(size=(T,S)), rng.normal(size=(T,S)), rng.normal(size=(T,S,3)))

def capture_fit(monkeypatch, func):
    fits = []
    original = np.linalg.lstsq
    def record(x, y, *args, **kw):
        fits.append((x.copy(), y.copy()))
        return original(x, y, *args, **kw)
    with monkeypatch.context() as m:
        m.setattr(np.linalg, 'lstsq', record)
        func()
    return fits

def test_a2_training_is_unchanged_by_future_returns(monkeypatch):
    data = arrays(); b = 360
    altered = [x.copy() for x in data]; altered[0][b:] += 1000
    def fit(ex, values):
        return capture_fit(monkeypatch, lambda: ex.evaluate(*values, .005, b, 719, boot=30))
    original = fit(candidate, data); changed = fit(candidate, altered)
    for (x,y),(xx,yy) in zip(original,changed):
        np.testing.assert_allclose(x,xx); np.testing.assert_allclose(y,yy)
    old, leaked = fit(registered, data), fit(registered, altered)
    assert not np.allclose(old[0][1], leaked[0][1])  # reproduces the registered defect

def test_a1_purges_all_eight_forward_labels(monkeypatch):
    data = arrays(); b=360
    altered = [x.copy() for x in data]; altered[3][b:] += 1000
    f = lambda ex, values: capture_fit(monkeypatch, lambda: ex.a1(*values,b,719))
    for (_,y),(_,yy) in zip(f(candidate,data),f(candidate,altered)):
        np.testing.assert_allclose(y,yy)
    assert not np.allclose(f(registered,data)[0][1],f(registered,altered)[0][1])

def test_partial_final_day_is_scored_and_counted():
    result = candidate.evaluate(*arrays(T=2880), .005, 1440, 2879, boot=30)
    assert result['n_scored_days'] == 30
    assert result['n_test_rows'] == 1439*2
    assert result['n_train_rows'] == (1439-96)*2

@pytest.mark.parametrize('vr,vy,gain', [(1,1,.01),(.2,1,.01),(.05,2,.01)])
def test_incremental_injection_algebra(vr,vy,gain):
    c = candidate.injection_coefficient(vr,vy,gain)
    achieved = vr*c*c/(1+c*c)/vy
    assert abs(achieved-gain) < 1e-14

def test_infeasible_injection_is_rejected():
    with pytest.raises(ValueError): candidate.injection_coefficient(.01,1,.02)

def test_power_gate_cannot_read_test_half(monkeypatch):
    data=arrays(T=1200); altered=[z.copy() for z in data]
    for z in altered: z[720:] += 10000
    f=lambda d:capture_fit(monkeypatch,lambda:candidate.power_gate(*d,720,np.random.default_rng(2),draws=1))
    left,right=f(data),f(altered)
    for (x,y),(xx,yy) in zip(left,right):
        np.testing.assert_allclose(x,xx); np.testing.assert_allclose(y,yy)

def test_candidate_live_run_disabled(tmp_path):
    with pytest.raises(SystemExit, match='live execution disabled'):
        candidate.run_all(tmp_path)

def test_checksum_failure_is_rejected(monkeypatch):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z: z.writestr('x.csv','a,b\n1,2\n')
    monkeypatch.setattr(candidate,'FETCH',lambda u:b'0'*64+b' x.zip' if u.endswith('CHECKSUM') else buf.getvalue())
    with pytest.raises(RuntimeError, match='checksum mismatch'): candidate.get_zip_csv('offline.zip')

@pytest.mark.parametrize('header',[True,False])
def test_kline_layouts(header):
    frame=pd.DataFrame([[1645920000000,1,1,1,1,1,1645920299999,1,1,.5,.5,0]],columns=candidate.KLINE_COLS)
    parsed=candidate.read_klines(frame.to_csv(index=False,header=header))
    assert len(parsed)==1 and float(parsed['close'].iloc[0])==1

def test_metrics_at_bar_end_not_used(monkeypatch):
    monkeypatch.setattr(candidate,'NDAYS',1)
    start=pd.Timestamp(candidate.WINDOW_START,tz='UTC')
    metrics=pd.DataFrame({'create_time':[start+pd.Timedelta(minutes=30)],'sum_open_interest':[5.],
                         **{c:[1.] for c in candidate.CLASSES}})
    out=candidate.to_bars(pd.DataFrame(columns=candidate.KLINE_COLS),metrics)
    assert np.isnan(out['sum_open_interest'].iloc[0])
    assert out['sum_open_interest'].iloc[1]==5
    five=candidate.to_bars(pd.DataFrame(columns=candidate.KLINE_COLS),metrics,bar='5min')
    assert len(five)==288 and five['sum_open_interest'].iloc[6]==5

def test_secondary_and_dependence_outputs_present():
    source=(HERE/'candidate_p1f_executor.py').read_text()
    assert 'A2_5minute' in source and 'A2_block_sensitivity' in source
    for length in (1,3,5):
        result=candidate.evaluate(*arrays(),.005,360,719,boot=20,block_days=length)
        assert result['block_days']==length and np.isfinite(result['dR2'])
