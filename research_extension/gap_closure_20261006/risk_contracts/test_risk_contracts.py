import numpy as np
from scipy import stats
from risk_contracts import power_peak_with_tail,market_jacobian,metric_contract,gaussian_input_radius,pnl_contract

def test_signed_target_output_magnification_is_monotone_with_coupling():
    A=np.array([[.6,.4],[-.1,.5]]);B=np.array([[.4,-.3],[.1,.6]]);L=np.array([[1,-2],[-.5,.3]]);C=np.array([[0,0,1,-.7],[0,0,-.2,1.1]])
    previous=np.zeros(80)
    for theta in [0,.2,.5,1,2]:
        J=np.block([[A,np.zeros((2,2))],[theta*L,B]])
        values=np.array([np.linalg.norm(C@np.linalg.matrix_power(J,t),2) for t in range(80)])
        assert np.all(values>=previous-1e-12);previous=values

def test_hedged_output_counterexample_has_certified_infinite_horizon_peak():
    rho=.85;C=np.array([[1.,0.,-1.]])
    uncoupled=power_peak_with_tail(np.array([[rho,2,0],[0,rho,0],[0,0,rho]]),C)
    hedged=power_peak_with_tail(np.array([[rho,2,0],[0,rho,0],[0,2,rho]]),C)
    assert uncoupled['M_C']>5 and np.isclose(hedged['M_C'],np.sqrt(2))
    assert hedged['safe_radius_B1']>uncoupled['safe_radius_B1']
    assert hedged['tail_upper']<hedged['M_C']

def test_original_structural_market_family_keeps_diagonal_spectrum():
    expected=sorted(np.linalg.eigvals(market_jacobian(0)))
    for theta in [0,2,4,8,16]:
        J=market_jacobian(theta);np.testing.assert_allclose(sorted(np.linalg.eigvals(J)),expected,atol=1e-6)
        # Unit leader-memory shock generates theta*q at target price in one step.
        assert np.isclose(J[2,1],theta*.2)
    assert power_peak_with_tail(market_jacobian(16),np.array([[0.,0.,1.,0.]]))['M_C']>4

def test_arbitrarily_varying_declared_metric_perturbations_obey_recursive_bound():
    J=np.array([[.6,.15],[0,.5]]);C=np.array([[1.,0.]]);D=np.eye(2);contract=metric_contract(J,C,D,.05)
    rng=np.random.default_rng(1004);r=.1;z=np.array([.2,-.1]);r0=np.linalg.norm(contract['sqrt']@z)
    for t in range(1,101):
        U,_,V=np.linalg.svd(rng.normal(size=(2,2)));E=contract['inverse']@(.05*U@V)@contract['sqrt']
        w=rng.normal(size=2);w=r*w/np.linalg.norm(w)
        z=(J+E)@z+D@w
        bound=contract['q']**t*r0+contract['d']*r*(1-contract['q']**t)/(1-contract['q'])
        assert np.linalg.norm(contract['sqrt']@z)<=bound+1e-12
        assert abs((C@z)[0])<=contract['c']*bound+1e-12

def test_individual_spectral_stability_does_not_control_switching_products():
    A=np.array([[.5,2],[0,.5]]);B=np.array([[.5,0],[2,.5]])
    assert max(abs(np.linalg.eigvals(A)))==.5 and max(abs(np.linalg.eigvals(B)))==.5
    assert max(abs(np.linalg.eigvals(B@A)))>4

def test_finite_gaussian_radius_uses_exact_marginal_tail_and_union_bound():
    sigma=.01;m=2;H=100;alpha=.05;r=gaussian_input_radius(sigma,m,H,alpha)
    assert np.isclose(H*stats.chi2.sf((r/sigma)**2,m),alpha)

def test_signed_portfolio_nonlinear_mark_remainder_bounds_actual_error():
    rng=np.random.default_rng(1005);h=np.array([10,-3,5]);p=np.array([100,200,50]);limits=np.array([100,50,200])
    for _ in range(100):
        b=rng.uniform(-1,1,size=3)*limits;out=pnl_contract(h,p,b,limits)
        assert out['absolute_approximation_error']<=out['remainder_bound_dollars']+1e-12
    # Zero pricing error alone does not bound a short's fundamental mark loss.
    price=100*np.exp(np.arange(6)*np.log(2));loss=price-100
    assert loss[-1]>3000


def test_zero_input_operator_has_no_repeated_input_loss_channel():
    J=np.eye(2)*.5;C=np.array([[1.,0.]])
    contract=metric_contract(J,C,np.zeros((2,2)),.01)
    assert contract['d']==0 and np.isinf(contract['radius_B1_repeated_input'])


def test_bounded_nonlinear_remainder_preserves_declared_region():
    J=np.array([[.6,.15],[0,.5]]);C=np.array([[1.,0.]]);D=np.eye(2);contract=metric_contract(J,C,D,.05)
    ell=.03;q=contract['q']+ell;r=.08;z=np.array([.3,-.2]);r0=np.linalg.norm(contract['sqrt']@z)
    R=max(r0,contract['d']*r/(1-q));rng=np.random.default_rng(1006)
    for t in range(1,101):
        U,_,V=np.linalg.svd(rng.normal(size=(2,2)));E=contract['inverse']@(.05*U@V)@contract['sqrt']
        remainder=ell*contract['inverse']@np.tanh(contract['sqrt']@z)
        assert np.linalg.norm(contract['sqrt']@remainder)<=ell*np.linalg.norm(contract['sqrt']@z)+1e-12
        w=rng.normal(size=2);w=r*w/np.linalg.norm(w)
        z=(J+E)@z+D@w+remainder
        bound=q**t*r0+contract['d']*r*(1-q**t)/(1-q)
        assert np.linalg.norm(contract['sqrt']@z)<=min(R,bound)+1e-12


def test_finite_contract_handles_unit_root_and_expanding_components():
    from risk_contracts import finite_metric_bound
    for q in [1.,1.05]:
        values=finite_metric_bound(.2,1,.01,q,50);z=.2
        for t in range(1,51):
            z=q*z+.01
            assert np.isclose(z,values[t])
    np.testing.assert_allclose(finite_metric_bound(.2,1,.01,1,50),.2+.01*np.arange(51))


def test_finite_contract_accounts_for_bounded_affine_model_residual():
    from risk_contracts import finite_metric_bound
    values=finite_metric_bound(.2,1,.01,1,50,offset=.005)
    np.testing.assert_allclose(values,.2+.015*np.arange(51))


def test_hedged_exact_certificate_matches_closed_form_infinite_peak():
    import json
    from fractions import Fraction
    from pathlib import Path
    data=json.loads((Path(__file__).resolve().parent/'exact_tail_certificates.json').read_text())
    rho=Fraction(17,20)
    # For t>=6 both rho^t and t*rho^(t-1) decrease, so only0..6 matter.
    assert rho*7<6
    for r in data['families']['hedged_portfolio']:
        theta=Fraction(r['theta']);squares=[2*rho**(2*t)+(2-theta)**2*t*t*rho**(2*t-2) for t in range(7)]
        certified=Fraction(int(r['peak_squared']['numerator']),int(r['peak_squared']['denominator']))
        assert max(squares)==certified
        block=Fraction(int(r['block_frobenius_squared']['numerator']),int(r['block_frobenius_squared']['denominator']))
        tail=Fraction(int(r['tail_squared']['numerator']),int(r['tail_squared']['denominator']))
        assert block<1 and tail<certified


def test_only_marginal_moments_allow_near_sharp_disjoint_rare_shocks():
    from fractions import Fraction
    from risk_contracts import moment_input_radius
    H=10;alpha=Fraction(1,20);amplitude_squared=Fraction(201)
    # Each disjoint event has probability1/201 and a random sign; each marginal second moment is1.
    event_probability=1/amplitude_squared
    assert event_probability*amplitude_squared==1
    failure_probability=H*event_probability
    assert failure_probability<alpha and float(failure_probability)>float(alpha)*.99
    radius=moment_input_radius(np.ones(H),float(alpha))
    assert radius**2< float(amplitude_squared)
    # A slightly smaller proposed radius can fail the confidence requirement.
    larger_failure=Fraction(H,199)
    assert larger_failure>alpha


def test_symmetric_positive_impact_family_has_fixed_spectrum_and_growing_response():
    from risk_contracts import symmetric_market_jacobian
    base,_,_=symmetric_market_jacobian(1)
    for theta in [1,2,4,8,16]:
        J,K,Q=symmetric_market_jacobian(theta)
        np.testing.assert_allclose(K,K.T);assert min(np.linalg.eigvalsh(K))>0
        S=np.diag([1,1,theta,theta]);np.testing.assert_allclose(J,S@base@np.linalg.inv(S),atol=1e-12)
        np.testing.assert_allclose(np.sort_complex(np.linalg.eigvals(J)),np.sort_complex(np.linalg.eigvals(base)),atol=1e-10)
        assert np.isclose(J[2,1],theta/10)
    assert max(abs(np.linalg.eigvals(base)))<1
