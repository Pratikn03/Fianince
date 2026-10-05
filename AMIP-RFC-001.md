# Agentic Market Invariant Protocol (AMIP)
## RFC 001: Universal Pre-Trade Safety Standard for Autonomous Agentic AI in Financial Markets

**Status:** Open Industry Standard Specification (Reference Implementation v1.0)  
**Target Entities:** Tier-1 Investment Banks, Central Counterparties (CCPs), Quantitative Hedge Funds, Prime Brokers, Electronic Exchanges, Autonomous Agent Frameworks (LangChain, AutoGen, CrewAI, Deep RL)  
**Authors:** Machine Markets Consortium  
**Mathematical Foundation:** Machine Markets Manuscript (Lean 4 Machine-Checked Formalization)

---

### 1. Abstract & Scope

Autonomous agentic artificial intelligence—powered by Large Language Models (LLMs), deep reinforcement learning (RL), and autonomous multi-agent orchestration frameworks—is rapidly displacing legacy algorithmic execution in global financial markets. However, unlike deterministic rule-based algorithms, agentic AI introduces severe systemic vulnerabilities:
1. **Semantic Hallucination & Goal Drift:** Generating orders detached from fundamental portfolio constraints, misinterpreting market regime context, or executing inverted buy/sell logic.
2. **Endogenous Momentum Feedback ($Q > 0$):** Reinforcement learning agents optimize short-term reward by following trends, collectively driving aggregate market feedback across the critical boundary $S = a + Q \ge 1.0$.
3. **Nonnormal Transient Liquidation Cascades:** Balance-sheet and margin exhaustion causing forced liquidations that dislocate order book depth and trigger systemic multi-dealer contagion.

The **Agentic Market Invariant Protocol (AMIP)** establishes the universal, open-standard pre-trade interceptor and runtime verification protocol that **every financial institution and autonomous execution agent must implement** to guarantee systemic market solvency and prevent flash crashes.

```
                              THE AMIP RUNTIME ARCHITECTURE
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                           AUTONOMOUS AGENT LAYER                                       │
  │   [LLM Reasoning Core]    [Deep RL Policy Gradient]    [Multi-Agent Debate Network]    │
  └─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                            │ Proposed Agent Action (Envelope v1)
                                            ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                      AMIP ZERO-TRUST PRE-TRADE INTERCEPTOR                             │
  │                                                                                        │
  │   1. Semantic & Conservation Invariant Check (Anti-Hallucination Barrier)              │
  │      • Exact double-entry cash/inventory conservation balance check                    │
  │      • Tick size, price reasonability band (±2.5%), and limit order polarity           │
  │                                                                                        │
  │   2. Streaming Conic Feedback Certificate [S_lower, S_upper] (Anti-Runaway Barrier)    │
  │      • Sliding-window 2SLS causal gain identification in < 100 microseconds            │
  │      • Real-time classification: Green (< 0.95), Yellow (0.95-1.00), Red (>= 1.00)     │
  │                                                                                        │
  │   3. Pseudospectral Kreiss Solvency Radius r* = B / (K(J) * P) (Anti-Contagion Barrier)│
  │      • Dynamic position cap strictly bounded below clearing member margin buffers      │
  │      • Eliminates secondary liquidation contagion with mathematical certainty          │
  │                                                                                        │
  │   4. Mandatory Abstention State Machine & Fallback Router                              │
  │      • Green: Pass through to exchange with full quoting capacity                      │
  │      • Yellow: 50% capacity throttle, mandatory inventory half-life reduction          │
  │      • Red: Immediate drop of aggressive order routing; emergency passive pegging only │
  └─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                            │ Certified Safe Execution Order
                                            ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                          EXCHANGE MATCHING ENGINES & CCP                               │
  │             [FIFO Price-Time LOB]     [Pro-Rata CME]     [Elastic CDA]                 │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Message Envelope Specification (AMIP-Envelope v1)

Every order submitted by an autonomous agentic system MUST be encapsulated in an AMIP Envelope before transmission:

```json
{
  "amip_version": "1.0",
  "provenance": {
    "agent_id": "AGENT_LLM_DEEPSEEK_R1_V2",
    "agent_type": "AUTONOMOUS_MARKET_MAKER",
    "model_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "reasoning_trace_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "disclosed_memory_rate_eta": 0.025
  },
  "order": {
    "cl_ord_id": "AMIP_ORD_20261005_0001",
    "symbol": "BTC-USD-PERP",
    "side": "BUY",
    "order_qty": 2.50,
    "order_type": "LIMIT",
    "price": 17180.50,
    "time_in_force": "IOC"
  },
  "portfolio_context": {
    "current_inventory": 12.50,
    "cash_balance": 250000.0,
    "unrealized_pnl": 1420.0,
    "cme_span2_initial_margin": 45000.0,
    "cme_span2_maintenance_margin": 33750.0
  }
}
```

---

### 3. The Four Core Invariant Barriers

#### Barrier 1: Semantic & Physical Conservation Invariant
1. **Cash & Inventory Identity:** Marked equity $E_t = C_t + I_t P_t$ must be strictly conserved.
2. **Reasonability Band:** The proposed execution price $P_{\mathrm{order}}$ must satisfy:
   $$|P_{\mathrm{order}} - P_{\mathrm{mid}}| \le 3 \times \text{Spread}_t + \lambda \sqrt{Q_{\mathrm{order}}}$$
   Any order violating this bound indicates an agentic hallucination or quote stuffing attack and is immediately rejected.
3. **Polarity Check:** An agent intending to reduce risk must NOT submit an aggressive order in the direction of its existing directional exposure.

#### Barrier 2: Streaming Conic Feedback Certificate
The supervisor tracks the sliding-window 2SLS feedback gain estimate $\hat S = \hat a + \hat Q$ and conformal confidence interval $[S_{\mathrm{lower}}, S_{\mathrm{upper}}]$:
$$S_{\mathrm{upper}} = \hat S + 1.96 \cdot \hat \sigma_S$$
- **GREEN ($S_{\mathrm{upper}} < 0.95$):** Stable market. Full quoting authorized.
- **YELLOW ($0.95 \le S_{\mathrm{upper}} < 1.00$):** Pre-critical throttle. Order quantity restricted to $50\%$ of requested size.
- **RED ($S_{\mathrm{upper}} \ge 1.00$):** **Mandatory Abstention Protocol**. Aggressive liquidity-taking is forbidden; agents are pegged to passive resting quotes or halted.

#### Barrier 3: Pseudospectral Kreiss Solvency Radius (Theorem M5)
To prevent nonnormal transient growth and secondary liquidation cascades, total agent inventory is bounded by:
$$|I_t + \Delta I_t| \le r_i^* = \frac{B_i}{\mathcal{K}(J) \cdot P_t}$$
where:
- $B_i = E_t^{(i)} - \mathrm{MM}_t^{(i)}$ is the clearing member's unencumbered capital buffer;
- $\mathcal{K}(J) = \sup_{\varepsilon > 0} \varepsilon \cdot \|(zI - J)^{-1}\|$ is the Kreiss constant of the market dynamical Jacobian $J$.

#### Barrier 4: Operational Fallback & Fail-Safe Routing
If communication between the agent and the supervisor suffers latency $> 5$ ms or if the agent enters an unhandled exception state, the AMIP gateway activates deterministic fail-safe mode:
1. Cancellation of all unexecuted open limit orders (`Tag 35 = q`).
2. Immediate conversion of inventory to delta-neutral index hedges via passive algorithmic TWAP.
3. PagerDuty / WebSocket dispatch to the human risk desk.

---

### 4. Implementation Compliance Levels

- **AMIP Level 1 (Retail & Proprietary Trading):** Local Python interceptor protecting individual desks against prompt hallucination and leverage breaches.
- **AMIP Level 2 (Prime Brokers & Hedge Funds):** Co-located pre-trade risk proxy evaluating multi-agent portfolio exposures and CME SPAN 2 / Basel III SA-CCR margins.
- **AMIP Level 3 (Exchanges & CCPs):** Hardware-accelerated FPGA/kernel-bypass FIX Drop-Copy supervisor enforcing exchange-wide Conic Certificates and market-wide Mandatory Abstention.
