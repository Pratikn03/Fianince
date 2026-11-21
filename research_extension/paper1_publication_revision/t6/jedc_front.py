"""Journal (JEDC) submission version: the journal version with a 98-word abstract and no working-paper date line.
Highlights and the cover letter are separate files (ceiling_suite/papers/paper1/review/JEDC_SUBMISSION_20261121.md)."""
import re

ABSTRACT = (r"Algorithmic traders read prices and, by trading, move them. We show that the population of such traders "
            r"affects prices, order flows and dealer inventories only through its aggregate feedback response, also in "
            r"equilibrium, and that separating $K$ trader types whose rules lie within $\Delta$ needs of order "
            r"$\Delta^{-(4K-2)}$ observations. A uniform cut in feedback can therefore be set from prices and, without "
            r"class tags, is the minimax supervisory policy; targeted restrictions need tags, which help only if "
            r"relabeling is costly. In Taiwan's tagged exchange flows, prices pin down a uniform cut but cannot "
            r"attribute feedback to trading classes.")


def apply(ssrn_tex):
    t = ssrn_tex
    m = re.search(r"(\\begin\{abstract\}\n\\noindent ).*?(\n\\end\{abstract\})", t, re.S)
    assert m, "abstract not found"
    t = t[:m.start()] + m.group(1) + ABSTRACT + m.group(2) + t[m.end():]
    d = re.search(r"\\date\{Working paper, [^}]*\}", t)
    assert d, "date line not found"
    t = t[:d.start()] + r"\date{November 2026}" + t[d.end():]
    return t
