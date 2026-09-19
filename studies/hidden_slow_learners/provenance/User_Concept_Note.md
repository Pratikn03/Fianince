Yes. I think we can turn this into something **substantially larger than a conventional “AI in finance” dissertation**.

The key is to stop framing it as:

> *What effects will AI have on financial markets?*

and instead ask whether the **mathematical behavior of the financial system itself changes when decision-making shifts from humans to adaptive machines**.

# Proposed flagship research program

## **From Human Markets to Machine Markets**

### *A Theory of Financial Stability Under Adaptive Autonomous Agents*

The central question would be:

> **Under what conditions does large-scale delegation of financial decision-making to adaptive AI agents cause a regime change in price formation, liquidity, market equilibrium and systemic stability?**

That wording is stronger than the original question because it gives us something that can actually be **derived, measured, simulated and falsified**.

---

# 1. The fundamental idea

Classical finance usually models some variation of:

```math
Information \rightarrow Agent\ Beliefs \rightarrow Decisions \rightarrow Prices
```

The agents may be rational, boundedly rational, behavioral, institutional, heterogeneous, etc.

But they are generally treated as having decision rules that don't fundamentally **rewrite themselves at machine speed as a consequence of market feedback**.

Adaptive autonomous AI introduces:

```math
Market_t \rightarrow AI_t \rightarrow Action_t \rightarrow Market_{t+1}
```

while simultaneously:

```math
Market_{t+1} \rightarrow Learning \rightarrow AI_{t+1}
```

Therefore:

```math
\boxed{ Market\ State \leftrightarrow Agent\ Policy }
```

Both evolve together.

That's the key phenomenon.

---

# 2. Our main theoretical claim to investigate

I would build the research around this proposition:

> ### **Financial-market behavior is not invariant to the architecture of the agents making financial decisions.**

Meaning that identical:

- information,
- preferences,
- capital,
- leverage,
- assets,
- objectives,
- shocks

could still produce different systemic outcomes simply because agents use different **decision architectures**.

The ECB now has experimental evidence pointing directly in this direction: Q-learning and LLM agents placed in comparable financial environments produced materially different coordination and bank-run-like behavior. ([European Central Bank](https://www.ecb.europa.eu/press/research-publications/resbull/2026/html/ecb.rb260521~4d8b12940b.en.html?utm_source=chatgpt.com "Financial stability in the age of artificial intelligence: the role of algorithmic architecture"))

But that's just the beginning.

They show:

```math
Architecture \rightarrow Different\ outcome
```

Our objective would be to derive:

```math
\boxed{ Architecture + Autonomy + Adaptation + Similarity + Market\ Structure \rightarrow Systemic\ Regime }
```

That's much broader.

---

# 3. Don't search for one AI threshold

Earlier I suggested:

```math
\alpha^*
```

as a critical AI participation threshold.

I would now make this more sophisticated.

There probably isn't simply:

> **42% AI = dangerous.**

Instead, there may be a **critical stability surface**.

Suppose:

```math
\alpha = AI\ autonomy/exposure
```

```math
C = algorithmic\ similarity
```

```math
\eta = adaptation\ speed
```

```math
L = leverage
```

```math
Q = market\ liquidity
```

```math
H = human\ intervention\ latency
```

Then systemic stability becomes:

```math
S = f(\alpha,C,\eta,L,Q,H,...)
```

And there may exist a boundary:

```math
\boxed{ \Omega^* }
```

such that:

```math
(\alpha,C,\eta,L,Q,H) \in \Omega_{stable}
```

produces stable markets,

while crossing the boundary gives:

```math
(\alpha,C,\eta,L,Q,H) \in \Omega_{critical}
```

and eventually:

```math
\Omega_{unstable}.
```

That is a much more defensible research target.

---

# 4. The Machine-Market Criticality Principle

This could become the centerpiece.

Consider the financial system:

```math
X_{t+1}=F(X_t,A_t,\epsilon_t)
```

where:

- `X_t` = financial-system state,
- `A_t` = aggregate AI/human actions,
- `\epsilon_t` = external shocks.

Each AI agent uses:

```math
a_{i,t} = \pi_i(X_t,I_{i,t},\theta_{i,t})
```

and adapts:

```math
\theta_{i,t+1} = G_i(\theta_{i,t},X_t,a_{i,t},R_{i,t})
```

Now the important object becomes the feedback Jacobian:

```math
J_t = \frac{\partial F}{\partial A} \frac{\partial A}{\partial X}
```

plus the effect of learning itself.

Then roughly:

```math
\rho(J_t)<1
```

means disturbances decay.

But:

```math
\rho(J_t)>1
```

means disturbances amplify.

Where:

```math
\rho()
```

is the spectral radius.

This gives us a potentially powerful quantity:

# **Machine-Market Criticality — MMC**

```math
\boxed{ MMC_t=\rho(J_t) }
```

Interpretation:

```math
MMC<1 \Rightarrow Stable
```

```math
MMC\approx1 \Rightarrow Critical
```

```math
MMC>1 \Rightarrow Amplifying
```

If a rigorous theoretical relationship like that survived proof and experiments, **that would be much more important than another stock-prediction model**.

---

# 5. A second new measurement

We also need to measure **how much of the financial system is actually controlled by AI**.

Counting algorithms would be useless.

Instead define:

## Machine Autonomy Exposure — MAE

Something like:

```math
MAE_t= \frac{ \sum_i E_{i,t}A_{i,t} }{ \sum_i E_{i,t} }
```

where:

- `E_i` = financial exposure/capital controlled,
- `A_i\in[0,1]` = autonomy level.

For example:

Human recommendation software:

```math
A=0.1
```

AI recommending but requiring approval:

```math
A=0.4
```

AI executing within limits:

```math
A=0.7
```

fully autonomous adaptive agent:

```math
A=1.
```

Now regulators could ask:

> What percentage of economically consequential decisions are effectively machine-controlled?

That's more meaningful than:

> How many banks use AI?

---

# 6. Then another missing quantity

Suppose 70% of the market uses AI.

That's not necessarily bad.

If every system behaves differently:

```math
Diversity \uparrow
```

could potentially stabilize the market.

But imagine 70% uses:

- the same foundation model,
- same data,
- same signals,
- similar prompts,
- same risk objectives.

Then:

```math
MAE=70\%
```

plus:

```math
Algorithmic\ Similarity=90\%
```

could behave very differently.

The FSB already identifies common models, correlations and third-party concentration as potential systemic vulnerabilities. ([Financial Stability Board](https://www.fsb.org/2024/11/the-financial-stability-implications-of-artificial-intelligence/?utm_source=chatgpt.com "The Financial Stability Implications of Artificial Intelligence - Financial Stability Board"))

So we introduce:

# **Algorithmic Decision Concentration — ADC**

Not just:

```math
\text{provider market share}
```

but similarity across:

```math
Model
```

```math
Data
```

```math
Objective
```

```math
Architecture
```

```math
Policy
```

```math
Response
```

Perhaps:

```math
ADC= w_1M+ w_2D+ w_3O+ w_4P+ w_5R.
```

Eventually we'd replace an arbitrary weighted index with a statistically identifiable measure.

---

# 7. The profound hypothesis

Here's where it becomes interesting.

Financial stability might depend on the interaction:

```math
\boxed{ MAE \times ADC \times AdaptationSpeed }
```

rather than simply AI adoption.

For example:

### Scenario A

```math
MAE=80\%
```

but:

```math
ADC=10\%
```

Highly diverse AI ecosystem.

Potentially stable.

### Scenario B

```math
MAE=40\%
```

but:

```math
ADC=95\%
```

Highly homogeneous agents.

Potentially dangerous.

Thus:

> **The dangerous variable may not be how much AI finance uses—it may be how similarly autonomous machines perceive and react to the same world.**

That's a much stronger research proposition.

---

# 8. A paradox we should specifically test

A very interesting 2026 agent-based study reports that increasing AI participation can **reduce ordinary volatility while increasing similarity among trading strategies and sensitivity to common shocks**. ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2214635026000894?utm_source=chatgpt.com "Artificial intelligence, market stability, and tail risk: A computational agent-based study - ScienceDirect"))

That suggests a potential paradox:

# **The Machine Stability Paradox**

```math
AI\ adoption\uparrow
```

could produce:

```math
Normal\ volatility\downarrow
```

while simultaneously:

```math
Tail\ systemic\ risk\uparrow.
```

In other words:

> **AI could make markets look safer during ordinary periods while making them more fragile during extreme periods.**

That is potentially extremely important.

It resembles other complex systems where suppressing small fluctuations allows hidden correlations to accumulate.

---

# 9. Candidate Law I — Machine Stability Paradox

Hypothesis:

```math
\frac{\partial \sigma_{normal}}{\partial MAE}<0
```

while:

```math
\frac{\partial TailRisk}{\partial MAE}>0
```

when algorithmic similarity exceeds some critical level.

We would need to prove conditions under which this occurs.

If it doesn't occur, we reject it.

That's science.

---

# 10. Candidate Law II — Algorithmic Diversity Principle

Another hypothesis:

> **Systemic stability depends more strongly on behavioral diversity among autonomous agents than on the absolute number of autonomous agents.**

Mathematically:

```math
Risk = f(MAE,ADC)
```

with:

```math
\frac{\partial Risk}{\partial ADC} > \frac{\partial Risk}{\partial MAE}
```

under some regimes.

This would have huge implications.

Instead of regulators saying:

> Limit AI.

They might eventually say:

> Prevent excessive algorithmic monoculture.

That's a fundamentally different policy.

---

# 11. Candidate Law III — Machine Reflexivity

Prediction:

```math
P_{t+1}\downarrow
```

causes AI to sell.

Selling causes:

```math
P_{t+1}\downarrow.
```

Another AI observes the movement.

It updates.

It sells.

Therefore:

```math
Prediction \rightarrow Action \rightarrow Market \rightarrow Learning \rightarrow Prediction.
```

Define:

```math
R_m= \frac{ \text{endogenous price movement} }{ \text{fundamental price movement} }
```

Call it:

## Machine Reflexivity Ratio

If:

```math
R_m\gg1
```

then machines are increasingly responding to conditions that **machines themselves created**.

That is a very interesting market state.

---

# 12. Candidate Law IV — Machine-Speed Instability

Traditional regulators operate on a human time scale.

Suppose:

```math
T_A = AI\ response\ time
```

and:

```math
T_R = regulatory/human\ intervention\ time.
```

Define:

```math
\boxed{ \Lambda=\frac{T_R}{T_A} }
```

If:

```math
\Lambda \approx 1
```

humans can respond roughly as quickly as the system evolves.

But:

```math
\Lambda=10^6
```

would mean:

> Machines complete one million meaningful feedback cycles before humans can intervene.

Then the relevant financial stability question changes.

The BIS says AI and digital finance can increase the **speed, intensity and complexity** of shock propagation. ([Bank for International Settlements](https://www.bis.org/speeches/20260126-financial-stability-implications-artificial-intelligence-and-digital-finance?utm_source=chatgpt.com "The financial stability implications of artificial intelligence and digital finance | Bank for International Settlements"))

The IMF similarly argues that AI is making financial markets faster and more tightly coupled and calls for system-wide exercises incorporating AI-enabled scenarios. ([IMF](https://www.imf.org/en/blogs/articles/2026/07/23/how-central-banks-can-contain-financial-stability-risks-as-ai-accelerates-change?utm_source=chatgpt.com "How Central Banks Can Contain Financial Stability Risks as AI Accelerates Change"))

So this isn't science fiction anymore.

---

# 13. Candidate Law V — Individually Rational, Collectively Catastrophic

This may become the deepest theorem.

Every AI solves:

```math
a_i^* = \arg\max_{a_i} E[U_i].
```

Therefore every agent can be acting rationally.

But:

```math
\{a_1^*,a_2^*,...,a_n^*\}
```

could cause:

```math
SystemicLoss \rightarrow huge.
```

Therefore:

```math
\boxed{ Individual\ Machine\ Optimality \not\Rightarrow Systemic\ Optimality }
```

Human finance already knows versions of this phenomenon.

But adaptive machines introduce:

- much shorter response times,
- high model similarity,
- continuous optimization,
- rapid learning,
- shared information,
- automated execution.

Therefore the severity and structure could fundamentally change.

---

# 14. This becomes our actual framework

I'd call the theoretical program:

# **Machine-Market Transition Theory — MMTT**

Not because we're declaring a new theory today.

The research program would investigate whether one exists.

The framework would have approximately six state variables:

```math
\boxed{ \mathcal{M} = (MAE,ADC,\eta,L,Q,H) }
```

where:

| SymbolMeaning |                                       |
| ------------- | ------------------------------------- |
| `MAE`         | Machine Autonomy Exposure             |
| `ADC`         | Algorithmic Decision Concentration    |
| `\eta`        | Adaptation speed                      |
| `L`           | Financial leverage                    |
| `Q`           | Market liquidity                      |
| `H`           | Human/regulatory intervention latency |

And outcome variables:

```math
Volatility
```

```math
Liquidity
```

```math
Price\ Efficiency
```

```math
Tail\ Risk
```

```math
Contagion
```

```math
Recovery\ Time
```

```math
Systemic\ Loss.
```

---

# 15. The experiment becomes enormous but manageable

Create an artificial financial economy.

We might eventually have:

```math
N=10,000+
```

agents.

Include:

### Human-like agents

- value investors
- momentum traders
- noise traders
- market makers
- banks
- hedge funds
- households

### Machine agents

- RL agents
- transformer agents
- LLM agents
- rule-based algorithms
- tool-using autonomous agents
- risk-management agents

Then vary:

```math
MAE = 0,10,20,\ldots,100\%.
```

And independently vary:

```math
ADC
```

```math
\eta
```

```math
L
```

```math
Q
```

```math
H.
```

That produces a **phase diagram of machine finance**.

---

# 16. What we want to discover

Maybe the result looks something like:

```text
                  ALGORITHMIC CONCENTRATION

             Low                High
        ┌──────────────────────────────────┐
 Low    │  STABLE          │  CORRELATED   │
 AI     │                  │               │
        ├──────────────────────────────────┤
 Mid    │  EFFICIENT       │  FRAGILE      │
 AI     │                  │               │
        ├──────────────────────────────────┤
 High   │  MACHINE         │  SYSTEMIC     │
 AI     │  EQUILIBRIUM     │  CRITICALITY  │
        └──────────────────────────────────┘
```

Obviously those labels cannot be assumed beforehand.

The experiment determines the regions.

That's what makes this scientifically meaningful.

---

# 17. Then introduce shocks

We shouldn't only simulate stock-price changes.

Hit the system with:

### Macroeconomic shock

```math
InterestRate +300bp
```

### Liquidity shock

```math
MarketDepth -70\%
```

### Information shock

False news.

### AI shock

Model provider outage.

### Model update

Common foundation model changes simultaneously.

### Cyber shock

Shared service failure.

### Policy shock

Unexpected monetary decision.

### Geopolitical shock

Commodity disruption.

### Agent failure

Major autonomous market maker malfunctions.

Then measure:

```math
Shock \rightarrow Propagation \rightarrow Amplification \rightarrow Recovery.
```

---

# 18. Here's where the global impact becomes real

Suppose eventually the framework can tell regulators:

> Your financial system has:

```math
MAE=0.62
```

```math
ADC=0.81
```

```math
MMC=0.93.
```

A major model update raises:

```math
MMC: 0.93\rightarrow1.08.
```

Now the system has crossed the theoretically identified critical region.

That is very different from current supervision.

Today regulators stress-test things such as:

- unemployment,
- GDP,
- property prices,
- rates,
- credit losses.

Future stress testing could additionally include:

```math
AI\ concentration
```

```math
AI\ learning
```

```math
AI\ synchronization
```

```math
AI\ autonomy.
```

The Bank of England has already identified the need for **visibility, indicators and intervention mechanisms** for collective autonomous AI behavior and is working with the BIS Innovation Hub on Project Logos, where LLM-based agents act as portfolio managers in simulated markets. ([Bank of England](https://www.bankofengland.co.uk/financial-stability-report/2026/july-2026?utm_source=chatgpt.com "Financial Stability Report - July 2026 | Bank of England – the UK's central bank"))

That's a strong indication that this research problem matters to real central banks.

---

# 19. It should not stop at trading

That's important.

Otherwise this becomes a narrow computational-finance project.

Eventually extend it into:

### Capital markets

```math
AI\leftrightarrow Trading
```

### Banking

```math
AI\leftrightarrow Lending
```

### Asset management

```math
AI\leftrightarrow Allocation
```

### Insurance

```math
AI\leftrightarrow Underwriting
```

### Payments

```math
AI\leftrightarrow Transactions
```

### Corporate finance

```math
AI\leftrightarrow Capital\ Decisions
```

### Household finance

```math
AI\leftrightarrow Saving/Borrowing
```

The IMF already describes agentic AI in payments as a potential **structural shift in the architecture of financial systems**, because agents can move beyond recommendations and initiate or coordinate transactions under delegated authority. ([IMF eLibrary](https://www.elibrary.imf.org/view/journals/068/2026/004/article-A001-en.xml?utm_source=chatgpt.com "How Agentic AI Will Reshape Payments"))

So our ultimate model becomes:

```math
\boxed{ Autonomous\ Financial\ Economy }
```

rather than merely:

```math
AI\ Trading.
```

---

# 20. The dissertation should therefore be a sequence

### Paper 1 — Theory

**From Human Markets to Machine Markets: A Theory of Adaptive-Agent Financial Stability**

Derive:

```math
MMC
```

critical conditions and stability propositions.

---

### Paper 2 — Emergence

**Do AI-Dominated Financial Markets Exhibit Critical Transitions?**

Mass multi-agent simulation.

Identify:

```math
\Omega^*.
```

---

### Paper 3 — Algorithmic monoculture

**Algorithmic Diversity and Systemic Financial Stability**

Test:

```math
ADC \rightarrow TailRisk.
```

---

### Paper 4 — Reflexivity

**Machine Reflexivity in Autonomous Financial Markets**

Determine whether AI-generated actions increasingly become the information future AI agents respond to.

---

### Paper 5 — Intervention

**How Do We Stabilize a Machine-Speed Financial System?**

Compare:

```math
Human\ intervention
```

vs.

```math
automated\ circuit\ breakers
```

vs.

```math
reliability-gated\ agents
```

vs.

```math
diversity\ requirements.
```

---

### Paper 6 — Global financial stability

**Stress Testing the Autonomous Financial System**

Convert everything into something institutions like:

- BIS,
- IMF,
- central banks,
- securities regulators,
- major exchanges

could potentially evaluate.

The FSB has already said authorities face information gaps around AI adoption and need better monitoring and assessment of whether current financial policy frameworks remain adequate. ([Financial Stability Board](https://www.fsb.org/2024/11/the-financial-stability-implications-of-artificial-intelligence/?utm_source=chatgpt.com "The Financial Stability Implications of Artificial Intelligence - Financial Stability Board"))

---

# 21. The ultimate question is even bigger

I would put this on the first page of the research vision:

> **For centuries, financial theory has studied markets populated principally by humans and institutions acting on human behalf. That assumption may no longer hold. This research asks whether markets remain governed by the same stability relationships once adaptive artificial agents become economically significant actors capable of observing, learning from and altering the environment in which they operate.**

Then the one-sentence mission:

> ### **Develop the theoretical and empirical foundations necessary to understand, measure and control systemic risk in financial systems increasingly governed by autonomous adaptive agents.**

That's the research program.

---

# 22. What would make this genuinely paradigm-level

It **will not** become paradigm-level merely because the question sounds large.

For that level, we need to produce at least some combination of:

1. **A new theoretical result** — ideally provable stability/instability conditions.
2. **A measurable state variable** such as machine-market criticality.
3. **A reproducible financial-agent testbed.**
4. **Evidence of a previously unknown regime transition.**
5. **A result that generalizes across architectures**, rather than one LLM.
6. **Real-market empirical evidence.**
7. **A policy intervention that works predictably.**
8. Eventually, **independent replication by other researchers.**

If we accomplish only #3:

> interesting ML paper.

If we accomplish #1 + #3:

> strong PhD research.

If we accomplish #1–5:

> potentially major finance/AI research.

If #1–8 hold and other researchers build on it:

> that's where discussion of a **new paradigm** becomes credible.

## The direction I would lock in

I would **not** make the thesis simply:

> *“What happens when AI controls financial markets?”*

I'd lock the core question as:

> **Does the transition from human-mediated to adaptive machine-mediated financial decision-making create identifiable critical regimes in which traditional relationships among information, liquidity, volatility and systemic risk cease to hold—and can those regimes be predicted before instability occurs?**

That gives us a target much more ambitious than predicting prices.

The target becomes:

```math
\boxed{\text{Predict the transition into financial instability itself.}}
```

And **that** is the version I think is worth building seriously.