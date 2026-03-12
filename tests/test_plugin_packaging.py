# Tests for plugin-market packaging assets
"""
Validate plugin-market manifest and packaging scripts baseline.
校验插件市场 manifest 与打包脚本基础可用性。
"""

from __future__ import annotations

import json
from pathlib import Path


def test_plugin_manifest_has_required_fields() -> None:
    """manifest should include required plugin-market metadata fields."""
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "packaging" / "plugin-market" / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    required_fields = [
        "id",
        "name",
        "version",
        "entrypoint",
        "install",
        "healthcheck",
        "configuration",
    ]
    for field in required_fields:
        assert field in payload

    assert payload["entrypoint"]["command"] == "spiderswitch"
    assert "script" in payload["install"]
