# Paper 1: status against the full work plan (13 November 2026, afternoon)

Written by an AI system for the authors; judgement, not independent review.

## Done

| Stage | What was done |
|---|---|
| 0.2 | Full Lean build passes (9,069 jobs). Receipt regenerated: build and strict axiom audit pass, 1,235 named declarations. The audit time limit in `verify_formalization.py` is now set by `VERIFY_TIMEOUT` (default 240 s; this machine needed more). |
| 1 | Headline adopted: the intervention is the unit of analysis; identification and market-wide questions separate without bound (new Corollary `n:sep`). The calibration (more than 4,000 years of daily prices) was already in the theory version and stays in the abstract and introduction. |
| 2 | New main-text paragraph "When impact is mechanical": where the model applies, and that with a rational market maker prices reveal less, not more. Classical tools named (Blackwell, Le Cam, data informativity). New framing Proposition `n:interv`, stated as a restatement of sufficiency plus a total-variation bound, not as a new theory. |
| 3 | New focused version (`paper1_focus`): main text 21 pages, supplement 94 pages (from 107). Cascades, insiders, and nonlinear and learning traders moved to a 19-page companion note (`paper1b_companion`), with cross-references resolved between the two. The theory version remains the complete record. |
| 6 | Introduction and abstract rewritten around the headline; one stale sentence fixed (the finite-sample near-instability bound is proved). |
| 7.1–7.2 | All five versions rebuild with no undefined references. Checks: 42 of 42. |

From the other tool's "Information for Intervention" draft: the framing, the headline and three literature references were taken. Its general-theory section, its use of the thesis and companion-paper results as theorems, and its synthetic decision example were not.

## Not done, and why

| Stage | Status |
|---|---|
| 0.3, 0.5 | Branch deletion and tags are blocked for this session; the authors do them in the GitHub interface. |
| 3.2 | The supplement is 94 pages, not 40. Reaching 40 means dropping whole sections; the proposal below needs the authors' decision. |
| 4 | Author verification of the proofs is the authors' work. |
| 5 | The Hyperliquid test cannot run before 10 December 2026 and its specification needs the authors' approval before registration. |
| 7.3–7.5 | Traceability rerun, written referee answers and the replication README are not yet done for the focused version. |
| 8 | Submission is the authors' act. |

## Proposed further cut of the focused supplement (for decision)

| Section | Pages | Proposal |
|---|---|---|
| S1–S7 full statements | 25 | Keep, but delete remarks that repeat the main text |
| S8 proofs of main results | 5 | Keep |
| S9 equilibrium: further results | 12 | Keep the inventory equilibrium and the zeros result; move the rest to the companion |
| S10 execution cost and capital | 4 | Keep (money value of tags) |
| S11 two unknown groups | 1 | Drop |
| S12 supervisory decision in detail | 8 | Keep the K-group targeting result; shorten |
| S13 saturating traders: proofs | 2 | Keep |
| S14 cheap questions | 4 | Keep |
| S15–S16 dynamics, running market | 7 | Keep |
| S18–S19 general memory, uniform rate | 6 | Keep |
| S20–S27 benchmarks, worked example, blind spot, audit-trail pricing | 9 | Move to the companion or drop |
| S29–S30 machine checks | 9 | Keep the table; move per-declaration detail to the repository |

This would bring the supplement to roughly 60 pages. Getting to 40 would also need S1–S7 merged with the proofs.
