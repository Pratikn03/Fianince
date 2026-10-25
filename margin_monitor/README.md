# margin-monitor

Certify whether a market's trading loop is damping shocks or amplifying them, from **public prices and anonymous
signed order flow**, without identifying any trader.

Order flow moves the price, and traders (human or algorithmic) respond to how far the price has moved from its recent
level. In the linear model this package estimates, the market's **stability margin** is

    M = reversion − feedback = −β − κ·Φ

where `−β` is how fast the price displacement reverts, `κ` is price impact per unit of flow and `Φ` is the traders'
total response to the displacement. `M > 0`: shocks die out. `M ≤ 0`: the loop amplifies them. Because `M` depends on
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
print(cert.margin, cert.ci, cert.sign)   # e.g. 0.041 (0.029, 0.054) 'safe'

roll = warnings(rolling_margin(bars, window="24h", step="1h"))
admit = throttle(roll["lo"].iloc[-1])    # share of algorithmic flow to admit, 0..1
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
| `certify` | margin, block-bootstrap interval, reversion, feedback, κ, Φ, and a verdict: `safe` (interval above 0), `unsafe` (below 0) or `undecided` |
| `rolling_margin` | the same on a rolling window, one row per step |
| `warnings` | three rules: `lost` (lower bound ≤ 0), `buffer` (lower bound ≤ buffer), `t2z` (margin falling and projected to reach zero within a horizon) |
| `throttle` | a continuous admission share: 0 at or below a buffer, 1 above a ceiling, linear between |

A 24-hour window of 5-minute bars gives a wide interval (in the quickstart, roughly ±0.1 around the margin), so a
throttle driven by the lower bound is conservative; longer windows trade speed for precision.

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
memory and abrupt switches), which are matters for disclosure rules. Under the continuous `throttle`, the agents' game
has an equilibrium and every strategy profile keeps the margin above the buffer (Proposition `prop:throttle`; the
fixed-point, uniqueness and safety parts are also checked in Lean in the repository).

## Status

Version 0.1.0, research software. The registered empirical tests of the thesis are still running; the README will
report their outcomes as they come in, whichever way they go.

## License

Apache-2.0. Written with AI assistance (Claude), disclosed as in the thesis.
