"""Builds the P7S amendment A1 notebooks. Each notebook carries the frozen source files inside it, checks their
SHA-256 before running, and needs no access to the repository.

  python3 make_p7s_A1_notebooks.py                      -> P7S_A1_Development_Colab.ipynb
  python3 make_p7s_A1_notebooks.py --dev-sha <sha256>   -> also P7S_A1_Evaluation_Colab.ipynb, which runs only on
                                                           the development outputs with that SHA-256
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CODE = ["p7s_executor_A1.py", "p7s_data.py", "p7s_pipeline_A1.py"]

SETUP = r'''
import datetime, hashlib, json, os, sys, time, zipfile

SRC = __SRC__
SHA = __SHA__
os.makedirs('p7s_code', exist_ok=True)
for name, text in SRC.items():
    got = hashlib.sha256(text.encode('utf-8')).hexdigest()
    assert got == SHA[name], f'{name}: source does not match the registered SHA-256'
    open(os.path.join('p7s_code', name), 'w', encoding='utf-8').write(text)
sys.path.insert(0, 'p7s_code')
import p7s_data as pdz, p7s_executor_A1 as ex, p7s_pipeline_A1 as pl
print('code verified:', {k: v[:12] for k, v in SHA.items()})
arch = pdz.Archive('p7s_cache')
CFG = pl.CFG_PRIMARY
t0 = time.time()
'''

DEV_MD = """# P7S amendment A1: development stage (run once)

This notebook reads **warm-up and development data only** (2023-12-04 to 2024-06-30). It does not touch the
evaluation window.

It does three things, all by rules fixed in `P7S_amendment_A1.md`:
1. draws the universe of 30 symbols by development-period quote volume;
2. fits every threshold on development data;
3. prints a blinded precision check: standard errors and event counts, with no estimate.

Run the cell (about 20 to 30 minutes, mostly downloads). If the connection drops, run it again: finished downloads
are kept. Send back the printed output and `p7s_dev_outputs.zip`. **Do not run any evaluation notebook until the
development outputs are committed and hashed.**
"""

DEV_RUN = r'''
folders = arch.list_symbol_folders()
out = pl.run_development(CFG, arch, folders)
out['utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out['code_sha256'] = SHA
out['downloads'] = {'downloaded': arch.n_downloaded, 'from_cache': arch.n_cached, 'absent_404': arch.n_absent}
raw = json.dumps(out, indent=1, sort_keys=True, default=float).encode('utf-8')
open('p7s_dev_outputs.json', 'wb').write(raw)
with zipfile.ZipFile('p7s_dev_outputs.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('p7s_dev_outputs.json')

print('\n=== P7S A1 development stage ===')
print('window: warm-up from', CFG['warmup_start'], '| development', CFG['dev_start'], 'to', CFG['dev_end'])
print('candidates:', out['n_candidates'], '| screened:', out['n_screened'],
      '| dropped for a missing development kline file:', len(out['dropped_missing_development_kline']),
      '| higher-ranked symbols skipped for missing files:', sorted(out['skipped_for_missing_files']))
print('universe (by development quote volume):')
print('  ' + ', '.join(out['universe']))
cov = out['coverage']
print('lowest kline bar coverage: %.4f | lowest metrics bar coverage: %.4f | lowest share of development bars with Pi: %.4f' % (
    min(c['kline_bar_coverage'] for c in cov.values()), min(c['metrics_bar_coverage'] for c in cov.values()),
    min(c['pi_defined_share_dev'] for c in cov.values())))
bp = out['blinded_precision_development']
print('blinded precision on development data (no estimate is computed or shown):')
print('  symbols with 20 events in every cell:', bp['n_symbols_used'], '| excluded:', bp['symbols_excluded'])
print('  events per cell:', bp['events_per_cell_total'])
print('  standard error of the calm difference: %.4f | of the DiD: %.4f | margin E: %.2f' % (
    bp['se_beta_calm'], bp['se_did'], bp['E_margin']))
print('SHA-256 of p7s_dev_outputs.json:', hashlib.sha256(raw).hexdigest())
print('downloads:', out['downloads'], '| minutes: %.1f' % ((time.time() - t0) / 60))
try:
    from google.colab import files
    files.download('p7s_dev_outputs.zip')
except Exception:
    pass
'''

EVAL_MD = """# P7S amendment A1: evaluation stage (the single run)

**This is the registered test. It is run once.** It reads the evaluation window (2024-07-01 to 2026-10-28) for
the universe and thresholds fixed in the development stage, and refuses any other development outputs.

1. Put `p7s_dev_outputs.zip` (from the development notebook) in the Colab files pane, or upload it when asked.
2. Run the cell (about 20 to 30 minutes). If the connection drops during the downloads, run it again: finished
   downloads are kept, and no statistic is computed until every file is in.
3. Send back the printed output and `p7s_eval_results.zip`.

Whatever the verdict, it is reported as it comes out.
"""

EVAL_RUN = r'''
DEV_SHA = '__DEV_SHA__'
if os.path.exists('p7s_eval_results.json'):
    raise SystemExit('The evaluation has already been run in this session. The results are in p7s_eval_results.json. It is not run twice.')
if not os.path.exists('p7s_dev_outputs.zip'):
    from google.colab import files
    files.upload()
with zipfile.ZipFile('p7s_dev_outputs.zip') as z:
    raw_dev = z.read('p7s_dev_outputs.json')
assert hashlib.sha256(raw_dev).hexdigest() == DEV_SHA, 'These are not the registered development outputs. Stop.'
dev_out = json.loads(raw_dev)
assert dev_out['code_sha256'] == SHA, 'The development stage ran with other code. Stop.'

# Format gate (logged addition of 11 November 2026, made before any evaluation data were read). It checks the
# layout of a sample of evaluation files, one day a month for the two largest symbols, and can only stop the run.
# It computes no statistic and prints no price or open-interest value.
def _format_problem(sym, day):
    ku, mu = pdz.kline_url(sym, day), pdz.metrics_url(sym, day)
    got = arch.get_many([ku, mu])
    if got[ku] is None or got[mu] is None:
        return 'file missing'
    t0 = pdz.day_start_ms(day)
    try:
        k = pdz.parse_klines(got[ku]); m = pdz.parse_metrics(got[mu])
    except Exception as e:
        return 'parse error: ' + type(e).__name__
    ko = k['open_ms'].to_numpy(); mt = m['ts_ms'].to_numpy()
    if len(ko) < 280 or ko.min() < t0 or ko.max() >= t0 + 288 * pdz.BAR_MS or ((ko - t0) % pdz.BAR_MS).any():
        return 'kline time stamps are not on the 5-minute grid of the day'
    if not (k['close'].to_numpy() > 0).all():
        return 'kline close is not a positive number'
    if len(mt) < 250 or mt.min() < t0 or mt.max() >= t0 + 288 * pdz.BAR_MS:
        return 'metrics time stamps are outside the day'
    if (m['oi_value'].to_numpy() > 0).mean() < 0.9 or (m['top_ratio'].to_numpy() > 0).mean() < 0.9:
        return 'metrics values are missing'
    return None

gate_days = sorted({d for d in pdz.days(CFG['eval_start'], CFG['eval_end']) if d.endswith('-01')}
                   | {CFG['eval_start'], CFG['eval_end']})
gate = {(s, d): _format_problem(s, d) for s in dev_out['universe'][:2] for d in gate_days}
gate_fail = {f'{s} {d}': r for (s, d), r in gate.items() if r}
print(f'format gate: {len(gate) - len(gate_fail)} of {len(gate)} sampled files pass; problems: {gate_fail}')
if len(gate_fail) > 0.1 * len(gate):
    raise SystemExit('FORMAT GATE FAILED before any statistic was computed. Send this output; do not rerun.')

res = pl.run_evaluation(CFG, arch, dev_out)
res['format_gate'] = {'sampled': len(gate), 'problems': gate_fail}
res['utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
res['code_sha256'] = SHA
res['dev_outputs_sha256'] = DEV_SHA
res['downloads'] = {'downloaded': arch.n_downloaded, 'from_cache': arch.n_cached, 'absent_404': arch.n_absent}
raw = json.dumps(res, indent=1, sort_keys=True, default=float).encode('utf-8')
open('p7s_eval_results.json', 'wb').write(raw)
with zipfile.ZipFile('p7s_eval_results.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('p7s_eval_results.json')

print('\n=== P7S A1 evaluation: the single registered run ===')
print('window:', CFG['eval_start'], 'to', CFG['eval_end'], '|', res['n_days'], 'days | symbols with enough events:',
      res['symbols_with_enough_events'])
if res['status'] != 'evaluated':
    print('NOT EVALUABLE:', res['reason'])
else:
    p = res['primary']
    print('symbols used:', p['n_symbols_used'], '| excluded:', p['symbols_excluded'])
    print('events per cell:', p['events_per_cell_total'])
    print('calm difference: %.4f | 90%% interval [%.4f, %.4f] | margin E = %.2f | H1 (calm silence): %s' % (
        p['beta_calm_mean'], p['beta_calm_ci90'][0], p['beta_calm_ci90'][1], p['E_margin'], p['h1_calm_silence']))
    print('stress difference: %.4f | DiD: %.4f | bootstrap 95%% interval [%.4f, %.4f]' % (
        p['beta_stress_mean'], p['did'], p['did_ci95'][0], p['did_ci95'][1]))
    print('H2 time-shift test: p = %.4f over %d shifts of %d days | H2 (stress reveals): %s' % (
        p['p_h2_stress_reveals'], p['shift_test']['n_shifts'], p['shift_test']['step_days'], p['h2_stress_reveals']))
    print('share of symbols with a positive stress difference: %.3f' % p['share_symbols_beta_stress_positive'])
    print('REGISTERED VERDICT:', p['verdict'])
    print('\nsensitivity checks (descriptive; none enters the verdict):')
    for k, v in res['sensitivity'].items():
        if 'did' in v:
            print('  %-12s calm %.4f | stress %.4f | DiD %.4f | shift p %.4f | symbols %d' % (
                k, v['beta_calm_mean'], v['beta_stress_mean'], v['did'], v['p_h2_stress_reveals'], v['n_symbols_used']))
        else:
            print('  %-12s %s' % (k, v['status']))
    print('  DiD with the state lagged 30 days:', res['placebo_30_days']['state_lagged_30_days'],
          '| led 30 days:', res['placebo_30_days']['state_led_30_days'])
    print('\nREADOUT (fixed text):')
    print(res['readout'])
print('SHA-256 of p7s_eval_results.json:', hashlib.sha256(raw).hexdigest())
print('downloads:', res['downloads'], '| minutes: %.1f' % ((time.time() - t0) / 60))
try:
    from google.colab import files
    files.download('p7s_eval_results.zip')
except Exception:
    pass
'''


def code_sha() -> dict:
    return {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in CODE}


def setup_cell() -> str:
    src = {n: (HERE / n).read_text(encoding="utf-8") for n in CODE}
    return SETUP.replace("__SRC__", json.dumps(src)).replace("__SHA__", json.dumps(code_sha()))


def notebook(md: str, code: str) -> dict:
    compile(code, "cell", "exec")
    return {"nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
            "cells": [{"cell_type": "markdown", "metadata": {}, "source": md.splitlines(keepends=True)},
                      {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": code.lstrip("\n").splitlines(keepends=True)}]}


def build(dev_sha: str | None = None) -> None:
    (HERE / "P7S_A1_Development_Colab.ipynb").write_text(json.dumps(notebook(DEV_MD, setup_cell() + DEV_RUN), indent=1))
    print("wrote P7S_A1_Development_Colab.ipynb")
    if dev_sha:
        assert len(dev_sha) == 64 and all(c in "0123456789abcdef" for c in dev_sha)
        code = setup_cell() + EVAL_RUN.replace("__DEV_SHA__", dev_sha)
        (HERE / "P7S_A1_Evaluation_Colab.ipynb").write_text(json.dumps(notebook(EVAL_MD, code), indent=1))
        print("wrote P7S_A1_Evaluation_Colab.ipynb for development outputs", dev_sha[:12])


if __name__ == "__main__":
    build(sys.argv[sys.argv.index("--dev-sha") + 1] if "--dev-sha" in sys.argv else None)
