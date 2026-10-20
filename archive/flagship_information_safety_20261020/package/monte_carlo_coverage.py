"""Monte Carlo simultaneous confidence-set coverage and I0 vs I2 stress evaluation (D3, D8, E03)."""
from __future__ import annotations
import numpy as np
from .uncertainty_calibration import run_coverage_simulation_T04


def evaluate_i0_vs_i2_coverage(true_h: np.ndarray, a: float = 0.40, true_Q: float = 0.08) -> dict:
    """Compare nominal iid Gaussian (I0) coverage against heavy-tailed/dependent observational (I2) stress."""
    i0 = run_coverage_simulation_T04(
        true_h=true_h, a=a, true_Q=true_Q, r_bar=0.95, noise_sd=0.002, sample_size_N=500, gamma=0.05, n_trials=400, seed=101
    )
    i2_stress = run_coverage_simulation_T04(
        true_h=true_h, a=a, true_Q=true_Q, r_bar=0.95, noise_sd=0.002, sample_size_N=500, gamma=0.05, n_trials=400, seed=202, heavy_tail_df=4.0
    )
    return {"I0_gaussian_nominal": i0, "I2_heavy_tail_diagnostic": i2_stress}
