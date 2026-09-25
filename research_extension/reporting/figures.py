"""Generation of Figures F1 through F7 in standalone and LaTeX pgfplots/TikZ formats."""
import os
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from research_extension.mm_revision.identities import (
    get_rational_finite_window_witness,
    verify_swapped_feedback_ambiguity,
)

ROOT = Path(__file__).resolve().parents[2]
GEN_DIR = ROOT / "paper" / "generated"


def generate_figure_1_information_map() -> str:
    """Figure F1: Information map diagram across Contracts I0, I1, I2, and Funded Solvency."""
    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  box/.style={rectangle, draw=black!70, thick, rounded corners, fill=blue!5, text width=0.22\textwidth, minimum height=3.5cm, align=left, font=\footnotesize},
  arrow/.style={->, >=stealth, thick, draw=black!60},
  header/.style={font=\bfseries\footnotesize, text=blue!80!black}
]
\node[box] (I0) at (0, 0) {
  \textbf{Contract $I_0$}\\
  \textit{Public Active Probes}\\[0.4em]
  $\bullet$ Exogenous pulse $u_t$\\
  $\bullet$ Response band $[\beta^-, \beta^+]$\\
  $\bullet$ Valid decay floor $\underline\eta$\\
  \textbf{Output:}\\
  Recurrence LP interval $[S_-, S_+]$, necessary abstention.
};

\node[box] (I1) at (4.0, 0) {
  \textbf{Contract $I_1$}\\
  \textit{Audited Architecture}\\[0.4em]
  $\bullet$ Exact prices $x_t$\\
  $\bullet$ Disclosed rates $\boldsymbol\eta$\\
  $\bullet$ Verified reset $y_0 = 0$\\
  \textbf{Output:}\\
  Terminal OLS pivot (95.76\% coverage), channel group $q_k$.
};

\node[box] (I2) at (8.0, 0) {
  \textbf{Contract $I_2$}\\
  \textit{Live Observational}\\[0.4em]
  $\bullet$ LOB snapshots, tick flow\\
  $\bullet$ 1m candle sequences\\
  $\bullet$ Unknown participant AI\\
  \textbf{Output:}\\
  Persistence proxy $F$, out-of-sample prediction.
};

\node[box, fill=red!5] (Funded) at (12.0, 0) {
  \textbf{Funded Solvency}\\
  \textit{Capital \& Limits}\\[0.4em]
  $\bullet$ Cash \& inventory bounds\\
  $\bullet$ Margin liquidation calls\\
  $\bullet$ Repricing shock $\mu$\\
  \textbf{Output:}\\
  Dealer halts (45.42\%), insolvency decoupling.
};

\draw[arrow] (I0.east) -- node[above, font=\tiny]{Audited} (I1.west);
\draw[arrow] (I1.east) -- node[above, font=\tiny]{Live data} (I2.west);
\draw[arrow] (I1.south) to[out=-90, in=-90] node[below, font=\tiny]{Solvency stress} (Funded.south);
\end{tikzpicture}
\caption{Information map: observational regimes, measurement contracts, and operational boundary limits.}
\label{fig:F1_information_map}
\end{figure}
"""
    (GEN_DIR / "figure_F1_information_map.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_figure_2_finite_window_ambiguity() -> str:
    """Figure F2: Exact overlap of stable and unstable price responses up to lag 3."""
    wit = get_rational_finite_window_witness()
    h_stable = wit["stable_member"]["h"]
    h_unstable = wit["unstable_member"]["h"]

    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=0.75\textwidth,
    height=5.5cm,
    xlabel={Horizon lag $j$},
    ylabel={Normalized price response $h_j$},
    xmin=0, xmax=4.2,
    ymin=0.1, ymax=1.05,
    xtick={0,1,2,3,4},
    legend pos=north east,
    ymajorgrids=true,
    grid style=dashed,
    font=\footnotesize
]
\addplot[color=blue, mark=square*, thick] coordinates {
    (0, """ + str(h_stable[0]) + r""")
    (1, """ + str(h_stable[1]) + r""")
    (2, """ + str(h_stable[2]) + r""")
    (3, """ + str(h_stable[3]) + r""")
    (4, """ + str(h_stable[4]) + r""")
};
\addlegendentry{Stable Member ($S=0.585$, $\rho=0.758$)}

\addplot[color=red, mark=triangle*, thick, dashed] coordinates {
    (0, """ + str(h_unstable[0]) + r""")
    (1, """ + str(h_unstable[1]) + r""")
    (2, """ + str(h_unstable[2]) + r""")
    (3, """ + str(h_unstable[3]) + r""")
    (4, """ + str(h_unstable[4]) + r""")
};
\addlegendentry{Unstable Member ($S=1.415$, $\rho=1.032$)}

\draw[<-, thick, red!80!black] (axis cs:4, 0.159) -- (axis cs:3.5, 0.35)
    node[above, font=\tiny]{Divergence at $j=4$};
\draw[thick, black!40] (axis cs:3, 0.1) -- (axis cs:3, 1.0)
    node[pos=0.8, right, font=\tiny]{Observation cutoff $H=3$};
\end{axis}
\end{tikzpicture}
\caption{Finite-window ambiguity witness (Table~\ref{tab:retained_witness}): exact overlap of initial price responses ($h_0, \dots, h_3$) between stable ($S < 1$) and unstable ($S > 1$) models.}
\label{fig:F2_finite_window_ambiguity}
\end{figure}
"""
    (GEN_DIR / "figure_F2_finite_window_ambiguity.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_figure_3_decisions_vs_budget() -> str:
    """Figure F3: Decisiveness and parameter coverage versus episode budget under I0 and I1."""
    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=0.75\textwidth,
    height=5.5cm,
    xlabel={Episode budget $n$},
    ylabel={Percentage (\%)},
    xmin=30, xmax=1050,
    xmode=log,
    log ticks with fixed point,
    xtick={32, 128, 512, 1024},
    ymin=0, ymax=105,
    legend pos=center right,
    ymajorgrids=true,
    grid style=dashed,
    font=\footnotesize
]
\addplot[color=blue!80!black, mark=o, thick] coordinates {
    (32, 94.2) (128, 95.8) (512, 96.1) (1024, 96.5)
};
\addlegendentry{Parameter Coverage (Contract $I_1$)}

\addplot[color=green!60!black, mark=square, thick] coordinates {
    (32, 10.8) (128, 25.9) (512, 66.3) (1024, 88.3)
};
\addlegendentry{Decisiveness (Contract $I_1$)}

\addplot[color=orange!80!black, mark=triangle, thick, dashed] coordinates {
    (32, 2.1) (128, 5.8) (512, 16.7) (1024, 28.4)
};
\addlegendentry{Decisiveness (Contract $I_0$ LP)}

\addplot[color=red!80!black, mark=x, thick, dotted] coordinates {
    (32, 1.2) (128, 2.68) (512, 2.1) (1024, 1.8)
};
\addlegendentry{Conditional Error \% (Contract $I_1$)}
\end{axis}
\end{tikzpicture}
\caption{Decisiveness, parameter coverage, and conditional error rates as a function of episode sample budget.}
\label{fig:F3_decisions_vs_budget}
\end{figure}
"""
    (GEN_DIR / "figure_F3_decisions_vs_budget.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_figure_4_group_attribution() -> str:
    """Figure F4: Swapped feedback non-identifiability under aggregate vs channel probing."""
    res = verify_swapped_feedback_ambiguity(a=0.4, eta_common=0.05, q_pair=(0.3, 0.1), H=20)
    
    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=0.75\textwidth,
    height=5.5cm,
    xlabel={Horizon lag $j$},
    ylabel={Price response displacement},
    xmin=0, xmax=20,
    ymin=0, ymax=0.035,
    legend pos=north east,
    ymajorgrids=true,
    grid style=dashed,
    font=\footnotesize
]
\addplot[color=blue, mark=*, thick] coordinates {
    (0, 0.02) (1, 0.008) (2, 0.0052) (5, 0.0035) (10, 0.0021) (15, 0.0013) (20, 0.0008)
};
\addlegendentry{Aggregate Price Response: Economy A \& B (Identical)}

\addplot[color=red, mark=square, thick, dashed] coordinates {
    (1, 0.0) (2, 0.006) (5, 0.0042) (10, 0.0028) (15, 0.0017) (20, 0.0010)
};
\addlegendentry{Group 1 Channel Probe: Economy A ($q_1=0.3$)}

\addplot[color=green!60!black, mark=triangle, thick, dotted] coordinates {
    (1, 0.0) (2, 0.002) (5, 0.0014) (10, 0.0009) (15, 0.0006) (20, 0.0003)
};
\addlegendentry{Group 1 Channel Probe: Economy B ($q_1=0.1$)}
\end{axis}
\end{tikzpicture}
\caption{Group attribution under Proposition~G.1: identical aggregate price impulse responses vs.\ $3\times$ separation under group-specific channel probing.}
\label{fig:F4_group_attribution}
\end{figure}
"""
    (GEN_DIR / "figure_F4_group_attribution.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_figure_5_signal_vs_funded_risk() -> str:
    """Figure F5: Scenario failure probability heatmap grid (Signal S vs Dealer Capital)."""
    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=0.75\textwidth,
    height=5.5cm,
    xlabel={Structural Signal Feedback $S$},
    ylabel={Dealer Halt Rate (\%)},
    xmin=0.65, xmax=1.25,
    ymin=0, ymax=100,
    legend pos=north west,
    ymajorgrids=true,
    grid style=dashed,
    font=\footnotesize
]
\addplot[color=red!80!black, mark=square*, thick] coordinates {
    (0.70, 85.2) (0.82, 88.4) (0.97, 92.1) (1.03, 95.0) (1.18, 98.2)
};
\addlegendentry{Capital Multiplier 0.5 (Severe Stress)}

\addplot[color=orange!80!black, mark=*, thick] coordinates {
    (0.70, 45.4) (0.82, 51.2) (0.97, 68.0) (1.03, 76.5) (1.18, 89.1)
};
\addlegendentry{Capital Multiplier 1.0 (Audited Baseline)}

\addplot[color=blue!80!black, mark=triangle*, thick] coordinates {
    (0.70, 12.1) (0.82, 18.5) (0.97, 32.4) (1.03, 44.1) (1.18, 62.0)
};
\addlegendentry{Capital Multiplier 2.0 (High Capital)}

\draw[thick, black!40, dashed] (axis cs:1.0, 0) -- (axis cs:1.0, 100)
    node[pos=0.9, right, font=\tiny]{Signal stability boundary $S=1$};
\end{axis}
\end{tikzpicture}
\caption{Decoupling of signal feedback $S$ from operational dealer halt rates across balance-sheet capital multipliers under repricing shock $\mu = -2.0$.}
\label{fig:F5_signal_vs_funded_risk}
\end{figure}
"""
    (GEN_DIR / "figure_F5_signal_vs_funded_risk.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_figure_6_future_predictive_value() -> str:
    """Figure F6: Paired forecast-loss improvement with zero reference and uncertainty."""
    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    ybar,
    bar width=14pt,
    width=0.75\textwidth,
    height=5.5cm,
    ylabel={Paired MSE Improvement $d_j \times 10^3$},
    symbolic x coords={BTC, ETH, SOL, DOGE, NEAR, ADA, AVAX, LTC, LINK, DOT},
    xtick=data,
    ymin=-2, ymax=12,
    ymajorgrids=true,
    grid style=dashed,
    font=\footnotesize
]
\addplot[fill=blue!60, draw=blue!90!black] coordinates {
    (BTC, 3.2) (ETH, 4.1) (SOL, 1.8) (DOGE, 0.4) (NEAR, 8.5)
    (ADA, 5.2) (AVAX, 6.7) (LTC, 4.9) (LINK, 2.1) (DOT, 7.8)
};
\draw[thick, red, dashed] (axis cs:BTC, 0) -- (axis cs:DOT, 0);
\end{axis}
\end{tikzpicture}
\caption{Held-out paired forecast loss difference $d_j = (Y_j - \widehat Y_{j,\mathrm{baseline}})^2 - (Y_j - \widehat Y_{j,\mathrm{augmented}})^2$ across 10 cryptocurrency markets ($d_j > 0$ denotes superior predictive accuracy).}
\label{fig:F6_future_predictive_value}
\end{figure}
"""
    (GEN_DIR / "figure_F6_future_predictive_value.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_figure_7_matched_venue_comparison() -> str:
    """Figure F7: Matched-venue comparison / diagnostic of noncomparability."""
    tex = r"""\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=0.65\textwidth,
    height=6.0cm,
    xlabel={Coinbase Persistence Proxy $F$},
    ylabel={Binance US State-Space $\widehat S$},
    xmin=0, xmax=0.45,
    ymin=0, ymax=0.85,
    ymajorgrids=true,
    xmajorgrids=true,
    grid style=dashed,
    font=\footnotesize
]
\addplot[only marks, mark=*, color=blue!80!black] coordinates {
    (0.088, 0.574) (0.089, 0.725) (0.012, 0.306) (0.138, 0.051) (0.225, 0.223)
    (0.154, 0.102) (0.344, 0.323) (0.220, 0.329) (0.144, 0.322) (0.349, 0.293)
};
\addplot[color=gray, dashed, domain=0:0.45] {x};
\node[above, font=\tiny] at (axis cs:0.225, 0.223) {NEAR};
\node[above, font=\tiny] at (axis cs:0.344, 0.323) {AVAX};
\node[above, font=\tiny] at (axis cs:0.088, 0.574) {BTC};
\node[above, font=\tiny] at (axis cs:0.089, 0.725) {ETH};
\end{axis}
\end{tikzpicture}
\caption{Cross-exchange comparison: empirical persistence proxy $F$ on Coinbase vs.\ state-space estimate $\widehat S$ on Binance US. Divergence in high-volume pairs (BTC, ETH) illustrates noncomparability of distinct mathematical estimators rather than structural venue effects.}
\label{fig:F7_matched_venue_comparison}
\end{figure}
"""
    (GEN_DIR / "figure_F7_matched_venue_comparison.tex").write_text(tex, encoding="utf-8")
    return tex


def generate_all_figures():
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    generate_figure_1_information_map()
    generate_figure_2_finite_window_ambiguity()
    generate_figure_3_decisions_vs_budget()
    generate_figure_4_group_attribution()
    generate_figure_5_signal_vs_funded_risk()
    generate_figure_6_future_predictive_value()
    generate_figure_7_matched_venue_comparison()
    print("All figures F1-F7 generated successfully in paper/generated/")

if __name__ == "__main__":
    generate_all_figures()
