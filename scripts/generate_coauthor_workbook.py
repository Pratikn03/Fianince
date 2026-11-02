"""
Full script to generate the comprehensive, PhD-level Co-Author Mastery & Contribution Workbook
for Sujan Khatiwada and Prashant Niroula on Paper 1:
"What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"
"""

import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

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

RGB_NAVY = RGBColor(11, 37, 69)
RGB_SLATE = RGBColor(19, 64, 116)
RGB_STEEL = RGBColor(0, 119, 182)
RGB_CHARCOAL = RGBColor(29, 45, 68)
RGB_CRIMSON = RGBColor(141, 8, 1)
RGB_MUTED = RGBColor(100, 116, 139)

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
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGB_NAVY

def style_heading_2(p):
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(13)
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
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGB_CHARCOAL
    if text:
        r_txt = p.add_run(text)
        r_txt.font.name = "Calibri"
        r_txt.font.size = Pt(10.5)
        r_txt.font.italic = italic
        r_txt.font.color.rgb = RGB_CHARCOAL

def add_header_footer(doc):
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
        # Header
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Machine Markets Research Project | Co-Author Mastery & Contribution Workbook")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor — Confidential Doctoral Research Workbook")
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
    border_color = ALERT_CRIMSON if alert_type == "alert" else STEEL_BLUE
    set_cell_borders(cell, left=("single", "24", "0", border_color),
                           top=("single", "4", "0", LIGHT_BORDER),
                           right=("single", "4", "0", LIGHT_BORDER),
                           bottom=("single", "4", "0", LIGHT_BORDER))
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(4)
    if title:
        rt = cp.add_run(title + "\n")
        rt.font.name = "Calibri"
        rt.font.size = Pt(11)
        rt.font.bold = True
        rt.font.color.rgb = RGB_CRIMSON if alert_type == "alert" else RGB_NAVY
        
    for item in text_list:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(item)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
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
        
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = RGB_SLATE
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGB_CHARCOAL
        
        row_idx += 1
        
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_response_box(doc, q_num, title, target_lead):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"Co-Author Written Response Workspace — Question {q_num}")
    r.font.name = "Calibri"
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGB_NAVY
    
    desc = doc.add_paragraph()
    desc.paragraph_format.space_before = Pt(0)
    desc.paragraph_format.space_after = Pt(4)
    r_desc = desc.add_run(
        f"MANDATORY REQUIREMENT: Provide a comprehensive, doctoral-level written response (minimum 1 full page, "
        f"400–600+ words). Address all parts of the master prompt and sub-questions above. Include formal mathematical "
        f"expressions, citations to equations/tables in the paper, and explicit recommendations for journal referee defense. "
        f"Lead Reviewer: {target_lead}."
    )
    r_desc.font.name = "Calibri"
    r_desc.font.size = Pt(9.5)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGB_MUTED

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "FAFAFA")
    set_cell_borders(cell, top=("single", "12", "0", SLATE_SECONDARY),
                           bottom=("single", "12", "0", SLATE_SECONDARY),
                           left=("single", "12", "0", SLATE_SECONDARY),
                           right=("single", "12", "0", SLATE_SECONDARY))
    set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
    
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(4)
    r_hdr = cp.add_run(f"WRITTEN SUBMISSION FOR QUESTION {q_num}: {title.upper()}\n")
    r_hdr.font.name = "Calibri"
    r_hdr.font.size = Pt(10)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = RGB_SLATE
    
    sections = [
        ("Part A: Formal Mathematical Derivation & Proof Reconstruction",
         "[Type detailed mathematical derivations, transfer function manipulations, Taylor expansions, or moment-matching steps here... (approx. 150-200 words)]"),
        ("Part B: Economic Mechanism, Institutional Interpretation & Empirical Analysis",
         "[Type detailed analysis of microstructure incentives, market impact, CFTC/Binance data findings, and test scorecard results here... (approx. 150-200 words)]"),
        ("Part C: Critical Review, Boundary Conditions & Journal Defense Strategy",
         "[Type evaluation of assumptions, unformalized frontiers, potential referee objections, and suggested manuscript enhancements here... (approx. 150-200 words)]")
    ]
    
    for sec_title, placeholder in sections:
        sp_title = cell.add_paragraph()
        sp_title.paragraph_format.space_before = Pt(6)
        sp_title.paragraph_format.space_after = Pt(2)
        r_st = sp_title.add_run(sec_title)
        r_st.font.name = "Calibri"
        r_st.font.size = Pt(9.5)
        r_st.font.bold = True
        r_st.font.color.rgb = RGB_STEEL
        
        sp_body = cell.add_paragraph()
        sp_body.paragraph_format.space_before = Pt(0)
        sp_body.paragraph_format.space_after = Pt(6)
        r_sb = sp_body.add_run(placeholder + "\n\n\n\n\n\n")
        r_sb.font.name = "Calibri"
        r_sb.font.size = Pt(9.5)
        r_sb.font.italic = True
        r_sb.font.color.rgb = RGBColor(160, 160, 160)

    # Page break after each question to ensure each question is a distinct 1-page assignment
    doc.add_page_break()

def build_workbook():
    doc = Document()
    add_header_footer(doc)
    
    # ==========================================
    # COVER / TITLE PAGE
    # ==========================================
    p_title_pre = doc.add_paragraph()
    p_title_pre.paragraph_format.space_before = Pt(36)
    p_title_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_title_pre.add_run("DOCTORAL RESEARCH & CO-AUTHOR CONTRIBUTION WORKBOOK")
    r_pre.font.name = "Calibri"
    r_pre.font.size = Pt(13)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Machine Markets Research Project:\nComprehensive Co-Author Mastery & Critical Review Assignment")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "A Rigorous, Chapter-by-Chapter Analytical Inquiry on Theoretical Proofs, System Dynamics, "
        "Empirical Evidence, and Lean 4 Formalization for Co-Authors Sujan Khatiwada and Prashant Niroula"
    )
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGB_SLATE

    # Metadata block
    meta_box = doc.add_table(rows=6, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_box.autofit = False
    
    meta_items = [
        ("Primary Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Companion Framework", "From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard"),
        ("Lead Author & PI", "Pratik Niroula (Department of Computer Information Science, Minnesota State University, Mankato)"),
        ("Contributing Co-Authors", "Sujan Khatiwada (Dept. of Electrical, Computer and Robotics Engineering, MNSU Mankato)\nPrashant Niroula (Faculty of Management, Tribhuvan University, Kirtipur, Nepal)"),
        ("Target Submission Venues", "Econometrica / Journal of Finance / Quantitative Economics / Western Finance Association (WFA) 2027"),
        ("Formal Verification State", "787 Lean 4 Kernel-Verified Declarations across 81 Modules; 0 sorry; Mathlib 4.34.1 Standard Axioms")
    ]
    
    for i, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(i, 0)
        c1 = meta_box.cell(i, 1)
        c0.width = Inches(2.0)
        c1.width = Inches(4.5)
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "FFFFFF")
        set_cell_borders(c0, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                              left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_borders(c1, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                              left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9.5); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9.5); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(12)
    sp.paragraph_format.space_after = Pt(4)
    
    add_callout(
        doc,
        [
            "\"A co-author who cannot defend every equation, every proof boundary, every failure mode, and every institutional table of the manuscript is merely a passive spectator. This workbook guarantees that Sujan Khatiwada and Prashant Niroula achieve full mastery, intellectual ownership, and decisive co-authorship equity across all dimensions of the Machine Markets research program.\"",
            "— Research Integrity & Publication Standard (November 2026 Revision)"
        ],
        title="EXECUTIVE CO-AUTHORSHIP DIRECTIVE",
        alert_type="alert"
    )
    
    doc.add_page_break()
    
    # ==========================================
    # SECTION 1: INSTRUCTIONS & METHODOLOGICAL ARCHITECTURE
    # ==========================================
    p_sec1 = doc.add_paragraph()
    style_heading_1(p_sec1)
    p_sec1.add_run("1. Executive Instructions & Methodological Guidelines")
    
    p_body = doc.add_paragraph()
    style_body(
        p_body,
        "Purpose of this Workbook: ",
        "This document is a formal, doctoral-level research engagement workbook designed to accompany the completed "
        "manuscripts of Paper 1 and Paper 2. It contains 12 comprehensive analytical modules covering every mathematical theorem, "
        "dynamical systems derivation, empirical econometric test, institutional dataset, and Lean 4 formalization module in the project. "
        "Its explicit goal is to ensure that both co-authors—Sujan Khatiwada and Prashant Niroula—thoroughly study the entire paper, "
        "understand its exact mechanics, and produce substantive, high-level written contributions that directly enhance the paper and "
        "prepare our team for the most hostile referee reports from top-tier journals."
    )
    
    p_req = doc.add_paragraph()
    style_heading_2(p_req)
    p_req.add_run("Rigorous Submission Standards for Each Question")
    
    requirements = [
        ("Minimum Page-Length Requirement: ", "Each of the 12 questions demands an exhaustive, highly technical written submission of at least one full page (approximately 400 to 600 words per question). Point-form summaries or superficial generalities will not be accepted."),
        ("Mathematical & Mechanical Precision: ", "Responses must explicitly cite and manipulate the mathematical equations, transfer functions, state-space representations, and moment bounds of the paper. Re-derive intermediate steps rather than paraphrasing high-level claims."),
        ("Institutional & Empirical Grounding: ", "Where questions address empirical tests, responses must cite exact market names, sample sizes, bootstrap intervals, Clark-West / Diebold-Mariano test statistics, and the pre-specified scorecard from Table 9."),
        ("Critical Defense & Referee Preparation: ", "Every response must address potential weaknesses, restrictive assumptions, unformalized frontiers, or econometric identification concerns that an aggressive referee at Econometrica or the Journal of Finance will raise.")
    ]
    for bold_pre, text_body in requirements:
        p_item = doc.add_paragraph(style='List Bullet')
        p_item.paragraph_format.space_before = Pt(2)
        p_item.paragraph_format.space_after = Pt(3)
        style_body(p_item, bold_pre, text_body)
        
    p_div = doc.add_paragraph()
    style_heading_2(p_div)
    p_div.add_run("Co-Author Division of Labor & Domain Specialization")
    
    div_table = doc.add_table(rows=3, cols=3)
    div_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    div_table.autofit = False
    
    headers = ["Co-Author", "Primary Research Domain", "Core Assigned Modules & Leadership Role"]
    for j, h in enumerate(headers):
        cell = div_table.cell(0, j)
        set_cell_background(cell, NAVY_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]; r = p.add_run(h); r.font.name = "Calibri"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    div_data = [
        ("Sujan Khatiwada\n(Electrical, Computer & Robotics Engineering)",
         "Dynamical Systems, Control Theory, Transfer Functions, State-Space Realizations, Hankel Matrices, Non-Normal Pseudospectra, Lean 4 Interactive Theorem Proving",
         "Lead Reviewer on Modules 1, 3, 5, 10, 12; Joint Lead on Modules 2, 6, 11.\nFocus: Exact mathematical proofs, spectral analysis, noise decoupling, and kernel-checked formalization."),
        ("Prashant Niroula\n(Faculty of Management, Tribhuvan University)",
         "Financial Economics, Market Microstructure, Regulatory Architecture, CFTC & Binance Datasets, Pre-Specified Econometric Testing, Failure Diagnostics, Policy Implications",
         "Lead Reviewer on Modules 4, 7, 8, 9; Joint Lead on Modules 2, 6, 11.\nFocus: Institutional realities, trading incentives, macroprudential capital rules, within-class sign cancellation, and MiFID II RTS 24 audit trails.")
    ]
    
    for i, (author, domain, roles) in enumerate(div_data):
        row = i + 1
        for j, text_val in enumerate([author, domain, roles]):
            cell = div_table.cell(row, j)
            set_cell_background(cell, "FFFFFF" if row % 2 == 1 else "F8FAFC")
            set_cell_borders(cell, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                                  left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]; r = p.add_run(text_val); r.font.name = "Calibri"; r.font.size = Pt(9); r.font.color.rgb = RGB_CHARCOAL
            if j == 0:
                r.font.bold = True; r.font.color.rgb = RGB_SLATE

    sp2 = doc.add_paragraph()
    sp2.paragraph_format.space_before = Pt(8)
    sp2.paragraph_format.space_after = Pt(4)
    doc.add_page_break()

    # ==========================================
    # 12 DETAILED QUESTION MODULES
    # ==========================================
    
    QUESTIONS = [
        {
            "num": 1,
            "title": "The Closed-Loop Transfer Function and the Fundamental Identification Boundary",
            "lead": "Sujan Khatiwada (Dynamical Systems Lead)",
            "sections": "Paper 1: Section 2 (Model and Motivating Examples), Appendices A & B",
            "equations": "Eq. (1)-(8), Lemma 2.1, Lemma 2.2, Transfer Functions H(z) and G(z)",
            "lean": "p1_thm_merged_exact, p1_transfer_function_degree, p1_closed_loop_feedback",
            "context": (
                "In Section 2, the paper models a limit order book populated by K heterogeneous trader cohorts. Each cohort k exhibits "
                "an exponential memory kernel with persistence parameter η_k ∈ [0,1) and portfolio weight w_k > 0 (summing to 1). "
                "Traders submit orders based on perceived mispricing y_{k,t} = w_k(p* - x_{k,t}), where the state evolves as "
                "x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1}. When aggregated through market depth (Kyle's impact parameter κ > 0) "
                "and residual dealer inventory damping q > 0, the open-loop transfer function H(z) = ∑_{k=1}^K w_k / (1 - η_k z^{-1}) "
                "is embedded inside the closed-loop feedback transfer function G(z) = κ H(z) / (1 + κ q H(z)). "
                "A supervisor observing only aggregate equilibrium transaction prices p_t sees only the closed-loop transfer function."
            ),
            "prompt": (
                "Conduct a rigorous mathematical and control-theoretic analysis of the fundamental identification boundary between open-loop "
                "trader parameters {w_k, η_k}_{k=1}^K and closed-loop price dynamics G(z). Specifically explain why standard econometric time-series "
                "techniques (such as autoregressive pole fitting or ARIMA estimation on prices) completely fail to recover internal memory rates, "
                "and prove why transmission zeros of the open-loop plant are obscured by the feedback denominator."
            ),
            "subquestions": [
                "Derive the exact state-space realization (A, B, C, D) of the K-cohort trader population and demonstrate the transformation between the open-loop poles and the closed-loop system eigenvalues λ_i(A_{cl}).",
                "Explain the algebraic distinction between the transmission zeros of H(z) and the poles of the closed-loop transfer function G(z). Why do the internal memory rates η_k enter as zeros of the return response rather than uncoupled poles?",
                "Prove why fitting autoregressive poles to price changes Δp_t identifies only the closed-loop eigenvalues of the entire coupled market system, and why infinitely many combinations of (w_k, η_k, κ, q) can produce the exact same closed-loop pole locations.",
                "How does Theorem 2.1 (Merged Measure Invariance) formally establish that two distinct trader populations with different cohort counts and memory distributions produce identical noise-free price trajectories if and only if their merged measures coincide on 2K+1 periods?"
            ],
            "citations": "Equations (1)–(8), Lemma 2.1, Lemma 2.2, Theorem 2.1, Figure 1 (Impulse Response Comparison), and Lean module p1_transfer_function_degree.",
            "sujan_prompt": "Evaluate this from a control systems / robotics perspective: How does feedback masking in this financial market parallel the classical unobservability and zero-pole cancellation problems in state estimation under feedback controllers?",
            "prashant_prompt": "Evaluate this from a market microstructure perspective: What does it mean economically that a market supervisor observing prices cannot tell whether a flash crash or price cascade is driven by two moderate-speed institutional algorithmic desks or five hyper-fast HFT market-makers?"
        },
        {
            "num": 2,
            "title": "Moment Indistinguishability and the Θ(σ²(Δη)^{-(4K-2)}) Minimax Lower Bound",
            "lead": "Joint Lead: Sujan Khatiwada & Prashant Niroula",
            "sections": "Paper 1: Section 3.1 (Near-Colliding Rates: A Uniform Rate), Appendix B (Proof of Theorem 3.1)",
            "equations": "Theorem 3.1, Theorem 3.2, Proof of Theorem 3.1, Le Cam's Two-Point Inequality",
            "lean": "p1_thm_merged_general_alpha, p1_thm_kcohort_lower, p1_le_cam_divergence",
            "context": (
                "Theorem 3.1 establishes the foundational lower bound of the paper: for K trader cohorts with minimum memory spacing "
                "Δη = min_{j ≠ k} |η_j - η_k|, no estimator—whether biased or unbiased, linear or non-linear—can separate two candidate "
                "trader populations with error probabilities below 1/4 using fewer than N* = Ω(σ² (Δη)^{-(4K-2)}) experiments. "
                "For K = 2 cohorts, this yields an explosion rate of (Δη)^{-6}; for K = 3, the exponent collapses to (Δη)^{-10}. "
                "This lower bound is proved using Le Cam's two-point testing method over a specially constructed pair of Radon measures "
                "whose moments match up to order 2K - 1."
            ),
            "prompt": (
                "Provide an exhaustive, PhD-level reconstruction of the proof of Theorem 3.1. Detail the exact construction of the moment-matched "
                "Radon measures, explain how the Gauss-Radau and Chebyshev quadrature rules produce identical low-order moments, and derive "
                "step-by-step why the Kullback-Leibler divergence between the resulting Gaussian price measures vanishes at order (Δη)^{4K-2}."
            ),
            "subquestions": [
                "Reconstruct the mathematical construction of the two competing economies μ_0 and μ_1. Why is it necessary that the first 2K - 1 moments of the measure match exactly: ∫ x^j dμ_0(x) = ∫ x^j dμ_1(x) for j = 0, 1, ..., 2K - 1?",
                "Derive the Taylor series expansion of the difference in impulse responses Δh_t = h_t(μ_0) - h_t(μ_1). Show how the vanishing of the first 2K - 1 moments forces the leading non-zero term to be of order (Δη)^{2K-1}.",
                "Write down the Gaussian Kullback-Leibler divergence formula D_{KL}(P_0 || P_1) = (1/2σ²) ∑_{t=1}^T (Δh_t)². Prove that this sum scales exactly as O(T (Δη)^{4K-2}).",
                "Apply Le Cam's two-point inequality (or Pinsker's inequality) to show that to achieve total variation distance TV(P_0, P_1) ≥ 1/2 (guaranteeing minimax testing error below 1/4), the required sample size N must scale as Ω(σ² (Δη)^{-(4K-2)}).",
                "For K = 2, calculate the numerical consequence: If memory spacing Δη is halved from 0.10 to 0.05, by what exact factor does the required observation sample size multiply? What about for K = 3?"
            ],
            "citations": "Theorem 3.1, Theorem 3.2, Lemmas B.1–B.4, Table 1 (Moment Matching Table), and Lean modules p1_thm_kcohort_lower and p1_le_cam_divergence.",
            "sujan_prompt": "Connect this derivation to the conditioning of polynomial interpolation and Vandermonde systems: Why is this moment-matching lower bound an intrinsic information-theoretic property of linear dynamical systems rather than a flaw in the chosen estimator?",
            "prashant_prompt": "Explain the profound economic consequence of the (Δη)^{-6} and (Δη)^{-10} rates: Why does this mathematically prove that supervisors can never resolve fine-grained algorithmic differences from public price tapes alone?"
        },
        {
            "num": 3,
            "title": "Hankel Matrix Deconvolution, Singular Value Lower Bounds, and Prony's Minimax Upper Bound",
            "lead": "Sujan Khatiwada (Signal Processing & Algorithms Lead)",
            "sections": "Paper 1: Section 3.2 (The Matching Upper Bound), Algorithm 1, Appendix B",
            "equations": "Theorem 3.2, Proposition 3.3, Algorithm 1 (Prony-Hankel Deconvolution), Hankel matrix H_m",
            "lean": "p1_prop_esprit_upper, p1_hankel_singular_value, p1_prony_root_stability",
            "context": (
                "While Theorem 3.1 proves that separating trader populations requires at least Ω(σ² (Δη)^{-(4K-2)}) observations, "
                "Theorem 3.2 and Proposition 3.3 establish that this rate is minimax optimal: a concrete algorithm based on Hankel matrix "
                "deconvolution and Prony's polynomial root method recovers all internal memory rates η_k and weights w_k to accuracy "
                "C √(log(4K/β)) ε_N, achieving the matching upper bound O(σ² (Δη)^{-(4K-2)}) without requiring advance knowledge of the true spacing Δη. "
                "The proof hinges on bounding the smallest singular value σ_{min}(H_m) of the Hankel matrix formed from estimated impulse responses."
            ),
            "prompt": (
                "Analyze the mechanics and stability of the Prony-Hankel deconvolution algorithm. Detail how the algorithm constructs the "
                "Hankel matrix from estimated impulse response coefficients, prove the lower bound on its smallest singular value as a function "
                "of Δη, and analyze how root-finding on the characteristic polynomial P(z) = ∏_{k=1}^K (z - η_k) achieves minimax optimal recovery."
            ),
            "subquestions": [
                "Formulate Algorithm 1 explicitly: How is the m × m Hankel matrix H_m defined in terms of the estimated impulse responses h_t? What are the exact dimensions required in terms of K?",
                "Provide the algebraic derivation of the factorization H_m = V_K diag(w_1, ..., w_K) V_K^T, where V_K is a Vandermonde matrix on the nodes (η_1, ..., η_K).",
                "Prove how the smallest singular value σ_{min}(H_m) scales with the minimum node separation Δη: Why does σ_{min}(H_m) ≥ c (Δη)^{2K-1} hold?",
                "Explain the matrix perturbation analysis: Under sub-Gaussian price noise with variance σ²/N, how does a perturbation in H_m translate into a perturbation in the roots of the characteristic polynomial P(z)?",
                "Why does ordinary linear least squares regression fail to achieve this bound, and why is non-linear polynomial root extraction strictly necessary to achieve minimax optimality?"
            ],
            "citations": "Theorem 3.2, Proposition 3.3, Algorithm 1, Lemma B.5, Table 3 (Prony vs. OLS Error Comparison), and Lean module p1_prop_esprit_upper.",
            "sujan_prompt": "Relate Prony's method and ESPRIT to high-resolution sensor array processing in robotics: How does the conditioning of the Hankel matrix govern signal subspace resolution when two signal sources are close in spatial or frequency domain?",
            "prashant_prompt": "Evaluate the computational feasibility of this estimator for an exchange or regulatory agency: Can this deconvolution run in near real-time on live message streams, or is it strictly an ex-post forensic audit tool?"
        },
        {
            "num": 4,
            "title": "Probing Capital, Margin Solvency, and the Θ(δ^{-4}) Financial Lower Bound",
            "lead": "Prashant Niroula (Financial Economics & Capital Dynamics Lead)",
            "sections": "Paper 1: Section 4 (Account-Level Capital and Probing Costs), Appendices B & C",
            "equations": "Theorem 4.1, Theorem 4.3, Lemma 4.2 (Toeplitz Quadratic Form), Margin Constraint B",
            "lean": "p1_thm_quantity_general_alpha, p1_thm_capital_general_alpha, p1_lem_toeplitz",
            "context": (
                "Section 4 translates information-theoretic sample complexity into hard currency and regulatory balance-sheet constraints. "
                "An active observer (such as a regulatory supervisor, central bank desk, or predatory liquidity seeker) attempts to identify "
                "unknown trader algorithms by injecting test orders (probes) v = (v_1, ..., v_T)^T into the order book. "
                "Theorem 4.1 proves that any active probe with total executed volume V = ||v||_1 gives divergence at most K_*² V² δ⁴ / (2σ²). "
                "Furthermore, Lemma 4.2 shows that executing against a linear book costs a positive-definite Toeplitz quadratic form "
                "(1/2) v^T T_H v, ensuring no round-trip probe can yield a sure gain. "
                "Finally, Theorem 4.3 proves that a counterparty maintaining mark-to-market margin solvency requires capital B ≥ σ² m / (4K_*² δ⁴)."
            ),
            "prompt": (
                "Provide an exhaustive financial and mathematical analysis of the capital cost of market probing. Explain why information "
                "resolution scales as the fourth power of memory spacing (δ^{-4}), prove that the execution cost matrix is strictly positive definite, "
                "and evaluate the balance-sheet capital required for an institution to probe hidden algorithmic traders."
            ),
            "subquestions": [
                "Derive the Toeplitz execution cost matrix T_H in terms of Kyle's lambda κ and the cohort memory parameters. Prove Lemma 4.2: Why is v^T T_H v > 0 for every non-zero round-trip probing sequence v with ∑ v_t = 0?",
                "Explain the economic meaning of the no-sure-gain property: Why does this rule out 'free lunch' exploratory probing by proprietary trading firms or regulators?",
                "Derive the capital lower bound of Theorem 4.3: Why does margin solvency at the fundamental mark force the probing desk's cash reserve B to satisfy B ≥ Ω(σ² / δ⁴)?",
                "Explain the scaling law: If the memory difference between two competing algorithmic trading groups is halved (δ → δ/2), why does the capital required to tell them apart multiply by sixteen (2⁴ = 16)?",
                "Analyze the 'Disclosure in Dollars' benchmark from Section 4.3 and Table 4: How does the paper calculate that re-learning two unknown algorithms each week costs between $15 million and $356 million per year per market?"
            ],
            "citations": "Theorem 4.1, Lemma 4.2, Theorem 4.3, Table 4 (Probing Capital vs. Spacing), and Lean modules p1_thm_capital_general_alpha and p1_lem_toeplitz.",
            "prashant_prompt": "Analyze this from a macroprudential perspective: If an active supervisor must hold millions in margin capital just to identify algorithmic types via probing, what does this imply about the economic necessity of regulatory audit trails versus market-based surveillance?",
            "sujan_prompt": "Examine the dynamic control aspect: How does the Toeplitz cost matrix penalize high-frequency exploratory probing compared to low-frequency signals, and what is the optimal probing trajectory under an LQR-style energy constraint?"
        },
        {
            "num": 5,
            "title": "Passive Observational Data vs. Active Probing: Whittle Spectral Divergence and Asymptotic Rate Limits",
            "lead": "Sujan Khatiwada (Ergodic Theory & Spectral Divergence Lead)",
            "sections": "Paper 1: Section 4.4 (Passive Data), Section 5.8 (Passive Whittle Divergence), Appendix B",
            "equations": "Theorem 5.8 (Theorem S14), Whittle Likelihood on [-π, π], Spectral Density f(λ)",
            "lean": "p1_prop_passive_whittle, p1_spectral_density_bound, p1_whittle_divergence_integral",
            "context": (
                "Instead of actively sending test orders, a supervisor or econometrician might choose to remain entirely passive, "
                "observing only the natural price fluctuations generated by ambient market noise. "
                "Theorem 5.8 (Theorem S14) investigates the asymptotic rate limit of passive observation using the Whittle spectral divergence "
                "for stationary Gaussian processes as T → ∞. The paper proves that the Kullback-Leibler divergence rate per observation "
                "lim_{T→∞} (1/T) D_{KL}(P_0 || P_1) = (1/4π) ∫_{-π}^π [ (f_0(λ) - f_1(λ))² / (f_0(λ) f_1(λ)) ] dλ scales as O((Δη)^{4K-2}). "
                "Consequently, passive data can never overcome the active probing lower bound: waiting and watching costs time at the exact same "
                "catastrophic rate."
            ),
            "prompt": (
                "Provide a rigorous mathematical analysis of the passive data observation frontier. Compare active probing with passive "
                "spectral observation, derive the Whittle spectral divergence rate limit, and prove why natural market excitation is fundamentally "
                "incapable of circumventing the minimax sample complexity explosion."
            ),
            "subquestions": [
                "Formulate the spectral density f(λ) of the observed price process under ambient Gaussian white noise shocks. How does the closed-loop transfer function G(e^{iλ}) shape the power spectrum of returns?",
                "Derive the Whittle spectral divergence integral formula on [-π, π]. Show how the discrepancy in spectral densities |f_0(λ) - f_1(λ)| relates to the transfer function difference |G_0(e^{iλ}) - G_1(e^{iλ})|.",
                "Prove why the L_2 integral of the spectral difference over [-π, π] collapses at rate O((Δη)^{4K-2}) when the two candidate economies have matched low-order moments.",
                "Explain the physical intuition: Active probing allows the observer to focus energy on the most revealing frequencies, whereas passive observation relies on ambient noise. Why does this imply that passive observation requires at least as many samples as active probing, and often orders of magnitude more?",
                "Discuss the ergodic assumptions required for this Whittle rate limit to hold, and identify why Mathlib 4.34.1 currently treats this theorem as a formalization frontier (requiring measure-preserving ergodic dynamical systems)."
            ],
            "citations": "Theorem 5.8, Proposition S14, Lemmas B.8–B.10, Figure 6 (Spectral Divergence Curves), and Lean module p1_prop_passive_whittle.",
            "sujan_prompt": "Evaluate this from an engineering system identification perspective: In classical adaptive control, what is the role of 'persistent excitation', and why does passive market data provide insufficient excitation in the frequency bands needed to separate near-colliding poles?",
            "prashant_prompt": "Connect this to regulatory reality: Why does this theorem prove that a supervisor who refuses to mandate account-level reporting cannot compensate by simply accumulating years of high-frequency tick data?"
        },
        {
            "num": 6,
            "title": "Empirical Noise Robustness (Real Bitcoin Price Returns) vs. Minimax Collapse under Completely Monotone Kernels",
            "lead": "Joint Lead: Sujan Khatiwada & Prashant Niroula",
            "sections": "Paper 1: Section 4.5 (Do the Rates Survive Real Market Noise?), Section 5.7 (General Memory), Appendix C",
            "equations": "Theorem 5.7, Table 6 (Real Noise Injection), Figure 5, Exact Multinomial Count Identity",
            "lean": "p1_thm_general_memory_lower, p1_thm_general_memory_upper, p1_exact_multinomial_resampling",
            "context": (
                "Section 4.5 and Section 5.7 subject the theory to two extreme stress-tests: (1) Replacing idealized Gaussian noise with real, "
                "heavy-tailed 1-minute Bitcoin return shocks; and (2) Relaxing the finite-cohort exponential assumption to completely general, "
                "continuous memory distributions (completely monotone kernels). "
                "In the real-noise injection test, exact empirical multinomial resampling (without normal approximations) confirms that the "
                "price-only sample requirement grows with fitted log-log slopes of -6.01 for K = 2 (theory -6) and -9.81 for K = 3 (theory -10), "
                "while class-tagged requirements remain flat. However, Theorem 5.7 proves that if memory is an arbitrary completely monotone kernel, "
                "the minimax rate collapses from polynomial (Δη)^{-(4K-2)} to logarithmic 1 / log(N/σ²), requiring exponential sample size exp(Θ(1/w))!"
            ),
            "prompt": (
                "Synthesize the findings of these two stress-tests. Explain why the polynomial rate survives real-world fat-tailed price noise under "
                "exact empirical resampling, and contrast this with the profound mathematical collapse that occurs when the trader memory kernel "
                "transitions from a discrete mixture of exponentials to a general continuous memory spectrum."
            ),
            "subquestions": [
                "Describe the exact multinomial resampling procedure used in the real Bitcoin price noise test (Section 4.5). Why was it critical to eliminate the normal approximation for large sample sizes N?",
                "Analyze the empirical log-log regression results in Table 6: Why do the fitted slopes of -6.01 (for K = 2) and -9.81 (for K = 3) provide such extraordinary validation of the theoretical lower bound exponents 4K - 2?",
                "Define a completely monotone memory kernel k(t) = ∫_0^1 e^{-λ t} dF(λ) according to Bernstein's Theorem. What does this represent economically in terms of continuous distributions of learning horizons?",
                "Reconstruct the proof of Theorem 5.7: How does approximation theory on compact intervals show that the minimax separation rate deteriorates to w = Θ(1 / log(N/σ²))?",
                "Explain the dramatic economic contrast: Why does discrete cohort identification require polynomial data (N ≈ δ^{-6}), whereas identifying continuous memory distributions requires astronomical, exponential data (N ≈ e^{1/w})?"
            ],
            "citations": "Theorem 5.7, Table 6 (Real-Noise Injection Table), Figure 5 (Slope Comparison), Bernstein's Theorem, and Lean modules p1_thm_general_memory_lower and p1_thm_general_memory_upper.",
            "sujan_prompt": "Analyze the functional analysis behind Theorem 5.7: How does the ill-posedness of the inverse Laplace transform explain why recovering a continuous memory distribution F(λ) suffers an exponential information loss compared to recovering discrete poles?",
            "prashant_prompt": "Discuss the institutional implications: In real financial markets where thousands of algorithms operate on heterogeneous timeframes (from microseconds to months), does this logarithmic collapse imply that recovering the aggregate market memory distribution is practically impossible without disclosure?"
        },
        {
            "num": 7,
            "title": "The Value of Class-Tagged Disclosure and Algorithmic Audit Trails",
            "lead": "Prashant Niroula (Regulatory Architecture & Market Design Lead)",
            "sections": "Paper 1: Section 5.1–5.3 (What Disclosure Buys), Section 5.5 (When Disclosure is Worth Acquiring), Appendix C",
            "equations": "Theorem 5.1, Proposition 5.2, Proposition 5.5 (Supervisory Choice Rule), Table 5",
            "lean": "p1_thm_tagged_reset_recovery, p1_prop_tagged_instrument_regularity, p1_prop_choice_boundary",
            "context": (
                "Section 5 formally evaluates what a market supervisor buys by mandating class-level position reporting or algorithmic audit "
                "trails (such as MiFID II RTS 24 algo_id tags). Theorem 5.1 and Proposition 5.2 establish that observing class-tagged order flow "
                "completely uncouples the multi-cohort deconvolution problem: The sample complexity to identify memory rates drops from "
                "Θ(σ² (Δη)^{-(4K-2)}) down to Θ(σ² (Δη)^{-2}), while the sample complexity to identify cohort weights w_k drops to a constant O(1), "
                "entirely independent of memory spacing Δη! Proposition 5.5 models the supervisor's economic choice: balancing the fixed cost of "
                "implementing an audit trail against the catastrophic error cost of slow identification from prices alone."
            ),
            "prompt": (
                "Provide an in-depth regulatory, economic, and mathematical analysis of the value of class-tagged disclosure. Detail how class tagging "
                "uncouples the joint identification problem, derive the supervisory choice boundary in Proposition 5.5, and evaluate the policy "
                "debate surrounding mandatory algorithmic audit trails (e.g., SEC Consolidated Audit Trail, CFTC Part 17/20, MiFID II RTS 24)."
            ),
            "subquestions": [
                "Mathematically show how observing separate class order flows y_{k,t} transforms the problem from a non-linear closed-loop deconvolution into K decoupled single-cohort autoregressions.",
                "Prove why the rate-recovery error under class disclosure scales as O((Δη)^{-2}) instead of O((Δη)^{-(4K-2)}). Where does the factor (Δη)^{-(4K-4)} information gain come from?",
                "Explain why cohort weight recovery becomes O(1) under disclosure: Why does estimating the relative capital share or size of an algorithmic class not depend on how close their memory rate is to another class?",
                "Derive the supervisor's decision rule in Proposition 5.5: Under what exact parameter conditions on supervisory loss L, detection delay T, audit trail maintenance cost C_audit, and memory spacing Δη does the supervisor strictly prefer mandatory disclosure over price surveillance?",
                "Analyze the 'Disclosure Frontier' across markets: Why is mandatory disclosure most valuable in an intermediate band of memory spacings, and why does an audit trail need to cover multiple markets to amortize its fixed institutional cost?"
            ],
            "citations": "Theorem 5.1, Proposition 5.2, Proposition 5.5, Table 5 (Sample Complexity: Tagged vs. Untagged), and Lean modules p1_thm_tagged_reset_recovery and p1_prop_choice_boundary.",
            "prashant_prompt": "Evaluate this from the perspective of regulatory compliance and institutional lobbying: High-frequency trading firms routinely lobby against granular algo_id tags citing intellectual property concerns. How does the paper's proof demonstrate that aggregate class tags (without revealing proprietary code or strategy weights) deliver 99% of the supervisory value?",
            "sujan_prompt": "Analyze the signal decoupling: How does direct sensor access (class tagging) in a distributed robotic or multi-agent network eliminate the exponential estimation complexity of inferring latent agent states through output coupling alone?"
        },
        {
            "num": 8,
            "title": "Institutional Empirical Reality: Mandated Trader-Class Reporting in 20 CFTC Futures Markets",
            "lead": "Prashant Niroula (Empirical Microstructure & Futures Markets Lead)",
            "sections": "Paper 1: Section 5.4 (Mandated Disclosure: The CFTC's Reports), Section 5.6 (Empirical Evidence), Appendix E",
            "equations": "Table 7 (CFTC 8-Market Primary Test), Table 8 (12-Market Replication), Stock-Flow Bridge Remark 2.2",
            "lean": "p1_cftc_primary_bounds, stock_flow_two_root_bridge, p1_data_equivalence_multiplier",
            "context": (
                "The paper tests its core theoretical prediction—that class-tagged reports pin down persistence parameters that prices leave "
                "unrestricted—on real institutional data: the U.S. Commodity Futures Trading Commission (CFTC) Commitments of Traders (COT) reports. "
                "In an initial pre-specified test across 8 major futures markets (Bitcoin, Ether, S&P 500, 10-Yr Treasuries, Euro, Yen, Crude Oil, Natural Gas), "
                "class-tagged positions pinned down speculative persistence to intervals 9 to 71 times narrower than weekly prices allow. "
                "On 31 October 2026, the authors registered a pre-specified replication across 12 completely new CFTC markets (Gold, Silver, Copper, Corn, "
                "Soybeans, Wheat, Cattle, Coffee, Sugar, Cotton, Nasdaq-100, British Pound; SHA-256 591e71c9...); the primary hypothesis replicated "
                "in 12 out of 12 markets, with width ratios ranging from 23 to 69!"
            ),
            "prompt": (
                "Provide an exhaustive empirical and econometric analysis of the CFTC Commitments of Traders investigation. Explain the stock-flow "
                "inventory bridge connecting theoretical trader positions to weekly reported COT categories, analyze the primary hypothesis test "
                "results across all 20 markets, and evaluate the calculated 'data equivalence multiplier' (median 1,350x)."
            ),
            "subquestions": [
                "Explain the two-root stock-flow inventory bridge derived in Remark 2.2 and Supplement S6: How does the model map theoretical flow demand u_t into observed weekly position stocks S_t and net trading changes ΔS_t under contract roll conventions?",
                "Analyze Table 7 and Table 8 in detail: Contrast the 95% bootstrap confidence intervals for the fast class's persistence parameter η_fast obtained from class positions versus prices alone. Why are the price-only intervals 0.85 to 0.96 wide across all markets?",
                "Explain the concept of the 'Data Equivalence Multiplier' (Table 7): How does standard root-T shrinkage imply that matching the precision of a single weekly CFTC class report from prices alone would require a median of 1,350 times as much price data (thousands of years of data)?",
                "Why is this 1,350x calculation described as a conservative lower bound, given that the price-only intervals hit the admissible boundary [0, 1)?",
                "Evaluate the replication methodology: Why was it essential to pre-specify and hash-register the 12-market replication before opening the new data, and what does the 100% replication rate (12 of 12) prove about the robustness of the primary identification result?"
            ],
            "citations": "Table 7 (Original 8 Markets), Table 8 (Replication 12 Markets), Remark 2.2, Section 5.4, Appendix E, and Lean module stock_flow_two_root_bridge.",
            "prashant_prompt": "Examine the institutional mechanics of COT reporting: How does the CFTC classify 'Managed Money' vs. 'Producers/Merchants' in Disaggregated reports, and 'Leveraged Funds' vs. 'Asset Managers' in Financial reports? What are the regulatory strengths and limitations of these buckets?",
            "sujan_prompt": "Evaluate the bootstrap econometric methodology: How does stationary block bootstrap with Politis-White optimal block length preserve the underlying temporal dependence of the time series when constructing confidence intervals for transfer function poles?"
        },
        {
            "num": 9,
            "title": "The Anatomy of Pre-Specified Empirical Test Failures and Within-Class Sign Cancellation",
            "lead": "Prashant Niroula (Institutional Microstructure & Test Autopsies Lead)",
            "sections": "Paper 1: Section 5.5, Section 5.6, Table 9 (The Full 22-Test Scorecard), Section S8",
            "equations": "Table 9 (Scorecard of 22 Tests), Pre-specified Hypotheses H2, H3, N2, N3, Clark-West & DM Tests",
            "lean": "p1_scorecard_audit, p1_diebold_mariano_n2, p1_taker_flow_interval_n3",
            "context": (
                "A defining hallmark of scientific integrity in this paper is the complete, transparent reporting of all pre-specified empirical tests, "
                "including all failures. Table 9 presents the comprehensive scorecard of all 22 pre-specified tests: 11 passed or held, 10 failed, "
                "and 1 secondary prediction was not supported. "
                "Critical failures include: (1) Trend-following (H2) failed on equities (S&P 500, Nasdaq-100); (2) Position persistence could not "
                "be separated into a distinct faster learning root (H3 failed in 6 of 8 markets); (3) Weekly flows did not pin down persistence (3 of 8); "
                "(4) Binance 5-minute price changes failed to forecast class positions out-of-sample (N2: 1 of 30); and (5) Aggregate taker flow "
                "failed to pin down the combined response Ψ (N3: 5 of 30)."
            ),
            "prompt": (
                "Conduct a rigorous, doctoral-level post-mortem autopsy of the 10 failed pre-specified tests. Explain the economic, institutional, "
                "and econometric reasons why each test failed, and prove why these failures provide the definitive institutional proof of "
                "'within-class sign cancellation'—demonstrating why coarse public buckets are insufficient and granular algorithmic audit trails are required."
            ),
            "subquestions": [
                "Analyze the failure of Hypothesis H2 (Trend-Following) in equities: Why does Managed Money trend-follow in commodities and currencies (buying after price rises), but trend-rebel / sell after price rises in the S&P 500 and Nasdaq-100?",
                "Autopsy the failure of Hypothesis H3 (Learning Memory Separation): Why did positions fail to exhibit a second, faster root corresponding to learning memory? What does this tell us about the confounding between algorithmic learning memory and physical position turnover?",
                "Explain the institutional phenomenon of 'Within-Class Sign Cancellation': In the CFTC 'Leveraged Funds' category, how do trend-following quantitative momentum funds (CTAs) trade against cash-futures basis arbitrageurs and relative-value desks within the exact same reporting category?",
                "Mathematically explain how aggregating two opposing strategies y_t = y_{CTA,t} + y_{basis,t} leads to cancellation in price impact and flow persistence, obscuring both signals in coarse aggregate data.",
                "Autopsy the October 2026 Binance USD-M perpetual tests (N2 and N3): Why did 5-minute price changes fail to forecast the top-trader position ratio out-of-sample (Diebold-Mariano p < 0.05 in only 1 of 30 markets)? Why did aggregate taker flow fail to pin down the combined one-hour response Ψ?",
                "How do these 10 test failures directly strengthen the paper's policy conclusion: That macroprudential supervision cannot rely on coarse reporting buckets and requires unique, granular algorithmic identifiers (MiFID II RTS 24 algo_id)?"
            ],
            "citations": "Table 9 (Complete 22-Test Scorecard), Section 5.5, Section 5.6, Table S7, Table S8, and Lean modules p1_scorecard_audit and p1_diebold_mariano_n2.",
            "prashant_prompt": "Evaluate the research integrity ethics: In finance literature, authors frequently bury or retroactively adjust failed tests to claim 100% success. Why is reporting the exact 11/10 pass/fail scorecard vital for credibility with Econometrica / Journal of Finance referees?",
            "sujan_prompt": "Examine the dynamic cancellation in transfer functions: If two parallel subsystems have opposite signs in their numerator gains (w_1 > 0, w_2 < 0), how does pole-zero cancellation or near-cancellation degrade the observability rank of the Hankel matrix?"
        },
        {
            "num": 10,
            "title": "The Spectral Blind Spot, Pseudospectra, and Catastrophic Transient Amplification",
            "lead": "Sujan Khatiwada (Non-Normal Control & Pseudospectra Lead)",
            "sections": "Paper 1: Section 6 (A Spectral Blind Spot), Appendix B; Paper 2: Section 1 & Section 2",
            "equations": "Theorem 6.1 (Theorem S19), Kreiss Matrix Theorem, Pseudospectrum σ_ε(A), Resolvent Norm ||(zI - A)^{-1}||",
            "lean": "p1_thm_blind_spectral, p1_kreiss_transient_bound, p1_pseudo_resolvent",
            "context": (
                "Section 6 reveals a profound 'spectral blind spot' that undermines conventional risk management and macroprudential regulation. "
                "Theorem 6.1 proves that for any prescribed closed-loop eigenvalues 0 < λ_2 < λ_1 < 1, any one-step return variance, and any "
                "sufficiently large stationary price variance, there exists a family of two-state economies sharing all three quantities whose "
                "worst-case transient amplification ||G^t||_2 grows without bound! "
                "This occurs because the state transition matrix A is highly non-normal (A A^T ≠ A^T A). While classical asymptotic stability "
                "relies on spectral radius ρ(A) < 1, non-normal dynamical systems can produce massive, catastrophic excursions before decaying."
            ),
            "prompt": (
                "Provide an advanced mathematical and control-theoretic analysis of the spectral blind spot and transient non-normal amplification. "
                "Reconstruct the proof of Theorem 6.1, apply the Kreiss Matrix Theorem and pseudospectral theory to order book dynamics, and explain "
                "why regulatory frameworks relying solely on eigenvalues, VaR, or volatility are fundamentally blind to transient systemic risk."
            ),
            "subquestions": [
                "Reconstruct the parametric construction of the family of two-state economies in Theorem 6.1: How are the internal couplings arranged to keep closed-loop eigenvalues (λ_1, λ_2) and stationary variance constant while driving the non-orthogonality of eigenvectors to infinity?",
                "State and apply the Kreiss Matrix Theorem: Define the Kreiss constant K(A) = sup_{|z|>1} (|z| - 1) ||(zI - A)^{-1}||. Show how K(A) provides a lower bound on the maximum transient excursion: sup_{t ≥ 0} ||A^t||_2 ≥ K(A).",
                "Explain the concept of ε-pseudospectra σ_ε(A) = { z ∈ C : ||(zI - A)^{-1}|| ≥ 1/ε }: How can the pseudospectrum protrude far outside the unit disk even when all eigenvalues lie strictly inside the unit circle (|λ_i| < 1)?",
                "Explain Figure 7 in Paper 1: How do two markets with identical asymptotic half-lives (e.g., 5 periods) and identical stationary volatility produce peak cumulative losses that differ by factors of 10x or 100x?",
                "Why does this theorem establish that observing volatility and eigenvalues provides a dangerous false sense of market safety prior to liquidity flash crashes?"
            ],
            "citations": "Theorem 6.1, Figure 7 (Transient Excursions for Matched Eigenvalues), Kreiss (1962), Trefethen and Embree (2005), and Lean module p1_thm_blind_spectral.",
            "sujan_prompt": "Bridge this to non-normal fluid mechanics and control engineering: How does transient amplification in this order book model parallel the subcritical transition to turbulence in Poiseuille/Couette fluid flows or transient overshoot in robotic actuators?",
            "prashant_prompt": "Evaluate the Basel III / Dodd-Frank regulatory failure: Why did standard risk models fail to foresee the 2010 Flash Crash, the 2014 Treasury flash rally, or the 2020/2021 crypto liquidation cascades, and how does the Kreiss bound explain these events?"
        },
        {
            "num": 11,
            "title": "The Pre-Trade Guard, Cumulative Risk S, and the Operational Bridge to Paper 2",
            "lead": "Joint Lead: Sujan Khatiwada & Prashant Niroula",
            "sections": "Paper 1: Section 7 (Policy Implications); Paper 2: Theorem 1, Theorem 2, Theorem 3, Section 4",
            "equations": "Cumulative Transient Risk S = κ~ / (m - q κ~), Overshoot Condition φε > (1-a)κ, Pre-Trade Guard C_3",
            "lean": "p1_bridge_cumulative_risk, p2_thm_overshoot_exact, p2_thm_guard_maximal",
            "context": (
                "Section 7 of Paper 1 and the companion manuscript (Paper 2) deliver the operational solution to the identification boundary: "
                "Because a market supervisor can never identify the internal cohort structure {w_k, η_k} in time to prevent a crash, "
                "regulatory safety controls must be identification-free! "
                "Paper 2 proves that cumulative transient risk is governed by the scalar invariant S = κ~ / (m - q κ~), and a book overshoots "
                "if and only if φε > (1 - a)κ. A pre-trade guard on the summed impulse response is the maximal safe control rule: "
                "it prevents transient overshoots regardless of how traders split into unknown cohorts, requires only Θ(σ² ε^{-2} log(1/ε)) "
                "experiments to certify, and is minimax optimal in lost trading capacity up to a logarithmic factor."
            ),
            "prompt": (
                "Provide a comprehensive synthesis bridging Paper 1's identification limits to Paper 2's pre-trade guard. Explain why identification-free "
                "control is the necessary economic paradigm for machine markets, derive the cumulative risk statistic S and the exact overshoot "
                "condition, and prove the maximality and minimax optimality of the certified pre-trade guard."
            ),
            "subquestions": [
                "Explain the fundamental paradigm shift: Why does Paper 1's lower bound Ω((Δη)^{-(4K-2)}) prove that 'identify-then-control' is impossible in real-time, necessitating an identification-free control architecture?",
                "Derive the exact one-period overshoot condition φε > (1 - a)κ from Paper 2: Define each parameter (momentum feedback φ, depth replenishment rate ε, price impact persistence a, Kyle's lambda κ) and explain the mechanical tug-of-war between liquidity replenishment and trend feedback.",
                "Define the cumulative transient risk statistic S = κ~ / (m - q κ~): Prove why S is an invariant that depends only on aggregate market primitives and does not require knowing the number of cohorts K or their individual memory rates η_k.",
                "Explain the certified pre-trade throttle: How does scaling an order size or position limit by 1 / S (or admitting flow only when C_3 < 0) guarantee balance-sheet solvency and bound transient excursions across all bounded shock paths?",
                "Prove the maximality of the guard: Why is any control rule that admits more volume than the certified guard strictly unsafe for at least one admissible economy within the uncertainty set?",
                "Analyze the pre-registered empirical backtests in Paper 2 (Part 13 & Part 15): How did the certified guard lower tail losses by 13% on untouched days, and why did limits based on volatility alone fail to prevent liquidation spikes?"
            ],
            "citations": "Paper 1 Section 7, Paper 2 Theorems 1–3, Proposition 7.1, Table 1 (Paper 2), Figure 1 (Paper 2), and Lean modules p2_thm_overshoot_exact and p2_thm_guard_maximal.",
            "prashant_prompt": "Evaluate this from an exchange architecture perspective: How can CME, Binance, or Nasdaq implement the pre-trade guard directly inside their matching engines without adding latency to non-amplifying orders?",
            "sujan_prompt": "Connect this to robust control theory: How does this identification-free guard relate to H_infinity control, small-gain theorems, and Kharitonov's theorem for interval plants?"
        },
        {
            "num": 12,
            "title": "Interactive Theorem Proving in Financial Economics: The Lean 4 Machine Verification",
            "lead": "Sujan Khatiwada (Formal Verification Lead) & Pratik Niroula",
            "sections": "Paper 1: Section 1.3, Section 8, Appendix D; Paper1FullFrontiers.lean",
            "equations": "Paper1FullFrontiers.lean (787 Named Declarations, 81 Modules, 0 sorry, Mathlib 4.34.1)",
            "lean": "Paper1FullFrontiers.lean, CeilingSuitePaper1.lean, tests/test_lean_formalization.py",
            "context": (
                "A breakthrough achievement of this project is the 100% formal verification of Paper 1's mathematical foundations in Lean 4 "
                "with Mathlib. The formalization spans 787 named declarations across 81 modules with exactly zero sorry placeholders and zero "
                "custom axioms, relying strictly on Lean's core logic (propext, Classical.choice, Quot.sound). "
                "This formalization covers the closed-loop identification boundary, moment-matched lower bounds for all K, Prony's matching "
                "upper bound under sub-Gaussian noise, active probing Toeplitz forms, margin solvency capital bounds, real Bitcoin noise resampling "
                "invariance, general completely monotone memory rates, and the 10 frontier environments."
            ),
            "prompt": (
                "Provide an advanced analysis of the role of interactive theorem proving and formal verification in financial economics and market design. "
                "Examine how machine-checking proofs in Lean 4 eliminates hidden mathematical errors, detail the architecture of Paper1FullFrontiers.lean, "
                "and explain how our team will present this verification to establish an unprecedented standard of mathematical rigor for journal review."
            ),
            "subquestions": [
                "Explain the foundational difference between paper-and-pencil mathematical proofs (which frequently contain hidden assumptions, sign slips, or boundary errors) and interactive theorem proving in Lean 4 checked by a small, trusted logical kernel.",
                "Detail the architecture of Paper1FullFrontiers.lean: How does it formalize the 10 frontier environments that previously relied on upstream Mathlib components (ergodic CLTs, general Pinsker inequalities, Whittle divergence, operator Hölder spaces)?",
                "Explain how Lean 4 formalized the general-alpha moment testing bound (Theorems 3.1, 4.1, 4.3) using algebraic quadratics and Cauchy-Schwarz bounds without requiring external measure-theoretic convergence lemmas.",
                "Review the formal verification receipt and automated regression test (tests/test_lean_formalization.py): How does the verification script confirm 787/787 theorems with zero unproven sorries?",
                "Formulate our strategy for journal referees: How does having a 100% kernel-verified Lean 4 codebase preemptively crush technical objections from mathematical reviewers at Econometrica or Quantitative Economics?",
                "Identify what role Sujan Khatiwada and Prashant Niroula will take in maintaining, extending, and co-authoring the Lean 4 formal artifacts as we move through journal revisions."
            ],
            "citations": "Section 1.3, Section 8, Appendix D, formal_verification_receipt.json, Paper1FullFrontiers.lean, and tests/test_lean_formalization.py.",
            "sujan_prompt": "Evaluate the intersection of formal methods and autonomous systems: In mission-critical aerospace robotics, formal verification is required to guarantee stability. Why should high-frequency algorithmic financial systems be held to the exact same formal standard?",
            "prashant_prompt": "Evaluate the auditability standard for regulatory agencies: How could central banks, the SEC, or the CFTC use machine-checked theorem provers to verify whether proposed market design rules (e.g., tick size changes, circuit breakers) possess formal mathematical guarantees before deployment?"
        }
    ]

    for q in QUESTIONS:
        # Module Title
        p_q = doc.add_paragraph()
        style_heading_1(p_q)
        p_q.add_run(f"Question {q['num']}: {q['title']}")
        
        # Metadata Table
        meta_dict = {
            "Assigned Lead Reviewer": q["lead"],
            "Primary Manuscript Sections": q["sections"],
            "Key Mathematical Objects": q["equations"],
            "Formal Verification Module": q["lean"]
        }
        add_metadata_table(doc, meta_dict)
        
        # Theoretical Context
        p_ctx_hdr = doc.add_paragraph()
        style_heading_3(p_ctx_hdr)
        p_ctx_hdr.add_run("Theoretical Context & Manuscript Foundations")
        
        p_ctx = doc.add_paragraph()
        style_body(p_ctx, "", q["context"])
        
        # The Master Prompt
        p_m_hdr = doc.add_paragraph()
        style_heading_3(p_m_hdr)
        p_m_hdr.add_run("The Master PhD Research Challenge")
        
        add_callout(
            doc,
            [q["prompt"]],
            title="CORE ANALYTICAL INQUIRY",
            alert_type="info"
        )
        
        # Detailed Sub-Questions
        p_sq_hdr = doc.add_paragraph()
        style_heading_3(p_sq_hdr)
        p_sq_hdr.add_run("Mandatory Technical Sub-Components to Address in Writing")
        
        for sq in q["subquestions"]:
            p_sq = doc.add_paragraph(style='List Bullet')
            p_sq.paragraph_format.space_before = Pt(2)
            p_sq.paragraph_format.space_after = Pt(3)
            style_body(p_sq, "", sq)
            
        # Required Citations
        p_cite = doc.add_paragraph()
        p_cite.paragraph_format.space_before = Pt(4)
        p_cite.paragraph_format.space_after = Pt(4)
        style_body(p_cite, "Mandatory Proof Artifacts & Citations to Reference: ", q["citations"])
        
        # Co-Author Prompts
        p_co_hdr = doc.add_paragraph()
        style_heading_3(p_co_hdr)
        p_co_hdr.add_run("Targeted Domain Specialization Inquiries")
        
        p_sujan = doc.add_paragraph()
        style_body(p_sujan, "For Sujan Khatiwada (Control & Robotics Focus): ", q["sujan_prompt"])
        
        p_prashant = doc.add_paragraph()
        style_body(p_prashant, "For Prashant Niroula (Microstructure & Policy Focus): ", q["prashant_prompt"])
        
        # Dedicated 1-Page Response Box
        add_response_box(doc, q["num"], q["title"], q["lead"])

    # ==========================================
    # FINAL SECTION: CO-AUTHOR SIGN-OFF & COMMITMENT
    # ==========================================
    p_end = doc.add_paragraph()
    style_heading_1(p_end)
    p_end.add_run("Co-Author Final Contribution Synthesis & Review Sign-Off")
    
    p_end_text = doc.add_paragraph()
    style_body(
        p_end_text,
        "Formal Declaration of Co-Authorship Contribution: ",
        "By completing this workbook and submitting the written analyses for all 12 modules, Sujan Khatiwada and Prashant Niroula "
        "formally demonstrate complete mastery, rigorous peer verification, and full intellectual ownership of the Machine Markets research program. "
        "In accordance with CRediT (Contributor Roles Taxonomy) standards for scientific publication, their contributions encompass: "
        "Conceptualization, Formal Analysis, Methodology, Investigation, Validation, and Writing – Review & Editing. "
        "The completed workbook will be archived in the project repository as an immutable record of co-author review and journal defense readiness."
    )
    
    # Sign-off Table
    sign_table = doc.add_table(rows=4, cols=4)
    sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sign_table.autofit = False
    
    shd_headers = ["Co-Author Name", "Institutional Affiliation", "Date Completed", "Signature / Verification"]
    for j, h in enumerate(shd_headers):
        cell = sign_table.cell(0, j)
        set_cell_background(cell, NAVY_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]; r = p.add_run(h); r.font.name = "Calibri"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    signers = [
        ("Pratik Niroula\n(Lead Author & PI)", "Minnesota State University, Mankato\nDept. of Computer Information Science"),
        ("Sujan Khatiwada\n(Co-Author)", "Minnesota State University, Mankato\nDept. of Electrical, Computer & Robotics Engineering"),
        ("Prashant Niroula\n(Co-Author)", "Tribhuvan University, Nepal\nFaculty of Management")
    ]
    
    for i, (name, affil) in enumerate(signers):
        row = i + 1
        c0 = sign_table.cell(row, 0)
        c1 = sign_table.cell(row, 1)
        c2 = sign_table.cell(row, 2)
        c3 = sign_table.cell(row, 3)
        
        c0.width = Inches(1.8)
        c1.width = Inches(2.2)
        c2.width = Inches(1.2)
        c3.width = Inches(1.3)
        
        for c in (c0, c1, c2, c3):
            set_cell_background(c, "FFFFFF" if row % 2 == 1 else "F8FAFC")
            set_cell_borders(c, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                                 left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
            set_cell_margins(c, top=120, bottom=120, left=100, right=100)
            
        p0 = c0.paragraphs[0]; r0 = p0.add_run(name); r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(affil); r1.font.name = "Calibri"; r1.font.size = Pt(8.5); r1.font.color.rgb = RGB_CHARCOAL
        p2 = c2.paragraphs[0]; r2 = p2.add_run("___ / ___ / 2026"); r2.font.name = "Calibri"; r2.font.size = Pt(9); r2.font.color.rgb = RGB_MUTED
        p3 = c3.paragraphs[0]; r3 = p3.add_run("________________"); r3.font.name = "Calibri"; r3.font.size = Pt(9); r3.font.color.rgb = RGB_MUTED

    # Output paths
    out1 = Path("CoAuthor_Mastery_Workbook_Paper1.docx")
    out2 = Path("ceiling_suite/papers/paper1/CoAuthor_Mastery_Workbook_Paper1.docx")
    
    doc.save(str(out1))
    out2.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out2))
    print(f"Successfully generated workbook at:\n  - {out1.resolve()}\n  - {out2.resolve()}")

if __name__ == "__main__":
    build_workbook()
