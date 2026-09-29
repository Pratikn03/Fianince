import Std
import Init.GrindInstances.Ring.Rat

namespace Mechanism

/- Executable economic primitives, independent of all numerical certificates.
   This version fixes epsilon=1/10 and alpha=1/2. -/
inductive Action where
  | low | mid | high
  deriving DecidableEq, Repr

def actions : List Action := [.low, .mid, .high]
def ask : Action → Rat | .low => 2 | .mid => 4 | .high => 6

structure Table where
  low : Rat
  mid : Rat
  high : Rat
  deriving DecidableEq, Repr

def Table.get (q : Table) : Action → Rat
  | .low => q.low | .mid => q.mid | .high => q.high

def Table.put (q : Table) (a : Action) (x : Rat) : Table :=
  match a with
  | .low => {q with low := x}
  | .mid => {q with mid := x}
  | .high => {q with high := x}

def policy (q : Table) : Table :=
  let top := max q.low (max q.mid q.high)
  let count : Rat := (if q.low = top then 1 else 0) +
    (if q.mid = top then 1 else 0) + (if q.high = top then 1 else 0)
  let prob := fun x => (1/30 : Rat) + (if x = top then (9/10)/count else 0)
  ⟨prob q.low, prob q.mid, prob q.high⟩

structure Outcome where
  profit0 : Rat
  profit1 : Rat
  customer : Rat
  welfare : Rat
  trade : Rat
  deriving DecidableEq, Repr

def zeroOutcome : Outcome := ⟨0,0,0,0,0⟩
def addOutcome (x y : Outcome) : Outcome :=
  ⟨x.profit0+y.profit0, x.profit1+y.profit1, x.customer+y.customer,
   x.welfare+y.welfare, x.trade+y.trade⟩
def scaleOutcome (p : Rat) (x : Outcome) : Outcome :=
  ⟨p*x.profit0, p*x.profit1, p*x.customer, p*x.welfare, p*x.trade⟩

def settle (a b : Action) (v c : Rat) : Outcome :=
  let price := min (ask a) (ask b)
  if c < price then zeroOutcome else
    let fill0 : Rat := if ask a < ask b then 1 else if a = b then 1/2 else 0
    let fill1 : Rat := if ask b < ask a then 1 else if a = b then 1/2 else 0
    ⟨fill0*(price-v), fill1*(price-v), c-price, c-v, 1⟩

-- Six IID economic atoms: (probability, asset value, customer valuation).
def atoms : List (Rat × Rat × Rat) :=
  [(1/8,0,-2), (1/4,0,2), (1/8,0,6),
   (1/8,4,2), (1/4,4,6), (1/8,4,10)]

def update (q : Table) (a : Action) (reward : Rat) : Table :=
  q.put a ((q.get a + reward)/2)

structure State where
  active0 : Table
  active1 : Table
  shadow0 : Table
  shadow1 : Table
  deriving DecidableEq, Repr

abbrev Pair := Bool × Bool

def release (s : State) (profile : Pair) : State :=
  {s with active0 := if profile.1 then s.shadow0 else s.active0,
          active1 := if profile.2 then s.shadow1 else s.active1}

def advance (s : State) (mask : Pair) (a b : Action) (o : Outcome) : State :=
  {s with shadow0 := if mask.1 then update s.shadow0 a o.profit0 else s.shadow0,
          shadow1 := if mask.2 then update s.shadow1 b o.profit1 else s.shadow1}

def refresh (s : State) : State :=
  {s with active0 := s.shadow0, active1 := s.shadow1}

-- Stipulated post-hoc grid state 140, not a trained population.
def witness : State := ⟨⟨0,1,0⟩, ⟨0,0,0⟩, ⟨0,0,1⟩, ⟨0,0,0⟩⟩

end Mechanism
