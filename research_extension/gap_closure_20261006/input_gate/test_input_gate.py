import numpy as np
from scipy.optimize import linprog
from input_gate import response,quantity_gate,worst_envelope


def test_envelope_matches_independent_linear_programs():
    J=np.array([[.6,1.2],[0,.4]]);C=np.array([1.,-.2]);H=np.array([.2,1.]);z=np.array([-.3,.1]);B,k,g=response(J,C,H,z,6);V=.8;fee=.07
    for criterion in ['loss','absolute']:
        predicted=worst_envelope(B,g,V,fee,criterion=criterion)
        for t in range(1,7):
            coefficients=np.array([float(C@np.linalg.matrix_power(J,t-1-j)@H) for j in range(t)])
            objectives=[]
            for sign in ([1,-1] if criterion=='absolute' else [1]):
                cost=np.r_[sign*coefficients+fee,-sign*coefficients+fee]
                opt=linprog(-cost,A_ub=np.ones((1,2*t)),b_ub=[V],bounds=[(0,None)]*(2*t),method='highs')
                assert opt.success;objectives.append(sign*B[t]-opt.fun)
            assert np.isclose(predicted[t],max(objectives))


def test_gate_is_sharp_for_declared_absolute_criterion():
    J=np.array([[.5,2],[0,.3]]);C=[1,0];H=[0,1];z=[.1,.2]
    r=quantity_gate(J,C,H,z,6,4,other_reserve=.2,cost_per_quantity=.1,seconds=60)
    envelope=worst_envelope(r['baseline'],r['prefix_gains'],r['quantity_cap'],.1,.2)
    assert max(envelope)<=4+1e-10 and np.isclose(max(envelope),4)
    assert max(worst_envelope(r['baseline'],r['prefix_gains'],r['quantity_cap']+1e-5,.1,.2))>4
    assert r['quantity_rate_cap']==r['quantity_cap']/60


def test_window_reset_fails_and_carried_state_reduces_second_cap():
    first=quantity_gate([[.9]],[1],[1],[0],1,1)
    assert first['quantity_cap']==1
    actual_after_first=1.;wrong_reset=first['quantity_cap']
    assert .9*actual_after_first+wrong_reset==1.9
    second=quantity_gate([[.9]],[1],[1],[actual_after_first],1,1)
    assert np.isclose(second['quantity_cap'],.1)
    assert .9*actual_after_first+second['quantity_cap']<=1


def test_gate_is_invariant_to_state_coordinate_changes():
    J=np.array([[.5,2],[0,.4]]);C=np.array([.7,-.2]);H=np.array([.1,1.]);z=np.array([.2,-.1]);T=np.array([[2.,1.],[0,.5]]);inv=np.linalg.inv(T)
    a=quantity_gate(J,C,H,z,7,10,cost_per_quantity=.2)
    b=quantity_gate(T@J@inv,C@inv,T@H,T@z,7,10,cost_per_quantity=.2)
    for key in ['baseline','kernel','prefix_gains','quantity_cap']:np.testing.assert_allclose(a[key],b[key],atol=1e-12)


def test_unobserved_components_defeat_price_only_norm_embedding():
    H=np.array([1.,10.]);price=np.array([1.,0.])@H
    assert np.linalg.norm(H)>abs(price)
    r=quantity_gate(np.eye(2),[0,1],H,[0,0],1,1)
    assert r['quantity_cap']==.1 # The relevant monetary output is ten times the price-only proxy.


def test_zero_gain_and_exceeded_background_have_distinct_statuses():
    assert quantity_gate([[.5]],[1],[0],[0],2,1)['status']=='UNBOUNDED_BY_THIS_OUTPUT_CONTRACT'
    bad=quantity_gate([[.5]],[1],[0],[2],2,1)
    assert bad['status']=='BACKGROUND_ALREADY_EXCEEDS_BUDGET' and bad['quantity_cap'] is None
    fees=quantity_gate([[.5]],[1],[0],[0],2,1,cost_per_quantity=.2)
    assert fees['quantity_cap']==5


def test_quantity_unit_conversion_preserves_physical_gate():
    a=quantity_gate([[.7]],[2],[.5],[.1],3,5,cost_per_quantity=.2)
    b=quantity_gate([[.7]],[2],[.05],[.1],3,5,cost_per_quantity=.02)
    assert np.isclose(b['quantity_cap'],10*a['quantity_cap'])


def test_cohort_nonidentification_need_not_change_financial_input_cap():
    import sympy as sp
    a=sp.Rational(1,2);eta=sp.Rational(3,10);total=sp.Rational(1,5)
    # One cohort versus two cohorts sharing a rate and merged total weight.
    one=sp.Matrix([[a,total],[eta*a,1-eta+eta*total]])
    split=sp.Matrix([[a,total/2,total/2],[eta*a,1-eta+eta*total/2,eta*total/2],[eta*a,eta*total/2,1-eta+eta*total/2]])
    H1=sp.Matrix([1,eta]);H2=sp.Matrix([1,eta,eta]);C1=sp.Matrix([[2,0]]);C2=sp.Matrix([[2,0,0]])
    for k in range(8):assert (C1*one**k*H1)[0]==(C2*split**k*H2)[0]
    r1=quantity_gate(np.array(one,float),np.array(C1,float),np.array(H1,float),[0,0],8,5,cost_per_quantity=.05)
    r2=quantity_gate(np.array(split,float),np.array(C2,float),np.array(H2,float),[0,0,0],8,5,cost_per_quantity=.05)
    assert np.isclose(r1['quantity_cap'],r2['quantity_cap'])


def test_positive_cohort_price_peak_and_sustained_gains_have_different_protocols():
    rng=np.random.default_rng(88)
    for K in range(1,6):
        a,kappa=.5,1.;eta=rng.uniform(.15,.9,K);q=rng.uniform(.1,1,K);q=q/q.sum()*.2
        J=np.zeros((K+1,K+1));J[0,0]=a;J[0,1:]=kappa*q
        J[1:,0]=eta*a;J[1:,1:]=np.diag(1-eta)+np.outer(eta,kappa*q)
        H=kappa*np.r_[1.,eta];C=np.r_[2.,np.zeros(K)]
        b,h,g=response(J,C,H,np.zeros(K+1),30)
        assert np.all(h>=0) and np.isclose(max(h),2*kappa)
        S=a+kappa*q.sum();steady=float(C@np.linalg.solve(np.eye(K+1)-J,H))
        assert np.isclose(steady,2*kappa/(1-S))
        # Independent forward simulation with a sustained unit input.
        z=np.zeros(K+1)
        for _ in range(1000):z=J@z+H
        assert np.isclose(float(C@z),steady,rtol=1e-8)


def test_execution_gain_can_rise_while_all_state_amplification_falls():
    def model(k):
        a=1-k;return np.array([[a,k*.1],[.9*a,.1+.09*k]]),k*np.array([1.,.9])
    low,Hlow=model(.1);high,Hhigh=model(1.)
    assert np.linalg.norm(low[:,0])>1 and np.linalg.norm(high,2)<1
    l=quantity_gate(low,[1,0],Hlow,[0,0],10,1);h=quantity_gate(high,[1,0],Hhigh,[0,0],10,1)
    assert np.isclose(l['quantity_cap'],10) and np.isclose(h['quantity_cap'],1)
