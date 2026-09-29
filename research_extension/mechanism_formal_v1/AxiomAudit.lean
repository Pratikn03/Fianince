import Mechanism
import Lean

open Lean Elab Command

-- Inventory the elaborated environment: indentation/namespaces cannot hide proofs.
run_cmd do
  let env ← getEnv
  let cwd ← IO.currentDir
  let mut modules : Array Name := #[]
  for m in env.header.moduleNames do
    let source := System.FilePath.mk (m.toString.replace "." "/" ++ ".lean")
    let object ← findOLean m
    let localObject := object.toString.startsWith (cwd.toString ++ "/.lake/")
    if (← source.pathExists) || localObject then
      unless ← source.pathExists do
        throwError "Local imported module has no bound source: {m}"
      modules := modules.push m
  let mut rows : Array Json := #[]
  for (name, info) in env.constants.toList do
    let kind := match info with
      | .thmInfo _ => "theorem"
      | .axiomInfo _ => "axiom"
      | _ => ""
    if kind != "" then
      if let some idx := env.getModuleIdxFor? name then
        let m := env.header.moduleNames[idx.toNat]!
        if modules.contains m then
          let axioms ← collectAxioms name
          rows := rows.push (Json.mkObj [
            ("name", toJson name.toString), ("module", toJson m.toString),
            ("kind", toJson kind), ("axioms", toJson (axioms.map Name.toString))])
  logInfo ("MM_AUDIT " ++ (Json.mkObj [
    ("modules", toJson (modules.map Name.toString)),
    ("declarations", toJson rows)]).compress)
