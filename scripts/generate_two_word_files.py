"""
Script to generate TWO clean, collaborative, reading-focused Word files:
1. Paper1_Questions_Workbook.docx (Raw Questions, Required Answer Points & Workspaces Only)
2. Paper1_Answers_Solution_Manual.docx (Complete Section Walkthrough & Full Model Answers Only)

Framed naturally as a Co-Author Reading Guide & Contribution Workbook for Sujan Khatiwada and Prashant Niroula.
Strictly Paper 1 ONLY. No Paper 2 references. No exam/doctoral posturing.
"""

import os
import sys
import shutil
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

from workbook_questions import QUESTIONS
from workbook_answers import ANSWERS

# --- Color Palette Constants ---
NAVY_PRIMARY = "0B2545"      # Deep Executive Navy
SLATE_SECONDARY = "134074"   # Secondary Slate Blue
STEEL_BLUE = "0077B6"        # Vibrant Steel Blue
CHARCOAL_TEXT = "1D2D44"     # Dark Neutral Body Text
LIGHT_BG = "EEF4F8"          # Ice Gray Callout Background
LIGHT_BORDER = "CFDBD5"      # Light Border Gray
ALERT_CRIMSON = "8D0801"     # Warning Accent
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
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGB_NAVY

def style_heading_2(p):
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGB_SLATE

def style_heading_3(p):
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
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
        frun = fp.add_run("Paper 1: What Prices Cannot Tell a Market Supervisor — Reading Guide")
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
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(3)
    if title:
        rt = cp.add_run(title + "\n")
        rt.font.name = "Calibri"
        rt.font.size = Pt(10)
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
    sp.paragraph_format.space_after = Pt(3)

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
        
        set_cell_margins(c0, top=50, bottom=50, left=90, right=90)
        set_cell_margins(c1, top=50, bottom=50, left=90, right=90)
        
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9); r1.font.color.rgb = RGB_CHARCOAL
        row_idx += 1
        
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3)

# ==============================================================================
# BUILDER 1: RAW QUESTIONS ONLY WORKBOOK
# ==============================================================================
def build_questions_only_file():
    doc = Document()
    add_header_footer(doc, "Paper 1 Questions Workbook")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36); p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("PAPER 1: READING & DISCUSSION QUESTIONS")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("What Prices Cannot Tell a Market Supervisor:\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(20); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "Section-by-Section Raw Questions & Required Analysis for Co-Authors (Sujan Khatiwada and Prashant Niroula)\n"
        "Development Revision: 2 November 2026 (Strictly Paper 1 Only)"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(11.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=4, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Lead Author & PI", "Pratik Niroula (Minnesota State University, Mankato)"),
        ("Co-Authors", "Sujan Khatiwada (Minnesota State University, Mankato) & Prashant Niroula (Tribhuvan University)"),
        ("Target Revision", "Latest November 2026 Draft (Registered 12-Market Replication, Binance Tests, Lean 4 Verification)")
    ]
    for idx, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(idx, 0); c1 = meta_box.cell(idx, 1)
        c0.width = Inches(2.0); c1.width = Inches(4.5)
        set_cell_background(c0, "F1F5F9"); set_cell_background(c1, "FFFFFF")
        set_cell_borders(c0, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                             left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_borders(c1, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                             left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_margins(c0, top=50, bottom=50, left=90, right=90)
        set_cell_margins(c1, top=50, bottom=50, left=90, right=90)
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(12); sp.paragraph_format.space_after = Pt(4)
    add_callout(
        doc,
        [
            "\"This workbook provides the 12 substantive questions covering our latest Paper 1 draft. "
            "Because you have our earlier draft, these questions focus specifically on the newly added sections: "
            "the registered 12-market CFTC replication (Table 8), the Binance perpetuals tests (Table 9), "
            "exact multinomial Bitcoin noise resampling (Table 6), the two-root stock-flow bridge, "
            "the finite-horizon inventory decision note (Appendix F), and the 787 Lean 4 verified theorems. "
            "Please read the specified sections and provide your detailed mathematical, empirical, and economic answers in the workspaces below.\"",
            "— Pratik Niroula"
        ],
        title="NOTE TO CO-AUTHORS",
        alert_type="info"
    )
    doc.add_page_break()

    # 12 Questions (Clean & Raw)
    for q in QUESTIONS:
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Question {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Where to Read in Paper 1": q["reading_ref"],
            "Key Mathematical Objects": q["key_objects"]
        })
        
        p_q_body = doc.add_paragraph()
        style_body(p_q_body, bold_prefix="Question: ", text=q["question"])
        
        p_req_hdr = doc.add_paragraph(); style_heading_3(p_req_hdr); p_req_hdr.add_run("Required Analysis Points:")
        for idx, sq in enumerate(q["subquestions"], 1):
            p_sq = doc.add_paragraph()
            p_sq.paragraph_format.space_before = Pt(1); p_sq.paragraph_format.space_after = Pt(2)
            p_sq.paragraph_format.line_spacing = 1.15
            r_num = p_sq.add_run(f"{idx}. ")
            r_num.font.name = "Calibri"; r_num.font.size = Pt(9.5); r_num.font.bold = True; r_num.font.color.rgb = RGB_SLATE
            r_sq = p_sq.add_run(sq)
            r_sq.font.name = "Calibri"; r_sq.font.size = Pt(9.5); r_sq.font.color.rgb = RGB_CHARCOAL
            
        p_sujan = doc.add_paragraph(); style_body(p_sujan, "Focus for Sujan: ", q["sujan_note"])
        p_prashant = doc.add_paragraph(); style_body(p_prashant, "Focus for Prashant: ", q["prashant_note"])
        
        # Dedicated Clean Response Workspace
        p_box_title = doc.add_paragraph()
        p_box_title.paragraph_format.space_before = Pt(8); p_box_title.paragraph_format.space_after = Pt(2)
        p_box_title.paragraph_format.keep_with_next = True
        r_bt = p_box_title.add_run(f"Your Written Answer & Analysis — Question {q['num']}")
        r_bt.font.name = "Calibri"; r_bt.font.size = Pt(10.5); r_bt.font.bold = True; r_bt.font.color.rgb = RGB_NAVY
        
        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, "FAFAFA")
        set_cell_borders(cell, left=("single", "18", "0", STEEL_BLUE),
                               top=("single", "4", "0", LIGHT_BORDER),
                               right=("single", "4", "0", LIGHT_BORDER),
                               bottom=("single", "4", "0", LIGHT_BORDER))
        set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
        
        p_in = cell.paragraphs[0]; p_in.paragraph_format.space_before = Pt(0); p_in.paragraph_format.space_after = Pt(4)
        r_lead = p_in.add_run("[Co-Author Name / Section Lead]: _____________________________________\n")
        r_lead.font.name = "Calibri"; r_lead.font.size = Pt(9.5); r_lead.font.bold = True; r_lead.font.color.rgb = RGB_SLATE
        
        prompts = [
            "Mathematical Derivations & Theoretical Proofs:\n(Detail the exact algebra, state-space representations, or bounds here...)\n\n\n\n\n\n",
            "Economic Intuition & Market Microstructure Analysis:\n(Explain the trading behavior, market impact, and pricing dynamics...)\n\n\n\n\n\n",
            "Empirical Evidence & Policy Evaluation:\n(Analyze CFTC/Binance data, regulatory tags, and surveillance implications...)\n\n\n\n\n"
        ]
        for p_text in prompts:
            p_sub_box = cell.add_paragraph()
            p_sub_box.paragraph_format.space_before = Pt(2); p_sub_box.paragraph_format.space_after = Pt(2)
            r_sb = p_sub_box.add_run(p_text)
            r_sb.font.name = "Calibri"; r_sb.font.size = Pt(9); r_sb.font.color.rgb = RGBColor(150, 150, 150)

        doc.add_page_break()

    out_path = ROOT / "Paper1_Questions_Workbook.docx"
    doc.save(str(out_path))
    print(f"Saved Raw Questions Workbook to: {out_path}")
    return out_path

# ==============================================================================
# BUILDER 2: ANSWERS ONLY MANUAL (Complete Technical Walkthrough)
# ==============================================================================
def build_answers_only_file():
    doc = Document()
    add_header_footer(doc, "Paper 1 Reading Guide: Complete Model Answers & Walkthrough")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36); p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("PAPER 1: COMPLETE MODEL ANSWERS & REFERENCE MANUAL")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("What Prices Cannot Tell a Market Supervisor:\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(20); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "Exhaustive, Publication-Grade Reference Solutions and Detailed Technical Walkthrough for all 12 Reading Modules\n"
        "Development Revision: 2 November 2026 (Strictly Paper 1 Only)"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(11.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=4, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Lead Author & PI", "Pratik Niroula (Minnesota State University, Mankato)"),
        ("Co-Authors", "Sujan Khatiwada (Minnesota State University, Mankato) & Prashant Niroula (Tribhuvan University)"),
        ("Technical Coverage", "Complete derivations, proofs, empirical calibrations, and regulatory policy analysis across all 12 modules")
    ]
    for idx, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(idx, 0); c1 = meta_box.cell(idx, 1)
        c0.width = Inches(2.0); c1.width = Inches(4.5)
        set_cell_background(c0, "F1F5F9"); set_cell_background(c1, "FFFFFF")
        set_cell_borders(c0, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                             left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_borders(c1, top=("single", "4", "0", BORDER_MUTED), bottom=("single", "4", "0", BORDER_MUTED),
                             left=("single", "4", "0", BORDER_MUTED), right=("single", "4", "0", BORDER_MUTED))
        set_cell_margins(c0, top=50, bottom=50, left=90, right=90)
        set_cell_margins(c1, top=50, bottom=50, left=90, right=90)
        p0 = c0.paragraphs[0]; r0 = p0.add_run(k); r0.font.name = "Calibri"; r0.font.size = Pt(9); r0.font.bold = True; r0.font.color.rgb = RGB_SLATE
        p1 = c1.paragraphs[0]; r1 = p1.add_run(v); r1.font.name = "Calibri"; r1.font.size = Pt(9); r1.font.color.rgb = RGB_CHARCOAL

    sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(12); sp.paragraph_format.space_after = Pt(4)
    add_callout(
        doc,
        [
            "\"This reference manual provides the authoritative, publication-grade model answers for each of the 12 questions. "
            "Every answer provides the complete mathematical derivations, parameter definitions, empirical figures from CFTC and Binance, "
            "and institutional policy implications. Co-authors can use this document as the reference benchmark to verify their derivations, "
            "prepare conference presentations, and address referee inquiries.\"",
            "— Pratik Niroula"
        ],
        title="ABOUT THIS REFERENCE MANUAL",
        alert_type="info"
    )
    doc.add_page_break()

    # 12 Modules with Complete Model Answers
    for idx, q in enumerate(QUESTIONS):
        ans_obj = ANSWERS[idx]
        
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Question {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Paper 1 Reading Reference": q["reading_ref"],
            "Key Mathematical Focus": q["key_objects"]
        })
        
        p_m_hdr = doc.add_paragraph(); style_heading_3(p_m_hdr); p_m_hdr.add_run("Question Recap:")
        p_q_txt = doc.add_paragraph(); style_body(p_q_txt, "", q["question"])
        
        p_a_hdr = doc.add_paragraph(); style_heading_2(p_a_hdr)
        p_a_hdr.paragraph_format.space_before = Pt(10); p_a_hdr.paragraph_format.space_after = Pt(4)
        p_a_hdr.paragraph_format.keep_with_next = True
        r_ah = p_a_hdr.add_run(f"Model Answer & Technical Walkthrough — Question {q['num']}")
        r_ah.font.name = "Calibri"; r_ah.font.size = Pt(11.5); r_ah.font.bold = True; r_ah.font.color.rgb = RGB_NAVY
        
        # Styled Box for Model Answer
        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, ANSWER_BG)
        set_cell_borders(cell, left=("single", "24", "0", SLATE_SECONDARY),
                               top=("single", "4", "0", LIGHT_BORDER),
                               right=("single", "4", "0", LIGHT_BORDER),
                               bottom=("single", "4", "0", LIGHT_BORDER))
        set_cell_margins(cell, top=130, bottom=130, left=160, right=160)
        
        # Split answer into sections/paragraphs
        answer_text = ans_obj["answer"]
        paragraphs = [p.strip() for p in answer_text.split("\n\n") if p.strip()]
        
        for p_idx, para in enumerate(paragraphs):
            p = cell.paragraphs[0] if p_idx == 0 else cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            
            # Check for numbered subsection headers
            if para.startswith("1. ") or para.startswith("2. ") or para.startswith("3. ") or para.startswith("4. "):
                lines = para.split("\n", 1)
                r_title = p.add_run(lines[0] + "\n")
                r_title.font.name = "Calibri"; r_title.font.size = Pt(10); r_title.font.bold = True; r_title.font.color.rgb = RGB_SLATE
                if len(lines) > 1:
                    r_body = p.add_run(lines[1])
                    r_body.font.name = "Calibri"; r_body.font.size = Pt(9.5); r_body.font.color.rgb = RGB_CHARCOAL
            else:
                r_body = p.add_run(para)
                r_body.font.name = "Calibri"; r_body.font.size = Pt(9.5); r_body.font.color.rgb = RGB_CHARCOAL
                
        doc.add_page_break()

    out_path = ROOT / "Paper1_Answers_Solution_Manual.docx"
    doc.save(str(out_path))
    print(f"Saved Answers Solution Manual to: {out_path}")
    return out_path

if __name__ == "__main__":
    print("Generating Streamlined Paper 1 Word Files...")
    q_file = build_questions_only_file()
    a_file = build_answers_only_file()
    
    # Mirror files to other paper directories
    dest_dirs = [
        ROOT / "ceiling_suite" / "papers" / "paper1",
        ROOT / "ceiling_suite" / "paper1",
        Path("/Users/pratik_n/.gemini/antigravity/brain/074febfe-ec2d-4a96-a621-f727c283f483")
    ]
    for d in dest_dirs:
        if d.exists():
            shutil.copy2(q_file, d / q_file.name)
            shutil.copy2(a_file, d / a_file.name)
            print(f"Mirrored to: {d}")
            
    print("Streamlined generation and mirroring complete!")
