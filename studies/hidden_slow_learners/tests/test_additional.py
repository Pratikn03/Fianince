from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
from machine_markets.model import Market,recover_kernel
from machine_markets.construction import construct_pair,to_markets
from machine_markets.inference import feedback_bounds,classify,gaussian_certificate,single_rate,matrix_pencil

@pytest.mark.parametrize('K',[1,2,3,4,6,8,12])
def test_exact_matching_arbitrary_configured_order(K):
    nodes=[F(0)] if K==1 else [F(3,4)*F(i,K-1) for i in range(K)]
    p=construct_pair(F(2,5),nodes+[F(99,100)])
    m1,m2=to_markets(p)
    assert abs(m1.impulse(K+1)-m2.impulse(K+1)).max()<2e-12
    assert m1.margin>0>m2.margin
    assert m1.spectral_radius()<1<m2.spectral_radius()

@pytest.mark.parametrize('eta',[.001,.02,.3,1.0])
def test_bound_is_sharp_at_common_floor(eta):
    m=Market(.4,np.array([.2,.3]),np.array([eta,eta]))
    k=m.kernel(30)
    L,U=feedback_bounds(k.sum(),k.sum(),k[-1],30,eta)
    assert U==pytest.approx(.5,abs=2e-12)


def test_agent_loop_kernel_matches_analytic():
    m=Market(.4,np.array([.2,.3]),np.array([.2,.002]))
    assert np.allclose(m.kernel(256),m.loop_open_kernel(256),atol=1e-14)


def test_same_short_shocks_cannot_distinguish_pair():
    p=construct_pair(F(2,5),[F(0),F(1,2),F(19,20)])
    m1,m2=to_markets(p)
    eps=np.random.default_rng(67).normal(size=4)
    assert np.allclose(m1.simulate(eps),m2.simulate(eps),atol=1e-13)


def test_frozen_learning_ablation_is_same_price_dynamics():
    m=Market(.4,np.array([.8,.2]),np.array([.1,.9]))
    assert np.allclose(m.simulate(np.zeros(10),1.0,True),.4**np.arange(11))


def test_boundary_never_receives_strict_label():
    assert classify(.4,.6,.6)=='inconclusive'


def test_zero_noise_certificate_equals_exact_bounds():
    m=Market(.4,np.array([.3]),np.array([.2]))
    k=m.kernel(16)
    out=gaussian_certificate(.4,k.sum(),k[-1],16,0.0,.2)
    assert out['label']=='stable'
    assert out['upper']==pytest.approx(.3)


def test_one_rate_fits_heterogeneous_witness_but_misses_instability():
    m1,m2=to_markets(construct_pair(F(2,5),[F(0),F(1,2),F(19,20)]))
    q1=single_rate(m1.kernel(2));q2=single_rate(m2.kernel(2))
    assert q1==pytest.approx(q2)
    assert .4+q2<1 and m2.margin<0


def test_matrix_pencil_resolves_two_active_modes_with_enough_exact_taps():
    m=Market(.4,np.array([.2,.6]),np.array([.7,.03]))
    assert matrix_pencil(m.kernel(16),0,.001)==pytest.approx(.8,rel=1e-7)


def test_experiment_runner_smoke(tmp_path):
    root=Path(__file__).resolve().parents[1]
    runner=root/'scripts'/'run_experiments.py'
    assert runner.exists(),'experiment runner not implemented'
    completed=subprocess.run([sys.executable,str(runner),'--smoke','--output',str(tmp_path)],capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr
    s=json.loads((tmp_path/'summary.json').read_text())
    assert s['exact']['all_opposite_stability']
    assert s['measurement']['datasets']>0


def test_standalone_rational_verifier_exists():
    root=Path(__file__).resolve().parents[1]
    verifier=root/'scripts'/'verify_exact.py'
    assert verifier.exists(),'standalone verifier not implemented'
    assert 'from machine_markets' not in verifier.read_text()


def test_reused_gaussian_cutoff_is_numerically_identical():
    import machine_markets.inference as inf
    from scipy.stats import norm
    assert hasattr(inf,'gaussian_multiplier'),'cached critical-value helper missing'
    assert inf.gaussian_multiplier(4,.05)==float(norm.ppf(1-.05/16))
    assert inf.gaussian_multiplier(4,.05)==inf.gaussian_multiplier(4,.05)
