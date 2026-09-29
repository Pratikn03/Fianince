import Mechanism.Model

namespace Mechanism

def sumOutcomes : List Outcome → Outcome
  | [] => zeroOutcome
  | x :: xs => addOutcome x (sumOutcomes xs)

-- Integrate the actual six settlement branches, not an imported payoff matrix.
def stage (a b : Action) : Outcome :=
  sumOutcomes (atoms.map fun (p,v,c) => scaleOutcome p (settle a b v c))

def stageExpectation (s : State) : Outcome :=
  let p := policy s.active0
  let q := policy s.active1
  sumOutcomes (actions.flatMap fun a => actions.map fun b =>
    scaleOutcome (p.get a * q.get b) (stage a b))

structure Branch where
  probability : Rat
  action0 : Action
  action1 : Action
  outcome : Outcome
  deriving Repr

-- Quotes are randomized before the independent current economic draw.
def branches (s : State) : List Branch :=
  let p := policy s.active0
  let q := policy s.active1
  actions.flatMap fun a => actions.flatMap fun b => atoms.map fun (w,v,c) =>
    ⟨p.get a * q.get b * w, a, b, settle a b v c⟩

def branchMass (s : State) : Rat :=
  ((branches s).map (·.probability)).foldr (· + ·) 0

-- Only a two-period evaluator is claimed. The second period is refreshed even
-- when a learning mask is false; only realized own rewards enter shadow updates.
def grossTwo (s : State) (mask : Pair) : Outcome :=
  sumOutcomes ((branches s).map fun b =>
    let later := refresh (advance s mask b.action0 b.action1 b.outcome)
    scaleOutcome b.probability (addOutcome b.outcome (stageExpectation later)))

def deduct (o : Outcome) (costs : Rat × Rat) (profile : Pair) : Outcome :=
  let k0 := if profile.1 then costs.1 else 0
  let k1 := if profile.2 then costs.2 else 0
  {o with profit0 := o.profit0-k0, profit1 := o.profit1-k1,
          welfare := o.welfare-k0-k1}

def evaluate (s : State) (profile mask : Pair) (costs : Rat × Rat) : Outcome :=
  deduct (grossTwo (release s profile) mask) costs profile

end Mechanism
