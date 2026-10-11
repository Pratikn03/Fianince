"""Dependence, equivalence and bias sensitivity on the reconstructed original panel.

These are retrospective references under stated assumptions, not a new causal
design. Year aggregation avoids treating 96 sampled dates as independent years.
"""
from pathlib import Path
import hashlib
import itertools
import json
import numpy as np
import pandas as pd
from scipy import linalg, stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / 'research_extension/gap_closure_20261006/cross_venue/original_panel_reproduction.json'


def run():
    rows = json.loads(INPUT.read_text())['rows']
    dependence = []
    for variant in ['legacy', 'observed', 'raw_return']:
        f = pd.DataFrame([dict(year=r['year'], date=r['date'], Q=r[variant]['Q']) for r in rows])
        d = f.groupby(['year', 'date']).Q.mean().reset_index()
        annual = d.groupby('year').Q.mean()
        n = len(annual)
        assert n == 4 and len(d) == 96
        mean = float(annual.mean())
        se = float(annual.std(ddof=1) / np.sqrt(n))
        half = float(stats.t.ppf(.975, n - 1) * se)
        # Exact enumeration is a reference only under independent symmetric
        # annual mean errors; it is not randomized treatment assignment.
        samples = np.array([np.mean(np.array(signs) * annual.to_numpy())
                            for signs in itertools.product([-1, 1], repeat=n)])
        p = float(np.mean(np.abs(samples) >= abs(mean) - 1e-15))
        dependence.append(dict(variant=variant, yearly_means=annual.to_dict(),
                               equal_year_mean=mean, year_t3_95=[mean-half, mean+half],
                               leave_one_year_out_means={str(y):float(annual.drop(y).mean()) for y in annual.index},
                               annual_sign_symmetry_reference_p=p, enumerated_patterns=len(samples)))
    f = pd.DataFrame([dict(symbol=r['symbol'], date=r['date'], Q=r['observed']['Q'])
                      for r in rows if r['year'] == 2022])
    treat = (f.symbol == 'BTCUSDT').to_numpy(float)
    post = (f.date >= '2022-07-08').to_numpy(float)
    X = np.column_stack([np.ones(len(f)), treat, post, treat*post])
    q, r = linalg.qr(X, mode='economic')
    beta = linalg.solve_triangular(r, q.T @ f.Q.to_numpy())
    residual = f.Q.to_numpy() - X @ beta
    bread = linalg.inv(r) @ linalg.inv(r).T
    labels = np.unique(f.date)
    scores = np.array([X[f.date == day].T @ residual[f.date == day] for day in labels])
    n, k = X.shape
    covariance = bread @ (scores.T @ scores) @ bread * len(labels)/(len(labels)-1)*(n-1)/(n-k)
    se = float(np.sqrt(covariance[3, 3]))
    effect = float(beta[3])
    df = len(labels)-1
    baseline = abs(next(x for x in dependence if x['variant'] == 'observed')['equal_year_mean'])
    h90 = float(stats.t.ppf(.95, df) * se)
    equivalence = []
    for fraction in [.1, .25, .5, 1., 2., 3.]:
        margin = fraction * baseline
        lower_p = float(stats.t.sf((effect + margin)/se, df))
        upper_p = float(stats.t.cdf((effect - margin)/se, df))
        equivalence.append(dict(fraction_of_pooled_observed_Q= fraction, margin=margin,
                                lower_test_p=lower_p, upper_test_p=upper_p,
                                passes_5_percent_TOST=max(lower_p, upper_p) < .05))
    h95 = float(stats.t.ppf(.975, df)*se)
    bias = [dict(bias_bound_fraction_of_pooled_observed_Q=fraction,
                 imposed_absolute_bias_bound=fraction*baseline,
                 interval_if_bias_bound_is_valid=[effect-h95-fraction*baseline,
                                                 effect+h95+fraction*baseline])
            for fraction in [0., .25, .5, 1., 2.]]
    result = dict(
        status='COMPLETED_RETROSPECTIVE_INFERENCE_SENSITIVITY',
        input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        dependence=dependence,
        fee=dict(n_rows=n, n_dates=len(labels), n_treated_assets=1, effect=effect,
                 date_cluster_se=se, reference_df=df,
                 reference_90_interval=[effect-h90,effect+h90],
                 reference_95_interval=[effect-h95,effect+h95],
                 pooled_observed_Q_benchmark=baseline,
                 minimum_symmetric_equivalence_margin=abs(effect)+h90,
                 minimum_margin_fraction_of_benchmark=(abs(effect)+h90)/baseline,
                 equivalence_sensitivity=equivalence, bias_sensitivity=bias),
        assumptions_and_limits=[
            'Year t3 references require approximately independent comparable annual mean errors; four years do not verify that assumption.',
            'Sign enumeration requires independent symmetric annual errors; the 16 patterns are not randomized treatment assignments.',
            'Margins and bias bounds are a retrospective sensitivity grid, not prespecified economically justified bounds.',
            'The pooled observed-Q mean is a descriptive dimensionless scale, not a structural or treatment-effect baseline.',
            'One treated asset, spillovers and differential trends still prevent a causal fee interpretation. No bias bound is identified from the data.',
        ])
    (HERE/'inference_completion.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'annual_references':dependence,
                      'minimum_equivalence_margin_fraction':result['fee']['minimum_margin_fraction_of_benchmark'],
                      'TOST_passes':[x['fraction_of_pooled_observed_Q'] for x in equivalence if x['passes_5_percent_TOST']]},indent=2))


if __name__ == '__main__':
    run()
