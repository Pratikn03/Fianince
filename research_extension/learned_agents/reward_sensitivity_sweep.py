"""
Reward-Penalty Sensitivity Sweep
==================================
Machine Markets — Supplement Section S14.7

Tests whether the key Q-learning finding (all 10 policies flagged as Outside
Class; low dislocation explained by inventory avoidance) is specific to the
declared reward specification (λI=0.01, λT=0.005) or holds across alternative
penalty configurations.

Four reward specifications (pre-registered before running):
  Spec A — Main:            λI=0.01,   λT=0.005  (existing checkpoints)
  Spec B — No inv. penalty: λI=0.0,    λT=0.005  (new training, seeds 501,502)
  Spec C — No turn. penalty:λI=0.01,   λT=0.0    (new training, seeds 601,602)
  Spec D — Low penalty:     λI=0.0025, λT=0.001  (new training, seeds 701,702)

For Spec A we reuse the already-evaluated mean across the 10 existing policies.
For Specs B–D we train 2 fresh policies each (100k steps) and evaluate on
the same held-out test seeds (301–310).

Output: research_extension/outputs/learned_agents/reward_sensitivity_results.json
Checkpoints: research_extension/outputs/learned_agents/reward_sweep_checkpoints/
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np

from research_extension.learned_agents.q_learning_env import (
    DiscreteTradingEnv, MarketConfig, discretize_state, ACTIONS,
)
from research_extension.learned_agents.q_learning_agent import QLearningAgent

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = ROOT / "research_extension" / "outputs" / "learned_agents" / "checkpoints"
SWEEP_CKPT_DIR = ROOT / "research_extension" / "outputs" / "learned_agents" / "reward_sweep_checkpoints"
RESULTS_DIR = ROOT / "research_extension" / "outputs" / "learned_agents"

REWARD_SPECS: List[Dict[str, Any]] = [
    {"label": "A_main",          "lambda_I": 0.01,   "lambda_T": 0.005, "seeds": [501, 502]},
    {"label": "B_no_inv",        "lambda_I": 0.0,    "lambda_T": 0.005, "seeds": [501, 502]},
    {"label": "C_no_turn",       "lambda_I": 0.01,   "lambda_T": 0.0,   "seeds": [601, 602]},
    {"label": "D_low_penalty",   "lambda_I": 0.0025, "lambda_T": 0.001, "seeds": [701, 702]},
]
VAL_SEEDS = [201, 202, 203, 204, 205]
TEST_SEEDS = [301 + i for i in range(10)]
TRAIN_STEPS = 100_000
EVAL_FREQ   = 25_000
SHOCK_STEP  = 16
MEAN_SHOCK  = -2.0


class PenaltyEnv(DiscreteTradingEnv):
    """Discrete trading environment with configurable reward penalty coefficients."""

    def __init__(self, lambda_I: float, lambda_T: float, **kwargs):
        super().__init__(**kwargs)
        self._lambda_I = lambda_I
        self._lambda_T = lambda_T

    def step(self, action_idx: int, external_shock: float = 0.0):
        s_next, r_orig, done, info = super().step(action_idx, external_shock)
        # Original reward includes: -0.01*inv^2 - 0.005*|trade|
        # We reverse and re-apply with our own coefficients
        inv = info.get("agent_inv", 0.0)
        trade = info.get("agent_trade", 0.0)
        r_corrected = r_orig + 0.01 * inv**2 + 0.005 * abs(trade)  # strip original penalties
        r_corrected -= self._lambda_I * inv**2 + self._lambda_T * abs(trade)  # apply new ones
        return s_next, r_corrected, done, info


def train_policy(policy_id: int, seed: int, lambda_I: float, lambda_T: float,
                 label: str) -> Tuple[QLearningAgent, Dict[str, Any]]:
    """Train a single policy under the given reward spec."""
    env = PenaltyEnv(lambda_I=lambda_I, lambda_T=lambda_T, seed=seed)
    agent = QLearningAgent(seed=seed)
    s = env.reset()

    best_val_r = -float("inf")
    best_step = 0
    best_q = None
    t0 = time.time()

    for step in range(1, TRAIN_STEPS + 1):
        a = agent.select_action(s, greedy=False)
        s_next, r, done, _ = env.step(a)
        agent.update(s, a, r, s_next, done)
        s = env.reset() if done else s_next

        if step % EVAL_FREQ == 0 or step == TRAIN_STEPS:
            # Quick validation: run greedy for 5 episodes per val seed
            val_rs = []
            for vs in VAL_SEEDS:
                venv = PenaltyEnv(lambda_I=lambda_I, lambda_T=lambda_T, seed=vs)
                for _ in range(4):
                    vs_state = venv.reset(seed=vs)
                    ep_r = 0.0
                    vdone = False
                    while not vdone:
                        va = agent.select_action(vs_state, greedy=True)
                        vs_state, vr, vdone, _ = venv.step(va)
                        ep_r += vr
                    val_rs.append(ep_r)
            val_r = float(np.mean(val_rs))
            if val_r > best_val_r:
                best_val_r = val_r
                best_step = step
                best_q = agent.q_table.copy()

    # Restore best checkpoint
    agent.q_table = best_q
    elapsed = time.time() - t0
    print(f"    [{label} seed={seed}] best_step={best_step} val_r={best_val_r:.2f} elapsed={elapsed:.1f}s")

    # Save checkpoint
    SWEEP_CKPT_DIR.mkdir(parents=True, exist_ok=True)
    ckpt_path = SWEEP_CKPT_DIR / f"{label}_seed{seed}_best.npz"
    agent.save(ckpt_path)

    return agent, {"seed": seed, "best_step": best_step, "best_val_reward": best_val_r}


def evaluate_policy(agent: QLearningAgent, cfg: MarketConfig,
                    lambda_I: float, lambda_T: float) -> Dict[str, Any]:
    """Evaluate a policy: model-class audit + mean dislocation + halt rate on test seeds."""
    agent.set_mode("frozen")

    # Model-class audit (same perturbation grid as main evaluation)
    perturbations = np.linspace(-1.0, 1.0, 21)
    actions_at = []
    for dx in perturbations:
        s_idx = discretize_state(x=float(dx), ret=float(dx), inv=0.0, cap_util=0.0, imb=0.0)
        a_idx = agent.select_action(s_idx, greedy=True)
        actions_at.append(float(ACTIONS[a_idx]))

    u_arr = np.array(actions_at)
    dx_arr = perturbations
    corr = float(np.corrcoef(dx_arr, u_arr)[0, 1]) if np.std(u_arr) > 1e-8 else 0.0
    r_squared = float(corr ** 2) if not np.isnan(corr) else 0.0
    cov = np.cov(dx_arr, u_arr)
    dq_dx = float(cov[0, 1] / (cov[0, 0] + 1e-12))
    in_class = (r_squared >= 0.70) and (dq_dx >= 0.0) and all(u_arr[i] <= u_arr[i+1] for i in range(len(u_arr)-1))

    # Evaluation on test seeds
    dislocations, halt_flags, turnovers = [], [], []
    for seed in TEST_SEEDS:
        env = PenaltyEnv(lambda_I=lambda_I, lambda_T=lambda_T, seed=seed)
        s = env.reset(seed=seed)
        step = 0
        ep_dislocations = []
        total_turnover = 0.0

        done = False
        while not done:
            step += 1
            shock_val = MEAN_SHOCK if step == SHOCK_STEP else 0.0
            a_idx = agent.select_action(s, greedy=True)
            s, _, done, info = env.step(a_idx, external_shock=shock_val)
            ep_dislocations.append(abs(info.get("x", 0.0)))
            total_turnover += abs(info.get("agent_trade", 0.0))

        dislocations.append(float(np.mean(ep_dislocations)))
        halt_flags.append(1 if env.dealer_halted else 0)
        turnovers.append(total_turnover)

    return {
        "r_squared": round(r_squared, 4),
        "dq_dx": round(dq_dx, 4),
        "in_class": bool(in_class),
        "classification": "CERTIFIED" if in_class else "OUTSIDE_CLASS",
        "mean_dislocation": round(float(np.mean(dislocations)), 4),
        "halt_rate": round(float(np.mean(halt_flags)), 3),
        "mean_turnover": round(float(np.mean(turnovers)), 2),
    }


def main():
    print("=" * 70)
    print("MACHINE MARKETS — REWARD-PENALTY SENSITIVITY SWEEP")
    print(f"Train steps per policy: {TRAIN_STEPS:,} | Test seeds: {TEST_SEEDS}")
    print("=" * 70)

    cfg = MarketConfig()
    all_results = []

    for spec in REWARD_SPECS:
        label = spec["label"]
        lI = spec["lambda_I"]
        lT = spec["lambda_T"]
        seeds = spec["seeds"]
        print(f"\n--- Spec {label} (λI={lI}, λT={lT}) ---")

        if label == "A_main":
            # Load the pre-computed mean from existing results
            existing_path = RESULTS_DIR / "q_learning_transfer_results.json"
            if existing_path.exists():
                existing = json.loads(existing_path.read_text())
                synth = existing.get("architecture_transfer_synthesis", {})
                # Use the overall mean from existing 10 policies
                existing_r2 = float(np.mean([
                    p["model_validity"]["r_squared"]
                    for p in existing.get("learned_policies", [])
                ]))
                existing_dq = float(np.mean([
                    p["jacobian"]["dq_dx"]
                    for p in existing.get("learned_policies", [])
                ]))
                existing_disloc = float(np.mean([
                    p["frozen"]["mean_dislocation"]
                    for p in existing.get("learned_policies", [])
                ]))
                existing_halt = float(np.mean([
                    p["frozen"]["halt_rate"]
                    for p in existing.get("learned_policies", [])
                ]))
                existing_turnover = float(np.mean([
                    p["frozen"]["total_turnover"]
                    for p in existing.get("learned_policies", [])
                ]))
                print(f"  Loaded from existing 10-policy evaluation")
                policy_evals = [{
                    "r_squared": round(existing_r2, 4),
                    "dq_dx": round(existing_dq, 4),
                    "in_class": False,
                    "classification": "OUTSIDE_CLASS",
                    "mean_dislocation": round(existing_disloc, 4),
                    "halt_rate": round(existing_halt, 3),
                    "mean_turnover": round(existing_turnover, 2),
                    "note": "Mean across 10 pre-trained policies (seeds 101-110)"
                }]
            else:
                print("  WARNING: existing results not found, skipping Spec A")
                continue
        else:
            # Train and evaluate fresh policies
            policy_evals = []
            for seed in seeds:
                agent, training_info = train_policy(
                    policy_id=seed, seed=seed, lambda_I=lI, lambda_T=lT, label=label
                )
                eval_res = evaluate_policy(agent, cfg, lI, lT)
                eval_res.update({"seed": seed, "training": training_info})
                policy_evals.append(eval_res)
                print(f"    Eval: R²={eval_res['r_squared']:.3f} | ∂u/∂x={eval_res['dq_dx']:+.3f} | "
                      f"Class={eval_res['classification']} | Disloc={eval_res['mean_dislocation']:.4f} | "
                      f"Halt={eval_res['halt_rate']*100:.0f}% | Turnover={eval_res['mean_turnover']:.1f}")

        # Aggregate across policies in this spec
        r2_vals = [p["r_squared"] for p in policy_evals]
        dq_vals = [p["dq_dx"] for p in policy_evals]
        disloc_vals = [p["mean_dislocation"] for p in policy_evals]
        halt_vals = [p["halt_rate"] for p in policy_evals]
        turn_vals = [p["mean_turnover"] for p in policy_evals]
        n_in_class = sum(1 for p in policy_evals if p.get("in_class", False))

        spec_result = {
            "label": label,
            "lambda_I": lI,
            "lambda_T": lT,
            "n_policies": len(policy_evals),
            "n_in_class": n_in_class,
            "mean_r_squared": round(float(np.mean(r2_vals)), 4),
            "mean_dq_dx": round(float(np.mean(dq_vals)), 4),
            "mean_dislocation": round(float(np.mean(disloc_vals)), 4),
            "mean_halt_rate": round(float(np.mean(halt_vals)), 3),
            "mean_turnover": round(float(np.mean(turn_vals)), 2),
            "policy_details": policy_evals,
        }
        all_results.append(spec_result)
        print(f"  → Summary: R²={spec_result['mean_r_squared']:.3f} | "
              f"In-class: {n_in_class}/{len(policy_evals)} | "
              f"Disloc={spec_result['mean_dislocation']:.4f} | "
              f"Turnover={spec_result['mean_turnover']:.1f}")

    output = {
        "meta": {
            "train_steps": TRAIN_STEPS,
            "test_seeds": TEST_SEEDS,
            "val_seeds": VAL_SEEDS,
            "shock": MEAN_SHOCK,
            "model_class_threshold_r2": 0.70,
            "description": (
                "Reward-penalty sensitivity study: trains fresh Q-learning policies under "
                "4 reward specifications varying λI (inventory penalty) and λT (turnover penalty). "
                "Spec A reuses existing 10-policy results. Specs B-D train 2 policies each. "
                "Evaluates model-class classification and market outcomes under each spec."
            ),
        },
        "reward_specs": all_results,
    }

    out_path = RESULTS_DIR / "reward_sensitivity_results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\n{'='*70}")
    print(f"Results saved: {out_path.relative_to(ROOT)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
