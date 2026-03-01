# ai-mcp-model-switcher base runtime interface
"""
Base runtime abstraction for different ai-lib implementations.
运行时抽象基类，定义统一的模型交互接口。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ModelCapabilities:
    """Capabilities supported by a model.
    
    Uses a capability mapping table for efficient to_list() conversion.
    使用能力映射表实现高效的 to_list() 转换。
    """

    streaming: bool = False
    tools: bool = False
    vision: bool = False
    embeddings: bool = False
    audio: bool = False

    # Capability name to attribute mapping for efficient conversion
    # 能力名称到属性的映射，用于高效转换
    _CAPABILITY_MAP: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize the capability mapping table."""
        if self._CAPABILITY_MAP is None:
            # Use object.__setattr__ to work with frozen dataclass
            object.__setattr__(
                self,
                "_CAPABILITY_MAP",
                {
                    "streaming": "streaming",
                    "tools": "tools",
                    "vision": "vision",
                    "embeddings": "embeddings",
                    "audio": "audio",
                },
            )

    def to_list(self) -> list[str]:
        """Convert capabilities to list representation.
        
        Uses the capability mapping table for efficient conversion.
        Returns only capabilities that are enabled.
        使用能力映射表进行高效转换，只返回已启用的能力。

        Returns:
            List of enabled capability names
        """
        if self._CAPABILITY_MAP is None:
            self.__post_init__()

        return [
            name
            for name, attr in self._CAPABILITY_MAP.items()  # type: ignore
            if getattr(self, attr, False)
        ]
class ModelCapabilities:
    """Capabilities supported by a model."""

    streaming: bool = False
    tools: bool = False
    vision: bool = False
    embeddings: bool = False
    audio: bool = False

    def to_list(self) -> list[str]:
        """Convert capabilities to list representation."""
        caps = []
        if self.streaming:
            caps.append("streaming")
        if self.tools:
            caps.append("tools")
        if self.vision:
            caps.append("vision")
        if self.embeddings:
            caps.append("embeddings")
        if self.audio:
            caps.append("audio")
        return caps


@dataclass
class ModelInfo:
    """Information about available models."""

    id: str
    provider: str
    capabilities: ModelCapabilities


class Runtime(ABC):
    """Abstract base class for ai-lib runtime implementations."""

    @abstractmethod
    async def list_models(
        self,
        filter_provider: str | None = None,
        filter_capability: str | None = None,
    ) -> list[ModelInfo]:
        """List available models.

        Args:
            filter_provider: Optional provider ID to filter by
            filter_capability: Optional capability to filter by

        Returns:
            List of ModelInfo objects
        """

    @abstractmethod
    async def switch_model(
        self,
        model_id: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> ModelInfo:
        """Switch to a specific model.

        Args:
            model_id: Model identifier (e.g., "openai/gpt-4o")
            api_key: Optional explicit API key
            base_url: Optional custom base URL

        Returns:
            ModelInfo for the switched model

        Raises:
            RuntimeError: If model switching fails
        """

    @abstractmethod
    async def get_current_model(self) -> ModelInfo | None:
        """Get information about the currently active model.

        Returns:
            ModelInfo if a model is configured, None otherwise
        """

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources."""
