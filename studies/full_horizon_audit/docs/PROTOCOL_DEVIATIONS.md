# Execution notes and deviations

The internal protocol was written before primary v2 outcomes were inspected. This is not an external preregistration or a held-out replication.

- The original input NPZ was cached once during regeneration. Repeated compressed-file lookup was unnecessarily slow. This did not change any random seed, measurement, or result; all prior saved inputs match exactly.
- The first separate interior-point verification command reached a 90-second command timeout before producing its final artifact. It was rerun with incremental checkpointing and a five-second per-LP limit. All 216 predetermined datasets then completed; no case was excluded. The timeout is a process limitation, not a reported experimental failure or a selected subset.
- The sensitivity grids and repetitions remained exactly as declared. Neither primary grid resolution nor error allocation was retuned after examining labels.
- The new Gaussian fixed-order analysis was developed alongside the primary execution. It is a mathematical follow-on analysis, not a preregistered empirical discovery. Its grid is independent of the primary estimator comparison and is not used for method selection.
- Timing values are environment-dependent and are excluded from exact reproduction comparisons. All result labels, bounds, residual audits and other non-timing fields are compared.
- No external reviewer, autonomous external agent, private repository, paid data source or API-based trading agent was used. The original archive remains unchanged.
