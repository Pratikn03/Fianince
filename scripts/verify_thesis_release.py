"""Read-only gates for frozen evidence, documentation counts and the delivered thesis PDF."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def verify(pdf=False):
    frozen = json.loads((ROOT / "thesis/checks/registered_artifacts_sha256.json").read_text())
    for relative, expected in frozen["files"].items():
        path = ROOT / relative
        assert path.is_file(), f"missing frozen artifact: {relative}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"frozen artifact changed: {relative}"
    formal = ROOT / "research_extension/current_manuscript_lean_20261008"
    entries = json.loads((formal / "named_declarations.json").read_text())
    count = len(entries)
    receipt = json.loads((formal / "formal_verification_receipt.json").read_text())
    assert receipt["named_theorems"] == count
    assert receipt["full_manuscript_formalization_complete"] is False
    for relative, expected in receipt["formal_source_sha256"].items():
        assert hashlib.sha256((formal / relative).read_bytes()).hexdigest() == expected, relative
    readme = (ROOT / "README.md").read_text()
    coverage = (ROOT / "COVERAGE.md").read_text()
    assert f"{count} named theorems" in readme and f"**{count}** named theorems" in coverage
    tags = re.findall(r"\| \*\*`(full|conditional|arithmetic)`\*\* \|", coverage)
    assert f"{len(tags)} environments" in readme
    for tag in ("full", "conditional", "arithmetic"):
        assert re.search(rf"{tags.count(tag)}(?: are tagged)? `{tag}`", readme)
    # These recently registered follow-ups were absent from the legacy verifier.
    for spec_name, mappings in (
        ("B3_diversity", {"b3_sha256": "b3_diversity.py", "llm_sha256": "llm_ailoop.py",
                          "sim_sha256": "ailoop_sim.py", "b1_sha256": "b1_ailoop.py"}),
        ("H2_cascade", {"h2_sha256": "h2_cascade.py", "h1_sha256": "h1_hyperliquid.py",
                        "c3_sha256": "c3_margin_more_days.py", "c2_sha256": "c2_margin_vs_identify.py",
                        "pilot4_sha256": "pilot4_curve_and_risk.py"}),
        ("K1_letf", {"k1_sha256": "k1_letf.py"}),
    ):
        spec_path = ROOT / f"thesis/checks/prereg/{spec_name}.json"
        spec = json.loads(spec_path.read_text())
        assert hashlib.sha256(spec_path.read_bytes()).hexdigest() == spec_path.with_suffix(".sha256").read_text().strip()
        for key, filename in mappings.items():
            assert hashlib.sha256((ROOT / "thesis/evidence" / filename).read_bytes()).hexdigest() == spec[key]
    if pdf:
        from pypdf import PdfReader
        reader = PdfReader(ROOT / "thesis/thesis.pdf")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        compact = re.sub(r"\s+", "", text).replace("_", "")
        for phrase in ("ResultofTestB2.", "3.5", "252,798", "Posthocsensitivityandreproducibility.", "modelsnapshot=null"):
            assert phrase in compact, f"committed PDF lacks current B2 content: {phrase}"
        for obsolete in ("At the time of writing its single run is pending", "whose run is pending"):
            assert re.sub(r"\s+", "", obsolete) not in compact, obsolete
        assert not re.search(r"\?\?", text), "unresolved PDF references"
        print(f"Current thesis PDF content: PASS ({len(reader.pages)} pages)")
    print(f"Frozen artifacts ({len(frozen['files'])}), formal sources and documentation: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true")
    verify(ap.parse_args().pdf)
