"""Inventory current standalone Paper 1; retain semantic obligations explicitly."""
from pathlib import Path
import ast
import hashlib
import json
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
src=(ROOT/'ceiling_suite/papers/paper1/paper1_ssrn.tex').read_text()
tree=ast.parse((ROOT/'ceiling_suite/verify_ceiling_suite_lean_proofs.py').read_text())
mapping=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='PAPER1_MAP' for t in n.targets))
typed={r['name']:r for line in (ROOT/'research_extension/current_manuscript_lean_20261008/paper1_release_axioms.jsonl').read_text().splitlines()
       if line.startswith('{') for r in [json.loads(line)] if r.get('kind')=='named_theorem'}
receipt_path=ROOT/'research_extension/current_manuscript_lean_20261008/paper1_release_receipt.json'
receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
receipt_matches=(receipt.get('status')=='FULL_PROJECT_BUILD_AND_STRICT_AXIOM_AUDIT_PASS' and
  receipt.get('manuscript_source_sha256',{}).get('ceiling_suite/papers/paper1/paper1_ssrn.tex')==hashlib.sha256(src.encode()).hexdigest())
notes={
 'lem:micro':'Steady-state filtering/OGD under their distinct information and objective assumptions; not identification of learning from fitted market persistence.',
 'lem:cm':'Positive stable response class; verify initial-state and a=0 boundary conventions before reuse.',
 'thm:merged':'Merged measure, not ownership or multiplicity at equal rates. Pole count does not by itself certify the unformalized minimal-realization step.',
 'prop:endogenous_kappa':'Rewritten: common selected fixed point; Lipschitz/contraction sensitivity. New scalar bound does not derive a dealer equilibrium or covariance-only information set.',
 'thm:quantity':'Separate executed quantity, disturbance and testing resources. Exact Gaussian quantile identity and solvency converse have historically narrower formal coverage.',
 'thm:kcohort':'Finite record and binomial pair formally supported; distinguish from a quadrature construction and constants uniform in record length.',
 'prop:esprit':'Revised statement. Existing two-point wrapper is insufficient; inspect all-K Prony/inverse-map declarations and the exact compact rich parameter class.',
 'cor:unknown_primitives':'Plug-in stability is conditional on bounded primitive error and nonzero impact; does not identify the fundamental proxy from prices.',
 'thm:minphase':'Revised statement. Separate zero geometry, spectral factorization, known innovation variance and minimum-phase normalization.',
 'prop:passive':'Finite-record sample bounds have actual Gaussian-law proofs; divergence-rate asymptotics and matching rate lower bound remain separate written obligations.',
 'prop:tagged':'Instrument nonsingularity is supported. Stationary IV ergodic/CLT steps and independence of reporting errors from the whole price path are separate obligations.',
 'thm:discvalue':'Reset experiment and stationary passive IV are different contracts; keep noise laws, known probe and rate accuracy metric explicit.',
 'prop:strategic':'Rewritten conditional limits. Old wrapper assumes the cost/profit gap. No unrestricted account splitting or equilibrium evasion theorem.',
 'prop:target':'Exact K=2 witness and finite Gaussian price-record bound checked in prior release. All-K dominant-weight gap absent; label executability and response conditions retained.',
 'prop:robust_gate':'Actual product-Gaussian unsafe event bound checked in prior release. Scalar R readings remain hypothetical; direct flow bridge is a separate contract.',
 'prop:priced_decision':'Fixed-menu affine optimization and acquisition algebra checked. No optimum over all interventions or acquisition schemes.',
 'thm:abstain':'Decision/algebra support does not establish the autoregression path divergence; inspect its derivation and horizon regime.',
 'prop:passive0':'Three-step decision reduction has support; observational variance formula and independent block assumptions require written review.',
 'prop:primitives':'Separate observable price law from assumed known a, impact and fundamental; simultaneous primitive identification is an additional problem.',
 'prop:tied':'Exact tied-rate equivalence must preserve positivity and total weight; does not establish a named trader class.',
 'prop:crb':'Local unbiased/regular information benchmark is not a minimax bound over biased estimators.',
 'prop:tri':'Region algebra is conditional on declared session, capital and observation contracts; do not infer a real trading timescale.',
 'thm:spectral':'Mapped wrapper verifies positivity and scalar rearrangement. Parseval, information-to-execution reduction, process-noise covariance KL and numerical infimum require separate correspondence checks.',
 'thm:adaptive':'Mapped wrapper assumes the information inequality. Added stopped likelihood/integrability conditions; ratio of lower bounds does not bound achievable savings.',
 'thm:rh':'Mapped scalar completion-of-square result does not certify the full generalized-eigenvector decomposition or numerical optimization. Review degeneracies and all denominators.',
 'cor:garch':'Heteroskedastic scaling alone is not a proof under arbitrary conditional volatility or endogenous observation errors.',
 'thm:uniformw1':'Confirm target Wasserstein class, tail bound and discretization against the typed declaration; no finite-support assumption may be silently transferred.',
 'thm:blind':'Constructive variance-matching example within its triangular model; not a general theorem that all volatility information is useless.',
 'lem:altpair':'Explicit matched pair supplies moment/Wasserstein separation; does not automatically give a largest-class action gap.',
 'thm:general':'Explicit binomial/cosine and constructive approximation proofs differ from the written approximation route and constants; compare the two versions, not just the order.',
 'lem:toeplitz':'Fundamental-mark round trip and average linear-book execution. Fairness alone does not supply the claimed arbitrary camouflage cost coefficient.',
 'thm:cap':'Positive monotone response and specified marking/margin convention; not universal protection of leveraged accounts.',
 'prop:disclosure':'Third-mark identity at common initial receipt, inventory and fee convention; economic utility needs a holding/exit decision.',
 'thm:capital':'Formal coercivity constant has the stated form but not necessarily the manuscript explicit modal bound; converse pulse margin remains written.',
 'thm:twocohort':'Known pair/determinant calculation differs from unknown mixture estimation; keep amplitude and experiment horizon fixed.',
 'prop:choice':'Stylized fixed-cost sharing and waiting harm. Algebra is conditional accounting, not calibrated regulator welfare.'}
extra={
 'prop:endogenous_kappa':['p1_endogenous_contraction_sensitivity'],
 'prop:strategic':['p1_sybil_share_count_bound','p1_camouflage_unprofitable'],
 'prop:target':['p1_gr_three_matched_moments','p1_gr_dominant_intensity_gap','p1_gr_aggregate_gap','p1_gr_reset_lower_bound'],
 'prop:robust_gate':['p1_supervisory_gaussian_unsafe_halt','p1_supervisory_gaussian_unsafe_halt_budget'],
 'prop:priced_decision':['p1_no_data_throttle_optimal','p1_no_data_capped_halt_optimal','p1_information_purchase_break_even','p1_optional_information_value_nonnegative']}
rows=[]
for m in re.finditer(r'\\begin\{(theorem|lemma|proposition|corollary)\}(.*?)\\end\{\1\}',src,re.S):
 label=re.search(r'\\label\{([^}]+)\}',m[2])
 if not label:raise ValueError('Unlabelled numbered statement')
 label=label[1];old=mapping.get(label,([],[]))[0];old=[old] if isinstance(old,str) else old
 names=list(dict.fromkeys(old+extra.get(label,[])))
 rows.append(dict(label=label,environment=m[1],source_line=src[:m.start()].count('\n')+1,
   statement_sha256=hashlib.sha256(m[0].encode()).hexdigest(),statement=m[0],
   historical_mapped_declarations=old,additional_review_declarations=extra.get(label,[]),
   historical_types={n:typed['CurrentMM.'+n]['type'] for n in names if 'CurrentMM.'+n in typed},
   status=('CONDITIONAL_REWRITE_ALGEBRA_KERNEL_CHECKED_MARKET_PREMISES_ASSUMED' if receipt_matches and all('CurrentMM.'+n in typed for n in extra[label]) else 'CONDITIONAL_REWRITE_NEW_BUILD_REQUIRED') if label in ['prop:endogenous_kappa','prop:strategic'] else
          'PRIOR_RELEASE_CORE_SCOPE_REVIEWED' if label in ['prop:target','prop:robust_gate','prop:priced_decision'] else
          'HISTORICAL_MAPPING_WITH_EXPLICIT_REMAINING_SEMANTIC_OBLIGATION',
   scope_note=notes[label]))
assert len(rows)==36
assert set(notes)=={r['label'] for r in rows}
out=dict(source_sha256=hashlib.sha256(src.encode()).hexdigest(),kernel_receipt_matches_manuscript=receipt_matches,
  scope='Standalone SSRN manuscript; exact statement hashes and historical typed signatures. A mapping is not equivalence.',
  full_manuscript_formalization_complete=False,human_independent_review_complete=False,
  rows=rows,operational_flow_bridge='Seven declarations in Paper1FlowDecision.lean; consult the current build receipt. Executable rule soundness remains a correspondence obligation.')
(OUT/'CLAIM_VERIFICATION_LEDGER.json').write_text(json.dumps(out,indent=2)+'\n')
md=['# Paper 1 statement correspondence ledger','',
    'All 36 numbered statements are inventoried below. This is a complete inventory, not a declaration of complete formalization. The JSON companion retains exact statement hashes and historical mapped theorem types. New kernel status belongs to the source-bound build receipt.','',
    '| Statement | Review finding / remaining obligation |','|---|---|']
md += [f"| `{r['label']}` | {r['scope_note']} |" for r in rows]
(OUT/'CLAIM_VERIFICATION_LEDGER.md').write_text('\n'.join(md)+'\n')
print('Inventoried 36 standalone statements; unresolved semantic obligations retained.')
