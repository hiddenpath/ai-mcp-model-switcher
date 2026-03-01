# ai-mcp-model-switcher custom exceptions
"""
Custom exceptions for better error handling in the model switcher.
自定义异常类，用于改进模型切换器的错误处理。
"""

from __future__ import annotations


class ModelSwitcherError(Exception):
    """Base exception for all model switcher errors.
    模型切换器的基础异常类。"""

    def __init__(
        self,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, object]:
        """Convert exception to dictionary for MCP response."""
        result = {
            "error_type": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class ModelNotFoundError(ModelSwitcherError):
    """Model not found in available models.
    在可用模型中找不到指定的模型。"""

    pass


class InvalidModelError(ModelSwitcherError):
    """Invalid model format or parameters.
    无效的模型格式或参数。"""

    pass


class ProviderNotAvailableError(ModelSwitcherError):
    """Provider is not available or not configured.
    Provider 不可用或未配置。"""

    pass


class ApiKeyMissingError(ModelSwitcherError):
    """API key is missing for the provider.
    缺少 Provider 的 API 密钥。"""

    pass


class ConnectionError(ModelSwitcherError):
    """Failed to connect to provider API.
    无法连接到 Provider API。"""

    pass


class ValidationError(ModelSwitcherError):
    """Input validation failed.
    输入验证失败。"""

    pass


__all__ = [
    "ModelSwitcherError",
    "ModelNotFoundError",
    "InvalidModelError",
    "ProviderNotAvailableError",
    "ApiKeyMissingError",
    "ConnectionError",
    "ValidationError",
]
