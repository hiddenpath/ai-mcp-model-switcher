# ai-mcp-model-switcher validation utilities
"""
Input validation utilities for model parameters.
模型参数输入验证工具类。
"""

from __future__ import annotations

import re
from typing import Any

from .errors import InvalidModelError, ValidationError


# Model ID format: provider/model
# 模型 ID 格式：provider/model
MODEL_PATTERN = re.compile(r"^[a-z0-9-]+/[a-z0-9-.]+$")

# These will be loaded from ai-protocol manifests
# Currently including common providers for validation
# These should be replaced with protocol-driven loading
# 这些将从 ai-protocol manifests 中加载
# 目前包含常见的 provider 用于验证
# 应替换为协议驱动的加载方式
DEFAULT_VALID_PROVIDERS = {
    "openai",
    "anthropic",
    "google",
    "deepseek",
    "cohere",
    "mistral",
    "meta",
}


class Validator:
    """Input validator for model parameters.
    模型参数输入验证器。
    """

    def __init__(
        self,
        valid_providers: set[str] | None = None,
        strict: bool = True,
    ) -> None:
        """Initialize validator.

        Args:
            valid_providers: Set of valid provider IDs. If None, uses default
            strict: If True, raises exception on validation failure; if False,
                   returns False
        """
        self.valid_providers = valid_providers or DEFAULT_VALID_PROVIDERS.copy()
        self.strict = strict

    def validate_model_id(self, model_id: str) -> None:
        """Validate model ID format.

        Args:
            model_id: Model ID to validate

        Raises:
            InvalidModelError: If validation fails and strict=True
        """
        if not isinstance(model_id, str):
            self._raise_error(
                InvalidModelError,
                f"Model ID must be a string, got {type(model_id).__name__}",
            )

        if not model_id:
            self._raise_error(
                InvalidModelError,
                "Model ID cannot be empty",
            )

        if not MODEL_PATTERN.match(model_id):
            self._raise_error(
                InvalidModelError,
                f"Invalid model format: '{model_id}'. "
                f"Expected format: 'provider/model' (e.g., 'openai/gpt-4o')",
            )

        # Validate provider
        provider = self._extract_provider(model_id)
        if provider not in self.valid_providers:
            self._raise_error(
                InvalidModelError,
                f"Unknown provider: '{provider}'. "
                f"Valid providers: {sorted(self.valid_providers)}",
            )

    def validate_api_key(self, api_key: Any) -> None:
        """Validate API key.

        Args:
            api_key: API key to validate

        Raises:
            ValidationError: If validation fails and strict=True
        """
        if api_key is None:
            # API key is optional
            return

        if not isinstance(api_key, str):
            self._raise_error(
                ValidationError,
                f"API key must be a string, got {type(api_key).__name__}",
            )

        # Some basic sanity checks
        if not api_key:
            self._raise_error(
                ValidationError,
                "API key cannot be empty string",
            )

        # Check for common placeholder strings
        placeholder_patterns = [
            "your-api-key",
            "your_api_key",
            "sk-...",
            "sk-ant-...",
        ]
        for pattern in placeholder_patterns:
            if api_key == pattern or api_key.startswith(pattern):
                self._raise_error(
                    ValidationError,
                    f"API key appears to be a placeholder: '{pattern}'",
                )

    def validate_base_url(self, base_url: Any) -> None:
        """Validate base URL.

        Args:
            base_url: Base URL to validate

        Raises:
            ValidationError: If validation fails and strict=True
        """
        if base_url is None:
            # Base URL is optional
            return

        if not isinstance(base_url, str):
            self._raise_error(
                ValidationError,
                f"Base URL must be a string, got {type(base_url).__name__}",
            )

        if not base_url:
            self._raise_error(
                ValidationError,
                "Base URL cannot be empty string",
            )

        # Check URL format
        if not base_url.startswith(("http://", "https://")):
            self._raise_error(
                ValidationError,
                f"Invalid base URL format: '{base_url}'. "
                f"Must start with http:// or https://",
            )

    def validate_switch_arguments(
        self,
        model: Any,
        api_key: Any = None,
        base_url: Any = None,
    ) -> tuple[str, str | None, str | None]:
        """Validate all switch_model arguments.

        Args:
            model: Model ID argument
            api_key: Optional API key argument
            base_url: Optional base URL argument

        Returns:
            Tuple of (model, api_key, base_url) with proper types

        Raises:
            ValidationError: If any validation fails
        """
        # Validate model
        if not model or not isinstance(model, str):
            raise InvalidModelError(
                "Missing required parameter: 'model'",
            )

        self.validate_model_id(model)
        self.validate_api_key(api_key)
        self.validate_base_url(base_url)

        return (model, api_key, base_url)

    def _extract_provider(self, model_id: str) -> str:
        """Extract provider ID from model ID.

        Args:
            model_id: Model ID string

        Returns:
            Provider ID
        """
        return model_id.split("/", 1)[0]

    def _raise_error(
        self,
        error_class: type[Exception],
        message: str,
    ) -> None:
        """Raise an exception if in strict mode.

        Args:
            error_class: Exception class to raise
            message: Error message

        Raises:
            The specified exception if strict=True
        """
        if self.strict:
            raise error_class(message)


# Default validator instance
DEFAULT_VALIDATOR = Validator()


def validate_or_raise(
    *args: Any,
    **kwargs: Any,
) -> tuple[str, str | None, str | None]:
    """Validate arguments using default strict validator.

    Args:
        model: Model ID
        api_key: Optional API key
        base_url: Optional base URL

    Returns:
        Tuple of validated arguments
    """
    return DEFAULT_VALIDATOR.validate_switch_arguments(*args, **kwargs)


__all__ = [
    "Validator",
    "DEFAULT_VALIDATOR",
    "DEFAULT_VALID_PROVIDERS",
    "MODEL_PATTERN",
    "validate_or_raise",
]
