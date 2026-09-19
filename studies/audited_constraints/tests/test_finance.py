import numpy as np
from src.finance import feasible_orders, settle, market_panel

def test_credit_and_inventory_bind():
    order,forced,default=feasible_orders(np.array([100.]),np.array([0.]),np.array([100.]),np.array([10.]),np.array([100.]),1.,1.,0.,.01)
    assert 0<order[0]<1 and not default[0]
    assert 100-order[0]*100.01>=-1e-9

def test_forced_margin_reduction():
    order,forced,default=feasible_orders(np.array([-150.]),np.array([2.]),np.array([100.]),np.array([1.]),np.array([50.]),2.,100.,10.,.01)
    assert forced[0] and order[0]<0

def test_settlement_conserves():
    c=np.array([[100.,100.,1000.]]);i=np.zeros_like(c);o=np.array([[1.,-.5]])
    c2,i2=settle(c,i,o,np.array([100.]),.01)
    assert abs(c2.sum()-c.sum())<1e-10
    assert abs(i2.sum())<1e-10
    assert c2[0,-1]>1000

def test_financial_run_nonvacuous():
    r=market_panel(gain=1.3,slow=.1,regime='tight',shock=-2,episodes=64,seed=2,steps=64,save_paths=True)
    assert r['audit']['max_cash_error']<1e-7
    assert r['audit']['max_share_error']<1e-9
    assert r['audit']['clipped_orders']>0
    assert np.all(np.isfinite(r['prices']))

def test_preloaded_dealer_can_halt_under_stress():
    r=market_panel(1.3,.1,'tight',-15,64,19,steps=64,save_paths=True,preloaded_dealer=True)
    assert r['halt'].any()
    assert r['audit']['max_cash_error']<1e-7

def test_feasible_projection_randomized():
    rng=np.random.default_rng(19);n=10000
    p=rng.uniform(50,200,n);E0=rng.uniform(100,1000,n);I=rng.uniform(-.5,.5,n)*E0/p
    C=E0-I*p;D=rng.normal(0,20,n)
    q,f,d=feasible_orders(C,I,p,D,E0,2.,10.,1.,.01)
    C2=C-q*p-.01*np.abs(q);I2=I+q;E2=C2+I2*p
    assert not f.any() and not d.any()
    assert np.all(C2>=-E0-1e-8)
    assert np.all(np.abs(I2)<=10+1e-8)
    assert np.all(np.abs(I2)*p<=2*E2+1e-8)

def test_defaults_preserve_debt():
    q,f,d=feasible_orders(np.array([-300.]),np.array([2.]),np.array([100.]),np.array([1.]),np.array([100.]),2.,10.,1.,.01)
    assert d[0] and q[0]==-2
    c,i=settle(np.array([[-300.,1000.]]),np.array([[2.,-2.]]),q[:,None],np.array([100.]),.01)
    assert c[0,0]<0 and np.isclose(c.sum(),700)
