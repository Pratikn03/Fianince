import Mechanism.Evaluator
import Lean

open Mechanism Lean

def pairs : List Pair := [(false,false), (false,true), (true,false), (true,true)]
def pairJson (p : Pair) : Json := toJson [p.1,p.2]
def outcomeJson (o : Outcome) : Json := toJson
  ([o.profit0,o.profit1,o.customer,o.welfare,o.trade].map toString)

def contractJson : Json := Json.mkObj [
  ("model", toJson "v0.12-state140-H2"),
  ("epsilon", toJson "1/10"), ("alpha", toJson "1/2"),
  ("asks", toJson ["2","4","6"]),
  ("state", toJson [["0","1","0"], ["0","0","0"],
                    ["0","0","1"], ["0","0","0"]]),
  ("atoms", toJson (atoms.map fun (p,v,c) => [toString p,toString v,toString c])),
  ("refresh", toJson "both-before-period-1-including-frozen-shadows"),
  ("costs", toJson ["0","0"])]

def outputJson : Json := Json.mkObj [
  ("contract", contractJson),
  ("cells", toJson (pairs.flatMap fun p => pairs.map fun m => Json.mkObj [
    ("profile", pairJson p), ("mask", pairJson m),
    ("total", outcomeJson (evaluate witness p m (0,0)))])),
  ("settlements", toJson (actions.flatMap fun a => actions.flatMap fun b =>
    atoms.map fun (_,v,c) => Json.mkObj [
      ("quotes", toJson [toString (ask a),toString (ask b)]),
      ("value", toJson (toString v)), ("customer", toJson (toString c)),
      ("total", outcomeJson (settle a b v c))])),
  ("costly_cells", toJson (pairs.map fun p => Json.mkObj [
    ("profile", pairJson p), ("mask", pairJson (false,true)),
    ("total", outcomeJson (evaluate witness p (false,true) (1/20,1/20)))]))]

-- Compiled execution is only a fixture export, not evidence of formal proof.
def main : IO Unit := IO.println outputJson.compress
