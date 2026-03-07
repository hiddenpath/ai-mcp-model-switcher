# spiderswitch exit/reset tool
"""
MCP tool for explicitly exiting spiderswitch model switching mode.
MCP工具：显式退出 spiderswitch 模型切换模式。
"""

from __future__ import annotations

import logging

from mcp.types import TextContent, Tool

from ..response import MCPResponse
from ..runtime.base import Runtime
from ..state import ModelStateManager

logger = logging.getLogger(__name__)


def tool_schema() -> Tool:
    """Get the exit_switcher tool schema."""
    return Tool(
        name="exit_switcher",
        description=(
            "Reset spiderswitch runtime/session state and exit model switching mode. "
            "重置 spiderswitch 运行时与会话状态，退出模型切换模式。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "runtime_id": {
                    "type": "string",
                    "description": (
                        "Optional runtime id to reset. 可选，仅重置指定 runtime。"
                    ),
                },
                "scope": {
                    "type": "string",
                    "enum": ["all", "runtime"],
                    "default": "all",
                    "description": (
                        "Reset scope. 'all' resets global state; "
                        "'runtime' resets only target runtime scope. "
                        "重置作用域：all=全局，runtime=单运行时。"
                    ),
                },
            },
        },
    )


async def handle(
    runtime: Runtime,
    state_manager: ModelStateManager,
    runtime_id: str | None = None,
    scope: str = "all",
) -> list[TextContent]:
    """Handle exit_switcher tool call."""
    try:
        await runtime.close()
        if scope == "runtime":
            state_manager.reset(runtime_id=runtime_id)
        else:
            state_manager.reset()
        response = MCPResponse.success(
            data={
                "exited": True,
                "scope": scope,
                "runtime_id": runtime_id,
                "status": state_manager.get_state().to_dict(),
            },
            message=(
                "spiderswitch state has been reset. "
                "Cursor built-in model selection is unaffected."
            ),
        )
        return [response.to_text_content()]
    except Exception as e:
        logger.exception("Failed to exit spiderswitch mode: %s", e)
        response = MCPResponse.error(
            message=f"Failed to exit switcher mode: {e}",
            error_type="RuntimeError",
        )
        return [response.to_text_content()]


__all__ = ["tool_schema", "handle"]
