"""Phase 3: Two-Channel Group Market Simulation and 70/30 Split Protocol.

Implements:
1. Two-group adaptive market environment with distinct feedback channels:
   - Group A (e.g. fast or high-sensitivity chartists): q_A, eta_A
   - Group B (e.g. slow or lower-sensitivity chartists): q_B, eta_B
   - Fundamentalist: mean-reverting demand -phi * x_t
   - Noise trader: background flow disturbance
   - Dealer: absorbs net flow V_t, quotes price P_{t+1} = P_t + kappa * V_t
   - Probing mechanism:
     * Mode 'market': market-wide probe u_M
     * Mode 'group_A': targeted probe u_A to Group A's input
     * Mode 'group_B': targeted probe u_B to Group B's input

2. Data management:
   - Generates independent episodes with balanced signed pulses
   - 70/30 train/eval split (Discovery Sample vs. Held-out Evaluation Sample)
   - Verifies double-entry ledger accounting conservation
"""

import numpy as np


class TwoGroupMarketSimulator:
    def __init__(
        self,
        p_star=100.0,
        kappa=0.02,
        phi=30.0,
        q_A=0.30,
        eta_A=0.05,
        q_B=0.10,
        eta_B=0.05,
        flow_noise_std=0.05,
        quote_noise_std=0.002,
        seed=None,
    ):
        self.p_star = float(p_star)
        self.kappa = float(kappa)
        self.phi = float(phi)
        self.a = 1.0 - self.kappa * self.phi  # 1 - 0.02 * 30 = 0.40
        self.q_A = float(q_A)
        self.eta_A = float(eta_A)
        self.q_B = float(q_B)
        self.eta_B = float(eta_B)
        self.flow_noise_std = float(flow_noise_std)
        self.quote_noise_std = float(quote_noise_std)
        self.rng = np.random.default_rng(seed)

    def run_episode(self, T=64, probe_mode="market", probe_magnitude=4.0, probe_sign=1):
        """Simulate a single independent market episode of length T.
        probe_mode: 'market', 'group_A', or 'group_B'
        """
        # States
        x = 0.0
        m_A = 0.0
        m_B = 0.0

        prices = np.zeros(T + 1)
        prices[0] = self.p_star + self.rng.normal(0.0, self.quote_noise_std)

        # Ledger tracking
        shares_A = 0.0
        shares_B = 0.0
        shares_fund = 0.0
        shares_dealer = 0.0

        price_changes = np.zeros(T)

        for t in range(T):
            # Probes
            u_M = probe_sign * probe_magnitude if (t == 0 and probe_mode == "market") else 0.0
            u_A_in = probe_sign * probe_magnitude if (t == 0 and probe_mode == "group_A") else 0.0
            u_B_in = probe_sign * probe_magnitude if (t == 0 and probe_mode == "group_B") else 0.0

            # Demands
            # v_i = (q_i / kappa) * m_i
            v_A = (self.q_A / self.kappa) * m_A
            v_B = (self.q_B / self.kappa) * m_B
            v_fund = -self.phi * x
            v_noise = self.rng.normal(0.0, self.flow_noise_std)

            net_order = v_A + v_B + v_fund + v_noise + u_M

            # Price adjustment
            x_next = x + self.kappa * net_order
            # Observed quote with sensor noise
            p_next_obs = self.p_star + x_next + self.rng.normal(0.0, self.quote_noise_std)

            # Update memories
            # Group A updates from x plus any targeted input
            m_A = (1.0 - self.eta_A) * m_A + self.eta_A * (x + u_A_in)
            m_B = (1.0 - self.eta_B) * m_B + self.eta_B * (x + u_B_in)

            x = x_next
            prices[t + 1] = p_next_obs
            price_changes[t] = prices[t + 1] - prices[0]

            # Accounting updates
            shares_A += v_A
            shares_B += v_B
            shares_fund += v_fund
            shares_dealer -= net_order

        # Verify net share conservation among non-probe participants
        # dealer absorbs all net flows
        conservation_error = abs(shares_A + shares_B + shares_fund + shares_dealer + u_M)

        return {
            "probe_mode": probe_mode,
            "probe_sign": probe_sign,
            "probe_magnitude": probe_magnitude,
            "prices": prices,
            "price_changes": price_changes,
            "conservation_error": float(conservation_error),
        }


def generate_group_study_dataset(
    n_panels=100,
    episodes_per_panel=128,
    T=64,
    delta=4.0,
    seed=20260924,
    q_A=0.30,
    q_B=0.10,
):
    """Generate panel datasets crossing probe modes:
    - Market probes
    - Group A targeted probes
    - Group B targeted probes
    Splits into 70% Discovery (train) and 30% Evaluation (held-out).
    """
    rng = np.random.default_rng(seed)
    sim = TwoGroupMarketSimulator(q_A=q_A, q_B=q_B, seed=rng.integers(1e9))

    panels = []
    modes = ["market", "group_A", "group_B"]

    for p in range(n_panels):
        panel_data = {m: [] for m in modes}
        for m in modes:
            for ep in range(episodes_per_panel):
                sign = 1 if (ep % 2 == 0) else -1
                res = sim.run_episode(T=T, probe_mode=m, probe_magnitude=delta, probe_sign=sign)
                panel_data[m].append(res)
        panels.append({
            "panel_id": p,
            "data": panel_data,
        })

    # 70/30 split
    n_discovery = int(0.70 * n_panels)
    discovery_panels = panels[:n_discovery]
    evaluation_panels = panels[n_discovery:]

    return {
        "n_total": n_panels,
        "n_discovery": len(discovery_panels),
        "n_evaluation": len(evaluation_panels),
        "discovery_panels": discovery_panels,
        "evaluation_panels": evaluation_panels,
        "parameters": {
            "a": sim.a,
            "q_A": sim.q_A,
            "q_B": sim.q_B,
            "eta_A": sim.eta_A,
            "eta_B": sim.eta_B,
            "kappa": sim.kappa,
            "total_Q": sim.q_A + sim.q_B,
            "S": sim.a + sim.q_A + sim.q_B,
        },
    }


if __name__ == "__main__":
    dataset = generate_group_study_dataset(n_panels=20, episodes_per_panel=32, T=32)
    print("Generated Group Study Dataset:")
    print(f"  Total panels: {dataset['n_total']}")
    print(f"  Discovery sample: {dataset['n_discovery']}")
    print(f"  Evaluation sample: {dataset['n_evaluation']}")
    print(f"  True parameters: {dataset['parameters']}")
