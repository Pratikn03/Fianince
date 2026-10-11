"""Reproducible interpretation and layout repairs after empirical regeneration."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[3]
def run():
 p=ROOT/'paper/Machine_Markets_JF_Submission.tex';s=p.read_text()
 s=s.replace('Let $p_t$ denote the log mid-price of a traded asset','Let $p_t$ denote the price level in monetary units of a traded asset')
 resource=r'\input{../research_extension/gap_closure_20261006/publication_completion/resource_frontier.tex}'
 capital=r'\input{../research_extension/gap_closure_20261006/publication_completion/capital_frontier.tex}'
 if capital not in s:s=s.replace(resource,resource+'\n\n'+capital)
 trader=r'\input{../research_extension/gap_closure_20261006/publication_completion/trader_capital_frontier.tex}'
 if trader not in s:s=s.replace(capital,capital+'\n\n'+trader)
 natural=r'\input{../research_extension/gap_closure_20261006/publication_completion/natural_excitation_boundary.tex}'
 if natural not in s:s=s.replace(capital,capital+'\n\n'+natural)
 # Replace the lower-bound sketch with an explicit uniform-family argument.
 s=s.replace('Under deterministic probing sequences satisfying power constraint','Under deterministic probing with $\\mathcal P_{\\text{probe}}>0$ satisfying the power constraint')
 theorempos=s.index(r'\label{thm:m1_equivalence}')
 proofstart=s.index(r'\begin{proof}',theorempos);proofend=s.index(r'\end{proof}',proofstart)+len(r'\end{proof}')
 s=s[:proofstart]+r'''\begin{proof}
Let $r_i=1-\eta_i$. Zero-state cohort recursion gives
\[G(z)=\sum_i\frac{q_i\eta_i z}{z-r_i},\qquad H(z)=\frac{\kappa}{z-a-\kappa G(z)}.\]
Equality of every controlled price response is equality of $H$, which recovers $G$ because $a,\kappa$ are known. Its residue at a retained rate is $r_i\eta_i$ times that rate's merged weight. Distinct nonzero residues identify the merged measure by uniqueness of partial fractions. Conversely identical merged measures give identical $G,H$ and responses. After signed cancellations, let $D(z)$ be the product of the retained distinct $(z-r_i)$ factors. The numerator of $H$ is $\kappa D$ and its denominator has degree one more. At any retained $r_i$, the denominator is nonzero because its residue, $r_i$ and $\eta_i$ are nonzero. Thus no common factor remains and the minimal realization has the claimed degree. The cohort poles are poles of $G$ and zeros of $H$, not its closed-loop poles.

For the symmetric pair write $q=Q/\kappa$. Direct algebra gives
\[G_\delta-G_0=-\frac{qz(z-1)\delta^2}{(z-1+\bar\eta)((z-1+\bar\eta)^2-\delta^2)}.\]
All three denominator factors on $|z|=1$ have modulus at least the declared rate separation from the endpoints, say $\epsilon$. Compactness and uniform Schur stability give a finite bound $M=\sup_{\theta\in\mathcal F,|z|=1}|H_\theta(z)|$. The identity $H_\delta-H_0=H_\delta H_0(G_\delta-G_0)$ therefore gives induced $\ell_2$ gain at most $K\delta^2$, where $K=2|q|M^2/\epsilon^3$. Zero-padding the finite probe and retaining its observed response cannot increase that gain. Its Gaussian mean difference consequently has squared norm at most $K^2\delta^4\mathcal P_{probe}T$, and equal-noise KL is at most $K^2\delta^4\mathcal P_{probe}T/(2\sigma_v^2)$. Error at most $\alpha$ requires total variation at least $1-2\alpha$. Pinsker then yields
\[T\ge\frac{4\sigma_v^2(1-2\alpha)^2}{K^2\mathcal P_{probe}\delta^4}.\]
The constant depends on the specified family and resources, rather than being universal. The following theorem gives matching known-pair resource orders and explicit financial contracts.
\end{proof}'''+s[proofend:]
 if r'\label{fig:capital_information}' not in s:
  figure=r'''\begin{figure*}[htbp]\centering
\includegraphics[width=\textwidth]{figures/fig_capital_information_20261008.pdf}
\caption{Constructed known-pair experiment funded by the counterparty cash/margin contract. Panel(a) gives exact Gaussian error at fixed counterparty capital100 and1,000, with separation0.05; waiting approaches a nonzero error floor. Panel(b) gives the sharp robust quantity allowance. Panel(c) gives exact required capital within that counterparty quantity-ball contract for error0.1 with200 observations. Parameters are $a=0.5,\kappa=0.8,q=0.2,\eta=0.4$, observation SD0.003, reference price100, margin0.25 and cost0.02. Quotes refresh after the uncontrolled update and executions pay half their direct impact. There is no process noise. These are imposed model units and fills, not market calibration; growing probes require the maintained linear model's validity.}
\label{fig:capital_information}\end{figure*}'''
  s=s.replace(capital,capital+'\n\n'+figure)
 # Refresh the caption in previously generated candidates as well.
 caption_start=s.index(r'\caption{Constructed known-pair')
 caption_end=s.index(r'\label{fig:capital_information}',caption_start)
 s=s[:caption_start]+r'''\caption{Constructed known-pair experiment funded by the counterparty cash/margin contract. Panel(a) gives exact Gaussian error at fixed counterparty capital100 and1,000, with separation0.05. Panel(b) gives the sharp robust quantity allowance. Panel(c) gives required capital within that counterparty quantity-ball contract for error0.1 with200 observations. Parameters are $a=0.5,\kappa=0.8,q=0.2,\eta=0.4$, observation SD0.003, reference price100, margin0.25 and cost0.02. Quotes refresh after the uncontrolled update and executions pay half their direct impact. There is no process noise. These are imposed model units and fills. This plot does not give globally optimal probe-trader capital constants.}
'''+s[caption_end:]
 s=s.replace('The new resource comparison establishes necessary and sufficient quantity order $\\delta^{-2}$ for a known symmetric pair and horizon order $\\delta^{-4}$ under average power (Theorem~\\ref{thm:resource_frontier}).','The resource comparison establishes necessary and sufficient quantity order $\\delta^{-2}$ for a known symmetric pair and horizon order $\\delta^{-4}$ under average power (Theorem~\\ref{thm:resource_frontier}). A self-financing cash/inventory account then gives a sharp robust margin allowance and matching capital order $\\delta^{-4}$ under nonnegative quantity-ball probing (Theorem~\\ref{thm:cash_capital_frontier}).')
 s=s.replace('Conditional monetary exposure and accumulated cost convert that quantity allowance into a resolution constraint.','The dealer\'s inventory change creates a quadratic adverse mark, rather than only a fixed linear price exposure. These are distinct input, cash and observation contracts.')
 s=s.replace('Positive price-response gains connect this distinction to an explicit monetary output and cost allowance.','A self-financing counterparty account yields a sharp robust margin allowance; matching capital order is $\\delta^{-4}$ under that quantity-ball contract, including the inventory created by the probe. This is distinct from the time requirement and from a fixed-exposure output bound.')
 s=s.replace('A fixed monetary-output and accumulated-cost allowance bounds quantity; more waiting alone cannot overcome that lifetime resource limit.','An explicit cash/inventory and margin contract bounds quantity, including its quadratic adverse mark, and gives matching capital order $\\delta^{-4}$ for robust quantity-ball probing. A fixed price-exposure output is a separate contract. More waiting alone cannot overcome a fixed lifetime quantity allowance; the result does not bound every tailored safe strategy.')
 start='The delegation of financial execution and market making to autonomous algorithms has fundamentally transformed'
 if start in s:
  a=s.index(start);b=s.index('\n\n',a)
  s=s[:a]+r'Electronic execution and market making raise a financial identification question: what can aggregate price and flow observations reveal about trading rules, and which financial constraints govern experiments intended to learn those rules? Microstructure research documents the interaction of trades, quotes and automated liquidity provision \citep{hasbrouck1991,menkveld2013,budish2015}. We study a declared linear feedback economy and its information/resource contracts, then test whether observable measurement diagnostics support the corresponding interpretation.'+s[b:]
 s=s.replace('We prove that local price stability ($\\rho(J) < 1$) does not guarantee financial intermediary solvency.','For a fixed initial-disturbance and model-output contract, spectral stability ($\\rho(J)<1$) alone does not bound the permitted loss-budget radius. A dealer solvency interpretation additionally requires a justified monetary accounting map.')
 s=s.replace('The exact worst-case safe shock radius for a leveraged dealer is governed by peak transient magnification:','The exact initial-state radius for that declared loss-budget experiment is governed by peak output magnification:')
 s=s.replace('3087--3111; primary preprint arXiv:2212.00536','primary preprint arXiv:2212.00536')
 s=s.replace(r'Nielsen, C., 2021, \texttt{crypto-rl}: High-frequency limit order book data capture, GitHub repository (CC0 License).',r'Nielsen, M. S., 2021, High Frequency Crypto Limit Order Book Data, Kaggle dataset version1, uploader-declared CC0, \url{https://www.kaggle.com/datasets/martinsn/high-frequency-crypto-limit-order-book-data}.')
 s=s.replace(r'\emph{IEEE Transactions on Neural Networks and Learning Systems} 29, 6153--6163.',r'\emph{Journal of Forecasting} 37, 852--866, doi:10.1002/for.2543.')
 s=s.replace(r'\bibitem[Almgren and Chriss(2000)]{almgren2000}',r'\bibitem[Almgren and Chriss(2001)]{almgren2000}')
 s=s.replace(r'Almgren, R., and N.~Chriss, 2000, Optimal execution',r'Almgren, R., and N.~Chriss, 2001, Optimal execution')
 old='While FBAs eliminate microsecond sniper races within batch intervals, they do not resolve closed-loop adaptive feedback across batches: algorithmic momentum strategies updating across consecutive 100-millisecond auction clearings still generate price impact loops.'
 s=s.replace(old,'Batch matching changes execution timing and incentives; a feedback model can also be posed across successive batches. This paper does not estimate its comparative economic effect.')
 s=s.replace('We show that two widely deployed algorithmic learning paradigms—steady-state Kalman filtering and regularized Online Gradient Descent—both reduce locally to the identical linear adaptive recursion.','The specified Kalman and regularized gradient models give exponential-memory recursions. Embedding either in the price-first cohort economy additionally requires the stated signal, gain and timing assumptions; the empirical regressions do not identify that embedding.')
 s=s.replace('with innovation variance $\\sigma_\\zeta^2 > 0$, observing noisy price return increments $r_t = v_t + \\nu_t$ with observation noise $\\sigma_\\nu^2 > 0$.','with independent centered Gaussian innovations of variance $\\sigma_\\zeta^2>0$, observing $r_t=v_t+\\nu_t$ with independent centered Gaussian observation noise of variance $\\sigma_\\nu^2>0$. Assume a Gaussian initial state and the steady-state prior covariance.')
 s=s.replace('where $\\alpha > 0$ is the learning step size.','where $H>0$ is scalar curvature and $\\alpha>0$ is the learning step size.')
 s=s.replace('The exact maximum shock radius $r^*_{\\text{exact}}$ guaranteeing that no initial disturbance with $\\|z_0\\|_2 \\le r^*_{\\text{exact}}$ triggers dealer insolvency in any direction is:', 'For the declared criterion $\\sup_t\\|CJ^tz_0\\|_2\\le B$, the exact maximum initial-state radius is:')
 s=s.replace('\\begin{theorem}[Dealer Solvency and the Kreiss Constant Bound]', '\\begin{theorem}[Conditional Loss Budget and Kreiss Bounds]')
 s=s.replace('where $M_C \\equiv \\sup_{t \\ge 0} \\|C J^t\\|_2$ is the peak transient magnification.', 'where $M_C \\equiv \\sup_{t \\ge 0} \\|C J^t\\|_2$ is the declared output gain. If $C=0$, the allowance is unbounded by this criterion; actual financial constraints still apply.')
 s=s.replace('Part~3 constructs an explicit non-normal Jordan family where spectral radius is held constant while non-orthogonal eigenvectors inflate the resolvent norm, sending $r^*_{\\text{exact}} \\to 0$. (Full proof in Appendix~A of the Online Internet Appendix.)',r'Part~3 uses $J_\theta=\left(\begin{smallmatrix}\rho&\theta\\0&\rho\end{smallmatrix}\right)$. Then $CJ_\theta=(\rho,\theta)$, so $M_C\ge\sqrt{\rho^2+\theta^2}\to\infty$. The family is defective; no eigenvector-basis argument is required.')
 if r'\begin{remark}[The Dangerous Illusion of Spectral Stability]' in s:
  a=s.index(r'\begin{remark}[The Dangerous Illusion of Spectral Stability]');b=s.index(r'\end{remark}',a)
  s=s[:a]+r'''\begin{remark}[Output and disturbance geometry]
The theorem applies to a specified initial-state ball and output norm. State coordinate changes require a corresponding change in the disturbance set; arbitrary latent-state units cannot be interpreted as monetary losses. A physical execution-input experiment has a different gain, as Theorem~\ref{thm:resource_frontier} shows. The Kreiss lower radius concerns full-state observation. A small spectral radius alone supplies no universal bound, but non-normality alone does not establish severe monetary losses in a calibrated market.
'''+s[b:]
 old='In complementary simulation environments ($N = 19{,}200$ paths across 48 cells), we evaluate dealer capital solvency strictly inside the spectrally stable regime ($\\rho(J) \\in [0.80, 0.985] < 1.0$), demonstrating that dealer solvency failure surges from $11.0\\%$ to $100.0\\%$ as feedback increases, driven by $(1 - S)^{-2}$ low-frequency variance inflation. This structural divergence motivates capital-aware pre-trade gating grounded in the exact safe radius $r^*_{\\text{exact}} = B/M_C$.'
 s=s.replace(old,r'The separate lagged-memory experiment reproduces 19,200 paths across 48 cells, but its halt event combines equity and position-limit causes. The 22,000-path funded grid instead has positive-equity inventory-limit events in effective supercritical dynamics. Neither supplies observed market defaults or an independently calibrated policy benefit. Long-run variance and marginal variance are distinct quantities.')
 s=s.replace('and portfolio loss operator $C \\ge 0$. Let $J_{\\text{diag}}$', 'nonnegative impact matrix $\\mathbf K\\ge0$, stable diagonal blocks, and fixed output operator $C\\ge0$. Let $J_{\\text{diag}}$')
 proof=r'''\begin{proof}
Permute coordinates by asset; directed impact makes the full transition block triangular, preserving the stable diagonal spectra. Entrywise $0\le J_{diag}\le J_{multi}$ implies ordered nonnegative powers and ordered Euclidean operator norms after multiplication by fixed nonnegative $C$. For $r>1$, the nonnegative Neumann series $(rI-J)^{-1}=\sum_{t\ge0}J^t/r^{t+1}$ is likewise ordered. At any complex $z$ with $|z|=r$, its modulus is entrywise bounded by this real-radius resolvent, so the norm supremum on that circle occurs at $z=r$. Taking the Kreiss supremum proves its monotonicity. The statements concern fixed coordinates and nonnegative output; signed hedge outputs need separate analysis.
\end{proof}
'''
 pos=s.index(r'\label{prop:cross_kreiss}');end=s.index(r'\end{proposition}',pos)+len(r'\end{proposition}')
 if proof not in s:s=s[:end]+'\n'+proof+s[end:]
 s=s.replace('a standard 2-standard-deviation liquidity shock can amplify by a factor of 100','an initial-state disturbance can be amplified')
 s=s.replace('Their printed numerical literals lack a verified generating chain for this current revision','Their earlier printed numerical literals lacked a verified generating chain')
 s=s.replace('\\citet{hasbrouck1991} & Trades and quotes (VAR) & Open-loop flow', '\\citet{hasbrouck1991} & Trades and quotes (VAR) & Joint response')
 s=s.replace(r'\textbf{This Paper} & \textbf{Closed-loop learning} & \textbf{Non-normal VAR} & \textbf{Kreiss radius $r^*_{\text{exact}}$} & \textbf{Abstention limits; Pre-trade gating}',r'\textbf{This Paper} & Defined reset probe & Merged memory & Quantity/output budget & Known-pair resource orders')
 # Scope literature claims to established work and proposed contribution.
 s=s.replace('its application to high-frequency market microstructure and dealer solvency is novel','financial non-normality precedes this paper')
 s=s.replace('a $\\sim 0.5$--$1.5$ second window','a declared cancellation window')
 s=s.replace('stable eigenvalues can coexist with massive transient balance-sheet excursion','stable eigenvalues can coexist with large declared-output gain under an appropriate disturbance/output contract')
 # Break long in-line mathematics without changing the scientific statements.
 s=s.replace(r'where $M_C',r'where $M_C')
 s=s.replace('For the 24 sampled 2022 dates, fit $Y_{it}=\\beta_0+\\beta_1\\mathrm{BTC}_i+\\beta_2\\mathrm{Post}_t+\\beta_3\\mathrm{BTC}_i\\mathrm{Post}_t+e_{it}$, where',r'For the 24 sampled 2022 dates, fit \[Y_{it}=\beta_0+\beta_1\mathrm{BTC}_i+\beta_2\mathrm{Post}_t+\beta_3\mathrm{BTC}_i\mathrm{Post}_t+e_{it}.\] Here')
 s=s.replace('The diagnostic $Q_L=\\hat J_{12}\\hat c_L/(1-\\sum_{\\ell=1}^L\\hat\\phi_\\ell)$ uses',r'The diagnostic \[Q_L=\hat J_{12}\hat c_L/(1-\sum_{\ell=1}^L\hat\phi_\ell)\] uses')
 s=s.replace(r'Its own implemented matrix is $J_{lag}=\left(\begin{smallmatrix}a&1\\\eta Q&1-\eta\end{smallmatrix}\right)$, so',r'Its implemented matrix is \[J_{lag}=\begin{pmatrix}a&1\\\eta Q&1-\eta\end{pmatrix}.\] Thus')
 s=s.replace(r'Here low-frequency power means long-run variance, not marginal variance. With two independent unit-variance shock streams, the lagged model\'s analytic flow LRV is',r'Here low-frequency power means long-run variance, not marginal variance. With two independent unit-variance shock streams, the lagged model\'s analytic flow LRV is')
 # Source/licence status is updated separately after byte verification.
 s=s.replace('Original Panel, Timing Sensitivity and the Fee-Schedule Comparison','Original Panel and Fee-Schedule Comparison')
 s=s.replace('Mean $Q=0.000910232$, while $Q_{30}=-0.001296032$ with date interval $[-0.001567464,-0.001024600]$.','The mean is $Q=0.000910232$. The controlled diagnostic is $Q_{30}=-0.001296032$, with date interval $[-0.001567464,-0.001024600]$.')
 s=s.replace('Anonymous aggregate market features do not reveal participant identities. The exact merged-rate','Anonymous aggregate market features do not reveal participant identities. The exact merged rate')
 s=s.replace('49 stock/day sessions','50 raw stock/day labels; 49 fitted sessions')
 import json
 receipt=ROOT/'research_extension/gap_closure_20261006/publication_completion/recorder_authentication.json'
 if receipt.exists() and len(json.loads(receipt.read_text())['rows'])==3:
  s=s.replace('Recorder/provider unresolved','Primary version1 bytes matched')
  s=s.replace('Provider attribution, the recorded flow accumulation window and reuse permission remain open.','The three recorder files exactly match the named Nielsen version1 release, which declares CC0. The original feature accumulation window and collection correctness require a separate recorder audit.')
  anchor='Counts of these objects cannot be combined into a count of independent, continuous one-second transitions.'
  if 'provider release byte for byte' not in s:
   s=s.replace(anchor,anchor+' The three recorder CSVs match the Nielsen version1 provider release byte for byte, with provider archive CRC and full SHA256 checks. Its primary metadata declares CC0. The FI-2010 primary metadata declares CC BY4.0; the local mirror licence does not supersede it. Its transformed stock/day representation still requires original-archive reconstruction. Current Binance Vision terms specify CC BY-NC-SA4.0 for the downloaded data; the final derivative-release package must reflect the provider terms. The January sample remains unauthenticated. Source metadata, hashes and licence texts accompany this revision.')
 january=ROOT/'research_extension/gap_closure_20261006/publication_completion/january_authentication.json'
 if january.exists() and json.loads(january.read_text())['serialization_bytes_match']:
  s=s.replace('The January sample remains unauthenticated.','The January CSV is exactly reconstructed from the named primary Parquet release, whose uploader declares Apache2.0; its exchange/contract metadata remain undocumented.')
  s=s.replace('Provider/licence unresolved','Primary distribution matched')
  s=s.replace('The provider is unresolved and the sample was previously examined;','The CSV exactly matches a Parquet-to-CSV reconstruction of the named primary distribution. Its uploader declares Apache2.0, while exchange/contract details remain undocumented. The sample was previously examined;')
  s=s.replace('The January sample remains unauthenticated.','The January distribution is authenticated; its upstream venue/contract remain undocumented.')
 calendar=ROOT/'research_extension/gap_closure_20261006/publication_completion/calendar_inference_sensitivity.json'
 if calendar.exists() and 'Calendar Bartlett' not in s:
  anchor='The original panel is fully reconstructed at its 768 named study units using current official archives.'
  s=s.replace(anchor,anchor+' Calendar Bartlett HAC sensitivity at 30,90,180 and365-day bandwidths retains positive pooled observed-EMA reference intervals and raw-return intervals spanning zero. These retrospective Gaussian references require additional mixing/stationarity assumptions; they do not establish causal or finite-sample coverage. All32 index/measurement references accompany the revision.')
 completeness=ROOT/'research_extension/gap_closure_20261006/publication_completion/recorder_bin_completeness.json'
 if completeness.exists():
  s=s.replace('The recorder EMA is reset at gaps, continues across contiguous dates, and regressions split dates and gaps.','The recorder baseline admits occupied ten-second bins, including partial bins; its EMA resets at missing whole bins and continues across contiguous dates, while regressions split dates and those bin gaps.')
  if 'The baseline recorder construction admits' not in s:
   anchor='The raw-return date intervals include zero for all three assets.'
   s=s.replace(anchor,anchor+' The baseline recorder construction admits 75,72 and69 partial bins for BTC, ETH and ADA. A stricter sensitivity requires ten observed seconds and resets the EMA across resulting gaps: mean observed-EMA $Q$ becomes 0.0010800,0.0007072 and0.0004148. Its ADA EMA interval spans zero; all three strict raw-return intervals also span zero. Every strict sample count, date estimate and interval is retained. The baseline covariance, switching and shuffle studies refer to their explicitly retained occupied-bin construction, rather than claiming complete-bin robustness.')
 s=s.replace('matching capital order is $\\delta^{-4}$ under that quantity-ball contract, including the inventory created by the probe.','matching capital order is $\\delta^{-4}$ for the restricted noisy-price observer under that quantity-ball contract, including the inventory created by the probe.')
 s=s.replace('An explicit cash/inventory and margin contract bounds quantity, including its quadratic adverse mark, and gives matching capital order $\\delta^{-4}$ for robust quantity-ball probing.','An explicit cash/inventory and margin contract bounds quantity, including its quadratic adverse mark, and gives matching capital order $\\delta^{-4}$ for a restricted noisy-price observer under robust quantity-ball probing. Exact equity disclosure and natural excitation supply constructive counterexamples to a universal capital barrier.')
 s=s.replace('a 100-event EMA deviation in dollars','an EMA deviation in dollars with adaptation0.01 per retained record')
 s=s.replace('Flow is signed base quantity;','Flow is a constructed signed base-unit feature;')
 s=s.replace('observed signed base-unit flow','the constructed signed base-unit feature')
 s=s.replace('These structural phenomena confront financial economists','These information and financial questions concern financial economists')
 s=s.replace('A self-financing cash/inventory account then gives a sharp robust margin allowance and matching capital order $\\delta^{-4}$ under nonnegative quantity-ball probing (Theorem~\\ref{thm:cash_capital_frontier}).','Actual trading cost gives matching capital order $\\delta^{-4}$ for deterministic probes financed by a trader who remains solvent after temporary impact dissipates, when the statistical observer receives only noisy price states (Theorem~\\ref{thm:trader_capital_frontier}). A separate counterparty account gives a sharp robust quantity/margin allowance (Theorem~\\ref{thm:cash_capital_frontier}).')
 s=s.replace('A self-financing counterparty account yields a sharp robust margin allowance; matching capital order is $\\delta^{-4}$ for the restricted noisy-price observer under that quantity-ball contract, including the inventory created by the probe.','A self-financing probe-trader account yields matching capital order $\\delta^{-4}$ for the restricted noisy-price observer; a separate counterparty account gives a sharp robust margin allowance.')
 start='Our realization-theoretic theorems prove that public market data suffer from fundamental blind spots:'
 if start in s:
  a=s.index(start);b=s.index('\n\n',a)
  s=s[:a]+r'Each result uses a declared information contract. Exact reset response functions determine a merged representation rather than participant identities. Noisy-price testing costs require the stated innovation law and exclusion of richer financial records. Exact marked equity and natural excitation supply constructive counterexamples to a universal capital barrier. The positive-class quantity certificate requires authenticated impact, margin and account assumptions; it does not require individual learning-rate identities once that model class is verified. Covariance rejection and measurement sensitivity prevent substituting public reduced-form coefficients for these operational conditions.'+s[b:]
 s=s.replace('An explicit cash/inventory and margin contract bounds quantity, including its quadratic adverse mark, and gives matching capital order $\\delta^{-4}$ for a restricted noisy-price observer under robust quantity-ball probing.','Actual probe-trader execution cost gives matching capital order $\\delta^{-4}$ for funded deterministic probes under the restricted noisy-price contract. A separate counterparty cash/margin contract gives a sharp quantity allowance, including the inventory created by the probe.')
 s=s.replace('(complemented by a benchmark sample of regulated NASDAQ Nordic equities)','(complemented by a supplied equity representation whose upstream transformation remains unauthenticated)')
 s=s.replace('In general, $\\mathbf{K}$ is asymmetric ($\\mathbf{K} \\neq \\mathbf{K}^\\top$): institutional order flow in a benchmark asset (such as BTC or SPY) exerts cross-impact on satellite assets, but the reverse flow produces much smaller reactions.','For the following mathematical feedforward benchmark, allow $\\mathbf K$ to be asymmetric. No causal instantaneous cross-asset impact matrix is calibrated here. A transactional interpretation additionally requires an execution-cost law consistent with no-price-manipulation restrictions; cross-impact symmetry under the relevant bounded-kernel assumptions is a substantive economic constraint \\citep{schneiderlillo2017}.')
 if 'Financial exploration already balances trading cost' not in s:
  anchor=r'\subsection{Empirical Research Design and Setting}'
  paragraph=r'''Financial exploration already balances trading cost and information. \citet{parkvanroy2012} study learning impact coefficients during execution, with known distinct transient decay rates and an adaptive expected-regret objective. Here the known-pair diagnostic concerns coalescing latent adaptation rates and an explicit initial-capital/solvency restriction under a specified observation law. The paper does not claim a first financial learning algorithm or a new general exploration-cost principle. Positive transaction-cost and no-dynamic-arbitrage conditions likewise precede this work \citep{gatheral2010,schneiderlillo2017}; the contribution must lie in the particular model/resource connection and its demonstrated scope.
'''
  s=s.replace(anchor,paragraph+'\n'+anchor)
 refs=r'''\bibitem[Park and Van Roy(2012)]{parkvanroy2012}
Park, B., and B. Van Roy, 2012, Adaptive execution: Exploration and learning of price impact, primary preprint arXiv:1207.6423.
\bibitem[Gatheral(2010)]{gatheral2010}
Gatheral, J., 2010, No-dynamic-arbitrage and market impact, \emph{Quantitative Finance} 10, 749--759, doi:10.1080/14697680903373692.
\bibitem[Schneider and Lillo(2017)]{schneiderlillo2017}
Schneider, M., and F. Lillo, 2017, Cross-impact and no-dynamic-arbitrage, primary preprint arXiv:1612.07742v2.
'''
 if r'\bibitem[Park and Van Roy' not in s:s=s.replace(r'\end{thebibliography}',refs+'\n'+r'\end{thebibliography}')
 # Reconcile remaining old empirical interpretations with the rebuilt estimands.
 s=s.replace('Our analysis demonstrates that non-normal transient amplification can trigger intermediary insolvency even when the underlying price-formation process is spectrally stable ($\\rho(J) < 1$).','Our conditional loss-output analysis separates spectral stability from a declared loss budget. The empirical studies do not demonstrate intermediary insolvency in a calibrated stable market; the positive price-only response has the more restrictive geometry proved below.')
 s=s.replace('establishing fundamental realization-theoretic bounds on what econometricians can infer from public ticker feeds.','establishing conditional realization and resource bounds for the declared controlled experiment. Public ticker data require a separate observation and identification argument.')
 s=s.replace('To operationalize the theoretical closed-loop system empirically, we construct an estimand that is invariant to arbitrary currency scaling and directly identifiable from high-frequency limit order books.','We compute reduced-form indices under explicit price/flow constructions. Their algebra is invariant to consistent constant price and flow rescaling, but this does not identify structural learning or physical execution impact.')
 s=s.replace('Let $p_b$ denote the log mid-price sampled at discrete uniform time bars $b$','Let $p_b$ denote a log recorded-price proxy sampled at discrete uniform time bars $b$')
 s=s.replace('where $W$ is the smoothing window (e.g., $W = 300$~seconds, yielding', 'where the proxy is transaction close for Binance trade bars and midpoint for the recorder. Multiplication of log prices by 10,000 changes their units, not the stated constant-scaling invariants. Here $W$ is the smoothing window (e.g., $W = 300$~seconds, yielding')
 a=s.index(r'\begin{remark}[Economic Interpretation of Empirical Feedback');b=s.index(r'\end{remark}',a)+len(r'\end{remark}')
 s=s[:a]+r'''\begin{remark}[Economic Interpretation of Empirical Feedback $\hat Q$]
The EMA state measures deviation from a trailing price proxy rather than the unobserved fundamental value. In the corrected observed-flow panel, equal-weight pooled date means give $\hat Q=0.0003807$ and $\hat S=0.9203825$, hence the corresponding mean $\hat J_{11}=0.9200018$. The mechanical martingale anchor is $29/31\simeq0.9354839$ for this filter. A smaller fitted coefficient is a descriptive comparison; it does not prove market-level fundamental stability, identify bid--ask bounce or inventory replenishment as its cause, or authenticate a structural feedback mechanism.
\end{remark}'''+s[b:]
 s=s.replace('where $J_{11} \\equiv a$ represents anchor-relative persistence, $J_{12} \\equiv \\lambda$ is price impact, $J_{21} \\equiv \\eta c$ captures feedback, and $J_{22} \\equiv 1 - \\eta$ measures flow autocorrelation.','Here all $J_{ij}$ are reduced-form coefficients for the constructed state and flow. They are not authenticated physical impact or latent learner parameters. When its denominators are nonzero, the diagnostic algebra is')
 s=s.replace('When its denominators are nonzero, the diagnostic algebra is From $\\hat{J}$, we extract','When its denominators are nonzero, we extract')
 s=s.replace('the signed market order flow (notional taker buy volume minus notional taker sell volume executed over $(t-\\Delta, t]$)','the sample-specific flow feature. Binance uses notional taker buy volume minus taker sell volume over the observed bar; recorder features and quote OFI use the separately declared constructions')
 s=s.replace('This is a recorded-series diagnostic; independent provider/licence authentication and the economic interpretation of its recorded flow remain separate gates.','This is a recorded-series diagnostic. Exact primary-source byte matching and uploader-declared CC0 are documented below; the economic interpretation of its recorded flow remains a separate question.')
 if 'Price-trajectory information and impact estimation also have prior work' not in s:
  paragraph=r'''Price-trajectory information and impact estimation also have prior work. \citet{li2024trajectory} compare regular-model Fisher information under different price sampling schemes. Our singular known-pair test asks about separation-dependent probing and capital, rather than a generally superior sampling method. The average-book quadratic execution cost and positive-kernel criterion are likewise established \citep{alfonsi2016matrix}; the positive-cohort lemma verifies that this particular response fits that geometry, rather than proposing a new no-manipulation criterion.
'''
  s=s.replace(r'\subsection{Empirical Research Design and Setting}',paragraph+'\n'+r'\subsection{Empirical Research Design and Setting}')
 refs=r'''\bibitem[Li et al.(2024)]{li2024trajectory}
Li, F., V. Ihnatiuk, Y. Chen, J. Lin, R. J. Kinnear, A. Schneider, Y. Nevmyvaka, and H. Lam, 2024, Do price trajectory data increase the efficiency of market impact estimation?, \emph{Quantitative Finance} 24, 545--568, doi:10.1080/14697688.2024.2351457.
\bibitem[Alfonsi et al.(2016)]{alfonsi2016matrix}
Alfonsi, A., A. Schied, and F. Kl\"ock, 2016, Multivariate transient price impact and matrix-valued positive definite functions, \emph{Mathematics of Operations Research} 41, 914--934; primary preprint arXiv:1310.4471.
'''
 if r'\bibitem[Li et al.(2024)]' not in s:s=s.replace(r'\end{thebibliography}',refs+'\n'+r'\end{thebibliography}')
 for old,new in {'version1':'version 1','CC BY4.0':'CC BY 4.0','CC BY-NC-SA4.0':'CC BY-NC-SA 4.0','Apache2.0':'Apache 2.0','75,72 and69':'75, 72 and 69','0.0010800,0.0007072 and0.0004148':'0.0010800, 0.0007072 and 0.0004148','30,90,180 and365-day':'30, 90, 180 and 365-day','All32':'All 32','adaptation0.01':'adaptation 0.01','capital100 and1,000':'capital 100 and 1,000','error0.1 with200':'error 0.1 with 200','SD0.003':'SD 0.003','margin0.25':'margin 0.25','cost0.02':'cost 0.02'}.items():s=s.replace(old,new)
 old='Existing expanding-date AR/VAR forecasts use training-only scaling and retain all contrasts; price-loss intervals include zero.'
 new='A fresh retrospective AR/VAR comparison now reconstructs this same sample, matching all 152 prior eligible segments and 844,621 baseline transitions. Training-only normalization and fitting precede six expanding evaluation dates, January 15--20, 2023. At lags one, two, three and six seconds, mean price-MSE reductions are 1.84275, 1.78394, 1.77683 and 1.75939 percent relative to AR. All four date-Student reference intervals are positive. With only six consecutive evaluation dates, retrospective choices and serial dependence, these are predictive associations rather than guaranteed confidence coverage or causal learning identification. Every lag and both price/flow loss targets are retained.'
 s=s.replace(old,new)
 # Retire duplicate prose from earlier spacing-sensitive insertion guards.
 for start,end in [('The three recorder CSVs match the Nielsen','Source metadata, hashes and licence texts accompany this revision.'),('The baseline recorder construction admits','rather than claiming complete-bin robustness.')]:
  match=re.search(re.escape(start)+r'.*?'+re.escape(end),s)
  if match:
   block=match.group()
   while s.count(block)>1:
    at=s.index(block,s.index(block)+len(block));s=s[:at]+s[at+len(block):]
 s=re.sub(r'(?<=[.!?]) {2,}', ' ',s)
 p.write_text(s)
 print('Finalized current-source interpretation and theorem/layout scope')
if __name__=='__main__':run()
