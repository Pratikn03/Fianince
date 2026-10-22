# Thesis completion tasks — instructions for an AI coding agent

You are working in the repository `Pratikn03/fianince`. Your job is to complete the open items of the thesis
**"From Human Markets to Machine Markets — Certify, Don't Identify: Safety and Identification in Markets with Adaptive Trading Agents"**
(`thesis/thesis.pdf`), a three-paper thesis: Paper 1 (Chapter 2), Paper 2 (Chapter 3) and Paper 3 (Chapter 4), with an
introduction (Chapter 1) and a conclusion (Chapter 5). **The thesis stays at three papers and stays in finance and
theory: do not add chapters on power grids, vehicles or other engineering domains.** Read this whole file before starting. Do the tasks in the order of Section 4. After every
task, run the checks in Section 3 and report in the format of Section 6.

---

## 1. Where things are

| What | Path |
|---|---|
| Thesis sources written for the thesis | `thesis/ch1_intro.tex`, `ch4_paper3.tex` (Paper 3), `ch5_conclusion.tex` (includes the evidence program), `appA_status.tex`, `bib_new.tex` |
| Thesis main file | `thesis/thesis.tex` |
| Chapters 2 and 3 (Papers 1 and 2) | generated from the papers by `thesis/make_chapters.py`; **never edit `ch2_paper1.tex` or `ch3_paper2.tex` by hand** |
| Paper 1 sources | `ceiling_suite/papers/paper1/p1_*.tex` (assembled by `ceiling_suite/papers/build_p1.sh`) |
| Paper 2 sources | `ceiling_suite/papers/paper2/p2_*.tex` (assembled by `ceiling_suite/papers/build_p2.sh`) |
| Journal versions | `ceiling_suite/papers/versions/build_versions.py` → `Paper1_QE.pdf`, `Paper2_JF.pdf` |
| Mirrors of the paper sources | `ceiling_suite/paper1/`, `ceiling_suite/paper2/` (keep identical to `ceiling_suite/papers/paper*/`) |
| Number verification | `ceiling_suite/papers/verify_paper_numbers.py` |
| Full reproduction (what CI runs) | `SKIP_LEAN=1 sh reproduce_paper_suite.sh` |
| Lean 4 project | `research_extension/current_manuscript_lean_20261008/` (namespace `CurrentMM`) |
| Pre-registration examples | `ceiling_suite/papers/results_archive/outputs/p2*res/prereg/` |
| Build the thesis | `sh thesis/build_thesis.sh` |

Status tags used in the thesis (macros in `thesis/thesis.tex`): `\Proved`, `\ProvedIn{...}`, `\Target`, `\Conj`,
`\Pending`, and the box `\pendbox{title}{text}`.

---

## 2. Rules you must never break

1. **No invented numbers.** Every number that appears in a `.tex` file must be written by a script into a
   result file (JSON/CSV) committed to the repo, and must be added to `verify_paper_numbers.py` (papers) or to a new
   `thesis/verify_thesis_numbers.py` (thesis). If a script cannot produce a number, the text says so.
2. **Status tags are earned, not edited.** Change `\Target` or `\Conj` to `\Proved` only when (a) the full proof
   is written in the thesis, (b) a numerical check script confirms the statement on random instances, and (c) where
   the statement is finite-dimensional or algebraic, a Lean 4 proof compiles (Section 4, task L1). If a proof
   attempt fails, **do not weaken the statement silently**: keep the tag, write what was proved, and add the gap
   to the open problems in `ch5_conclusion.tex`.
3. **Pre-registration protocol for every empirical or simulation test.**
   - Write the specification JSON (hypotheses, data, dates, primaries, pass rules, correction, code version).
   - Compute its SHA-256, create an unlock counter file set to 0.
   - **Commit and push the specification alone** (one commit, no results, no data). GitHub records the push time.
   - Only then download or record test data. Open the test set once; increment the counter.
   - Report the outcome against the registered pass rule, whatever it is. A failed primary is reported as failed.
   - A follow-up test designed after a failure must say so in its specification and in the text.
4. **No secrets in files.** API keys, tokens and passwords never go into the repo, notebooks, logs or result files.
   Read them from environment variables or Colab Secrets.
5. **Data access.** Use only data you are allowed to access from your location. Do not use VPNs, proxies or
   other means to get around geographic restrictions or terms of service. If a source is unavailable, use the
   fallback named in the task and say so.
6. **Co-authored chapters.** Chapters 2 and 3 are papers with co-authors. Change their sources only to fix a
   documented error; record every such change in `thesis/CHANGELOG.md` with the reason.
7. **Git.** Pull before you start (`git pull --ff-only origin main`); another session also pushes to `main`.
   Make small commits with clear messages. Never force-push. Never rewrite history.
8. **Honest prose.** Write claims at the strength the evidence supports. Use "consistent with" for exploratory
   results, "we find" for registered passes, "fails" for registered failures.

---

## 3. Checks after every task

```sh
git pull --ff-only origin main
sh thesis/build_thesis.sh                      # must print "Output written" with no "!" errors
cd ceiling_suite/papers && python3 verify_paper_numbers.py && cd ../..
SKIP_LEAN=1 sh reproduce_paper_suite.sh        # must end with "done: all checks passed"
ruff check .
```

If a task touches Lean: `cd research_extension/current_manuscript_lean_20261008 && lake build && lake env lean AxiomAudit.lean`.
The word `admit` (and `sorry`) must not appear anywhere in Lean files, including comments.

---

## 4. Tasks, in order

Each task lists: goal, steps, files, acceptance criteria. Do not start a task until the previous one passes its
checks, except where marked *parallel*.

### Part A — Theory (highest value)

#### A1. The matching lower bound — Theorem `thm:dich`(iv) in `ch4_paper3.tex`
- **Goal.** Prove: for `g(r) = Σ a_t r^t` with coefficients of eventually constant sign and at most polynomial
  growth, `N_cert(ε) ≥ c σ² A_g(c′ T_g(ε)) ε⁻²` under the reset contract (Assumption `ass:reset`).
- **Plan given in the thesis.** Combine (1) truncation necessity (part (ii), already proved) with (2) a Le Cam
  two-point bound in which the two economies are moment-matched up to order `T−1` (Gauss vs Gauss–Radau
  quadrature pairs of Chapter 2, Theorem `p1:thm:kcohort`) and their tap differences align with the coefficient
  vector `(a_0,…,a_{T−1})`.
- **Steps.**
  1. Write the proof in a new subsection "Proof of part (iv)" after the existing proof.
  2. Write `thesis/checks/check_dich_lower.py`: for `g = 1/(1−r)`, `g = r^m`, `g = (1−βr)^{-1}`, construct the
     pairs numerically, compute the KL divergence and the functional gap, and confirm the bound's scaling in `ε`
     (fitted log–log slopes within 10% of theory). Save `thesis/checks/R_dich_lower.json`.
  3. If the full statement fails, prove the strongest version you can (for example for `a_t ≥ 0` only), state
     exactly that version, keep `\Target` on the rest.
- **Acceptance.** Proof written; script passes; tag changed only per Rule 2; Corollary `cor:cases`(e) updated if
  the logarithmic rate now follows formally.

#### A2. Sharp multi-asset bound — Proposition `prop:multiasset` (*parallel with A1*)
- **Goal.** For positive cross-impact (all entries of `A`, `K`, `Q_i` non-negative), prove the sharp bound
  `sup_t ||x_t||_∞ ≤ w̄ ||(I − A − K Σ Q̄_i S_i)^{-1} K||_∞` (spectral radius below one), the multi-asset
  analogue of `S`.
- **Acceptance.** Proof (comparison principle for positive systems), numerical check, tag updated.

#### A3. Strategic agents — Conjecture `conj:strategic` in `ch4_paper3.tex`
- **Goal.** Prove existence of a guard-consistent equilibrium and safety of the guard in every equilibrium, or
  find a counterexample.
- **Steps.** Formalize the agents' problem (choose `q_i ∈ [0, q̄_i]` to maximize expected profit minus a convex
  cost, given an admission rule that throttles when certified `Φ` exceeds `Φ_max`). Use Theorem `thm:sector`
  (safety depends only on `Φ̄`) and a fixed-point argument (Kakutani or Tarski if best responses are monotone).
- **Acceptance.** Theorem or counterexample; if neither in reasonable effort, write the partial result and keep
  `\Conj`.

#### L1. Lean formalization of the new proved results
- **Goal.** Formalize in Lean 4 + Mathlib, in the existing project:
  1. the induction of Theorem `thm:sector` (robust safety bound) for finitely many cohorts over a finite horizon;
  2. Corollary `thm:lifetime`;
  3. the bias/variance arithmetic of `thm:dich`(i) (deterministic part: bias ≤ tail, interval half-width ≤ ε).
- **Rules.** Namespace `CurrentMM`; add theorems to `CurrentProofs/`; register them in the manifest the CI
  uses (`CEILING_SUITE_LEAN_PROOF_MANIFEST.json` / `MANUSCRIPT_COVERAGE.*`); no `sorry`/`admit`.
- **Acceptance.** `lake build` and the axiom audit pass in CI; the thesis status register cites the Lean names.

### Part B — Evidence (do the pre-registration commits first, then wait for data)

#### B1. Test E1: certificate against ground truth — Chapter 5, Section `sec:ev_e1`
- **Data.** CFTC Commitments of Traders (public CFTC reports) for the eight markets of Chapter 2, Section
  `p1:sec:cot`; Binance USD-M `metrics` files (public `data.binance.vision`) for the 30 perpetuals of Section
  `p1:sec:disc_data`. Use dates **not used by any earlier part** (check `results_archive` manifests).
- **Primaries (from the thesis).** P1: the price-only certificate interval for `Φ` overlaps the class-composed
  interval `Φ_class = Σ_c ŵ_c/(1 − r̂_c)` in at least 75% of markets. P2: price-only intervals for individual class
  memories are at least 10× wider than class-based ones. Holm correction across the two.
- **Steps.** Spec → hash → push alone (Rule 3) → download → run once → `thesis/evidence/E1_results.json` →
  replace the `\pendbox{E1}` with a paragraph and one table → add numbers to `verify_thesis_numbers.py`.

#### B2. Test E2: prospective mechanism test — Chapter 5, Section `sec:ev_e2`
- **Preferred data.** Binance's public forced-liquidation stream (at most one liquidation per symbol per second,
  so a sample), recorded after the specification is pushed, for at least three months, with order-book depth from
  `data.binance.vision`. **First check that the stream is accessible from your location. If it is not, do not use
  a VPN or proxy (Rule 5).**
- **Fallback (allowed everywhere the public archive is).** A prospective-in-time test: register now, then use only
  daily archive files for dates **after** the registration push (open-interest contractions with adverse moves as
  the liquidation proxy of Part 22, plus the persistence measures of Part 25).
- **Primaries.** P1: six-hour `Ĉ3` forecasts next-hour (sampled) liquidation volume beyond the volatility, impact
  and lagged-liquidation baseline. P2: adding realized next-hour liquidation volume removes at least half of `Ĉ3`'s
  excursion forecasting gain.
- **Deliverables.** `thesis/evidence/E2_recorder.py` (robust to disconnects, writes daily compressed files,
  logs gaps), spec in `thesis/evidence/prereg/`, results JSON, updated Section `sec:ev_e2`, and the same text
  added to Paper 2's tests section as a new Part with its own subsection.

#### B3. Multi-agent learning simulation — `ch4_paper3.tex`, Section `sec:bl_ai` (*parallel*)
- **Design.** Reinforcement-learning trading agents in the price model of Chapter 3; certify at time 0; let agents
  keep learning at rates `γ ∈ {0.001, 0.003, 0.01, 0.03}`; measure when the realized worst-case loss first exceeds
  the budget.
- **Primary.** Realized certificate lifetime is at least the bound of Corollary `thm:lifetime` in every run, and
  within a factor of three of it in at least 75% of runs.

### Part C — Writing and integration (after A and B)

#### C1. Update the thesis
- Replace every resolved `\pendbox` and `\Target` per Rules 1–2; update `appA_status.tex`, the status table in
  `ch1_intro.tex`, the abstract and the open problems in `ch5_conclusion.tex`. Keep the abstract under 400 words.
#### C2. Verify the bibliography of the new chapters
- Check every entry in `thesis/bib_new.tex` against the publisher's page (authors, year, volume, issue, pages).
  Fix errors. Add DOIs.
#### C3. Final consistency pass
- Every theorem referenced in Chapters 1, 4 and 5 exists and says what the reference claims.
- No sentence claims more than its tag allows.
- `sh thesis/build_thesis.sh` gives no warnings other than float-placement notes.

#### C4. Paper 3 as a stand-alone journal paper (after A1)
- Build `paper3/` from `thesis/ch4_paper3.tex`: its own title page, abstract (about 150 words), introduction
  that summarizes Papers 1 and 2 in one paragraph each and cites them, the theory sections, proofs in an appendix,
  and its own references. Target: Operations Research, Mathematics of Operations Research or Management Science.
- Keep `thesis/ch4_paper3.tex` as the single source of the shared text (generate the paper from it, as
  `make_chapters.py` does in the other direction), so the two never drift apart.

### Part D — Human tasks (the agent must not do these; list them in the report)
- Co-authorship statement in `thesis/thesis.tex` (needs the co-authors).
- Permission from co-authors to include Chapters 3 and 4.
- Decision on journals for the papers and on submitting the thesis.

---

## 5. Definition of done (the "highest ceiling" version)

The thesis reaches its ceiling when all of the following hold:
1. `thm:dich`(iv) proved (or its strongest provable version proved and the rest stated as an open problem).
2. A2 or A3 proved (or A3 settled by a counterexample).
3. L1 formalized and passing CI.
4. E1 run and reported (pass or fail).
5. E2 run and reported (pass or fail).
6. B3 run and reported.
7. The thesis still has exactly three papers, and all checks of Section 3 pass on `main`.

A pass on E1 and E2 is not required for "done"; honest reporting is.

---

## 6. Report after each task

Write a short entry in `thesis/PROGRESS.md`:

```
## <task id> — <date>
Status: done | partial | failed
What changed: <files>
Result: <one paragraph, with numbers that appear in result files>
Checks: build ok/failed; verify ok/failed; reproduce ok/failed; ruff ok/failed; lean ok/failed/n.a.
Open issues: <list>
```
