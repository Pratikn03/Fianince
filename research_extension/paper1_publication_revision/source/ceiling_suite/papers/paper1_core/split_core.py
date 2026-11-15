from pypdf import PdfReader, PdfWriter
import shutil, os
r = PdfReader("paper1_core.pdf")
i = [k for k, p in enumerate(r.pages) if "Online Supplement" in (p.extract_text() or "")[:300]][0]
for name, rng in (("main", range(0, i)), ("supplement", range(i, len(r.pages)))):
    w = PdfWriter()
    for k in rng: w.add_page(r.pages[k])
    w.write(f"Paper1_core_{name}.pdf")
shutil.copy("paper1_core.pdf", "Paper1_core_combined.pdf")
os.makedirs("../../../pdf_delivered", exist_ok=True)
for f in ("Paper1_core_main.pdf", "Paper1_core_supplement.pdf", "Paper1_core_combined.pdf"):
    shutil.copy(f, "../../../pdf_delivered/" + f)
print("main", i, "pages; supplement", len(r.pages) - i, "pages")
