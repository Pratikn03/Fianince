"""
Script to generate TWO clean, collaborative, reading-focused Word files:
1. Paper1_Questions_Workbook.docx (Questions, Required Analysis & Workspaces Only)
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
# BUILDER 1: QUESTIONS ONLY WORKBOOK (Reading & Written Contribution Guide)
# ==============================================================================
def build_questions_only_file():
    doc = Document()
    add_header_footer(doc, "Paper 1 Co-Author Reading & Contribution Workbook")
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36); p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("CO-AUTHOR READING & CONTRIBUTION WORKBOOK")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Paper 1: What Prices Cannot Tell a Market Supervisor\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(20); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "A Section-by-Section Reading Companion & Analytical Contribution Workbook for Sujan Khatiwada and Prashant Niroula "
        "covering the Latest November 2026 Revision of Paper 1"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(12); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=5, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Lead Author & PI", "Pratik Niroula (Minnesota State University, Mankato)"),
        ("Co-Authors", "Sujan Khatiwada (Minnesota State University, Mankato) & Prashant Niroula (Tribhuvan University)"),
        ("Current Manuscript Revision", "Development Revision: 2 November 2026 (787 Lean 4 Theorems, 20 CFTC Markets, October 2026 Binance Perpetuals)"),
        ("Workbook Purpose", "Guide co-authors through the newly added sections of the latest draft and provide dedicated workspaces for their analytical contributions")
    ]
    for idx, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(idx, 0); c1 = meta_box.cell(idx, 1)
        c0.width = Inches(2.2); c1.width = Inches(4.3)
        set_cell_background(c0, "F1F5F9"); set_cell_background(c1, "FFFFFF")
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
            "\"Welcome Sujan and Prashant! This reading workbook is designed to guide us through our updated Paper 1 draft section by section. "
            "You have our older draft, but our latest November 2026 revision includes major new analytical breakthroughs: the pre-registered "
            "12-market CFTC replication (Table 8), the October 2026 Binance perpetuals tests (Table 9), exact multinomial Bitcoin noise resampling, "
            "the two-root stock-flow inventory bridge, the finite-horizon inventory decision note (Appendix F), and 100% Lean 4 machine verification. "
            "Please read each section thoroughly, reflect on the questions, and write your detailed analysis in the provided workspace. "
            "Your written submissions will serve as your direct co-author analytical contribution to the manuscript.\"",
            "— Pratik Niroula (Lead Author & Research Lead)"
        ],
        title="WELCOME & CO-AUTHOR CONTRIBUTION OBJECTIVES",
        alert_type="info"
    )
    doc.add_page_break()

    # Instructions Section
    p_s1 = doc.add_paragraph(); style_heading_1(p_s1); p_s1.add_run("1. How to Use this Reading & Contribution Workbook")
    p_b1 = doc.add_paragraph()
    style_body(
        p_b1,
        "Structure & Submission Process: ",
        "This workbook contains 12 core reading modules that follow the exact structure of Paper 1. "
        "For each module, please follow these four steps:\n"
        "1. Open the latest draft of Paper 1 and read the specified pages, sections, and appendices.\n"
        "2. Review the summary of what is new in this revision compared to the earlier draft.\n"
        "3. Review the main discussion question and the required analysis points.\n"
        "4. In the provided 'Co-Author Written Contribution' workspace, write your complete analysis (aim for ~1 full page, approx. 400–600 words per module). "
        "Address the specific technical derivations, economic intuition, and empirical implications."
    )
    
    # 12 Questions with Clean Workspaces
    for q in QUESTIONS:
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Module {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Where to Read in Paper 1": q["reading_ref"],
            "Key Mathematical Objects": q["key_objects"]
        })
        
        p_c_hdr = doc.add_paragraph(); style_heading_3(p_c_hdr); p_c_hdr.add_run("Overview & Context from Latest Draft")
        p_ctx = doc.add_paragraph(); style_body(p_ctx, "", q["summary"])
        
        p_m_hdr = doc.add_paragraph(); style_heading_3(p_m_hdr); p_m_hdr.add_run("Core Discussion Question")
        add_callout(doc, [q["question"]], title="MAIN DISCUSSION QUESTION", alert_type="info")
        
        p_sq_hdr = doc.add_paragraph(); style_heading_3(p_sq_hdr); p_sq_hdr.add_run("Required Analysis Points to Cover")
        for sq in q["subquestions"]:
            p_sq = doc.add_paragraph(style='List Bullet')
            p_sq.paragraph_format.space_before = Pt(2); p_sq.paragraph_format.space_after = Pt(3)
            style_body(p_sq, "", sq)
            
        p_co_hdr = doc.add_paragraph(); style_heading_3(p_co_hdr); p_co_hdr.add_run("Specific Co-Author Focus")
        p_sujan = doc.add_paragraph(); style_body(p_sujan, "For Sujan Khatiwada: ", q["sujan_note"])
        p_prashant = doc.add_paragraph(); style_body(p_prashant, "For Prashant Niroula: ", q["prashant_note"])
        
        # Dedicated Clean Response Box
        p_box_title = doc.add_paragraph()
        p_box_title.paragraph_format.space_before = Pt(10); p_box_title.paragraph_format.space_after = Pt(3)
        p_box_title.paragraph_format.keep_with_next = True
        r_bt = p_box_title.add_run(f"Co-Author Written Contribution Workspace — Module {q['num']}")
        r_bt.font.name = "Calibri"; r_bt.font.size = Pt(11); r_bt.font.bold = True; r_bt.font.color.rgb = RGB_NAVY
        
        desc = doc.add_paragraph(); desc.paragraph_format.space_before = Pt(0); desc.paragraph_format.space_after = Pt(4)
        r_desc = desc.add_run(
            f"Please write your thorough analysis and response here (~1 full page, approx. 400–600 words). "
            f"Address all required analysis points, detail the mathematical derivations, and provide institutional and empirical interpretations."
        )
        r_desc.font.name = "Calibri"; r_desc.font.size = Pt(9.5); r_desc.font.italic = True; r_desc.font.color.rgb = RGB_MUTED

        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, "FAFAFA")
        set_cell_borders(cell, left=("single", "18", "0", STEEL_BLUE),
                               top=("single", "4", "0", LIGHT_BORDER),
                               right=("single", "4", "0", LIGHT_BORDER),
                               bottom=("single", "4", "0", LIGHT_BORDER))
        set_cell_margins(cell, top=160, bottom=160, left=180, right=180)
        
        p_in = cell.paragraphs[0]; p_in.paragraph_format.space_before = Pt(0); p_in.paragraph_format.space_after = Pt(4)
        r_lead = p_in.add_run("[Co-Author Name / Section Lead]: _____________________________________\n")
        r_lead.font.name = "Calibri"; r_lead.font.size = Pt(10); r_lead.font.bold = True; r_lead.font.color.rgb = RGB_SLATE
        
        prompts = [
            "1. Mathematical Derivations & Theoretical Architecture:\n   (Write your detailed mathematical steps and structural proofs here...)\n\n\n\n\n",
            "2. Economic Intuition & Market Microstructure Analysis:\n   (Explain the economic mechanics, trader behavior, and price impact dynamics...)\n\n\n\n\n",
            "3. Institutional Data, Regulatory Policy & Empirical Evaluation:\n   (Analyze CFTC/Binance data, audit trail requirements, and surveillance consequences...)\n\n\n\n\n",
            "4. Synthesis, Verification & Open Questions for Manuscript Expansion:\n   (Note any feedback, proposed extensions, or Lean verification thoughts...)\n\n\n\n"
        ]
        for p_text in prompts:
            p_sub_box = cell.add_paragraph()
            p_sub_box.paragraph_format.space_before = Pt(2); p_sub_box.paragraph_format.space_after = Pt(2)
            r_sb = p_sub_box.add_run(p_text)
            r_sb.font.name = "Calibri"; r_sb.font.size = Pt(9.5); r_sb.font.color.rgb = RGBColor(140, 140, 140)

        doc.add_page_break()

    out_path = ROOT / "Paper1_Questions_Workbook.docx"
    doc.save(str(out_path))
    print(f"Saved Questions Workbook to: {out_path}")
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
    r_pre = p_pre.add_run("PAPER 1 READING GUIDE: COMPLETE MODEL ANSWERS & REFERENCE MANUAL")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(13); r_pre.font.bold = True; r_pre.font.color.rgb = RGB_STEEL
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Paper 1: What Prices Cannot Tell a Market Supervisor\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(20); r_title.font.bold = True; r_title.font.color.rgb = RGB_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run(
        "Exhaustive, Publication-Grade Reference Solutions and Detailed Technical Walkthrough for all 12 Reading Modules\n"
        "Development Revision: 2 November 2026"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(12); r_sub.font.italic = True; r_sub.font.color.rgb = RGB_SLATE

    # Metadata table
    meta_box = doc.add_table(rows=5, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER; meta_box.autofit = False
    meta_items = [
        ("Manuscript", "What Prices Cannot Tell a Market Supervisor: The Cost of Identifying Trader Groups and the Value of Class Disclosure"),
        ("Lead Author & PI", "Pratik Niroula (Minnesota State University, Mankato)"),
        ("Co-Authors", "Sujan Khatiwada (Minnesota State University, Mankato) & Prashant Niroula (Tribhuvan University)"),
        ("Manual Purpose", "Authoritative reference solutions and analytical walkthrough for co-author review, presentation preparation, and journal defense"),
        ("Technical Coverage", "Complete derivations, proofs, empirical calibrations, and regulatory policy analysis across all 12 modules")
    ]
    for idx, (k, v) in enumerate(meta_items):
        c0 = meta_box.cell(idx, 0); c1 = meta_box.cell(idx, 1)
        c0.width = Inches(2.2); c1.width = Inches(4.3)
        set_cell_background(c0, "F1F5F9"); set_cell_background(c1, "FFFFFF")
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
            "\"This reference manual provides the definitive, publication-grade model answers for each of the 12 modules in our reading guide. "
            "Every answer provides the complete mathematical derivations, parameter definitions, empirical figures from CFTC and Binance, "
            "and institutional policy implications. Co-authors can use this document as the reference benchmark to verify their derivations, "
            "prepare conference presentations, and address referee inquiries.\"",
            "— Pratik Niroula (Lead Author & Research Lead)"
        ],
        title="ABOUT THIS REFERENCE MANUAL",
        alert_type="info"
    )
    doc.add_page_break()

    # Introduction
    p_s1 = doc.add_paragraph(); style_heading_1(p_s1); p_s1.add_run("1. Master Overview of Paper 1's Results")
    p_b1 = doc.add_paragraph()
    style_body(
        p_b1,
        "Paper 1's Unified Architecture: ",
        "Paper 1 investigates what a market supervisor can and cannot learn about the internal composition of trader groups "
        "by observing transaction prices. The paper establishes a fundamental identification boundary: price feedback transforms "
        "individual trader learning rates into transmission zeros of the open loop, burying them inside the closed-loop characteristic polynomial. "
        "Separating K trader cohorts requires sample sizes scaling as Ω(σ² (Δη)^{-(4K-2)}). Active market probing costs quadratic execution losses "
        "and requires cash capital scaling as Ω(δ^{-4}). Passively watching prices costs time at the exact same polynomial rate under Whittle divergence. "
        "Continuous memory causes the rate to collapse to logarithmic 1 / log(N / σ²). Mandating class disclosure (MiFID II RTS 24) completely uncouples "
        "the estimation problem, dropping sample complexity to (Δη)^{-2} for rates and O(1) for weights. In 20 CFTC futures markets, mandated disclosure "
        "narrows parameter intervals by 23x to 69x. Finally, while aggregate inventory warehousing requires only the scalar cumulative response at rate "
        "O(N^{-1/2}), targeted supervisory interventions strictly require individual cohort deconvolution, proving that granular algorithmic tags "
        "are essential for market surveillance."
    )
    
    # 12 Modules with Complete Model Answers
    for idx, q in enumerate(QUESTIONS):
        ans_obj = ANSWERS[idx]
        
        p_q = doc.add_paragraph(); style_heading_1(p_q); p_q.add_run(f"Module {q['num']}: {q['title']}")
        add_metadata_table(doc, {
            "Paper 1 Reading Reference": q["reading_ref"],
            "Key Mathematical Focus": q["key_objects"]
        })
        
        p_m_hdr = doc.add_paragraph(); style_heading_3(p_m_hdr); p_m_hdr.add_run("Discussion Question Recap")
        add_callout(doc, [q["question"]], title=f"MODULE {q['num']} QUESTION", alert_type="info")
        
        p_a_hdr = doc.add_paragraph(); style_heading_2(p_a_hdr)
        p_a_hdr.paragraph_format.space_before = Pt(12); p_a_hdr.paragraph_format.space_after = Pt(4)
        p_a_hdr.paragraph_format.keep_with_next = True
        r_ah = p_a_hdr.add_run(f"Complete Model Answer & Technical Walkthrough — Module {q['num']}")
        r_ah.font.name = "Calibri"; r_ah.font.size = Pt(12); r_ah.font.bold = True; r_ah.font.color.rgb = RGB_NAVY
        
        # Styled Box for Model Answer
        tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        cell = tbl.cell(0, 0); cell.width = Inches(6.5)
        set_cell_background(cell, ANSWER_BG)
        set_cell_borders(cell, left=("single", "24", "0", SLATE_SECONDARY),
                               top=("single", "4", "0", LIGHT_BORDER),
                               right=("single", "4", "0", LIGHT_BORDER),
                               bottom=("single", "4", "0", LIGHT_BORDER))
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        
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
                r_title.font.name = "Calibri"; r_title.font.size = Pt(10.5); r_title.font.bold = True; r_title.font.color.rgb = RGB_SLATE
                if len(lines) > 1:
                    r_body = p.add_run(lines[1])
                    r_body.font.name = "Calibri"; r_body.font.size = Pt(10); r_body.font.color.rgb = RGB_CHARCOAL
            else:
                r_body = p.add_run(para)
                r_body.font.name = "Calibri"; r_body.font.size = Pt(10); r_body.font.color.rgb = RGB_CHARCOAL
                
        doc.add_page_break()

    out_path = ROOT / "Paper1_Answers_Solution_Manual.docx"
    doc.save(str(out_path))
    print(f"Saved Answers Solution Manual to: {out_path}")
    return out_path

if __name__ == "__main__":
    print("Generating Paper 1 Word Files (Strictly Paper 1 Only)...")
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
            
    print("Generation and mirroring complete!")
