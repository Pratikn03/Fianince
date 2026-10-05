"""
Continuous Trading Environment with an Inventory-Constrained Dealer
==================================================================
Machine Markets — Deep Reinforcement Learning Suite

Features:
  - Continuous state space s_t in R^5:
      s_t = (price_deviation x_t, return ret_t, agent_inventory inv_t,
             dealer_capacity_utilization cap_util_t, recent_order_imbalance imb_t)
  - Supports both:
      1. Discrete action indexing A = {-2.0, -1.0, 0.0, +1.0, +2.0} (for DQN)
      2. Continuous action u in [-2.0, +2.0] (for Continuous Actor-Critic / PPO)
  - Strict balance sheet and inventory conservation:
      cash_residual == 0, inventory_residual == 0 across all 4 market participants.
  - Marked equity change reward with inventory quadratic penalty and turnover friction.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional
import numpy as np


ACTIONS = np.array([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float64)
N_ACTIONS = len(ACTIONS)
STATE_DIM = 5


@dataclass
class ContinuousMarketConfig:
    p_star: float = 100.0
    a: float = 0.40
    kappa: float = 0.02
    phi: float = 0.50          # Fundamental mean-reversion elasticity
    sigma_noise: float = 0.10   # Exogenous disturbance standard deviation
    spread_bps: float = 1.0     # Full bid-ask spread; half paid per execution
    max_inventory: float = 25.0 # Dealer inventory capacity
    lambda_inv: float = 0.01    # Agent inventory holding penalty
    lambda_trans: float = 0.005 # Agent turnover transaction penalty
    max_steps: int = 128


class ContinuousTradingEnv:
    """Continuous market environment with conservation-preserving dealer execution."""

    def __init__(self, config: Optional[ContinuousMarketConfig] = None, seed: int = 42):
        self.cfg = config or ContinuousMarketConfig()
        if self.cfg.max_inventory <= 0 or self.cfg.max_steps <= 0:
            raise ValueError("Positive inventory capacity and horizon required")
        self.rng = np.random.default_rng(seed)
        self.half_spread = (self.cfg.spread_bps / 10000.0) * self.cfg.p_star / 2.0
        self.reset()

    def reset(self, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.step_idx = 0
        self.x = 0.0
        self.prev_x = 0.0
        self.agent_inv = 0.0
        self.agent_cash = 10000.0
        self.agent_equity = 10000.0
        self.dealer_inv = 0.0
        self.dealer_cash = 10000.0
        self.fundamental_inv = self.noise_inv = 0.0
        self.fundamental_cash = self.noise_cash = 10000.0
        self.dealer_halted = False
        self.recent_imbalance = 0.0

        return self._get_state(ret=0.0)

    def _get_state(self, ret: float) -> np.ndarray:
        cap_util = min(1.0, abs(self.dealer_inv) / self.cfg.max_inventory)
        return np.array([self.x, ret, self.agent_inv, cap_util, self.recent_imbalance], dtype=np.float32)

    def step(self, action: float | int, external_shock: float = 0.0) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        if self.step_idx >= self.cfg.max_steps:
            raise RuntimeError("Episode complete; reset before further execution")

        if isinstance(action, (int, np.integer)):
            if action not in range(N_ACTIONS):
                raise ValueError(f"Invalid discrete action index {action}")
            desired_trade = float(ACTIONS[action])
        else:
            desired_trade = float(np.clip(action, -2.0, 2.0))

        if not np.isfinite(external_shock):
            raise ValueError("External shock must be finite")

        self.step_idx += 1
        v_fund = -self.cfg.phi * self.x
        v_exog = float(self.rng.normal(0.0, self.cfg.sigma_noise))
        requested = float(desired_trade + v_fund + v_exog)

        feasible = float(np.clip(
            requested,
            self.dealer_inv - self.cfg.max_inventory,
            self.dealer_inv + self.cfg.max_inventory
        ))

        fill_fraction = 0.0 if self.dealer_halted else 1.0
        if not self.dealer_halted and abs(feasible - requested) > 1e-12:
            fill_fraction = feasible / requested if abs(requested) > 1e-12 else 0.0
            self.dealer_halted = True

        agent_trade = float(desired_trade * fill_fraction)
        fund_trade = float(v_fund * fill_fraction)
        noise_trade = float(v_exog * fill_fraction)
        net_flow = agent_trade + fund_trade + noise_trade

        # Update dealer inventory
        self.dealer_inv -= net_flow

        # Closed-loop price update
        x_next = self.cfg.a * self.x + self.cfg.kappa * net_flow + external_shock
        p_next = self.cfg.p_star + x_next

        # Ledger accounting
        spread_cost = abs(agent_trade) * self.half_spread
        self.agent_cash -= agent_trade * p_next + spread_cost
        self.agent_inv += agent_trade

        fund_payment = fund_trade * p_next + abs(fund_trade) * self.half_spread
        noise_payment = noise_trade * p_next + abs(noise_trade) * self.half_spread
        self.fundamental_cash -= fund_payment
        self.noise_cash -= noise_payment
        self.fundamental_inv += fund_trade
        self.noise_inv += noise_trade

        self.dealer_cash += agent_trade * p_next + spread_cost + fund_payment + noise_payment

        # Marked equity
        new_equity = self.agent_cash + self.agent_inv * p_next
        delta_equity = new_equity - self.agent_equity
        self.agent_equity = new_equity

        # Penalized reward
        reward = float(delta_equity - self.cfg.lambda_inv * (self.agent_inv ** 2) - self.cfg.lambda_trans * abs(agent_trade))

        # Update state variables
        ret = x_next - self.x
        self.prev_x = self.x
        self.x = x_next
        self.recent_imbalance = 0.8 * self.recent_imbalance + 0.2 * net_flow

        next_state = self._get_state(ret=ret)
        done = self.step_idx >= self.cfg.max_steps

        info = {
            "x": self.x,
            "agent_inv": self.agent_inv,
            "agent_equity": self.agent_equity,
            "dealer_inv": self.dealer_inv,
            "dealer_halted": self.dealer_halted,
            "net_flow": net_flow,
            "agent_trade": agent_trade,
            "spread_cost": spread_cost,
            "fundamental_trade": fund_trade,
            "noise_trade": noise_trade,
            "fill_fraction": fill_fraction,
            "cash_residual": float(self.agent_cash + self.dealer_cash + self.fundamental_cash + self.noise_cash - 40000.0),
            "inventory_residual": float(self.agent_inv + self.dealer_inv + self.fundamental_inv + self.noise_inv),
        }
        return next_state, reward, done, info
