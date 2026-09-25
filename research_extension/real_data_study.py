"""Phase 7B: Real-Market Data Ingestion and Empirical Validation Study (Coinbase).

Downloads and analyzes high-frequency trade and quote data from Coinbase Exchange
across 10 digital asset markets:
  ['BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD',
   'AVAX-USD', 'LINK-USD', 'LTC-USD', 'DOT-USD', 'NEAR-USD']

Methodological Design:
  Strict Temporal Split (Genuinely Held-Out Validation):
  Period A (Estimation Window, first 70% of candle bars):
    Estimates closed-loop feedback parameter S_hat_A = |a_A| + sum_{tau in {1,2,5}} |rho_A(tau)|,
    along with Period A realized volatility and quoted spread.
  Period B (Evaluation Window, subsequent 30% of candle bars):
    Measures held-out 1-minute return autocorrelation rho_{1, B}.
    The outcome rho_{1, B} NEVER enters the construction of the predictor S_hat_A,
    eliminating mechanical circularity.

Model:
  rho_{i, 1}^{(B)} = alpha_0 + alpha_1 * S_hat_{i}^{(A)} + alpha_2 * Spread_i + alpha_3 * Vol_i^{(A)} + e_i
"""

import json
import os
import time
import urllib.request
import numpy as np


ASSETS = [
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
    "DOGE-USD",
    "ADA-USD",
    "AVAX-USD",
    "LINK-USD",
    "LTC-USD",
    "DOT-USD",
    "NEAR-USD",
]


def fetch_coinbase_asset_data(product_id):
    """Fetch order book spread, recent tick trades, and 1-minute candle bars with offline cache."""
    cached_path = "research_extension/data/real_market_empirical_panel.json"
    headers = {"User-Agent": "Mozilla/5.0 (MachineMarkets/1.0 Research)"}
    base = "https://api.exchange.coinbase.com/products"

    try:
        # 1. Level 1 Book for spread
        book_url = f"{base}/{product_id}/book?level=1"
        req = urllib.request.Request(book_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            book = json.loads(resp.read().decode())
        best_bid = float(book["bids"][0][0])
        best_ask = float(book["asks"][0][0])
        midpoint = (best_bid + best_ask) / 2.0
        rel_spread_bps = ((best_ask - best_bid) / midpoint) * 10000.0

        # 2. 1-minute candles (300 bars)
        candles_url = f"{base}/{product_id}/candles?granularity=60"
        req = urllib.request.Request(candles_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            candles = json.loads(resp.read().decode())
        candles.sort(key=lambda c: c[0])
        closes = np.array([c[4] for c in candles], dtype=float)
        volumes = np.array([c[5] for c in candles], dtype=float)

        # 3. Recent 1,000 tick trades for signed order flow
        trades_url = f"{base}/{product_id}/trades"
        req = urllib.request.Request(trades_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            trades = json.loads(resp.read().decode())
        trades.sort(key=lambda tr: tr["trade_id"])
        trade_prices = np.array([float(tr["price"]) for tr in trades])
        trade_sizes = np.array([float(tr["size"]) for tr in trades])
        trade_signs = np.array([1.0 if tr["side"] == "buy" else -1.0 for tr in trades])
        signed_flow = trade_sizes * trade_signs

        return {
            "product_id": product_id,
            "midpoint": midpoint,
            "rel_spread_bps": float(rel_spread_bps),
            "closes": closes.tolist(),
            "volumes": volumes.tolist(),
            "signed_flow": signed_flow.tolist(),
            "trade_prices": trade_prices.tolist(),
        }
    except Exception as e:
        print(f"    Live fetch warning for {product_id}: {e}. Checking cache...")
        if os.path.exists(cached_path):
            with open(cached_path, "r") as f:
                cached = json.load(f)
            if product_id in cached:
                print(f"    Loaded {product_id} from cache.")
                return cached[product_id]
        raise RuntimeError(f"Could not load data for {product_id}: {e}")


def analyze_asset_temporal_split(data, train_ratio=0.70):
    """Estimate feedback strictly on Period A and evaluate on Period B."""
    closes = np.array(data["closes"])
    returns = np.diff(np.log(closes))
    n = len(returns)
    n_A = int(n * train_ratio)
    
    ret_A = returns[:n_A]
    ret_B = returns[n_A:]

    # Autocorrelation helper
    def autocorr(x, lag):
        if len(x) <= lag + 2:
            return 0.0
        c0 = np.var(x)
        if c0 < 1e-15:
            return 0.0
        return float(np.mean((x[:-lag] - np.mean(x)) * (x[lag:] - np.mean(x))) / c0)

    # Period A estimates:
    a_A = float(np.cov(ret_A[1:], ret_A[:-1])[0, 1] / np.var(ret_A[:-1])) if len(ret_A) > 5 and np.var(ret_A[:-1]) > 1e-15 else 0.0
    a_A = max(-0.95, min(0.95, a_A))
    
    rho1_A = autocorr(ret_A, 1)
    rho2_A = autocorr(ret_A, 2)
    rho5_A = autocorr(ret_A, 5)
    
    # Structural feedback proxy strictly from Period A:
    q_hat_A = abs(rho1_A) + abs(rho2_A) + abs(rho5_A)
    s_hat_A = abs(a_A) + q_hat_A
    vol_A = float(np.std(ret_A) * 10000.0)

    # Period B held-out outcome:
    rho1_B = autocorr(ret_B, 1)

    return {
        "product_id": data["product_id"],
        "midpoint": data["midpoint"],
        "rel_spread_bps": data["rel_spread_bps"],
        "vol_bps_A": vol_A,
        "a_hat_A": a_A,
        "q_hat_A": q_hat_A,
        "s_hat_A": s_hat_A,
        "rho1_A": rho1_A,
        "rho1_B": rho1_B,  # Genuinely held-out
    }


def run_empirical_validation_study():
    print("=== COINBASE NON-CIRCULAR EMPIRICAL VALIDATION STUDY ===")
    os.makedirs("research_extension/data", exist_ok=True)
    os.makedirs("research_extension/outputs", exist_ok=True)

    panel_records = []
    raw_data = {}

    for p_id in ASSETS:
        print(f"  Processing {p_id}...")
        try:
            d = fetch_coinbase_asset_data(p_id)
            raw_data[p_id] = d
            stats = analyze_asset_temporal_split(d)
            panel_records.append(stats)
            time.sleep(0.1)
        except Exception as e:
            print(f"    Error processing {p_id}: {e}")

    # Save raw data cache if new
    cache_path = "research_extension/data/real_market_empirical_panel.json"
    if not os.path.exists(cache_path):
        with open(cache_path, "w") as f:
            json.dump(raw_data, f)

    n_assets = len(panel_records)
    print(f"\nSuccessfully processed {n_assets} digital assets on Coinbase.")

    # Cross-sectional regression:
    # Dependent variable: rho1_B (Held-out Period B 1-minute return autocorrelation)
    # Regressors: [1, s_hat_A, rel_spread_bps, vol_bps_A]
    Y = np.array([r["rho1_B"] for r in panel_records])
    X = np.column_stack([
        np.ones(n_assets),
        np.array([r["s_hat_A"] for r in panel_records]),
        np.array([r["rel_spread_bps"] for r in panel_records]),
        np.array([r["vol_bps_A"] for r in panel_records]),
    ])

    beta_ols, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
    residuals = Y - X @ beta_ols
    dof = max(1, n_assets - X.shape[1])
    sigma_sq = float(np.sum(residuals**2) / dof)
    cov_beta = sigma_sq * np.linalg.pinv(X.T @ X)
    se_beta = np.sqrt(np.maximum(1e-15, np.diag(cov_beta)))
    t_stats = beta_ols / se_beta

    ss_tot = np.sum((Y - np.mean(Y))**2)
    r_squared = 1.0 - (np.sum(residuals**2) / ss_tot) if ss_tot > 1e-15 else 0.0

    regression_result = {
        "n_assets": n_assets,
        "protocol": "Strict Temporal Split (Period A Estimation -> Period B Held-Out Validation)",
        "dependent_var": "Period B Return Autocorrelation (rho_{1, B})",
        "r_squared": float(r_squared),
        "coefficients": {
            "intercept": {"estimate": float(beta_ols[0]), "std_err": float(se_beta[0]), "t_stat": float(t_stats[0])},
            "s_hat_A (Period A Feedback Parameter)": {
                "estimate": float(beta_ols[1]),
                "std_err": float(se_beta[1]),
                "t_stat": float(t_stats[1]),
            },
            "rel_spread_bps": {
                "estimate": float(beta_ols[2]),
                "std_err": float(se_beta[2]),
                "t_stat": float(t_stats[2]),
            },
            "vol_bps_A (Period A Realized Volatility)": {
                "estimate": float(beta_ols[3]),
                "std_err": float(se_beta[3]),
                "t_stat": float(t_stats[3]),
            },
        },
        "asset_table": panel_records,
    }

    out_path = "research_extension/outputs/empirical_results.json"
    with open(out_path, "w") as f:
        json.dump(regression_result, f, indent=2)

    print(f"\nEmpirical regression finished. Results saved to {out_path}.")
    print("\n--- Non-Circular Cross-Sectional OLS Results ---")
    print(f"R-squared: {r_squared:.4f}")
    for var, vals in regression_result["coefficients"].items():
        print(f"  {var:40s}: Coeff = {vals['estimate']:+.4f} (SE = {vals['std_err']:.4f}, t = {vals['t_stat']:+.2f})")

    return regression_result


if __name__ == "__main__":
    run_empirical_validation_study()
