import Std

/-
Conditional decision logic only. No statistical coverage, impulse-response
bound, minimax rate, financial-account model, or novelty theorem is asserted.
These standard logical implications are intentionally separated from the
analytic assumptions that must be proved in the manuscript.
-/
namespace InformationDecision

def Certified {Theta Action : Type} (compatible : Theta → Prop)
    (safe : Theta → Action → Prop) (action : Action) : Prop :=
  ∀ theta, compatible theta → safe theta action

theorem coverage_soundness {Theta Action : Type}
    {compatible : Theta → Prop} {safe : Theta → Action → Prop}
    {truth : Theta} {action : Action}
    (covered : compatible truth)
    (certificate : Certified compatible safe action) : safe truth action := by
  exact certificate truth covered

theorem disclosure_refinement {Theta Action : Type}
    {coarse fine : Theta → Prop} {safe : Theta → Action → Prop}
    {action : Action} (refines : ∀ theta, fine theta → coarse theta)
    (certificate : Certified coarse safe action) : Certified fine safe action := by
  intro theta h
  exact certificate theta (refines theta h)

theorem selected_action_soundness {Data Theta Action : Type}
    (compatible : Data → Theta → Prop) (safe : Theta → Action → Prop)
    (select : Data → Action) (data : Data) (truth : Theta)
    (covered : compatible data truth)
    (selection_certified : Certified (compatible data) safe (select data)) :
    safe truth (select data) := by
  exact selection_certified truth covered

theorem empty_set_vacuity {Theta Action : Type}
    (safe : Theta → Action → Prop) (action : Action)
    (empty : Theta → Prop) (none : ∀ theta, ¬ empty theta) :
    Certified empty safe action := by
  intro theta h
  exact False.elim (none theta h)

/- The last theorem exposes vacuous truth: the implementation must independently
   reject empty compatible sets rather than interpreting it as useful evidence. -/

theorem certificate_does_not_need_unique_identity {Theta Action : Type}
    (compatible : Theta → Prop) (safe : Theta → Action → Prop)
    (action : Action) (all_safe : ∀ theta, compatible theta → safe theta action) :
    Certified compatible safe action := by
  exact all_safe

theorem robust_value_monotone {Action : Type} (coarse fine : Action → Prop)
    (value : Action → Int) (upper : Int)
    (included : ∀ action, coarse action → fine action)
    (fine_upper_bound : ∀ action, fine action → value action ≤ upper) :
    ∀ action, coarse action → value action ≤ upper := by
  intro action h
  exact fine_upper_bound action (included action h)

theorem equal_loss_same_safety {Theta Action : Type}
    (loss : Theta → Action → Nat) (budget : Nat) (left right : Theta)
    (same_loss : ∀ action, loss left action = loss right action) :
    ∀ action, (loss left action ≤ budget ↔ loss right action ≤ budget) := by
  intro action
  rw [same_loss action]

theorem equal_risk_not_equal_objective :
    ∃ risk utility : Bool → Nat,
      risk false = risk true ∧ utility false ≠ utility true := by
  refine ⟨(fun _ => 0), (fun b => if b then 1 else 0), ?_⟩
  decide

end InformationDecision

#print axioms InformationDecision.coverage_soundness
#print axioms InformationDecision.disclosure_refinement
#print axioms InformationDecision.selected_action_soundness
#print axioms InformationDecision.empty_set_vacuity
#print axioms InformationDecision.certificate_does_not_need_unique_identity
#print axioms InformationDecision.robust_value_monotone
#print axioms InformationDecision.equal_loss_same_safety
#print axioms InformationDecision.equal_risk_not_equal_objective
