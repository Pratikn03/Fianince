"""Conditional signed-output and robust loss-contract computations.
Illustrative fixed coordinates only; no market or institutional calibration.
"""
from pathlib import Path
import json
import numpy as np
from scipy import linalg,stats
HERE=Path(__file__).resolve().parent

def power_peak_with_tail(J,C,N=150):
    h=next(k for k in range(1,1025) if np.linalg.norm(np.linalg.matrix_power(J,k),2)<1)
    q=float(np.linalg.norm(np.linalg.matrix_power(J,h),2))
    magnifications=[float(np.linalg.norm(C@np.linalg.matrix_power(J,t),2)) for t in range(N)]
    tail=float(max(np.linalg.norm(C@np.linalg.matrix_power(J,N+j),2) for j in range(h)))
    peak=max(magnifications)
    if tail>peak:raise ValueError('Finite peak not certified; increase horizon')
    return {'M_C':peak,'peak_step':int(np.argmax(magnifications)),'N':N,'block_h':h,'block_norm':q,'tail_upper':tail,'safe_radius_B1':1/peak}

def market_jacobian(coupling,a=.5,eta=.2,q=.2):
    # Two assets, original simultaneous-memory update, ordered x1,y1,x2,y2.
    diagonal=np.array([[a,q],[eta*a,1-eta+eta*q]])
    leader_to_target=np.array([[0,coupling*q],[0,eta*coupling*q]])
    return np.block([[diagonal,np.zeros((2,2))],[leader_to_target,diagonal]])

def symmetric_market_jacobian(theta,a=.5,eta=.2,q=.2,cross=.5):
    if theta<=0 or not 0<=cross<1:raise ValueError('Invalid symmetric impact family')
    impact=np.array([[1.,cross*theta],[cross*theta,theta*theta]])
    feedback=np.diag([q,q/(theta*theta)])
    effective=impact@feedback
    full=np.block([[np.eye(2)*a,effective],[np.eye(2)*eta*a,np.eye(2)*(1-eta)+eta*effective]])
    order=[0,2,1,3]
    return full[np.ix_(order,order)],impact,feedback

def metric_contract(J,C,D,epsilon):
    if epsilon<0 or not np.isfinite(epsilon) or max(abs(np.linalg.eigvals(J)))>=1:raise ValueError('Nominal metric construction requires a stable matrix and nonnegative finite uncertainty')
    P=linalg.solve_discrete_lyapunov(J.T,np.eye(len(J)))
    values,vectors=np.linalg.eigh(P);sqrt=(vectors*np.sqrt(values))@vectors.T;inverse=(vectors/np.sqrt(values))@vectors.T
    q0=float(np.linalg.norm(sqrt@J@inverse,2));q=q0+epsilon
    if q>=1:raise ValueError('No contraction certificate for declared uncertainty')
    c=float(np.linalg.norm(C@inverse,2));d=float(np.linalg.norm(sqrt@D,2))
    return {'P':P,'sqrt':sqrt,'inverse':inverse,'q0':q0,'epsilon':epsilon,'q':q,'c':c,'d':d,'radius_B1_repeated_input':float('inf') if c*d==0 else (1-q)/(c*d)}

def finite_metric_bound(r0,d,r,q,H,offset=0):
    if not np.all(np.isfinite([r0,d,r,q,offset,H])) or min(r0,d,r,q,offset)<0 or H<0 or int(H)!=H:raise ValueError('Invalid finite-horizon contract')
    values=[float(r0)]
    for _ in range(H):values.append(q*values[-1]+d*r+offset)
    return np.array(values)

def gaussian_input_radius(sigma,m,H,alpha):
    if not np.all(np.isfinite([sigma,m,H,alpha])) or sigma<=0 or m<1 or H<1 or int(m)!=m or int(H)!=H or not 0<alpha<1:raise ValueError('Invalid Gaussian contract')
    return float(sigma*np.sqrt(stats.chi2.ppf(1-alpha/H,m)))

def moment_input_radius(moment_bounds,alpha):
    values=np.asarray(moment_bounds,float)
    if not np.all(np.isfinite(values)) or np.any(values<0) or not 0<alpha<1:raise ValueError('Invalid moment-tail contract')
    return float(np.sqrt(values.sum()/alpha))

def pnl_contract(positions,prices,b,component_bounds):
    h=np.asarray(positions,float);p=np.asarray(prices,float);b=np.asarray(b,float);delta=np.asarray(component_bounds,float)/10000
    if not np.all(np.isfinite(np.r_[h,p,b,delta])) or np.any(delta<0) or np.any(p<=0) or np.any(np.abs(b)>np.asarray(component_bounds)):raise ValueError('Outside mark-price contract')
    linear=float((h*p/10000)@b);actual=float((h*p)@np.expm1(b/10000))
    remainder=float(np.sum(np.abs(h)*p*np.exp(delta)*delta**2/2))
    return {'linear_pnl_dollars':linear,'exact_mark_pnl_dollars':actual,'remainder_bound_dollars':remainder,'absolute_approximation_error':abs(actual-linear)}

def run():
    hedged=[];structural=[];symmetric=[];rho=.85
    for theta in [0.,1.,2.,3.,4.]:
        J=np.array([[rho,2,0],[0,rho,0],[0,theta,rho]]);C=np.array([[1.,0.,-1.]])
        row=power_peak_with_tail(J,C);row.update(theta=theta,rho=rho);hedged.append(row)
    for theta in [0.,2.,4.,8.,16.]:
        K=market_jacobian(theta);row=power_peak_with_tail(K,np.array([[0.,0.,1.,0.]]));row.update(theta=theta,rho=float(max(abs(np.linalg.eigvals(K[:2,:2])))),rho_numeric=float(max(abs(np.linalg.eigvals(K)))));structural.append(row)
    base=symmetric_market_jacobian(1)[0];common_radius=float(max(abs(np.linalg.eigvals(base))))
    for theta in [1.,2.,4.,8.,16.]:
        K,impact,feedback=symmetric_market_jacobian(theta);row=power_peak_with_tail(K,np.array([[0.,0.,1.,0.]]))
        row.update(theta=theta,rho=common_radius,rho_numeric=float(max(abs(np.linalg.eigvals(K)))),impact=impact.tolist(),feedback=feedback.tolist())
        symmetric.append(row)
    J=np.array([[.6,.15],[0,.5]]);C=np.array([[1.,0.]]);D=np.eye(2);contract=metric_contract(J,C,D,.05)
    switchingA=np.array([[.5,2],[0,.5]]);switchingB=np.array([[.5,0],[2,.5]])
    pnl=pnl_contract([10,-3],[100,200],[20,-15],[20,15])
    output={'scope':'Constructed exact/model-only examples; no calibrated market impact, dealer capital, execution or causal policy validation','hedged_portfolio':hedged,'structural_market_family':structural,'symmetric_impact_family':symmetric,'uncertainty_contract':{k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in contract.items()},'switching_counterexample':{'individual_radii':[float(max(abs(np.linalg.eigvals(A)))) for A in [switchingA,switchingB]],'two_step_product_radius':float(max(abs(np.linalg.eigvals(switchingB@switchingA))))},'gaussian_example':{'sigma':.01,'input_dimensions':2,'horizon':100,'alpha':.05,'union_bound_input_radius':gaussian_input_radius(.01,2,100,.05)},'static_mark_example':pnl}
    (HERE/'risk_results.json').write_text(json.dumps(output,indent=2)+'\n')
    print('Hedged magnifications',[r['M_C'] for r in hedged]);print('Structural radii',[r['rho'] for r in structural]);print('Structural magnifications',[r['M_C'] for r in structural]);print('Switching product radius',output['switching_counterexample']['two_step_product_radius'])
if __name__=='__main__':run()
