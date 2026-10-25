"""Certify a simulated market whose true margin is known, then watch it on a rolling window.

    python examples/quickstart.py
"""
from margin_monitor import certify, closed_loop, rolling_margin, throttle, warnings

for phi in (0.06, 0.20):                                  # feedback below and above the market's reversion
    bars, true_m = closed_loop(days=40, phi=phi, seed=100)
    c = certify(bars)
    print(f"true margin {true_m:+.3f}   certified {c.margin:+.3f}  95% CI [{c.ci[0]:+.3f}, {c.ci[1]:+.3f}]  -> {c.sign}")

bars, _ = closed_loop(days=5, seed=1)
roll = warnings(rolling_margin(bars, window="24h", step="1h"))
last = roll.iloc[-1]
print(f"rolling: {len(roll)} hourly certificates; latest {last['margin']:+.3f} [{last['lo']:+.3f}, {last['hi']:+.3f}], "
      f"trend warning {bool(last['t2z'])}, admit {throttle(last['lo']):.2f} of algorithmic flow")
