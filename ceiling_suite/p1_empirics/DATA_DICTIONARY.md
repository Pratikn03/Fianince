# Data dictionary from the schema probe (Phase 2), 7 November 2026

**Run.** The author ran the probe in Colab on 2026-11-07 at 06:37 UTC. Result file:
`schema_probe_results.zip`. The SHA-256 of each raw response is listed in the zip's `log.json`.

**What was examined.** Only the layout and the internal accounting identities. No outcome was computed.

**Burned days.** The days below are now burned and are excluded from every confirmatory sample.
- TWSE: 2024-01-02 and 2024-01-03.
- TPEx: 2024-01-02 and 2024-01-03.
- NSE: 2024-01-02.

**JPX.** No file was fetched. The index page links only to the five most recent weekly files (2026-09-28 to
2026-10-30), so the 2024 file is not reachable from that page. The JPX burn was declared but not used.

## TWSE, report T86: three major institutional investors, per security, daily

| Item | Finding |
|---|---|
| Request | `https://www.twse.com.tw/rwd/zh/fund/T86?date=YYYYMMDD&selectType=ALLBUT0999&response=json` |
| Response | `stat`, `date`, `title`, `fields` (19), `data` (rows), `notes`. The unit hint is `單位：股` (shares). |
| Rows | 1,178 on 2024-01-02; 1,184 on 2024-01-03. The universe changes by day, so missing and zero must be distinguished (see open item 1). |
| Identifier | `證券代號`. 996 rows are four-digit common-stock codes. The rest are ETFs, including leveraged and inverse ones with suffixes L and R. Foreign-currency ETFs carry K, M, S or C in the sixth position. |
| Classes | Foreign and mainland investors (excluding foreign dealers); foreign dealers; investment trusts (domestic funds); dealers' own-account trading; dealers' hedging trades. |
| Variables | For each class: buy shares, sell shares, net shares. Also the dealer total and the total for the three institutions. |
| Coverage | Includes regular, odd-lot, after-hours fixed-price and block trades. Excludes auctions and tenders. Counted from original executions, not from error-corrected accounts. |
| Identities | All hold on both days for every row: buy − sell = net for each class, dealer own + dealer hedge = dealer total, and the three-institution total equals the sum of its parts. |
| Prices | Not in this report. They need a separate daily price source (for example TWSE `STOCK_DAY`), still to be probed. |

## TPEx, three major institutional investors, per security, daily

| Item | Finding |
|---|---|
| Request | `https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&o=json&se=EW&t=D&d=113/MM/DD` (ROC year) |
| Rows | 790 on 2024-01-02; 795 on 2024-01-03. No duplicate codes. |
| Layout | 24 fields with repeated headers. Column groups were identified from the identities, all of which hold for every row: [2–4] foreign excluding foreign dealers; [5–7] foreign dealers; [8–10] foreign total; [11–13] investment trusts; [14–16] dealer own account; [17–19] dealer hedging; [20–22] dealer total; [23] three-institution total. |
| Coverage | Common stocks, block, odd-lot and omnibus-account trust volume, per the subtitle. |

## NSE, participant-wise F&O trading volume, daily

| Item | Finding |
|---|---|
| File | `archives.nseindia.com/content/nsccl/fao_participant_vol_DDMMYYYY.csv`, 5 rows: Client, DII, FII, Pro, Total |
| Variables | Long and short contracts traded by category: index futures, stock futures, index and stock call and put options. |
| Limitation | Market-wide aggregates by product type, with no instrument identifier. Header strings contain stray tabs. |

## Decision for each source

- **TWSE and TPEx: candidate for a direct test, conditional on two bridges.**
  - They give daily signed net executed flow by investor class for each security, in shares.
  - Market clearing makes the residual class implied: domestic individuals plus other domestic institutions have
    net flow equal to minus the three-institution total. The classes therefore cover the whole market.
  - This is much closer to Proposition 6.1's tagged flow u_{i,t} than COT positions or Binance top-trader ratios.
  - Bridges still required before the test counts as direct:
    - one day being the model's period, and net shares (or net value) being the flow variable;
    - a reference price p*_t for the pricing error x_t.
- **NSE: proxy only.** There is no instrument identifier, and net contracts are mixed across products.
- **JPX: proxy only.** It is market-wide and weekly. It could support at most an aggregate index-level analysis.
- **KRX: not probed.** The download needs a session. It would be the replication venue.

## Open items before a test specification

1. **Missing versus zero.** Does a security absent from a day's file have zero institutional flow, or was it
   suspended or not trading? Check against the daily trading list.
2. **Units.** Shares versus value. Should flow be scaled by shares outstanding or by turnover across securities?
3. **Mechanical flows.** Dealer hedging flow is tied to warrant and derivative books, so it is a mechanical
   response, not a learning rule. Should it be excluded from the classes or kept as its own class?
4. **Universe.** Exclude ETFs, leveraged and inverse ETFs, foreign-currency ETFs, new listings, and corporate-event
   days.
5. **Prices.** Probe the daily price source, adjustments and limit-up/limit-down days. Taiwan's ±10% price limit
   truncates returns.
6. **Reference price.** Choose p*_t with no future data. For example, use the market index return as a factor, or
   define x_t as an index-relative pricing error, labelled honestly as a market-reference basis.
7. **Split the history** into development, validation and holdout periods before computing any statistic. Size them
   with a simulation power analysis.

## Probe 2 (7 November 2026, 06:46 UTC; `schema_probe/schema_probe2_results.zip`)

### Burn record correction

The TPEx quote endpoint ignored the requested date and returned the full quote table for **2026-11-06**
(`115/11/06`, 13,618 rows). Both requests returned that same file (identical SHA-256). No statistic was computed
from it.

The following are added to the burned set and excluded from every confirmatory sample:
- TPEx daily quotes for 2026-11-06;
- the TPEx sample as a whole for that day.

The TPEx quote request still needs a working date parameter before TPEx can serve as the replication universe.

### TWSE `MI_INDEX` (all securities, daily)

| Item | Finding |
|---|---|
| Quote table | `每日收盤行情(全部(不含權證、牛熊證、可展延牛熊證))`, 1,222 rows on 2024-01-02. Fields: code, name, volume (shares), trades, value, open, high, low, close, change sign, change, last bid and ask with sizes, P/E. |
| Change sign | Given as HTML. `+`, `-` or **`X`**; the notes say `X` means "not compared" (不比價). That flag marks ex-rights/ex-dividend and other reference-price resets directly. |
| Index tables | Price indices (TWSE, cross-market, TIP) and **total-return indices**. TAIEX and its return index are in the same response. |
| Coverage | Includes regular, odd-lot, after-hours fixed-price and block trades. Excludes auctions and tenders. This matches T86. |

### Missing versus zero (item 1): resolved on the burned days

| Date | Four-digit stocks in quotes | Traded | Traded but absent from T86 | Median volume, all traded | Median volume, absent | In T86 but not traded |
|---|---|---|---|---|---|---|
| 2024-01-02 | 1,009 | 1,009 | 13 | 431,400 | 26,123 | 0 |
| 2024-01-03 | 1,009 | 1,008 | 12 | 498,337 | 15,020 | 0 |

- T86 omits only traded stocks with very low volume, and it never lists an untraded stock.
- The rule "traded but absent means zero institutional flow" is therefore consistent with the data on these days.
- These stocks fall far below the top-300 turnover filter in any case.
- One stock did not trade on 2024-01-03; it is treated as missing for that day.

### Ex-rights table `TWT49U`

It returned "no matching data" for 2024-01-02 to 2024-01-03. Two explanations remain open: no events in those two
days, or a wrong query. The `X` change-sign flag in `MI_INDEX` gives an independent event marker. The spec will use
both and report disagreements.
