# spiderswitch
"""
Model Context Protocol server for dynamic AI model switching in ai-lib ecosystem.
MCP服务器，用于ai-lib生态系统中的动态AI模型切换。

This package provides:
- MCP server with model switching capabilities
- Runtime abstraction layer for multiple ai-lib implementations
- Thread-safe state management
- Comprehensive error handling and validation

该包提供：
- 具有模型切换功能的 MCP 服务器
- 多个 ai-lib 实现的运行时抽象层
- 线程安全的状态管理
- 全面的错误处理和验证
"""

from __future__ import annotations

# Lazy import to avoid loading mcp dependency on package import
# This allows the package to be imported in tests without mcp installed


def main() -> None:
    """Main entry point for the MCP server."""
    from spiderswitch.server import cli

    cli()


__all__ = ["main"]

__version__ = "0.4.0"
