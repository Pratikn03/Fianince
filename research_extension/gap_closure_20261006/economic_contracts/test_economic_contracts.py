import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from economic_contracts import robust_spread,gaussian_cost,depth_solution,clearing_matrix,schur_conditions,equity_step,allocation_loss

def test_nonidentification_can_have_zero_ambiguity_price():
    # Arbitrarily different latent decompositions can have identical relevant cost.
    s,markup=robust_spread([gaussian_cost(.3,2.,.4)]*3)
    assert s==.7 and markup==0
    assert robust_spread([.7,.9])[1]>0

def test_capacity_solution_matches_independent_bounded_optimizer_and_infeasibility():
    for A in [.5,2,20]:
        r,h,m,minimum,maximum=3.,2.,.5,.1,4.
        expected=depth_solution(r,h,m,A,minimum,maximum)['quantity']
        numerical=minimize_scalar(lambda L:-(r*L-h*L*L/2),bounds=(minimum,min(maximum,A/m)),method='bounded').x
        assert abs(expected-numerical)<1e-4
    assert depth_solution(3,2,.5,.01,.1,4)['status']=='INFEASIBLE_QUOTING_COMMITMENT'

def test_larger_impact_can_eliminate_transient_amplification_inside_cohort_model():
    low=clearing_matrix(.1,1,.1,.9);high=clearing_matrix(1,1,.1,.9)
    assert max(abs(np.linalg.eigvals(low)))<1 and max(abs(np.linalg.eigvals(high)))<1
    assert np.linalg.norm(low[:,0])>1
    assert np.linalg.norm(high,2)<1
    # At high impact, every power contracts and the t=0 all-state magnification is1.
    assert max(np.linalg.norm(np.linalg.matrix_power(high,t),2) for t in range(50))==1

def test_depth_stability_boundary_matches_independent_eigenvalues():
    rng=np.random.default_rng(69)
    for _ in range(100):
        phi=rng.uniform(.1,3);q=rng.uniform(-2,phi*.99);eta=rng.uniform(.05,.95)
        bound=(4-2*eta)/((2-eta)*phi-eta*q)
        for factor in [.8,1.2]:
            k=factor*bound;conditions=schur_conditions(k,phi,q,eta);stable=max(abs(np.linalg.eigvals(clearing_matrix(k,phi,q,eta))))<1
            assert stable==bool(np.all(conditions>0))
            assert stable==(factor<1)

def test_cash_inventory_ledger_matches_marked_equity_under_buys_and_sells():
    for I in [-3,0,3]:
        for q in [-2,0,2]:
            for P1 in [8,12]:
                r=equity_step(100,I,10,P1,q,.2,.03,.05)
                assert np.isclose(r['pnl'],r['equity_change'])
    r=equity_step(100,3,10,12,0,0)
    assert r['pnl']==6 # A long inventory gains when the price rises.

def test_welfare_triangle_requires_efficient_baseline_and_corrects_existing_markup():
    V0,b,c=20.,2.,3.
    for s0,d in [(c,.7),(c+1,.7)]:
        Vbefore=V0-b*s0;Vafter=V0-b*(s0+d)
        direct=quad(lambda V:(V0-V)/b-c,Vafter,Vbefore)[0]
        assert np.isclose(direct,allocation_loss(b,s0,c,d))
        if s0>c:assert direct>b*d*d/2


def test_signed_feedback_stability_depends_on_execution_timing():
    a,eta,Q=.5,.5,-2.
    immediate=np.array([[a,Q],[eta*a,1-eta+eta*Q]])
    lagged=np.array([[a,1],[eta*Q,1-eta]])
    assert max(abs(np.linalg.eigvals(immediate)))<1
    assert max(abs(np.linalg.eigvals(lagged)))>1


def test_cohort_pole_is_a_closed_loop_transfer_zero_with_correct_timing():
    import sympy as sp
    z=sp.symbols('z');a=sp.Rational(1,2);eta=sp.Rational(1,2);q=sp.Rational(1,5);k=1;r=1-eta
    G=q*eta*z/(z-r);H=sp.cancel(k/(z-a-k*G));num,den=sp.fraction(H)
    assert num.subs(z,r)==0 and den.subs(z,r)!=0
    assert sp.degree(den,z)==2
    # State-space response from the original current-price update agrees exactly.
    J=sp.Matrix([[a,k*q],[eta*a,1-eta+eta*k*q]]);B=sp.Matrix([k,eta*k]);C=sp.Matrix([[1,0]])
    direct=(C*(z*sp.eye(2)-J).inv()*B)[0]
    assert sp.cancel(H-direct)==0


def test_scalar_abstention_kl_matches_full_gaussian_covariance_calculation():
    def covariance(s,T,sigma):
        L=np.array([[s**(i-j) if i>=j else 0 for j in range(T)] for i in range(T)])
        return sigma**2*L@L.T
    c=.2;sigma=1.7
    for T in [2,5,11]:
        s0=1-c/(2*T);s1=s0+c/T
        for a,b in [(s0,s1),(s1,s0)]:
            A=covariance(a,T,sigma);B=covariance(b,T,sigma)
            full=.5*(np.trace(np.linalg.solve(B,A))-T+np.linalg.slogdet(B)[1]-np.linalg.slogdet(A)[1])
            transition=(b-a)**2/(2*sigma**2)*sum(sigma**2*sum(a**(2*j) for j in range(t-1)) for t in range(1,T+1))
            assert np.isclose(full,transition,rtol=1e-8,atol=1e-10)
            assert transition<=c*c*np.exp(2*c)/4
