"""Information contracts governing estimation, inference, and claims in Machine Markets.

Separates three strictly distinct information regimes:
- Contract I0: Controlled public-response experiment
- Contract I1: Audited architecture
- Contract I2: Real observational market records
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any


class InformationContractType(str, Enum):
    I0 = "I0_controlled_public_response"
    I1 = "I1_audited_architecture"
    I2 = "I2_real_observational_records"


@dataclass(frozen=True)
class InformationContract:
    contract_type: InformationContractType
    description: str
    observables: List[str]
    maintained_assumptions: List[str]
    forbidden_assumptions: List[str]
    permitted_claims: List[str]


CONTRACT_I0 = InformationContract(
    contract_type=InformationContractType.I0,
    description="Controlled public-response experiment via randomized probing.",
    observables=[
        "Exogenous probe orders u_t (randomized pulse magnitude)",
        "Observed execution prices Y_{r, j}",
        "Quoted best bid and ask (where recorded)",
        "Assumed valid minimum memory decay rate floor eta_0 > 0",
    ],
    maintained_assumptions=[
        "Probes u_t are strictly exogenous (uncorrelated with market innovations)",
        "Rate floor eta_0 is strictly valid (no latent decay slower than eta_0)",
        "Episodes are independent and identically distributed",
        "Sign-positive market price-formation model",
    ],
    forbidden_assumptions=[
        "Known internal agent memory states y_t",
        "Known individual learning rates eta_k",
        "Verified system memory reset to zero between episodes",
        "Known complete inventory of participating algorithmic channels",
        "Single-rate memory decay without empirical justification",
    ],
    permitted_claims=[
        "Estimated closed-loop impulse response band [beta_j^-, beta_j^+]",
        "Observable LP outer stability interval [S_-, S_+]",
        "Abstention when confidence set spans S = 1",
        "Non-identifiability of latent internal states and individual learning rates",
    ]
)


CONTRACT_I1 = InformationContract(
    contract_type=InformationContractType.I1,
    description="Audited architecture with verified runtime disclosures and resets.",
    observables=[
        "Exact price records x_t",
        "Disclosed and audited learning rates eta = (eta_1, ..., eta_n)",
        "Verified system memory reset y_0 = 0",
        "Exhaustive channel inventory (no omitted feedback loops)",
        "Direct observation of terminal innovation residuals",
    ],
    maintained_assumptions=[
        "Truthful architectural disclosure by algorithmic operators",
        "Verified zero reset at start of each estimation window",
        "No unmonitored shadow learning loops or exogenous feedback channels",
        "Spherical Gaussian innovations for classical OLS pivots",
    ],
    forbidden_assumptions=[
        "Automatic operational solvency or bounded drawdown under capital constraints",
        "Extrapolation of linear stability certificates beyond margin/balance-sheet limits",
        "Invariance of architecture under extreme market stress",
    ],
    permitted_claims=[
        "Audited terminal-row regression stability intervals",
        "Calibrated parameter coverage under Gaussian innovations",
        "Decoupling of signal stability (S < 1) from dealer solvency and halt rates",
        "Channel-specific group identification when measurement map U has full rank",
    ]
)


CONTRACT_I2 = InformationContract(
    contract_type=InformationContractType.I2,
    description="Real observational records from live cryptocurrency exchanges.",
    observables=[
        "Limit order book depth snapshots (best bids, asks, depth quantities)",
        "Tick-by-tick public trade executions with maker/taker flags",
        "Consecutive 1-minute candle bars (open, high, low, close, volume)",
    ],
    maintained_assumptions=[
        "Standard exchange matching engine rules",
        "Strict temporal ordering of observations",
        "Non-circular temporal split between estimation (Period A) and evaluation (Period B)",
    ],
    forbidden_assumptions=[
        "Exogenous order flow (passive flow is endogenous to quote placement)",
        "Verified memory reset to zero in live trading",
        "Complete-state observation (true number and nature of trading algorithms is unknown)",
        "Identification of human vs AI participant attribution from price/flow alone",
        "Treating historical order-book spread as identical to live snapshot spread",
        "Treating empirical persistence proxy F as structural system stability S",
        "Claiming cross-exchange venue effects from incompatible estimators",
    ],
    permitted_claims=[
        "Empirical out-of-sample return persistence prediction",
        "Comparison of reduced-form proxy F vs baseline AR(1) autocorrelation",
        "Assessment of numerical optimization dispersion across seeds",
        "Microstructure-consistent signed trade flow conversion",
    ]
)


def get_contract(contract_type: InformationContractType) -> InformationContract:
    if contract_type == InformationContractType.I0:
        return CONTRACT_I0
    elif contract_type == InformationContractType.I1:
        return CONTRACT_I1
    elif contract_type == InformationContractType.I2:
        return CONTRACT_I2
    raise ValueError(f"Unknown contract type: {contract_type}")
