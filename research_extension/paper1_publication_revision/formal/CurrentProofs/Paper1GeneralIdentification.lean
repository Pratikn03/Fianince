import CurrentProofs.Paper1StressIdentification

/-!
# Paper 1: identification for general (nonlinear) feedback populations

A population is represented only by its aggregate feedback flow map `F`, which may be any function of the price
path (linear, saturating, switching after past profits, ...). In the probing recursion
`x 0 = κ (F x 0 + v 0)`, `x (t+1) = a x t + κ (F x (t+1) + v (t+1))` with `κ ≠ 0`:

* `p1_general_identification`: two populations produce the same set of (probe, price path) pairs (in the sense
  that every pair of the first is a pair of the second) if and only if their flow maps agree on every price path.
* `p1_general_identification_iff`: the same with equality of the two response relations.
* `p1_identified_functional`: a group-level quantity `g` of the population can be recovered from probe responses
  only if it is constant on populations with the same flow map; conversely, any `g` that factors through the flow
  map is determined by the responses.

So the aggregate flow map is a minimal sufficient statistic for probe responses, for any population.
-/

namespace CurrentMM

/-- The response relation of a population with flow map `F`: the (probe, price path) pairs it can produce. -/
def ProbeResponses (a κ : ℝ) (F : (ℕ → ℝ) → ℕ → ℝ) : Set ((ℕ → ℝ) × (ℕ → ℝ)) :=
  {p | ProbePricePath a κ F p.1 p.2}

/-- Equal flow maps give equal response relations (sufficiency for probing, any population). -/
theorem p1_responses_of_flow_eq (a κ : ℝ) (F F' : (ℕ → ℝ) → ℕ → ℝ) (h : ∀ x t, F x t = F' x t) :
    ProbeResponses a κ F = ProbeResponses a κ F' := by
  ext p
  show ProbePricePath a κ F p.1 p.2 ↔ ProbePricePath a κ F' p.1 p.2
  unfold ProbePricePath
  constructor
  · rintro ⟨h0, hs⟩
    exact ⟨by rw [← h]; exact h0, fun t => by rw [← h]; exact hs t⟩
  · rintro ⟨h0, hs⟩
    exact ⟨by rw [h]; exact h0, fun t => by rw [h]; exact hs t⟩

/-- **General identification.** If every (probe, price path) pair of the first population is one of the second,
the two flow maps agree on every price path. -/
theorem p1_general_identification (a κ : ℝ) (F F' : (ℕ → ℝ) → ℕ → ℝ) (hκ : κ ≠ 0)
    (hsub : ProbeResponses a κ F ⊆ ProbeResponses a κ F') :
    ∀ x t, F x t = F' x t := by
  intro x t
  have hp : ProbePricePath a κ F (steeringProbe a κ F x) x := p1_probe_steer_target a κ F x hκ
  have hp' : ProbePricePath a κ F' (steeringProbe a κ F x) x :=
    hsub (show (steeringProbe a κ F x, x) ∈ ProbeResponses a κ F from hp)
  exact p1_probe_flow_recovery_eq a κ F F' (steeringProbe a κ F x) x hp hp' hκ t

/-- **General identification, iff form.** Two populations have the same probe responses exactly when their
aggregate flow maps agree on every price path. -/
theorem p1_general_identification_iff (a κ : ℝ) (F F' : (ℕ → ℝ) → ℕ → ℝ) (hκ : κ ≠ 0) :
    ProbeResponses a κ F = ProbeResponses a κ F' ↔ ∀ x t, F x t = F' x t := by
  constructor
  · intro h
    exact p1_general_identification a κ F F' hκ (le_of_eq h)
  · exact p1_responses_of_flow_eq a κ F F'

/-- **Which group-level quantities are identified.** Let populations be indexed by `P`, with flow maps `flow p`
and a group-level quantity `g p` (for example the weight of the largest group). If `g` is determined by the probe
responses, it is constant on populations with the same flow map; and if it is constant on such populations, it is
determined by the responses. -/
theorem p1_identified_functional {P β : Type*} (a κ : ℝ) (hκ : κ ≠ 0)
    (flow : P → (ℕ → ℝ) → ℕ → ℝ) (g : P → β) :
    (∀ p p', ProbeResponses a κ (flow p) = ProbeResponses a κ (flow p') → g p = g p') ↔
      (∀ p p', (∀ x t, flow p x t = flow p' x t) → g p = g p') := by
  constructor
  · intro h p p' hf
    exact h p p' ((p1_general_identification_iff a κ (flow p) (flow p') hκ).2 hf)
  · intro h p p' hr
    exact h p p' ((p1_general_identification_iff a κ (flow p) (flow p') hκ).1 hr)

end CurrentMM
