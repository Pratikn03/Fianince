"""margin-monitor: certify a market's stability margin from public prices and anonymous order flow.

    from margin_monitor import bars_from_trades, certify, rolling_margin, warnings, throttle
"""
from .core import (Certificate, add_displacement, bars_from_klines, bars_from_trades, certify, rolling_margin,
                   throttle, warnings)
from .simulate import closed_loop

__version__ = "0.1.0"
__all__ = ["Certificate", "add_displacement", "bars_from_klines", "bars_from_trades", "certify", "rolling_margin",
           "throttle", "warnings", "closed_loop"]
