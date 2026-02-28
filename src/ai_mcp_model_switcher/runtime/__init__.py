# ai-mcp-model-switcher runtime module
"""
Runtime abstraction layer for different ai-lib implementations.
运行时抽象层，支持不同的ai-lib实现。
"""

from __future__ import annotations

from ai_mcp_model_switcher.runtime.base import Runtime
from ai_mcp_model_switcher.runtime.python_runtime import PythonRuntime

__all__ = ["Runtime", "PythonRuntime"]
