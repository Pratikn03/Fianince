"""Platform-independent text fingerprint of a PDF for reproduction checks.

pdftotext output differs across TeX/poppler builds in glyph mapping (footnote symbols such as * vs U+2217,
dagger vs a control byte) and in layout spacing, which made the macOS-built delivered PDFs fail a byte
comparison against the Ubuntu CI rebuild. This compares the stream of words and numbers instead: every
word, digit and decimal point must match in order; symbol glyphs, whitespace and end-of-line hyphenation
are ignored.
Usage: python3 pdf_text_tokens.py A.txt B.txt  (exit 0 if equal, 1 otherwise, printing the first difference)
"""
import re
import sys


def tokens(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"-\s*\n\s*", "", t)            # undo end-of-line hyphenation
    return re.findall(r"[A-Za-z0-9]+(?:[.,][0-9]+)*", t)


a, b = tokens(sys.argv[1]), tokens(sys.argv[2])
if a == b:
    sys.exit(0)
i = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
print(f"first difference at token {i}: {' '.join(a[max(0, i-8):i+8])!r} vs {' '.join(b[max(0, i-8):i+8])!r} "
      f"({len(a)} vs {len(b)} tokens)")
sys.exit(1)
