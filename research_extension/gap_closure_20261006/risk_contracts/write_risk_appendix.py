from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def build():
    s=(HERE/'risk_results.tex').read_text();d=json.loads((HERE/'risk_results.json').read_text());rows=[]
    for key,label in [('hedged_portfolio','Hedged'),('structural_market_family','Directed market'),('symmetric_impact_family','Symmetric impact')]:
        for r in d[key]:rows.append([label,f"{r['theta']:.1f}",f"{r['rho']:.6f}",r['peak_step'],f"{r['M_C']:.6f}",f"{r['safe_radius_B1']:.6f}",f"{r['tail_upper']:.3g}"])
    s+='\n\\begin{table}[htbp]\n\\centering\\small\n\\caption{Constructed fixed-coordinate examples, budget one in declared output units. The tail certificate bounds all times after the 150-step search; market calibration is not asserted.}\\label{tab:risk_contract_examples}\n\\begin{adjustbox}{max width=\\textwidth}\n\\begin{tabular}{lrrrrrr}\\toprule\n'
    s+=r'Family & Coupling & $\rho$ & Peak & $M_C$ & $1/M_C$ & Tail upper\\\midrule'+'\n'
    s+='\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)
    s+='\n\\bottomrule\\end{tabular}\n\\end{adjustbox}\n\\end{table}\n'
    s+='The directed-market spectral radius comes from its unchanged diagonal blocks; the symmetric-impact family uses similarity to its coupling-one matrix. Full-matrix floating-point eigenvalues are also retained digitally, because repeated eigenvalues can show small numerical discrepancies. Both families use fixed coordinates, the same initial-state ball within each family, and their stated output operators. These calculations illustrate the proved distinctions; they do not estimate real cross-impact or actual dealer safety.\n'
    return s
if __name__=='__main__':(HERE/'risk_appendix.tex').write_text(build());print('Generated risk-contract appendix')
