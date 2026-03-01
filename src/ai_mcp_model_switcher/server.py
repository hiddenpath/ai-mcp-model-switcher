# ai-mcp-model-switcher MCP server
"""
MCP server entry point for model switching.
MCP服务器主入口，提供模型切换功能。

Provides dependency injection for better testability and multiple instance support.
提供依赖注入以便于更好的测试和多实例支持。
"""

from __future__ import annotations

import asyncio
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .runtime import PythonRuntime
from .runtime.base import Runtime
from .state import ModelStateManager
from .tools import list, status, switch


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_app(
    runtime: Runtime | None = None,
    state_manager: ModelStateManager | None = None,
) -> Server:
    """Create MCP server with optional dependencies.
    
    This factory function allows for dependency injection, making the server
    more testable and enabling multiple instances with different runtimes.
    
    Args:
        runtime: Optional runtime instance. If None, uses PythonRuntime
        state_manager: Optional state manager instance. If None, creates new one
    
    Returns:
        Configured MCP Server instance
    """
    _runtime = runtime or PythonRuntime()
    _state = state_manager or ModelStateManager()
    
    app = Server("ai-mcp-model-switcher")
    
    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """Expose available MCP tools.
        
        Returns:
            List of Tool objects
        """
        return [
            switch.tool_schema(),
            list.tool_schema(),
            status.tool_schema(),
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, object]) -> list:
        """Handle tool calls with structured error logging.
        
        Args:
            name: Tool name
            arguments: Tool arguments
        
        Returns:
            List of response content or error content
        """
        try:
            if name == "switch_model":
                return await switch.handle(_runtime, _state, arguments)
            elif name == "list_models":
                return await list.handle(_runtime, arguments)
            elif name == "get_status":
                return await status.handle(_state)
            else:
                logger.warning(f"Unknown tool requested: {name}")
                return switch.format_model_info(_runtime)._format_error_response(
                    message=f"Unknown tool: {name}",
                    error_type="UnknownToolError",
                )
        except Exception as e:
            logger.exception(
                f"Error handling tool call '{name}': {e}",
                extra={
                    "tool": name,
                    "arguments": arguments,
                }
            )
            return switch.format_model_info(_runtime)._format_error_response(
                message=f"Internal error: {e}",
                error_type="InternalServerError",
            )
    
    return app


async def main(
    runtime: Runtime | None = None,
    state_manager: ModelStateManager | None = None,
) -> None:
    """Main entry point for the MCP server.
    
    Runs the stdio server and handles cleanup on shutdown.
    
    Args:
        runtime: Optional runtime instance for dependency injection
        state_manager: Optional state manager for dependency injection
    """
    logger.info("Starting ai-mcp-model-switcher MCP server")
    
    # Create app with dependencies
    app = create_app(runtime, state_manager)
    
    # Store runtime reference for cleanup
    _runtime = runtime or app._get_runtime()  # type: ignore
    
    try:
        # Run stdio server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        try:
            await _runtime.close()  # type: ignore
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        logger.info("Server shutdown complete")


def cli() -> None:
    """CLI entry point for the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()


__all__ = ["create_app", "main", "cli"]
