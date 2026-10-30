"""Independent identities, information timing and durable-replay checks."""
import json,tempfile,unittest
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from scipy.stats import norm
import study,market,proof_audit
from model import Contract,response,position,net_value,no_data_randomized

class ResearchChecks(unittest.TestCase):
    def test_generated_class_includes_hidden_structure_and_prior_extremes(self):
        for seed in range(6):
          for j in range(12):
            case=study.make_case(seed,j,20261030);c=Contract(**case['contract'])
            for key in ['observation_gain','future_gain']:
                self.assertLessEqual(c.gain_min-1e-9,case[key]);self.assertLessEqual(case[key],c.gain_max+1e-9)
            self.assertAlmostEqual(response([c.qmax],[1.],c.H,c.a,c.kappa).sum(),c.gain_max)
            self.assertAlmostEqual(response([0.],[1e-8],c.H,c.a,c.kappa).sum(),c.gain_min)

    def test_gaussian_projection_known_distribution_and_covariance(self):
        case=study.make_case(1,2,98);c=replace(Contract(**case['contract']),N=32)
        stats,v=study.sufficient_statistics(case,c.N,20000)
        self.assertLess(abs(stats['mean'].mean()-case['observation_gain']),5*np.sqrt(v/c.N/20000))
        self.assertAlmostEqual(stats['mean'].var()/(v/c.N),1.,delta=.04)
        cert,_,_=study.certificates(stats,c,'gaussian_variance_bound',v)
        rate=np.mean(cert>=case['observation_gain']);self.assertGreater(rate,.968);self.assertLessEqual(rate,1.)

    def test_student_t_interval_uses_only_projected_reset_samples(self):
        case=study.make_case(0,2,155);c=replace(Contract(**case['contract']),N=32)
        stats,v=study.sufficient_statistics(case,c.N,15000)
        C,_,_=study.certificates(stats,c,'student_t_projection',v)
        self.assertGreater(np.mean(C>=case['observation_gain']),.968)
        self.assertTrue(study.method_valid(case,'student_t_projection',True))
        self.assertFalse(study.method_valid(case,'gaussian_iid',True))

    def test_median_of_means_bound_and_paid_fallback(self):
        c=Contract(N=8);k,m=study.mom_parameters(c.N,c.gamma)
        self.assertEqual(m,0);self.assertEqual(k%2,1);self.assertLessEqual(np.exp(-k/8),c.gamma)
        C,used,why=study.certificates(dict(mean=np.zeros(7),sd=np.ones(7),mom=np.zeros(7)),c,'median_of_means',.1)
        np.testing.assert_array_equal(C,np.full(7,c.gain_max));self.assertFalse(used);self.assertIn('paid',why)
        case=study.make_case(0,3,31);c=replace(Contract(**case['contract']),N=128)
        stats,v=study.sufficient_statistics(case,c.N,10000);C,used,_=study.certificates(stats,c,'median_of_means',v)
        self.assertTrue(used);self.assertGreater(np.mean(C>=case['observation_gain']),.975)

    def test_invalid_readings_are_not_claimed_safe(self):
        for scenario in [4,5]:
            case=study.make_case(0,scenario,77)
            for method in study.METHODS:self.assertFalse(study.method_valid(case,method,True))
            self.assertTrue(study.method_valid(case,'median_of_means',False))

    def test_holm_known_sequence(self):
        np.testing.assert_allclose(study.holm([.02,.001,.04,.8]),[.06,.004,.08,.8])
        self.assertEqual(len(study.holm([])),0)

    def test_saved_statistics_replay_decisions_and_reject_corruption(self):
        case=study.make_case(0,0,17)
        with tempfile.TemporaryDirectory() as tmp:
            job=(case,64,'code_config_hash',tmp);self.assertFalse(study.one_case(job)['cached'])
            self.assertTrue(study.one_case(job)['cached']);p=Path(tmp)/(case['case_id']+'.npz')
            saved=json.loads((Path(tmp)/(case['case_id']+'.json')).read_text())
            row=next(x for x in saved['rows'] if x['policy']=='gaussian_iid' and x['N']==32 and x['information_multiplier']==1.)
            c=replace(Contract(**case['contract']),N=32,reset_fee=.0005+.000025*case['contract']['H'])
            with np.load(p) as a:stats={k:a['N32_'+k] for k in ['mean','sd','mom']}
            C,_,_=study.certificates(stats,c,'gaussian_iid',c.H*c.sigma**2)
            self.assertAlmostEqual(net_value(position(C,c,c.info_fee),c,c.info_fee).mean(),row['mean_net_value'])
            p.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):study.one_case(job)

    def test_witness_is_strict_exact_rational(self):
        w=proof_audit.witness();self.assertEqual(len(w['inequalities']),7)
        self.assertGreater(w['net_information_advantage_lower']['decimal'],.14)
        self.assertEqual(proof_audit.lean_source(w).count('by decide'),7)

class QuoteChecks(unittest.TestCase):
    @staticmethod
    def events(n=1100):
        rng=np.random.default_rng(7);mid=100*np.exp(np.cumsum(rng.normal(0,.0003,n)))
        return pd.DataFrame(dict(timestamp=pd.date_range('2025-01-01',periods=n,freq='min',tz='UTC'),market='SYNTHETIC',bid=mid-.01,ask=mid+.01,bid_size=rng.uniform(30,100,n),ask_size=rng.uniform(30,100,n)))

    def test_ofi_quote_changes(self):
        g=pd.DataFrame(dict(bid=[100,100,101,101],ask=[102,102,102,103],bid_size=[10,12,7,7],ask_size=[8,9,9,6]))
        np.testing.assert_allclose(market.event_ofi(g),[0,1,7,9])

    def test_feature_prefix_invariance_and_forward_labels(self):
        e=self.events(650);a=market.minute_features(e,H=10,var_window=180)
        changed=e.copy();changed.loc[450:,'bid']*=1.02;changed.loc[450:,'ask']*=1.02
        b=market.minute_features(changed,H=10,var_window=180)
        cols=sorted(set(sum(market.FEATURES.values(),[])))
        np.testing.assert_allclose(a.iloc[:450][cols],b.iloc[:450][cols],equal_nan=True)
        # Quotes at t are known only at the END of the minute containing t.
        self.assertEqual(a.timestamp.iloc[0],e.timestamp.iloc[0]+pd.Timedelta(minutes=1))
        i=300;mid=((e.bid+e.ask)/2).to_numpy();future=mid[i+1:i+11]
        self.assertAlmostEqual(a.target.iloc[i],max(np.log(future.max()/mid[i]),np.log(mid[i]/future.min())))
        self.assertAlmostEqual(a.future_min_bid.iloc[i],e.bid.iloc[i+1:i+11].min())

    def test_gap_does_not_join_training_histories(self):
        e=self.events(650).drop(index=range(300,310));a=market.minute_features(e,H=10)
        segments=a.groupby('segment');self.assertEqual(len(segments),2)
        for _,g in segments:self.assertTrue(g.response_score.iloc[:180].isna().all())

    def test_purging_removes_labels_reaching_next_split(self):
        t=pd.date_range('2025-01-01',periods=1000,freq='min',tz='UTC');g=pd.DataFrame(dict(timestamp=t,label_end=t+pd.Timedelta(minutes=60)))
        tr,va,te=market.split_masks(g,t[500],t[700],t[900])
        self.assertTrue((g[tr].label_end<t[500]).all());self.assertTrue((g[va].label_end<t[700]).all())
        self.assertEqual(tr.sum(),440);self.assertEqual(va.sum(),140);self.assertEqual(te.sum(),200)

    def test_flat_market_pays_spread_fees_and_carry(self):
        a=market.trade_account(dict(ask=101.,exit_bid=99.,future_min_bid=98.),2.,10.,.05,60)
        carry=202*.05*60/(365*1440)
        self.assertAlmostEqual(a['net_pnl'],198*.999-202*1.001-carry)
        self.assertAlmostEqual(a['entry_cash'],202*1.001+carry)
        self.assertGreater(a['sampled_max_loss'],-a['net_pnl'])

    def test_optional_pipeline_fixture_never_masquerades_as_market_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);e=self.events(1600);e.to_csv(tmp/'events.csv',index=False)
            meta=dict(data_kind='best_quote_events',source='test generator',venue='fixture',instrument_type='synthetic',previous_use='unit test',fee_bps=2.,synthetic=True)
            (tmp/'meta.json').write_text(json.dumps(meta))
            status=market.evaluate(tmp/'events.csv',tmp/'meta.json',tmp/'out',H=10,bootstrap=20)
            self.assertEqual(status['status'],'COMPLETED_SYNTHETIC_FIXTURE');self.assertFalse(status['formal_certificate'])
            e.loc[0,'bid']=np.inf;e.to_csv(tmp/'events.csv',index=False)
            with self.assertRaises(ValueError):market.read_events(tmp/'events.csv',tmp/'meta.json')

if __name__=='__main__':unittest.main()
