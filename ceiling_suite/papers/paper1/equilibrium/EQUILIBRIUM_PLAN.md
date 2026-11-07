# Paper 1 equilibrium extension: Kyle insider with feedback cohorts (plan, 7 November 2026)

**Decision (author, 7 November 2026).**
- The extension is folded into Paper 1.
- Mechanism: a strategic informed trader and a competitive market maker, with the paper's exponential-memory
  feedback cohorts.
- It may build on Paper 2, with attribution.

**Standing rule still in force.** Paper 2's cost-separation results stay out of Paper 1. That rule was set before
this decision, and it is kept unless the author lifts it explicitly.

## 1. Why this, and the one finding that shapes everything

The referee objection is that price impact κ and pricing-error persistence a are assumed, not derived, and that
no one optimizes. A Kyle insider plus a market maker makes κ an equilibrium object.

**The finding that shapes the design.** Feedback cohorts trade on the public price history. A rational,
risk-neutral market maker who knows their aggregate kernel k_m = Σ_i w_i r_i^m can compute their aggregate flow
f_t = Σ_m k_m Δp_{t-m}. It nets that flow out of total order flow, so predictable feedback flow then has **no
price impact**.

In that benchmark the closed loop of Paper 1 does not exist in equilibrium. Prices would carry no information about
the cohorts, and the identification results would be about a non-equilibrium reduced form. The plan therefore needs
a channel through which predictable flow moves prices. There are two candidates, and each is a modelling fork:

| Fork | Channel | Prices respond to feedback flow? | What identifies the cohorts |
|---|---|---|---|
| A. Inventory | The market maker bears inventory cost (Grossman–Miller, Ho–Stoll): p_t = E[v \| F_t] − γ I_t | Yes, with impact γ (κ becomes the inventory coefficient) | Prices, as in Paper 1 |
| B. Kernel uncertainty | A risk-neutral market maker that does not know the kernel and learns it | Only through its estimation error | The market maker's order-flow regression; an outsider who sees prices only learns much less |

**Recommendation: build both.**
- Fork A makes Paper 1's closed loop an equilibrium outcome.
- Fork B gives the sharpest new result (E2 below).

They combine naturally: a market maker with inventory cost that is also learning the kernel.

## 2. Model (discrete time; stationary version)

- **Value.** v ~ N(0, Σ₀), revealed at a random date with geometric hazard 1−ρ (Caldentey–Stacchetti 2010). This
  gives constant equilibrium coefficients, matching Paper 1's constant κ.
- **Insider.** Knows v and submits x_t to maximize expected profit.
- **Noise traders.** z_t ~ N(0, σ_z²), i.i.d.
- **Feedback cohorts** i = 1..K. Positions follow u_{i,t} = r_i u_{i,t-1} + w_i Δp_{t-1}, the paper's exponential
  memory on price changes. Aggregate flow is f_t = Σ_i (u_{i,t} − u_{i,t-1}), or the position form, fixed in the
  draft.
- **Market maker.** Competitive. Sees total order flow y_t = x_t + z_t + f_t.
  - Fork A: sets p_t = E[v \| y^t] − γ I_t, where I_t is its inventory.
  - Fork B: γ = 0, and the kernel is estimated from data.
- **Observers.**
  - A supervisor who sees prices only, which is Paper 1's observer.
  - A supervisor with class-tagged records.

## 3. Theorem targets

| ID | Statement (conjectured) | Novelty against the literature | Difficulty |
|---|---|---|---|
| **E1** Equilibrium invariance | Two economies with the same aggregate kernel, i.e. the same merged measure M, have the same equilibrium: prices, insider strategy, market-maker coefficients, informativeness. Group-level non-identification is economically irrelevant to every agent that acts on prices. | New as a link between the identification boundary and equilibrium. Close: Noh (2026, arXiv 2601.09872), a continuous-time Kyle model with momentum and contrarian traders whose rule the market maker knows; no identification. Holds for deterministic cohort rules; cohort-specific demand noise breaks it, and the paper must say so. | Low (linear aggregation). The value is the framing. |
| **E2** Manipulation rents while learning | If the market maker uses an estimated kernel k̂, the insider can "pump" the cohorts, and its extra profit is bounded by C‖k − k̂‖ (and is of that order). The aggregate kernel is learnable at the ordinary T^{-1/2} rate, so rents vanish fast, while group separation still needs (Δη)^{-(4K-2)}. | Manipulation with feedback traders is classical (De Long et al. 1990; Allen–Gale 1992). New: rents tied to kernel estimation error, and the contrast with the group-separation rate. | Medium–high. Needs a fixed point under misspecification. |
| **E3** Equilibrium targeted intervention | Two economies with nearly equal aggregate kernels (the Gauss/Radau pair of Proposition `prop:target`) have nearly identical pre-intervention equilibria. Halting the largest group leads to post-halt equilibria whose price impact and fragility differ by O(1). | Extends `prop:target` from a reduced form to equilibrium. | Medium. Reuses E1 and the Paper 1 machinery. |
| **E4** Endogenous κ | In Fork A, the closed-loop impact κ equals the inventory coefficient plus the Kyle λ term. The stability condition of Paper 1 becomes a condition on primitives (γ, σ_z, Σ₀, ρ, kernel). | Combines Kyle with inventory with feedback; check against Paper 2's depth condition, attributed. | Medium. |
| **E5** Disclosure in equilibrium | Publishing class-tagged flow reveals nothing about v from deterministic cohorts. Its equilibrium effect comes from identifying the insider's class (Huddart–Hughes–Levine 2001: dissimulation) and from enabling targeted supervision (E3). | Positions the value of disclosure from Paper 1 against Huddart–Hughes–Levine. | Medium. |

## 4. Work plan

1. **Literature check (days).**
   - Kyle 1985, Back 1992, Caldentey–Stacchetti 2010.
   - De Long–Shleifer–Summers–Waldmann 1990, Allen–Gale 1992.
   - Huddart–Hughes–Levine 2001, Grossman–Miller 1988, Noh 2026.
   - Collin-Dufresne–Fos (stochastic noise).
   - For each: what it proves, and what E1–E5 add.
2. **E1 and E4 (1–2 weeks).**
   - Solve Fork A in closed form for one cohort, then K cohorts.
   - Prove E1 by aggregation.
   - Numerical check with a simulator built on the existing recursion.
3. **E3 (1–2 weeks).** Equilibrium version of `prop:target` for K = 2.
4. **E2 (3–6 weeks).** The hardest part. Start with a one-period-ahead misspecified market maker, bound the
   insider's deviation profit, then the stationary case.
5. **Lean (in parallel).** E1 is a good formal target (linear aggregation). E3 can reuse `p1_prop_target`.
6. **Paper integration.**
   - New Section "Equilibrium" in the main text, about 6–8 pages, with proofs in the supplement.
   - Abstract and Table `tab:whatnew` updated.
   - The main text must stay at about 40 pages, so the equilibrium section replaces material that moves to the
     supplement.

## 5. Risks, stated now

- **The benchmark kills the closed loop.** With a risk-neutral market maker that knows the kernel, feedback has no
  price effect (Section 1). If the referee prefers that benchmark, Paper 1's price-only identification becomes a
  statement about markets whose market maker bears inventory risk or is learning. The paper must say this openly. It
  changes how the main results are interpreted.
- **E1 may be judged "too easy".** The paper's interest then rests on E2 and E3.
- **Timeline.** Months, not weeks. Paper 1's SSRN posting is delayed until at least E1, E3 and E4 are done, by the
  author's choice to fold the extension in.
- **Taiwan test.** P1T stays as registered. The equilibrium work does not change the frozen test.

## Sources consulted for this plan

- Noh (2026), "A continuous-time Kyle model with price-responsive traders", arXiv 2601.09872.
- Caldentey and Stacchetti (2010), "Insider trading with a random deadline", Econometrica 78(1), 245–283.

## Status (7 November 2026, evening)

- **E1 done.** Theorem `thm:eqinv` (main text) with its proof in Supplement S28. Machine-checked pathwise in
  `Paper1EquilibriumInvariance.lean`, CI pending at commit 708beda. Numerical illustration in `e1_demo.py`.
- **E2 done in a stated partial-equilibrium form.** Theorem `thm:rents` gives the insider's best response to a
  dealer with a fixed coefficient λ and a misjudged kernel:
  - exact value;
  - an explicit bound |ΔV| ≤ 2Σ₀T²ε/(1−λε);
  - the first-order coefficient;
  - the learning corollary, which rests on an assumed √n estimator rate.

  Proved on paper; numerical check in `e2_rents.py`. Not done: re-solving the dealer's λ, adaptive (non-committed)
  insider strategies, and a proof of the estimator rate.
- **E3 done.** Theorem `thm:eqhalt`:
  - kernel gap O(d³) with an explicit constant;
  - pre-halt price gap O(d³);
  - post-halt kernel gap W/4 at every spacing.

  Proved on paper; numerical check in `e3_halt.py` (pre-halt gap ≈ 3d³, post-halt ≈ 0.19).
- **E4 done** (Fork A, in a stated form). Theorem `thm:inventory`, now Theorem 4.1, opens the new main-text Section 4,
  "Equilibrium foundations". E1–E3 follow it as Theorems 4.2–4.4.
  - Model: overlapping generations of CARA dealers with risk aversion A, who carry inventory with layoff share 1−ā,
    plus a public random-walk fundamental. No Kyle insider in this part.
  - (i) Characterization: β_i = κ/(D−r_i), D = 1−κG(D) with G the Stieltjes transform of M, κ(D−ā) = AVD and
    V = σ_F²+κ²σ_ξ²/D².
  - (ii) No-feedback closed form, which is exactly Paper 1's x_t = ā x_{t−1} + κ y_t, with the existence condition.
  - (iii) Invariance through G.
  - (iv) Small-feedback existence and uniqueness by the implicit function theorem, with first-order formulas.
  - Lean `Paper1InventoryEquilibrium.lean` proves the FOC in every state, the innovation coefficient κ/D and the
    benchmark existence iff. Parts (iii)–(iv) are proved on paper.
  - Numerics in `e4_inventory.py`. Positive feedback raises impact and shrinks the existence region: A* is 0.40,
    0.255, 0.130, 0.068 and 0.034 for G(1) = 0, 0.067, 0.167, 0.333 and 0.667.
  - **Not done.** The combination with the Kyle insider (the λ term).
- **Rate in equilibrium done.** Theorem `thm:eqreduced` (now 4.2). Pathwise, the equilibrium price is the paper's
  closed loop with a* = ā/D, κ* = κ/D and w̃_i = (D−ā)w_i/(D−r_i), at the same memory rates.
  - So the zeros, the merged-measure boundary and every flow-to-price result transfer, with constants at the
    effective parameters.
  - The Gauss/Radau lower-bound pair of Theorem kcohort is realized by two equilibria with identical primitives:
    D = 1 − κ*W/(1−a*), and the kcohort stability condition gives D > every rate.
  - Lean `Paper1EquilibriumReducedForm.lean` covers the pathwise identity and the realization. Numerics in
    `e4_reduced_form.py`: paths agree to 4e-16, and the pair's gap is ≈ 1.25 d³.
  - New assumption, stated in the paper: dealers price the probe as part of exogenous noise.
- **Fragility done for one cohort.** Theorem `thm:fragility` (now 4.3).
  - A positive-impact equilibrium exists iff A ≤ A*(w) = max Ψ_w, and every such equilibrium is stable.
  - A* is strictly decreasing in w, with A* → (1−ā)/(2σ_Fσ_ξ) as w → 0.
  - A* < min{A*_0, Φ*/(σ_F² w)}, and w A* → Φ*/σ_F². In terms of G(1): A* < (1−ā)(1−r)/(4σ_F²G(1)).
  - The Lean necessary conditions are in the same file. Several cohorts: numerical only.
- **Still open.** E5 (disclosure in equilibrium). Lean versions of E2, E3 and E4(iii)–(iv).

## Status (7 November 2026, late evening)

- **Numbering now:** 4.1 inventory, 4.2 closed loop, 4.3 disclosure corollary, 4.4 fragility, 4.5 invariance;
  S28.1 rents; S28.2 halt.
- **Stability of every positive multi-cohort equilibrium proved** (Theorem 4.4(iv)): Perron–Frobenius at the
  effective parameters, plus κΣ g_i/(1−r_i) < 1. The inequality core is in Lean (`Paper1EquilibriumExtras.lean`).
- **E5, partial (Corollary 4.3).** Tagged-flow identification and the value of disclosure hold in equilibrium, with
  the true weights. The Huddart–Hughes–Levine dissimulation channel needs an insider and is not covered.
- **Lean** (`Paper1EquilibriumExtras.lean`), built locally because GitHub Actions is blocked by billing:
  - the necessity direction of Theorem 4.1(i);
  - S28.1(i) optimum and value;
  - S28.2(iii).
- **Gauss/Radau largest weights differ for K = 2..200** (numerical); a proof for every K is open.
- **Still open:**
  - the strategic insider inside the inventory equilibrium;
  - the implicit function theorem of Theorem 4.1(iv) in Lean;
  - Perron–Frobenius in Lean;
  - the O(d³) kernel bound of S28.2(i) in Lean.

## Status addendum (7 November 2026, night)

- **Insider inside the inventory equilibrium, done in a stated form** (Theorem 4.6, `thm:insider`):
  - a short-lived insider who observes only her news;
  - the characterization, and the Kyle limit;
  - invariance, and the observer's reduced form with a known MA(1) input, so the rates hold.
  - Positive feedback raises impact and lowers informativeness.
  - Lean: `Paper1EquilibriumInsider.lean`, built locally. Numerics: `e6_insider.py`.
- **Not solved:** an insider who also uses the public state, which adds an arbitrage term against predictable
  mispricing; and a long-lived Kyle insider.
