# spiderswitch state management
"""
State management for the MCP model switcher.
管理MCP模型切换器的状态。
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .runtime.base import ModelInfo

logger = logging.getLogger(__name__)


@dataclass
class ModelState:
    """Current model state."""

    provider: str | None = None
    model: str | None = None
    capabilities: list[str] | None = None
    runtime_id: str | None = None
    runtime_epoch: int = 0
    runtime_epochs: dict[str, int] | None = None
    is_configured: bool = False
    connection_epoch: int = 0
    last_switched_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for MCP response."""
        return {
            "provider": self.provider,
            "model": self.model,
            "capabilities": self.capabilities or [],
            "runtime_id": self.runtime_id,
            "runtime_epoch": self.runtime_epoch,
            "runtime_epochs": self.runtime_epochs or {},
            "is_configured": self.is_configured,
            "connection_epoch": self.connection_epoch,
            "last_switched_at": self.last_switched_at,
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

    def update_from_model_info(self, info: ModelInfo) -> ModelState:
        """Update state from ModelInfo.

        Args:
            info: ModelInfo object to update state from

        Returns:
            Updated ModelState
        """
        return self.update_from_model_info_with_runtime(info, runtime_id="python-runtime")

    def update_from_model_info_with_runtime(
        self,
        info: ModelInfo,
        runtime_id: str,
    ) -> ModelState:
        """Update state from ModelInfo with runtime dimension."""
        with self._lock:
            parts = info.id.split("/")
            provider = parts[0] if parts else None
            model_name = parts[1] if len(parts) > 1 else None
            current_epoch = self._state.connection_epoch
            runtime_epochs = dict(self._state.runtime_epochs or {})
            next_runtime_epoch = runtime_epochs.get(runtime_id, 0) + 1
            runtime_epochs[runtime_id] = next_runtime_epoch

            self._state = ModelState(
                provider=provider,
                model=model_name,
                capabilities=info.capabilities.to_list(),
                runtime_id=runtime_id,
                runtime_epoch=next_runtime_epoch,
                runtime_epochs=runtime_epochs,
                is_configured=True,
                connection_epoch=current_epoch + 1,
                last_switched_at=datetime.now(timezone.utc).isoformat(),
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
                capabilities=list(self._state.capabilities) if self._state.capabilities else None,
                runtime_id=self._state.runtime_id,
                runtime_epoch=self._state.runtime_epoch,
                runtime_epochs=dict(self._state.runtime_epochs or {}),
                is_configured=self._state.is_configured,
                connection_epoch=self._state.connection_epoch,
                last_switched_at=self._state.last_switched_at,
            )

    def reset(self, runtime_id: str | None = None) -> None:
        """Reset state to uninitialized.

        runtime_id=None resets all runtime scopes.
        runtime_id='x' resets only runtime x scope.
        """
        with self._lock:
            if runtime_id is None:
                self._state = ModelState(connection_epoch=self._state.connection_epoch + 1)
            else:
                runtime_epochs = dict(self._state.runtime_epochs or {})
                runtime_epochs.pop(runtime_id, None)
                if self._state.runtime_id == runtime_id:
                    self._state = ModelState(
                        runtime_id=runtime_id,
                        runtime_epochs=runtime_epochs,
                        connection_epoch=self._state.connection_epoch + 1,
                    )
                else:
                    self._state.runtime_epochs = runtime_epochs
                    self._state.connection_epoch += 1
        logger.info("State reset")


__all__ = ["ModelState", "ModelStateManager"]
