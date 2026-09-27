"""Work Package 6: Retained funded scenarios and paired mechanism controls.

Scenario S labels use stored nominal a; the implemented unconstrained price
persistence is 1-kappa*phi, with memories updated from the new price. Diagnostics
expose this distinction without changing historical trajectories. The legacy
capital multiplier scales inventory capacity at fixed initial equity of 10,000.

Cash and inventory are marked at the current price. Margin breaches are counted
without liquidation. Halt is a sticky occurrence flag for an inventory constraint
hit, not a persistent trading ban: subsequent fills and marking continue. Default,
halt occurrence, and drawdown are separate outputs. The accounting-residual field
is retained but is not calculated or checked by this implementation.

Paired controls use identical shock tapes for adaptive memories, memories frozen
from shock_step, removed feedback, and unlimited inventory capacity.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


@dataclass
class DealerBalanceSheet:
    """Marked cash/inventory account; margin counts do not trigger liquidation."""

    cash: float
    inventory: float
    initial_cash: float
    initial_inventory: float
    max_inventory: float
    maintenance_margin_rate: float = 0.25 # 25% margin
    min_equity: float = float("inf")
    peak_drawdown: float = 0.0
    initial_equity: float = 0.0
    halted: bool = False
    defaulted: bool = False
    margin_calls_count: int = 0
    unfilled_volume: float = 0.0
    max_accounting_residual: float = 0.0

    def mark_to_market(self, current_price: float) -> float:
        equity = self.cash + self.inventory * current_price
        if equity < self.min_equity:
            self.min_equity = equity
        if self.initial_equity > 0:
            dd = max(0.0, (self.initial_equity - equity) / self.initial_equity)
            if dd > self.peak_drawdown:
                self.peak_drawdown = dd
        
        # Check margin
        position_value = abs(self.inventory * current_price)
        if position_value > 0:
            margin_ratio = equity / position_value
            if margin_ratio < self.maintenance_margin_rate:
                self.margin_calls_count += 1
                if equity <= 0:
                    self.defaulted = True

        return equity


class FundedScenarioMarket:
    """Retained price-impact dynamics with an inventory-limited dealer.

    ``a`` is nominal metadata only. ``dealer_capital_multiplier`` scales the
    inventory limit, not equity. ``unlimited_funding`` removes that limit only.
    """

    def __init__(
        self,
        p_star: float = 100.0,
        kappa: float = 0.02,
        phi: float = 10.0, # Fundamental trading elasticity
        a: float = 0.40,
        q_fast: float = 0.252,
        q_slow: float = 0.168,
        eta_fast: float = 0.50,
        eta_slow: float = 0.02,
        dealer_capital_multiplier: float = 1.0,
        initial_utilization: float = 0.0,
        base_inventory_limit: float = 25.0,
        unlimited_funding: bool = False
    ):
        self.p_star = float(p_star)
        self.kappa = float(kappa)
        self.phi = float(phi)
        self.a = float(a)
        self.q_fast = float(q_fast)
        self.q_slow = float(q_slow)
        self.eta_fast = float(eta_fast)
        self.eta_slow = float(eta_slow)
        self.unlimited_funding = bool(unlimited_funding)

        max_inv = base_inventory_limit * dealer_capital_multiplier
        init_inv = initial_utilization * max_inv
        init_cash = 10000.0 - init_inv * p_star

        self.dealer = DealerBalanceSheet(
            cash=init_cash,
            inventory=init_inv,
            initial_cash=init_cash,
            initial_inventory=init_inv,
            max_inventory=max_inv,
            initial_equity=init_cash + init_inv * p_star,
            min_equity=init_cash + init_inv * p_star
        )

    def dynamics_diagnostics(self, learning_regime: str = "adaptive") -> Dict[str, Any]:
        """Describe the unconstrained, zero-input recurrence actually executed.

        State order is (x, y_fast, y_slow). Price updates first, then adaptive
        memories consume x_next. The matrix excludes inventory clipping and the
        additive shock inputs. Frozen learning uses this matrix before shock_step
        and the reported post-freeze matrix from shock_step onward. Removed
        feedback holds the unused memories fixed, so its full-state spectral
        radius includes unit eigenvalues even when price decays.
        """
        effective_a = 1.0 - self.kappa * self.phi
        q_f = 0.0 if learning_regime == "zero_feedback" else self.q_fast
        q_s = 0.0 if learning_regime == "zero_feedback" else self.q_slow
        Q = q_f + q_s
        held_matrix = np.array([
            [effective_a, q_f, q_s],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])
        matrix = held_matrix.copy()
        updates_memory = learning_regime in ("adaptive", "frozen")
        if updates_memory:
            for row, eta in ((1, self.eta_fast), (2, self.eta_slow)):
                matrix[row] = eta * matrix[0]
                matrix[row, row] += 1.0 - eta
        diagnostics = {
            "nominal_a": self.a,
            "effective_a": float(effective_a),
            "Q": float(Q),
            "nominal_S": float(self.a + Q),
            "effective_S": float(effective_a + Q),
            "parameter_mismatch": bool(not np.isclose(self.a, effective_a, rtol=1e-12, atol=1e-12)),
            "effective_minus_nominal_a": float(effective_a - self.a),
            "state_order": ["x", "y_fast", "y_slow"],
            "transition_matrix": matrix.tolist(),
            "spectral_radius": float(np.max(np.abs(np.linalg.eigvals(matrix)))),
            "scope": "unconstrained_zero_input_full_state",
            "learning_regime": learning_regime,
            "memory_timing": "x_next" if updates_memory else "held",
            "units": {
                "x": "price", "y_fast": "price", "y_slow": "price",
                "shock_tape": "shares_per_step", "mean_repricing_shock": "price",
                "kappa": "price_per_share", "phi": "shares_per_price",
                "q": "dimensionless", "eta": "per_step_fraction",
            },
            "shock_timing": "repricing adds to x before demand; shock_tape adds to desired share flow",
            "capacity_multiplier_scope": "inventory_limit_at_fixed_initial_equity_10000",
            "halt_scope": "sticky_constraint_hit_occurrence_not_persistent_trading_ban",
            "margin_scope": "breach_count_without_liquidation",
        }
        if learning_regime == "frozen":
            diagnostics["transition_matrix_scope"] = "before_shock_step"
            diagnostics["post_freeze_transition_matrix"] = held_matrix.tolist()
            diagnostics["post_freeze_spectral_radius"] = float(np.max(np.abs(np.linalg.eigvals(held_matrix))))
            diagnostics["freeze_timing"] = "memories held from shock_step onward"
        return diagnostics

    def run_trajectory(
        self,
        shock_tape: np.ndarray,
        mean_repricing_shock: float = 0.0,
        shock_step: int = 16,
        learning_regime: str = "adaptive", # 'adaptive', 'frozen', 'zero_feedback'
        initial_memory: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        """Execute len(shock_tape) steps; add diagnostics without altering outcomes.

        A constraint hit records halt occurrence but does not disable later fills.
        Margin counts do not liquidate positions. Repricing is an additive change
        to x before demand; the reference price p_star itself remains fixed.
        """
        T = len(shock_tape)
        x = 0.0
        p = self.p_star
        if initial_memory is not None:
            y_fast, y_slow = float(initial_memory[0]), float(initial_memory[1])
        else:
            y_fast = 0.05
            y_slow = 0.05

        q_f = 0.0 if learning_regime == "zero_feedback" else self.q_fast
        q_s = 0.0 if learning_regime == "zero_feedback" else self.q_slow

        dislocations = []
        equity_series = []

        for t in range(T):
            # Inject additive price-dislocation shock before demand at shock_step
            if t == shock_step:
                x += mean_repricing_shock

            # Adaptive agent demands
            v_fast = (q_f / self.kappa) * y_fast
            v_slow = (q_s / self.kappa) * y_slow
            v_fund = -self.phi * x
            v_exog = shock_tape[t]

            desired_flow = v_fast + v_slow + v_fund + v_exog

            # Check dealer inventory constraints
            if not self.unlimited_funding:
                new_inventory = self.dealer.inventory - desired_flow
                if abs(new_inventory) > self.dealer.max_inventory:
                    self.dealer.halted = True
                    # Fill only up to max inventory
                    avail_capacity = self.dealer.max_inventory - abs(self.dealer.inventory)
                    fill_amt = max(0.0, avail_capacity) * np.sign(-desired_flow) if desired_flow != 0 else 0.0
                    actual_flow = -fill_amt
                    self.dealer.unfilled_volume += abs(desired_flow - actual_flow)
                else:
                    actual_flow = desired_flow
            else:
                actual_flow = desired_flow

            # Price impact
            x_next = x + self.kappa * actual_flow
            p_next = self.p_star + x_next

            # Dealer balance sheet update
            self.dealer.inventory -= actual_flow
            self.dealer.cash += actual_flow * p_next

            # Continue fills and marking after a halt occurrence (no halt guard).
            eq = self.dealer.mark_to_market(p_next)
            equity_series.append(eq)

            # Memory update
            if learning_regime == "adaptive":
                y_fast = (1.0 - self.eta_fast) * y_fast + self.eta_fast * x_next
                y_slow = (1.0 - self.eta_slow) * y_slow + self.eta_slow * x_next
            elif learning_regime == "frozen":
                # For t < shock_step, memory accumulates pre-shock conditions
                # For t >= shock_step, memory remains frozen at the pre-shock level
                if t < shock_step:
                    y_fast = (1.0 - self.eta_fast) * y_fast + self.eta_fast * x_next
                    y_slow = (1.0 - self.eta_slow) * y_slow + self.eta_slow * x_next
                else:
                    pass # Freeze memory at pre-shock accumulated state
            elif learning_regime == "zero_feedback":
                # Feedback removed (q = 0); no memory demand generated
                pass

            x = x_next
            p = p_next
            dislocations.append(abs(x))

        return {
            "dealer_halt": bool(self.dealer.halted),
            "dealer_default": bool(self.dealer.defaulted),
            "drawdown_gt_20pct": bool(self.dealer.peak_drawdown > 0.20),
            "composite_failure": bool(self.dealer.halted or self.dealer.defaulted or self.dealer.peak_drawdown > 0.20),
            "min_equity": float(self.dealer.min_equity),
            "peak_drawdown": float(self.dealer.peak_drawdown),
            "margin_calls": int(self.dealer.margin_calls_count),
            "unfilled_volume": float(self.dealer.unfilled_volume),
            "final_equity": float(equity_series[-1]),
            "mean_dislocation": float(np.mean(dislocations)),
            "dynamics_diagnostics": self.dynamics_diagnostics(learning_regime),
        }


def run_funded_scenario_grid(
    S_values: List[float] = [0.70, 0.82, 0.97, 1.03, 1.18],
    capital_multipliers: List[float] = [0.5, 1.0, 2.0, 4.0],
    mean_shocks: List[float] = [0.0, -2.0, -10.0],
    initial_utilizations: List[float] = [0.0, 0.5, 0.9],
    slow_rates: List[float] = [0.02, 0.10],
    n_replications: int = 10,
    seed_base: int = 20260924
) -> Dict[str, Any]:
    """Map nominal S labels versus inventory capacity at fixed equity and shocks.

    With default kappa and phi, effective S is nominal S + 0.4 for this grid.
    Historical field names are preserved; capital_multiplier scales inventory.
    """
    rng = np.random.default_rng(seed_base)
    cells = []

    for S_val in S_values:
        a = 0.40
        Q = max(0.0, S_val - a)
        q_f = 0.6 * Q
        q_s = 0.4 * Q

        for cap_mult in capital_multipliers:
            for m_shock in mean_shocks:
                for init_u in initial_utilizations:
                    for s_rate in slow_rates:
                        halt_count = 0
                        default_count = 0
                        drawdown_count = 0
                        composite_count = 0
                        min_equities = []

                        for rep in range(n_replications):
                            shock_tape = rng.normal(0.0, 0.05, size=64)
                            market = FundedScenarioMarket(
                                a=a, q_fast=q_f, q_slow=q_s,
                                eta_slow=s_rate,
                                dealer_capital_multiplier=cap_mult,
                                initial_utilization=init_u
                            )
                            res = market.run_trajectory(
                                shock_tape=shock_tape,
                                mean_repricing_shock=m_shock,
                                learning_regime="adaptive"
                            )
                            if res["dealer_halt"]:
                                halt_count += 1
                            if res["dealer_default"]:
                                default_count += 1
                            if res["drawdown_gt_20pct"]:
                                drawdown_count += 1
                            if res["composite_failure"]:
                                composite_count += 1
                            min_equities.append(res["min_equity"])

                        cells.append({
                            "S": S_val,
                            "capital_multiplier": cap_mult,
                            "mean_shock": m_shock,
                            "initial_utilization": init_u,
                            "slow_rate": s_rate,
                            "halt_rate_pct": (halt_count / n_replications) * 100.0,
                            "default_rate_pct": (default_count / n_replications) * 100.0,
                            "drawdown_rate_pct": (drawdown_count / n_replications) * 100.0,
                            "composite_failure_pct": (composite_count / n_replications) * 100.0,
                            "mean_min_equity": float(np.mean(min_equities)),
                        })

    return {
        "n_cells": len(cells),
        "n_replications_per_cell": n_replications,
        "grid_cells": cells,
    }


def run_paired_mechanism_controls(
    n_replicates: int = 50,
    seed: int = 20260924
) -> Dict[str, Any]:
    """Execute paired counterfactual mechanism controls on identical exogenous shock tapes.

    Controls:
      1. Full Adaptive Funded System
      2. Frozen Learning (memories held constant from shock_step onward)
      3. Removed Feedback (Q = 0)
      4. Unlimited inventory capacity diagnostic at the same initial equity
    """
    rng = np.random.default_rng(seed)
    regimes = ["adaptive", "frozen", "zero_feedback", "unlimited_funding"]
    results = {r: [] for r in regimes}

    for rep in range(n_replicates):
        shock_tape = rng.normal(0.0, 0.05, size=64)
        m_shock = -2.0 # Standard repricing shock

        # 1. Full adaptive
        m1 = FundedScenarioMarket(a=0.4, q_fast=0.252, q_slow=0.168, dealer_capital_multiplier=1.0)
        r1 = m1.run_trajectory(shock_tape, mean_repricing_shock=m_shock, learning_regime="adaptive")
        results["adaptive"].append(r1)

        # 2. Frozen learning
        m2 = FundedScenarioMarket(a=0.4, q_fast=0.252, q_slow=0.168, dealer_capital_multiplier=1.0)
        r2 = m2.run_trajectory(shock_tape, mean_repricing_shock=m_shock, learning_regime="frozen")
        results["frozen"].append(r2)

        # 3. Removed feedback (Q=0)
        m3 = FundedScenarioMarket(a=0.4, q_fast=0.0, q_slow=0.0, dealer_capital_multiplier=1.0)
        r3 = m3.run_trajectory(shock_tape, mean_repricing_shock=m_shock, learning_regime="zero_feedback")
        results["zero_feedback"].append(r3)

        # 4. Unlimited funding
        m4 = FundedScenarioMarket(a=0.4, q_fast=0.252, q_slow=0.168, unlimited_funding=True)
        r4 = m4.run_trajectory(shock_tape, mean_repricing_shock=m_shock, learning_regime="adaptive")
        results["unlimited_funding"].append(r4)

    summary = {}
    for reg in regimes:
        recs = results[reg]
        summary[reg] = {
            "halt_rate_pct": float(np.mean([1.0 if r["dealer_halt"] else 0.0 for r in recs]) * 100.0),
            "composite_failure_pct": float(np.mean([1.0 if r["composite_failure"] else 0.0 for r in recs]) * 100.0),
            "mean_dislocation": float(np.mean([r["mean_dislocation"] for r in recs])),
            "mean_min_equity": float(np.mean([r["min_equity"] for r in recs])),
            "mean_unfilled_volume": float(np.mean([r["unfilled_volume"] for r in recs])),
            "mean_peak_drawdown": float(np.mean([r["peak_drawdown"] for r in recs])),
        }

    # Paired differences and bootstrap confidence intervals
    def bootstrap_ci(diff_array: np.ndarray, n_boot: int = 1000) -> Tuple[float, float, float]:
        mean_diff = float(np.mean(diff_array))
        boot_means = [float(np.mean(rng.choice(diff_array, size=len(diff_array), replace=True))) for _ in range(n_boot)]
        ci_lo = float(np.percentile(boot_means, 2.5))
        ci_hi = float(np.percentile(boot_means, 97.5))
        return mean_diff, ci_lo, ci_hi

    fail_adapt = np.array([1.0 if r["composite_failure"] else 0.0 for r in results["adaptive"]])
    fail_froz = np.array([1.0 if r["composite_failure"] else 0.0 for r in results["frozen"]])
    fail_q0 = np.array([1.0 if r["composite_failure"] else 0.0 for r in results["zero_feedback"]])

    dis_adapt = np.array([r["mean_dislocation"] for r in results["adaptive"]])
    dis_froz = np.array([r["mean_dislocation"] for r in results["frozen"]])
    dis_q0 = np.array([r["mean_dislocation"] for r in results["zero_feedback"]])

    m_df_fail, lo_df_fail, hi_df_fail = bootstrap_ci(fail_adapt - fail_froz)
    m_df_dis, lo_df_dis, hi_df_dis = bootstrap_ci(dis_adapt - dis_froz)
    m_dq0_fail, lo_dq0_fail, hi_dq0_fail = bootstrap_ci(fail_adapt - fail_q0)
    m_dq0_dis, lo_dq0_dis, hi_dq0_dis = bootstrap_ci(dis_adapt - dis_q0)

    paired_contrasts = {
        "adaptive_minus_frozen": {
            "failure_diff_mean": m_df_fail,
            "failure_diff_ci_95": (lo_df_fail, hi_df_fail),
            "dislocation_diff_mean": m_df_dis,
            "dislocation_diff_ci_95": (lo_df_dis, hi_df_dis),
        },
        "adaptive_minus_zero_feedback": {
            "failure_diff_mean": m_dq0_fail,
            "failure_diff_ci_95": (lo_dq0_fail, hi_dq0_fail),
            "dislocation_diff_mean": m_dq0_dis,
            "dislocation_diff_ci_95": (lo_dq0_dis, hi_dq0_dis),
        },
    }

    return {
        "n_replicates": n_replicates,
        "summary": summary,
        "paired_contrasts": paired_contrasts,
        "dynamics_diagnostics": {
            reg: results[reg][0]["dynamics_diagnostics"] for reg in regimes
        },
        "central_finding": (
            "The retained adaptive baseline has nominal S=0.82 but effective S=1.22 "
            "with new-price memory updates and an unstable unconstrained transition matrix. "
            "These paired outcomes do not establish dealer failure under stable linear dynamics. "
            "The capital multiplier scales inventory capacity at fixed initial equity; halt "
            "records a constraint-hit occurrence, and margin counts are not liquidations."
        )
    }


def run_near_threshold_factorial_design(
    capital_multipliers: List[float] = [0.75, 1.0, 1.5, 2.0],
    initial_utilizations: List[float] = [0.0, 0.50, 0.80, 0.95],
    mean_shocks: List[float] = [0.0, -1.0, -2.0, -4.0],
    S_values: List[float] = [0.70, 0.82, 0.97, 1.03, 1.18],
    slow_rates: List[float] = [0.02, 0.10],
    n_replications: int = 20,
    seed_base: int = 20260924
) -> Dict[str, Any]:
    """Execute the retained factorial grid indexed by nominal S and capacity.

    Nominal thresholds need not be effective dynamic thresholds; saturation is an
    empirical outcome, not a property guaranteed by this design.
    """
    rng = np.random.default_rng(seed_base)
    cells = []

    for S_val in S_values:
        a = 0.40
        Q = max(0.0, S_val - a)
        q_f = 0.6 * Q
        q_s = 0.4 * Q

        for cap_mult in capital_multipliers:
            for m_shock in mean_shocks:
                for init_u in initial_utilizations:
                    for s_rate in slow_rates:
                        fail_count = 0
                        halt_count = 0
                        default_count = 0
                        dislocations = []
                        min_equities = []

                        for rep in range(n_replications):
                            shock_tape = rng.normal(0.0, 0.05, size=64)
                            market = FundedScenarioMarket(
                                a=a, q_fast=q_f, q_slow=q_s,
                                eta_slow=s_rate,
                                dealer_capital_multiplier=cap_mult,
                                initial_utilization=init_u
                            )
                            res = market.run_trajectory(
                                shock_tape=shock_tape,
                                mean_repricing_shock=m_shock,
                                learning_regime="adaptive"
                            )
                            if res["composite_failure"]:
                                fail_count += 1
                            if res["dealer_halt"]:
                                halt_count += 1
                            if res["dealer_default"]:
                                default_count += 1
                            dislocations.append(res["mean_dislocation"])
                            min_equities.append(res["min_equity"])

                        cells.append({
                            "S": S_val,
                            "capital_multiplier": cap_mult,
                            "mean_shock": m_shock,
                            "initial_utilization": init_u,
                            "slow_rate": s_rate,
                            "failure_prob": fail_count / n_replications,
                            "halt_prob": halt_count / n_replications,
                            "default_prob": default_count / n_replications,
                            "mean_dislocation": float(np.mean(dislocations)),
                            "mean_min_equity": float(np.mean(min_equities)),
                        })

    return {
        "n_cells": len(cells),
        "n_replications_per_cell": n_replications,
        "grid_cells": cells,
    }
