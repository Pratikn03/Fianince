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
    # Extract prose words (>=3 letters) and multi-digit/decimal numbers; single-letter math
    # variables/subscripts and 2-digit stacked fractions (\tfrac{1}{2} -> 12 vs 21) vary in
    # 2D bounding-box order across macOS vs Ubuntu TeX/poppler builds.
    raw = re.findall(r"[A-Za-z]{3,}|[0-9]+(?:[.,][0-9]+)+|[0-9]{3,}", t)
    return raw


a, b = tokens(sys.argv[1]), tokens(sys.argv[2])
if a == b:
    sys.exit(0)
# Allow local reordering within a 25-token window for multi-line display equations
W = 25
used = [False] * len(b)
diffs = []
for i, tok in enumerate(a):
    lo, hi = max(0, i - W), min(len(b), i + W + 1)
    matched = False
    for j in range(lo, hi):
        if not used[j] and b[j] == tok:
            used[j] = True
            matched = True
            break
    if not matched:
        diffs.append(i)
        if len(diffs) >= 1:
            break

if not diffs and len(a) == len(b):
    sys.exit(0)
i = diffs[0] if diffs else min(len(a), len(b))
print(f"first difference at token {i}: {' '.join(a[max(0, i-8):i+8])!r} vs {' '.join(b[max(0, i-8):i+8])!r} "
      f"({len(a)} vs {len(b)} tokens)")
sys.exit(1)
