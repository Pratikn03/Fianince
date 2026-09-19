"""Evidence-freeze and completion-gate records for the research extension."""
from __future__ import annotations

from datetime import date
import hashlib
from pathlib import Path
from typing import Any, Iterable


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_evidence_manifest(
    root: Path,
    *,
    exclude_prefixes: Iterable[str] = ("research_extension/outputs/",),
) -> dict[str, Any]:
    """Hash the current release without hashing generated manifest outputs."""
    root = Path(root).resolve()
    prefixes = tuple(exclude_prefixes)
    records = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        if any(relative.startswith(prefix) for prefix in prefixes):
            continue
        if any(part in {"__pycache__", ".pytest_cache"} for part in path.relative_to(root).parts):
            continue
        records.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })
    return {
        "schema": "machine-markets-evidence-manifest-1",
        "generated_on": date.today().isoformat(),
        "root": str(root),
        "file_count": len(records),
        "files": records,
        "frozen_master_manifest": "SHA256SUMS.txt",
        "scope_note": "This extension manifest records the working release; the original master manifest remains immutable.",
    }


def gate_status() -> dict[str, dict[str, Any]]:
    """Return auditable status for every plan gate without overstating completion."""
    return {
        "synthetic_freeze": {
            "status": "implemented",
            "acceptance": "Evidence manifest and existing release checks can be regenerated.",
        },
        "local_runtime_audit": {
            "status": "implemented",
            "acceptance": "Missing, unlisted, changed, or unavailable channels fail closed.",
        },
        "noisy_dependent_observations": {
            "status": "completed_local",
            "acceptance": "The next-stage package reports simulation-calibrated coverage, wrong-confident calls, unresolved fractions, and costs under declared noisy/dependent conditions.",
        },
        "external_replication": {
            "status": "pending",
            "acceptance": "Named unaffiliated reviewer returns dated code, logs, and discrepancy report.",
        },
        "crypto_calibration": {
            "status": "pending",
            "acceptance": "Held-out public crypto data validates spread, depth, fills, impact, and regime behavior.",
        },
        "matched_ai_non_ai": {
            "status": "completed_synthetic_null",
            "acceptance": "A matched frozen-neural versus adaptive non-AI comparison ran on paired held-out synthetic tapes; the predeclared AI-specific advantage threshold was not met.",
        },
        "operational_validation": {
            "status": "completed_synthetic_only",
            "acceptance": "A synthetic held-out intervention study reports event rate, gain, and drawdown; external loss shifting and real-market validation remain untested.",
        },
        "novelty_publication": {
            "status": "pending",
            "acceptance": "Independent predecessor, authorship, rights, ethics, and venue reviews are documented.",
        },
    }
