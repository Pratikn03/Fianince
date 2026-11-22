"""Journal (JEDC) submission version: the journal version with an abstract under 100 words and no working-paper date line.
Highlights and the cover letter are separate files (ceiling_suite/papers/paper1/review/JEDC_SUBMISSION_20261121.md)."""
import re

ABSTRACT = (r"Algorithmic traders read prices and move them. We show that a population of such traders "
            r"affects prices, order flows and dealer inventories only through its aggregate feedback response, also in "
            r"equilibrium, and that in the worst case separating $K$ trader types whose rules lie within $\Delta$ takes "
            r"on the order of $\Delta^{-(4K-2)}$ observations. Given the market's persistence and a memory bound, a "
            r"uniform cut in feedback can be set from prices and, without class tags, is minimax over labellings; "
            r"targeted restrictions need tags, which help only if relabeling is costly. A calibration to Taiwan's "
            r"tagged exchange flows illustrates the barrier.")


def apply(ssrn_tex):
    t = ssrn_tex
    m = re.search(r"(\\begin\{abstract\}\n\\noindent ).*?(\n\\end\{abstract\})", t, re.S)
    assert m, "abstract not found"
    t = t[:m.start()] + m.group(1) + ABSTRACT + m.group(2) + t[m.end():]
    d = re.search(r"\\date\{Working paper, [^}]*\}", t)
    assert d, "date line not found"
    t = t[:d.start()] + r"\date{November 2026}" + t[d.end():]
    return t
