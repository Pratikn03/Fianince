import Mechanism.Certificates

namespace Mechanism

theorem settlement_conserves (a b : Action) (v c : Rat) :
    (settle a b v c).profit0 + (settle a b v c).profit1 +
      (settle a b v c).customer = (settle a b v c).welfare := by
  cases a <;> cases b <;> simp [settle, ask, zeroOutcome] <;> split <;> simp_all <;> grind

theorem release_preserves_shadow (s : State) (p : Pair) :
    (release s p).shadow0 = s.shadow0 ∧ (release s p).shadow1 = s.shadow1 := by
  exact ⟨rfl, rfl⟩

theorem frozen_shadow (s : State) (a b : Action) (o : Outcome) :
    advance s (false,false) a b o = s := by simp [advance]

theorem scheduled_refresh (s : State) :
    (refresh s).active0 = s.shadow0 ∧ (refresh s).active1 = s.shadow1 := by
  exact ⟨rfl, rfl⟩

theorem costs_conserve (o : Outcome) (k : Rat × Rat) (p : Pair)
    (h : o.profit0 + o.profit1 + o.customer = o.welfare) :
    (deduct o k p).profit0 + (deduct o k p).profit1 +
      (deduct o k p).customer = (deduct o k p).welfare := by
  simp only [deduct]
  grind

theorem stage_welfare_identity (a b : Action) :
    (stage a b).welfare = 2 + (if a = .low ∨ b = .low then 1/4 else 0) := by
  cases a <;> cases b <;> decide +kernel

theorem low_ask_dominated (b : Action) :
    (stage .mid b).profit0 > (stage .low b).profit0 := by
  cases b <;> decide +kernel

-- The specific reward-to-policy path cited in the informal proof.
theorem accommodation_path :
    policy (update witness.shadow1 .high (settle .mid .high 4 6).profit1) = ⟨1/3,1/3,1/3⟩ ∧
    policy (update witness.shadow1 .high (settle .high .high 4 6).profit1) = ⟨1/30,1/30,14/15⟩ := by
  decide +kernel

theorem witness_gross_private_gain :
    (evaluate witness (true,false) (false,true) (0,0)).profit0 -
    (evaluate witness (false,false) (false,true) (0,0)).profit0 = 1023/16000 := by
  rw [witness_early_payoff, witness_wait_payoff]
  decide +kernel

theorem witness_gross_welfare_loss :
    (evaluate witness (true,false) (false,true) (0,0)).welfare -
    (evaluate witness (false,false) (false,true) (0,0)).welfare = -87/8000 := by
  rw [witness_early_payoff, witness_wait_payoff]
  decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem frozen_rival_null :
    (evaluate witness (true,false) (false,false) (0,0)).profit0 =
    (evaluate witness (false,false) (false,false) (0,0)).profit0 ∧
    (evaluate witness (true,false) (false,false) (0,0)).welfare =
    (evaluate witness (false,false) (false,false) (0,0)).welfare := by decide +kernel

def costlyGame (p : Pair) : Outcome := evaluate witness p (false,true) (1/20,1/20)

def IsPureEquilibrium (p : Pair) : Prop :=
  (∀ x : Bool, (costlyGame p).profit0 ≥ (costlyGame (x,p.2)).profit0) ∧
  (∀ x : Bool, (costlyGame p).profit1 ≥ (costlyGame (p.1,x)).profit1)

def IsPlannerChoice (p : Pair) : Prop :=
  ∀ x y : Bool, (costlyGame p).welfare ≥ (costlyGame (x,y)).welfare

-- Proofs enumerate all feasible deviations/profiles, not a selected equilibrium.
set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem unique_pure_equilibrium (x y : Bool) :
    IsPureEquilibrium (x,y) ↔ (x,y) = (true,false) := by
  unfold IsPureEquilibrium
  cases x <;> cases y <;> decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem unique_planner (x y : Bool) :
    IsPlannerChoice (x,y) ↔ (x,y) = (false,false) := by
  unfold IsPlannerChoice
  cases x <;> cases y <;> decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem costly_private_gain :
    (costlyGame (true,false)).profit0 - (costlyGame (false,false)).profit0 = 223/16000 := by
  decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem planner_equilibrium_gap :
    (costlyGame (false,false)).welfare - (costlyGame (true,false)).welfare = 487/8000 := by
  decide +kernel

def negativeInitial : State := {witness with shadow1 := ⟨-1/100,-1/100,-1/100⟩}

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem initialization_fragility :
    policy negativeInitial.shadow1 = policy witness.shadow1 ∧
    (evaluate negativeInitial (true,false) (false,true) (0,0)).profit0 =
      (evaluate negativeInitial (false,false) (false,true) (0,0)).profit0 ∧
    (evaluate negativeInitial (true,false) (false,true) (0,0)).welfare =
      (evaluate negativeInitial (false,false) (false,true) (0,0)).welfare := by
  decide +kernel

end Mechanism
