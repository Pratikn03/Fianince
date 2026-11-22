# P1A: an AMM–CEX test of Paper 1. Design note (not a spec, nothing registered, no data read)

21 November 2026. Written by an AI system for the authors. Judgement, not independent review.

**22 November 2026:** the liquidity-side test below is now drafted, with its power simulation, in
`p1a_liquidity/P1A_liquidity_spec_DRAFT.md`. It is still not registered, and no data has been read.

## Correction to the plan of 21 November

The plan called the AMM–CEX laboratory "the first direct test of Theorem n:suff". That was wrong, for this reason.

In a constant-function AMM:
- the pool price is a deterministic function of net order flow;
- so prices depend on traders only through aggregate net flow by construction;
- an OLS regression of aggregate flow is the sum of the class regressions, so "prices identify the aggregate response" also holds by linearity.

A registered test of either statement would pass mechanically, and a referee would say so.

## Where an AMM can still test something

**Equilibrium sufficiency on the liquidity side** (Theorems thm:eqinv / n:thm_eqreduced):
- **The theorem:** liquidity providers play the dealers' role. In equilibrium, the impact they set depends on the trading population only through its aggregate feedback response.
- **Prediction:** liquidity depth depends on the arbitrage population only through the aggregate response, meaning how fast the pool–CEX basis closes. Composition should add nothing once that response is controlled for. Composition here means:
  - the concentration of arbitrage volume across bot contracts;
  - the number of active bots;
  - the replacement of a dominant bot.
- **Data:**
  - Uniswap v3 Swap events (`sender`, signed amounts, `sqrtPriceX96`, `liquidity`), plus Mint/Burn events for liquidity, from the Google BigQuery public blockchain datasets;
  - CEX reference prices from the Binance public archive;
  - pool-days or pool-weeks across many pools.
- **Status: bridge (B), not direct.** AMM liquidity providers are passive and bear loss-versus-rebalancing. They are not the CARA inventory dealers of the theorem, so the mapping needs its own argument.
- **Main confounders:** volatility, volume, fee tier, the token pair, builder/searcher integration, gas costs.
- **Size:** weeks. A spec, a power simulation, and a development-period exploration, then one registered run. The authors must approve before registration.

## Recommendation

Do not count on this test for the paper's score in 2026. The direct evidence route is H1 (Hyperliquid). There, prices are formed by a central limit order book, so impact is not mechanical, and accounts carry addresses. H1 opens no earlier than 10 December 2026. The Taiwan measurement (P1M) is the other near-term addition.

Revised ceiling, judgement:

| Route | Level |
|---|---|
| Theory and polishing | about 87 |
| + P1M | 88 |
| + H1 supportive | 89–90 |
| + the liquidity bridge test supportive as well | 91–92, with more uncertainty than stated earlier |
