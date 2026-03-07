# Tests for MCP tools
"""
测试MCP工具
"""

from __future__ import annotations

from spiderswitch.tools import list, reset, status, switch


class TestSwitchTool:
    """Tests for switch_model tool."""

    def test_tool_schema_structure(self) -> None:
        """Test tool schema has correct structure."""
        schema = switch.tool_schema()
        assert schema.name == "switch_model"
        assert schema.inputSchema is not None
        assert "model" in schema.inputSchema["properties"]
        assert "runtime_id" in schema.inputSchema["properties"]
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
        assert "runtime_id" in schema.inputSchema["properties"]


class TestStatusTool:
    """Tests for get_status tool."""

    def test_tool_schema_structure(self) -> None:
        """Test tool schema has correct structure."""
        schema = status.tool_schema()
        assert schema.name == "get_status"
        assert schema.inputSchema is not None
        assert "runtime_id" in schema.inputSchema["properties"]


class TestResetTool:
    """Tests for exit_switcher tool."""

    def test_tool_schema_structure(self) -> None:
        """Test tool schema has correct structure."""
        schema = reset.tool_schema()
        assert schema.name == "exit_switcher"
        assert schema.inputSchema is not None
        assert "runtime_id" in schema.inputSchema["properties"]
        assert "scope" in schema.inputSchema["properties"]
