"""Addendum A1 to Test F1 (registered before any F1 data were downloaded).

What happened. F1 was opened (counter 1) in Colab, but drawing the universe failed before any symbol was chosen and before
any market data were downloaded: the public archive now lists a perpetual whose symbol is written in Chinese characters
(the run stopped on "哈基米USDT"). Python's str.isalnum() accepts such characters, so the universe rule's filter let the
symbol through, and the download helper cannot form an ASCII URL for it. No universe file was written and no data were
seen.

What changes. Only the universe filter: candidate symbols must also be ASCII (str.isascii()), which is what the rule's
"isalnum" was meant to express and what every earlier universe (C2, C3) satisfied. Everything else in the registered
specification and pipeline is unchanged; the pipeline file and its hash are untouched. The run continues with
resume=True (the counter stays at 1), draws the universe under the corrected filter, writes it, and only then downloads.
"""
import c2_margin_vs_identify as C2


def apply():
    orig = C2.list_archive_symbols
    if getattr(orig, "_f1_ascii_only", False):
        return
    def ascii_only():
        return [s for s in orig() if s.isascii()]
    ascii_only._f1_ascii_only = True
    C2.list_archive_symbols = ascii_only
