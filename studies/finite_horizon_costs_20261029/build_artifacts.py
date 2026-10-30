"""Build the checked appendix, notebook, and existing-paper source integration."""
from pathlib import Path
import argparse,base64,hashlib,json,re,shutil,zipfile,io,subprocess,collections
import pandas as pd

HERE=Path(__file__).resolve().parent
BEGIN='% BEGIN FINITE HORIZON COST 20261029'
END='% END FINITE HORIZON COST 20261029'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strip(s):return re.sub(re.escape(BEGIN)+'.*?'+re.escape(END)+'\n*','',s,flags=re.S)
def write_block(path,block):
    s=strip(path.read_text());path.write_text(s.replace('\\end{document}',BEGIN+'\n'+block+'\n'+END+'\n\n\\end{document}'))

def results_tex(result):
    t=pd.read_csv(result/'primary_decisions.csv');s=json.loads((result/'primary_summary.json').read_text())
    h=pd.read_csv(result/'hard_pair_requirements.csv');f=pd.read_csv(result/'assumption_failures.csv')
    names={'functional':'Finite-horizon certificate','linear_functional_projection':'Standard Gaussian projection',
       'ellipsoid':'Full-response ellipsoid','point':'Point estimate (uncertified)',
       'no_data_robust':'No data, zero violations','no_data_same_gamma':'Best no data, same error budget',
       'oracle_response':'Response oracle, zero violations','oracle_same_gamma':'Response oracle, same error budget',
       'targeted_gain_disclosure':'Exact gain report, fee 0.05'}
    z=r'''\section*{Checked synthetic financial illustration}
This illustration uses the frozen primary design and the stronger comparison
recorded in the design amendment. It is exploratory and was developed after
the earlier project runs; it is not independent preregistration or replication.
The two-cohort primary has $a=0.4$, $\kappa=1$, $Q=0.4$, rates
$0.49,0.51$, and equal weights. The known class cap is $\overline Q=0.55$;
$H=60$ one-minute model periods, $N=32$, $\sigma=0.02$, and
$\gamma=0.025$. Initial wealth is 1,000, price 100, stress budget 1,
and flow bound 0.04. The service fee is 0.08 per unit. Execution costs are
$0.002I+0.0002I^2$ and carry is charged at 5 percent annualized.
The assumed all-in reset fee is 0.002, so the learning bill is 0.064.
These are hypothetical model dollars, not an exchange calibration or returns.
The same-error-budget no-data lottery is a theoretical strongest comparator,
not a proposed desk practice. The zero-violation comparisons are also shown.

\begin{center}\footnotesize
\begin{tabular}{p{0.43\textwidth}rrr}
\toprule
Policy & Mean units & Net expected profit & Unsafe reserve (\%)\\
\midrule
'''
    order=['no_data_robust','no_data_same_gamma','functional','linear_functional_projection','ellipsoid','point','targeted_gain_disclosure','oracle_response','oracle_same_gamma']
    for p in order:
        x=t[t.policy==p].iloc[0]
        z+=f"{names[p]} & {x.units:.3f} & {x.net_value_integral:.4f} & {100*x.reserve_violation_rate:.2f}\\\\\n"
    z+=r'''\bottomrule\end{tabular}\end{center}
Profit integrates the future zero-mean flow model and every declared cost;
the data-dependent policy values are also integrated over reading noise by
one-dimensional Gaussian quadrature. Mean units and empirical reserve
violations use 20,000 synthetic reading draws. Oracle and no-data lottery
values are analytic. A reserve violation means some bounded future path can
exceed the budget, not that a sampled market path actually did so.
The 97.5 percent safety statement is over measurement draws for a single
future commitment; it is not certainty, market-wide stability, or time-uniform
coverage. The point rule buys slightly more expected profit by violating the
same risk requirement and is not a valid superiority comparison.
The proposed estimator and standard Gaussian projection coincide exactly.
'''
    b=s['guarantees']
    z+=f"\nThe net information advantage over the strongest same-error-budget no-data rule is {s['expected_information_gain']:.4f}. The written theorem's sufficient lower bound is {b['net_information_value_lower']:.4f}, strictly positive even after all costs. At the limiting merged economy the lower bound is {s['limiting_merged_net_value_lower']:.4f}; continuity therefore supports the small-separation corollary. These bounds are evaluated in floating point with a wide positive margin, not claimed interval-arithmetic certificates.\n"
    z+=r'''\begin{center}\small\begin{tabular}{rrr}
\toprule
Separation $\delta$ & Known-pair resets required & Implied fee bill\\
\midrule
'''
    for _,x in h.iterrows():z+=f"{x.delta:.4f} & {x.N_required:.3g} & {x.information_cost_lower:.3g}\\\\\n"
    z+=r'''\bottomrule\end{tabular}\end{center}
The known-pair test receives all 60 taps, exactly as the financial rule does.
Response differences are calculated in rational arithmetic before conversion
to floating point. The sample threshold is the Gaussian testing formula, not
a measured runtime or an asserted physical trading-capital requirement.
For the primary $\delta=0.01$, distinguishing the two already-known
alternatives requires about 191 million resets at 5 percent error. Even
this optimistic information fee is far beyond the unit stress budget.
Identifying arbitrary cohorts cannot be easier than this embedded test under
the same fixed query contract. Other experimental designs are not covered.
'''
    z+=f"\nAt fixed $N=32$, the expected net benefit crosses zero at an illustrative reset price of about {s['per_reset_break_even']:.6f}. An exact scalar gain report is worth purchasing only below a fee of about {s['exact_gain_disclosure_break_even']:.6f} in this example. These are computed break-even prices, not observed reporting costs.\n"
    z+=r'''\paragraph{Failures retained.}
The full output includes all 819 cost, horizon and service-fee sensitivity
rows, including negative values and unaffordable information budgets.
A low service premium or expensive measurements can make abstaining from
data acquisition preferable. Independent checks cover 13 algebra, optimizer,
shock-corner, cash-flow and Gaussian-testing properties, including the
same-error-budget no-data optimum checked against a separate linear program.
An initial low-premium LP check was affected by the solver's absolute
objective tolerance; rescaling the objective resolved it, and that failed
log is retained. This is not independent mathematical proof review.

\begin{center}\footnotesize\begin{tabular}{p{0.52\textwidth}rr}
\toprule
Reading/model contract & Gain coverage (\%) & Unsafe reserve (\%)\\
\midrule
'''
    labels={'iid_valid':'Independent Gaussian, valid','correlated_iid_formula_invalid':'Correlated taps, wrong variance','correlated_corrected_variance':'Correlated taps, correct variance','negative_reading_bias_invalid':'Negative reading bias, invalid','future_feedback_change_invalid':'Future feedback changes, invalid'}
    for case,label in labels.items():
        x=f[f.case==case].iloc[0];z+=f"{label} & {100*x.gain_coverage:.2f} & {100*x.reserve_violation_rate:.2f}\\\\\n"
    z+=r'''\bottomrule\end{tabular}\end{center}
The valid Gaussian row has finite Monte Carlo variation around its nominal
97.5 percent coverage. Using the correct correlated variance restores the
specified measurement contract at the cost of a larger margin. Bias or
future parameter change is not repaired by a larger sample under the wrong
model. A signed kernel such as $(1,-0.9)$ has sum $0.1$ and absolute sum
$1.9$, so positivity is indispensable to using the plain sum. The same
certificate used repeatedly without correction does not retain its
one-decision guarantee.

\paragraph{What changed economically.}
In this model, the desk can choose a larger inventory commitment while
paying for information and retaining the same permitted unsafe-action
probability as its strongest no-data comparator. This is an example of
positive decision value, not evidence that information always pays, that
trading strategies must be identified, or that a real venue's liquidity and
welfare improve. Realistic observation costs and a public-data bridge remain
requirements for an empirical finance claim.
'''
    return z

def make_notebook(package,out):
    names=['model.py','run.py','test_theory.py','PROTOCOL.md','DESIGN_AMENDMENT.md','PROOF.tex','LITERATURE.md','README.md']
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for name in names:z.writestr(name,(package/name).read_bytes())
    payload=buf.getvalue();enc=base64.b64encode(payload).decode();expected=hashlib.sha256(payload).hexdigest()
    import numpy,scipy,pandas,matplotlib
    pins=f'numpy=={numpy.__version__} scipy=={scipy.__version__} pandas=={pandas.__version__} matplotlib=={matplotlib.__version__}'
    intro='''# Machine Markets: finite-horizon information and net decision value
Run all cells on a CPU. This is a NEW experiment, separate from the earlier
expected-log investor notebook. It tests the written cost-aware inventory-
service theorem. All outcomes are synthetic. It does not establish novelty,
independent proof review, real-market stability, or a full Lean proof.

The same-error-budget no-data comparator is included. The direct certificate
equals standard Gaussian projection; no new estimator is claimed. The last
cell downloads a ZIP containing every result, negative cases, source snapshot,
checks and hashes. Upload that ZIP for review. Do not describe these numbers
as observed exchange results.
'''
    code1=f'''import base64, hashlib, io, os, pathlib, subprocess, sys, zipfile\nfrom datetime import datetime, timezone\nif os.environ.get("MM_SKIP_INSTALL") != "1":\n    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + {pins!r}.split())\nembedded = base64.b64decode({enc!r})\nassert hashlib.sha256(embedded).hexdigest() == {expected!r}\nwork = pathlib.Path.cwd() / "finite_horizon_cost_separation"\nwork.mkdir(exist_ok=True)\nwith zipfile.ZipFile(io.BytesIO(embedded)) as z:\n    for n in z.namelist():\n        assert not pathlib.PurePosixPath(n).is_absolute() and ".." not in pathlib.PurePosixPath(n).parts\n    z.extractall(work)\nprint("Verified source package:", {expected!r})\n'''
    code2='''profile = os.environ.get("MM_PROFILE", "full")
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
result_dir = pathlib.Path.cwd() / ("Cost_Separation_Results_" + stamp)
cmd = [sys.executable, str(work / "run.py"), "--profile", profile,
       "--seed", "20261030", "--out", str(result_dir)]
run = subprocess.run(cmd, cwd=work, text=True, capture_output=True)
print(run.stdout)
print(run.stderr[-5000:])
assert run.returncode == 0, "Execution failed; preserve the output folder and log."
archive = result_dir.with_suffix(".zip")
assert archive.is_file()
import json
with zipfile.ZipFile(archive) as z:
    manifest = json.loads(z.read("manifest.json"))
    for name, digest in manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest() == digest
print("Verified return ZIP:", archive)
'''
    code3='''try:
    from google.colab import files
except ImportError:
    print("Local run: download", archive)
else:
    files.download(str(archive))
'''
    def cell(kind,text,n):
        v=dict(cell_type=kind,id=f'cost-separation-{n}',metadata={},source=text.splitlines(keepends=True))
        if kind=='code':v.update(execution_count=None,outputs=[])
        return v
    nb=dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3',language='python'),colab=dict(name='Machine_Markets_Cost_Separation.ipynb')),cells=[cell('markdown',intro,0),cell('code',code1,1),cell('code',code2,2),cell('code',code3,3)])
    (out/'Machine_Markets_Cost_Separation.ipynb').write_text(json.dumps(nb,indent=1)+'\n')
    (package/'Cost_Separation_Run_and_Return.ipynb').write_text(json.dumps(nb,indent=1)+'\n')
    (package/'EMBEDDED_SOURCE.json').write_text(json.dumps(dict(sha256=expected,files=names,pins=pins),indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();repo=args.repo.resolve();result=args.result.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    status=json.loads((result/'run_status.json').read_text());assert status['status']=='COMPLETED_SYNTHETIC' and status['tests_returncode']==0
    (HERE/'RESULTS.tex').write_text(results_tex(result))
    package=repo/'studies/finite_horizon_costs_20261029';package.mkdir(parents=True,exist_ok=True)
    for f in HERE.iterdir():
        if f.is_file() and f.suffix in {'.py','.md','.tex'}:shutil.copyfile(f,package/f.name)
    shutil.copytree(HERE/'validation',package/'validation',dirs_exist_ok=True)
    dst=package/'results/final_full_20261030';shutil.copytree(result,dst,dirs_exist_ok=True)
    shutil.copyfile(result.with_suffix('.zip'),package/'results/final_full_20261030.zip')
    make_notebook(package,out)
    body=(HERE/'PROOF.tex').read_text()+'\n'+(HERE/'RESULTS.tex').read_text()
    # Preserve existing blocks exactly; the new appendix is explicitly scoped.
    edited=[];before={}
    files=['ceiling_suite/papers/paper1/paper1.tex','ceiling_suite/papers/paper2/paper2.tex','ceiling_suite/paper1/paper1.tex','ceiling_suite/paper2/paper2.tex','ceiling_suite/papers/versions/Paper1_QE.tex','ceiling_suite/papers/versions/Paper2_JF.tex','ceiling_suite/papers/flagship/identify_certify.tex','ceiling_suite/papers/paper1/p1_appendix.tex','ceiling_suite/papers/paper2/p2_appendix.tex','ceiling_suite/paper1/p1_appendix.tex','ceiling_suite/paper2/p2_appendix.tex']
    for name in files:
        path=repo/name;before[name]=strip(path.read_text());write_block(path,body);edited.append(name)
    # A single thesis appendix avoids repeating the new result in both chapters.
    name='thesis/thesis.tex';path=repo/name;before[name]=strip(path.read_text());s=before[name]
    th=body.replace('\\section*{Finite-horizon information, cohort ambiguity, and net inventory-service value}','\\chapter{Finite-horizon information and net inventory-service value}',1)
    anchor='\\chapter*{Bibliography for Chapters~1, 4 and 5}'
    assert anchor in s;path.write_text(s.replace(anchor,BEGIN+'\n'+th+'\n'+END+'\n\n'+anchor));edited.append(name)
    path=repo/'thesis/make_chapters.py';s=path.read_text()
    if 'FINITE HORIZON COST' not in s:
        anchor='    body = s[s.index("\\\\begin{document}")';at=s.index(anchor)
        s=s[:at]+'    s = re.sub(r"% BEGIN FINITE HORIZON COST 20261029.*?% END FINITE HORIZON COST 20261029", "", s, flags=re.S)\n'+s[at:];path.write_text(s)
    preservation=[]
    for name,old in before.items():
        new=(repo/name).read_text();counts={}
        for env in ['theorem','lemma','proposition','corollary','proof','tabular','longtable']:
            pat=r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}'
            a=collections.Counter(hashlib.sha256(x.encode()).hexdigest() for x in re.findall(pat,old,re.S));b=collections.Counter(hashlib.sha256(x.encode()).hexdigest() for x in re.findall(pat,new,re.S))
            assert not a-b,(name,env);counts[env]=sum(a.values())
        preservation.append(dict(path=name,retained_original_blocks=counts))
    (package/'validation/original_blocks_retained.json').write_text(json.dumps(preservation,indent=2)+'\n')
    (out/'source_edits.json').write_text(json.dumps(edited+['thesis/make_chapters.py'],indent=2)+'\n')
    print('Integrated the scoped appendix into existing papers and generated the source-checked Colab.')

if __name__=='__main__':main()
