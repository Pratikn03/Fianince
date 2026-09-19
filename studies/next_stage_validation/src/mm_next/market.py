"""A small, independently specified market environment for controlled tests.

This environment is intentionally not imported from any historical study. It is
an offline validation mechanism, not a calibrated real-market simulator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class MarketConfig:
    horizon: int = 48
    initial_price: float = 100.0
    initial_cash: float = 100.0
    max_order: float = 0.5
    max_inventory: float = 2.0
    spread: float = 0.02
    depth: float = 5.0
    impact: float = 0.04
    volatility: float = 0.01
    mean_reversion: float = 0.03
    fee_rate: float = 0.001
    partial_fill: float = 0.15
    margin_rate: float = 0.10
    maintenance_margin: float = 0.05
    drawdown_limit: float = 0.25
    seed: int = 0

    def validate(self) -> None:
        if self.horizon <= 0 or self.initial_price <= 0 or self.initial_cash <= 0:
            raise ValueError("horizon, initial_price, and initial_cash must be positive")
        if self.max_order <= 0 or self.max_inventory <= 0 or self.depth <= 0:
            raise ValueError("order, inventory, and depth limits must be positive")
        if self.spread < 0 or self.impact < 0 or self.volatility < 0:
            raise ValueError("market frictions must be nonnegative")
        if not 0 <= self.partial_fill <= 1:
            raise ValueError("partial_fill must lie in [0, 1]")
        if self.fee_rate < 0 or self.margin_rate < 0 or self.maintenance_margin < 0:
            raise ValueError("fees and margin parameters must be nonnegative")


@dataclass(frozen=True)
class MarketTape:
    shocks: np.ndarray
    fill_uniforms: np.ndarray

    def validate(self, horizon: int) -> None:
        if self.shocks.shape != (horizon,) or self.fill_uniforms.shape != (horizon,):
            raise ValueError("tape arrays must have exactly the configured horizon")
        if np.any((self.fill_uniforms < 0) | (self.fill_uniforms > 1)):
            raise ValueError("fill uniforms must lie in [0, 1]")


@dataclass(frozen=True)
class StepResult:
    observation: np.ndarray
    requested_quantity: float
    filled_quantity: float
    execution_price: float
    fees: float
    mark_to_market_equity: float
    margin_required: float
    event: str | None
    done: bool


def make_tape(config: MarketConfig, seed: int) -> MarketTape:
    config.validate()
    rng = np.random.default_rng(seed)
    return MarketTape(
        shocks=rng.normal(0.0, config.volatility, size=config.horizon),
        fill_uniforms=rng.random(config.horizon),
    )


class SyntheticMarket:
    """Discrete-time single-asset market with explicit accounting.

    The action is a requested signed quantity in [-1, 1]. The environment
    applies spread, impact, partial fills, fees, inventory limits, margin, and
    drawdown halts. All monetary quantities are in the environment's units.
    """

    def __init__(self, config: MarketConfig, tape: MarketTape | None = None) -> None:
        config.validate()
        self.config = config
        self._rng = np.random.default_rng(config.seed)
        self._tape = tape
        if tape is not None:
            tape.validate(config.horizon)
        self.reset()

    def reset(self, tape: MarketTape | None = None) -> np.ndarray:
        if tape is not None:
            tape.validate(self.config.horizon)
            self._tape = tape
        self.step_index = 0
        self.price = float(self.config.initial_price)
        self.previous_price = self.price
        self.inventory = 0.0
        self.cash = float(self.config.initial_cash)
        self.max_equity = self.cash
        self.done = False
        self.last_event: str | None = None
        return self._observation()

    def _random_at(self, index: int) -> tuple[float, float]:
        if self._tape is not None:
            return float(self._tape.shocks[index]), float(self._tape.fill_uniforms[index])
        return float(self._rng.normal(0.0, self.config.volatility)), float(self._rng.random())

    @property
    def equity(self) -> float:
        return float(self.cash + self.inventory * self.price)

    @property
    def margin_required(self) -> float:
        return float(abs(self.inventory * self.price) * self.config.margin_rate)

    def _observation(self) -> np.ndarray:
        equity = self.equity
        return np.asarray(
            [
                (self.price - self.previous_price) / max(self.previous_price, 1e-12),
                self.inventory / self.config.max_inventory,
                equity / self.config.initial_cash - 1.0,
                self.config.spread / max(self.price, 1e-12),
                self.config.depth / max(self.config.depth + abs(self.inventory), 1e-12),
                self.margin_required / max(abs(equity), 1e-12),
                self.step_index / self.config.horizon,
            ],
            dtype=float,
        )

    def step(self, action: float) -> StepResult:
        if self.done:
            raise RuntimeError("cannot step a completed episode")
        if not np.isfinite(action):
            raise ValueError("action must be finite")
        action = float(np.clip(action, -1.0, 1.0))
        requested = action * self.config.max_order
        remaining = self.config.max_inventory - abs(self.inventory)
        capacity = max(0.0, remaining)
        constrained = abs(requested) > capacity + 1e-12
        quantity = float(np.sign(requested) * min(abs(requested), capacity))
        _, fill_uniform = self._random_at(self.step_index)
        fill_fraction = 1.0 - self.config.partial_fill * fill_uniform
        filled = quantity * fill_fraction
        direction = float(np.sign(filled))
        execution_price = self.price + direction * self.config.spread / 2.0
        execution_price += self.config.impact * filled / max(self.config.depth, 1e-12)
        fees = self.config.fee_rate * abs(filled) * execution_price

        self.cash -= filled * execution_price + fees
        self.inventory += filled
        shock, _ = self._random_at(self.step_index)
        return_component = self.config.mean_reversion * (
            (self.config.initial_price - self.price) / self.config.initial_price
        )
        self.previous_price = self.price
        self.price = max(1e-6, self.price * (1.0 + shock + return_component))
        self.step_index += 1

        equity = self.equity
        self.max_equity = max(self.max_equity, equity)
        drawdown = (self.max_equity - equity) / max(abs(self.max_equity), 1e-12)
        event: str | None = None
        if constrained:
            event = "halt"
        elif equity <= 0:
            event = "default"
        elif self.margin_required > max(equity, 0.0) * (1.0 - self.config.maintenance_margin):
            event = "margin_breach"
        elif drawdown >= self.config.drawdown_limit:
            event = "drawdown_halt"
        elif self.step_index >= self.config.horizon:
            event = "terminal"
        self.last_event = event
        self.done = event in {"halt", "default", "margin_breach", "drawdown_halt", "terminal"}
        return StepResult(
            observation=self._observation(),
            requested_quantity=requested,
            filled_quantity=filled,
            execution_price=float(execution_price),
            fees=float(fees),
            mark_to_market_equity=float(equity),
            margin_required=self.margin_required,
            event=event,
            done=self.done,
        )


def make_tapes(config: MarketConfig, episodes: int, seed: int) -> Iterable[MarketTape]:
    if episodes <= 0:
        raise ValueError("episodes must be positive")
    return (make_tape(config, seed + index) for index in range(episodes))
