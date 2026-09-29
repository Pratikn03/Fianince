"""Generate static paper figures and complete tables from verified outputs."""
import argparse
from collections import Counter
import csv
from fractions import Fraction as F
import json
from pathlib import Path
from .model import Interval,sign,rules
from .run import HERE,decode_number,digest,rule_id,write_json
from .verify import read_checked

LABELS={'greedy':'Epsilon-greedy','softmax_1_10':'Softmax 0.10','softmax_1_4':'Softmax 0.25',
        'softmax_1_2':'Softmax 0.50','softmax_1':'Softmax 1.00','softmax_2':'Softmax 2.00'}
FAMILIES={'shadow_only':'Shadow only','active_shadow':'Active + shadow'}
METRICS=('profit0','profit1','customer_surplus','welfare','units')


def require_verification(report):
    if report.get('passed') is not True or report.get('clean_copy_reproduction') is not True:
        raise RuntimeError('completed clean verification required')


def chart_rows(summary):
    return [dict(rule=r['rule'],family=r['family'],kind=r['kind'],
                 count=r['strict_conflict'],denominator=r['n']) for r in summary['rows']
            if r['family']!='baseline' and r['kind'] in ('learning','interaction')]


def midpoint(x):
    value=decode_number(x)
    return float(value.mid() if isinstance(value,Interval) else value)


def number_fields(x):
    value=decode_number(x)
    if isinstance(value,F):
        return str(value),str(value),str(value),sign(value),abs(value)<=F(1,10**12)
    return '',str(value.lo),str(value.hi),sign(value),max(abs(F(value.lo)),abs(F(value.hi)))<=F(1,10**12)


def export_csv(rows,path):
    header=['state_id','family','offset','spread','ordering','rule','own_learning','rival_early','contrast','outcome']
    header += [f'{period}_{field}' for period in ('total','t0','t1') for field in ('exact','lower','upper','sign','near_zero_1e_12')]
    count=0
    with path.open('x',newline='') as f:
        w=csv.writer(f);w.writerow(header)
        for r in rows:
            s=r['state']
            for c in r['contrasts']:
                for i,metric in enumerate(METRICS):
                    line=[s['id'],s['family'],s['offset']['rational'],s['spread']['rational'],s['ordering'],
                          r['rule'],c['own_learning'],c['rival_early'],c['kind'],metric]
                    for vector in (c['total'],*c['periods']):
                        line.extend(number_fields(vector[i]))
                    w.writerow(line);count+=1
    assert count==39240
    return count


def render(results,verification,output):
    verified=json.loads(verification.read_text());require_verification(verified)
    if verified['result_summaries_sha256'].get(str(results.resolve()))!=digest(results/'summary.json'):
        raise RuntimeError('verification belongs to different result data')
    summary,rows=read_checked(results)
    output.mkdir(parents=True,exist_ok=False)
    charts=chart_rows(summary)
    write_json(output/'chart_data.json',charts)
    n=export_csv(rows,output/'all_contrasts.csv')
    lines=['# Robustness results: finite stipulated states, not trained populations','',
           'Generated from the verified 60-digit run. Positive private profit and negative',
           'gross welfare define a strict conflict. Each family/rule has 54 non-tied',
           'states; the original tied baseline is separate. The primary contrast has',
           'own learning off and rival learning on, with the rival waiting.', '',
           '| Rule | Initialization | Total conflict | Learning-interaction conflict | Other total sign pairs |',
           '|---|---|---:|---:|---|']
    ordered=[rule_id(*r) for r in rules()]
    for rule in ordered:
        for family in FAMILIES:
            a=next(x for x in summary['rows'] if (x['rule'],x['family'],x['kind'])==(rule,family,'learning'))
            b=next(x for x in summary['rows'] if (x['rule'],x['family'],x['kind'])==(rule,family,'interaction'))
            other=', '.join(f'{key}: {value}' for key,value in a['sign_pairs'].items() if key!='positive/negative') or 'None'
            lines.append(f"| {LABELS[rule]} | {FAMILIES[family]} | {a['strict_conflict']}/54 | {b['strict_conflict']}/54 | {other} |")
    lines+=['','Signs in the final column are profit/welfare. The learning interaction',
            'subtracts the frozen-rival deployment contrast. It is not a unique causal',
            'mediation estimate. No Monte Carlo sampling or confidence interval is involved.',
            '', '## Original tied baseline (not in the 54-case denominators)','',
            '| Rule | Gross profit change | Gross welfare change | Pure equilibrium at cost 0.05 | Planner |',
            '|---|---:|---:|---|---|']
    for rule in ordered:
        r=next(r for r in rows if r['rule']==rule and r['state']['family']=='baseline')
        c=next(c for c in r['contrasts'] if not c['own_learning'] and not c['rival_early'] and c['kind']=='learning')
        lines.append(f"| {LABELS[rule]} | {midpoint(c['total'][0]):+.8f} | {midpoint(c['total'][3]):+.8f} | {r['game']['certified_pure_equilibria']} | {r['game']['certified_planner_profiles']} |")
    lines+=['','Profiles use [dealer 0 early, dealer 1 early]; false means wait.',
            'Decimal displays are rounded; all numerical bounds are in the source JSON/CSV.',
            '', '## Costly deployment games over non-tied states','',
            '| Rule | Family | Unique pure NE outside planner set | Unique pure NE within planner set | Multiple pure NE | No certified pure NE | Unresolved comparisons |',
            '|---|---|---:|---:|---:|---:|---:|']
    games=[]
    for rule in ordered:
        for family in FAMILIES:
            count=Counter()
            for r in rows:
                if r['rule']!=rule or r['state']['family']!=family:continue
                g=r['game'];ne=g['certified_pure_equilibria'];planner=g['certified_planner_profiles']
                if g['unresolved_equilibrium_profiles'] or g['unresolved_planner_profiles']:count['unresolved']+=1
                if len(ne)==1:count['same' if ne[0] in planner else 'different']+=1
                elif len(ne)>1:count['multiple']+=1
                else:count['none']+=1
            games.append(dict(rule=rule,family=family,**count))
            lines.append(f"| {LABELS[rule]} | {FAMILIES[family]} | {count['different']} | {count['same']} | {count['multiple']} | {count['none']} | {count['unresolved']} |")
    lines+=['','Cost is a real resource cost of 1/20 per early dealer. Profits and welfare',
            'are net of that cost; learner rewards are not. All four feasible profiles',
            'are compared. Multiple pure equilibria are not resolved by selecting a',
            'favorable one; no mixed-equilibrium calculation is claimed.',
            '', '## Complete sign inventory','',
            '| Rule | Family | Contrast | Denominator | Profit/welfare signs and counts |',
            '|---|---|---|---:|---|']
    for r in summary['rows']:
        signs=', '.join(f'{k}: {v}' for k,v in r['sign_pairs'].items())
        lines.append(f"| {LABELS[r['rule']]} | {r['family']} | {r['kind']} | {r['n']} | {signs} |")
    with (output/'RESULTS.md').open('x') as f:f.write('\n'.join(lines)+'\n')
    write_json(output/'game_counts.json',games)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.labelcolor':'#252525','text.color':'#252525'})
    colors={'learning':'#285A83','interaction':'#C78425'}
    fig,axes=plt.subplots(1,2,figsize=(12,5),sharex=True,sharey=True)
    for ax,family in zip(axes,FAMILIES):
        for shift,kind,label in ((-.18,'learning','Total conflict'),(.18,'interaction','Learning-interaction conflict')):
            values=[next(x['count'] for x in charts if (x['rule'],x['family'],x['kind'])==(r,family,kind)) for r in ordered]
            bars=ax.barh([i+shift for i in range(6)],values,height=.33,color=colors[kind],label=label,
                         hatch='' if kind=='learning' else '//',edgecolor='white',linewidth=.5)
            for bar,val in zip(bars,values):
                ax.text(val+.4,bar.get_y()+bar.get_height()/2,str(val),va='center',fontsize=9)
        ax.set_title(FAMILIES[family]);ax.set_yticks(range(6),[LABELS[r] for r in ordered])
        ax.set_xlim(0,60);ax.set_xticks((0,18,36,54));ax.set_xlabel('States with profit > 0 and welfare < 0 (out of 54)')
        ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    axes[0].invert_yaxis();handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=2,bbox_to_anchor=(.5,.06),frameon=False)
    fig.suptitle('Initialization and smooth-choice robustness',fontsize=16,x=.5,y=.97)
    fig.text(.5,.025,'H = 2; own learning frozen; rival waits. Grid counts are not population frequencies.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.14,1,.92));fig.savefig(output/'robustness_counts.png',dpi=180);plt.close(fig)

    fig,axes=plt.subplots(2,3,figsize=(12,8),sharex=True,sharey=True)
    points=[]
    for ax,rule in zip(axes.flat,ordered):
        for family,marker,color,fill in (('shadow_only','o','#285A83',True),('active_shadow','^','#C78425',False)):
            subset=[r for r in rows if r['state']['family']==family and r['rule']==rule]
            cc=[next(c for c in r['contrasts'] if not c['own_learning'] and not c['rival_early'] and c['kind']=='learning') for r in subset]
            xx=[midpoint(c['total'][0]) for c in cc];yy=[midpoint(c['total'][3]) for c in cc]
            ax.scatter(xx,yy,marker=marker,s=30,facecolors=color if fill else 'none',edgecolors=color,
                       linewidths=.9,label=FAMILIES[family],alpha=.75)
            points.extend(dict(rule=rule,state=r['state']['id'],family=family,profit=x,welfare=y)
                          for r,x,y in zip(subset,xx,yy))
        ax.axhline(0,color='#666666',lw=.8);ax.axvline(0,color='#666666',lw=.8)
        ax.set_title(LABELS[rule]);ax.grid(alpha=.12)
    for ax in axes[1]:ax.set_xlabel('Total focal profit change (model units)')
    for ax in axes[:,0]:ax.set_ylabel('Total welfare change (model units)')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=2,bbox_to_anchor=(.5,.055),frameon=False)
    fig.suptitle('Private incentive versus gross welfare',fontsize=16,y=.98)
    fig.text(.5,.025,'Each panel includes all 108 non-tied cases; coincident points overlap. Common axes; no sampling intervals.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.12,1,.94));fig.savefig(output/'profit_welfare.png',dpi=180);plt.close(fig)
    write_json(output/'scatter_data.json',points)
    write_json(output/'manifest.json',dict(result_summary_sha256=digest(results/'summary.json'),
                 verification_sha256=digest(verification),renderer_sha256=digest(Path(__file__)),
                 csv_rows=n,chart_points=len(points),matplotlib_version=matplotlib.__version__,
                 files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results',type=Path,default=HERE/'results/reviewed_p60')
    p.add_argument('--verification',type=Path,default=HERE/'verification/reviewed/report.json')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();render(a.results.resolve(),a.verification.resolve(),a.output.resolve())
