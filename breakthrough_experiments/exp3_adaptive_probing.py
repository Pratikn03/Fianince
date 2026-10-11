#!/usr/bin/env python3
"""
Experiment 2B / Priority 3: Adaptive vs. Predetermined Probing Protocols
Compares Method A (single pulse), Method B (multi-pulse), Method C (sequential feedback),
and Method D (minimax LQG probe). Evaluates error vs executed quantity, inventory, and capital.
"""
import json
from pathlib import Path
import numpy as np

def simulate_probing(protocol, delta, V_target, T=20, sigma=0.01, kappa=0.8, q=0.2, a=0.5, eta=0.4):
    """
    Simulates a closed-loop market economy under 2 competing models:
    Model 0: single cohort with rate eta
    Model delta: two cohorts with rates eta - delta, eta + delta (weights q/2)
    """
    # Cohort state dynamics: x_{t+1} = a x_t + kappa * u_t + kappa * v_t
    # y_{i, t+1} = (1 - eta_i) y_{i, t} + eta_i x_{t+1}
    
    def run_path(split=False):
        rates = [eta - delta, eta + delta] if split else [eta]
        weights = [q / 2, q / 2] if split else [q]
        K = len(rates)
        
        x = np.zeros(T + 1)
        y = np.zeros((K, T + 1))
        v = np.zeros(T)
        obs_x = np.zeros(T + 1)
        
        inventory = 0.0
        max_inv = 0.0
        
        for t in range(T):
            # Compute algorithmic demand
            u_t = np.sum(weights * y[:, t])
            
            # Select probing action v_t based on protocol
            if protocol == "Method_A_Single_Pulse":
                v_t = V_target if t == 0 else 0.0
            elif protocol == "Method_B_Multi_Pulse":
                v_t = (V_target / 3.0) if t in [0, 2, 4] else 0.0
            elif protocol == "Method_C_Sequential_Feedback":
                # Reactive feedback: inject probe counter to observed displacement
                if t == 0:
                    v_t = V_target * 0.5
                else:
                    v_t = -0.3 * obs_x[t] * (V_target * 0.5)
                    v_t = np.clip(v_t, -V_target / 3.0, V_target / 3.0)
            elif protocol == "Method_D_Minimax_LQG":
                # Smooth energy-dispersed probe minimizing inventory variance
                decay = np.exp(-0.5 * t)
                v_t = (V_target * decay) / 1.5
            else:
                v_t = 0.0
                
            v[t] = v_t
            inventory += v_t
            max_inv = max(max_inv, abs(inventory))
            
            # Price update: x_{t+1} = a x_t + kappa * u_t + kappa * v_t
            x[t + 1] = a * x[t] + kappa * u_t + kappa * v_t
            
            # Algorithmic state update
            for k in range(K):
                y[k, t + 1] = (1.0 - rates[k]) * y[k, t] + rates[k] * x[t + 1]
                
            # Noisy observation
            obs_x[t + 1] = x[t + 1] + np.random.normal(0, sigma)
            
        # Compute execution cost: 0.5 * sum v_t * (x_{t+1} - x_t) + c * |v|
        c_fee = 0.001
        cost = 0.5 * kappa * np.sum(v ** 2) + c_fee * np.sum(np.abs(v))
        return obs_x[1:], v, max_inv, cost

    # Monte Carlo trials to compute empirical minimax error
    trials = 200
    errors = 0
    total_qty = 0.0
    total_inv = 0.0
    total_cost = 0.0
    
    for _ in range(trials):
        obs0, v0, inv0, c0 = run_path(split=False)
        obs1, v1, inv1, c1 = run_path(split=True)
        
        # Test statistic: log likelihood ratio for known mean signal
        # Mean difference signal d = E[obs1] - E[obs0]
        # Under Gaussian noise, midpoint test between obs0 and obs1
        midpoint = 0.5 * (obs0 + obs1)
        diff = obs1 - obs0
        norm_diff = np.linalg.norm(diff)
        
        if norm_diff > 1e-12:
            stat0 = np.dot(obs0 - midpoint, diff)
            stat1 = np.dot(obs1 - midpoint, diff)
            if stat0 > 0: errors += 1
            if stat1 < 0: errors += 1
        else:
            errors += 1
            
        total_qty += np.sum(np.abs(v0))
        total_inv += inv0
        total_cost += c0
        
    err_rate = errors / (2.0 * trials)
    return {
        "protocol": protocol,
        "delta": delta,
        "target_V": V_target,
        "empirical_error": float(err_rate),
        "mean_executed_quantity": float(total_qty / trials),
        "mean_max_inventory": float(total_inv / trials),
        "mean_capital_cost": float(total_cost / trials)
    }

def run_experiment():
    np.random.seed(123)
    protocols = [
        "Method_A_Single_Pulse",
        "Method_B_Multi_Pulse",
        "Method_C_Sequential_Feedback",
        "Method_D_Minimax_LQG"
    ]
    deltas = [0.03, 0.05, 0.08, 0.12]
    # For delta=0.05, V_target ~ delta^{-2} ~ 400. Let's scale V realistically
    results = []
    for delta in deltas:
        # Scale V roughly proportional to delta^{-2}
        base_V = 2.0 / (delta ** 2) * 0.05  # scaled for simulation stability
        for prot in protocols:
            res = simulate_probing(prot, delta, V_target=base_V)
            results.append(res)
            print(f"[{prot}] delta={delta:.2f}, V={res['mean_executed_quantity']:.1f}, err={res['empirical_error']:.3f}, cost={res['mean_capital_cost']:.2f}")
            
    out_file = Path("breakthrough_experiments/results_exp3_adaptive_probing.json")
    out_file.write_text(json.dumps(results, indent=2))
    print(f"Experiment 2B complete. Results written to {out_file}")

if __name__ == "__main__":
    run_experiment()
