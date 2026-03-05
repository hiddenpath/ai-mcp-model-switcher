# Tests for MCP tool and server regressions
"""
测试MCP工具与服务端关键回归路径。
"""

from __future__ import annotations

import json

import pytest

from spiderswitch.runtime.base import ModelCapabilities, ModelInfo, Runtime
from spiderswitch.server import _redact_sensitive_arguments
from spiderswitch.state import ModelStateManager
from spiderswitch.tools import list as list_tool
from spiderswitch.tools import status as status_tool
from spiderswitch.tools import switch as switch_tool


class _DummyRuntime(Runtime):
    """Minimal runtime for MCP tool path tests."""

    def __init__(self) -> None:
        self.last_filter_provider: str | None = None
        self.last_filter_capability: str | None = None
        self.closed = False

    async def list_models(
        self,
        filter_provider: str | None = None,
        filter_capability: str | None = None,
    ) -> list[ModelInfo]:
        self.last_filter_provider = filter_provider
        self.last_filter_capability = filter_capability
        return [
            ModelInfo(
                id="openai/gpt-4o",
                provider="openai",
                capabilities=ModelCapabilities(streaming=True, tools=True),
            )
        ]

    async def switch_model(
        self,
        model_id: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> ModelInfo:
        _ = api_key, base_url
        return ModelInfo(
            id=model_id,
            provider=model_id.split("/")[0],
            capabilities=ModelCapabilities(streaming=True),
        )

    async def close(self) -> None:
        self.closed = True

    async def get_current_model(self) -> ModelInfo | None:
        return None


def test_redact_sensitive_arguments_masks_secret_like_keys() -> None:
    """Server log redaction should mask common secret markers."""
    redacted = _redact_sensitive_arguments(
        {
            "model": "openai/gpt-4o",
            "api_key": "sk-live-secret",
            "token": "abc",
            "base_url": "https://example.com",
        }
    )
    assert redacted["model"] == "openai/gpt-4o"
    assert redacted["base_url"] == "https://example.com"
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["token"] == "***REDACTED***"


@pytest.mark.asyncio
async def test_list_tool_ignores_non_string_filter_arguments() -> None:
    """list_models tool should pass only validated string filters to runtime."""
    runtime = _DummyRuntime()
    response = await list_tool.handle(
        runtime=runtime,
        arguments={"filter_provider": 123, "filter_capability": ["tools"]},
    )
    assert runtime.last_filter_provider is None
    assert runtime.last_filter_capability is None
    assert len(response) == 1
    payload = json.loads(response[0].text)
    assert payload["status"] == "success"
    first_model = payload["data"]["models"][0]
    assert "api_key_status" in first_model
    assert "proxy_status" in first_model
    assert first_model["api_key_status"]["provider"] == "openai"


@pytest.mark.asyncio
async def test_status_tool_includes_connection_coordination_metadata() -> None:
    """get_status should expose epoch/timestamp fields after a switch."""
    state = ModelStateManager()
    state.update_from_model_info(
        ModelInfo(
            id="openai/gpt-4o",
            provider="openai",
            capabilities=ModelCapabilities(streaming=True),
        )
    )
    result = await status_tool.handle(state)
    payload = json.loads(result[0].text)
    assert payload["status"] == "success"
    assert payload["data"]["connection_epoch"] == 1
    assert payload["data"]["last_switched_at"] is not None


@pytest.mark.asyncio
async def test_switch_tool_missing_model_returns_structured_error() -> None:
    """switch_model should return structured validation error for missing model."""
    runtime = _DummyRuntime()
    state = ModelStateManager()
    result = await switch_tool.handle(runtime=runtime, state_manager=state, arguments={})
    payload = json.loads(result[0].text)
    assert payload["status"] == "error"
    assert payload["error"]["type"] == "InvalidModelError"


@pytest.mark.asyncio
async def test_exit_switcher_resets_runtime_and_state() -> None:
    """exit_switcher should close runtime and reset state."""
    from spiderswitch.tools import reset as reset_tool

    runtime = _DummyRuntime()
    state = ModelStateManager()
    state.update_from_model_info(
        ModelInfo(
            id="openai/gpt-4o",
            provider="openai",
            capabilities=ModelCapabilities(streaming=True),
        )
    )

    result = await reset_tool.handle(runtime=runtime, state_manager=state)
    payload = json.loads(result[0].text)
    assert payload["status"] == "success"
    assert payload["data"]["exited"] is True
    assert payload["data"]["status"]["is_configured"] is False
    assert runtime.closed is True
