#!/usr/bin/env python3
"""Rebuild separate figures from archived results; no synthetic result generation."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def load_csv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))

def save(fig, out, stem):
    fig.tight_layout()
    fig.savefig(out / f'{stem}.png', dpi=180)
    fig.savefig(out / f'{stem}.pdf')
    plt.close(fig)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--results', type=Path, default=ROOT/'results')
    p.add_argument('--output', type=Path, default=ROOT/'figures')
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    path_rows = load_csv(args.results/'witness_impulses.csv')
    t = np.array([int(r['t']) for r in path_rows])
    fig, ax = plt.subplots(figsize=(8.0,4.7))
    keep = t <= 100
    for key, label, ls in [('stable','Stable adaptive market','-'),
                            ('unstable','Unstable adaptive market','--'),
                            ('frozen_learning','Frozen-learning control',':')]:
        ax.plot(t[keep], np.array([float(r[key]) for r in path_rows])[keep],
                label=label, linestyle=ls, linewidth=2)
    ax.set(xlabel='Model time step (not calendar time)', ylabel='Price response to unit impulse',
           title='Identical first four coefficients; different long-run stability')
    ax.legend(frameon=False)
    save(fig,args.output,'matched_market_impulses')
    w = json.loads((args.results/'readable_witness.json').read_text())
    from fractions import Fraction
    rs = np.array([float(Fraction(x)) for x in w['nodes']])
    j = np.arange(60)
    fig, ax = plt.subplots(figsize=(8.0,4.7))
    for key,label,ls in [('q_minus','Stable market','-'),('q_plus','Unstable market','--')]:
        q = np.array([float(Fraction(x)) for x in w[key]])
        k = np.sum((q*(1-rs))[:,None]*rs[:,None]**j[None,:],axis=0)
        ax.plot(j,k,label=label,linestyle=ls,linewidth=2)
    ax.set(xlabel='Kernel lag',ylabel='Feedback-kernel coefficient',
           title='A slowly decaying hidden feedback tail')
    ax.legend(frameon=False)
    save(fig,args.output,'hidden_feedback_kernel')
    rows = load_csv(args.results/'comparison_summary.csv')
    fig, ax = plt.subplots(figsize=(8.0,4.7))
    for noise,ls in [(0,'-'),(1,'--')]:
        for method,marker,label in [('rate_aware','o','Rate-aware'),('no_floor','s','No rate floor')]:
            r=[x for x in rows if int(x['noise_id'])==noise and x['method']==method]
            ax.plot([int(x['H']) for x in r],[100*float(x['decision_fraction']) for x in r],
                    marker=marker,linestyle=ls,label=f'{label}; noise {float(r[0]["relative_sigma"]):g}')
    ax.set_xscale('log',base=2)
    ax.set_xticks([4,16,64,256],['4','16','64','256'])
    ax.set(xlabel='Observed kernel horizon H',ylabel='Datasets receiving a decisive label (%)',
           title='Decision coverage under valid measurement assumptions',ylim=(0,100))
    ax.legend(frameon=False,fontsize=9)
    save(fig,args.output,'decision_coverage')
    fig, ax = plt.subplots(figsize=(8.0,4.7))
    for method,marker,label in [('rate_aware','o','Rate-aware interval'),('truncation','s','Truncated sum'),
                                ('one_rate','^','Two-tap one-rate fit'),('matrix_pencil','D','Matrix pencil (32-tap cap)')]:
        r=[x for x in rows if int(x['noise_id'])==0 and x['method']==method]
        ax.plot([int(x['H']) for x in r],[100*float(x['wrong_stable_fraction']) for x in r],
                marker=marker,label=label)
    ax.set_xscale('log',base=2)
    ax.set_xticks([4,16,64,256],['4','16','64','256'])
    ax.set(xlabel='Available kernel horizon H',ylabel='Unstable cases incorrectly labeled stable (%)',
           title='Low-noise panel: false reassurance versus abstention',ylim=(-2,80))
    ax.legend(frameon=False,fontsize=9)
    save(fig,args.output,'false_stable_comparison')
    print(f'Wrote four figures in PNG and PDF formats to {args.output}')

if __name__ == '__main__':
    main()
