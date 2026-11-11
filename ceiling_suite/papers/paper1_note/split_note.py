import subprocess
from pypdf import PdfReader, PdfWriter
r = PdfReader("paper1_note.pdf")
k = next(i for i, p in enumerate(r.pages) if "Online Supplement" in (p.extract_text() or ""))
for name, rng in (("Paper1_note_main.pdf", range(0, k)), ("Paper1_note_supplement.pdf", range(k, len(r.pages)))):
    w = PdfWriter()
    for i in rng: w.add_page(r.pages[i])
    w.write(name)
print(f"main {k} pages; supplement {len(r.pages) - k} pages")
