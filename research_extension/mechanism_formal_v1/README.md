# Model-derived formalization of the finite deployment example

This package continues the approved exact economic model without changing the
62-page main paper, the sealed mechanism dossier, or the older Lean scaffold.
It addresses a specific formal gap: the payoff certificates here are computed
from actual quotes, customer acceptance, tied fills, gross rewards, selected-
action learning, and scheduled refresh. They are not imported payoff tables.

## Economic scope

Two dealers, asks {2,4,6}, six IID asset-value/customer atoms, two periods,
epsilon=1/10 and alpha=1/2. The stipulated initial state is grid state 140 from
the prior **post-hoc** search. Dealer 0's learning is frozen; dealer 1 learns in
the central comparison. Owners know the law and choose early or scheduled
refresh once; learners receive only their own realized gross rewards.

The model has no inventory, funding, liquidation, execution calibration, neural
training, or systemic-loss target. Exact arithmetic provides no sampling
confidence interval and establishes no prevalence in trained populations.

## What the formal declarations state

| Claim | Lean declaration | Scope |
|---|---|---|
| Trading payments cancel in total surplus | `settlement_conserves` | Every legal quote pair and rational asset/customer value |
| Resource costs are deducted once and preserve accounting | `costs_conserve` | Every accounting-consistent outcome and cost pair; economic use assumes nonnegative costs |
| Early release preserves shadows; frozen updates preserve them; refresh uses shadows | `release_preserves_shadow`, `frozen_shadow`, `scheduled_refresh` | All states under these fixed definitions |
| Changing a rival's reward changes its next policy | `accommodation_path` | The specified concrete trade event |
| Gross focal gain = 1023/16000 | `witness_gross_private_gain` | Default state/parameters, H2, rival learns |
| Gross welfare change = -87/8000 | `witness_gross_welfare_loss` | Same comparison; payments included as transfers |
| Both focal-profit and welfare contrasts vanish when rival learning is off | `frozen_rival_null` | Does not assert all participant payoffs are unchanged |
| Unique pure equilibrium is (early, wait); unique same-menu planner choice is (wait, wait) | `unique_pure_equilibrium`, `unique_planner` | Costs (1/20,1/20); all four profiles and unilateral deviations |
| Net private gain = 223/16000; planner–equilibrium gap = 487/8000 | `costly_private_gain`, `planner_equilibrium_gap` | Same costed finite game |
| A small negative common shadow shift removes both contrasts despite equal initial action laws | `initialization_fragility` | Rival shadow (-1/100,-1/100,-1/100); other inputs fixed |
| Welfare changes through low-ask allocation; ask 2 is statically dominated by ask 4 | `stage_welfare_identity`, `low_ask_dominated` | This finite economic law, not general market welfare |

The explicit pure-equilibrium certificate is not a formal mixed-equilibrium
classification. The prior informal dominance argument remains separate.

## Trust boundary and coverage still pending

`Model.lean` and `Evaluator.lean` define the executable economy. They do not
depend on the result certificates. `Certificates.lean` and `Proofs.lean` use
ordinary proof terms and kernel reduction (`decide +kernel`). The distinct
`Export.lean` executable supplies fixtures; running that executable alone is
not a proof. Every theorem in an imported local module is discovered from Lean's
elaborated environment and receives a transitive dependency audit using the same
`collectAxioms` machinery as `#print axioms`. Auxiliary/generated declarations
are included; source indentation and namespaces do not define coverage.
The local modules are additionally replayed through Lean's kernel checker.
Standard allowed dependencies are propext, Classical.choice, and Quot.sound.
This is not a second independent proof-assistant implementation.

The Python bridge compares all 16 zero-cost profile/mask cells, four costed
profiles, and 54 settlement branches against the separately implemented,
hash-verified dossier calculator. **Tested cross-language agreement is not a
universal proof of Python correctness.**

Not formalized here: continuous epsilon/alpha formulas, arbitrary-horizon
history/recursion equivalence, general transition normalization for all states,
all 4,096 grid cells, empirical validity, or novelty. Only one initial branch-
mass fixture is formally certified. These omissions must not acquire a complete
status because the bounded certificate builds.

## Reproduce

From the release repository, using the existing pinned Lean 4.29.1 toolchain:

```sh
python3.11 -m research_extension.mechanism_formal_v1.run_verify \
  --lake /Users/pratik_n/.elan/toolchains/leanprover--lean4---v4.29.1/bin/lake \
  --output /tmp/machine-markets-formal-new-run --clean
python3.11 -m pytest -q research_extension/mechanism_formal_v1
```

Choose a new output path on each run. Existing destinations are refused. Clean
builds copy the formal sources/configuration to a new temporary directory, with
no previous build products. Original and executed source inventories/hashes are
checked before execution, between verification stages, and before acceptance.
The Python dossier is pinned to the previously approved manifest's digest; an
empty or substituted manifest cannot establish preservation. That dossier remains
an explicit reference input. Saved `report.json` records hashes, failures, audit
coverage, toolchain and bridge results; inspect `passed`, not mere file presence.

See `LITERATURE_CHALLENGE.md` for the narrower contribution assessment. The
nearest-work gate remains open: established strategic teaching explains the
reward channel. A correct finite welfare example is progress, not proof that
the paper is field-defining. No further training or manuscript integration is
represented as completed by this package.

`verification/first` and `verification/clean_initial` retain pre-review runs.
Their economic numbers were reproduced, but their verifier had three integrity
gaps documented in `REVIEW.md`; do not use those runs as final integrity evidence.
The final accepted run is identified in `STATUS.md` after the fix verification.
