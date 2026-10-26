# margin-monitor

Estimate a market feedback margin from **public prices and anonymous signed order flow**, without identifying any trader. The result is a model-dependent statistical diagnostic.

Order flow moves the price, and traders (human or algorithmic) respond to how far the price has moved from its recent
level. In the linear model this package estimates, the market's **stability margin** is

    M = reversion − feedback = −β − κ·Φ

where `−β` is how fast the price displacement reverts, `κ` is price impact per unit of flow and `Φ` is the traders'
total response to the displacement. Within the thesis's positive/dominant-root model class, the sign of `M` determines stability. A positive `M` alone does not rule out explosive negative or complex roots. This package does not verify that model class. Because `M` depends on
the traders only through their *total* feedback, it can be certified from aggregate flow; nobody's identity, account
or strategy is needed.

The method comes from the thesis *From Human Markets to Machine Markets* (Niroula, Minnesota State University,
Mankato, 2026), which proves the certification result and its limits.

## Install and use

```bash
pip install ./margin_monitor            # from this repository; needs numpy and pandas only
```

```python
from margin_monitor import bars_from_trades, certify, rolling_margin, warnings, throttle

bars = bars_from_trades(trades)          # columns time, price, size, side (+1/-1 or 'B'/'S')
cert = certify(bars)                     # full-sample certificate with a day-block bootstrap interval
print(cert.margin, cert.ci, cert.sign)   # e.g. 0.041 (0.029, 0.054) 'positive'

roll = warnings(rolling_margin(bars, window="24h", step="1h"))
response = throttle(roll["lo"].iloc[-1]) # response signal only; not a guaranteed controller
```

Candles that report taker-buy volume (e.g. Binance klines) work too: `bars_from_klines`. From the shell:

```bash
margin-monitor trades.csv --format trades --out rolling.csv
```

`examples/quickstart.py` runs on a simulated market whose true margin is known; `examples/binance_klines.py` runs on
Binance's public kline files.

## What it outputs

| function | output |
|---|---|
| `certify` | margin, block-bootstrap interval, reversion, feedback, κ, Φ, and a margin sign: `positive` (interval above 0), `negative` (below 0) or `undecided`; `stability_conditions_verified` is false |
| `rolling_margin` | the same on a rolling window, one row per step |
| `warnings` | three rules: `lost` (lower bound ≤ 0), `buffer` (lower bound ≤ buffer), `t2z` (margin falling and projected to reach zero within a horizon) |
| `throttle` | evaluate the response function g(m); missing/nonfinite margin gives zero |
| `equilibrium_throttle` | solve the implicit static positive-loop admission equation from supplied coefficient bounds |

A 24-hour window of 5-minute bars gives a wide interval (in the quickstart, roughly ±0.1 around the margin), so a
response driven by the lower bound may be small; longer windows trade speed for precision. Bootstrap intervals are not finite-sample guarantees under arbitrary dependence or nonstationarity.

## Checked against known truth

On simulated closed-loop markets with a known margin (`margin_monitor.simulate.closed_loop`, 20 seeds each), the
certificate's mean error was −0.001 (40 days of 5-minute bars, sd 0.008; 160 days, sd 0.004), and the 95% interval
covered the true margin in 19/20 and 18/20 runs. The tests in `tests/` check recovery on a safe and an unsafe market, that
noise added to the flow does not bias the estimate, the bar builders, gap handling and the throttle.

## What it cannot see (read this before relying on it)

* **Slow memory.** The estimator sees feedback that responds within `lags` bars (default 12 bars = 1 hour). Feedback
  that responds over much longer horizons is invisible to *any* finite record of prices and flow; this is a theorem
  in the thesis, not a tuning issue. A strategy with slow memory can make the certificate look safer than the market
  is. Choose `lags` to cover the horizon you care about and disclose it.
* **Abrupt switches.** The certificate describes the window it was estimated on. A loop that changes faster than the
  window will be reported late; the rolling certificate and the trend rule shorten, but do not remove, that delay.
* **Linear model.** It measures the linear part of the loop around normal conditions. It is a diagnostic of how close
  the loop is to amplifying, not a forecast of crashes.
* **Flow sign.** Trade-level aggressor side or taker-buy volume is required; flow signed by a tick rule is noisier.

## Can traders game it?

Not cheaply, within the memory bound. The thesis shows (Theorem `thm:nogaming`) that flow injected independently of
the past adds noise but no bias, and that moving the certificate within the memory bound requires actually moving the
margin, i.e. changing behaviour in the direction the supervisor wants. What remains are the two limits above (slow
memory and abrupt switches), which are matters for disclosure rules. The proposition concerns the implicit equation `alpha = g(reversion - alpha * feedback)`. Calling `throttle` on an earlier margin does not solve that equation or guarantee its buffer.

For a static positive-feedback loop, `equilibrium_throttle(reversion_lower, feedback_upper)` solves the equation using simultaneous bounds for the proposed loop. For example, bounds 0.1 and 0.09 give admission about 0.470588 and admitted margin at least 0.057647. Feeding the previous margin 0.1 directly to `throttle` would admit everything and can leave margin 0.01 below the 0.02 buffer. The solver does not estimate these bounds or establish safety for signed feedback, hidden memory, changing strategies or delayed control.

## Status

Version 0.2.0, research software. The `sign` values changed from `safe`/`unsafe` to `positive`/`negative` to distinguish margin estimation from stability verification. Completed thesis studies have mixed results: the margin is often decided while memories are unidentified, but the public-data guard did not outperform a volatility limit in G1, and several risk forecasts failed. Prospective studies remain pending; see `thesis/READINESS.md`.

## License

Apache-2.0. Written with AI assistance (Claude), disclosed as in the thesis.
