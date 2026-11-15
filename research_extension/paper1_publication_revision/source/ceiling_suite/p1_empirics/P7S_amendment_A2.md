# P7S amendment A2: descriptive split of the prospective replication by underlying asset

Registered 12 November 2026, before the replication's evaluation window opens (16 November 2026). Approved by the
author in this session ("Keep, add split"). Drafted by an AI system; not independent review.

## 1. Why

The replication's development stage (run once, `results/p7s_rep_dev_printed_output.txt`) drew its universe of 30
by the registered A1 rule. Twelve of the 30 are perpetuals on non-crypto underlyings, a kind of contract that did
not exist in the primary sample's universe:

SNDKUSDT, XAUUSDT, SOXLUSDT, SKHYNIXUSDT, SPCXUSDT, CLUSDT, XAGUSDT, KORUUSDT, MUUSDT, BZUSDT, CRCLUSDT, MSTRUSDT.

The underlying of each trades mostly outside Binance, on venues with their own hours and participants, so the
replication could differ from the primary test for that reason alone. Readers should be able to see this.

## 2. What changes and what does not

- **Unchanged:** the A1 universe rule, thresholds, statistics, decision rule and readout. The replication's verdict
  is the A1 verdict on all 30 symbols. The development outputs are those already produced (SHA-256
  `f8a453ca1a196c6f18cc60df6f2cf85b505531fdbb9462b637266216855f8587`).
- **Added, descriptive only:** after the A1 evaluation of the replication, `p7s_split_A2.py` computes the A1
  primary statistic separately for the 18 crypto symbols and the 12 non-crypto symbols: the calm difference with
  its 90% and 95% intervals, the stress difference, the difference-in-differences with its 95% interval and the
  shift-test p-value. A group with fewer than 5 symbols having 20 events in every cell is reported as too small.
- **No verdict per group.** The split is reported in a table next to the A1 readout, with the sentence: "By
  underlying (descriptive, amendment A2): crypto [numbers]; non-crypto [numbers]." No other wording about the split
  is added unless it only states numbers from the results file.
- The split runs in the same notebook session as the replication evaluation, after it, on the same downloaded
  files. It is not run otherwise and it does not count as a separate unlock.

## 3. Classification rule

Non-crypto: a perpetual whose underlying is an equity, an exchange-traded fund or a commodity, including equities of
crypto-related firms (CRCLUSDT, MSTRUSDT). Everything else in the universe is crypto. The list in section 1 is
final; it was fixed from the universe's names before any replication evaluation data existed.

## 4. Files

`p7s_split_A2.py` (the split), `test_p7s_split_A2.py` (checks that the groups partition the registered universe
and that the split equals a direct computation on simulated markets). Hashes in `P7S_SHA256SUMS`.
