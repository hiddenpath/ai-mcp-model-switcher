# Tests for state management
"""
测试状态管理
"""

from __future__ import annotations

from spiderswitch.runtime.base import ModelCapabilities, ModelInfo
from spiderswitch.state import ModelState, ModelStateManager


def test_model_state_default() -> None:
    """Test default model state."""
    state = ModelState()
    assert state.provider is None
    assert state.model is None
    assert state.capabilities is None
    assert state.runtime_id is None
    assert state.runtime_epoch == 0
    assert state.is_configured is False


def test_model_state_to_dict() -> None:
    """Test converting state to dictionary."""
    state = ModelState(
        provider="openai",
        model="gpt-4o",
        capabilities=["streaming", "tools"],
        is_configured=True,
    )
    result = state.to_dict()
    assert result["provider"] == "openai"
    assert result["model"] == "gpt-4o"
    assert result["capabilities"] == ["streaming", "tools"]
    assert result["is_configured"] is True


def test_state_manager_update() -> None:
    """Test updating state from model info."""
    manager = ModelStateManager()

    info = ModelInfo(
        id="openai/gpt-4o",
        provider="openai",
        capabilities=ModelCapabilities(streaming=True, tools=True),
    )

    state = manager.update_from_model_info(info)

    assert state.provider == "openai"
    assert state.model == "gpt-4o"
    assert state.capabilities == ["streaming", "tools"]
    assert state.is_configured is True
    assert state.connection_epoch == 1
    assert state.runtime_id == "python-runtime"
    assert state.runtime_epoch == 1
    assert state.last_switched_at is not None


def test_state_manager_epoch_increments() -> None:
    """Test connection_epoch increments on every switch."""
    manager = ModelStateManager()

    first = ModelInfo(
        id="openai/gpt-4o",
        provider="openai",
        capabilities=ModelCapabilities(streaming=True),
    )
    second = ModelInfo(
        id="anthropic/claude-3-5-sonnet",
        provider="anthropic",
        capabilities=ModelCapabilities(streaming=True, tools=True),
    )

    state1 = manager.update_from_model_info(first)
    state2 = manager.update_from_model_info(second)

    assert state1.connection_epoch == 1
    assert state2.connection_epoch == 2


def test_state_manager_get() -> None:
    """Test getting state."""
    manager = ModelStateManager()
    state = manager.get_state()
    assert state.is_configured is False


def test_state_manager_reset() -> None:
    """Test resetting state."""
    manager = ModelStateManager()

    # Setup initial state
    info = ModelInfo(
        id="openai/gpt-4o",
        provider="openai",
        capabilities=ModelCapabilities(streaming=True),
    )
    manager.update_from_model_info(info)

    # Verify state is set
    assert manager.get_state().is_configured is True

    # Reset
    manager.reset()

    # Verify state is cleared
    assert manager.get_state().is_configured is False


def test_state_manager_runtime_scoped_reset() -> None:
    """Runtime-scoped reset only affects target runtime epoch map."""
    manager = ModelStateManager()
    manager.update_from_model_info_with_runtime(
        ModelInfo(
            id="openai/gpt-4o",
            provider="openai",
            capabilities=ModelCapabilities(streaming=True),
        ),
        runtime_id="python-runtime",
    )
    manager.update_from_model_info_with_runtime(
        ModelInfo(
            id="anthropic/claude-3-5-sonnet",
            provider="anthropic",
            capabilities=ModelCapabilities(streaming=True),
        ),
        runtime_id="rust-runtime",
    )

    manager.reset(runtime_id="python-runtime")
    state = manager.get_state()
    assert "python-runtime" not in state.runtime_epochs
    assert "rust-runtime" in state.runtime_epochs
