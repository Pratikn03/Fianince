"""
Training Pipeline for Tabular Q-Learning Agents
===============================================
Machine Markets — Learned-Agent Transfer Layer

Strict train / validation / test seed separation:
  - Training seeds: 101 .. 110
  - Validation seeds: 201 .. 205 (checkpoint selection)
  - Test seeds: 301 .. 310 (held-out evaluation)
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

from research_extension.learned_agents.q_learning_env import DiscreteTradingEnv, MarketConfig
from research_extension.learned_agents.q_learning_agent import QLearningAgent

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = ROOT / "research_extension" / "outputs" / "learned_agents" / "checkpoints"
RESULTS_DIR = ROOT / "research_extension" / "outputs" / "learned_agents"


def evaluate_policy(agent: QLearningAgent, val_seeds: List[int], n_episodes: int = 20) -> Dict[str, float]:
    """Evaluate agent greedily across validation seeds without exploration or updates."""
    prev_mode = agent.mode
    agent.set_mode("frozen")

    rewards = []
    equities = []
    max_dislocations = []
    dealer_halts = []

    for seed in val_seeds:
        env = DiscreteTradingEnv(seed=seed)
        for ep in range(n_episodes // len(val_seeds)):
            s = env.reset(seed=seed * 1000 + ep)
            ep_reward = 0.0
            done = False
            while not done:
                a = agent.select_action(s, greedy=True)
                s_next, r, done, info = env.step(a)
                ep_reward += r
                s = s_next
            rewards.append(ep_reward)
            equities.append(env.agent_equity)
            max_dislocations.append(abs(env.x))
            dealer_halts.append(1 if env.dealer_halted else 0)

    agent.set_mode(prev_mode)
    return {
        "mean_reward": float(np.mean(rewards)),
        "std_reward": float(np.std(rewards)),
        "mean_terminal_equity": float(np.mean(equities)),
        "mean_max_dislocation": float(np.mean(max_dislocations)),
        "dealer_halt_rate": float(np.mean(dealer_halts)),
    }


def train_single_agent(
    policy_id: int,
    train_seed: int,
    val_seeds: List[int],
    total_steps: int = 500_000,
    eval_freq: int = 50_000,
) -> Dict[str, Any]:
    """Train a single Q-learning policy with periodic validation checkpointing."""
    print(f"\n--- Training Policy {policy_id:02d} (seed={train_seed}, steps={total_steps:,}) ---")
    cfg = MarketConfig()
    env = DiscreteTradingEnv(config=cfg, seed=train_seed)
    agent = QLearningAgent(seed=train_seed)

    s = env.reset()
    best_val_reward = -float("inf")
    best_step = 0
    history = []

    t0 = time.time()
    for step in range(1, total_steps + 1):
        a = agent.select_action(s, greedy=False)
        s_next, r, done, info = env.step(a)
        agent.update(s, a, r, s_next, done)

        if done:
            s = env.reset()
        else:
            s = s_next

        # Validation check and checkpointing
        if step % eval_freq == 0 or step == total_steps:
            val_metrics = evaluate_policy(agent, val_seeds)
            val_r = val_metrics["mean_reward"]
            is_best = val_r > best_val_reward
            if is_best:
                best_val_reward = val_r
                best_step = step
                # Save best checkpoint
                best_ckpt_path = CHECKPOINT_DIR / f"policy_{policy_id:02d}_best.npz"
                agent.save(best_ckpt_path)

            record = {
                "step": step,
                "epsilon": float(agent.epsilon),
                "val_reward": val_r,
                "val_equity": val_metrics["mean_terminal_equity"],
                "dealer_halt_rate": val_metrics["dealer_halt_rate"],
                "is_best": is_best,
            }
            history.append(record)
            elapsed = time.time() - t0
            print(f"  Step {step:7,d} | eps={agent.epsilon:.3f} | Val Reward: {val_r:7.2f} | "
                  f"Equity: ${val_metrics['mean_terminal_equity']:,.1f} | Halts: {val_metrics['dealer_halt_rate']*100:.1f}% | "
                  f"Elapsed: {elapsed:.1f}s {'[BEST]' if is_best else ''}")

    # Save final checkpoint as well
    final_ckpt_path = CHECKPOINT_DIR / f"policy_{policy_id:02d}_final.npz"
    agent.save(final_ckpt_path)

    return {
        "policy_id": policy_id,
        "train_seed": train_seed,
        "best_step": best_step,
        "best_val_reward": best_val_reward,
        "best_checkpoint": str(best_ckpt_path.relative_to(ROOT)),
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser(description="Train Q-Learning Agents for Machine Markets")
    parser.add_argument("--policies", type=int, default=10, help="Number of independent policies")
    parser.add_argument("--steps", type=int, default=200_000, help="Total environment transitions per policy")
    parser.add_argument("--eval_freq", type=int, default=25_000, help="Evaluation frequency in steps")
    parser.add_argument("--pilot", action="store_true", help="Run 3-seed pilot (50k steps)")
    args = parser.parse_args()

    n_policies = 3 if args.pilot else args.policies
    steps = 50_000 if args.pilot else args.steps
    eval_freq = 10_000 if args.pilot else args.eval_freq

    train_seeds = [101 + i for i in range(n_policies)]
    val_seeds = [201, 202, 203, 204, 205]

    print("=" * 70)
    print(f"MACHINE MARKETS — Q-LEARNING TRAINING PIPELINE ({'PILOT' if args.pilot else 'CONFIRMATION'})")
    print(f"Policies: {n_policies} | Steps/policy: {steps:,} | Eval freq: {eval_freq:,}")
    print(f"Train seeds: {train_seeds} | Val seeds: {val_seeds}")
    print("=" * 70)

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    all_summaries = []

    for i, t_seed in enumerate(train_seeds, start=1):
        summary = train_single_agent(
            policy_id=i,
            train_seed=t_seed,
            val_seeds=val_seeds,
            total_steps=steps,
            eval_freq=eval_freq,
        )
        all_summaries.append(summary)

    out_file = RESULTS_DIR / f"q_learning_training_{'pilot' if args.pilot else 'confirmation'}_results.json"
    out_file.write_text(json.dumps({
        "mode": "pilot" if args.pilot else "confirmation",
        "n_policies": n_policies,
        "steps_per_policy": steps,
        "train_seeds": train_seeds,
        "val_seeds": val_seeds,
        "summaries": all_summaries,
    }, indent=2))
    print(f"\nTraining complete. Manifest saved to: {out_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
