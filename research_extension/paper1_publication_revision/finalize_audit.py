"""Assemble the final verification record from completed machine-readable outputs."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
V=HERE/'validation'
grid=json.loads((V/'calibration_grid_results.json').read_text())
assert grid['complete'] and grid['replications']==3200
fresh=json.loads((V/'fresh_global_search_validation.json').read_text())
assert len(fresh['case_summary'])==5
duality=json.loads((HERE/'source/research_extension/duality/duality_results.json').read_text())
checks={
 'Gaussian mismatch identity simulation':duality['identity_max_z']<4,
 'low-information testing diagnostic':duality['min_error_with_Lambda_at_most_1']>=.25,
 'local truth-initialized recovery slopes':all(abs(v['slope']-v['predicted'])<.3 for v in duality['upper'].values()),
 'Bayesian cumulative log-loss examples':all(v['cumulative_excess_logloss']<=v['bound'] for v in duality['irrelevance'].values())}
assert all(checks.values())
(V/'incoming_claim_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
pdf=json.loads((V/'pdf_checks.json').read_text())
counts=[]
for name in ['revision_tests.xml','incoming_tests.xml','notebook_tests.xml']:
    root=ET.parse(V/name).getroot()
    cases=root.findall('.//testcase')
    assert all(c.find('failure') is None and c.find('error') is None for c in cases)
    counts.append(len(cases))
assert counts==[36,21,2]
text=r'''| Verification | Observed result | What it does not establish |
|:--|:--|:--|
| Repository Python suite | 707 passed; 15 skipped; 722 collected in the final consolidated checkout. | Economic validity or coverage of every numerical script. |
| Repository lint | Configured Ruff checks passed, with narrow documented exceptions for immutable or pasted-cell artifacts. | Notebook execution or statistical calibration. |
| Clean paper-suite reproduction | 28 tests passed; archived numerical outputs matched; all four legacy PDF text streams matched rebuilt sources; 76 reported numbers checked with zero mismatches. | New market-data collection or validation of every inherited claim. |
| Notebook schema review | Two checks passed; original defect preserved and separate review copy schema-valid with all code cells blocked. | An amended or executed registration. |
| New revision regression tests | 36 passed. | A completed real-data experiment. |
| Incoming-theorem regression tests | 21 passed, including non-unit noise and failure cases. | Full mechanization of the new theorems. |
| Paper 1 numerical checks | All 44 inherited assertions passed, including the slow runner; the 4 incoming assertions were evaluated against a fresh rerun and passed. | A universal rate theorem from fitted slopes; the inherited search assertion read an archived file. |
| Larger Lean project | Build passed, 9,069 jobs; 1,235 named declarations and 3,011 project constants audited. Standard foundational axioms only. | Full semantic coverage of the manuscript. |
| Independent core Lean project | Build passed; 439 theorems audited. | Additional independent manuscript theorems beyond the larger project's coverage. |
| New Lean revision | All 10 deterministic lemmas checked; standard axioms only. | Formal Gaussian KL, concentration, inverse-map or asymptotic proofs. |
| High-precision information | 6 family/size cases passed, with 60/90-digit agreement. | A passive-price likelihood or unrestricted global inverse. |
| Fixed-order forecast simulation | 192 simulations; fixed choices and evaluation, without evaluation-driven selection. | A uniform MSE rate or drift theorem. |
| Pooled moment certificate | 35 exact rational reconstructions; positive rank-deficient control passed. | Reliable rank selection from noisy data. |
| Archive-format synthetic pipeline | Both 30-market, 60-day worlds completed; full 200-draw gate and 2,000 bootstrap replications. | Statistical adequacy over a broad DGP class. |
| Frozen calibration grid | 3,200 replications completed; 7 of 12 non-descriptive criteria failed. | Clearance for a confirmatory empirical run. |
'''
text+=f"| Final manuscript PDF | {pdf['combined_pages']} pages: {pdf['main_pages']} main and {pdf['supplement_pages']} supplement. No undefined references, duplicate labels or overfull boxes in the final build. Selected pages visually inspected. | Author approval or independent peer review. |\n"
text+=r'''
The earlier repository run had 720 collected tests and 13 skips; the final consolidated checkout has 722 and 15. The passing count is 707 in both. The final skips concern unavailable external datasets or collection requirements, with exact details in `repository_final_test_summary.json`. No missing market data were replaced by synthetic evidence.

The full extended global search was regenerated separately: five $(K,D)$ cases, 12 configurations per case, and 400 starting points per solve. Its actual output was inspected rather than relying on the archived truncated search. The configuration counts with an apparent alternative are:

| $(K,D)$ | At $l^*$ | At $l^*+1$ |
|:--|--:|--:|
'''
for key,row in fresh['case_summary'].items():
    text+=f"| ({key}) | {row['with_other_solution_at_lstar']} | {row['with_other_solution_at_lstar_plus_1']} |\n"
diagnostics=fresh['solution_diagnostics']
if diagnostics:
    text+=f"\nThere were {len(diagnostics)} saved approximate alternatives. The largest distance from a relabelling was {max(x['distance_to_permutation'] for x in diagnostics):.6g}, and the largest moment residual was {max(x['residual'] for x in diagnostics):.6g}. All fell within the inherited near-collision diagnostic tolerance: **{fresh['all_apparent_solutions_within_legacy_near_collision_tolerance']}**. This tolerance is not a proof that approximate roots are identical. The block-Hankel proposition supplies the exact rank-conditional uniqueness argument separately.\n"
else:text+='\nNo approximate alternative passed the search tolerances. This is not a proof of uniqueness; the block-Hankel proposition supplies the exact rank-conditional argument separately.\n'
text+=r'''
The two archive-format worlds returned primary gains of approximately **−0.00516 percentage points** (feedback-only; irrelevant) and **+0.79201 percentage points** (informed; relevant). Both five-minute outputs returned the corresponding verdict. A3 gate frequencies were 0.99 and 1.00. These are synthetic results, not Binance observations.

The incoming detection simulation checked 64 pair-and-probe combinations. Its largest likelihood-identity deviation was 2.824 Monte Carlo standard errors; its fitted local weight-error slopes were −3.053 and −3.081. The two Bayesian examples had average cumulative excess log-loss 44.353 and 44.134 nats against a bound of 66.543. The script inputs (0.30, 0.60) and (0.44, 0.46) are **update rates** $\eta$, not persistence rates $r=1-\eta$. Both use $S=0.7$ and a class memory bound $\bar r=0.7$. These examples differ from the earlier fixed-order stationary experiment.

### Complete calibration diagnostic

Each row uses 200 independent worlds. “Gain” and “Mean estimate” below are percentage points of $R^2$; the margin is 0.5 points. I/R/U are irrelevant, relevant and inconclusive counts. The central interval between the two one-sided 90% limits has nominal coverage 80%. The coverage column compares that interval with the known **population-oracle** gain; it does not measure conditional fitted-learner coverage. Exact Wilson 95% Monte Carlo intervals for all verdict probabilities and coverage are in the JSON.

| Scenario | Gain | Mean estimate | I/R/U | Oracle coverage | Criterion |
|:--|--:|--:|:--|--:|:--|
'''
for row in grid['rows']:
    c=row['verdict_counts'];status='descriptive' if row['diagnostic_pass'] is None else ('pass' if row['diagnostic_pass'] else 'FAIL')
    text+=f"| {row['scenario'].replace('_',' ')} | {100*row['population_incremental_R2']:.2f} | {100*row['mean_estimate']:.4f} | {c['irrelevant']}/{c['relevant']}/{c['inconclusive']} | {100*row['central80_coverage']:.1f}% | {status} |\n"
text+=r'''
The frozen diagnostic criteria require the Wilson 95% lower limit for a correct verdict to be at least 0.80 at gains zero and twice the margin; at the margin, the upper limit for either decisive verdict must be at most 0.15. Half-margin cells are descriptive. The four margin cells and three twice-margin cells failed. This is an offline diagnostic, not a registered empirical result.

The failed oracle-boundary checks reflect a combination of finite learner error, dependence and inferential calibration; this design does not isolate a bootstrap size failure. The exact projection identity explains why an estimate of a fitted learner's gain cannot alone certify oracle irrelevance. No tuning was applied to remove the failed cells. Measurement-error and changing-volatility scenarios, an estimand-specific coverage result, and a complete statistical power-gate validation remain open. The candidate therefore remains unregistered and blocked from live execution.
'''
p=HERE/'Research_Audit.md'
audit=p.read_text().replace('For a stronger MSE result, Fix a class','For a stronger MSE result, fix a class')
assert '{{VALIDATION}}' in audit
p.write_text(audit.replace('{{VALIDATION}}',text))
(V/'verification_record.md').write_text(text)
print('Finalized the verification record from completed outputs.')
