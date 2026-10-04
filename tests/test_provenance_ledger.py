"""The provenance ledger must (a) pass on the current paper and artifacts and (b) fail when either drifts.

These tests are deliberately falsifiable: they mutate the manuscript text or a claim's printed value
and require the checker to notice.
"""
import dataclasses
import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provenance_ledger", ROOT / "scripts" / "provenance_ledger.py")
ledger = importlib.util.module_from_spec(spec)
sys.modules["provenance_ledger"] = ledger
spec.loader.exec_module(ledger)

WORDS = {"3": "three", "9": "nine", "20": "twenty", "7": "seven"}


def test_every_claim_verified():
    bad = ledger.check()
    assert not bad, "\n".join(f"{c.cid}: {why} (printed {c.printed!r}, computed {got!r})" for c, why, got in bad)


def test_claim_ids_unique():
    ids = [c.cid for c in ledger.CLAIMS]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("claim", [c for c in ledger.CLAIMS if c.printed != "present"], ids=lambda c: c.cid)
def test_printed_tokens_appear_in_paper_snippet(claim):
    """The value we verify must be the value the paper shows, not a free-floating string."""
    flat = re.sub(r"\s+", " ", claim.tex)
    for tok in claim.printed.split("/"):
        assert tok in flat or WORDS.get(tok, "\0") in flat, f"{claim.cid}: {tok!r} not in {flat!r}"


@pytest.mark.parametrize("claim", ledger.CLAIMS[::7], ids=lambda c: c.cid)
def test_paper_edit_is_detected(claim):
    """Changing the paper's text for a claim must break the ledger."""
    paper = ledger.TEX.read_text()
    flat = re.sub(r"\s+", " ", paper)
    target = re.sub(r"\s+", " ", claim.tex)
    i = next((k for k, ch in enumerate(target) if ch.isdigit()), None)
    if i is None:  # number written as a word, e.g. "three"
        w = next(v for v in WORDS.values() if v in target)
        bumped = target.replace(w, "four" if w != "four" else "five", 1)
    else:
        bumped = target[:i] + str((int(target[i]) + 1) % 10) + target[i + 1:]
    mutated = flat.replace(target, bumped)
    assert mutated != flat
    failing = {c.cid for c, _, _ in ledger.check(mutated)}
    assert claim.cid in failing


@pytest.mark.parametrize("claim", [c for c in ledger.CLAIMS if c.printed != "present"][::5], ids=lambda c: c.cid)
def test_wrong_printed_value_is_detected(claim):
    """If the paper printed a different number, recomputation from the artifact must disagree."""
    toks = claim.printed.split("/")
    wrong = "/".join(toks[:-1] + [toks[-1] + "1"])
    assert claim.value() != wrong


def test_withdrawn_items_listed():
    assert len(ledger.WITHDRAWN) >= 10
    names = " ".join(a for a, _ in ledger.WITHDRAWN)
    for key in ("2SLS", "Table 24", "DQN", "7.2e-14"):
        assert key in names


def test_generated_ledger_files_written(tmp_path, monkeypatch):
    ledger.render()
    assert (ROOT / "paper" / "generated" / "provenance_ledger.tex").exists()
    assert (ROOT / "results" / "provenance" / "ledger.md").exists()
    body = (ROOT / "paper" / "generated" / "provenance_ledger.tex").read_text()
    assert body.count(r"\\") >= len(ledger.CLAIMS)
