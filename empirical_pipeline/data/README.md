# Data Provenance and Integrity Documentation

This directory contains public crypto order book datasets used in the empirical analysis of market-order feedback and stability boundaries.

## 1. High-Frequency Order Book Snapshots (April 2021)

* **Source**: Martin Søgaard Nielsen, *"High Frequency Crypto Limit Order Book Data"*, Kaggle Dataset 1567989 (v1, modified 2021-09-02).
  * URL: <https://www.kaggle.com/datasets/martinsn/high-frequency-crypto-limit-order-book-data>
  * License: CC0: Public Domain
* **Collector Architecture**: Collected from the **Coinbase Pro WebSocket** feed using Sadighian's open-source recorder `crypto-rl` (<https://github.com/sadighian/crypto-rl>).
* **Coverage**: 2021-04-07 11:32 UTC through 2021-04-19 09:54 UTC (~11.9 days).
* **Assets**:
  * `BTC-USD` (Bitcoin / USD)
  * `ETH-USD` (Ethereum / USD)
  * `ADA-USD` (Cardano / USD)
* **Sampling Frequencies**:
  * 1-second: `BTC_1sec.csv`, `ETH_1sec.csv`, `ADA_1sec.csv` (~1,030,700 rows each)
  * 1-minute: `BTC_1min.csv`, `ETH_1min.csv`, `ADA_1min.csv` (~17,110 rows each)
  * 5-minute: `BTC_5min.csv`, `ETH_5min.csv`, `ADA_5min.csv` (~3,368 rows each)

### Timing and Variable Conventions
* **Timestamp**: `system_time` is recorded in UTC with microsecond resolution. Snapshots are emitted approximately once per second.
* **Midpoint & Spread**: `midpoint` is $(P_{\text{best ask}} + P_{\text{best bid}})/2$. `spread` is $P_{\text{best ask}} - P_{\text{best bid}}$.
* **Order Flow (`buys`, `sells`)**:
  * Taker buy and sell volumes measured in **quote currency notional** (USD), aggregated by `crypto-rl`'s `trade_tracker` over the interval $(T-1, T]$.
* **Duplicated Render Correction**:
  * In `crypto-rl`, when no websocket tick is received in an elapsed second, the previous book snapshot is re-emitted with its previous `buys` and `sells` values intact.
  * Without correcting for duplicated renders, cumulative volume is inflated by 2.5% to 7.0%.
  * Setting flow to zero on duplicated consecutive rows restores exact interval closure: the sum of 1-second flows over $(T-60, T]$ matches the dataset's own 1-minute buys/sells exactly ($100\%$ match across all verified minutes, median relative difference $< 4 \times 10^{-13}$; see `results/provenance/timing_check.json`).

---

## 2. January 2023 Order Book Dataset (`1-09-1-20.csv`)

* **File**: `1-09-1-20.csv` (1.20 GB, 3,730,871 lines).
* **Coverage**: 2023-01-09 22:17:28 UTC to 2023-01-20 18:10:04 UTC (~10.8 days).
* **Instrument**: Bitcoin perpetual / USDT (`BTCUSDT`).
  * Price tick size: 0.1 USDT.
  * Size step: 0.001 BTC.
  * Format and decimal conventions match the Binance USDⓈ-M perpetual futures book stream.
* **Schema**:
  * Column 0: Row index
  * Column 1: Epoch timestamp in milliseconds
  * Column 2: Formatted UTC timestamp string (`YYYY-MM-DD HH:MM:SS.mmm`)
  * Columns 3–22: 10 levels of bid prices and quantities (`bid_price_0`, `bid_qty_0`, ..., `bid_price_9`, `bid_qty_9`)
  * Columns 23–42: 10 levels of ask prices and quantities (`ask_price_0`, `ask_qty_0`, ..., `ask_price_9`, `ask_qty_9`)
* **Trade Flow**: This file records limit order book depth only, without executed market order flow. Flow is aligned from Binance public `aggTrades` archives for the corresponding dates.

---

## 3. Reference Benchmark Data

* `LOBSTER_SampleFile_AMZN_2012-06-21_10.zip`: Standard LOBSTER public sample benchmark for Amazon (AMZN) on 2012-06-21 (10 levels of message book and order book), used for parser and benchmark calibration.

---

## 4. SHA-256 Integrity Checksums and Line Counts

| Filename | Line Count | SHA-256 Checksum |
| :--- | :--- | :--- |
| `1-09-1-20.csv` | 3,730,871 | `5d3f14a2d252a884e3c9b81a6f3767c7161296ecc8fdd1280c7d46a1cea19847` |
| `BTC_1sec.csv` | 1,030,729 | `a6b46071b1804e6181a1fb3eca9df70c13afa58195f18cb469d9682b86a0c85b` |
| `ETH_1sec.csv` | 1,030,776 | `908f10a56bb265a56d9c913ab72ad363c8016aa81870eb467c4807885f17dcac` |
| `ADA_1sec.csv` | 1,030,534 | `ec8fbc1925f14c589f717f3cf497584ad56384e0daeba34c541c33f583c998aa` |
| `BTC_1min.csv` | 17,114 | `1a4bf5d19f0f9b41f93a7fadacb44f015f8f7eb3212995b77bd70182d99afa93` |
| `ETH_1min.csv` | 17,111 | `c2a26ac19017b7d205e1f4a51adfc68112f9509e11f9f65130844bf1fe33fe83` |
| `ADA_1min.csv` | 17,110 | `d1126b9d06a7eb1a452016c2c634f04afd5017f78ed70f3ff7b0135df81d36b3` |
| `BTC_5min.csv` | 3,368 | `095ee45ed97240a12e64cb2e038e04eef537da520851b1be4f05e1eee91395b9` |
| `ETH_5min.csv` | 3,366 | `d63af34f75e7e5c54d3800f28e24ef2148b51640dd607454352246a3b2a81476` |
| `ADA_5min.csv` | 3,368 | `ce416ff1fbe627a7397ce1f222ec61e162aaec8d25a27c3e738fd9676f0bbb1c` |
| `LOBSTER_SampleFile_AMZN_2012-06-21_10.zip` | — | `3967668ba6d7b3ed9bc3a4173555252ac38bcdcbfbebea2fab8c1bd2a18a63cb` |
