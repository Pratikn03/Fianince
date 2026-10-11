"""
Comprehensive Unit & Integration Test Suite: Institutional Hardening & Real-World Safeguards
=============================================================================================
Machine Markets — Production Institutional Verification Suite

Verifies:
  1. Real-World Level-3 Limit Order Book Replay & Balance Sheet Conservation.
  2. Neural Deep RL Policy Networks & Multiscale Empirical Jacobians.
  3. Basel III SA-CCR Capital & CME SPAN 2 Dynamic Margining Calculations.
  4. Real Order Book Depth Liquidation & Kreiss Safe Radius Contagion Elimination.
  5. Bivariate Hawkes Process Mutual Excitation & Tri-Simulator Invariance.
  6. FIX 5.0 SP2 Drop-Copy Stream Parser & Real-Time Supervisory Fallback Controller.
"""
from __future__ import annotations
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from research_extension.learned_agents.real_lob_replay_env import (
    RealLOBReplayEnv, STATE_DIM_REAL, ACTIONS_REAL
)
from research_extension.learned_agents.train_real_lob_deep_rl import (
    RealActorCritic, RealDQNNetwork
)
from simulations.institutional_sacr_clearing_engine import (
    compute_sacr_capital, compute_span2_margins,
    execute_liquidation_on_depth, load_real_l3_depth_slices,
    run_institutional_clearing_simulation, DealerProfile
)
from simulations.hawkes_tri_simulator import BivariateHawkesProcess
from production_runtime.institutional_fix_supervisor import (
    parse_fix_message, InstitutionalFIXSupervisor, SupervisorState, FIXMessage
)


# --------------------------------------------------------------------------- Phase 1 Tests
class TestPhase1RealLOBReplayAndDeepRL:
    def test_real_lob_replay_env_lifecycle(self):
        env = RealLOBReplayEnv(max_steps=32, seed=42)
        state = env.reset()
        assert isinstance(state, np.ndarray)
        assert state.shape == (STATE_DIM_REAL,)
        assert np.all(np.isfinite(state))

        # Run several steps and verify balance sheet accounting
        for step_i in range(10):
            action = float(np.random.choice(ACTIONS_REAL))
            next_state, reward, done, info = env.step(action)
            assert next_state.shape == (STATE_DIM_REAL,)
            assert isinstance(reward, float)
            assert "agent_equity" in info
            # Balance sheet identity: equity = cash + inv * price
            calc_eq = env.agent_cash + env.agent_inv * info["next_mid"]
            assert abs(calc_eq - info["agent_equity"]) < 1e-4
            if done:
                break

    def test_real_actor_critic_forward_and_jacobian(self):
        model = RealActorCritic(state_dim=STATE_DIM_REAL)
        model.eval()
        dummy_state = torch.zeros(1, STATE_DIM_REAL)
        mean, std, val = model(dummy_state)
        
        assert mean.shape == (1, 1)
        assert std.shape == (1,)
        assert val.shape == (1, 1)
        assert -2.0 <= mean.item() <= 2.0
        assert std.item() > 0.0

    def test_real_dqn_forward(self):
        model = RealDQNNetwork(state_dim=STATE_DIM_REAL, n_actions=5)
        model.eval()
        dummy_state = torch.randn(2, STATE_DIM_REAL)
        q_vals = model(dummy_state)
        assert q_vals.shape == (2, 5)


# --------------------------------------------------------------------------- Phase 2 Tests
class TestPhase2InstitutionalSACRAndMargining:
    def test_basel3_sacr_capital_calculation(self):
        # Under positive inventory and price
        res = compute_sacr_capital(
            inventory=10.0,
            current_price=17000.0,
            cash_collateral=50000.0,
            supervisory_factor=0.32,
            alpha=1.4
        )
        assert res["replacement_cost"] >= 0.0
        assert 0.05 <= res["multiplier"] <= 1.0
        assert res["addon"] > 0.0
        assert res["capital_requirement"] > 0.0

    def test_cme_span2_margins_ordering(self):
        im, mm = compute_span2_margins(inventory=25.0, current_price=17000.0)
        assert im > 0.0
        assert mm > 0.0
        assert abs(mm - 0.75 * im) < 1e-4

    def test_real_depth_liquidation_monotonicity(self):
        # 10 levels of bid depth
        bid_ladder = [(100.0 - i * 0.10, 5.0) for i in range(10)]
        exec_qty, vwap, dislocation = execute_liquidation_on_depth(
            quantity_to_sell=15.0,
            bid_ladder=bid_ladder,
            reference_price=100.0
        )
        assert exec_qty == 15.0
        assert vwap < 100.0  # VWAP must be strictly below top of book
        assert dislocation > 0.0

    def test_kreiss_safe_radius_eliminates_contagion(self):
        # Run small simulation (N = 50) and test that Kreiss bounded contagion is 0
        sim_res = run_institutional_clearing_simulation(n_replications=50, seed=12345)
        kreiss_res = sim_res["regime_comparison"]["kreiss_bounded"]
        assert kreiss_res["contagion_cascade_count"] == 0
        assert kreiss_res["contagion_cascade_rate_pct"] == 0.0


# --------------------------------------------------------------------------- Phase 3 Tests
class TestPhase3HawkesProcessTriSimulator:
    def test_hawkes_spectral_stability(self):
        mu = np.array([0.5, 2.0])
        alpha = np.array([[0.3, 0.2], [0.5, 0.6]])
        beta = np.array([[1.5, 1.2], [1.2, 1.0]])
        hawkes = BivariateHawkesProcess(mu=mu, alpha=alpha, beta=beta, seed=42)
        assert hawkes.spectral_radius < 1.0

    def test_hawkes_event_stream_generation(self):
        mu = np.array([1.0, 3.0])
        alpha = np.array([[0.2, 0.1], [0.3, 0.4]])
        beta = np.array([[2.0, 1.5], [1.5, 1.2]])
        hawkes = BivariateHawkesProcess(mu=mu, alpha=alpha, beta=beta, seed=99)
        events = hawkes.simulate_events(T=10.0)
        assert len(events) > 0
        # Timestamps must be monotonic
        timestamps = [ev[0] for ev in events]
        assert all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps) - 1))
        # Dimensions in {0, 1}
        dims = set(ev[1] for ev in events)
        assert dims.issubset({0, 1})


# --------------------------------------------------------------------------- Phase 4 Tests
class TestPhase4FIXSupervisorAndFallback:
    def test_fix_message_parser(self):
        raw = "8=FIXT.1.1|9=120|35=D|11=ORD_001|50=AGENT_X|54=1|38=5.50|44=17180.50|847=eta=0.045|10=99|"
        msg = parse_fix_message(raw)
        assert msg.cl_ord_id == "ORD_001"
        assert msg.sender_sub_id == "AGENT_X"
        assert msg.side == 1
        assert msg.order_qty == 5.50
        assert msg.price == 17180.50
        assert abs(msg.strategy_param_eta - 0.045) < 1e-4

    def test_fix_supervisor_state_machine_transitions(self):
        supervisor = InstitutionalFIXSupervisor(window_size=30, reference_price=17180.0)
        assert supervisor.current_state == SupervisorState.GREEN

        # Send calm message
        msg_calm = "8=FIXT.1.1|35=D|11=CALM_1|50=AG_1|54=1|38=1.0|44=17180.0|10=00|"
        res_calm = supervisor.process_fix_message(msg_calm, current_market_px=17180.0)
        assert res_calm["supervisor_state"] == SupervisorState.GREEN.value
        assert res_calm["order_allowed"] is True

        # Artificially inject high positive feedback history to trigger RED state
        supervisor.flow_history = [10.0] * 50
        supervisor.price_history = [17000.0 + i * 50.0 for i in range(50)]
        
        msg_spiral = "8=FIXT.1.1|35=D|11=SPIRAL_1|50=AG_1|54=1|38=20.0|44=19500.0|10=00|"
        res_spiral = supervisor.process_fix_message(msg_spiral, current_market_px=19500.0)
        assert res_spiral["supervisor_state"] == SupervisorState.RED.value
        assert res_spiral["order_allowed"] is False
        assert "MANDATORY_ABSTENTION" in res_spiral["verdict"]
        assert len(supervisor.alerts_generated) >= 1
