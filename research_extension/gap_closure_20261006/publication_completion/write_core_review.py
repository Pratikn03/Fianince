"""Single-file editable specialist packet for the fully specified central results."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def run():
 header=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[margin=1in]{geometry}\usepackage{amsmath,amssymb,amsthm}
\usepackage[round]{natbib}\usepackage[colorlinks=true,urlcolor=blue]{hyperref}
\newtheorem{theorem}{Theorem}[section]\newtheorem{proposition}[theorem]{Proposition}\newtheorem{lemma}[theorem]{Lemma}
\title{Memory Identification under Probing and Capital Constraints}
\author{Pratik Niroula and Prashant Niroula}
\date{October 8, 2026}
\begin{document}\maketitle
\noindent This standalone review packet contains the current central proofs. It is a conditional theoretical result and an independent-review candidate, not a novelty, market-calibration or publication certification.
\section{Declared Model and Observation Contract}
Use a price-first positive cohort economy:
\[
x_{t+1}=a x_t+\kappa\sum_iq_i y_{i,t}+\kappa v_t,
\qquad y_{i,t+1}=(1-\eta_i)y_{i,t}+\eta_i x_{t+1}.
\]
Here $0\le a<1$, $\kappa>0$, $q_i\ge0$, $\eta_i\in(0,1)$, and $S=a+\kappa\sum_iq_i<1$. All states reset to zero. With $z=(x,y_1,\ldots,y_K)$, the transition has price row $(a,\kappa q_1,\ldots,\kappa q_K)$ and cohort row $i$ equal to $\eta_i$ times that row plus $1-\eta_i$ in its own coordinate. The execution input is $H=\kappa(1,\eta_1,\ldots,\eta_K)^\top$; the price selector is $e_x^\top$.

The statistical pair has known common $a,\kappa,q,\eta$: one weight$q$ at rate$\eta$ versus two weights$q/2$ at rates$\eta\pm\delta$. The first two results have no process noise and independent centered Gaussian observation noise of variance$\sigma^2>0$. The last result deliberately changes the process-noise contract. No unknown-mixture, participant-identity or feedback-adaptive optimality assertion is made.
\section{Resource and Financial Results}
'''
 refs=r'''\begin{thebibliography}{9}
\bibitem[Almgren and Chriss(2001)]{almgren2000}Almgren, R., and N. Chriss, 2001, Optimal execution of portfolio transactions, Journal of Risk 3, 5--39. Primary December 2000 manuscript also available at \url{https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf}.
\bibitem[Manole and Ho(2022)]{manoleho2022}Manole, T., and N. Ho, 2022, Refined convergence rates for maximum likelihood estimation under finite mixture models, PMLR 162, 14979--15006.
\bibitem[Liu and Ammari(2023)]{liuammari2023}Liu, P., and H. Ammari, 2023, Super-resolution of positive near-colliding point sources, Information and Inference 12, 3087--3111; primary preprint arXiv:2212.00536.
\bibitem[Sornette et al.(2023)]{sornette2023nonnormal}Sornette, D., S. Lera, J. Lin, and K. Wu, 2023, Non-normal interactions create socio-economic bubbles, arXiv:2205.08661v5.
\end{thebibliography}\end{document}
'''
 bodies='\n\n'.join((HERE/n).read_text() for n in ['resource_frontier.tex','capital_frontier.tex','trader_capital_frontier.tex','natural_excitation_boundary.tex'])
 target=HERE/'Machine_Markets_Central_Result_Review_20261008.tex';target.write_text(header+bodies+'\n'+refs)
 print(target)
if __name__=='__main__':run()
