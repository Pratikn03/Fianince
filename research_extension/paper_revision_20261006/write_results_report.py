from pathlib import Path
import json,hashlib,platform,csv
ROOT=Path(__file__).resolve().parents[2];REV=Path(__file__).resolve().parent
load=lambda n:json.loads((REV/'results'/f'{n}.json').read_text())
cb=load('coinbase_reanalysis');md=load('md_reanalysis');fee=load('fee_reanalysis');dep=load('depth_reanalysis');p=load('saved_panel_audit');d=load('dealer_reproduction');eq=load('equity_reanalysis')
s='''# Machine Markets — actual revision results

October 6, 2026. These are computed results, not promised future experiments. The review candidate retains all ten original study questions and includes a disposition of all 48 original pages. Its scientific gaps remain explicit. The original PDFs are preserved.

## Corrected primary Coinbase diagnostics

Past-observed 10-second flow, 300-second log-price EMA deviation, gap/date resets, five-horizon burn-in. Intervals are date-level Student-t summaries, not structural/causal learning confidence sets. Dates: April7–19,2021, including partial endpoints.

|Asset|Dates|Segments|Transitions|Q mean [95% CI]|S mean|Maximum fitted rho|Forward-flow Q mean|
|---|---:|---:|---:|---|---:|---:|---:|
'''
for a,v in cb.items():
 z=v['variants']['x_observed'];q=z['Q'];s+=f"|{a}|{z['n_days']}|{z['n_segments']}|{z['n_transitions']}|{q['mean']:.9f} [{q['ci95'][0]:.9f},{q['ci95'][1]:.9f}]|{z['S']['mean']:.9f}|{z['max_rho']:.9f}|{v['variants']['x_forward']['Q']['mean']:.9f}|\n"
s+='''
All raw-to-cache comparisons are exact for sec/mid/flow/duplicate indicators. Recovered Gemini timing results were rerun into this revision and match the saved agent JSON exactly; all1,995 tested past-minute buy sums per asset close after deduplication. This resolves local timing arithmetic, not provider authentication. Raw-return Q intervals span zero for all three assets. Four no-adaptation null families (60 repeats each) and both timing conventions show that small positive Q is not sufficient to identify adaptive learning. All24 nondegenerate sampling/window cells are saved, including negative/zero-spanning cells.

## Specification tests

|Asset|Moment rows|Rank|df|J statistic|Chi-square p|MD Q|
|---|---:|---:|---:|---:|---:|---:|
'''
for a,v in md.items():s+=f"|{a}|{v['n_moment_rows']}|{v['rank']}|{v['df']}|{v['J_stat']:.8f}|{v['p_chi2']:.9g}|{v['Q']:.9f}|\n"
s+='''
All three reject5%. Successful optimization does not reverse this specification finding. HAC reference inference and unrestricted innovations do not establish a causal learner model.

## Fee contrast — same saved192-row panel

|Outcome|Covariance|Coefficient|SE|df|p|95% CI|
|---|---|---:|---:|---:|---:|---|
'''
for outcome in ['Q','S']:
 for name in ['classical','asset_cluster','date_cluster']:
  v=fee[outcome][name];s+=f"|{outcome}|{name}|{v['beta']:.9f}|{v['se']:.9f}|{v['df']}|{v['p_t']:.7f}|[{v['ci95'][0]:.9f},{v['ci95'][1]:.9f}]|\n"
s+=f"\nQ date-cluster TOST at margin0.007: p={fee['Q']['equivalence_date_cluster']['p_tost']:.9f}; equivalence not established at5%. Descriptive asset-assignment rank fractions are Q={fee['Q']['placebo_rank_fraction']}, S={fee['S']['placebo_rank_fraction']}. Single treated asset, nonrandom assignment and possible spillovers limit causal interpretation.\n"
s+='''
The recovered event-study script assigns pooled DiD SE*sqrt(2) to individual dated gaps and literal +180% volume growth. Those operations do not establish the old monthly joint F/p or observed volume response. Correctly dated point contrasts are saved without fabricated inference.

## Saved Binance evidence

'''
s+=f"768 asset-days,96dates, {p['n_fitted_states']:,} fitted states. Maximum Q/S/rho identity error={p['max_identity_error']}. Qmean={p['pooled']['Q']['mean']:.9f}, date-block CI={p['pooled']['Q']['ci95_date_block']}; Smean={p['pooled']['S']['mean']:.9f}; positiveQ share={100*p['share_Q_positive']:.5f}%; maximumrho={p['max_rho']:.9f}. These are saved-derived legacy timing results, not raw reproduction or L3 measurements.\n"
s+='''
The original Table7 displayed matrix has radius1.002578519, not0.9612. That arithmetic is resolved. A generating joint fit, raw join and residual covariance are still not established after expanded searching; the empirical propagation and FEVD study gates stay open.

## Liquidity, equities and January secondary sample

Corrected first50,000 BTC-record conditional regression: calm flow slope0.626728431, wide-spread0.750974908, difference0.124246478, HAC SE0.218130659,p0.568951347. Residual SD ratio1.450627273. These dimensional slopes are not structural Q. Old62.7x scalar switching output is archived; it does not validate a bivariate structural S or an unsupported extremep.

The supplied equity counts are18308,39555,66862,71750,76466 (272941total), not five equal54588 samples. Every retained session is listed in the candidate. Source/provider stock mapping remains unauthenticated, and event-time fits do not share a physical sampling rate with crypto.

The January file covers January9–20,2023, including partial dates and gaps. It is quote/depth data with OFI, not authenticated executed trades or an untouched whole-month holdout. Primary Q remains positive in its date summary; Q30 is negative with a negative interval. The actual output file preserves all segments and counts.

## Simulation and mathematical results

All48 funded-dealer replay cells (400 seeds each;19,200paths) match the archived halt counts. Exact binomial intervals are generated. These results remain conditional on the preserved flow-moment calibration, which was not independently re-estimated.

At fixedrho=.85, nonnormal theta0,.5,2,8 yields M_C=1,1.383514147,5.337804416,21.301194083 and safe radii1,.722797090,.187342945,.046945725 for budget1. The nonzero examples peak at discrete time6. Constructed worst-direction shocks at the radius attain the budget; slightly larger shocks breach it.

The initial-shock theorem's repeated-input gap now has a separate proved linear induced-gain statement and computable stable-tail bound. A signed/nonnormal finite-horizon construction test attains its scalar-output gain and checks the tail certificate. Applying it to real execution still requires calibrated C,D,units and admissible bounded inputs. A scalar Gaussian surveillance lower bound is proved for its own experiment; it does not prove the old full noiseless control/state claim.

The historical crash source assigns reported feedback parameters and simulates E-mini price/depth. Its Treasury function returns constants. Those outputs are illustrative scenarios, not historical TAQ estimates. Protected E-mini scenarios also change depth/external liquidation, so they do not isolate interceptor effects.

## Expanded evidence search and why gaps remain

The text/archive search inspected14,804 items,10,570unique content hashes, with no archive-read errors. Exact scope/exclusions/hashes and candidate snippets are in `existing_evidence_search.json`. The agent's numeric-token matcher accepts unrelated tokens with sign/percentage rescaling; its “verified” label is not scientific lineage. Already withdrawn synthetic-IV results, earlier repairs and learner outputs were located and remain recovery leads.

T9 files/directories were listed, then became unavailable before content verification. Named January2025 archives are located but unverified; they are not automatically the original2021–2024 one-second input sample. The gap register distinguishes these from genuinely unestablished artifacts.

## Delivery and validation boundary

The full review candidate is49pages and retains all original scientific topics; it adds methods, complete dealer/session ledgers, repeated-input mathematics and the48-page disposition. It is a review candidate with unresolved raw/joint/causal/provider/external-review gates, not an externally validated submission. Ten revision tests pass. The final build and visual receipt records exact PDF/source hashes, page count and inspection scope. See `REVISED_PLAN.md`, `GAPS.md`, and `FULL_48_PAGE_AUDIT.md` for active work and the three user-requested expansion deferrals.
'''
(ROOT/'RESULTS_REANALYSIS.md').write_text(s)
inputs={'saved_panel_audit':'revise_evidence.py','fee_reanalysis':'revise_evidence.py','coinbase_reanalysis':'revise_evidence.py','mechanical_nulls':'revise_evidence.py','equity_reanalysis':'revise_evidence.py','md_reanalysis':'diagnostics.py','threshold_reanalysis':'diagnostics.py','transient_checks':'diagnostics.py','dealer_reproduction':'diagnostics.py','depth_reanalysis':'holdout_reanalysis.py','sampling_grid':'sampling_grid.py','raw_input_verification':'verify_raw_inputs.py','recovered_timing_check':'recovered_timing_check.py'}
rows=[]
for n,g in inputs.items():
 f=REV/'results'/f'{n}.json';rows.append({'output':str(f.relative_to(ROOT)),'output_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'generator':str((REV/g).relative_to(ROOT)),'generator_sha256':hashlib.sha256((REV/g).read_bytes()).hexdigest(),'scope':'See output-specific scope and gap register; named local result only'})
(REV/'claim_evidence_map.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Wrote actual results report and generator/output map')
