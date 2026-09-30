import Proofs
import Lean

open Lean Elab Command

run_cmd do
  let env ← getEnv
  let mut count : Nat := 0
  let mut hasSorry : Bool := false
  for (name, info) in env.constants.toList do
    if name.toString.startsWith "MachineMarkets" then
      if let .thmInfo _ := info then
        count := count + 1
        let axioms ← collectAxioms name
        let axList := axioms.toList.map (fun (n : Name) => n.toString)
        if axList.contains "sorryAx" then
          hasSorry := true
          IO.println s!"  FAIL: {name} depends on sorryAx!"
        else
          IO.println s!"  PASS: {name} (axioms: {axList})"
  
  IO.println s!"Audited {count} theorems in namespace MachineMarkets."
  if hasSorry then
    throwError "Axiom audit failed: unproved theorems detected."
  else
    IO.println "SUCCESS: ALL THEOREMS FULLY VERIFIED WITHOUT SORRY!"
