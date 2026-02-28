# Tests for MCP tools
"""
测试MCP工具
"""

from __future__ import annotations

import pytest

from ai_mcp_model_switcher.tools import list, status, switch


class TestSwitchTool:
    """Tests for switch_model tool."""

    def test_tool_schema_structure(self) -> None:
        """Test tool schema has correct structure."""
        schema = switch.tool_schema()
        assert schema.name == "switch_model"
        assert schema.inputSchema is not None
        assert "model" in schema.inputSchema["properties"]
        assert schema.inputSchema["properties"]["model"]["type"] == "string"


class TestListTool:
    """Tests for list_models tool."""

    def test_tool_schema_structure(self) -> None:
        """Test tool schema has correct structure."""
        schema = list.tool_schema()
        assert schema.name == "list_models"
        assert schema.inputSchema is not None
        assert "filter_provider" in schema.inputSchema["properties"]
        assert "filter_capability" in schema.inputSchema["properties"]


class TestStatusTool:
    """Tests for get_status tool."""

    def test_tool_schema_structure(self) -> None:
        """Test tool schema has correct structure."""
        schema = status.tool_schema()
        assert schema.name == "get_status"
        assert schema.inputSchema is not None
        assert schema.inputSchema["properties"] == {}
