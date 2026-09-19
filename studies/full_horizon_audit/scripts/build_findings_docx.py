#!/usr/bin/env python3
"""Build the human-readable research findings. Optional dependency: python-docx."""
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
d=Document();s=d.sections[0]
s.page_width=Inches(8.5);s.page_height=Inches(11)
s.top_margin=Inches(.7);s.bottom_margin=Inches(.65);s.left_margin=s.right_margin=Inches(.75)
s.header_distance=Inches(.28);s.footer_distance=Inches(.28)
normal=d.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(11)
normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.10
for n,size in [('Title',27),('Heading 1',18),('Heading 2',12.5)]:
 st=d.styles[n];st.font.name='Calibri';st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string('16324F');st.paragraph_format.space_after=Pt(7)
 st.paragraph_format.keep_with_next=True
h=s.header.paragraphs[0];h.text='MACHINE MARKETS  /  RESEARCH AUDIT V2';h.style='Caption';h.runs[0].font.size=Pt(9)
f=s.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=f.add_run('18 September 2026  •  ');r.font.size=Pt(9)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');f._p.append(fld)
d.core_properties.title='Hidden Slow Learners: Full-Horizon Findings and Next Steps'
d.core_properties.subject='Executed comparison, measurement limits, novelty boundary and reproduction'
d.core_properties.author=''
def p(text,bold=False,style=None):
 q=d.add_paragraph(style=style);r=q.add_run(text);r.bold=bold;return q
def h1(text):d.add_heading(text,1)
def h2(text):d.add_heading(text,2)
def page():d.add_page_break()
def table(headers,rows,widths):
 t=d.add_table(rows=1,cols=len(headers));t.autofit=False
 for i,(x,w) in enumerate(zip(headers,widths)):
  t.columns[i].width=Inches(w);t.rows[0].cells[i].width=Inches(w);t.rows[0].cells[i].text=x
 for cell in t.rows[0].cells:
  shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EFF5');cell._tc.get_or_add_tcPr().append(shade)
  for rr in cell.paragraphs[0].runs:rr.bold=True;rr.font.size=Pt(10)
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  cells=t.add_row().cells
  for i,(x,w) in enumerate(zip(row,widths)):
   cells[i].width=Inches(w);cells[i].text=str(x)
   for par in cells[i].paragraphs:
    par.paragraph_format.space_after=Pt(5);par.paragraph_format.space_before=Pt(5)
    for rr in par.runs:rr.font.size=Pt(10)
 for row in t.rows:
  ns=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(ns)
 return t
p('EXECUTED RESEARCH • FINDINGS & NEXT STEPS',style='Subtitle')
d.add_heading('Hidden Slow Learners',0)
p('The full-horizon test changes the conclusion',bold=True)
p('The strongest supported result is a measurement requirement in a restricted model—not superiority of the original diagnostic. Conventional positive-mixture bounds use the full observed response more effectively than the earlier summary formula on this benchmark.')
h2('Primary comparison: all 256 observed response coefficients')
p('Each noise condition contains 10,800 independently generated measurement-noise vectors. All methods receive the same data, known noise level and valid learning-rate floor. No method receives hidden rates, weights, component count or truth.')
table(['Method','Lower noise: decided / wrong','Higher noise: decided / wrong'],[
('Original summary bound','8,930 (82.69%) / 0','7,150 (66.20%) / 0'),
('Full-horizon positive NNLS fit','10,800 (100%) / 24','10,800 (100%) / 306'),
('Full-moment positive LP bounds','9,508 (88.04%) / 0','8,278 (76.65%) / 4')],[2.5,2.25,2.25])
p('“Decided” means a stable or unstable label. Conflicts and inconclusive outcomes remain in the denominator. The NNLS fit is a point estimate, not a confidence certificate.',style='Caption')
h2('What changed scientifically')
p('The conventional bounds produce 578 more decisions at lower noise and 1,128 more at higher noise: gains of 5.35 and 10.44 percentage points. They are not better on every dataset; some earlier decisions become conflicts. At higher noise, four confident labels are wrong versus zero for the original bound.')
p('The new research direction is: What measurements and precision are necessary to justify a stability decision when slow adaptive feedback may be hidden?',bold=True)
p('Evidence status: synthetic controlled measurements and model-specific proofs. No real-market validation, trained AI agents, outside proof approval, or independent external reproduction is claimed.',style='Caption')

page();h1('1. What the result means')
h2('A plausible fitted model is not proof of safety')
p('A positive fit can match observed responses closely while leaving other compatible positive models on the opposite side of the stability boundary. A confidence-set method instead asks whether every compatible model is stable, every one is unstable, or the evidence cannot decide. This distinction is established in data-informativity research; it is not new to this project [1].')
h2('The hidden slow-feedback example')
p('The new example uses two adaptive memory states in each model. Both share the same learning rates. The first has total normalized feedback 0.9 and is stable; the other has feedback 1.1 and is unstable. Their separation from the boundary remains fixed. Only the slow response rate becomes very small.')
p('For a slow rate of 0.00001, 256 observed taps and the declared higher-noise measurement precision, even an oracle told both complete candidate models has a best possible forced-classification error of 49.64%. A generic estimator with less information cannot do better on this pair.')
table(['Quantity','Constructed example'],[
('Stable / unstable normalized feedback','0.9 / 1.1'),
('Number of hidden adaptive states','2 in each model'),
('Best forced error with 256 taps','49.64%'),
('Maximum decision coverage if unconditional error is ≤5%','10.72%'),
('Oracle error with infinitely many equally noisy taps','44.97%')],[3.65,3.35])
p('The coverage ceiling is a necessary bound, not a promise that a procedure attains it. These are mathematical examples—not measured financial-crisis probabilities.',style='Caption')
h2('The practical implication')
p('More observations do not automatically solve every slow-memory problem. Measurement precision, excitation and validated restrictions on the unseen response matter. A rate floor is one useful assumption, not the only possible remedy and not sufficient at every noise level. The experiment assumes direct kernel measurements; ordinary price data do not automatically provide them.')

page();h1('2. What was executed and verified')
table(['Work completed','Evidence'],[
('Full measurement reconstruction','21,600 vectors × 256 taps = 5,529,600 responses. Every prior saved input matched exactly.'),
('Equal-information primary comparison','86,400 paired rows across four horizons; the full 256-tap result is the primary endpoint.'),
('Predetermined resolution checks','5,400 additional estimator runs on 1,080 selected vectors. No new independent data are implied.'),
('Exact proof examples','112 rational pairs plus one readable witness rechecked with Fraction arithmetic.'),
('Alternate numerical route','216 cases checked with separately constructed constraints and HiGHS interior point. Maximum bound difference: 5.62 × 10⁻⁹.'),
('Confidence-event audit','82,364 on-event rows; every LP interval contains the true feedback gain.'),
('Fixed-order testing calculation','60 parameter settings; 12,000,000 projected likelihood-ratio draws, not market simulations.'),
('Complete clean-directory rerun','All 86,400 rows reproduced. All 33 non-timing fields match; numeric differences are zero in this environment.')],[2.35,4.65])
h2('The four wrong confident labels were investigated')
p('All four occurred at higher noise and H = 256. Two falsely called unstable models stable; two did the reverse. In every case, the simultaneous confidence event failed: the declared uncertainty intervals missed at least one true response feature. None was an on-event violation of the mathematical inclusion argument.')
p('The simultaneous event held for 95.33% of the 21,600 vectors, compared with its nominal lower bound of 95%. This is a finite-family, unconditional probability statement under the assumed Gaussian model—not a promise of zero errors or an error rate conditional on deciding.')
p('The separate verifiers and clean rerun were all executed in the same environment. They establish internal repeatability, not external independent replication.',bold=True)

page();h1('3. Novelty and proof review')
h2('The strongest existing work narrows the claim')
table(['Existing research','Consequence for this paper'],[
('Data informativity [1]','The distinction between one fitted system and a property shared by all compatible systems already exists.'),
('Positive identification [2]','Nonnegative/internal-positive identification is established. Our NNLS and LP are not the first positive estimators.'),
('Gain side-information and long memory [3]','The link between slow impulse responses, total gain and useful side information is already studied.'),
('Convex moment bounds [4]','Optimizing a quantity over positive measures subject to finite observations is a classical approach.'),
('Two-point statistical testing [5]','The Gaussian lower-bound technique is established. Our contribution is its explicit specialization and audit.'),
('Adaptive-agent market models [6]','Feedback between learning and market outcomes is not a newly discovered finance mechanism.')],[2.7,4.3])
h2('What may remain publishable')
p('A defensible paper could connect a precise observation budget to stability decisions in a financially meaningful setting, with a sharp theorem, an equally informed benchmark and a realistic measurement protocol. The current package supplies a restricted building block and evidence that prevents an overstated method claim.')
h2('What is not established')
p('Global originality, a new finance law, a paradigm shift, optimality among all conventional estimators, a real-market crisis predictor, and independent outside replication are not established. The exact finite-window construction may be a useful specialization rather than a new theorem family.')
p('No outside professor, reviewer or cited author has reviewed or endorsed these results. The literature review was focused and used primary sources; it was not exhaustive. Both an expert proof review and a more systematic priority search remain necessary.')

page();h1('4. The next defensible research steps')
table(['Research gate','Required output and decision criterion'],[
('1. Independent proof and priority review','Send the explicit model, exact theorem statements and closest-source comparison to a control/system-identification researcher. Record counterexamples or equivalent prior theorems rather than renaming established results.'),
('2. Realistic measurement protocol','Specify how response coefficients are estimated without direct access to hidden states. Derive the resulting noise covariance, bias and uncertainty. Do not assume observed prices satisfy the current independent-noise contract.'),
('3. Stronger conventional comparison','Evaluate a continuous positive-moment or suitable constrained kernel estimator under the same information and uncertainty target. Keep model conflicts and solver failures in the denominator.'),
('4. Deliberate model violations','Test signed feedback, rate-floor error, correlated noise, drift, switching and nonlinearity. State when the confidence logic is invalid rather than reporting unjustified stable labels.'),
('5. Economic meaning','Add an economically grounded market mechanism, conventional liquidity/leverage explanations, and measurable costs of false-safe decisions and abstention. Show what the new observation requirement adds.'),
('6. External reproduction','Use a separately authored implementation, new seeds and models, and preferably another solver implementation. Preserve the full failure and sensitivity record.')],[2.1,4.9])
h2('Recommended paper positioning')
p('“When does a finite stress-test response justify a stability statement under hidden adaptive memory?” is supportable as a research target. “Our original indicator predicts global AI financial instability better than existing finance” is not supported by this release.')
p('Do not spend the next stage enlarging the title or the claimed scope. The most valuable advance is closing the observation gap: demonstrate an attainable measurement protocol and prove exactly what can be inferred from it.',bold=True)

page();h1('5. Files, reproduction and sources')
h2('Where to start')
p('Read the 13-page paper in paper/Full_Horizon_Identification_Audit.pdf. Its self-contained .tex source is alongside it. The README explains installation and commands. The data dictionary and claim/proof audit are in docs/. All measurements, decisions, conflicts and erroneous labels are retained in data/ and results/.')
h2('Core reproduction commands')
for line in ['python -m pip install -r requirements.txt','python -m pytest -q','python scripts/verify_confidence_events.py','python scripts/verify_exact.py --results data','python scripts/reproduce_clean.py --output ../mmfh-new-run --datasets 21600']:
 q=p(line);q.paragraph_format.space_after=Pt(4)
 for r in q.runs:r.font.name='Consolas';r.font.size=Pt(9)
p('Use a new output directory for clean reproduction. It copies inputs and reruns the full comparison without overwriting the saved primary results. Runtimes and small floating-point differences can vary by platform.',style='Caption')
h2('Closest primary sources')
refs=[
'[1] van Waarde, Eising, Trentelman & Camlibel (2020). Data informativity: a new perspective on data-driven analysis and control. arXiv:1908.00468.',
'[2] Khosravi & Smith (2025). Regularized Identification with Internal Positivity Side-Information. SIAM J. Control Optim., 63(1), 26–56. DOI: 10.1137/23M1556095.',
'[3] Khosravi & Smith (2022, reviewed preprint). Kernel-based Impulse Response Identification with Side-Information on Steady-State Gain. arXiv:2111.00409v2.',
'[4] Bertsimas & Popescu (2005). Optimal Inequalities in Probability Theory: A Convex Optimization Approach. SIAM J. Optim., 15(3), 780–804.',
'[5] Polyanskiy & Wu (2019). Dualizing Le Cam’s method for functional estimation, with applications to estimating the unseens. arXiv:1902.05616.',
'[6] Georges & Pereira (2021). Market Stability with Machine Learning Agents. J. Economic Dynamics and Control, 122, 104032. Reviewed author preprint: April 2019.'
]
for r in refs:
 q=p(r);q.paragraph_format.space_after=Pt(6)
 for rr in q.runs:rr.font.size=Pt(9.5)
p('AI-assisted research development. The original archive is preserved. Resolve authorship, attribution and submission disclosure requirements before using this draft as a manuscript.',style='Caption')
d.save(ROOT/'Full_Horizon_Findings_and_Next_Steps.docx')
print(ROOT/'Full_Horizon_Findings_and_Next_Steps.docx')
