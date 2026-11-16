#!/usr/bin/env python3
"""Build the one-page Errata and Integrity Note PDF for the Paper 1 public-data revision.

Run from the repository root:
    .venv/bin/python research_extension/paper1_public_data_study_20261116/build_errata_note.py
"""
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

OUT = Path(__file__).with_name("Errata_Integrity_Note_S31_20261115.pdf")

title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=13, leading=16, spaceAfter=4)
sub = ParagraphStyle("sub", fontName="Helvetica-Oblique", fontSize=9.5, leading=13,
                     textColor="#444444", spaceAfter=8)
h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
                   spaceBefore=10, spaceAfter=3)
body = ParagraphStyle("body", fontName="Helvetica", fontSize=9.5, leading=13.5,
                      alignment=TA_JUSTIFY)
mono = ParagraphStyle("mono", parent=body, fontName="Courier", fontSize=8.2, leading=11,
                      leftIndent=14, spaceBefore=2, spaceAfter=2)

doc = SimpleDocTemplate(str(OUT), pagesize=letter,
                        leftMargin=0.95 * inch, rightMargin=0.95 * inch,
                        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
                        title="Errata and Integrity Note — Paper 1 Public-Data Revision",
                        author="Author-side review session")

story = [
    Paragraph("Errata and Integrity Note", title),
    Paragraph("To accompany: <i>Observationally Equivalent Algorithms: What Prices Reveal About "
              "Trader Populations, and What Supervisors Need</i> — 141-page public-data revision dated "
              "16 November 2026 (delivered PDF SHA-256 2b02c1e6fe980d4db605bb6336cd5af4378d111d"
              "5fc0549f098881cb43cc951c). Issued 15 November 2026 by the author-side review session.", sub),
    HRFlowable(width="100%", thickness=0.7, color="#888888"),

    Paragraph("E1 — S31.1 protocol-lock timestamp (consistency correction)", h),
    Paragraph("The sentence “The protocol was locked on 16 November 2026 before final-validation "
              "outcome extraction (SHA-256 4345510f…b40e)” should read:", body),
    Paragraph("“The protocol (SHA-256 4345510fd1d1b16021483a726494f0aafb21f3b7bc7045bc522c5c1d3204b40e) "
              "was locked before the final-validation outcome extraction recorded in the run manifest, "
              "which ran 15 November 2026, 22:33:53–22:36:30 UTC; 16 November 2026 is the manuscript "
              "revision date, not the lock time.”", mono),
    Paragraph("Rationale: the run manifest’s <i>started_utc</i>/<i>finished_utc</i> fall on 15 November UTC "
              "and <i>outcome_available_on_2026_11_16</i> is false; the lock’s evidential force depends on "
              "it preceding final-validation extraction. No design, data, or result is affected.", body),

    Paragraph("E2 — Frozen candidate list integrity (reproducibility addition)", h),
    Paragraph("In S31.1, immediately after the address-ordering sentence, add:", body),
    Paragraph("“The frozen 192-candidate list has SHA-256 "
              "6d4fd1fbbac918f1bd97f5d3cb6ac79bc206a8cf9421147e70c05f37ab55ce58 (run manifest); the "
              "originating 47,705-row leaderboard frame snapshot is retained with its hash for third-party "
              "verification and will be deposited with the replication archive.”", mono),
    Paragraph("This closes the publicly checkable chain 47,705 addresses → 192 candidates → 60 complete "
              "histories without disclosing any new data.", body),

    Paragraph("Verification statement", h),
    Paragraph("On 15 November 2026 the undersigned review session checked every empirical value printed "
              "in S31 against the delivered evidence package: Table S7 coverage/admission/exceedance, the "
              "block-bootstrap interval [0.732143, 0.964286], the ten-specification robustness coverage "
              "range 83.929–92.857%, the forecast and placebo diagnostics, the drawdown and range "
              "observables, and the sampling-ledger counts (192 queried; 111 empty; 81 nonempty; "
              "6 retention-truncated; 60 complete). All match the machine-readable summaries exactly. "
              "No other discrepancy was found.", body),
    Spacer(1, 10),
    HRFlowable(width="100%", thickness=0.7, color="#888888"),
    Paragraph("Repository: Pratikn03/Fianince · integration commit fa87234e · evidence package: "
              "research_extension/paper1_public_data_study_20261116/ (zip SHA-256 "
              "6d414fd7bf555eb5b2d26b09f019e55ce9786496cb3595b47a117eb9c4df5e57).", sub),
]

doc.build(story)
print("written:", OUT)
