"""Exact fourth-moment check of the passive-excitation counterexample."""
import sympy as sp

def test_uniform_product_variance_and_valid_chebyshev_envelope():
    b, sig, u, v = sp.symbols('b sig u v', positive=True)
    w1,w2,w3,n1,n3 = sp.symbols('w1 w2 w3 n1 n3')
    product=(w1+n1)*(v*w1+u*w2+w3+n3)
    variables=(w1,w2,w3,n1,n3)
    def expectation(expression):
        total=0
        for powers,coef in sp.Poly(sp.expand(expression),*variables).terms():
            term=coef
            for var,power in zip(variables,powers):
                if power%2:term=0;break
                if var in (w1,w2,w3):term*=b**power/sp.Integer(power+1)
                else:term*=sig**power*(sp.factorial2(power-1) if power else 1)
            total+=term
        return sp.expand(total)
    variance=expectation(product**2)-expectation(product)**2
    sw2=b**2/3
    envelope=(sw2+sig**2)*(sw2*(1+u**2+v**2)+sig**2)+sw2**2*v**2
    assert sp.factor(envelope-variance)==2*b**4*v**2/15
    assert sp.factor(expectation(product))==b**2*v/3
    # The envelope follows the general variance identity before using the
    # negative fourth cumulant; this checks both terms independently.
    assert sp.factor(envelope-sw2**2*v**2-variance)==b**4*v**2/45
