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


def same_token(x: str, y: str) -> bool:
    if x == y:
        return True
    # pdftotext orders stacked \tfrac{a}{b} numerator/denominator as ab on Ubuntu vs ba on macOS
    return len(x) == 2 and len(y) == 2 and x.isdigit() and y.isdigit() and x == y[::-1]


a, b = tokens(sys.argv[1]), tokens(sys.argv[2])
if len(a) == len(b) and all(same_token(x, y) for x, y in zip(a, b)):
    sys.exit(0)
i = next((k for k, (x, y) in enumerate(zip(a, b)) if not same_token(x, y)), min(len(a), len(b)))
print(f"first difference at token {i}: {' '.join(a[max(0, i-8):i+8])!r} vs {' '.join(b[max(0, i-8):i+8])!r} "
      f"({len(a)} vs {len(b)} tokens)")
sys.exit(1)
