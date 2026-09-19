# Post-primary work and held-out confirmation

The following was chosen AFTER the primary v0.5 results, not preregistered.

## Input design exploration
A four-share single round trip and a preassigned distribution of observation endpoints were investigated in small pilots. The original eight half-share round trips reduced input energy and performed worse. The endpoint-diversification pilot showed potential benefit at rates .02/.1, not .002. No claim of globally optimal design follows.

## Frozen follow-up comparison
Use a four-share initial impulse in both arms. Endpoint arm A: 64 transitions in every episode. Arm B: equal allocations to 8,16,32,64 transitions, with assignments shuffled independently before looking at prices. Average B record length is 30 transitions; maximum 64. Both arms hold four probe shares until their endpoint; flattening AFTER the observation adds four shares of volume (eight total), which is identical across arms but not simulated as part of the measurement law. Source generates 64 points once for paired evaluation; B inference sees ONLY its preassigned prefix.
Twelve models, N=32/128/512, 20 held-out panels per cell, fresh seed range starting 130000000. Each panel is evaluated in both arms, yielding 1,440 decision rows from 720 independent panel datasets. No covariance pooling from multiple rows of the same episode. Report paired switches and exact McNemar tests descriptively with Holm correction across three episode budgets. Statistical success is not required for delivery.

## Binding dealer stress extension
The primary 24 settings had binding participant limits but no dealer halts. This follow-up intentionally tests that branch. In the tight regime, the dealer starts with 19 shares and equity 1,000, matched by -9 shares in the fundamentalist and -10 in the probe account. Cash is adjusted so initial equity is unchanged and shares sum to zero. All six accounts satisfy initial limits. Evaluate gains .7/1.3, rates .02/.1, repricing mean -2/-10 with independent sd=1 at step 16. Eight settings, 8,192 episodes each. These are synthetic stress scenarios, NOT a calibrated market shock distribution or a confirmatory replication of the flat-start setting.

## Negative controls
Audited rates omitted, reset broken, noisy covariates, extra inventory feedback, code/config tampering, and a self-issued false contract. The last demonstrates that source identity alone is not proof of truthful configuration or complete channel coverage.
