"""
Script to generate TWO distinct, beautifully formatted Word files:
1. Paper1_Questions_Workbook.docx (Questions & Blank Workspaces Only)
2. Paper1_Answers_Solution_Manual.docx (Full Model Answers & Solution Key Only)
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

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from workbook_questions import QUESTIONS
from workbook_answers import ANSWERS as answers

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
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor — Confidential Doctoral Research Document")
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
        
        set_cell_margins(c0, top=70, bottom=70, left=120, right=120)
        set_cell_margins(c1, top=70, bottom=70, left=120, right=120)
        
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9); r1.font.color.rgb = RGB_CHARCOAL
        row_idx += 1
        
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

# ==============================================================================
# BUILDER 1: QUESTIONS ONLY WORKBOOK (Blank Workspaces for Sujan & Prashant)
# ==============================================================================
def build_questions_only_file():
    doc = Document()
    add_header_footer(doc, "Co-Author Examination & Contribution Workbook")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("DOCTORAL RESEARCH EXAMINATION & CONTRIBUTION WORKBOOK")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Machine Markets Research Program:\nCo-Author Mastery & Contribution Assignment")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(24); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "A 12-Module Rigorous Chapter-by-Chapter Inquiry on Dynamic Proofs, Microstructure Econometrics, "
        "Institutional Data, and Lean 4 Formalization for Co-Authors Sujan Khatiwada and Prashant Niroula"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(13); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=6, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Primary Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Document Edition", "Questions & Written Workspace Edition (Blank Workspaces for Co-Author Completion)"),
        ("Lead Author & PI", "Pratik Niroula (Department of Computer Information Science, Minnesota State University, Mankato)"),
        ("Contributing Co-Authors", "Sujan Khatiwada (Dept. of Electrical, Computer & Robotics Engineering, MNSU Mankato)\nPrashant Niroula (Faculty of Management, Tribhuvan University, Kirtipur, Nepal)"),
        ("Submission Standard", "Minimum 1 full page (400–600+ words) per question module. Hand in completed document for co-author review."),
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
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9.5); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9.5); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(12); sp.paragraph_format.space_after = Pt(4)
    add_callout(
        doc,
        [
            "\"This workbook is the official co-author examination assignment. Each co-author is required to study the paper thoroughly "
            "and write out an exhaustive, one-page doctoral-level answer (400–600+ words) inside each designated response box. "
            "Answers must include formal derivations, institutional table references, and referee defense strategies.\"",
            "— Research Integrity Standard (November 2026)"
        ],
        title="CO-AUTHOR COMPLETION DIRECTIVE",
        alert_type="alert"
    )
    doc.add_page_break()

    # Section 1: Instructions & Responsibility Matrix
    p_s1 = doc.add_paragraph(); style_heading_1(p_s1); p_s1.add_run("1. Instructions & Domain Specialization Matrix")
    p_b1 = doc.add_paragraph()
    style_body(
        p_b1,
        "Doctoral Submission Standard: ",
        "Every question module in this workbook addresses an essential pillar of Paper 1 and its operational companion (Paper 2). "
        "Sujan Khatiwada is designated lead on dynamical systems, transfer functions, Hankel matrix conditioning, spectral limits, and Lean 4 formalization. "
        "Prashant Niroula is designated lead on market microstructure, capital bounds, CFTC/Binance empirical testing, and supervisory policy. "
        "Both co-authors must write full 1-page responses to all 12 questions to achieve full intellectual ownership and publication equity."
    )
    
    # 12 Questions with Blank Workspaces
    for q in QUESTIONS:
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Question {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Assigned Lead Reviewer": q["lead"],
            "Primary Manuscript Sections": q["sections"],
            "Key Mathematical Objects": q["equations"],
            "Formal Verification Module": q["lean"]
        })
        
        p_c_hdr = doc.add_paragraph(); style_heading_3(p_c_hdr); p_c_hdr.add_run("Theoretical Context & Manuscript Foundations")
        p_ctx = doc.add_paragraph(); style_body(p_ctx, "", q["context"])
        
        p_m_hdr = doc.add_paragraph(); style_heading_3(p_m_hdr); p_m_hdr.add_run("The Master PhD Research Challenge")
        add_callout(doc, [q["prompt"]], title="CORE ANALYTICAL INQUIRY", alert_type="info")
        
        p_sq_hdr = doc.add_paragraph(); style_heading_3(p_sq_hdr); p_sq_hdr.add_run("Mandatory Technical Sub-Components to Address in Writing")
        for sq in q["subquestions"]:
            p_sq = doc.add_paragraph(style='List Bullet')
            p_sq.paragraph_format.space_before = Pt(2); p_sq.paragraph_format.space_after = Pt(3)
            style_body(p_sq, "", sq)
            
        p_cite = doc.add_paragraph(); p_cite.paragraph_format.space_before = Pt(4); p_cite.paragraph_format.space_after = Pt(4)
        style_body(p_cite, "Mandatory Proof Artifacts & Citations to Reference: ", q["citations"])
        
        p_co_hdr = doc.add_paragraph(); style_heading_3(p_co_hdr); p_co_hdr.add_run("Targeted Domain Specialization Inquiries")
        p_sujan = doc.add_paragraph(); style_body(p_sujan, "For Sujan Khatiwada (Control & Robotics Focus): ", q["sujan_prompt"])
        p_prashant = doc.add_paragraph(); style_body(p_prashant, "For Prashant Niroula (Microstructure & Policy Focus): ", q["prashant_prompt"])
        
        # Dedicated Blank Response Box
        p_box_title = doc.add_paragraph()
        p_box_title.paragraph_format.space_before = Pt(10); p_box_title.paragraph_format.space_after = Pt(3)
        p_box_title.paragraph_format.keep_with_next = True
        r_bt = p_box_title.add_run(f"Co-Author Written Response Workspace — Question {q['num']}")
        r_bt.font.name = "Calibri"; r_bt.font.size = Pt(11.5); r_bt.font.bold = True; r_bt.font.color.rgb = RGB_NAVY
        
        desc = doc.add_paragraph(); desc.paragraph_format.space_before = Pt(0); desc.paragraph_format.space_after = Pt(4)
        r_desc = desc.add_run(
            f"MANDATORY REQUIREMENT: Provide a comprehensive, doctoral-level written response (minimum 1 full page, "
            f"400–600+ words). Address all parts of the master prompt and sub-questions above. Include formal mathematical "
            f"expressions, citations to equations/tables in the paper, and explicit recommendations for journal referee defense. "
            f"Lead Reviewer: {q['lead']}."
        )
        r_desc.font.name = "Calibri"; r_desc.font.size = Pt(9.5); r_desc.font.italic = True; r_desc.font.color.rgb = RGB_MUTED

        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, "FAFAFA")
        set_cell_borders(cell, top=("single", "12", "0", SLATE_SECONDARY), bottom=("single", "12", "0", SLATE_SECONDARY),
                               left=("single", "12", "0", SLATE_SECONDARY), right=("single", "12", "0", SLATE_SECONDARY))
        set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
        
        cp = cell.paragraphs[0]; cp.paragraph_format.space_before = Pt(0); cp.paragraph_format.space_after = Pt(4)
        r_hdr = cp.add_run(f"WRITTEN SUBMISSION FOR QUESTION {q['num']}: {q['title'].upper()}\n")
        r_hdr.font.name = "Calibri"; r_hdr.font.size = Pt(10); r_hdr.font.bold = True; r_hdr.font.color.rgb = RGB_SLATE
        
        sections = [
            ("Part A: Formal Mathematical Derivation & Proof Reconstruction",
             "[Type detailed mathematical derivations, transfer function manipulations, Taylor expansions, or moment-matching steps here... (approx. 150-200 words)]"),
            ("Part B: Economic Mechanism, Institutional Interpretation & Empirical Analysis",
             "[Type detailed analysis of microstructure incentives, market impact, CFTC/Binance data findings, and test scorecard results here... (approx. 150-200 words)]"),
            ("Part C: Critical Review, Boundary Conditions & Journal Defense Strategy",
             "[Type evaluation of assumptions, unformalized frontiers, potential referee objections, and suggested manuscript enhancements here... (approx. 150-200 words)]")
        ]
        for sec_title, placeholder in sections:
            sp_title = cell.add_paragraph(); sp_title.paragraph_format.space_before = Pt(6); sp_title.paragraph_format.space_after = Pt(2)
            r_st = sp_title.add_run(sec_title); r_st.font.name = "Calibri"; r_st.font.size = Pt(9.5); r_st.font.bold = True; r_st.font.color.rgb = RGB_STEEL
            
            sp_body = cell.add_paragraph(); sp_body.paragraph_format.space_before = Pt(0); sp_body.paragraph_format.space_after = Pt(6)
            r_sb = sp_body.add_run(placeholder + "\n\n\n\n\n\n")
            r_sb.font.name = "Calibri"; r_sb.font.size = Pt(9.5); r_sb.font.italic = True; r_sb.font.color.rgb = RGBColor(160, 160, 160)

        doc.add_page_break()

    # Sign-Off Page
    p_end = doc.add_paragraph(); style_heading_1(p_end); p_end.add_run("Co-Author Final Contribution Synthesis & Review Sign-Off")
    p_et = doc.add_paragraph()
    style_body(
        p_et,
        "Formal Declaration of Co-Authorship Contribution: ",
        "By completing this workbook and submitting the written analyses for all 12 modules, Sujan Khatiwada and Prashant Niroula "
        "formally demonstrate complete mastery, rigorous peer verification, and full intellectual ownership of the Machine Markets research program. "
        "In accordance with CRediT standards, their contributions encompass Conceptualization, Formal Analysis, Methodology, Investigation, "
        "Validation, and Writing – Review & Editing."
    )
    
    sign_table = doc.add_table(rows=4, cols=4); sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER; sign_table.autofit = False
    shd_headers = ["Co-Author Name", "Institutional Affiliation", "Date Completed", "Signature / Verification"]
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
# BUILDER 2: ANSWERS ONLY SOLUTION MANUAL (Pure Comprehensive Answer Key)
# ==============================================================================
def build_answers_only_file():
    doc = Document()
    add_header_footer(doc, "Master Solution Manual & Authoritative Answer Key")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("DOCTORAL SOLUTION MANUAL & AUTHORITATIVE ANSWER KEY")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Machine Markets Research Program:\nComprehensive Doctoral Solution Manual")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(24); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "Exhaustive 12-Module Doctoral Answer Key (500–700 Words Per Module) Providing Rigorous Mathematical Derivations, "
        "Empirical Market Evidence, and Top-Tier Journal Defense Strategies"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(13); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=6, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Primary Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Document Edition", "Authoritative Answer Key & Solution Manual (Contains Pure Detailed Model Answers)"),
        ("Lead Author & PI", "Pratik Niroula (Department of Computer Information Science, Minnesota State University, Mankato)"),
        ("Contributing Co-Authors", "Sujan Khatiwada (Dept. of Electrical, Computer & Robotics Engineering, MNSU Mankato)\nPrashant Niroula (Faculty of Management, Tribhuvan University, Kirtipur, Nepal)"),
        ("Standard of Rigor", "Publication-grade doctoral solutions meeting the standards of Econometrica and the Journal of Finance."),
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
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9.5); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9.5); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(12); sp.paragraph_format.space_after = Pt(4)
    add_callout(
        doc,
        [
            "\"This Solution Manual contains the official, peer-reviewed model answers for all 12 modules of the Machine Markets "
            "research curriculum. Sujan Khatiwada and Prashant Niroula should use this volume as an authoritative reference guide "
            "to study the exact mathematical manipulations, econometric test interpretations, and referee defense arguments "
            "required for top-journal presentations and formal publication reviews.\"",
            "— Research Leadership Directive (November 2026)"
        ],
        title="EXECUTIVE REFERENCE GUIDE DIRECTIVE",
        alert_type="info"
    )
    doc.add_page_break()

    # Section 1: Executive Study Architecture
    p_s1 = doc.add_paragraph(); style_heading_1(p_s1); p_s1.add_run("1. Executive Guide to the Model Solutions")
    p_b1 = doc.add_paragraph()
    style_body(
        p_b1,
        "How to Use this Solution Manual: ",
        "Each module in this volume contains a complete, 500-to-700-word doctoral-level answer structured into three distinct sections: "
        "(1) Part A: Formal Mathematical Derivation & Proof Reconstruction; (2) Part B: Economic Mechanism, Institutional Interpretation & Empirical Analysis; "
        "and (3) Part C: Critical Review, Boundary Conditions & Journal Defense Strategy. Every equation, theorem, empirical scorecard table, "
        "and Lean 4 machine-checked module is fully articulated to provide an unassailable standard of research mastery."
    )
    
    # 12 Questions with Full Model Answers
    for q in QUESTIONS:
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Module {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Domain Lead": q["lead"],
            "Manuscript Sections": q["sections"],
            "Key Mathematical Objects": q["equations"],
            "Lean 4 Module": q["lean"]
        })
        
        # Summary of the prompt being answered
        p_pr_hdr = doc.add_paragraph(); style_heading_3(p_pr_hdr); p_pr_hdr.add_run("Research Challenge Answered in this Module")
        p_pr = doc.add_paragraph(); style_body(p_pr, "Master Research Prompt: ", q["prompt"], italic=True)
        
        # Full Comprehensive Model Answer
        q_ans = answers.get(q["num"], {})
        
        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, ANSWER_BG)
        set_cell_borders(cell, top=("single", "16", "0", NAVY_PRIMARY), bottom=("single", "16", "0", NAVY_PRIMARY),
                               left=("single", "16", "0", NAVY_PRIMARY), right=("single", "16", "0", NAVY_PRIMARY))
        set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
        
        cp = cell.paragraphs[0]; cp.paragraph_format.space_before = Pt(0); cp.paragraph_format.space_after = Pt(4)
        r_hdr = cp.add_run(f"AUTHORITATIVE MODEL ANSWER: QUESTION {q['num']}\n")
        r_hdr.font.name = "Calibri"; r_hdr.font.size = Pt(11); r_hdr.font.bold = True; r_hdr.font.color.rgb = RGB_NAVY
        
        for sec_key, sec_text in q_ans.items():
            sp_title = cell.add_paragraph(); sp_title.paragraph_format.space_before = Pt(8); sp_title.paragraph_format.space_after = Pt(2)
            r_st = sp_title.add_run(sec_key); r_st.font.name = "Calibri"; r_st.font.size = Pt(10); r_st.font.bold = True; r_st.font.color.rgb = RGB_SLATE
            
            sp_body = cell.add_paragraph(); sp_body.paragraph_format.space_before = Pt(0); sp_body.paragraph_format.space_after = Pt(4)
            sp_body.paragraph_format.line_spacing = 1.15
            r_sb = sp_body.add_run(sec_text)
            r_sb.font.name = "Calibri"; r_sb.font.size = Pt(9.5); r_sb.font.color.rgb = RGB_CHARCOAL

        doc.add_page_break()

    # Final Attribution and Research Ethics Declaration
    p_end = doc.add_paragraph(); style_heading_1(p_end); p_end.add_run("Research Integrity & Peer Defense Readiness Declaration")
    p_et = doc.add_paragraph()
    style_body(
        p_et,
        "Authoritative Scientific Record: ",
        "This Solution Manual constitutes the authoritative reference foundation of the Machine Markets research program. "
        "By mastering these model solutions, all co-authors (Pratik Niroula, Sujan Khatiwada, and Prashant Niroula) stand fully prepared "
        "to deliver unified, mathematically sound, and empirically verified defenses before referees, editors, and conference audiences worldwide."
    )
    
    out_path = Path("Paper1_Answers_Solution_Manual.docx")
    doc.save(str(out_path))
    doc.save(str(ROOT / "ceiling_suite/papers/paper1/Paper1_Answers_Solution_Manual.docx"))
    doc.save(str(ROOT / "ceiling_suite/paper1/Paper1_Answers_Solution_Manual.docx"))
    print(f"Built Answers Only Solution Manual: {out_path.resolve()}")

if __name__ == "__main__":
    build_questions_only_file()
    build_answers_only_file()
