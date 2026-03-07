# spiderswitch get_status tool
"""
MCP tool for getting current model status.
MCP工具：获取当前模型状态。

Provides structured error responses and proper logging.
提供结构化的错误响应和适当的日志记录。
"""

from __future__ import annotations

import logging

from mcp.types import TextContent, Tool

from ..errors import ModelSwitcherError
from ..response import MCPResponse
from ..runtime.base import Runtime
from ..state import ModelStateManager

logger = logging.getLogger(__name__)


def tool_schema() -> Tool:
    """Get the get_status tool schema.

    Returns:
        Tool schema definition
    """
    return Tool(
        name="get_status",
        description=(
            "Get current model status and configuration (runtime-aware). "
            "获取当前模型状态和配置（支持运行时维度）。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "runtime_id": {
                    "type": "string",
                    "description": (
                        "Optional runtime id selected by upper-layer strategy. "
                        "可选，上层策略选择的运行时 ID。"
                    ),
                },
            },
        },
    )


async def handle(
    state_manager: ModelStateManager,
    runtime: Runtime,
) -> list[TextContent]:
    """Handle get_status tool call.

    Args:
        state_manager: State manager instance

    Returns:
        List of TextContent with status
    """
    try:
        state = state_manager.get_state()
        result = state.to_dict()
        result["runtime_profile"] = runtime.describe_runtime_profile().to_dict()

        response = MCPResponse.success(data=result)

        return [response.to_text_content()]

    except ModelSwitcherError as e:
        logger.error(f"Failed to get status: {e}")
        response = MCPResponse.error(
            message=str(e),
            error_type=e.__class__.__name__,
            details=e.details if hasattr(e, "details") else None,
        )
        return [response.to_text_content()]

    except Exception as e:
        logger.exception(f"Unexpected error in get_status: {e}")
        response = MCPResponse.error(
            message=f"Internal error: {e}",
            error_type="RuntimeError",
        )
        return [response.to_text_content()]


__all__ = ["tool_schema", "handle"]
