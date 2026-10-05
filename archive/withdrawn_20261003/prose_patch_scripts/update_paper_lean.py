with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

old_lean_block = r'''\begin{lstlisting}[language=Python, caption={Representative Lean 4 formalization of the Positive-Feedback Boundary.}, label={lst:lean4}]
import Mathlib.LinearAlgebra.Matrix.Spectrum
import Mathlib.Analysis.Complex.Polynomial

/-- Theorem 2.3: The deterministic linear joint system is asymptotically stable 
    if and only if the feedback loop gain satisfies the strict bound. --/
theorem positive_feedback_stability 
  (a g \eta Q : \mathbb{R}) 
  (ha : a < 1) 
  (h\eta : 0 < \eta) :
  spectral_radius J < 1 \leftrightarrow g * Q < 1 - a := by
  -- Proof omitted for brevity; exact mechanized proof tree is 
  -- provided in the supplementary Lean 4 repository (/lean_proofs/Stability.lean)
  sorry
\end{lstlisting}'''

new_lean_block = r'''\begin{lstlisting}[language=Python, caption={Representative Lean 4 mechanized formalization of Theorem 2.3 and Proposition 5.1 in \texttt{lean\_proofs/}.}, label={lst:lean4}]
import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

-- Characteristic polynomial: det(lambda*I - J)
def charPoly (a g eta kappa lam : Rat) : Rat :=
  lam * lam - (a + 1 - eta) * lam + a * (1 - eta) - g * eta * kappa

-- Theorem 2.3: Exact algebraic root factorization at boundary lambda = 1
theorem charPoly_at_one_identity (a g eta kappa : Rat) :
    charPoly a g eta kappa 1 = (1 - a - g * kappa) * eta := by
  unfold charPoly
  grind

-- Proposition 5.1: PBH unobservable eigenspace defect (J*v = (1 - eta)*v and C*v = 0)
theorem pbh_unobservable : C_dot pbh_null_vec = 0 := by
  unfold C_dot pbh_null_vec; decide

theorem pbh_eigenvector_x (a eta q1 q2 : Rat) :
    (J_mul a eta q1 q2 pbh_null_vec).x = 0 := by
  unfold J_mul pbh_null_vec; grind
\end{lstlisting}'''

content = content.replace(old_lean_block, new_lean_block)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)

print("Updated Lean 4 listing in paper.")
