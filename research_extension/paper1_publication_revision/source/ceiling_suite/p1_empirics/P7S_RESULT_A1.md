# P7S amendment A1: result of the single registered run (11 November 2026)

**Registered verdict: inconclusive.**

Readout (fixed text, amendment A1 section 6):

> A pre-specified test on Binance perpetual futures was inconclusive (calm difference -0.002, 90% interval [-0.007, 0.004]; difference-in-differences 0.041, p = 0.553). It neither supports nor contradicts the prediction of Section 7.

| Quantity | Value |
|---|---|
| Window | 2024-07-01 to 2026-10-28, 850 days, 30 symbols, all used |
| Events | calm high 833,636; calm low 387,589; stress high 18,505; stress low 16,074 |
| Calm difference (sd units) | -0.0018, 90% interval [-0.0070, 0.0044], bootstrap SE 0.0036 |
| H1, calm silence (interval inside ±0.10) | passed |
| Stress difference | 0.0395 |
| Difference-in-differences | 0.0412, bootstrap 95% interval [-0.0702, 0.1572] |
| H2, time-shift test (169 shifts of 5 days) | p = 0.5529; not passed |
| Share of symbols with a positive stress difference | 0.633 |

Sensitivity checks (descriptive; none enters the verdict):

| Check | Calm difference | DiD | Shift-test p | Symbols |
|---|---|---|---|---|
| rv | -0.0010 | 0.0785 | 0.1294 | 30 |
| top | -0.0026 | -0.0275 | 0.6647 | 28 |
| volume_high | -0.0107 | 0.0646 | 0.4294 | 30 |
| volume_low | 0.0049 | -0.2253 | 0.3588 | 2 |
| volume_mid | -0.0117 | 0.0558 | 0.6176 | 12 |

DiD with the state lagged 30 days: 0.0604; led 30 days: 0.0206.

**Integrity record.**
- Code SHA-256 as registered (executor 7718ba33f554, data 7e6e963acebe, pipeline 5a85f51de705).
- The development outputs were regenerated in the evaluation session (the registered file was lost) and matched the
  printed record of the registered development run, as section 11 requires; otherwise the notebook would have
  stopped. The regenerated file's fingerprint is `11d171abd33f…`, not the registered `7330ef3d…`,
  because the file also contains its run time and download counts.
- Format gate: 58 of 58 sampled files passed.
- Run once. The result is reported as it came out.

**What it means.** Calm moves were silent in the sense registered: the calm response did not depend on proximity
to the open-interest maximum, and the interval is far inside the margin. Stress moves did not show a detectable
dependence either. The test therefore does not provide the two-layer pattern. With an interval of ±0.007 the calm
result is precise, but a calm null is also what a world without position-limit effects predicts, so H1 alone is
not evidence for Section 7. Simulation suggested power near 1 for the simulated effect size at this window length;
the real effect, if any, is smaller than that or the open-interest proxy does not track position limits.
