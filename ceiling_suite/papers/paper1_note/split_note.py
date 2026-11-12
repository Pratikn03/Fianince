"""Splits the note PDF at the page that begins the online supplement.
Usage: python3 split_note.py [in.pdf main.pdf supplement.pdf]; defaults to the 1.5-spaced working version."""
import sys
from pypdf import PdfReader, PdfWriter
src, out_main, out_supp = (sys.argv[1:4] if len(sys.argv) >= 4 else
                           ("paper1_note.pdf", "Paper1_note_main.pdf", "Paper1_note_supplement.pdf"))
r = PdfReader(src)
k = next(i for i, p in enumerate(r.pages) if "Online Supplement" in (p.extract_text() or ""))
for name, rng in ((out_main, range(0, k)), (out_supp, range(k, len(r.pages)))):
    w = PdfWriter()
    for i in rng: w.add_page(r.pages[i])
    w.write(name)
print(f"{src}: main {k} pages; supplement {len(r.pages) - k} pages")
