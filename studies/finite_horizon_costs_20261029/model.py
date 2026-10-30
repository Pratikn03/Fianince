"""Explicit finite-horizon cohort market and cost-aware inventory decision."""
from dataclasses import dataclass, asdict
from fractions import Fraction as R
import numpy as np
from scipy.stats import norm, chi2

@dataclass(frozen=True)
class Contract:
    H: int = 60
    a: float = .4
    kappa: float = 1.
    qmax: float = .55
    sigma: float = .02
    gamma: float = .025
    N: int = 32
    reset_fee: float = .002
    budget: float = 1.
    wealth: float = 1000.
    price: float = 100.
    flow_bound: float = .04
    service_fee: float = .08
    linear_trade: float = .002
    quadratic_trade: float = .0002
    funding_rate: float = .05

    @property
    def b(self):
        return self.linear_trade+self.price*self.funding_rate*self.H/(365*24*60)
    @property
    def info_fee(self): return self.N*self.reset_fee
    @property
    def se(self): return self.sigma*np.sqrt(self.H/self.N)
    @property
    def z(self): return norm.ppf(1-self.gamma)
    @property
    def gain_min(self): return self.kappa*np.sum(self.a**np.arange(self.H))
    @property
    def gain_max(self):
        return self.kappa*np.sum((self.a+self.kappa*self.qmax)**np.arange(self.H))

def response(q, eta, H, a=.4, kappa=1.):
    q=np.asarray(q,float);eta=np.asarray(eta,float)
    if len(q)!=len(eta) or np.any(q<0) or np.any(eta<=0) or np.any(eta>1):
        raise ValueError('positive cohort contract required')
    x=float(kappa); y=eta*x; out=[]
    for _ in range(H):
        out.append(x)
        x=a*x+kappa*np.dot(q,y)
        y=(1-eta)*y+eta*x
    return np.asarray(out)

def rational_pair(delta, H=60, a=R(2,5), kappa=R(1), Q=R(2,5), eta=R(1,2)):
    delta=R(delta)
    def one(q,e):
        x=kappa;y=[v*x for v in e];h=[]
        for _ in range(H):
            h.append(x);x=a*x+kappa*sum(v*w for v,w in zip(q,y))
            y=[(1-v)*w+v*x for v,w in zip(e,y)]
        return h
    A=one([Q/2,Q/2],[eta-delta,eta+delta])
    B=one([Q/5,4*Q/5],[eta-2*delta,eta+delta/2])
    return A,B

def pair_testing(delta,H=60,sigma=.02,beta=.05):
    A,B=rational_pair(R(str(delta)),H)
    diff=np.array([float(b-a) for a,b in zip(A,B)])
    d=float(np.linalg.norm(diff))
    n=(2*sigma*norm.ppf(1-beta)/d)**2
    return dict(delta=delta,distance=d,N_required=n,first_difference=float(B[3]-A[3]),
        gain_A=float(sum(A)),gain_B=float(sum(B)),H=H,sigma=sigma,beta=beta)

def root_capacity(remaining, coefficient, d):
    """Stable nonnegative root; negative remaining is not an affordable action."""
    remaining=np.asarray(remaining,float);coefficient=np.asarray(coefficient,float)
    if np.any(coefficient<=0) or d<=0:raise ValueError('positive costs needed')
    v=2*np.maximum(remaining,0)/(coefficient+np.sqrt(coefficient**2+4*d*np.maximum(remaining,0)))
    return np.where(remaining>=0,v,np.nan)

def gain_certificate(observed_sum,c,kind='functional',rho=0.):
    if kind in {'functional','linear_functional_projection'}:margin=c.z*c.se
    elif kind=='ellipsoid':margin=c.se*np.sqrt(chi2.ppf(1-c.gamma,c.H))
    elif kind=='point':margin=0.
    elif kind=='corrected_covariance':margin=c.z*c.se*np.sqrt(1+(c.H-1)*rho)
    else:raise ValueError(kind)
    return np.clip(np.asarray(observed_sum)+margin,c.gain_min,c.gain_max)

def position(gain,c,fee=0.):
    if fee<0 or fee>min(c.budget,c.wealth):
        return np.full_like(np.asarray(gain,float),np.nan)
    preferred=max(0.,(c.service_fee-c.b)/(2*c.quadratic_trade))
    stress=root_capacity(c.budget-fee,c.flow_bound*np.asarray(gain)+c.b,c.quadratic_trade)
    cash=root_capacity(c.wealth-fee,c.price+c.b,c.quadratic_trade)
    return np.minimum(np.minimum(preferred,stress),cash)

def gross_value(I,c): return (c.service_fee-c.b)*I-c.quadratic_trade*I**2
def net_value(I,c,fee=0.): return gross_value(I,c)-fee
def no_data_randomized(c):
    """Best no-data value allowing the SAME gamma probability of unsafe action."""
    safe=float(position(c.gain_max,c))
    free=min(max(0.,(c.service_fee-c.b)/(2*c.quadratic_trade)),
             float(root_capacity(c.wealth,c.price+c.b,c.quadratic_trade)))
    value=(1-c.gamma)*gross_value(safe,c)+c.gamma*gross_value(free,c)
    return dict(safe_units=safe,free_units=free,
                mean_units=(1-c.gamma)*safe+c.gamma*free,value=float(value))
def risk_reserve(I,gain,c,fee=0.):
    return c.flow_bound*gain*I+c.b*I+c.quadratic_trade*I**2+fee

def guarantees(gain,c):
    """Written-theorem bounds, not an empirical estimate or priority claim."""
    F=c.info_fee
    if F>min(c.budget,c.wealth):return dict(affordable=False)
    I0=float(position(c.gain_max,c));Io=float(position(gain,c))
    Im=float(position(gain+2*c.z*c.se,c,fee=F))
    randomized=no_data_randomized(c)
    lower=(1-2*c.gamma)*float(gross_value(Im,c))-F-randomized['value']
    r0=c.flow_bound*c.gain_min+c.b
    Imax=c.wealth/c.price
    LG=c.flow_bound*Imax/r0
    LF=1/min(r0,c.price+c.b)
    p=max(0,c.service_fee-c.b)
    A=2*c.z*c.sigma*np.sqrt(c.H)*p*LG
    D=1+p*LF
    regret=A/np.sqrt(c.N)+D*F
    return dict(affordable=True,no_data_units=I0,oracle_units=Io,
        conservative_units=Im,no_data_value=float(gross_value(I0,c)),
        no_data_same_gamma_value=randomized['value'],
        oracle_value=float(gross_value(Io,c)),net_information_value_lower=lower,
        regret_upper=regret,A=A,D=D,L_gain=LG,L_fee=LF,
        real_optimal_bound_N=(A/(2*D*c.reset_fee))**(2/3) if c.reset_fee else None)

def account_path(h,u,I,c,fee=0.):
    """Flat-to-flat cash accounting; service premium arrives AFTER settlement."""
    u=np.asarray(u,float)
    if u.shape[-1]!=c.H:raise ValueError('holding horizon mismatch')
    x=np.apply_along_axis(lambda v:np.convolve(v,h)[:c.H],-1,u)
    trade=c.linear_trade*I+c.quadratic_trade*I**2
    carry=(c.b-c.linear_trade)*I
    cash=c.wealth-fee-c.price*I-trade/2
    equity=cash+I*(c.price+x)
    before_fee_credit=equity[...,-1]-trade/2-carry
    net=before_fee_credit+c.service_fee*I
    return dict(price_change=x,equity=equity,settlement=before_fee_credit,
                terminal=net,maximum_loss=np.maximum(c.wealth-equity.min(axis=-1),
                                                     c.wealth-before_fee_credit))
