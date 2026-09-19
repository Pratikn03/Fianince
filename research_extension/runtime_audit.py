"""Fail-closed runtime boundary audit for model-conditioned claims."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
from typing import Any


REQUIRED_CHANNELS = frozenset({"memory", "inventory", "funding", "execution", "reset"})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_manifest(source_path: Path, configuration: dict[str, Any]) -> dict[str, Any]:
    """Create a machine-readable declaration of the audited runtime boundary."""
    source_path = Path(source_path).resolve()
    return {
        "schema": "mm-runtime-audit-1",
        "source_path": str(source_path),
        "source_sha256": _sha256(source_path),
        "configuration": dict(configuration),
        "declared_channels": sorted(REQUIRED_CHANNELS),
    }


@dataclass
class AuditTrace:
    manifest: dict[str, Any]
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, step: int, channel: str, value: Any) -> None:
        if not isinstance(step, int) or step < 0:
            raise ValueError("step must be a nonnegative integer")
        self.events.append({"step": step, "channel": str(channel), "value": value})


def validate_trace(trace: AuditTrace) -> dict[str, Any]:
    """Validate completeness and current source identity; reject uncertainty."""
    reasons: list[str] = []
    manifest = trace.manifest
    if manifest.get("schema") != "mm-runtime-audit-1":
        reasons.append("schema mismatch")
    source_path = Path(str(manifest.get("source_path", "")))
    if not source_path.is_file():
        reasons.append("source file unavailable")
    elif _sha256(source_path) != manifest.get("source_sha256"):
        reasons.append("source digest mismatch")

    declared = set(manifest.get("declared_channels", []))
    missing_declared = REQUIRED_CHANNELS - declared
    reasons.extend(f"missing declaration: {name}" for name in sorted(missing_declared))
    observed = {event.get("channel") for event in trace.events}
    reasons.extend(f"missing channel: {name}" for name in sorted(REQUIRED_CHANNELS - observed))
    reasons.extend(
        f"unlisted channel: {name}" for name in sorted(observed - declared)
        if name is not None
    )
    return {
        "eligible": not reasons,
        "reasons": reasons,
        "source_sha256": manifest.get("source_sha256"),
        "observed_channels": sorted(str(name) for name in observed if name is not None),
        "event_count": len(trace.events),
    }

