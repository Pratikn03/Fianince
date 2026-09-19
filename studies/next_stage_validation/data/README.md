# Next-stage data

The synthetic environment generates checkpointable tapes from declared seeds.
The empirical pilot reads the public Binance kline archives under
`research_extension/data/raw/binance/spot/klines/`; it does not copy or mutate
the raw files. No credentials, live orders, or unauthorized data are used.

The current public pilot is OHLCV-only and cannot validate level-2 execution,
queue priority, cancellations, or historical fill probabilities.
