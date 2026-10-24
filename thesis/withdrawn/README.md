# Withdrawn results (kept for the record; not reported in the thesis)

Withdrawn on 2026-10-24. The thesis states the reasons in Chapter 5, Section "Withdrawn results".

| Files | What was reported | Why it is withdrawn | Replaced by |
|---|---|---|---|
| `E1_pipeline.py`, `E1_results.json`, `E1_numbers.tex` | "Test E1" in 38 markets (8 CFTC, 30 Binance), both primaries passed | Nothing was estimated from fresh data. The script read results archived from earlier tests, hard-coded the CFTC certificate interval, set the class intervals to an invented +/-25% band and the Binance class value to one constant for every symbol, reused Paper 1's width ratios for Primary 2, and printed a Holm p-value it never computed. The design also compared class positions with flow kernels, which are in different units. | Test E1v2, `checks/prereg/E1v2_certify_vs_identify.json`, registered in commit 2c34fc1 before any data were downloaded |
| `check_multiagent.py`, `R_multiagent.json`, `multiagent_numbers.tex` | Simulation B3: realized certificate lifetimes 1.87-1.90 times the bound in 100 of 100 runs | Weight updates were a positive clipped step at every period, so weights could only increase and the "realized lifetime" was fixed by the construction; it could not fall below the bound it was said to test. The thesis table and PROGRESS.md also disagreed about its numbers. | Simulation B3v2, `checks/prereg/multiagent_v2.json`, registered in commit be1a36b and run once in 91c3e11 |

The registration records of the withdrawn runs (`checks/prereg/E1_cert_vs_truth.*`, `checks/prereg/E1_unlock.json`,
`checks/prereg/multiagent.*`, `checks/prereg/multiagent_unlock.json`) stay where they were, unchanged.
