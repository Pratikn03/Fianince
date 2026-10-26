"""Seal a review package of the canonical thesis, reproduction inputs and archived evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "thesis/SUBMISSION_MANIFEST.json"


def inputs():
    paths = set()
    trees = ["thesis", "margin_monitor", "research_extension/current_manuscript_lean_20261008",
             "ceiling_suite/papers/paper1", "ceiling_suite/papers/paper2", "ceiling_suite/papers/flagship"]
    extensions = {".tex", ".py", ".json", ".jsonl", ".sha256", ".md", ".sh", ".pdf", ".gz", ".ipynb", ".toml", ".lean"}
    for tree in trees:
        for path in (ROOT / tree).rglob("*"):
            relative = path.relative_to(ROOT)
            if any(part in {".lake", ".venv", "__pycache__", "submission", ".pytest_cache"} for part in relative.parts):
                continue
            if path.is_file() and not path.is_symlink() and (path.suffix in extensions or path.name in {"LICENSE", "lean-toolchain"}):
                paths.add(str(relative))
    paths.discard(str(MANIFEST.relative_to(ROOT)))
    paths.update(["README.md", "COVERAGE.md", "requirements-runtime.txt", "requirements-artifacts.txt",
                  "scripts/verify_thesis_release.py", "scripts/package_thesis.py"])
    return sorted(paths)


def seal():
    files = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inputs()}
    manifest = {
        "kind": "THESIS_REVIEW_PACKAGE_NOT_INSTITUTIONAL_APPROVAL",
        "baseline_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "snapshot_identity": "SHA-256 of individual files; includes local edits, not a claim of committed CI",
        "canonical_pdf": "thesis/thesis.pdf",
        "scope": "Thesis draft, source/build inputs, archived thesis evidence, standalone margin-monitor and current Lean source/receipts. Full repository and raw market/model downloads are not included.",
        "files": files,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def check():
    manifest = json.loads(MANIFEST.read_text())
    assert set(manifest["files"]) == set(inputs()), "package input set changed; reseal explicitly"
    for relative, digest in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative
    print(f"Submission manifest: PASS ({len(manifest['files'])} files)")
    return manifest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal", action="store_true", help="write the manifest for current local inputs")
    ap.add_argument("--zip", action="store_true", help="package the sealed, verified inputs")
    args = ap.parse_args()
    if args.seal:
        seal()
    manifest = check()
    if args.zip:
        output = ROOT / "thesis/submission/Thesis_Review_Package_20261026.zip"
        output.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative in sorted([*manifest["files"], str(MANIFEST.relative_to(ROOT))]):
                archive.write(ROOT / relative, relative)
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n")
        print(output)
