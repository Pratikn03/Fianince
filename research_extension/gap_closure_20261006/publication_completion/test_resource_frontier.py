"""Independent exact algebra, state-space responses, and Gaussian likelihood checks."""
import numpy as np
import sympy as sp
from scipy import stats

def system(a,k,q,eta,d):
    rates=np.array([eta]) if d==0 else np.array([eta-d,eta+d])
    weights=np.array([q]) if d==0 else np.array([q/2,q/2])
    J=np.zeros((len(rates)+1,len(rates)+1));J[0]=np.r_[a,k*weights]
    for i,e in enumerate(rates):J[i+1]=e*J[0];J[i+1,i+1]+=1-e
    H=k*np.r_[1,rates];C=np.eye(len(H))[0]
    return J,H,C

def test_transfer_identity_exact():
    z,e,d,q=sp.symbols('z e d q');G=q*e*z/(z-1+e)
    split=q*z/2*((e-d)/(z-1+e-d)+(e+d)/(z-1+e+d))
    expected=-q*z*(z-1)*d*d/((z-1+e)*((z-1+e)**2-d*d))
    assert sp.factor(split-G-expected)==0

def test_third_tap_exact():
    a,k,q,e,d=sp.symbols('a k q e d')
    J0=sp.Matrix([[a,k*q],[e*a,1-e+e*k*q]]);H0=k*sp.Matrix([1,e])
    J=sp.zeros(3);J[0,:]=sp.Matrix([[a,k*q/2,k*q/2]])
    for i,r in enumerate([e-d,e+d]):
        J[i+1,:]=r*J[0,:];J[i+1,i+1]+=1-r
    H=k*sp.Matrix([1,e-d,e+d])
    assert (H[0]-H0[0])==0
    assert sp.factor((J*H)[0]-(J0*H0)[0])==0
    assert sp.factor((J**2*H)[0]-(J0**2*H0)[0])==-k*k*q*d*d

def test_quantity_kl_uniform_horizon():
    rng=np.random.default_rng(3);a,k,q,e=.5,.8,.2,.4;eps=.1;S=a+k*q
    K=2*k*k*q/(eps**3*(1-S)**2)
    for d in [.001,.02,.1]:
        kernels=[]
        for split in [0,d]:
            J,H,C=system(a,k,q,e,split);h=[];v=H.copy()
            for _ in range(1200):h.append(float(C@v));v=J@v
            h=np.array(h);assert np.isclose(h.max(),k);assert np.isclose(h.sum(),k/(1-S))
            kernels.append(h)
        diff=kernels[1]-kernels[0];assert np.linalg.norm(diff)<=K*d*d
        u=rng.standard_normal(300);u/=sum(abs(u));u*=2
        dm=np.convolve(diff,u)
        assert np.linalg.norm(dm)<=K*d*d*sum(abs(u))

def test_attaining_gaussian_midpoint():
    a,k,q,e,d=.5,.8,.2,.4,.02;sigma=.03;alpha=.1
    A=2*sigma*stats.norm.ppf(1-alpha)/(k*k*q*d*d)
    means=[]
    for split in [0,d]:
        J,H,C=system(a,k,q,e,split);means.append(float(C@J@J@H)*A)
    error=stats.norm.cdf(-abs(means[1]-means[0])/(2*sigma))
    assert np.isclose(error,alpha)

def test_monetary_gate_peak_not_state_norm():
    J,H,C=system(.5,.8,.2,.4,.1);B,L,lam,c=4.,.2,3.,.04
    V=(B-L)/(abs(lam)*.8+c)
    assert np.isclose(abs(lam*(C@H))*V+c*V+L,B)
    assert np.linalg.norm(H)>.8

def test_finite_horizon_optimal_l1_pulse():
    kernels=[]
    for d in [0,.1]:
        J,H,C=system(.5,.8,.2,.4,d);v=H.copy();h=[]
        for _ in range(120):h.append(float(C@v));v=J@v
        kernels.append(np.array(h))
    diff=kernels[1]-kernels[0];rng=np.random.default_rng(12)
    for T in [1,2,3,12,120]:
        D=np.zeros((T,T))
        for col in range(T):D[col:,col]=diff[:T-col]
        norms=np.linalg.norm(D,axis=0)
        assert np.isclose(norms.max(),np.linalg.norm(diff[:T]))
        for _ in range(20):
            v=rng.normal(size=T);v/=sum(abs(v))
            assert np.linalg.norm(D@v)<=norms[0]+1e-15
