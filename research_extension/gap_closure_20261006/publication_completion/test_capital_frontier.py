import numpy as np
import pytest
from capital_frontier import robust_quantity_cap,account,probe_trader_account
from test_resource_frontier import system

def test_actual_fill_mark_changes_zero_initial_exposure():
    J,H,C=system(.5,.8,.2,.4,.1);V=2.;B=10.;cost=.02
    rows=account(J,H,C,[V,0,0,0],B,100.,cost)
    assert np.isclose(rows[0]['equity'],B-.5*.8*V*V-cost*V)
    assert rows[0]['inventory']==-V
    assert min(r['equity'] for r in rows)==rows[0]['equity']

def test_margin_cap_is_attained_and_above_cap_fails():
    J,H,C=system(.5,.8,.2,.4,.1);B=100.;mu=.25;P=100.;cost=.02
    cap=robust_quantity_cap(B,.8,mu,P,cost)
    at=account(J,H,C,[cap],B,P,cost)[0]
    assert np.isclose(at['equity'],mu*abs(at['inventory'])*at['price'])
    above=account(J,H,C,[cap*1.00001],B,P,cost)[0]
    assert above['equity']<mu*abs(above['inventory'])*above['price']

def test_many_probe_paths_obey_robust_margin_and_cash_bound():
    rng=np.random.default_rng(20);B=100.;mu=.25;P=100.;k=.8;c=.02
    cap=robust_quantity_cap(B,k,mu,P,c)
    for d in [0,.01,.1]:
        J,H,C=system(.5,k,.2,.4,d)
        for _ in range(40):
            v=rng.random(80);v*=cap/v.sum()
            rows=account(J,H,C,v,B,P,c)
            for i,r in enumerate(rows):
                total=v[:i+1].sum()
                assert B-r['equity']<=.5*k*total**2+c*total+1e-9
                assert r['equity']>=mu*abs(r['inventory'])*r['price']-1e-9

def test_full_lot_unit_change_preserves_capital_and_margin():
    B=100.;k=.8;mu=.25;P=100.;c=.02;g=100.
    cap=robust_quantity_cap(B,k,mu,P,c)
    changed=robust_quantity_cap(B,g*g*k,mu,g*P,g*c)
    assert np.isclose(changed,cap/g)
    J,H,C=system(.5,k,.2,.4,.1);Jl,Hl,Cl=system(.5,g*g*k,.2/(g*g),.4,.1)
    a=account(J,H,C,[cap*.3,cap*.7,0],B,P,c)
    b=account(Jl,Hl,Cl,[cap*.3/g,cap*.7/g,0],B,g*P,g*c)
    np.testing.assert_allclose([r['equity'] for r in a],[r['equity'] for r in b])
    np.testing.assert_allclose([r['cash'] for r in a],[r['cash'] for r in b])

def test_numerically_stable_root_with_large_reference_price():
    B=1.;k=1e-5;mu=.25;P=1e8
    cap=robust_quantity_cap(B,k,mu,P)
    assert cap>0
    assert np.isclose((.5+mu)*k*cap*cap+mu*P*cap,B)

def test_linear_fixed_exposure_omits_trade_inventory_loss():
    J,H,C=system(.5,.8,.2,.4,0);A=3.
    row=account(J,H,C,[A],10.,100.)[0]
    assert 10-row['equity']>.8*A

def test_invalid_financial_contract_is_rejected():
    for params in [(0,1,.25,100,0),(1,0,.25,100,0),(1,1,0,100,0),(1,1,.25,-100,0),(1,1,.25,100,-1)]:
        with pytest.raises(ValueError):robust_quantity_cap(*params)

def test_passive_process_noise_covariance_changes_without_probes():
    a,k,q,e,d=.5,.8,.2,.4,.1;sw=.02;obs=.003;covariances=[]
    for split in [0,d]:
        J,H,C=system(a,k,q,e,split);G=H/k
        # Independent state recursion maps three process innovations to prices.
        transfer=np.zeros((3,3))
        for col in range(3):
            state=np.zeros(len(G))
            for t in range(3):
                state=J@state+G*(t==col);transfer[t,col]=C@state
        cov=sw*sw*(transfer@transfer.T)+obs*obs*np.eye(3)
        covariances.append(cov)
        b1=a+k*q*e;b2=b1*b1+k*q*e*(1-e)-k*q*split*split
        assert np.isclose(cov[0,2],sw*sw*b2)
        product_variance=cov[0,0]*cov[2,2]+cov[0,2]**2
        assert product_variance>0
        account_path=account(J,H,C,[0,0,0],100.,100.)
        assert all(r['inventory']==0 and r['equity']==100 for r in account_path)
    assert np.isclose(covariances[0][0,2]-covariances[1][0,2],k*q*sw*sw*d*d)
    b=np.sqrt(3)*sw
    assert np.isclose(b**4/5-3*sw**4,-2*b**4/15)

def test_positive_price_response_is_completely_monotone():
    for a in [0.,.2,.5]:
        J,H,C=system(a,.8,.2,.4,.1);z=H.copy();h=[]
        for _ in range(30):h.append(float(C@z));z=J@z
        seq=np.array(h)
        for order in range(5):
            assert ((-1)**order*seq>=-1e-13).all()
            seq=np.diff(seq)

def test_refreshed_half_impact_execution_has_no_roundtrip_gain():
    J,H,C=system(.5,.8,.2,.4,.1);rng=np.random.default_rng(71)
    for _ in range(50):
        v=rng.normal(size=20);v[-1]=-v[:-1].sum();z=np.zeros(len(H));cost=0.
        for trade in v:
            baseline=J@z;fill=100.+C@baseline+.5*(C@H)*trade
            cost+=trade*fill;z=baseline+H*trade
        assert abs(v.sum())<1e-12 and cost>=-1e-9

def test_exact_equity_disclosure_distinguishes_noiseless_pair():
    A=.001;B=100.;k=.8;q=.2;d=.1;marks=[]
    for split in [0,d]:
        J,H,C=system(.5,k,q,.4,split)
        marks.append(account(J,H,C,[A,0,0],B,100.)[-1]['equity'])
    assert marks[1]>marks[0]
    assert np.isclose(marks[1]-marks[0],A*A*k*k*q*d*d,atol=1e-12,rtol=1e-4)

def test_probe_trader_pulse_is_margin_solvent_after_price_reversion():
    J,H,C=system(.5,.8,.2,.4,.1);A=10.;mu=.25;P=100.;cost=.02
    B=.5*.8*A*A+(cost+mu*P)*A
    rows=probe_trader_account(J,H,C,np.r_[A,np.zeros(499)],B,P,cost)
    assert min(r['equity']-mu*abs(r['inventory'])*r['price'] for r in rows)>-1e-9
    assert np.isclose(rows[-1]['equity'],mu*A*P)

def test_trading_cost_equals_toeplitz_and_bounds_energy():
    J,H,C=system(.5,.8,.2,.4,.1);rng=np.random.default_rng(19);v=rng.normal(size=20);h=[];z=H.copy()
    for _ in range(20):h.append(float(C@z));z=J@z
    T=np.array([[h[abs(i-j)] for j in range(20)] for i in range(20)])
    row=probe_trader_account(J,H,C,v,1000.,100.)[-1]
    actual=1000.-row['fundamental_equity'];assert np.isclose(actual,.5*v@T@v)
    r=1-.3*(1-.5-.8*.2);m=.8*(1-r)/(1+r)
    assert actual>=.5*m*(v@v)-1e-9

def test_counterparty_and_probe_trader_conserve_cash_and_inventory():
    J,H,C=system(.5,.8,.2,.4,.1);v=np.array([.1,.2,0,.1]);fee=.02
    dealer=account(J,H,C,v,100.,100.,fee);trader=probe_trader_account(J,H,C,v,100.,100.,fee)
    for i,(a,b) in enumerate(zip(dealer,trader)):
        assert np.isclose(a['inventory']+b['inventory'],0)
        assert np.isclose(a['equity']+b['equity'],200-2*fee*v[:i+1].sum())
