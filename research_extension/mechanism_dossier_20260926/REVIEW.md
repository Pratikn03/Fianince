# AI-assisted review record and dispositions

These reviews are internal AI-assisted challenges, not independent human
economics, proof, authorship or ethics approvals. No correspondence was sent.

## Literature challenge

Reviewer task: 01a0e105-f0fe-7bb1-ab42-b4d0efaad53d (Fermat).
Scope: approved v0.12 model and nearest mechanism comparison; read-only.

The reviewer read CFL IA.6 prose on printed pp.17-19 and captions through p.21
using a publisher-generated signed supplementary link. The unsigned durable
path is the Oxford/Silverchair `hhag010_supplementary_data.pdf` associated with
DOI 10.1093/rfs/hhag010. The signed token is not stored here. No byte hash or
local copy of that reading was retained, so this dossier does not claim a
byte-identical archived literature source. The official article page supplies
the durable access route; a later unsigned fetch can fail.

Finding: substantial teaching/accommodation overlap, not novelty clearance.
The restricted ex-ante deployment choice and exact welfare calculation must be
judged for substantive economic value, not labeled a new mechanism by default.
Disposition: incorporated into the comparison matrix, proof scope, claim ledger
and production-training gate. The entire article/supplement was not read by
this reviewer. Further comparisons remain explicitly pending.

## Mathematical and economic challenge

Reviewer task: 01a0e105-f1cf-7df2-9f5a-b4837a70287a (Beauvoir).
Scope: v0.12 assumptions, counterexamples, finite mechanism and actual Lean
coverage; subsequently reviewed the new checker, proof and prediction protocol.

Findings incorporated:

- State-140 formulas and cost threshold are consistent under their assumptions.
- Common initial policy probabilities do not imply common learning-state
  behavior. Nearby shadow values can remove the effect.
- Existing Lean transitions/list sums/zero fixtures are not economic-kernel
  proofs or a formal certificate of this deployment equilibrium.
- Hoeffding's paired range [-2,2], radius and proposed numerical-validation
  precision calculation are consistent under ideal IID common-input sampling.

Final code/protocol review found two important reporting issues and one minor
input-validation issue. They were resolved as follows:

1. **Underspecified six-state screen:** now give the full predicate, six broad
   IDs and four strict both-null IDs in `PROOF_AUDIT.md`. States 188 and 189
   have pre-existing frozen focal gains; this is no longer hidden by the count.
2. **Missing manifest at review time:** finish artifact generation, then record
   and freshly verify `manifest.json`. A local hash record is not external
   preregistration. The review did not itself certify this later step.
3. **Warm-cache validation bypass:** a rational table cached under its numeric
   hash could cause a subsequently supplied integer table to bypass validation.
   Added a regression test, observed its failure, then moved validation outside
   the cached implementation. The 17-test suite passes; exact numerical outputs
   are regenerated separately under `verified/`. The initial source and outputs
   remain available and are not overwritten.

The reviewer reported no critical mathematical defect in the six reviewed new
files. It ran 15 read-only tests before the regression was added, excluding the
filesystem-writing test. Full dossier tests and the clean-copy checks are the
main agent's verification, not additional independent review.

## Still outside review completion

Human proof and priority review, formalization of the true transition kernel,
long-horizon robustness, trained-population evidence, actual market execution,
author approvals and publication acceptance are not completed by this packet.
