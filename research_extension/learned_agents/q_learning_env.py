"""
Discrete Trading Environment with an Inventory-Constrained Dealer
===========================================================
Machine Markets — Learned-Agent Transfer Layer (Q-Learning)

State space:
  s_t = (price_deviation_bin, return_bin, inventory_bin, dealer_capacity_bin, imbalance_bin)
  Dimensions: 7 x 5 x 7 x 5 x 5 = 6,125 discrete states.

Action space:
  A = {-2, -1, 0, +1, +2} shares/units (5 discrete actions).

Execution:
  Simultaneous customer orders are netted and prorated at dealer capacity.
  Four explicit cash/inventory ledgers conserve transfers. Cash balances may be
  negative: this is NOT the separately implemented funded/liquidation market.

Reward:
  r_t = Delta E_t - lambda_I * I_t^2 - lambda_T * |Delta I_t|
  where Delta E_t is marked equity change including spread friction.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional


PRICE_EDGES = np.array([-1.5, -0.5, -0.1, 0.1, 0.5, 1.5])      # 7 bins (0..6)
RETURN_EDGES = np.array([-0.5, -0.05, 0.05, 0.5])               # 5 bins (0..4)
INV_EDGES = np.array([-10.0, -3.0, -1.0, 1.0, 3.0, 10.0])        # 7 bins (0..6)
CAP_EDGES = np.array([0.20, 0.40, 0.60, 0.80])                  # 5 bins (0..4)
IMB_EDGES = np.array([-2.0, -0.5, 0.5, 2.0])                     # 5 bins (0..4)

ACTIONS = np.array([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float64)
N_ACTIONS = len(ACTIONS)
N_STATES = 7 * 5 * 7 * 5 * 5  # 6,125


def discretize_state(x: float, ret: float, inv: float, cap_util: float, imb: float) -> int:
    """Map continuous market observables into a single unique state index in [0, 6124]."""
    p_b = int(np.digitize(x, PRICE_EDGES))
    r_b = int(np.digitize(ret, RETURN_EDGES))
    i_b = int(np.digitize(inv, INV_EDGES))
    c_b = int(np.digitize(cap_util, CAP_EDGES))
    m_b = int(np.digitize(imb, IMB_EDGES))
    return p_b * 875 + r_b * 175 + i_b * 25 + c_b * 5 + m_b


@dataclass
class MarketConfig:
    p_star: float = 100.0
    a: float = 0.40
    kappa: float = 0.02
    phi: float = 0.50          # Fundamental mean-reversion elasticity
    sigma_noise: float = 0.10   # Exogenous disturbance standard deviation
    spread_bps: float = 1.0     # full bid-ask spread; half paid per execution
    max_inventory: float = 25.0 # Dealer inventory capacity
    lambda_inv: float = 0.01    # Agent inventory holding penalty
    lambda_trans: float = 0.005 # Agent turnover transaction penalty
    max_steps: int = 128


class DiscreteTradingEnv:
    """Inventory-only execution model; no funding, margin or liquidation rule."""

    def __init__(self, config: Optional[MarketConfig] = None, seed: int = 42):
        self.cfg = config or MarketConfig()
        if self.cfg.max_inventory <= 0 or self.cfg.max_steps <= 0:
            raise ValueError('Positive inventory capacity and horizon required')
        self.rng = np.random.default_rng(seed)
        self.half_spread = (self.cfg.spread_bps / 10000.0) * self.cfg.p_star / 2.0
        self.reset()

    def reset(self, seed: Optional[int] = None) -> int:
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

        ret = 0.0
        cap_util = abs(self.dealer_inv) / self.cfg.max_inventory
        return discretize_state(self.x, ret, self.agent_inv, cap_util, self.recent_imbalance)

    def step(self, action_idx: int, external_shock: float = 0.0) -> Tuple[int, float, bool, Dict[str, Any]]:
        if self.step_idx >= self.cfg.max_steps:
            raise RuntimeError('Episode complete; reset before further execution')
        if action_idx not in range(N_ACTIONS) or not np.isfinite(external_shock):
            raise ValueError('Invalid action or shock')
        self.step_idx += 1
        desired_trade = ACTIONS[action_idx]
        v_fund = -self.cfg.phi * self.x
        # Consume the same exogenous random draw even after a halt.
        v_exog = self.rng.normal(0.0, self.cfg.sigma_noise)
        requested = float(desired_trade + v_fund + v_exog)
        feasible = float(np.clip(requested, self.dealer_inv - self.cfg.max_inventory,
                                 self.dealer_inv + self.cfg.max_inventory))
        fill_fraction = 0.0 if self.dealer_halted else 1.0
        if not self.dealer_halted and abs(feasible - requested) > 1e-12:
            fill_fraction = feasible / requested
            self.dealer_halted = True
        agent_trade = float(desired_trade * fill_fraction)
        fund_trade = float(v_fund * fill_fraction)
        noise_trade = float(v_exog * fill_fraction)
        net_flow = agent_trade + fund_trade + noise_trade

        # Update dealer inventory
        self.dealer_inv -= net_flow

        # Price update
        x_next = self.cfg.a * self.x + self.cfg.kappa * net_flow + external_shock
        p_next = self.cfg.p_star + x_next

        # Agent balance sheet and reward
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
        new_equity = self.agent_cash + self.agent_inv * p_next
        delta_equity = new_equity - self.agent_equity
        self.agent_equity = new_equity

        # Penalized reward: marked equity change - inventory penalty - transaction penalty
        reward = delta_equity - self.cfg.lambda_inv * (self.agent_inv ** 2) - self.cfg.lambda_trans * abs(agent_trade)

        # State updates
        ret = x_next - self.x
        self.prev_x = self.x
        self.x = x_next
        self.recent_imbalance = 0.8 * self.recent_imbalance + 0.2 * net_flow
        cap_util = min(1.0, abs(self.dealer_inv) / self.cfg.max_inventory)

        next_state = discretize_state(self.x, ret, self.agent_inv, cap_util, self.recent_imbalance)
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
            "cash_residual": self.agent_cash + self.dealer_cash + self.fundamental_cash + self.noise_cash - 40000.,
            "inventory_residual": self.agent_inv + self.dealer_inv + self.fundamental_inv + self.noise_inv,
        }
        return next_state, reward, done, info
