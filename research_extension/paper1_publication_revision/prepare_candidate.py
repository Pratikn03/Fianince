"""Prepare an OFFLINE amendment candidate. No registration file or unlock is changed."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = (HERE/'source/ceiling_suite/p1_empirics/p1f_executor_A1.py').read_text()
src = '"""UNREGISTERED OFFLINE CANDIDATE. Requires a new documented amendment and simulation gate.\nLive archive downloads are disabled in run_all.\n"""\n'+src
src = src.replace('def to_bars(k, m):', 'def to_bars(k, m, bar="30min"):')
a, b = src.index('def to_bars('), src.index('# ---------------------------------------------------------------- features')
chunk = src[a:b].replace('NDAYS * 48, freq=BAR', 'NDAYS * int(pd.Timedelta("1d") / pd.Timedelta(bar)), freq=bar')
chunk = chunk.replace('resample(BAR,', 'resample(bar,').replace('pd.Timedelta(BAR)', 'pd.Timedelta(bar)')
chunk = chunk.replace(' < 6,', ' < int(pd.Timedelta(bar) / pd.Timedelta("5min")),')
chunk = chunk.replace('age > 1800', 'age > pd.Timedelta(bar).total_seconds()')
chunk = chunk.replace('searchsorted(ends - pd.Timedelta("1ns"), side="right")', 'searchsorted(ends, side="left")')
chunk = chunk.replace('pd.Timedelta("1d")', 'pd.Timedelta("1D")')
src = src[:a]+chunk+src[b:]
# The specification names quantity open interest and a 48-bar moving average.
src = src.replace('sum_open_interest_value', 'sum_open_interest')
src = src.replace('lev = N - ema(N, 48)', 'lev = N - np.stack([pd.DataFrame(N[..., j]).rolling(48, min_periods=48).mean().values for j in range(N.shape[-1])], -1)')
src = src.replace('boot=BOOT, bpd=48):', 'boot=BOOT, bpd=48, block_days=3):')
src = src.replace('tmask[start:train_end] = True', 'tmask[start:train_end - 1] = True  # one-step target must remain inside training')
src = src.replace('tr[train_end:] = False', 'tr[train_end - 8:] = False  # purge every eight-step boundary label')
old = '''    nday = (test_end - train_end) // bpd
    sl = slice(train_end, train_end + nday * bpd)
    dd = d[sl].reshape(nday, bpd, S).sum((1, 2))
    vv = v[sl].reshape(nday, bpd, S).sum((1, 2))'''
new = '''    sl = slice(train_end, test_end)
    starts = np.arange(0, test_end - train_end, bpd)
    nday = len(starts)
    dd = np.add.reduceat(d[sl].sum(1), starts)
    vv = np.add.reduceat(v[sl].sum(1), starts)
    if nday < 2 or vv.sum() <= 0:
        raise ValueError("Insufficient evaluation days or target variation")'''
assert old in src
src = src.replace(old, new)
src = src.replace('idx = rng.integers(0, nday, (boot, nday))', '''if not 1 <= block_days <= nday:
        raise ValueError("Invalid bootstrap block length")
    nb = (nday + block_days - 1) // block_days
    starts_boot = rng.integers(0, nday, (boot, nb))
    idx = ((starts_boot[..., None] + np.arange(block_days)) % nday).reshape(boot, -1)[:, :nday]''')
src = src.replace('elif lo > 0 and est >= delta:', 'elif lo > delta:')
src = src.replace('"n_test_rows": int(rows_te.sum()),', '"n_test_rows": int(rows_te.sum()), "n_scored_days": nday, "block_days": block_days, "one_sided_confidence": 0.9,')
start, end = src.index('def power_gate('), src.index('\ndef a1(')
src = src[:start]+'''def injection_coefficient(residual_variance, target_variance, gain):
    """Population algebra when residuals are orthogonal to the baseline.
    Sample estimates of these variances supply only a calibration diagnostic.
    """
    target = gain * target_variance
    if not 0 < target < residual_variance:
        raise ValueError("Requested incremental signal is infeasible")
    return np.sqrt(target / (residual_variance - target))


def power_gate(R, A, dOI, N, train_end, rng, draws=GATE_DRAWS, bpd=48):
    """Training-only candidate; injection calibrated from inner-training residuals.
    Its achieved out-of-sample power must be established in an amended simulation gate.
    """
    R, A, dOI, N = [z[:train_end].copy() for z in (R, A, dOI, N)]
    y = np.roll(R, -1, 0); y[-1] = np.nan
    T, S = R.shape
    mid = 2*bpd + ((train_end-2*bpd)//bpd//2)*bpd
    X = features(R, A, dOI)
    signal = np.full_like(R, np.nan)
    for s in range(S):
        fitmask = np.arange(T) >= 2*bpd
        fitmask[mid-1:] = False
        fitmask &= np.isfinite(X[:, s]).all(1) & np.isfinite(y[:, s])
        Z = np.column_stack([np.ones(T), X[:, s]])
        beta = np.linalg.lstsq(Z[fitmask], y[fitmask, s], rcond=None)[0]
        residual = y[:, s] - Z @ beta
        vr = np.var(residual[fitmask]); vy = np.var(y[fitmask, s])
        c = injection_coefficient(vr, vy, 2*DELTA)
        signal[:, s] = c * residual / np.sqrt(vr)
    hits = 0
    for _ in range(draws):
        z = signal + rng.standard_normal(signal.shape)
        result = evaluate(R, A, dOI, N, DELTA, mid, train_end-1,
                          inject=z, rng=rng, boot=400, bpd=bpd)
        hits += result["verdict"] == "relevant"
    return hits/draws

''' + src[end:]
src = src.replace('    import os\n    os.makedirs(workdir', '''    import os
    if FETCH is http_fetch:
        raise SystemExit("UNREGISTERED OFFLINE CANDIDATE: live execution disabled; amend and validate first")
    os.makedirs(workdir''')
src = src.replace('bars, coverage, files = {}, {},', 'bars, bars5, coverage, files = {}, {}, {},')
src = src.replace('bars[s] = b', 'bars[s] = b\n        bars5[s] = to_bars(k, m, bar="5min")')
anchor = '    res["A2_delta_0.002"] = '
src = src.replace(anchor, '''    R5, A5, O5, N5 = panel_arrays({s: bars5[s] for s in kept})
    res["A2_5minute"] = evaluate(R5, A5, O5, N5, DELTA, TRAIN_DAYS*288, NDAYS*288-1,
                                 rng=np.random.default_rng(SEED), bpd=288)
    res["A2_block_sensitivity"] = {str(k): evaluate(R, A, dOI, N, DELTA, train_end, test_end,
        rng=np.random.default_rng(SEED), block_days=k) for k in (1, 5)}
''' + anchor)
src = src.replace('SUPPORTIVE: composition was invisible to prices and irrelevant for price forecasts',
                  'SUPPORTIVE FOR SPECIFIED LEARNERS AND MARGIN; no structural invisibility inference')
src = src.replace('P1F_forecast_irrelevance_spec.md + P1F_amendment_A1.md', 'UNREGISTERED OFFLINE CANDIDATE: P1F_candidate_amendment.md')
src = src.replace('A2_registered_wording', 'A2_candidate_wording').replace('A1_registered_wording', 'A1_candidate_wording')
src = src.replace('Class positions did not improve price forecasts by delta or more beyond public prices and anonymous flow.',
                  'For the specified model, features, horizon and bootstrap, the upper one-sided 90% limit is below delta.')
src = src.replace('Class positions improved price forecasts beyond public prices and anonymous flow; the irrelevance prediction is rejected.',
                  'For the specified model, features, horizon and bootstrap, the lower one-sided 90% limit exceeds delta.')
src = src.replace('Prices and anonymous flow did not reveal how top-trader positions moved.',
                  'The specified baseline met the registered position-change prediction threshold; no structural non-identification follows.')
src = src.replace('Prices and anonymous flow revealed how top-trader positions moved.',
                  'The specified baseline did not meet the registered position-change prediction threshold.')
src = src.replace('feb2022_quote_volume', 'ranking_month_quote_volume')
src = src.replace('Implements ceiling_suite/p1_empirics/P1F_forecast_irrelevance_spec.md exactly.',
                  'This candidate changes the registered implementation and is not the registered test.')
(HERE/'candidate_p1f_executor.py').write_text(src)
print('Wrote offline candidate with purged labels, all-day scoring, dependence sensitivity, and 5-minute output.')
