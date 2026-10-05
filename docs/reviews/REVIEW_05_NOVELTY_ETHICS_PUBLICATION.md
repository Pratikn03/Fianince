# Review 5 — novelty, authorship, ethics, and publication readiness

## Scope

This pass checked the manuscript's priority language, source rights, human
contribution record, responsible-release obligations, and venue acceptance
claims against the current repository state.

## Findings

1. **Critical — no independent novelty review is complete.** The topic has
   close predecessor areas in finite-sample system identification, data
   informativity, order-flow/limit-order-book analysis, adaptive quantitative
   trading, and AI-in-finance market simulation. The current branch must not
   label its combination novel without a documented human comparison.
2. **Critical — authorship and AI-use decisions are human gates.** The
   repository can provide a contribution template and disclosure draft but
   cannot assign authorship, consent for attribution, or attest to institutional
   ethics review.
3. **High — data rights and venue acceptance are not inferred from public
   downloadability.** Exchange archive terms, redistribution permissions,
   retention, and venue-specific requirements require human/legal/venue review.
4. **Medium — a generated PDF is not publication acceptance.** No editor or
   venue decision exists in this checkout.

## Implemented remediation

- Added `docs/NOVELTY_POSITIONING.md` and a primary-source predecessor matrix
  with explicit “human verification pending” fields.
- Added `review_packets/HUMAN_AUTHorship_ETHICS_REVIEW.md` with consent,
  contribution, AI-use, data-rights, and ethics questions.
- Added `submission/PUBLICATION_PACKET.md` with claim, artifact, rights,
  review, and venue checklists.
- Kept all manuscript language scoped and marked authorship/review status
  pending.

## Residual status

Independent human novelty, authorship, ethics, rights, and publication review
remain pending. No acceptance, authorship assignment, or ethical approval is
claimed.
