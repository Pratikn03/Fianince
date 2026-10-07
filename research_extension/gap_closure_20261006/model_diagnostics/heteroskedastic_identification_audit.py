"""Exact root ambiguity and endogenous-regime assumption audit for existing C2."""
from pathlib import Path
import hashlib,json
import numpy as np
import sympy as sp
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def run():
    lam=sp.Rational(1,20);alpha=sp.Rational(-3,20);A=sp.Matrix([[1,-lam],[-alpha,1]])
    P=sp.Matrix([[0,1],[1,0]]);D=sp.diag(-1/alpha,-1/lam);alternative=D*P*A
    roots={'original_lambda':str(lam),'original_alpha':str(alpha),'original_product':str(lam*alpha),'alternative_lambda':str(1/alpha),'alternative_alpha':str(1/lam),'alternative_product':str(1/(lam*alpha))}
    exact=[]
    for vp,vf in [(1,4),(3,2),(7,10)]:
        V=sp.diag(vp,vf);V2=D*P*V*P.T*D.T
        Omega=A.inv()*V*A.inv().T;Omega2=alternative.inv()*V2*alternative.inv().T
        assert Omega==Omega2
        exact.append({'variances':[vp,vf],'original_covariance':[[str(x) for x in row] for row in Omega.tolist()],'alternate_variances':[str(V2[0,0]),str(V2[1,1])],'exact_covariance_equal':True})
    rng=np.random.default_rng(20261008);e=rng.normal(size=(200000,2));mix=np.linalg.inv([[1,-.8],[-.2,1]]);z=e@mix.T
    threshold=np.quantile(abs(z[:,0]),[1/3,2/3]);masks=[abs(z[:,0])<threshold[0],(abs(z[:,0])>=threshold[0])&(abs(z[:,0])<threshold[1]),abs(z[:,0])>=threshold[1]]
    conditional=[{'n':int(m.sum()),'structural_error_correlation':float(np.corrcoef(e[m].T)[0,1])} for m in masks]
    out={'source':'empirical_pipeline/binance_panel.py:fit_rigobon_c2','source_sha256':hashlib.sha256((ROOT/'empirical_pipeline/binance_panel.py').read_bytes()).hexdigest(),'root_example':roots,'exact_regime_covariances':exact,'selection_example':{'n':len(e),'unconditional_error_correlation':float(np.corrcoef(e.T)[0,1]),'conditioning':'thirds of absolute contemporaneous reduced-form price innovation; illustrative mathematical confounding, not calibrated to real regimes','regimes':conditional},'source_findings':['Uses dx and forward-aligned flow rather than innovations from a declared dynamic reduced form','Rolling 60-bin price-level volatility includes current price and backward-fills initialization','Regimes use pooled quantiles of an endogenous measured state','Fits unweighted covariance discrepancies with one initialization','Bounds lambda and alpha to [-1,1] and standard deviations to [.01,5], excluding other observationally equivalent branches','No independent justification of invariant slopes, conditional structural-error orthogonality, variance-profile separation, or shock labels','Optimizer success is not a causal identification or uncertainty certificate'],'limits':['Distinct nonproportional variance shifts can identify a mixing matrix only under defended restrictions and labeling/scaling','External sign/exclusion information could distinguish branches, but the code bounds alone are not that evidence','The endogenous-selection simulation illustrates an assumption failure; it does not estimate actual structural error correlations']}
    (HERE/'heteroskedastic_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Exact branch covariance matches:',len(exact));print('Root products:',roots['original_product'],roots['alternative_product']);print('Structural correlations unconditional/conditional:',out['selection_example']['unconditional_error_correlation'],[r['structural_error_correlation'] for r in conditional])
if __name__=='__main__':run()
