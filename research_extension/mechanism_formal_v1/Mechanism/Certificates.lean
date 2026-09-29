import Mechanism.Model
import Mechanism.Evaluator

namespace Mechanism

-- Wrong tie allocation, clipping losses, or allowing unaffordable trade breaks
-- these hand-derived economic checks, independently of the evaluator.
theorem loss_making_tie : settle .low .low 4 6 = ⟨-1, -1, 4, 2, 1⟩ := by decide +kernel
theorem abstention : settle .mid .high 0 2 = zeroOutcome := by decide
theorem tied_policy : policy ⟨1, 1, 0⟩ = ⟨29/60, 29/60, 1/30⟩ := by decide +kernel
theorem frozen_refresh : (refresh (advance witness (false, false) .mid .high
    (settle .mid .high 0 6))).active0 = witness.shadow0 := by decide
theorem reward_updates_chosen_only : update ⟨0,0,0⟩ .high 3 = ⟨0,0,3/2⟩ := by decide +kernel

theorem stage_low_tie : stage .low .low = ⟨-1/8,-1/8,5/2,9/4,7/8⟩ := by decide +kernel
theorem stage_high_tie : stage .high .high = ⟨3/4,3/4,1/2,2,1/2⟩ := by decide +kernel
theorem witness_branch_mass : branchMass (release witness (true,false)) = 1 := by decide +kernel

-- A wrong refresh schedule, oracle rewards, or resetting the shadow at release
-- would break these independently obtained exact two-period targets.
set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem witness_wait_payoff : evaluate witness (false,false) (false,true) (0,0) =
    ⟨261703/576000,7063/23040,246211/72000,1203983/288000,243983/192000⟩ := by decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem witness_early_payoff : evaluate witness (true,false) (false,true) (0,0) =
    ⟨298531/576000,379723/576000,215431/72000,1200851/288000,240851/192000⟩ := by decide +kernel

end Mechanism
