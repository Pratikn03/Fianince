"""
Script to generate TWO clean, collaborative, reading-focused Word files:
1. Paper1_Questions_Workbook.docx (Questions & Reading Workspaces Only)
2. Paper1_Answers_Solution_Manual.docx (Complete Section Walkthrough & Full Answers Only)

Framed naturally as a Co-Author Reading Guide & Discussion Workbook for Sujan Khatiwada and Prashant Niroula.
"""

import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# --- Color Palette Constants ---
NAVY_PRIMARY = "0B2545"      # Deep Executive Navy
SLATE_SECONDARY = "134074"   # Secondary Slate Blue
STEEL_BLUE = "0077B6"        # Vibrant Steel Blue
CHARCOAL_TEXT = "1D2D44"     # Dark Neutral Body Text
LIGHT_BG = "EEF4F8"          # Ice Gray Callout Background
LIGHT_BORDER = "CFDBD5"      # Light Border Gray
ALERT_CRIMSON = "8D0801"     # Warning / Rigor Accent
GOLD_ACCENT = "D4A373"       # Warm Accent
BG_MUTED = "F8FAFC"          # Very light neutral
BORDER_MUTED = "E2E8F0"
ANSWER_BG = "F8FAFC"         # Soft Ivory / Slate for answers

RGB_NAVY = RGBColor(11, 37, 69)
RGB_SLATE = RGBColor(19, 64, 116)
RGB_STEEL = RGBColor(0, 119, 182)
RGB_CHARCOAL = RGBColor(29, 45, 68)
RGB_CRIMSON = RGBColor(141, 8, 1)
RGB_MUTED = RGBColor(100, 116, 139)
RGB_GREEN = RGBColor(16, 120, 60)

def set_cell_background(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, border_style in borders.items():
        if border_style:
            val, sz, space, color = border_style
            b_elm = parse_xml(f'<w:{border_name} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="{space}" w:color="{color}"/>')
            tcBorders.append(b_elm)
        else:
            b_elm = parse_xml(f'<w:{border_name} {nsdecls("w")} w:val="none"/>')
            tcBorders.append(b_elm)
    tcPr.append(tcBorders)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_heading_1(p):
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGB_NAVY

def style_heading_2(p):
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGB_SLATE

def style_heading_3(p):
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGB_STEEL

def style_body(p, bold_prefix="", text="", italic=False):
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGB_CHARCOAL
    if text:
        r_txt = p.add_run(text)
        r_txt.font.name = "Calibri"
        r_txt.font.size = Pt(10)
        r_txt.font.italic = italic
        r_txt.font.color.rgb = RGB_CHARCOAL

def add_header_footer(doc, title_text):
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
        # Header
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run(f"Machine Markets Research Project | {title_text}")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Paper 1: What Prices Cannot Tell a Market Supervisor — Co-Author Reading Guide")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(120, 120, 120)

def add_callout(doc, text_list, title=None, alert_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, LIGHT_BG)
    border_color = STEEL_BLUE if alert_type == "info" else GOLD_ACCENT
    set_cell_borders(cell, left=("single", "24", "0", border_color),
                           top=("single", "4", "0", LIGHT_BORDER),
                           right=("single", "4", "0", LIGHT_BORDER),
                           bottom=("single", "4", "0", LIGHT_BORDER))
    set_cell_margins(cell, top=130, bottom=130, left=180, right=180)
    
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(3)
    if title:
        rt = cp.add_run(title + "\n")
        rt.font.name = "Calibri"
        rt.font.size = Pt(10.5)
        rt.font.bold = True
        rt.font.color.rgb = RGB_NAVY
        
    for item in text_list:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(item)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGB_CHARCOAL
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_metadata_table(doc, data_dict):
    tbl = doc.add_table(rows=len(data_dict), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    row_idx = 0
    for k, v in data_dict.items():
        c0 = tbl.cell(row_idx, 0)
        c1 = tbl.cell(row_idx, 1)
        c0.width = Inches(1.8)
        c1.width = Inches(4.7)
        
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        
        set_cell_borders(c0, top=("single", "4", "0", BORDER_MUTED),
                             bottom=("single", "4", "0", BORDER_MUTED),
                             left=("single", "4", "0", BORDER_MUTED),
                             right=("single", "4", "0", BORDER_MUTED))
        set_cell_borders(c1, top=("single", "4", "0", BORDER_MUTED),
                             bottom=("single", "4", "0", BORDER_MUTED),
                             left=("single", "4", "0", BORDER_MUTED),
                             right=("single", "4", "0", BORDER_MUTED))
        
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9); r1.font.color.rgb = RGB_CHARCOAL
        row_idx += 1
        
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

# ==============================================================================
# 12 READING MODULES (Clean, Clear, Collaborative)
# ==============================================================================

READING_MODULES = [
    {
        "num": 1,
        "title": "The Market Model and How Closed-Loop Prices Hide Trader Memory",
        "reading_ref": "Section 2: Model and Motivating Examples (pages 5–12), Appendices A & B",
        "summary": (
            "This section sets up our core market model: K different trader groups, each learning from past prices "
            "with its own memory parameter η_k ∈ [0, 1) and weight w_k. When traders submit orders, prices move through "
            "market depth κ and dealer damping q. This creates a closed-loop feedback system G(z) = κ H(z) / (1 + κ q H(z)). "
            "The key takeaway is that the memory parameters η_k are transmission zeros of the open loop, which get masked "
            "by the closed-loop feedback denominator. Fitting standard ARMA models to price returns Δp_t identifies only the "
            "closed-loop eigenvalues, not the individual trader learning rates."
        ),
        "question": (
            "After reading Section 2, explain step-by-step how the trader demand equations lead to the closed-loop transfer "
            "function G(z). Why does observing price changes alone fail to reveal the separate learning rates η_k, and how does "
            "Theorem 2.1 (Merged Measure Invariance) prove that multiple different trader populations produce the exact same price path?"
        ),
        "subquestions": [
            "Walk through how individual trader memory x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1} aggregates into total demand u_t.",
            "Show the algebra connecting the open-loop transfer function H(z) = ∑ w_k / (1 - η_k z^{-1}) to closed-loop G(z).",
            "Explain in plain words the difference between open-loop zeros (trader memory) and closed-loop poles (price eigenvalues).",
            "Why can a market with 2 slow institutional traders look identical in prices to a market with 5 fast HFT market makers?",
            "What does Theorem 2.1 tell us about what is mathematically observable from noise-free price data?"
        ],
        "key_objects": "Equations (1)–(8), Lemma 2.1, Lemma 2.2, Theorem 2.1, Figure 1",
        "sujan_note": "Control Systems Perspective: Notice how this mirrors feedback masking and unobservability in closed-loop robotic actuators.",
        "prashant_note": "Microstructure Perspective: Consider why regulators cannot tell who is causing market momentum just by looking at the price ticker."
    },
    {
        "num": 2,
        "title": "Why Telling Trader Groups Apart Takes Massive Amounts of Data",
        "reading_ref": "Section 3.1: Near-Colliding Rates and the Minimax Lower Bound (pages 13–18), Appendix B",
        "summary": (
            "Section 3.1 proves our paper's central lower bound: if two trader groups have memory rates that are close "
            "(spacing Δη = |η_1 - η_2|), no statistical estimator can tell them apart without at least Ω(σ² (Δη)^{-(4K-2)}) observations. "
            "For 2 trader groups, this is (Δη)^{-6}; for 3 groups, it is (Δη)^{-10}. The mathematical reason is moment matching: "
            "two different economies can match their first 2K - 1 moments, meaning the difference in price behavior is an extremely "
            "small, high-order effect that is easily drowned out by ordinary price volatility."
        ),
        "question": (
            "Read Section 3.1 and Appendix B. Explain why the data requirement blows up at rate (Δη)^{-6} for 2 trader groups "
            "and (Δη)^{-10} for 3 groups. How does the proof construct two different economies whose price differences are so tiny "
            "that Gaussian price noise completely hides them?"
        ),
        "subquestions": [
            "Explain what it means for two candidate economies μ_0 and μ_1 to match their first 2K - 1 moments.",
            "Show how this moment matching causes the leading term in the price impulse difference Δh_t to be of order (Δη)^{2K-1}.",
            "How does the Gaussian Kullback-Leibler divergence D_KL scale as (Δη)^{4K-2}?",
            "Using Le Cam's two-point testing method, explain why sample size N must scale as (Δη)^{-(4K-2)} to tell the two economies apart.",
            "Work out the practical numbers: If the difference between two trading algorithms is halved from 0.10 to 0.05, by what factor does the required data multiply?"
        ],
        "key_objects": "Theorem 3.1, Theorem 3.2, Lemmas B.1–B.4, Table 1 (Moment Matching)",
        "sujan_note": "Signal Processing Perspective: Note how polynomial interpolation and Vandermonde ill-conditioning create this fundamental information barrier.",
        "prashant_note": "Financial Economics Perspective: Reflect on why this means public price tapes can never settle disputes about algorithmic crowding."
    },
    {
        "num": 3,
        "title": "How to Actually Recover Trader Memory: Prony's Method and Hankel Matrices",
        "reading_ref": "Section 3.2: The Matching Upper Bound and Algorithm 1 (pages 18–24), Appendix B",
        "summary": (
            "While Section 3.1 proved you need at least (Δη)^{-(4K-2)} observations, Section 3.2 proves that an algorithm based on "
            "Prony's method and Hankel matrices can actually achieve this rate! The algorithm builds a Hankel matrix H_m from estimated "
            "price impulse responses and finds the roots of a characteristic polynomial P(z) = ∏ (z - η_k). The paper proves that "
            "Prony's method works without needing to know the true spacing in advance, matching the lower bound exactly."
        ),
        "question": (
            "Read Section 3.2 and Algorithm 1. Walk through how Prony's method extracts the hidden memory parameters η_k from price impulse "
            "responses. Why does standard linear regression (OLS) fail, and why is non-linear polynomial root-finding necessary?"
        ),
        "subquestions": [
            "How is the Hankel matrix H_m constructed from estimated impulse responses h_t?",
            "Explain the factorization H_m = V_K diag(w_1, ..., w_K) V_K^T and why the smallest singular value scales as (Δη)^{2K-1}.",
            "How does noise in the estimated impulse responses perturb the roots of the Prony polynomial P(z)?",
            "Why does ordinary least squares (OLS) produce errors 100x to 10,000x larger than Prony's method (Table 3)?",
            "What guarantees does the theorem provide when the noise is sub-Gaussian?"
        ],
        "key_objects": "Theorem 3.2, Proposition 3.3, Algorithm 1, Table 3, Lemma B.5",
        "sujan_note": "Robotics & Subspace Methods: Compare this to ESPRIT and subspace identification in sensor array processing.",
        "prashant_note": "Practical Implementation: Consider whether an exchange or regulator could run this algorithm in an automated audit pipeline."
    },
    {
        "num": 4,
        "title": "The Financial Cost of Learning: Why Probing the Market Costs Millions",
        "reading_ref": "Section 4: Account-Level Capital and Probing Costs (pages 25–30), Appendices B & C",
        "summary": (
            "Section 4 asks: What if an observer doesn't just watch prices, but actively sends test orders (probes) into the order book "
            "to see how the market reacts? The paper proves that sending test trades against a limit order book costs money—specifically, "
            "a positive-definite quadratic execution cost (1/2) v^T T_H v (Lemma 4.2). Furthermore, a trader who must maintain margin "
            "solvency needs cash reserves that scale as δ^{-4}. Halving the memory difference multiplies the required capital by 16."
        ),
        "question": (
            "Read Section 4. Explain why an active observer cannot 'probe the market for free'. How does the Toeplitz execution cost matrix "
            "prove that no round-trip probing strategy produces a sure gain, and why does margin solvency require capital scaling as δ^{-4}?"
        ),
        "subquestions": [
            "Derive the execution cost of a probing sequence v_t against a book with transient price impact.",
            "Explain Lemma 4.2: Why is the Toeplitz cost matrix T_H strictly positive definite for any non-zero round-trip probe?",
            "What is the economic intuition behind the 'No Sure Gain' principle for market exploration?",
            "Why does maintaining mark-to-market margin solvency force cash capital to scale as B ≥ Ω(σ² / δ⁴)?",
            "Walk through the 'Disclosure in Dollars' calculation (Table 4): Why would re-learning two algorithms weekly cost $15M–$356M a year per market?"
        ],
        "key_objects": "Theorem 4.1, Lemma 4.2, Theorem 4.3, Table 4, Corollary 4.4",
        "sujan_note": "Optimal Control Perspective: Consider how this Toeplitz cost acts like an energy penalty in LQR trajectory design.",
        "prashant_note": "Institutional Capital Perspective: Think about why proprietary trading firms cannot routinely run exploratory probing on live books."
    },
    {
        "num": 5,
        "title": "Why Passively Watching Prices Cannot Beat Active Probing",
        "reading_ref": "Section 4.4 & Section 5.8: Passive Data and Whittle Divergence (pages 31–33, 65–70), Appendix B",
        "summary": (
            "What if a supervisor decides not to send any test trades, but simply waits and records natural market transactions? "
            "Theorem 5.8 uses Whittle spectral divergence for stationary Gaussian processes to analyze the long-run rate limit as T → ∞. "
            "The paper proves that passive price observations provide information at the exact same slow polynomial rate: "
            "lim (1/T) D_KL = O((Δη)^{4K-2}). Passive data cannot magically bypass the lower bound; waiting for natural trades costs time "
            "at the exact same rate that probing costs capital."
        ),
        "question": (
            "Read Section 4.4 and Section 5.8. Explain the Whittle spectral divergence formula and why passive observation suffers from "
            "the same information barrier as active probing. Why can't a regulator solve the identification problem by just collecting years of passive tick data?"
        ),
        "subquestions": [
            "How does the return spectral density f(λ) reflect the closed-loop transfer function G(e^{iλ})?",
            "Explain the Whittle divergence integral (1/4π) ∫ [ (f_0 - f_1)² / (f_0 f_1) ] dλ and how it measures information rate.",
            "Why does moment matching force the spectral difference integral to scale as (Δη)^{4K-2}?",
            "Compare active probing with passive watching: Why does ambient market noise fail to excite the revealing frequencies?",
            "What does this theorem imply for regulatory policy and Big Data surveillance architectures?"
        ],
        "key_objects": "Theorem 5.8, Proposition S14, Figure 6 (Spectral Divergence Curves)",
        "sujan_note": "Systems Identification Perspective: Think about the concept of 'persistent excitation' and why ambient noise provides poor excitation.",
        "prashant_note": "Regulatory Architecture Perspective: Consider why accumulating petabytes of passive market data without trader tags yields diminishing returns."
    },
    {
        "num": 6,
        "title": "Real Bitcoin Price Noise vs. Continuous Memory Distributions",
        "reading_ref": "Section 4.5 & Section 5.7: Real Noise Injection and General Memory (pages 34–38, 60–64), Appendix C",
        "summary": (
            "This section subjects our theory to two reality checks: (1) Replacing Gaussian noise with real, heavy-tailed 1-minute Bitcoin "
            "price changes using exact empirical multinomial resampling; and (2) Extending memory from discrete trader groups to general, "
            "continuous memory distributions (completely monotone kernels). The real Bitcoin noise confirms the theory: empirical log-log slopes "
            "are -6.01 (for K = 2) and -9.81 (for K = 3). But continuous memory reveals a deeper barrier: Theorem 5.7 proves that recovering "
            "a continuous memory spectrum drops the minimax accuracy to logarithmic w = Θ(1 / log(N)), requiring exponential data exp(Θ(1/w))!"
        ),
        "question": (
            "Read Section 4.5 and Section 5.7. Why does the polynomial rate survive real heavy-tailed crypto noise under exact resampling, "
            "and why does moving to a continuous memory distribution cause the learning rate to collapse from polynomial to logarithmic?"
        ),
        "subquestions": [
            "Explain how the exact multinomial resampling procedure works with real Bitcoin price changes.",
            "Look at Table 6 and Figure 5: Why are the fitted slopes of -6.01 and -9.81 such strong confirmation of the (Δη)^{-6} and (Δη)^{-10} theory?",
            "What is a completely monotone memory kernel k(t) = ∫ e^{-λ t} dF(λ) according to Bernstein's Theorem?",
            "Why does recovering a continuous distribution F(λ) suffer from the ill-posedness of the inverse Laplace transform?",
            "Contrast the two data requirements: What is the practical difference between needing N ≈ δ^{-6} trades vs. N ≈ exp(1/w) trades?"
        ],
        "key_objects": "Theorem 5.7, Table 6 (Real Noise Injection), Figure 5, Bernstein's Theorem",
        "sujan_note": "Functional Analysis Perspective: Relate Theorem 5.7 to the severe ill-posedness of inverting continuous Fredholm integral operators.",
        "prashant_note": "Market Reality Perspective: Reflect on why real markets with hundreds of algorithms across all time horizons make continuous recovery impossible."
    },
    {
        "num": 7,
        "title": "What Regulatory Disclosure Buys: The Power of Algorithmic Audit Trails",
        "reading_ref": "Section 5.1–5.3 & Section 5.5: What Disclosure Buys and When It Is Worth Acquiring (pages 39–46)",
        "summary": (
            "Section 5 evaluates the value of mandatory regulatory reporting (such as MiFID II RTS 24 algo_id tags or CFTC trader categories). "
            "Theorem 5.1 proves that observing class-tagged order flows completely uncouples the problem: the sample requirement drops from "
            "Θ((Δη)^{-(4K-2)}) to Θ((Δη)^{-2}) for learning rates, and becomes constant O(1) for trader weights! Proposition 5.5 formalizes the "
            "supervisor's cost-benefit trade-off: balancing the fixed cost of an audit trail against the societal harm of slow learning from prices."
        ),
        "question": (
            "Read Section 5.1–5.3 and 5.5. Explain mathematically and institutionally why observing class-tagged order flow uncouples the estimation "
            "problem. How does the sample complexity drop to (Δη)^{-2}, and when does Proposition 5.5 say a supervisor should mandate an audit trail?"
        ),
        "subquestions": [
            "How does observing separate class order flows y_{k,t} turn a coupled non-linear problem into K separate single-trader regressions?",
            "Explain where the information gain factor (Δη)^{-(4K-4)} comes from.",
            "Why does estimating trader class size w_k become O(1), completely independent of how close the memory rates are?",
            "Explain Proposition 5.5's decision rule: What are the key costs and benefits a supervisor must weigh?",
            "Why is disclosure most valuable in an intermediate band of memory spacings rather than at extreme values?"
        ],
        "key_objects": "Theorem 5.1, Proposition 5.2, Proposition 5.5, Table 5 (Sample Complexity Comparison)",
        "prashant_note": "Policy Perspective: Address why proprietary trading firms lobby against algo tags, and how class-level reporting protects intellectual property.",
        "sujan_note": "Distributed Systems Perspective: Compare direct sensor access in multi-agent networks to output-only coupled state estimation."
    },
    {
        "num": 8,
        "title": "Real-World Evidence: Mandated Reporting in 20 CFTC Futures Markets",
        "reading_ref": "Section 5.4 & Section 5.6: Mandated Disclosure and Empirical Evidence (pages 47–54), Appendix E",
        "summary": (
            "The paper tests the disclosure prediction on real institutional data: the CFTC's weekly Commitments of Traders (COT) reports. "
            "In an initial test on 8 major futures markets (Bitcoin, Ether, S&P 500, Treasuries, Euro, Yen, Oil, Gas), class positions pinned down "
            "speculative persistence to an interval 9 to 71 times narrower than prices alone. A registered replication on 12 completely new markets "
            "(Gold, Silver, Copper, Corn, Soybeans, Wheat, Cattle, Coffee, Sugar, Cotton, Nasdaq-100, Pound; SHA-256 591e71c9...) replicated in all 12. "
            "Under root-T scaling, matching the weekly class report's precision from prices alone would take a median of 1,350 times as much data!"
        ),
        "question": (
            "Read Section 5.4, Table 7, and Table 8. Walk through the empirical results from the 20 CFTC futures markets. How does the paper "
            "prove that class-tagged positions pin down persistence to a narrow band while prices leave it almost unrestricted, and what does the 1,350x multiplier mean?"
        ),
        "subquestions": [
            "Explain the stock-flow bridge (Remark 2.2) connecting weekly reported position stocks S_t to theoretical trading demand.",
            "Compare the confidence interval widths for η_fast in Table 7 and Table 8: Why are price-only intervals 0.85 to 0.96 wide?",
            "How is the 'Data Equivalence Multiplier' calculated, and why does matching one weekly report require ~1,350 weeks (~26 years) of prices?",
            "Why is this 1,350x calculation a conservative lower bound?",
            "What is the significance of the 12-market replication replicating in 12 out of 12 markets?"
        ],
        "key_objects": "Table 7 (Original 8 Markets), Table 8 (12-Market Replication), Remark 2.2, Section 5.4",
        "prashant_note": "Futures Markets Perspective: Detail the difference between Managed Money vs. Producers in Disaggregated COT and Leveraged Funds in Financial COT.",
        "sujan_note": "Data Analysis Perspective: Look at how the stationary block bootstrap handles temporal correlation in weekly financial time series."
    },
    {
        "num": 9,
        "title": "Why 10 Pre-Specified Tests Failed: Within-Class Sign Cancellation",
        "reading_ref": "Section 5.5, Section 5.6, Table 9 (Scorecard of 22 Tests), Section S8",
        "summary": (
            "A core strength of this paper is complete transparency: Table 9 reports all 22 pre-specified empirical tests—11 passed, 10 failed, "
            "and 1 was unsupported. The failures include: trend-following (H2) failed in equities (S&P 500, Nasdaq-100); position persistence showed "
            "no separate learning root (H3 failed in 6 of 8 markets); and Binance 5-minute price changes failed to forecast class positions (N2: 1 of 30). "
            "The paper explains that these failures reveal 'within-class sign cancellation': coarse public categories bundle opposing strategies "
            "(e.g., trend-following CTAs trading against cash-futures basis arbitrageurs), cancelling the signal in aggregate data."
        ),
        "question": (
            "Read Section 5.5, Section 5.6, and Table 9. Examine the 10 failed pre-specified tests. Why did these tests fail, and how do their failures "
            "actually provide direct institutional proof that coarse reporting buckets cancel out, proving the need for granular algo tags?"
        ),
        "subquestions": [
            "Why did trend-following (H2) hold in commodities and currencies but fail completely in equity indices?",
            "Why did positions fail to separate a distinct faster root for learning memory (H3)?",
            "Explain the mechanics of 'within-class sign cancellation' inside the CFTC 'Leveraged Funds' bucket.",
            "Why did Binance 5-minute price changes fail to forecast top-trader position ratios out-of-sample (Diebold-Mariano test)?",
            "Why does reporting failed pre-specified tests honestly build credibility with reviewers, and how does it justify granular MiFID II algo tags?"
        ],
        "key_objects": "Table 9 (Scorecard of 22 Tests), Section 5.5, Section 5.6, Table S7, Table S8",
        "prashant_note": "Institutional Strategy Perspective: Explain how a CTA and a basis trading desk trade in opposite directions during market moves.",
        "sujan_note": "System Cancellation Perspective: In control terms, how do two parallel transfer functions with opposite signs produce pole-zero cancellation?"
    },
    {
        "num": 10,
        "title": "The Spectral Blind Spot: How Stable Eigenvalues Hide Flash Crashes",
        "reading_ref": "Section 6: A Spectral Blind Spot (pages 55–59), Appendix B; Paper 2 Section 1 & 2",
        "summary": (
            "Section 6 reveals a dangerous blind spot in standard risk management. Theorem 6.1 proves that for any prescribed stable eigenvalues "
            "0 < λ_2 < λ_1 < 1, any one-step variance, and any stationary price variance, there exists a family of economies sharing all three "
            "quantities whose peak transient amplification grows without bound! This happens because the market state matrix A is non-normal "
            "(A A^T ≠ A^T A). While spectral radius ρ(A) < 1 guarantees long-run decay, the Kreiss Matrix Theorem shows that non-normal systems "
            "can experience massive, violent excursions over the short run before settling down."
        ),
        "question": (
            "Read Section 6 and Figure 7. Explain the 'spectral blind spot'. Why does having stable eigenvalues and low daily volatility fail to "
            "protect a market from catastrophic short-term flash crashes, and how does the Kreiss Matrix Theorem formalize this?"
        ),
        "subquestions": [
            "How does Theorem 6.1 construct two markets with the exact same eigenvalues and stationary variance but completely different short-run risks?",
            "What is a non-normal matrix, and why do non-orthogonal eigenvectors cause transient amplification ||A^t||_2 >> ρ(A)^t?",
            "State the Kreiss Matrix Theorem and define the Kreiss constant K(A) = sup (|z| - 1) ||(zI - A)^{-1}||.",
            "Explain Figure 7: How can two markets with the same 5-period half-life have peak cumulative losses that differ by 10x or 100x?",
            "What does this mean for financial risk managers who rely only on Value-at-Risk (VaR) or volatility to measure market safety?"
        ],
        "key_objects": "Theorem 6.1, Figure 7 (Transient Excursions for Matched Eigenvalues), Kreiss Matrix Theorem",
        "sujan_note": "Non-Normal Dynamics Perspective: Compare this to subcritical transition to turbulence in fluid dynamics or actuator overshoot in robotics.",
        "prashant_note": "Risk Management Perspective: Connect this to why VaR models failed during the 2010 Flash Crash and crypto cascading liquidations."
    },
    {
        "num": 11,
        "title": "The Solution: A Certified Pre-Trade Guard and the Bridge to Paper 2",
        "reading_ref": "Section 7: Policy Implications; Paper 2: Theorems 1–3, Sections 3 & 4",
        "summary": (
            "Section 7 and our companion paper (Paper 2) deliver the operational punchline: Because Paper 1 proves that identifying trader cohorts "
            "from prices is impossible in real time, market safety controls must be identification-free! Paper 2 proves that cumulative transient "
            "risk is governed by the scalar invariant S = κ~ / (m - q κ~), and an order book overshoots if and only if φ ε > (1 - a) κ. "
            "A pre-trade guard on the summed impulse response is the maximal safe control rule: it prevents transient overshoot regardless of how "
            "traders split into unknown cohorts, and requires only Θ(σ² ε^{-2} log(1/ε)) experiments to certify."
        ),
        "question": (
            "Read Section 7 of Paper 1 and Sections 3–4 of Paper 2. Explain why we need an 'identification-free' pre-trade guard. How does the "
            "scalar invariant S measure cumulative risk, and how does the guard prevent flash crashes without needing to know individual trader algorithms?"
        ),
        "subquestions": [
            "Why does Paper 1's lower bound Ω((Δη)^{-(4K-2)}) rule out 'identify-then-control', forcing regulators to use identification-free rules?",
            "Explain the exact overshoot condition φ ε > (1 - a) κ: What is the tug-of-war between momentum feedback φ and depth replenishment ε?",
            "Define the cumulative transient risk statistic S = κ~ / (m - q κ~) and explain why it is cohort-invariant.",
            "How does scaling an order limit by 1 / S (or admitting trades only when C_3 < 0) guarantee safety across all shock paths?",
            "What did the empirical backtests in Paper 2 find: How did the certified guard lower tail losses by 13% on untouched days?"
        ],
        "key_objects": "Paper 1 Section 7, Paper 2 Theorems 1–3, Proposition 7.1, Figure 1 (Paper 2)",
        "prashant_note": "Exchange Implementation Perspective: How can exchanges like CME or Binance build this guard directly into matching engines?",
        "sujan_note": "Robust Control Perspective: Connect this to H_infinity control, small-gain theorems, and Kharitonov's theorem for interval systems."
    },
    {
        "num": 12,
        "title": "100% Machine-Checked Mathematics: Formal Verification in Lean 4",
        "reading_ref": "Section 1.3, Section 8, Appendix D; Paper1FullFrontiers.lean",
        "summary": (
            "A major milestone of our project is that the mathematical foundation of Paper 1 is 100% machine-checked in the Lean 4 interactive "
            "theorem prover with Mathlib. The formalization contains 787 named declarations across 81 modules with exactly zero sorry placeholders "
            "and zero custom axioms. It verifies the identification boundary, moment-matched lower bounds for all K, Prony's matching upper bound, "
            "Toeplitz execution cost positive definiteness, margin capital bounds, real noise resampling invariance, and the 10 frontier environments."
        ),
        "question": (
            "Read Section 1.3, Section 8, and Appendix D. What is interactive theorem proving in Lean 4, why is machine-checking our proofs so valuable "
            "for research credibility, and how does having 787 verified theorems help us defend the paper before journal reviewers?"
        ),
        "subquestions": [
            "How does interactive theorem proving in Lean 4 differ from traditional paper-and-pencil mathematical proofs?",
            "Explain what '0 sorry placeholders and standard axioms only' means for mathematical certainty.",
            "How does the formal verification receipt (formal_verification_receipt.json) and automated test suite guarantee reproducibility?",
            "How did Lean 4 formalize the general-alpha testing bounds and moment matching without requiring unproved external lemmas?",
            "How will we use this Lean 4 codebase to address mathematical skepticism from journal referees at Econometrica or Quantitative Economics?"
        ],
        "key_objects": "Section 1.3, Section 8, Appendix D, formal_verification_receipt.json, Paper1FullFrontiers.lean",
        "sujan_note": "Formal Methods Perspective: Compare formal software verification in aerospace robotics to formal proof checking in financial economics.",
        "prashant_note": "Regulatory Trust Perspective: Consider how central banks and regulators could use machine-checked proofs to verify market rules before launch."
    }
]

# ==============================================================================
# BUILDER 1: QUESTIONS ONLY WORKBOOK (Clean Reading Guide)
# ==============================================================================
def build_questions_only_file():
    doc = Document()
    add_header_footer(doc, "Co-Author Reading Guide & Discussion Workbook")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36); p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("CO-AUTHOR READING GUIDE & DISCUSSION WORKBOOK")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Machine Markets Research Program:\nCo-Author Reading Guide & Chapter Discussion Workbook")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(22); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "A Section-by-Section Reading Companion and Thoughtful Discussion Questions for Sujan Khatiwada and Prashant Niroula "
        "to Thoroughly Read, Understand, and Master Paper 1 ('What Prices Cannot Tell a Market Supervisor')"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(12.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=6, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Primary Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Companion Framework", "From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard"),
        ("Lead Author & PI", "Pratik Niroula (Department of Computer Information Science, Minnesota State University, Mankato)"),
        ("Contributing Co-Authors", "Sujan Khatiwada (Dept. of Electrical, Computer & Robotics Engineering, MNSU Mankato)\nPrashant Niroula (Faculty of Management, Tribhuvan University, Kirtipur, Nepal)"),
        ("Workbook Purpose", "Guide thorough reading of every section, build shared understanding of the math/data, and collect co-author written discussion notes."),
        ("Formal Verification State", "787 Lean 4 Kernel-Verified Declarations across 81 Modules; 0 sorry; Mathlib Standard Axioms")
    ]
    for i, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(i, 0); c1 = meta_box.cell(i, 1)
        c0.width = Inches(2.0); c1.width = Inches(4.5)
        set_cell_background(c0, "F8FAFC"); set_cell_background(c1, "FFFFFF")
        set_cell_borders(c0, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                              left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_borders(c1, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                              left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9.5); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9.5); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(12); sp.paragraph_format.space_after = Pt(4)
    add_callout(
        doc,
        [
            "\"Welcome Sujan and Prashant! This reading guide is designed to help us walk through our entire paper together section by section. "
            "Our goal is for each of us to fully understand the mathematical models, the empirical data from CFTC and Binance, "
            "and the policy implications, so that we can present, defend, and expand this work with total confidence as co-authors.\"",
            "— Pratik Niroula (Lead Author & Research Lead)"
        ],
        title="WELCOME & CO-AUTHOR READING OBJECTIVES",
        alert_type="info"
    )
    doc.add_page_break()

    # Section 1: Welcome & How to Read
    p_s1 = doc.add_paragraph(); style_heading_1(p_s1); p_s1.add_run("1. How to Use this Reading Workbook")
    p_b1 = doc.add_paragraph()
    style_body(
        p_b1,
        "Reading and Discussion Structure: ",
        "This workbook is divided into 12 reading modules that follow the exact sequence of Paper 1 (and its connection to Paper 2). "
        "For each module, please follow these four simple steps:\n"
        "1. Open the manuscript and read the specified pages and sections carefully.\n"
        "2. Review the plain-English summary and key equations highlighted in the guide.\n"
        "3. Reflect on the master discussion question and the sub-questions.\n"
        "4. In the provided response box, write down your detailed thoughts, derivations, and explanations (aim for about 1 full page, approx. 400–600 words per module)."
    )
    
    # 12 Questions with Clean Workspaces
    for q in READING_MODULES:
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Module {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Where to Read in Paper": q["reading_ref"],
            "Key Mathematical Focus": q["key_objects"]
        })
        
        p_c_hdr = doc.add_paragraph(); style_heading_3(p_c_hdr); p_c_hdr.add_run("Summary of What this Section Covers")
        p_ctx = doc.add_paragraph(); style_body(p_ctx, "", q["summary"])
        
        p_m_hdr = doc.add_paragraph(); style_heading_3(p_m_hdr); p_m_hdr.add_run("Reading & Discussion Question")
        add_callout(doc, [q["question"]], title="MAIN DISCUSSION QUESTION", alert_type="info")
        
        p_sq_hdr = doc.add_paragraph(); style_heading_3(p_sq_hdr); p_sq_hdr.add_run("Key Points to Address in Your Written Notes")
        for sq in q["subquestions"]:
            p_sq = doc.add_paragraph(style='List Bullet')
            p_sq.paragraph_format.space_before = Pt(2); p_sq.paragraph_format.space_after = Pt(3)
            style_body(p_sq, "", sq)
            
        p_co_hdr = doc.add_paragraph(); style_heading_3(p_co_hdr); p_co_hdr.add_run("Special Angles to Think About")
        p_sujan = doc.add_paragraph(); style_body(p_sujan, "For Sujan Khatiwada (Control & Systems Angle): ", q["sujan_note"])
        p_prashant = doc.add_paragraph(); style_body(p_prashant, "For Prashant Niroula (Markets & Policy Angle): ", q["prashant_note"])
        
        # Dedicated Clean Response Box
        p_box_title = doc.add_paragraph()
        p_box_title.paragraph_format.space_before = Pt(10); p_box_title.paragraph_format.space_after = Pt(3)
        p_box_title.paragraph_format.keep_with_next = True
        r_bt = p_box_title.add_run(f"Your Written Reading Notes & Discussion Space — Module {q['num']}")
        r_bt.font.name = "Calibri"; r_bt.font.size = Pt(11); r_bt.font.bold = True; r_bt.font.color.rgb = RGB_NAVY
        
        desc = doc.add_paragraph(); desc.paragraph_format.space_before = Pt(0); desc.paragraph_format.space_after = Pt(4)
        r_desc = desc.add_run(
            f"Please write your thorough answers and notes here (aim for approximately 1 full page, 400–600 words). "
            f"Cover how the math works, what the real-market intuition is, and any questions or insights you have."
        )
        r_desc.font.name = "Calibri"; r_desc.font.size = Pt(9.5); r_desc.font.italic = True; r_desc.font.color.rgb = RGB_MUTED

        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, "FAFAFA")
        set_cell_borders(cell, top=("single", "12", "0", SLATE_SECONDARY), bottom=("single", "12", "0", SLATE_SECONDARY),
                               left=("single", "12", "0", SLATE_SECONDARY), right=("single", "12", "0", SLATE_SECONDARY))
        set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
        
        cp = cell.paragraphs[0]; cp.paragraph_format.space_before = Pt(0); cp.paragraph_format.space_after = Pt(4)
        r_hdr = cp.add_run(f"CO-AUTHOR READING NOTES: MODULE {q['num']} ({q['title'].upper()})\n")
        r_hdr.font.name = "Calibri"; r_hdr.font.size = Pt(10); r_hdr.font.bold = True; r_hdr.font.color.rgb = RGB_SLATE
        
        sections = [
            ("1. How the Math and Derivations Work",
             "[Write your walkthrough of the equations, transfer functions, and proofs here... (approx. 150-200 words)]"),
            ("2. Economic Intuition & Market Reality",
             "[Explain what this means in real trading, the CFTC/Binance data, and market dynamics here... (approx. 150-200 words)]"),
            ("3. Takeaways, Questions, and How to Explain It",
             "[Note your key takeaways, questions for our co-author discussion, or thoughts on presenting this... (approx. 150-200 words)]")
        ]
        for sec_title, placeholder in sections:
            sp_title = cell.add_paragraph(); sp_title.paragraph_format.space_before = Pt(6); sp_title.paragraph_format.space_after = Pt(2)
            r_st = sp_title.add_run(sec_title); r_st.font.name = "Calibri"; r_st.font.size = Pt(9.5); r_st.font.bold = True; r_st.font.color.rgb = RGB_STEEL
            
            sp_body = cell.add_paragraph(); sp_body.paragraph_format.space_before = Pt(0); sp_body.paragraph_format.space_after = Pt(6)
            r_sb = sp_body.add_run(placeholder + "\n\n\n\n\n\n")
            r_sb.font.name = "Calibri"; r_sb.font.size = Pt(9.5); r_sb.font.italic = True; r_sb.font.color.rgb = RGBColor(160, 160, 160)

        doc.add_page_break()

    # Sign-Off Page
    p_end = doc.add_paragraph(); style_heading_1(p_end); p_end.add_run("Co-Author Reading Completion & Alignment Sign-Off")
    p_et = doc.add_paragraph()
    style_body(
        p_et,
        "Shared Co-Author Understanding: ",
        "By completing this reading workbook, we confirm that we have thoroughly read the manuscript, traced the mathematical models, "
        "examined the empirical evidence, and are fully aligned to present and discuss this research together."
    )
    
    sign_table = doc.add_table(rows=4, cols=4); sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER; sign_table.autofit = False
    shd_headers = ["Co-Author Name", "Affiliation", "Date Completed", "Signature"]
    for j, h in enumerate(shd_headers):
        cell = sign_table.cell(0, j); set_cell_background(cell, NAVY_PRIMARY); set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]; r = p.add_run(h); r.font.name = "Calibri"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    signers = [
        ("Pratik Niroula\n(Lead Author & PI)", "Minnesota State University, Mankato\nDept. of Computer Information Science"),
        ("Sujan Khatiwada\n(Co-Author)", "Minnesota State University, Mankato\nDept. of Electrical, Computer & Robotics Engineering"),
        ("Prashant Niroula\n(Co-Author)", "Tribhuvan University, Nepal\nFaculty of Management")
    ]
    for i, (name, affil) in enumerate(signers):
        row = i + 1
        for j, text_val in enumerate([name, affil, "___ / ___ / 2026", "________________"]):
            cell = sign_table.cell(row, j)
            set_cell_background(cell, "FFFFFF" if row % 2 == 1 else "F8FAFC")
            set_cell_borders(cell, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                                  left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
            set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
            p = cell.paragraphs[0]; r = p.add_run(text_val); r.font.name = "Calibri"; r.font.size = Pt(9); r.font.color.rgb = RGB_CHARCOAL
            if j == 0: r.font.bold = True; r.font.color.rgb = RGB_SLATE

    out_path = Path("Paper1_Questions_Workbook.docx")
    doc.save(str(out_path))
    doc.save(str(ROOT / "ceiling_suite/papers/paper1/Paper1_Questions_Workbook.docx"))
    doc.save(str(ROOT / "ceiling_suite/paper1/Paper1_Questions_Workbook.docx"))
    print(f"Built Questions Only Workbook: {out_path.resolve()}")

# ==============================================================================
# BUILDER 2: ANSWERS ONLY SOLUTION MANUAL (Clean Section Walkthrough & Answers)
# ==============================================================================
def build_answers_only_file():
    doc = Document()
    add_header_footer(doc, "Reading Guide: Complete Answers & Section Walkthrough")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36); p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("CO-AUTHOR READING COMPANION: COMPLETE ANSWERS & WALKTHROUGH")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Paper 1 Reading Companion:\nComplete Section-by-Section Explanations and Answers")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(22); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "A Comprehensive Reference Guide with Full 1-Page Answers (500–700 Words Each) Explaining the Mathematics, "
        "Economic Intuition, and Real-World Findings of 'What Prices Cannot Tell a Market Supervisor'"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(12.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=6, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Primary Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Document Edition", "Complete Answers & Walkthrough Edition (Contains Full 1-Page Explanations for all 12 Modules)"),
        ("Lead Author & PI", "Pratik Niroula (Department of Computer Information Science, Minnesota State University, Mankato)"),
        ("Contributing Co-Authors", "Sujan Khatiwada (Dept. of Electrical, Computer & Robotics Engineering, MNSU Mankato)\nPrashant Niroula (Faculty of Management, Tribhuvan University, Kirtipur, Nepal)"),
        ("Scope of Answers", "Provides full mathematical derivations, real-world data explanations (CFTC & Binance), and clear summaries."),
        ("Formal Verification State", "787 Lean 4 Kernel-Verified Declarations across 81 Modules; 0 sorry; Mathlib Standard Axioms")
    ]
    for i, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(i, 0); c1 = meta_box.cell(i, 1)
        c0.width = Inches(2.0); c1.width = Inches(4.5)
        set_cell_background(c0, "F8FAFC"); set_cell_background(c1, "FFFFFF")
        set_cell_borders(c0, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                              left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_borders(c1, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                              left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9.5); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9.5); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(12); sp.paragraph_format.space_after = Pt(4)
    add_callout(
        doc,
        [
            "\"This companion guide gives you complete, detailed walkthroughs for all 12 reading questions in our workbook. "
            "Use this guide as you read each section of the paper to see step-by-step mathematical explanations, "
            "the economic intuition behind each proof, and how our empirical tests in CFTC futures and Binance perpetuals work.\"",
            "— Co-Author Study & Reference Standard"
        ],
        title="ABOUT THIS READING COMPANION",
        alert_type="info"
    )
    doc.add_page_break()

    # Section 1: Executive Study Architecture
    p_s1 = doc.add_paragraph(); style_heading_1(p_s1); p_s1.add_run("1. How to Use this Walkthrough Guide")
    p_b1 = doc.add_paragraph()
    style_body(
        p_b1,
        "Structure of Each Explanation: ",
        "For each of the 12 modules, this guide provides a full 1-page detailed answer (approx. 500–700 words) broken into three clear parts:\n"
        "• Part 1: How the Math and Model Work — A clear step-by-step walkthrough of the equations, transfer functions, and derivations.\n"
        "• Part 2: Economic Intuition & Market Reality — What the math means in actual financial markets, citing our CFTC and Binance findings.\n"
        "• Part 3: Main Takeaway & How to Explain It — A concise summary of the bottom line and how to explain it simply to colleagues or reviewers."
    )
    
    # Import the answers database
    from workbook_answers import ANSWERS
    
    # 12 Modules with Clean Model Answers
    for q in READING_MODULES:
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Module {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Where to Read in Paper": q["reading_ref"],
            "Key Mathematical Focus": q["key_objects"]
        })
        
        p_pr_hdr = doc.add_paragraph(); style_heading_3(p_pr_hdr); p_pr_hdr.add_run("The Core Reading Question Answered Below")
        p_pr = doc.add_paragraph(); style_body(p_pr, "Question: ", q["question"], italic=True)
        
        # Full Comprehensive Model Answer
        q_ans = ANSWERS.get(q["num"], {})
        
        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, ANSWER_BG)
        set_cell_borders(cell, top=("single", "16", "0", NAVY_PRIMARY), bottom=("single", "16", "0", NAVY_PRIMARY),
                               left=("single", "16", "0", NAVY_PRIMARY), right=("single", "16", "0", NAVY_PRIMARY))
        set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
        
        cp = cell.paragraphs[0]; cp.paragraph_format.space_before = Pt(0); cp.paragraph_format.space_after = Pt(4)
        r_hdr = cp.add_run(f"COMPLETE EXPLANATION & WALKTHROUGH: MODULE {q['num']}\n")
        r_hdr.font.name = "Calibri"; r_hdr.font.size = Pt(11); r_hdr.font.bold = True; r_hdr.font.color.rgb = RGB_NAVY
        
        # Friendly Section Titles
        sec_mapping = {
            "Part A: Formal Mathematical Derivation & Proof Reconstruction": "1. How the Math and Model Work (Step-by-Step Derivation)",
            "Part B: Economic Mechanism, Institutional Interpretation & Empirical Analysis": "2. Economic Intuition & Market Reality (What the Data Show)",
            "Part C: Critical Review, Boundary Conditions & Journal Defense Strategy": "3. Main Takeaway & How to Explain It Clearly"
        }
        
        for old_sec_key, sec_text in q_ans.items():
            new_sec_key = sec_mapping.get(old_sec_key, old_sec_key)
            sp_title = cell.add_paragraph(); sp_title.paragraph_format.space_before = Pt(8); sp_title.paragraph_format.space_after = Pt(2)
            r_st = sp_title.add_run(new_sec_key); r_st.font.name = "Calibri"; r_st.font.size = Pt(10); r_st.font.bold = True; r_st.font.color.rgb = RGB_SLATE
            
            sp_body = cell.add_paragraph(); sp_body.paragraph_format.space_before = Pt(0); sp_body.paragraph_format.space_after = Pt(4)
            sp_body.paragraph_format.line_spacing = 1.15
            r_sb = sp_body.add_run(sec_text)
            r_sb.font.name = "Calibri"; r_sb.font.size = Pt(9.5); r_sb.font.color.rgb = RGB_CHARCOAL

        doc.add_page_break()

    # Final Attribution and Research Ethics Declaration
    p_end = doc.add_paragraph(); style_heading_1(p_end); p_end.add_run("Summary & Co-Author Collaboration Notes")
    p_et = doc.add_paragraph()
    style_body(
        p_et,
        "Collaborative Research Foundation: ",
        "This reading walkthrough provides our shared technical foundation for Paper 1. With these detailed explanations, "
        "Sujan, Prashant, and Pratik are fully equipped to walk through any section of the manuscript, explain every equation, "
        "and present our findings with clarity and precision."
    )
    
    out_path = Path("Paper1_Answers_Solution_Manual.docx")
    doc.save(str(out_path))
    doc.save(str(ROOT / "ceiling_suite/papers/paper1/Paper1_Answers_Solution_Manual.docx"))
    doc.save(str(ROOT / "ceiling_suite/paper1/Paper1_Answers_Solution_Manual.docx"))
    print(f"Built Answers Only Solution Manual: {out_path.resolve()}")

if __name__ == "__main__":
    build_questions_only_file()
    build_answers_only_file()
