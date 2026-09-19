# Next-stage validation

This is a separately packaged, CPU-only validation study. It does not import
the original market or fill engine.

Run the tests and confirmation outputs from the repository root:

```bash
python3.11 -m pytest -q studies/next_stage_validation/tests
python3.11 studies/next_stage_validation/scripts/run_all.py \
  --output studies/next_stage_validation/results --episodes 128
python3.11 studies/next_stage_validation/scripts/run_interventions.py \
  --output studies/next_stage_validation/results --episodes 256
python3.11 studies/next_stage_validation/scripts/run_observation_benchmark.py \
  --output studies/next_stage_validation/results --replicates 200
python3.11 studies/next_stage_validation/scripts/analyze_results.py
python3.11 studies/next_stage_validation/scripts/render_paper_artifacts.py
```

The saved confirmation result is a null AI-specific comparison, a noisy/dependent
coverage limitation, a synthetic intervention result, and a descriptive OHLCV
pilot. Full order-book calibration and external replication remain blocked.
