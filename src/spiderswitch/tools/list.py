# spiderswitch list_models tool
"""
MCP tool for listing available models.
MCP工具：列出可用模型。

Provides structured error responses and proper logging.
提供结构化的错误响应和适当的日志记录。
"""

from __future__ import annotations

import logging

from mcp.types import TextContent, Tool

from ..errors import ModelSwitcherError
from ..response import MCPResponse
from ..runtime.base import Runtime
from ..runtime.python_runtime import format_model_info
from ..validation import get_provider_api_key_status, get_provider_proxy_status

logger = logging.getLogger(__name__)


def tool_schema() -> Tool:
    """Get the list_models tool schema.

    Returns:
        Tool schema definition
    """
    return Tool(
        name="list_models",
        description=(
            "List all available models from registered providers in ai-protocol manifests. "
            "列出ai-protocol manifests中所有已注册provider的可用模型。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "filter_provider": {
                    "type": "string",
                    "description": (
                        "Optional filter by provider (e.g., 'openai', 'anthropic'). "
                        "可选，按provider过滤（如 'openai', 'anthropic'）"
                    ),
                },
                "filter_capability": {
                    "type": "string",
                    "enum": ["streaming", "tools", "vision", "embeddings", "audio"],
                    "description": ("Optional filter by capability. 可选，按能力过滤"),
                },
                "require_api_key": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "If true, only return models from providers with configured API keys. "
                        "如果为 true，只返回已配置 API Key 的 provider 的模型"
                    ),
                },
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
    runtime: Runtime,
    arguments: dict[str, object],
) -> list[TextContent]:
    """Handle list_models tool call.

    Args:
        runtime: Runtime implementation (e.g., PythonRuntime)
        arguments: Tool arguments from MCP request

    Returns:
        List of TextContent with model list
    """
    try:
        filter_provider_raw = arguments.get("filter_provider")
        filter_capability_raw = arguments.get("filter_capability")
        require_api_key_raw = arguments.get("require_api_key")
        filter_provider = filter_provider_raw if isinstance(filter_provider_raw, str) else None
        filter_capability = (
            filter_capability_raw if isinstance(filter_capability_raw, str) else None
        )
        require_api_key = (
            require_api_key_raw if isinstance(require_api_key_raw, bool) else False
        )

        logger.info(
            f"Listing models: filter_provider={filter_provider}, "
            f"filter_capability={filter_capability}, "
            f"require_api_key={require_api_key}"
        )

        # Get models from runtime
        models = await runtime.list_models(
            filter_provider=filter_provider,
            filter_capability=filter_capability,
        )

        # Format response with success status
        provider_status_cache: dict[str, dict[str, object]] = {}
        provider_proxy_cache: dict[str, dict[str, object]] = {}
        model_entries: list[dict[str, object]] = []
        for model in models:
            provider = model.provider
            if provider not in provider_status_cache:
                provider_status_cache[provider] = get_provider_api_key_status(provider)
            if provider not in provider_proxy_cache:
                provider_proxy_cache[provider] = get_provider_proxy_status(provider)

            # Filter out models from providers without API keys if required
            if require_api_key:
                api_key_status = provider_status_cache[provider]
                if not api_key_status.get("has_api_key", False):
                    logger.debug(
                        f"Skipping model {model.id} from provider {provider}: "
                        "no API key configured"
                    )
                    continue

            model_entries.append(
                {
                    **format_model_info(model),
                    "api_key_status": provider_status_cache[provider],
                    "proxy_status": provider_proxy_cache[provider],
                }
            )

        response = MCPResponse.success(
            data={
                "count": len(model_entries),
                "models": model_entries,
                "runtime_profile": runtime.describe_runtime_profile().to_dict(),
                "filtered": {
                    "require_api_key": require_api_key,
                    "provider": filter_provider,
                    "capability": filter_capability,
                },
            },
        )

        return [response.to_text_content()]

    except ModelSwitcherError as e:
        logger.error(f"Failed to list models: {e}")
        response = MCPResponse.error(
            message=str(e),
            error_type=e.__class__.__name__,
            details=e.details if hasattr(e, "details") else None,
        )
        return [response.to_text_content()]

    except Exception as e:
        logger.exception(f"Unexpected error in list_models: {e}")
        response = MCPResponse.error(
            message=f"Internal error: {e}",
            error_type="RuntimeError",
        )
        return [response.to_text_content()]


__all__ = ["tool_schema", "handle"]
