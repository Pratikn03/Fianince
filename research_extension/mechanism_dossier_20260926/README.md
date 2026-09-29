# Machine Markets: mechanism dossier

This dossier executes a bounded first pass through the five requested items,
without training, merging the research worktree, changing the manuscript, or
certifying novelty. Its strongest result is a transparent exact two-period
example of a learning-mediated private/social deployment difference.

## Read in this order

1. [Closest-literature comparison](LITERATURE_COMPARISON.md): corrected source
   records, actual reading scope and the substantial CFL accommodation overlap.
2. [Economic model, proof and counterexamples](PROOF_AUDIT.md): the approved
   information/timing contract; closed forms; a constrained deployment game;
   unfavorable initialization sensitivities and the formal-proof boundary.
3. [Locked prediction protocol](PREDICTION_PROTOCOL.md): a local numerical
   validation specification, not a completed trained-population protocol or
   retrospective preregistration.
4. [Machine-readable claim/evidence map](claims.json).

## Results and acceptance status

| Requested item | Delivered | Remaining limit |
|---|---|---|
| Closest literature | Eight-source comparison with primary links; focused CFL IA.6 and Brown-MacKay comparison; four historical registry corrections documented | Full relevant-paper/appendix priority review and independent human assessment remain open |
| Minimal model | Approved two-dealer early-versus-scheduled-refresh model restated with accounting and information | Not a calibrated market, unrestricted equilibrium or trained-agent population |
| Proof/counterexamples | Closed-form state-140 proposition and cost threshold; nulls, opposite-sign cases, initialization failures | Informal proof, not new Lean certification; generality and novelty not established |
| Exact computation | 4,096 rational profile/mask cells over all 256 stipulated states; separate calculator; 64 matched reference cells; clean-copy reproduction | Same-team differential checking, not external replication; 64 rather than all 4,096 cells compared to the old evaluator |
| Locked prediction | Numerical means, nulls, paired streams, fixed precision design and rejection rules | No new sampling/training executed; broad population protocol waits for the novelty/design gate |

The narrow grid contrast has 88 positive, 88 negative and 80 zero t=1 welfare
interactions. The sign is not universal, and these are not representative
frequencies of trained agents. State 140 was selected after inspection.

For that state, zero-cost early deployment increases focal expected profit by
1023/16000 and decreases gross total surplus by 87/8000. Both changes vanish
when rival learning is frozen. With both deployment costs set to 1/20, the unique
equilibrium is (early,wait), the feasible planner chooses (wait,wait), the
focal net gain is 223/16000 and the welfare gap is 487/8000. All units are
dimensionless model payoff units. Separate customer/rival payoffs are retained.

**This does not establish a new teaching mechanism, damaged estimate accuracy,
long-run fragility, or a field-defining contribution.** The literature overlap
and unfavorable initial-state sensitivities are substantive findings, not
publication disclaimers to be removed after favorable simulations.

## Source and preservation boundary

Delivery checkout:
`/Users/pratik_n/Downloads/Machine_Markets_Master_Release`, baseline commit
`b5f0bdc`, branch `codex/paper-evidence-repair-20260926`.

Reference model checkout:
`/Users/pratik_n/.codex/worktrees/machine-markets-wp00-wp01/Machine_Markets_Master_Release`,
commit `c958188654f6777c63168c6d13d5c29e042606ec`.

The reference worktree contained pre-existing untracked studies/results. They
were neither merged nor edited. Only this new dossier directory was added to
the delivery checkout. No existing `.tex`, PDF, training checkpoint or historical
result was changed; no commit, push, external correspondence or submission made.
Reference source hashes are saved in `verified/exact_results.json` and `manifest.json`.
Accepted outputs are in `verified/`. Initial outputs at this directory's root
are retained with `snapshots/exact_audit_initial.py`; they predate the reviewed
cache-validation repair. Their numerical results are unchanged.

## Reproduction

Use Python 3.11 from the delivery repository root. The new checker itself needs
only the standard library. Outputs are create-only: choose unused filenames.

```sh
PYTHONDONTWRITEBYTECODE=1 python3.11 -m unittest discover -s research_extension/mechanism_dossier_20260926 -p 'test_*.py' -v

PYTHONDONTWRITEBYTECODE=1 python3.11 -m research_extension.mechanism_dossier_20260926.exact_audit --output /tmp/mm-grid-fresh.json --reference-root /Users/pratik_n/.codex/worktrees/machine-markets-wp00-wp01/Machine_Markets_Master_Release

PYTHONDONTWRITEBYTECODE=1 python3.11 -m research_extension.mechanism_dossier_20260926.witness_audit --output /tmp/mm-witness-fresh.json --reference-root /Users/pratik_n/.codex/worktrees/machine-markets-wp00-wp01/Machine_Markets_Master_Release
```

The optional reference root imports the older evaluator only for differential
checks, never to compute the separate calculator's answers. Without it, exact
results still reproduce, but reference comparison is explicitly `not_run`.
The checker integrates only H=1/H=2; terminal expectations are cached by full
action laws, not by lossy earlier state merging. No confidence intervals are
attached to exact enumeration.

Fresh verification in this pass:

- 17 new dossier tests passed; tests first failed before implementation.
- 381 existing current-release pytest tests passed.
- Final combined current-release plus dossier run: 398 tests passed.
- 98 native scientific tests and 6 release-tool tests passed; full native logs
  are under `verification/native/`.
- 173 v0.12 reference-worktree tests passed.
- 48 preselected reference comparisons plus 16 state-140 comparisons matched
  exactly. Closed forms matched 16 epsilon/alpha boundary/interior checks.
- A temporary source-only copy reproduced all 4,096 grid cells and the full
  witness's semantic results exactly; reference-path metadata is intentionally
  different when the reference comparison is omitted.

These counts establish their named software checks, not scientific novelty or
outside replication. The earlier statistical release seal and main PDF were
not rebuilt or resealed here. A syntax error during new witness implementation
was fixed before successful tests; no failed intermediate result was published.

## Review and next decision

Two AI-assisted reviewers challenged (a) closest-literature overlap and
(b) proof/counterexample/formal scope. A final code/protocol review examines the
new dossier; review outcomes are recorded in `REVIEW.md`. No human reviewer or
author approval is inferred from these automated reviews.

The next scientifically useful decision is whether the limited-information,
one-shot deployment restriction supports a contribution beyond known
accommodation. If not, keep this as a benchmark rather than funding a larger
training campaign around a renamed mechanism. Formalizing the actual economic
kernel and this bounded proposition is a separate concrete work item; the old
Lean scaffold is not evidence that it has already been done.
