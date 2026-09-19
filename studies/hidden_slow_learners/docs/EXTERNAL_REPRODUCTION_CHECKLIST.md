# External reproduction checklist

No independent external reproduction has yet occurred. This checklist is an invitation to test the result, not a statement that someone has already done so.

## Preserve the evidence

1. Extract the ZIP into a new directory and retain the original archive.
2. Verify `MANIFEST.sha256` using `python scripts/verify_manifest.py` before changing files.
3. Record operating system, Python, NumPy, SciPy, and BLAS versions. The delivered lock is the executed environment, not proof of compatibility with every version permitted by the broad requirements.
4. Read the model assumptions, information-set distinction, and claim ledger before running.

## Reproduce without importing the main inference code

Run `python scripts/verify_exact.py` first. It uses rational arithmetic and the standard library. Inspect that it rederives the moment and impulse identities, rather than merely trusting stored labels.

After installing numerical dependencies, run `python scripts/verify_measurements.py`. It regenerates the recorded noisy inputs and recomputes the diagnostic independently of the main package. Its agreement is useful, but shared conceptual errors remain possible.

## Recompute the complete experiment

```bash
python -m pytest -q
python scripts/run_experiments.py --output reproduced_results
python scripts/verify_exact.py --results reproduced_results
python scripts/verify_measurements.py --results reproduced_results
python scripts/check_reproduction.py --candidate reproduced_results
python scripts/build_figures.py --results reproduced_results --output reproduced_figures
```

Exact identities and qualitative decisions are the primary portability targets. Different numerical-library builds can perturb floating-point paths near boundaries; report discrepancies rather than silently expanding tolerances. The exact-data comparator may report byte differences across environments even when the mathematical claim remains supported.

## Try to falsify the claims

- Derive the positive-model stability criterion and barycentric construction independently.
- Check off-by-one indexing: K matched kernel taps yield h[0] through h[K+1], not arbitrarily many observations.
- Remove the rate floor, introduce an unmodeled slower state, use signed responses, or correlate noise. Confirm that the advertised statistical assumptions no longer hold rather than extending the guarantee without proof.
- Test a full-horizon constrained identification or moment-feasibility comparator with the same data, valid side information, and compute budget.
- Search positive-realization and truncated-moment literature for an equivalent theorem. Report an overlap even if it changes publication positioning.

## Report form

Record your identity or anonymous reviewer identifier, date, whether you were involved in creating this release, environment, exact commands, checks passed or failed, numerical discrepancies, proof objections, prior-art overlap, and whether the data-access assumptions seem achievable in the intended financial setting.

A successful external run would establish computational replication in that environment. It would not by itself establish global novelty, calibrated real-world performance, or financial usefulness.
