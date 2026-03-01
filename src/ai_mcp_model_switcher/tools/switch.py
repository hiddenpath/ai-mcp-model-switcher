# ai-mcp-model-switcher switch_model tool
"""
MCP tool for switching AI models.
MCP工具：切换AI模型。

Provides structured error responses and proper logging.
提供结构化的错误响应和适当的日志记录。
"""

from __future__ import annotations

import logging

from ..errors import InvalidModelError, ModelSwitcherError
from ..response import MCPResponse
from mcp.types import TextContent, Tool
from ..runtime.python_runtime import (
    extract_model_from_args,
    format_model_info,
)


logger = logging.getLogger(__name__)


def tool_schema() -> Tool:
    """Get the switch_model tool schema.
    
    Returns:
        Tool schema definition
    """
    return Tool(
        name="switch_model",
        description=(
            "Switch to a different AI model/provider. "
            "Requires provider API key configured in environment or passed explicitly. "
            "切换到不同的AI模型/provider。需要在环境变量中配置provider API密钥或显式传递。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": (
                        "Model identifier (e.g., 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet'). "
                        "模型标识符（如 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet'）"
                    ),
                    "pattern": "^[a-z0-9-]+/[a-z0-9-.]+$",
                },
                "api_key": {
                    "type": "string",
                    "description": (
                        "Optional explicit API key (overrides environment variable). "
                        "可选的显式API密钥（覆盖环境变量）"
                    ),
                },
                "base_url": {
                    "type": "string",
                    "description": (
                        "Optional custom base URL for testing/mock. "
                        "可选的自定义基础URL，用于测试/mock"
                    ),
                },
            },
            "required": ["model"],
        },
    )


async def handle(
    runtime: object,
    state_manager: object,
    arguments: dict[str, object],
) -> list[TextContent]:
    """Handle switch_model tool call.

    Args:
        runtime: Runtime implementation (e.g., PythonRuntime)
        state_manager: State manager instance
        arguments: Tool arguments from MCP request

    Returns:
        List of TextContent with result
    """
    try:
        model_id, api_key, base_url = extract_model_from_args(arguments)
        logger.info(f"Switching to model: {model_id}")

        # Switch model via runtime
        model_info = await runtime.switch_model(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
        )

        # Update state
        state_manager.update_from_model_info(model_info)

        # Format response with success status
        response = MCPResponse.success(
            data={
                **format_model_info(model_info),
            },
            message=f"Successfully switched to {model_info.provider}/{model_info.id.split('/')[1] if '/' in model_info.id else model_info.id}",
        )

        return [response.to_text_content()]

    except InvalidModelError as e:
        # Client error - invalid input
        logger.warning(f"Invalid argument: {e}")
        response = MCPResponse.error(
            message=str(e),
            error_type="InvalidModelError",
            details=e.details if hasattr(e, 'details') else None,
        )
        return [response.to_text_content()]

    except ModelSwitcherError as e:
        # Server error - switch failed
        logger.error(f"Failed to switch model: {e}")
        response = MCPResponse.error(
            message=str(e),
            error_type=e.__class__.__name__,
            details=e.details if hasattr(e, 'details') else None,
        )
        return [response.to_text_content()]

    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error in switch_model: {e}")
        response = MCPResponse.error(
            message=f"Internal error: {e}",
            error_type="RuntimeError",
        )
        return [response.to_text_content()]


__all__ = ["tool_schema", "handle"]
