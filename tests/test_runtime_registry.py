# Tests for runtime registry/resolver
"""
测试运行时注册表与解析器。
"""

from __future__ import annotations

import pytest

from spiderswitch.errors import ModelSwitcherError
from spiderswitch.runtime.base import ModelCapabilities, ModelInfo, Runtime, RuntimeProfile
from spiderswitch.runtime.registry import RuntimeRegistry, RuntimeResolver


class _RegistryDummyRuntime(Runtime):
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        self.closed = False

    async def list_models(
        self,
        filter_provider: str | None = None,
        filter_capability: str | None = None,
    ) -> list[ModelInfo]:
        _ = filter_provider, filter_capability
        return [
            ModelInfo(
                id="openai/gpt-4o",
                provider="openai",
                capabilities=ModelCapabilities(streaming=True),
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

    async def get_current_model(self) -> ModelInfo | None:
        return None

    async def close(self) -> None:
        self.closed = True

    def describe_runtime_profile(self) -> RuntimeProfile:
        return RuntimeProfile(runtime_id=self._runtime_id, language="python", supports=["model_switching"])


def test_runtime_registry_get_runtime() -> None:
    primary = _RegistryDummyRuntime("python-runtime")
    backup = _RegistryDummyRuntime("rust-runtime")
    registry = RuntimeRegistry(
        runtimes={"python-runtime": primary, "rust-runtime": backup},
        default_runtime_id="python-runtime",
    )
    runtime_id, runtime = registry.get_runtime("rust-runtime")
    assert runtime_id == "rust-runtime"
    assert runtime is backup


def test_runtime_registry_unknown_runtime_raises() -> None:
    registry = RuntimeRegistry(
        runtimes={"python-runtime": _RegistryDummyRuntime("python-runtime")},
        default_runtime_id="python-runtime",
    )
    with pytest.raises(ModelSwitcherError):
        registry.get_runtime("missing-runtime")


def test_runtime_resolver_priority_request_state_default() -> None:
    registry = RuntimeRegistry(
        runtimes={
            "python-runtime": _RegistryDummyRuntime("python-runtime"),
            "rust-runtime": _RegistryDummyRuntime("rust-runtime"),
        },
        default_runtime_id="python-runtime",
    )
    resolver = RuntimeResolver(registry)

    request_first = resolver.resolve("rust-runtime", active_runtime_id="python-runtime")
    assert request_first.runtime_id == "rust-runtime"
    assert request_first.source == "request"

    state_second = resolver.resolve(None, active_runtime_id="rust-runtime")
    assert state_second.runtime_id == "rust-runtime"
    assert state_second.source == "state"

    default_last = resolver.resolve(None, active_runtime_id=None)
    assert default_last.runtime_id == "python-runtime"
    assert default_last.source == "default"
