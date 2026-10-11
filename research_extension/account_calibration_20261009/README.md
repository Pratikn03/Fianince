# Public contract calibration and account reconciliation

The user delegated the target choice. The selected target is the paper's provider-declared Binance BTCUSDT USD-M perpetual, January9-20,2023. It is not an authenticated personal account. Existing snapshot data and simulated execution ledgers do not supply original exchange wallet/position statements.

Three official Binance archives were retrieved with their official SHA256 CHECKSUM files. Full archive hashes and ZIP CRCs pass. The mark and index archives each contain44,640 monthly minute bars, including17,280 continuous, unique, OHLC-valid bars during the12 selected dates. The funding archive contains36 selected settlements,34 positive and2 negative, with an observed8-hour interval. Archive millisecond settlement jitter is retained.

For a declared1BTC position entering at January9 00:01UTC and remaining through January20,35 settlements give a reference long cost of68.2378305368269295USDT and the opposite short cash flow. Summing the minute-mark OHLC ranges gives68.2062061540229377-68.2656837231663798USDT. This range brackets prices recorded within those minutes; it is not an authenticated account settlement amount. No historical fee/margin tier is inferred from current documentation.

The existing15,593 selected book midpoints are compared with same-minute closing mark/index prices, retaining the large tails. This is a retrospective clock/price comparison, not proof of exchange identity or independent measurement noise. Fees0.02%/0.04%, maintenance rates0.5%/1%/2.5%/5% and initial leverage2/5/10/20 are declared sensitivity inputs. The64 resulting wallet envelopes are independently recomputed with decimal arithmetic. They are not continuous-time liquidation guarantees or recommended trading settings.

## Account contract

For a single-asset linear perpetual, wallet changes follow realized P&L minus commission plus signed funding and transfers. Opening notional is not a principal cash debit. Equity is wallet plus unrealized P&L. This differs from the manuscript's physically settled counterparty account. The price sample cannot validate that principal-fill contract as an actual perpetual account.

`reconcile_linear_perpetual.py` accepts chronological normalized fills, funding, transfers and account snapshots. It checks wallet, signed position, weighted-average entry, realized P&L and marked equity; it retains discrepancies and negative margin headroom. Non-USDT fees require an authenticated conversion, and absent snapshots are not replaced with zeros. Historical margin tiers, collateral mode, liquidation rules and source authentication remain separate requirements. Its7 tests use hand-computed synthetic accounts with partial closes, reversals, fees, nonzero opening positions and missing-record failures. Passing these tests does not validate a private account.

## Reproduce

Use the bundled Python runtime in this desktop workspace. From this directory:

```sh
python3 acquire_public_account_inputs.py
python3 calibrate_public_funding.py
python3 verify_public_funding.py
python3 -m unittest -v test_perpetual_reconciliation.py
```

Raw archives are on T9. The existing selected-book NPZ is read with `allow_pickle=False` and only numeric members are accessed. Receipts bind the scripts, archive hashes and calculated JSON outputs. No private histories or account credentials are published.

## Primary references and remaining records

- [Binance public data and checksum convention](https://github.com/binance/binance-public-data)
- [Official funding-rate explanation](https://www.binance.com/en/support/faq/detail/360033525031)
- [USD-M account API: wallet, unrealized P&L, signed commission and leverage brackets](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account)
- [USD-M public market API: funding and marks](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data)

The documentation was checked October9,2026. Current examples are not historical2023 account-tier evidence. Actual closure requires original trades/commissions, funding cash flows, transfers, position/entry and wallet/equity snapshots, collateral mode and dated margin/liquidation rules. No authenticated private account export was available for the current reconciliation.
