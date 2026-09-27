# Second evidence repair: fixed design before corrective reruns

This is a post-hoc correction, not a preregistration or independent replication.
The purpose is to repair implementation and reporting against existing mathematical
contracts, not to select favorable outcomes. Historical results are preserved.

## Starting evidence

- Checkout: Downloads/Machine_Markets_Master_Release, branch
  `codex/paper-evidence-repair-20260926`; HEAD `1ec937cc512a12f8a36e887c20ce721bf675d87e`.
- Starting files (including pre-existing uncommitted work) archived outside the
  repository in `/Users/pratik_n/Downloads/Machine_Markets_second_repair_izLlqU/starting-evidence.tgz`.
  SHA-256 `b0e9d785ca097a502400f37f78991f856c2ecf01cb8ac17a9be49fba784f4c9f`.
- An initial tar command named a nonexistent requirements.txt and exited nonzero;
  all existing requested directories were verified in the resulting archive.
  Actual runtime/artifact requirements files are copied alongside that archive.
- Earlier correction seal passed for 111 files before this repair. It remains
  historical; it will not be silently refreshed after changing those files.

## Fixed analysis plan

1. Comparator grid: the original 120 cells (S in .70,.82,1,1.03,1.18;
   slow rate .002,.02,.10; R=128,1024; probe=1,4; H=24,64), five independent
   panels per cell. Seed=20260924+1000*cell_index+replicate. All five estimators
   receive the same corrected response observations x1 through x(H+1).
   Oracle parameters enter evaluation only, not estimator initialization.
2. Conic budget sweep: S=.60,.82,1.25, five original budgets from 128 to
   32768, 20 draws per cell, H=24. Two distinct experiments (300 panels each):
   known covariance/chi-square region and independent Wishart-estimated
   covariance/F region, with matched Gaussian coefficient noise.
   These coefficient experiments are not reconstructed real-market records.
3. Response-region calibration: 20,000 draws per covariance mode, p=25,R=128,
   seed310001. Report empirical coverage, exact 99% binomial intervals, and
   the fixed absolute tolerance .01 around .95. This validates the sampling
   pivot in its declared simulation, not the structural interval solver.
4. Output-error diagnostic: H=24,R=1024,seed20260924; 100 independent noisy
   panels each for matched/misspecified generators (C2/C4). C1/C3 are one
   deterministic case each, not 100 pseudo-replicates. Preserve every fit,
   optimizer/bound status, profile interval, sandwich interval and unavailable
   fallback. Conditional coverage must state its availability denominator.
5. Funded scenario: 100 paired seeds under existing settings. Do not change
   trajectories. Add effective transition matrices, spectral radii and event
   definitions. The nominal S=.82 scenario has effective S=1.22 and rho>1;
   it cannot establish a stable-system safety counterexample. Capacity
   multipliers do not change initial equity, and recorded constraint hits do
   not permanently halt subsequent reversing fills.

## Interpretation and acceptance

- Keep all attempted panels, errors, invalid and infinite intervals. No
  NaN-as-coverage, dropping failed fits, or finite-only mean mislabeled as an
  unconditional mean. Do not pool separately defined studies.
- Conic endpoints are numerical outer-relaxation candidates. Both dual
  objectives and solved-cut bookkeeping are repaired, but full outward
  constraint construction is unverified. Official labels are withheld
  (`certified=False`); numerical candidate labels are separate diagnostics.
- Output-error intervals are local/asymptotic, not globally guaranteed profile
  sets or finite-sample structural certificates.
- Publication statements are revised after results, not tuned to them. A
  failed check is retained and narrows the claim. No new model training.
- Each CLI stage requires a new output directory and stores its source hashes
  before and after execution. Changed-source runs are retained but rejected.
- Generate paper tables/figures from accepted outputs; rerun tests and clean-copy
  numerical reproduction; compile and visually inspect PDFs. Record fresh
  checks in a new scoped receipt. Original strict-release failures stay visible.
- Human independent review, novelty priority, and real execution validation
  remain external/open scientific gates, regardless of test outcomes.

## Commands

Use Python3.11, with OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and
VECLIB_MAXIMUM_THREADS=1. The module
`research_extension.evidence_repair.statistical_repair` accepts `--stage`
`grid`, `sweep_known`, `sweep_estimated`, `calibration`, `diagnostic`, or
`funded`, and mandatory `--output-dir`. Grid permits `--workers 4`.
Production outputs use `research_extension/outputs/statistical_repair_20260926/`.
Smoke outputs are separate and never treated as production evidence.
