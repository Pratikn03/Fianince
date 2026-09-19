#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base=(ROOT/'provenance/Integrated_v0_4.tex').read_text()
new=(ROOT/'docs/NEW_SECTIONS.tex').read_text()
s=base.replace('Integrated research v0.4','Audited constraints v0.5').replace('version 0.4\\\\18 September 2026','version 0.5\\\\18 September 2026')
s=s.replace('Feedback Stability, Hidden Learning, and Observable Stress Tests','Feedback Stability, Auditable Memory, and Financial Constraints')
a=s.index('\\begin{abstract}');b=s.index('\\end{abstract}',a)
s=s[:a]+r'''\begin{abstract}
Adaptive financial agents can alter the market observations on which they subsequently act. This paper studies what measurements can establish about that feedback, rather than claiming that artificial intelligence replaces fundamental financial identities. We integrate a joint market--learning framework, finite-window counterexamples, a full-horizon identification audit, and observable order--price experiments. Earlier findings favor conventional full-information bounds over the original summary diagnostic and show that a false learning-rate floor can invalidate an otherwise accurate response estimate. We extend the analysis with explicit implementation-conditioned tail bounds, terminal-row inference from public price histories and audited update rules, and a funded transaction model. The architectural contract is stronger than a black-box rate assumption and requires a truthful reset and complete channel inventory; a self-issued manifest is not sufficient. In 2,880 primary audited-model panels, gain intervals cover the truth in 95.76\% of cases. A fresh-seed endpoint-design comparison improves definite decisions at small episode budgets but loses that advantage at the largest budget; wrong calls are retained. The funded model enforces inventory, leverage and credit constraints, forced liquidation, rejected fills and dealer halts. Its local linear certificate is not extrapolated through those nonlinearities. Instead, exact binomial intervals quantify a specified finite-horizon loss event. A preloaded dealer can halt frequently even when the isolated signal-feedback model is locally stable. All experiments are synthetic and uncalibrated; several primary financial settings are easy probability extremes. Source, observations, complete result rows, failure controls and alternate internal verifiers are released. No outside replication, authenticated institutional audit, established novelty or real-market crisis-prediction capability is claimed.
''' + s[b:]
s=s.replace('No trained neural agents, funded exchange environment, independent outside replication, established priority, or financial-safety deployment is claimed.', 'Version~0.5 adds audited-memory inference and binding simulated balance sheets. No trained neural agents, calibrated exchange implementation, independent outside replication, established priority, or financial-safety deployment is claimed.')
s=s.replace('The integrated manuscript now has four evidential layers.', 'The first four evidential layers, retained from version~0.4, are the following.')
s=s.replace('The later intervention, rich multi-agent and institutional studies remain prospective.', 'Sections~\\ref{sec:audited_tails}--\\ref{sec:binding_finance} add the v0.5 source-contract, observation-budget and binding-finance studies. Rich trained-agent, calibrated exchange and institutional studies remain prospective.')
s=s.replace('\\section{Intervention under uncertainty and liquidity feedback}',new+'\n\\section{Intervention under uncertainty and liquidity feedback}')
s=s.replace('The positive-feedback specialization excludes', 'The linear positive-feedback specialization excludes')
s=s.replace('The original algebra checks and subsequent measurement experiments are uncalibrated to a real exchange.', 'The original algebra checks and all subsequent measurement and funded-market experiments are uncalibrated to a real exchange. The v0.5 funded model introduces binding financial limits, but its source-aware linear interval is deliberately not applied across those nonlinear limits.')
old='The next consequential result must improve the measurement design or uncertainty set under a realistic observation and intervention budget, compare against equally informed conventional alternatives, and test transfer to models with binding financial constraints. An externally reviewed proof and independently reproduced observation protocol would be meaningful progress. A global safety framework still requires real institutional evidence, validated economic outcomes and wider adoption, not simply a larger manuscript.'
replacement=r'''Version~0.5 makes further model-conditioned progress. A truthful implementation contract bounds the isolated memory tail; a terminal-row design estimates gain and tail contrasts from observable prices without reading private states. Preassigned diverse endpoints improve low-budget decisions on held-out synthetic panels but do not uniformly dominate a fixed endpoint. Binding limits and preloaded dealer stress show why the linear signal certificate cannot serve as a blanket financial-safety claim. A different, finite-horizon probability target remains statistically measurable under explicit independent-scenario assumptions.

The resulting direction is a separation of guarantees, not a completed universal detector. Architectural audit, observed statistical uncertainty and operational financial risk must each be established at their own level. The next external requirements are truthful complete-state provenance, a calibrated observation and funding environment, an appropriately strong equal-information comparator for each target, outside proof and novelty review, and an independent team's reproduction. A global safety framework requires institutional evidence and validated economic outcomes, not simply a larger manuscript.'''
assert old in s;s=s.replace(old,replacement)
s=s.replace('The new price-only study was executed for this integration;', 'The v0.4 price-only study was executed for the previous integration;')
s=s.replace('Rich trained-agent and real-institution experiments remain unexecuted.', 'The v0.5 supplement adds source-audited regression, measured tails, endpoint-budget comparisons and funded-market studies, with all terminal regression rows, per-episode financial outcomes, selected complete price paths and source-based regeneration. Rich trained-agent and real-institution experiments remain unexecuted.')
bibs=r'''
\bibitem[Manchester(2010)]{manchester2010}
Ian R. Manchester.
\newblock Input Design for System Identification via Convex Relaxation.
\newblock arXiv:1009.5614, 2010.
\newblock \url{https://arxiv.org/abs/1009.5614}.

\bibitem[Clopper and Pearson(1934)]{clopper1934}
C. J. Clopper and E. S. Pearson.
\newblock The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial.
\newblock \emph{Biometrika}, 26(4):404--413, 1934.
\newblock doi:10.1093/biomet/26.4.404.

\bibitem[Abi Jaber et~al.(2024)]{abijaber2024}
Eduardo Abi Jaber, Nathan De Carvalho and Huy\^en Pham.
\newblock Trading with propagators and constraints: applications to optimal execution and battery storage.
\newblock arXiv:2409.12098, 2024.
\newblock \url{https://arxiv.org/abs/2409.12098}.
'''
s=s.replace('\\end{thebibliography}',bibs+'\n\\end{thebibliography}')
s=s.replace('\\subsection{Practical gates still open}', '\\subsection{Version 0.4 gates and the v0.5 response}')
s=s.replace('A realistic next observation study should predeclare', 'Version~0.4 identified the following gates. A realistic observation study should predeclare')
s=s.replace('The next economic environment should impose funded positions, inventory and margin limits, heterogeneous objectives and endogenously changing liquidity, with matched non-AI adaptive baselines.', 'Version~0.5 implements funded positions and binding inventory, credit and leverage limits, including dealer-capacity reductions. It does not close the requirements for calibrated endogenously changing liquidity, richer objectives, or matched trained-AI versus non-AI adaptive baselines.')
s=s.replace('These are concrete remaining scientific requirements, not matters solved by the present synthetic sample size.', 'The source audit and synthetic financial implementation make some of these requirements testable in this release, but independent external reproduction, institutional applicability and original-priority review remain open. Synthetic sample size does not close them.')
appendix=r'''
\section{Version 0.5 evidence and reproduction contract}
\label{app:v05_release}
The main manuscript preserves the original framework and both companion conclusions. Sections~\ref{sec:audited_tails}--\ref{sec:binding_finance} are new. Primary, post-primary pilot, held-out confirmation, and dealer-stress extension are distinguished in the protocol files. No experiment is described as externally preregistered.

\subsection{Data lineage and counts}
The v0.5 primary linear study contains 2,880 panels and 645,120 independent episode rows. Its tail reanalysis uses the same rows. Endpoint confirmation uses 720 fresh datasets and 161,280 episodes, evaluated twice for 1,440 paired decision rows. The financial primary uses 491,520 setting-trajectories but only 163,840 unique exogenous tapes because three funding regimes share each tape. Its 2,880 probability rows use nested episode budgets, not new data at every look. The preloaded-dealer extension adds 65,536 paths; the five assumption controls use 400 panels of 512 episodes. These are synthetic experimental counts, not counts of real institutions or independent crises.

\subsection{Executable information separation}
Files under \texttt{src/inference.py} accept public prices or reconstructed terminal rows and public rates. They do not accept the true $q_i$, noise variance, simulator memory, hidden equity state, or target label. Public records include probe schedules and preassigned endpoints where relevant. Source-truth parameters are used only by generators and post-estimation evaluators. Configuration disclosure is a maintained audit input, not a fact inferred from short prices. The standalone verifier uses SVD regression, explicit convolution, exact binomial intervals and LP order projection without project inference imports.

\subsection{Portable rerun}
From the new package root, the following commands rebuild the new studies. The finance runner checkpoints after eight newly computed settings; three invocations complete all 24. It rejects stale checkpoints when the financial source hash changes. To force a fresh run, use a clean copied directory, not an output folder containing old checkpoints.
\begin{lstlisting}[language=bash,numbers=none]
python -m pip install -r requirements.txt
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -m pytest -q tests
python scripts/run_linear.py
python scripts/run_finance.py --max-new 8
python scripts/run_finance.py --max-new 8
python scripts/run_finance.py --max-new 8
python scripts/run_followup.py
python scripts/run_controls.py
python scripts/measure_tail.py
python scripts/prepare_replication.py
python replication/verify_without_project_imports.py
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=paper paper/Machine_Markets_Audited_Integrated_Paper.tex
# Run the same pdflatex command again for cross-references.
\end{lstlisting}
The PDF and TeX are self-contained; reproducing research calculations does not require LaTeX. A clean-directory rerun and the final release record document the executed checks. Floating-point tolerances are part of the external contract; cross-platform bit identity is not promised.

\subsection{External-review acceptance checklist}
An outside reviewer should independently reconstruct the filters and final-row independence argument; challenge completeness of the declared audit boundary; check the geometric tail bound and the two-point predecessors; evaluate observation error and unknown initial states; inspect dealer and liquidation mechanics; compare fair budgets including inventory unwind; and rerun at least one observation panel in a separate implementation. A source digest from an untrusted issuer is not sufficient evidence. Passing the shipped tests is not proof of scientific novelty or external economic validity. The release's status for outside replication is explicitly \texttt{pending}, with no reviewer or institution attributed.
'''
s=s.replace('\\end{document}',appendix+'\n\\end{document}')
s=s.replace('Integrated research manuscript: feedback stability, hidden learning, and observable stress tests','Integrated research manuscript: audited memory, observation budgets, and binding financial constraints')
(ROOT/'paper/Machine_Markets_Audited_Integrated_Paper.tex').write_text(s)
print('Wrote',len(s),'characters')
