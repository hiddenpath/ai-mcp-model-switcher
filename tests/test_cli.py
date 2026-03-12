# Tests for CLI onboarding commands
"""
Test spiderswitch CLI commands for plugin-market onboarding flows.
测试 spiderswitch CLI 在插件市场场景下的 init/doctor 行为。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spiderswitch.cli import run_doctor_checks, write_init_config


def test_write_init_config_generates_cursor_template(tmp_path: Path) -> None:
    """init config writer should produce cursor-compatible schema."""
    target = tmp_path / "mcp.json"
    write_init_config(
        output=target,
        client="cursor",
        ai_protocol_path="/tmp/ai-protocol",
        force=False,
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert "mcpServers" in payload
    assert "spiderswitch" in payload["mcpServers"]
    server = payload["mcpServers"]["spiderswitch"]
    assert server["command"] == "spiderswitch"
    assert server["args"] == ["serve"]


def test_write_init_config_respects_force_flag(tmp_path: Path) -> None:
    """init config writer should block overwrite unless force=true."""
    target = tmp_path / "mcp.json"
    target.write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_init_config(
            output=target,
            client="cursor",
            ai_protocol_path=None,
            force=False,
        )


def test_doctor_reports_unsupported_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """doctor should mark unsupported proxy scheme as unhealthy."""
    monkeypatch.setenv("ALL_PROXY", "socks4://127.0.0.1:9999")
    result = run_doctor_checks(include_runtime_probe=False)
    check_map = {item["name"]: item for item in result["checks"]}
    assert check_map["proxy_scheme"]["ok"] is False
    assert result["healthy"] is False


def test_doctor_skips_runtime_probe_when_disabled() -> None:
    """doctor should not include runtime probe when explicitly disabled."""
    result = run_doctor_checks(include_runtime_probe=False)
    names = [item["name"] for item in result["checks"]]
    assert "runtime_probe" not in names
