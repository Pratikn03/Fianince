"""Formal model, observation, risk, and balance-sheet contracts for Flagship Paper 2."""
from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Sequence
import numpy as np


@dataclass(frozen=True)
class PositiveMemoryMarket:
    """Positive-memory cohort economy:
    x_{t+1} = a x_t + sum_i y_{i,t} + kappa u_t
    y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i q_i x_t
    """
    name: str
    a: Fraction
    etas: tuple[Fraction, ...]
    qs: tuple[Fraction, ...]
    kappa: Fraction = Fraction(1, 1)

    def __post_init__(self) -> None:
        if len(self.etas) != len(self.qs):
            raise ValueError("etas and qs must have identical length")
        if not (Fraction(0) <= self.a < Fraction(1)):
            raise ValueError("a must lie in [0, 1)")
        for eta, q in zip(self.etas, self.qs):
            if not (Fraction(0) < eta <= Fraction(1)):
                raise ValueError("Each eta_i must lie in (0, 1]")
            if q < Fraction(0):
                raise ValueError("PositiveMemoryMarket requires q_i >= 0")

    @property
    def num_cohorts(self) -> int:
        return len(self.etas)

    @property
    def total_feedback_Q(self) -> Fraction:
        return sum(self.qs, Fraction(0))

    @property
    def is_stable(self) -> bool:
        return self.a + self.kappa * self.total_feedback_Q < Fraction(1)

    @property
    def long_run_gain(self) -> Fraction:
        if not self.is_stable:
            raise ValueError("Market is not stable; infinite-horizon gain diverges")
        return self.kappa / (Fraction(1) - self.a - self.kappa * self.total_feedback_Q)

    def max_per_period_shock(self, budget: Fraction = Fraction(1), inventory: Fraction = Fraction(1)) -> Fraction:
        """Maximum per-period shock v_max for budget B and inventory |I|: v_max = B / (|I| * S)."""
        return budget / (abs(inventory) * self.long_run_gain)


@dataclass(frozen=True)
class ObservationContract:
    """Specifies what the supervisor or dealer observes."""
    horizon_L: int
    noise_sd: float
    eta_min: float = 0.05
    mode: str = "public_impulse"  # "public_impulse", "class_tagged", "audited_channel"


@dataclass(frozen=True)
class RiskContract:
    """Specifies the risk budget B, inventory |I|, horizon H, and error tolerance."""
    budget_B: float = 1.0
    inventory_I: float = 1.0
    shock_bound_u: float = 1.0
    safety_alpha_beta: float = 0.05
    confidence_gamma: float = 0.05


@dataclass(frozen=True)
class BalanceSheetContract:
    """Full dealer balance-sheet contract for Theorem E and forward solvency."""
    equity_E0: float = 10000.0
    inventory_I0: float = -2000.0
    mark_price_P: float = 100.0
    maintenance_margin_mu: float = 0.005
    tier_deduction: float = 50.0
    reserve_R_safe: float = 950.0
    max_fill_u: float = 200.0
    hedge_capacity_H: float = 100.0
    exec_cost_rate: float = 0.02

    @property
    def initial_buffer_B_rem(self) -> float:
        maint_req = max(0.0, abs(self.inventory_I0) * self.mark_price_P * self.maintenance_margin_mu - self.tier_deduction)
        return self.equity_E0 - maint_req

    def post_trade_inventory(self, alpha: float) -> float:
        return abs(self.inventory_I0 + alpha * self.hedge_capacity_H) + alpha * self.max_fill_u

    def execution_and_fill_cost(self, alpha: float) -> float:
        return self.exec_cost_rate * alpha * (self.hedge_capacity_H + self.max_fill_u)
