# Implementation and verification plan
1. Write failing tests for observable-response regression, interval deconvolution, positive recurrence feasibility and balance-sheet conservation.
2. Implement an isolated market generator and a public inference module that cannot accept hidden states or true parameters.
3. Test exact zero-noise recurrence, positive-bin containment and numerical dual feasibility before Monte Carlo evaluation.
4. Execute the frozen primary panel; record all result rows, sufficient statistics and seed manifests. Keep sample public observations for inspection.
5. Run misspecification controls, a separate recurrence verifier and deterministic clean rerun checks.
6. Integrate results into the original manuscript with an explicit provenance/evidence table; retain both earlier studies' findings and adverse comparison results.
7. Compile and visually inspect the updated PDF, then package source, results, code and reproduction instructions.
