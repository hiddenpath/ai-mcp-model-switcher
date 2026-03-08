# Tests for runtime abstraction layer
"""
测试运行时抽象层
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from spiderswitch.runtime.base import ModelCapabilities, ModelInfo
from spiderswitch.runtime.registry import RuntimeRegistry, RuntimeResolver
from spiderswitch.runtime.python_runtime import PythonRuntime
from spiderswitch.state import ModelStateManager


class TestModelCapabilities:
    """Tests for ModelCapabilities."""

    def test_default_capabilities(self) -> None:
        """Test default capabilities are all False."""
        caps = ModelCapabilities()
        assert caps.streaming is False
        assert caps.tools is False
        assert caps.vision is False
        assert caps.embeddings is False
        assert caps.audio is False

    def test_to_list_empty(self) -> None:
        """Test to_list returns empty list when no capabilities."""
        caps = ModelCapabilities()
        assert caps.to_list() == []

    def test_to_list_with_capabilities(self) -> None:
        """Test to_list includes enabled capabilities."""
        caps = ModelCapabilities(
            streaming=True,
            tools=True,
            vision=True,
            embeddings=False,
            audio=False,
        )
        result = caps.to_list()
        assert "streaming" in result
        assert "tools" in result
        assert "vision" in result
        assert "embeddings" not in result
        assert "audio" not in result


class TestModelInfo:
    """Tests for ModelInfo."""

    def test_model_info_creation(self) -> None:
        """Test ModelInfo can be created."""
        caps = ModelCapabilities(streaming=True, tools=True)
        info = ModelInfo(
            id="openai/gpt-4o",
            provider="openai",
            capabilities=caps,
        )
        assert info.id == "openai/gpt-4o"
        assert info.provider == "openai"
        assert info.capabilities.streaming is True
        assert info.capabilities.tools is True


def test_runtime_profile_exposes_routing_capability_signal() -> None:
    """Runtime should expose capability signals, not strategy policy."""
    runtime = PythonRuntime()
    profile = runtime.describe_runtime_profile()
    assert profile.runtime_id == "python-runtime"
    assert profile.language == "python"
    assert "model_switching" in profile.supports
    assert "provider_manifest_loading" in profile.supports
    assert "streaming_chat" in profile.model_capabilities
    assert "runtime_switch_execution" in profile.runtime_capabilities
    assert "go-runtime" in profile.reserved_runtimes
    assert profile.notes is not None


def test_runtime_auto_sets_ai_protocol_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Runtime should set AI_PROTOCOL_PATH when auto-discovering local protocol path."""
    protocol_root = tmp_path / "ai-protocol"
    model_dir = protocol_root / "v1" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "openai.yaml").write_text(
        yaml.safe_dump(
            {
                "models": {
                    "gpt-4o": {
                        "provider": "openai",
                        "model_id": "gpt-4o",
                        "capabilities": ["streaming", "tools"],
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SPIDERSWITCH_SYNC_DIST", "0")
    monkeypatch.delenv("AI_PROTOCOL_PATH", raising=False)
    monkeypatch.delenv("AI_PROTOCOL_DIR", raising=False)

    runtime = PythonRuntime(ai_protocol_path=str(protocol_root))
    runtime._ensure_initialized()  # noqa: SLF001

    assert os.getenv("AI_PROTOCOL_PATH") == str(protocol_root)


@pytest.mark.asyncio
async def test_runtime_normalizes_public_id_and_runtime_model_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Runtime should expose switchable IDs while using provider-qualified runtime IDs."""
    protocol_root = tmp_path / "ai-protocol"
    model_dir = protocol_root / "v1" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "nvidia.yaml").write_text(
        yaml.safe_dump(
            {
                "models": {
                    "deepseek-ai/deepseek-r1": {
                        "provider": "nvidia",
                        "model_id": "deepseek-ai/deepseek-r1",
                        "capabilities": ["streaming", "tools"],
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SPIDERSWITCH_SYNC_DIST", "0")
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test")

    runtime = PythonRuntime(ai_protocol_path=str(protocol_root))
    models = await runtime.list_models(filter_provider="nvidia")
    assert len(models) == 1
    assert models[0].id == "nvidia/deepseek-r1"
    assert models[0].runtime_model_id == "nvidia/deepseek-ai/deepseek-r1"

    captured: dict[str, object] = {}

    async def fake_create(*_: object, **kwargs: object) -> object:
        captured.update(kwargs)

        class _DummyClient:
            async def close(self) -> None:
                return None

        return _DummyClient()

    monkeypatch.setattr(
        "spiderswitch.runtime.python_runtime.AiClient.create",
        fake_create,
    )

    await runtime.switch_model("nvidia/deepseek-r1")
    assert captured["model"] == "nvidia/deepseek-ai/deepseek-r1"


@pytest.mark.asyncio
async def test_runtime_temporarily_unsets_unsupported_socks4_proxy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Unsupported socks4 proxy vars should not break ai-lib client creation."""
    protocol_root = tmp_path / "ai-protocol"
    model_dir = protocol_root / "v1" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "openai.yaml").write_text(
        yaml.safe_dump(
            {
                "models": {
                    "gpt-4o": {
                        "provider": "openai",
                        "model_id": "gpt-4o",
                        "capabilities": ["streaming", "tools"],
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SPIDERSWITCH_SYNC_DIST", "0")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ALL_PROXY", "socks4://127.0.0.1:9999")

    runtime = PythonRuntime(ai_protocol_path=str(protocol_root))
    observed_proxy_during_create: str | None = None

    async def fake_create(*_: object, **__: object) -> object:
        nonlocal observed_proxy_during_create
        observed_proxy_during_create = os.getenv("ALL_PROXY")

        class _DummyClient:
            async def close(self) -> None:
                return None

        return _DummyClient()

    monkeypatch.setattr(
        "spiderswitch.runtime.python_runtime.AiClient.create",
        fake_create,
    )

    await runtime.switch_model("openai/gpt-4o")
    assert observed_proxy_during_create is None
    assert os.getenv("ALL_PROXY") == "socks4://127.0.0.1:9999"


@pytest.mark.asyncio
async def test_runtime_resolver_is_deterministic() -> None:
    """Resolver must follow request -> state -> default order."""
    python_runtime = PythonRuntime()
    rust_runtime = PythonRuntime()
    ts_runtime = PythonRuntime()
    runtimes = {
        "python-runtime": python_runtime,
        "rust-runtime": rust_runtime,
        "ts-runtime": ts_runtime,
    }
    registry = RuntimeRegistry(runtimes=runtimes, default_runtime_id="python-runtime")
    resolver = RuntimeResolver(registry)

    r1 = resolver.resolve(requested_runtime_id="ts-runtime", active_runtime_id="rust-runtime")
    assert r1.runtime_id == "ts-runtime"
    assert r1.source == "request"

    r2 = resolver.resolve(requested_runtime_id=None, active_runtime_id="rust-runtime")
    assert r2.runtime_id == "rust-runtime"
    assert r2.source == "state"

    r3 = resolver.resolve(requested_runtime_id=None, active_runtime_id=None)
    assert r3.runtime_id == "python-runtime"
    assert r3.source == "default"

    await registry.close_all()


def test_state_manager_scoped_reset_keeps_other_runtime_epochs() -> None:
    """Runtime-scoped reset must only clear target runtime state."""
    manager = ModelStateManager()
    model_info = ModelInfo(
        id="openai/gpt-4o",
        provider="openai",
        capabilities=ModelCapabilities(streaming=True, tools=True),
    )
    manager.update_from_model_info_with_runtime(model_info, runtime_id="python-runtime")
    manager.update_from_model_info_with_runtime(model_info, runtime_id="rust-runtime")

    before = manager.get_state().to_dict()
    assert before["runtime_epochs"]["python-runtime"] == 1
    assert before["runtime_epochs"]["rust-runtime"] == 1

    manager.reset(runtime_id="python-runtime")
    after = manager.get_state().to_dict()
    assert "python-runtime" not in after["runtime_epochs"]
    assert after["runtime_epochs"]["rust-runtime"] == 1


def test_runtime_profile_fixtures_cover_tri_runtime_contract() -> None:
    """Fixture snapshots must include python/rust/ts runtime profiles."""
    fixture = Path(__file__).parent / "fixtures" / "runtime_profiles.yaml"
    data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    profiles = data.get("profiles", [])
    ids = {p.get("runtime_id") for p in profiles}
    assert {"python-runtime", "rust-runtime", "ts-runtime"}.issubset(ids)
    for profile in profiles:
        assert profile.get("language")
        assert isinstance(profile.get("supports"), list)
        assert "runtime_switch_execution" in profile.get("runtime_capabilities", [])
