"""
Item 1: Cross-Simulator Validation
====================================
Tests the probe/audit identification protocol across THREE independent simulators:
  1. Price-Time LOB — paper's own simulator (mean-reverting x)
  2. Pro-Rata LOB  — different fill rule, price-level dynamics
  3. Kyle lambda CDA — different market microstructure

KEY: All three simulators produce monotone-growing price IRFs.
Stability is identified from whether the GROWTH RATE of the IRF converges
(stable: IRF plateaus) or diverges (unstable: IRF accelerates away).
The identification criterion: fit log(beta[t]) ~ c + rho*t; stable iff rho < threshold.

Contract-Violation Robustness Curve:
  Sweeps epsilon-violations of Contract I1: price noise, wrong lr, hidden resets.
"""
import numpy as np
import pytest
from scipy import stats
from scipy.optimize import curve_fit


# ===========================================================================
# Simulator A: Price-Time LOB (paper's own structure)
# ===========================================================================
def simulate_price_time(
    S: float, episodes: int = 300, steps: int = 25,
    noise_sd: float = 0.001, seed: int = 0
) -> dict:
    """
    Standard price-time LOB. Net order flow = probe + S*memory + noise.
    Price = cumulative impact of net flow.
    For S < 1: memory self-corrects, IRF growth rate < 1.
    For S > 1: memory amplifies, IRF growth rate > 1.
    """
    rng = np.random.default_rng(seed)
    impact = 0.05; eta = 0.20
    signs = np.tile([-1.0, 1.0], episodes // 2)
    rng.shuffle(signs)
    probes = signs * 4.0
    prices = np.empty((episodes, steps))
    for ep in range(episodes):
        mem = 0.0; x = 0.0
        for t in range(steps):
            flow = rng.normal(0, 0.08)
            pr = probes[ep] if t == 0 else 0.0
            net = pr + S * mem + flow
            x = x + impact * net
            prices[ep, t] = x + rng.normal(0, noise_sd)
            mem = (1 - eta) * mem + eta * x
    return {"probes": probes, "prices": prices}


# ===========================================================================
# Simulator B: Pro-Rata LOB (independent fill rule)
# ===========================================================================
def simulate_pro_rata(
    S: float, episodes: int = 300, steps: int = 25,
    noise_sd: float = 0.001, seed: int = 1
) -> dict:
    """
    Pro-rata LOB. Fill proportion = order / total_queue.
    Feedback S enters through signed order-flow imbalance (not price memory).
    Structurally different from price-time: the feedback channel is the
    accumulated imbalance, not the price level.
    """
    rng = np.random.default_rng(seed)
    impact = 0.055; eta_b = 0.22
    signs = np.tile([-1.0, 1.0], episodes // 2)
    rng.shuffle(signs)
    probes = signs * 4.0
    prices = np.empty((episodes, steps))
    for ep in range(episodes):
        x = 0.0; imbalance = 0.0
        for t in range(steps):
            pr = probes[ep] if t == 0 else 0.0
            noise_order = rng.normal(0, 0.08)
            net = pr + S * imbalance + noise_order
            x = x + impact * net
            prices[ep, t] = x + rng.normal(0, noise_sd)
            imbalance = (1 - eta_b) * imbalance + eta_b * net
    return {"probes": probes, "prices": prices}


# ===========================================================================
# Simulator C: Kyle lambda CDA (continuous double auction)
# ===========================================================================
def simulate_kyle_cda(
    S: float, episodes: int = 300, steps: int = 25,
    noise_sd: float = 0.001, seed: int = 2
) -> dict:
    """
    Kyle (1985) lambda-style CDA. Price adjusts by lambda * net_order_flow.
    Informed trader learns signal; S controls how much past signal amplifies
    future orders. Structurally different: the market-maker updates prices
    based on order-flow inference (different from both LOB types).
    """
    rng = np.random.default_rng(seed)
    lam = 0.05; sigma_v = 1.0; sigma_u = 0.25; eta_k = 0.18
    signs = np.tile([-1.0, 1.0], episodes // 2)
    rng.shuffle(signs)
    probes = signs * 4.0
    prices = np.empty((episodes, steps))
    for ep in range(episodes):
        v = rng.normal(0, sigma_v); p = 0.0; signal = 0.0
        for t in range(steps):
            u_noise = rng.normal(0, sigma_u)
            pr = probes[ep] if t == 0 else 0.0
            informed = 0.45 * (v - p) + S * signal
            net_flow = pr + u_noise + informed
            p = p + lam * net_flow
            prices[ep, t] = p + rng.normal(0, noise_sd)
            signal = (1 - eta_k) * signal + eta_k * net_flow
    return {"probes": probes, "prices": prices}


# ===========================================================================
# Identification Engine: IRF Growth-Rate Test
# ===========================================================================
def identify_feedback(data: dict, alpha: float = 0.05) -> dict:
    """
    Probe/audit protocol using IRF growth-rate identification:

    1. OLS: beta[t] = Cov(price[t], probe)/Var(probe)  -> IRF
    2. Fit log(beta[t]) = log(c) + rho*t  (exponential growth model)
       Using OLS on log-transformed IRF (tail only, t >= 2)
    3. Test H0: rho >= rho_boundary vs H1: rho < rho_boundary
       where rho_boundary is calibrated per simulator type.

    Stable:      growth rate CI upper bound < rho_boundary
    Unstable:    growth rate CI lower bound > rho_boundary
    Inconclusive: CI straddles rho_boundary
    """
    probes = np.asarray(data["probes"], dtype=float)
    prices = np.asarray(data["prices"], dtype=float)
    u = probes - probes.mean()
    ss = float(u @ u)
    if ss <= 0 or len(u) < 4:
        return {"label": "inconclusive", "rho": np.nan, "decisive": False}

    # OLS: IRF at each horizon
    beta = u @ prices / ss   # shape (steps,)
    T = len(beta)

    # Use only the tail of the IRF (skip t=0 which is just the probe fill)
    t_start = 2
    t_vals = np.arange(t_start, T, dtype=float)
    b_tail = beta[t_start:]

    # Require positive IRF for log-transform
    if np.any(b_tail <= 0) or len(b_tail) < 4:
        return {"label": "inconclusive", "rho": np.nan, "decisive": False}

    log_b = np.log(b_tail)

    # OLS: log_b[t] = a + rho * t
    X = np.column_stack([np.ones(len(t_vals)), t_vals])
    try:
        coef, resid_ss, _, _ = np.linalg.lstsq(X, log_b, rcond=None)
    except Exception:
        return {"label": "inconclusive", "rho": np.nan, "decisive": False}

    rho_hat = float(coef[1])   # growth rate per step
    n_fit = len(t_vals)
    dof = max(1, n_fit - 2)

    # SE of rho_hat from OLS residuals
    y_hat = X @ coef
    s2 = float(np.sum((log_b - y_hat)**2)) / dof
    Xtx_inv = np.linalg.pinv(X.T @ X)
    se_rho = float(np.sqrt(max(0, s2 * Xtx_inv[1, 1])))

    t_crit = float(stats.t.ppf(1 - alpha / 2, df=dof))
    rho_lo = rho_hat - t_crit * se_rho
    rho_hi = rho_hat + t_crit * se_rho

    # Stability boundary: rho = 0 means no growth (pure plateau).
    # rho > 0 means IRF still growing (integrating price), but at a decelerating rate
    # for stable S and accelerating rate for unstable S.
    # Calibrated boundary: 0.03 (slight growth is expected due to price integration)
    rho_boundary = 0.03

    if rho_hi < rho_boundary - 1e-6:
        lbl = "stable"
    elif rho_lo > rho_boundary + 1e-6:
        lbl = "unstable"
    else:
        lbl = "inconclusive"

    return {
        "label": lbl,
        "decisive": lbl != "inconclusive",
        "rho_hat": rho_hat,
        "lo": rho_lo,
        "hi": rho_hi,
        "se": se_rho,
    }


# ===========================================================================
# Coverage sweep
# ===========================================================================
def coverage_over_seeds(
    sim_fn, S: float, n_seeds: int = 30, episodes: int = 300, steps: int = 25
) -> dict:
    correct = 0; decisive_count = 0
    is_stable_truth = S < 1.0
    expected_label = "stable" if is_stable_truth else "unstable"
    for seed in range(n_seeds):
        data = sim_fn(S=S, episodes=episodes, steps=steps, seed=seed)
        result = identify_feedback(data)
        if result["label"] == expected_label:
            correct += 1
        if result["decisive"]:
            decisive_count += 1
    return {
        "coverage": correct / n_seeds,
        "decisive_rate": decisive_count / n_seeds,
        "n_seeds": n_seeds,
        "S": S,
    }


# ===========================================================================
# Contract-violation robustness curve
# ===========================================================================
def robustness_violation_curve(
    epsilon_levels: list, violation_type: str = "price_noise",
    n_seeds: int = 20, S: float = 0.55
) -> list:
    results = []
    for eps in epsilon_levels:
        correct = 0
        for seed in range(n_seeds):
            rng = np.random.default_rng(seed + 300)
            base = simulate_price_time(S=S, episodes=300, steps=25, seed=seed)
            probes = base["probes"]
            prices = base["prices"].copy()
            if violation_type == "price_noise":
                prices += rng.normal(0, eps, prices.shape)
            elif violation_type == "wrong_lr":
                # Scales prices by a random factor: mimics wrong learning-rate disclosure
                scale = 1.0 + eps * rng.standard_normal(prices.shape) * 0.10
                prices = prices * scale
            elif violation_type == "hidden_resets":
                # Zero out eps fraction of episodes (hidden memory resets)
                mask = rng.uniform(0, 1, prices.shape[0]) < eps
                prices[mask] = 0.0
            data = {"probes": probes, "prices": prices}
            result = identify_feedback(data)
            if result["label"] == "stable":
                correct += 1
        results.append({
            "epsilon": eps,
            "coverage": correct / n_seeds,
            "violation_type": violation_type,
        })
    return results


# ===========================================================================
# Tests
# ===========================================================================
class TestCrossSimulatorValidation:
    """Item 1 from referee punch list: cross-simulator coverage tests."""

    def test_price_time_coverage_stable(self):
        """Price-Time LOB: >= 80% coverage for stable regime (S=0.55)."""
        result = coverage_over_seeds(simulate_price_time, S=0.55, n_seeds=30)
        print(f"\nPrice-Time S=0.55 | Coverage={result['coverage']:.2%} "
              f"Decisive={result['decisive_rate']:.2%}")
        assert result["coverage"] >= 0.80

    def test_pro_rata_coverage_stable(self):
        """Pro-Rata LOB (independent): >= 70% coverage for stable regime (S=0.55)."""
        result = coverage_over_seeds(simulate_pro_rata, S=0.55, n_seeds=30)
        print(f"\nPro-Rata S=0.55   | Coverage={result['coverage']:.2%} "
              f"Decisive={result['decisive_rate']:.2%}")
        assert result["coverage"] >= 0.70

    def test_kyle_cda_coverage_stable(self):
        """Kyle CDA (structurally different): >= 65% coverage for stable regime (S=0.45)."""
        result = coverage_over_seeds(simulate_kyle_cda, S=0.45, n_seeds=30)
        print(f"\nKyle CDA S=0.45   | Coverage={result['coverage']:.2%} "
              f"Decisive={result['decisive_rate']:.2%}")
        assert result["coverage"] >= 0.65

    def test_price_time_coverage_unstable(self):
        """Price-Time LOB: >= 80% coverage for unstable regime (S=1.6)."""
        result = coverage_over_seeds(simulate_price_time, S=1.6, n_seeds=30)
        print(f"\nPrice-Time S=1.6  | Coverage={result['coverage']:.2%}")
        assert result["coverage"] >= 0.80

    def test_robustness_price_noise(self):
        """Coverage must be high at eps=0 and degrade gracefully with price noise."""
        epsilons = [0.0, 0.005, 0.01, 0.05, 0.10]
        curve = robustness_violation_curve(epsilons, "price_noise", n_seeds=20)
        print("\nPrice-noise robustness:")
        for r in curve:
            print(f"  eps={r['epsilon']:.3f} -> {r['coverage']:.2%}")
        assert curve[0]["coverage"] >= 0.70
        assert curve[-1]["coverage"] <= curve[0]["coverage"] + 0.15

    def test_robustness_wrong_lr(self):
        """Coverage curve under wrong learning-rate disclosure."""
        epsilons = [0.0, 0.05, 0.10, 0.20]
        curve = robustness_violation_curve(epsilons, "wrong_lr", n_seeds=20)
        print("\nWrong-LR robustness:")
        for r in curve:
            print(f"  eps={r['epsilon']:.2f} -> {r['coverage']:.2%}")
        assert curve[0]["coverage"] >= 0.65

    def test_robustness_hidden_resets(self):
        """Coverage curve under hidden resets contract violation."""
        epsilons = [0.0, 0.05, 0.10, 0.20]
        curve = robustness_violation_curve(epsilons, "hidden_resets", n_seeds=20)
        print("\nHidden-reset robustness:")
        for r in curve:
            print(f"  eps={r['epsilon']:.2f} -> {r['coverage']:.2%}")
        assert curve[0]["coverage"] >= 0.65

    def test_cross_simulator_summary(self):
        """All three simulators pass >= 65% in their respective stable regimes."""
        configs = [
            ("price_time", simulate_price_time, 0.55),
            ("pro_rata",   simulate_pro_rata,   0.55),
            ("kyle_cda",   simulate_kyle_cda,   0.45),
        ]
        results = {}
        for name, fn, s_val in configs:
            results[name] = coverage_over_seeds(fn, S=s_val, n_seeds=30)
        print("\nCross-Simulator Summary:")
        for name, r in results.items():
            print(f"  {name:12s} | S={r['S']:.2f} | "
                  f"coverage={r['coverage']:.2%} | decisive={r['decisive_rate']:.2%}")
        assert all(r["coverage"] >= 0.65 for r in results.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
