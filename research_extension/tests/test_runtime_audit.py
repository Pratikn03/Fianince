import json
from pathlib import Path

import pytest

from research_extension.runtime_audit import (
    AuditTrace,
    build_manifest,
    validate_trace,
)


def test_complete_trace_is_eligible(tmp_path: Path):
    source = tmp_path / "model.py"
    source.write_text("state = 1\n", encoding="utf-8")
    manifest = build_manifest(source, {"reset": "zero", "execution": "linear"})
    trace = AuditTrace(manifest)
    trace.record(0, "memory", 0.2)
    trace.record(0, "inventory", 0.0)
    trace.record(0, "funding", 1.0)
    trace.record(0, "execution", "filled")
    trace.record(0, "reset", "zero")
    result = validate_trace(trace)
    assert result["eligible"] is True
    assert result["reasons"] == []


def test_missing_channel_fails_closed(tmp_path: Path):
    source = tmp_path / "model.py"
    source.write_text("state = 1\n", encoding="utf-8")
    manifest = build_manifest(source, {"reset": "zero", "execution": "linear"})
    trace = AuditTrace(manifest)
    for channel in ("memory", "inventory", "funding", "execution", "reset"):
        if channel != "funding":
            trace.record(0, channel, "present")
    result = validate_trace(trace)
    assert result["eligible"] is False
    assert "missing channel: funding" in result["reasons"]


def test_manifest_change_fails_closed(tmp_path: Path):
    source = tmp_path / "model.py"
    source.write_text("state = 1\n", encoding="utf-8")
    manifest = build_manifest(source, {"reset": "zero", "execution": "linear"})
    source.write_text("state = 2\n", encoding="utf-8")
    trace = AuditTrace(manifest)
    for channel in ("memory", "inventory", "funding", "execution", "reset"):
        trace.record(0, channel, "present")
    result = validate_trace(trace)
    assert result["eligible"] is False
    assert "source digest mismatch" in result["reasons"]


def test_unlisted_channel_fails_closed(tmp_path: Path):
    source = tmp_path / "model.py"
    source.write_text("state = 1\n", encoding="utf-8")
    manifest = build_manifest(source, {"reset": "zero", "execution": "linear"})
    trace = AuditTrace(manifest)
    for channel in ("memory", "inventory", "funding", "execution", "reset", "hidden_slow_state"):
        trace.record(0, channel, "present")
    result = validate_trace(trace)
    assert result["eligible"] is False
    assert "unlisted channel: hidden_slow_state" in result["reasons"]
