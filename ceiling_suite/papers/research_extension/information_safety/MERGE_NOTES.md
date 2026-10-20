# Merging with `Pratikn03/Fianince` (branch `paper2-information-safety`, commit 73dd4de)

The repository has its own `research_extension/information_safety/` package with the blueprint's file names. It implements a
different numbering ("Theorems A–G", `thm:flagship_*`) from an earlier draft of Paper 2. This package matches the current
paper (Theorems thm:window, thm:certcost, thm:robustguard, thm:disclosure, thm:venuebb; Propositions prop:twoworld,
prop:hotelling, prop:venue, prop:probe; Lemmas lem:sound, lem:certnum).

| Repo module | This package | Recommendation |
|---|---|---|
| `data_compatibility.py` (`compatible_feedback_bounds_d0/d1/general`, "Theorem B/C") | exact Markov–Krein bounds plus certified endpoints | replace: the repo's general bound is not the sharp interval the paper states |
| `uncertainty_calibration.py` (Mahalanobis moment box, "Theorem D") | O1 certificate, t-certificate, Hotelling region | replace; keep the repo's moment-box idea only if a section uses it |
| `robust_admission.py` ("Theorem E", balance-sheet global solve) | closed form, venue mode, interval branch and bound | replace |
| `economic_ledger.py` (8-method horse race T11, T10 "external validation") | rebate T12 and balance-sheet step | replace; the repo's T10/T11 are not in the current paper |
| `exact_rational_witness.py`, `price_response.py`, `risk_gain.py`, `adversarial_paths.py`, `disclosure_experiment.py`, `monte_carlo_coverage.py` | same roles, current-paper numbers | replace |
| `model_contracts.py` (dataclasses `PositiveMemoryMarket`, `ObservationContract`, ...) | functions plus a `CONTRACTS` dict | either; the dataclasses are nicer for users, the numbers must come from this package |
| `__init__.py` (package with relative imports) | flat modules | add an `__init__.py` here if the repo needs package imports |
| `tests/test_balance_sheet.py`, `test_confidence_coverage.py`, `test_exact_witness.py`, `test_two_world_bound.py` (duplicates) | the ten test files listed in README | drop the duplicates |
| `results/flagship_upgrade_results.json` | `results/*.json` | replace; the old file's numbers do not match the paper |

Also fix in the repo (from the Lean review): the README badge ("170 theorems verified"), the committed `axiom_audit.jsonl`
(it contains a build error, not an audit), and the Lean statements of Theorems A–G, which assume their key steps.
