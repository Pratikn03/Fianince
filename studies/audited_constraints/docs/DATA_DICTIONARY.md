# Data dictionary

- `linear_terminal_rows.npz`: concatenated X, y and offsets for 2,880 independent panels. X columns are intercept, final pre-terminal price, reconstructed fast memory, reconstructed slow memory. Units: prices dollars; no truth parameters in X. `linear_panels.csv` carries design and post-estimation truth fields; inference receives no CSV truth fields.
- `linear_public_<model>_<design>.npz`: exact observed prices, requested/filled unbounded-model probes, disclosed rates and seed; selected 128-episode, 64-step examples.
- `endpoint_terminal_rows.npz`: terminal rows for 1,440 decision records (720 paired datasets). Do not count both arms as new episode draws.
- `endpoint_public_<model>.npz`: raw prices and preassigned endpoint schedule. Diversified inference ignores prices after each assigned endpoint.
- `measured_tail.csv`: tail horizon H=64, joint gain/tail analysis with error split .025/.025 on reused primary rows. `model_conflict` is true for an empty intersection; do not discard those rows.
- `finance_episodes_<setting>.npz`: one scalar/vector of length 20,480 for event, default, halt, margin, clipping, maximum adaptive-trader drawdown fraction, maximum price displacement dollars, gross filled volume shares, filled probe volume shares, peak marked leverage, liquidation count and rejected volume. Settings in financial_settings.csv. Exogenous tapes are paired across funding regimes.
- `finance_ledger_example_<setting>.npz`: ledger has axes time, episode, variable, account. Variables cash, inventory, post-price-update equity. Six accounts: fast-memory trader, slow-memory trader, fundamentalist, background, probe, dealer. Prices are deviations from 100 dollars. Total shares zero; initial total cash depends on funding setting.
- `dealer_stress_<setting>.npz`: 8,192 episodes per post-primary preloaded-dealer setting; same outcome units. Starting positions sum to zero; source records initial cash adjustments.
- `financial_budget_panels.csv`: forty blocks of 512 outcomes per setting; nested n=32,128,512. Exact interval error per look .05/3; threshold .05. These are finite-horizon event decisions, not stability labels.
- `finance_checkpoints/`: restart records for each primary setting; source hash included. They cache completed computation and are not independent data.
- `assumption_controls.csv`: intentionally invalid ungated inference. Full-system spectral radius is used only for evaluation, especially for omitted inventory feedback.
- `binomial_exact_coverage.csv`: exact binomial coverage enumeration on 1,001 p-grid values for each planned budget; not market simulation episodes.
- `standalone_verification.json`: internal alternate-code checks. `outside_replication=false` is intentional.
