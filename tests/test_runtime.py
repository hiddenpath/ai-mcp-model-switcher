# Tests for runtime abstraction layer
"""
测试运行时抽象层
"""

from __future__ import annotations

import pytest

from ai_mcp_model_switcher.runtime.base import ModelCapabilities, ModelInfo


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
