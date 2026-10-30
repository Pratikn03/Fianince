# Machine Markets: advanced cost-aware separation audit

Open `Machine_Markets_Advanced_Research.ipynb` in Google Colab and use **Run all**.
The notebook contains the source; it does not depend on the moving GitHub branch.
Default profile **deep** uses 288 randomly generated cohort economies, 4,096
measurement repetitions per economy and N, three measurement budgets, three
information prices and seven measurement rules plus an oracle. No GPU is
required: NumPy/SciPy CPU workloads use the available CPU allocation. A paid
runtime may supply more CPU/RAM; it cannot establish originality or proof.

## What this can answer

Can a known finite-horizon aggregate response support an inventory-warehousing
decision when latent cohort weights are hard to recover, and is that information
worth purchasing after execution, carry and information costs? The institution
holds a fixed long inventory for H=10,60,240 model minutes and earns an exogenous
service premium AFTER settlement. It is not a crypto trading-profit forecast.
The comparison allows the no-data benchmark the same error budget.

`PROOF.tex` preserves the restricted written theorem from the earlier study.
`EXACT_WITNESS.md` and `proof_audit.py` add seven exact scalar certificates,
checked by pinned Lean 4.19.0 with axiom output. This is **not a Lean proof of
the full theorem or the existing papers**. `ROBUST_CONTRACTS.md` gives the
standard Student-t and median-of-means alternatives and their assumptions.
`LITERATURE.md` identifies established antecedents; novelty remains unconfirmed.

## Run and resume

```bash
python -m pip install -r requirements.txt
python runner.py --out /content/drive/MyDrive/MachineMarkets/advanced_deep --profile deep
```

Use a NEW output directory after changing code, seed, profile, Python/package
versions or other scientific inputs. An unchanged directory resumes only checksum-verified matching case
checkpoints. Worker count can change. Never launch two processes against the
same output directory. Put the Lean cache outside that directory. A local run
supports `--skip-lean` explicitly; this is recorded as NOT_RUN, never as PASS.
The final sibling ZIP contains all results, sufficient statistics, source,
configuration, proof receipts, tests, negative results and a verified manifest.
Download/upload the ZIP even if a stage fails; failure logs are valuable.

## Optional quote data

Set RUN_MARKET=True in Colab and provide an event-level best-quote CSV plus
metadata JSON. See `market_metadata.example.json`. Columns: timestamp (ISO-8601
with timezone), market, bid, ask, bid_size, ask_size. Every row is a complete
best-quote state after an event, already chronologically ordered. Supply units
in the metadata; depth and inventory must be in the same base units. Snapshots,
OHLC candles and spot/perpetual mixes are not acceptable substitutes for events.
Metadata are self-declared and must be independently checked. Real-data files
are NOT embedded into the returned ZIP; their hashes and metadata are retained.
Keep original data for replication and respect redistribution permissions.

The optional module performs purged chronological forecasts against EWMA,
intraday HAR and OFI/depth baselines, followed by a conservative isolated
round-trip exposure replay using quoted spread, fees and carry. Its reduced-form
VAR score is NOT the theoretical impulse response. The replay assumes fills
at recorded quotes up to 10% displayed depth, omits latency/queues and is not a
portfolio backtest or certified solvency rule. Insufficient data stays marked
NOT_ENOUGH_DATA. Without quote data the stage is NOT_RUN.

## Interpretation

This is an exploratory simulator audit following earlier results, not a
preregistered confirmatory study, independent replication or market validation.
Dependent policy/cost rows reuse readings. Seed-cluster intervals describe the
declared simulator design only. Biased observations and future regime changes
are deliberately outside the measurement guarantee; robust intervals do not
repair that failure. Preserve failures, negative information values and
unaffordable purchases. No result assigns a 9+ paper rating.
The fixed-N rules do not optimize whether to buy information before observing
it. Negative net values show why a worthwhile certificate is not automatically
a worthwhile information purchase. Do not select a profitable method after
looking at hidden gains or test outcomes and call that an implementable policy.

Existing manuscripts should retain supported content and mark only pending
results as pending. This package does not replace the papers with an empty
manuscript or automatically insert unreviewed run outputs into them. After the
returned ZIP is reviewed, revise the original manuscripts with traceable
results and an explicit distinction between theorem, simulation and evidence.
