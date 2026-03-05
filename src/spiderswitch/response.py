# spiderswitch response utilities
"""
Unified MCP response format and utilities.
统一的 MCP 响应格式和工具类。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from mcp.types import TextContent


@dataclass
class MCPResponse:
    """Unified MCP response format.
    统一的 MCP 响应格式。

    Attributes:
        status: Response status - 'success' or 'error'
        data: Optional response data for successful responses
        error: Optional error information for error responses
        message: Optional human-readable message
    """

    status: str
    data: dict[str, Any] | None = None
    error_info: dict[str, Any] | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary representation.
        将响应转换为字典表示。

        Returns:
            Dictionary with response data
        """
        result: dict[str, Any] = {"status": self.status}

        if self.data is not None:
            result["data"] = self.data

        if self.error_info is not None:
            result["error"] = self.error_info

        if self.message is not None:
            result["message"] = self.message

        return result

    def to_text_content(self) -> TextContent:
        """Convert response to MCP TextContent.
        将响应转换为 MCP TextContent。

        Returns:
            TextContent object with serialized response
        """
        return TextContent(
            type="text",
            text=json.dumps(self.to_dict(), ensure_ascii=False),
        )

    @classmethod
    def success(
        cls,
        data: dict[str, Any],
        message: str | None = None,
    ) -> MCPResponse:
        """Create a successful response.
        创建成功响应。

        Args:
            data: Response data
            message: Optional success message

        Returns:
            MCPResponse with success status
        """
        return cls(status="success", data=data, message=message)

    @classmethod
    def error(
        cls,
        message: str,
        error_type: str = "RuntimeError",
        details: dict[str, Any] | None = None,
    ) -> MCPResponse:
        """Create an error response.
        创建错误响应。

        Args:
            message: Error message
            error_type: Type of error
            details: Optional error details

        Returns:
            MCPResponse with error status
        """
        error_info: dict[str, Any] = {"type": error_type, "message": message}
        if details:
            error_info["details"] = details

        return cls(status="error", error_info=error_info, message=message)


def format_error_response(
    message: str,
    error_type: str = "RuntimeError",
    error_code: str | None = None,
) -> TextContent:
    """Format an error response as TextContent.
    格式化错误响应为 TextContent。

    Args:
        message: Error message
        error_type: Type of error
        error_code: Optional error code for programmatic handling

    Returns:
        TextContent with formatted error
    """
    error_dict: dict[str, Any] = {
        "status": "error",
        "error": {
            "type": error_type,
            "message": message,
        },
    }

    if error_code:
        error_dict["error"]["code"] = error_code

    return TextContent(type="text", text=json.dumps(error_dict, ensure_ascii=False))


def format_success_response(
    data: dict[str, Any],
    message: str | None = None,
) -> TextContent:
    """Format a success response as TextContent.
    格式化成功响应为 TextContent。

    Args:
        data: Response data
        message: Optional success message

    Returns:
        TextContent with formatted success response
    """
    response_dict = {"status": "success", "data": data}

    if message:
        response_dict["message"] = message

    return TextContent(type="text", text=json.dumps(response_dict, ensure_ascii=False))


__all__ = [
    "MCPResponse",
    "format_error_response",
    "format_success_response",
]
