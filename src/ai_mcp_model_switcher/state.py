# ai-mcp-model-switcher state management
"""
State management for the MCP model switcher.
管理MCP模型切换器的状态。
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any
from dataclasses import dataclass
from typing import Any

from .runtime.base import ModelInfo

logger = logging.getLogger(__name__)


@dataclass
class ModelState:
    """Current model state."""

    provider: str | None = None
    model: str | None = None
    capabilities: list[str] | None = None
    is_configured: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for MCP response."""
        return {
            "provider": self.provider,
            "model": self.model,
            "capabilities": self.capabilities or [],
            "is_configured": self.is_configured,
        }


class ModelStateManager:
    """Manages the current model selection and state.

    Thread-safe state management for the MCP server.
    Uses threading.Lock for concurrent access protection.
    线程安全的状态管理，使用 threading.Lock 保护并发访问。
    """

    def __init__(self) -> None:
        """Initialize the state manager with a lock."""
        self._state = ModelState()
        self._lock = threading.Lock()
    """Manages the current model selection and state.

    Thread-safe state management for the MCP server.
    """

    def __init__(self) -> None:
        """Initialize the state manager."""
        self._state = ModelState()

    def update_from_model_info(self, info: ModelInfo) -> ModelState:
        """Update state from ModelInfo.

        Args:
            info: ModelInfo object to update state from

        Returns:
            Updated ModelState
        """
        with self._lock:
            parts = info.id.split("/")
            provider = parts[0] if parts else None
            model_name = parts[1] if len(parts) > 1 else None

            self._state = ModelState(
                provider=provider,
                model=model_name,
                capabilities=info.capabilities.to_list(),
                is_configured=True,
            )

            logger.info(
                f"State updated: provider={provider}, model={model_name}, "
                f"capabilities={self._state.capabilities}"
            )

            return self._state
        """Update state from ModelInfo."""
        parts = info.id.split("/")
        provider = parts[0] if parts else None
        model_name = parts[1] if len(parts) > 1 else None

        self._state = ModelState(
            provider=provider,
            model=model_name,
            capabilities=info.capabilities.to_list(),
            is_configured=True,
        )

        logger.info(
            f"State updated: provider={provider}, model={model_name}, "
            f"capabilities={self._state.capabilities}"
        )

        return self._state

    def get_state(self) -> ModelState:
        """Get current state.

        Returns:
            Current ModelState (thread-safe copy)
        """
        with self._lock:
            # Return a copy to avoid external modification
            return ModelState(
                provider=self._state.provider,
                model=self._state.model,
                capabilities=self._state.capabilities,
                is_configured=self._state.is_configured,
            )
        """Get current state."""
        return self._state

    def reset(self) -> None:
        """Reset state to uninitialized."""
        with self._lock:
            self._state = ModelState()
        logger.info("State reset")
        """Reset state to uninitialized."""
        self._state = ModelState()
        logger.info("State reset")


__all__ = ["ModelState", "ModelStateManager"]
