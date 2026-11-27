"""P1KS power check, exactly as fixed in P1KS_power_criteria.md (27 November 2026, before any data were read).

Input: the summary JSON printed by P1KS_Dev_Window_Naver_Colab.ipynb (development window 2015-2019).
Run:   python p1ks_power.py calibration.json      -> writes p1ks_power_results.json and prints the verdict.

Simulation (per replication):
  * Stocks: n_T treated ('large' calibration group) and n_C controls ('other' group).
  * Predictor: c_hat_s drawn from the group's calibrated distribution of the full-window estimate (linear
    interpolation of the printed quantiles). The true contribution is drawn from its regression on the estimate:
    c_s = mu + lam (c_hat_s - mu) + sqrt(lam (1 - lam)) sd_hat z_s, where lam = var_true / var(c_hat) is the
    reliability of the full-window estimate. var_true is the between-half covariance, recovered from the placebo
    s.d. of c_h2 - c_h1 and the between-half correlation; it is floored at zero.
  * Outcome: Delta S_s = theta c_s (treated) or 0 (control), plus noise with the placebo s.d. of S_h2 - S_h1, rescaled
    from the placebo half length to the test's 250-day windows by sqrt(days_half / 250).
  * Statistic: coefficient on Treated x c_hat in OLS of Delta S on (1, Treated, c_hat, Treated x c_hat), HC1 standard
    error, one-sided test at 5% (b > 0).
Pass: rejection in [3%, 7%] at theta = 0; power >= 80% at theta = 1; power >= 50% at theta = 0.5.
"""
import json
import sys
from pathlib import Path

import numpy as np

SEED = 20261127
REPS = 2000
N_T, N_C = 350, 1500        # KOSPI 200 + KOSDAQ 150 treated; other listed common stocks as controls (approximate)
WINDOW = 250
Z95 = 1.6448536269514722


def quantile_sampler(q, rng, n):
    """Inverse-CDF sampling from printed quantiles (5, 25, 50, 75, 95), linear between and in the tails."""
    p = np.array([0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
    lo = q['q05'] - (q['q25'] - q['q05']) * 0.25
    hi = q['q95'] + (q['q95'] - q['q75']) * 0.25
    v = np.array([lo, q['q05'], q['q25'], q['median'], q['q75'], q['q95'], hi])
    return np.interp(rng.random(n), p, v)


def group_params(g):
    q = g['c_full']
    sd_hat = q['sd']
    rho_h = g['corr_c_h1_h2']
    sd_dc = g['dc_placebo']['sd']
    v_half = sd_dc ** 2 / (2 * max(1e-12, 1 - rho_h))
    var_true = max(0.0, rho_h * v_half)
    lam = min(1.0, var_true / sd_hat ** 2) if sd_hat > 0 else 0.0
    days = 0.5 * (g['days_h1']['median'] + g['days_h2']['median'])
    sd_ds = g['dS_placebo']['sd'] * np.sqrt(days / WINDOW)
    return {'q': q, 'mu': q['mean'], 'sd_hat': sd_hat, 'lam': lam, 'sd_ds': sd_ds, 'var_true': var_true}


def one_rep(rng, pt, pc, theta):
    ch_t = quantile_sampler(pt['q'], rng, N_T)
    ch_c = quantile_sampler(pc['q'], rng, N_C)

    def true_c(ch, p):
        return p['mu'] + p['lam'] * (ch - p['mu']) + np.sqrt(p['lam'] * (1 - p['lam'])) * p['sd_hat'] * rng.standard_normal(len(ch))

    ct = true_c(ch_t, pt)
    ds_t = theta * ct + pt['sd_ds'] * rng.standard_normal(N_T)
    ds_c = pc['sd_ds'] * rng.standard_normal(N_C)
    y = np.concatenate([ds_t, ds_c])
    T = np.concatenate([np.ones(N_T), np.zeros(N_C)])
    ch = np.concatenate([ch_t, ch_c])
    X = np.column_stack([np.ones_like(y), T, ch, T * ch])
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    n, k = X.shape
    meat = (X * e[:, None] ** 2).T @ X
    V = XtX_inv @ meat @ XtX_inv * n / (n - k)
    return b[3] / np.sqrt(V[3, 3]) > Z95


def run(calib):
    pt, pc = group_params(calib['large']), group_params(calib['other'])
    rng = np.random.default_rng(SEED)
    rates = {}
    for theta in (0.0, 0.5, 1.0):
        rates[theta] = float(np.mean([one_rep(rng, pt, pc, theta) for _ in range(REPS)]))
    checks = {'size_theta0_in_3_7pct': 0.03 <= rates[0.0] <= 0.07,
              'power_theta1_ge_80pct': rates[1.0] >= 0.80,
              'power_theta05_ge_50pct': rates[0.5] >= 0.50}
    return {'rates': {str(k): v for k, v in rates.items()}, 'checks': checks, 'pass': all(checks.values()),
            'inputs': {'treated': {k: v for k, v in pt.items() if k != 'q'}, 'control': {k: v for k, v in pc.items() if k != 'q'},
                       'N_T': N_T, 'N_C': N_C, 'reps': REPS, 'seed': SEED}}


if __name__ == '__main__':
    calib = json.loads(Path(sys.argv[1]).read_text())
    res = run(calib)
    Path(__file__).with_name('p1ks_power_results.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    print('VERDICT:', 'PASS' if res['pass'] else 'FAIL')
