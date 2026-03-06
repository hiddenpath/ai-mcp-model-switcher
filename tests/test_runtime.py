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
from spiderswitch.runtime.python_runtime import PythonRuntime


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
