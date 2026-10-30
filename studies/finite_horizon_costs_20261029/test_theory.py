"""Independent identities and adversarial checks for the written theorem."""
import itertools,unittest
from fractions import Fraction as F
from dataclasses import replace
import numpy as np
from scipy.optimize import minimize_scalar,linprog
from scipy.stats import norm
from model import *

class TheoryChecks(unittest.TestCase):
    def test_moment_matching_exact(self):
        for delta in [F(1,10),F(1,100),F(1,1000)]:
            eta=F(1,2)
            A=[eta-delta,eta+delta];B=[eta-2*delta,eta+delta/2]
            for j in range(3):
                self.assertEqual(sum(x**j/2 for x in A),B[0]**j/5+4*B[1]**j/5)
            a,b=rational_pair(delta,H=5)
            self.assertEqual(a[:3],b[:3])
            self.assertEqual(b[3]-a[3],-F(3,2)*F(2,5)*delta**3)

    def test_rational_and_state_response_agree(self):
        for delta in [.01,.04,.08]:
            a,b=rational_pair(F(str(delta)))
            np.testing.assert_allclose(response([.2,.2],[.5-delta,.5+delta],60),[float(v) for v in a],rtol=1e-13)
            np.testing.assert_allclose(response([.08,.32],[.5-2*delta,.5+delta/2],60),[float(v) for v in b],rtol=1e-13)

    def test_all_shock_corners_exact_stress(self):
        c=replace(Contract(),H=6)
        h=response([.1,.3],[.02,.9],c.H)
        I=1.2;fee=.04
        shocks=np.array(list(itertools.product([-c.flow_bound,c.flow_bound],repeat=c.H)))
        a=account_path(h,shocks,I,c,fee)
        self.assertAlmostEqual(a['maximum_loss'].max(),float(risk_reserve(I,h.sum(),c,fee)),places=10)

    def test_cashflow_identity_with_service_and_funding(self):
        c=Contract();h=response([.4],[.2],60);rng=np.random.default_rng(5)
        u=rng.uniform(-c.flow_bound,c.flow_bound,(37,60));I=3.;F=.064
        a=account_path(h,u,I,c,F)
        np.testing.assert_allclose(a['terminal'],c.wealth-F+I*a['price_change'][:,-1]+gross_value(I,c),atol=1e-11)

    def test_optimal_action_against_numerical_optimizer(self):
        rng=np.random.default_rng(4)
        for _ in range(80):
            c=replace(Contract(),service_fee=float(rng.uniform(.001,.1)))
            gain=float(rng.uniform(c.gain_min,c.gain_max));fee=float(rng.uniform(0,.8))
            I=float(position(gain,c,fee))
            cap=min(float(root_capacity(c.budget-fee,c.flow_bound*gain+c.b,c.quadratic_trade)),float(root_capacity(c.wealth-fee,c.price+c.b,c.quadratic_trade)))
            opt=minimize_scalar(lambda i:-float(net_value(i,c,fee)),bounds=(0,cap),method='bounded',options={'xatol':1e-10})
            self.assertGreaterEqual(float(net_value(I,c,fee))+1e-8,-opt.fun)
            self.assertLessEqual(float(risk_reserve(I,gain,c,fee)),c.budget+1e-12)
            self.assertLessEqual(c.price*I+c.b*I+c.quadratic_trade*I**2+fee,c.wealth+1e-12)

    def test_no_data_envelope_including_very_slow_memory(self):
        rng=np.random.default_rng(10)
        for H in [2,10,60,240]:
            c=replace(Contract(),H=H)
            self.assertAlmostEqual(response([c.qmax],[1.],H).sum(),c.gain_max,places=11)
            for _ in range(60):
                weights=rng.dirichlet(np.ones(5))*rng.uniform(0,c.qmax)
                eta=10**rng.uniform(-8,0,5)
                g=response(weights,eta,H).sum()
                self.assertGreaterEqual(g+1e-12,c.gain_min);self.assertLessEqual(g,c.gain_max+1e-12)

    def test_gaussian_known_pair_power(self):
        x=pair_testing(.04);n=x['N_required']
        self.assertAlmostEqual(norm.cdf(-np.sqrt(n)*x['distance']/(2*x['sigma'])),.05,places=12)
        self.assertGreater(norm.cdf(-np.sqrt(n/2)*x['distance']/(2*x['sigma'])),.05)

    def test_uniform_regret_bound_on_confidence_event(self):
        rng=np.random.default_rng(8)
        for _ in range(150):
            c=replace(Contract(),N=int(rng.choice([8,32,128])),reset_fee=float(rng.uniform(0,.005)),service_fee=float(rng.uniform(.001,.1)))
            if c.info_fee>=c.budget:continue
            g=float(rng.uniform(c.gain_min,c.gain_max));bound=guarantees(g,c)
            z=rng.uniform(-c.z,c.z);cert=float(gain_certificate(g+c.se*z,c))
            I=float(position(cert,c,c.info_fee));Io=float(position(g,c))
            self.assertLessEqual(gross_value(Io,c)-net_value(I,c,c.info_fee),bound['regret_upper']+1e-10)

    def test_projection_is_not_a_new_estimator(self):
        c=Contract();Y=np.linspace(1,30,100)
        np.testing.assert_array_equal(gain_certificate(Y,c),gain_certificate(Y,c,'linear_functional_projection'))

    def test_correlated_standard_error_requires_correction(self):
        c=Contract();rho=.2
        naive=norm.cdf(c.z/np.sqrt(1+(c.H-1)*rho))
        self.assertLess(naive,.8)
        self.assertAlmostEqual(norm.cdf(c.z),1-c.gamma)

    def test_no_trade_and_unaffordable_information(self):
        c=replace(Contract(),service_fee=.001)
        self.assertEqual(float(position(5,c)),0.)
        self.assertLess(float(net_value(position(5,c,c.info_fee),c,c.info_fee)),0.)
        self.assertTrue(np.isnan(position(5,c,fee=2.)))

    def test_signed_kernel_counterexample(self):
        h=np.array([1.,-.9]);self.assertAlmostEqual(h.sum(),.1)
        self.assertAlmostEqual(abs(h).sum(),1.9)
        v=np.array(list(itertools.product([-1.,1.],repeat=2)))
        self.assertAlmostEqual(max(abs(np.dot(x,h)) for x in v),1.9)

    def test_same_gamma_no_data_optimum_against_linear_program(self):
        for fee in [.003,.02,.08]:
            c=replace(Contract(),service_fee=fee);r=no_data_randomized(c)
            grid=np.unique(np.r_[np.linspace(0,r['free_units'],1001),r['safe_units']])
            unsafe=(grid>r['safe_units']+1e-12).astype(float)
            # Scale the objective so the solver's absolute dual tolerance does
            # not hide the tiny low-premium portfolio differences.
            scale=1e6
            lp=linprog(-scale*gross_value(grid,c),A_ub=[unsafe],b_ub=[c.gamma],A_eq=[np.ones(len(grid))],b_eq=[1.],bounds=(0,None),method='highs')
            self.assertTrue(lp.success);self.assertAlmostEqual(-lp.fun/scale,r['value'],places=9)

if __name__=='__main__':unittest.main(verbosity=2)
