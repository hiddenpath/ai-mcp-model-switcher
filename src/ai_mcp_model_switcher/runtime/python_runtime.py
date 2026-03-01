# ai-mcp-model-switcher Python runtime implementation
"""
ai-lib-python runtime implementation using ProtocolLoader and AiClient.
使用ai-lib-python SDK的实现，通过ProtocolLoader和AiClient进行模型交互。

Follows ARCH-001: All provider configurations loaded from ai-protocol manifests.
遵循 ARCH-001：所有 provider 配置从 ai-protocol manifests 加载。
"""

from __future__ import annotations

import logging

from ai_lib_python import AiClient
from ai_lib_python.protocol import ProtocolLoader

from ..errors import (
    InvalidModelError,
    ModelNotFoundError,
    ModelSwitcherError,
)
from ..validation import DEFAULT_VALIDATOR
from .base import ModelCapabilities, ModelInfo, Runtime


logger = logging.getLogger(__name__)


class PythonRuntime(Runtime):
    """ai-lib-python runtime implementation.
    
    This implementation uses the ai-lib-python SDK to interact with AI models.
    It follows the protocol-driven design principle (ARCH-001): all provider
    behavior is loaded from ai-protocol manifests, with no hardcoded provider logic.
    
    Runtime state is managed internally and cleaned up on close().
    使用 ai-lib-python SDK 的实现。遵循协议驱动设计原则 (ARCH-001)：
    所有 provider 行为从 ai-protocol manifests 加载，没有硬编码的 provider 逻辑。
    运行时状态在内部管理，并在 close() 时清理。
    """

    def __init__(
        self,
        fallback_to_github: bool = True,
        cache_enabled: bool = True,
        ai_protocol_path: str | None = None,
    ) -> None:
        """Initialize the Python runtime.

        Args:
            fallback_to_github: Whether to fetch manifests from GitHub if not found locally
            cache_enabled: Whether to cache loaded manifests
            ai_protocol_path: Optional custom path to ai-protocol directory
        """
        self._loader = ProtocolLoader(
            fallback_to_github=fallback_to_github,
            cache_enabled=cache_enabled,
            ai_protocol_path=ai_protocol_path,
        )
        self._current_client: AiClient | None = None
        self._current_model_info: ModelInfo | None = None
        self._is_initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of the model manager.
        
        Loads models from ai-protocol manifests on first use.
        延迟初始化模型管理器，首次使用时从 ai-protocol manifests 加载。
        """
        if self._is_initialized:
            return

        try:
            # Load models from ai-protocol manifests
            # ProtocolLoader handles all provider loading - no hardcoded logic
            # 从 ai-protocol manifests 加载模型
            # ProtocolLoader 处理所有 provider 加载 - 无硬编码逻辑
            self._model_manager = self._loader.load_all_manifests()
            self._is_initialized = True
            logger.info(
                f"Runtime initialized: loaded {len(list(self._model_manager.list_models()))} models"
            )
        except Exception as e:
            logger.error(f"Failed to initialize runtime: {e}")
            raise ModelSwitcherError(
                "Failed to load model manifests from ai-protocol",
                details={"error": str(e)},
            ) from e

    async def list_models(
        self,
        filter_provider: str | None = None,
        filter_capability: str | None = None,
    ) -> list[ModelInfo]:
        """List available models from ai-protocol manifests.

        Args:
            filter_provider: Optional provider ID to filter by
            filter_capability: Optional capability to filter by

        Returns:
            List of ModelInfo objects matching filters

        Raises:
            ModelSwitcherError: If runtime initialization fails
        """
        # Ensure initialization
        self._ensure_initialized()

        models = list(self._model_manager.list_models())

        result = []
        for model in models:
            provider_id = model.name.split("/")[0]

            if filter_provider and provider_id != filter_provider:
                continue

            # Get capabilities for this model
            caps = ModelCapabilities()
            if "streaming" in model.capabilities:
                caps.streaming = True
            if "tools" in model.capabilities:
                caps.tools = True
            if "vision" in model.capabilities:
                caps.vision = True
            if "embeddings" in model.capabilities:
                caps.embeddings = True
            if "audio" in model.capabilities:
                caps.audio = True

            if filter_capability and not getattr(caps, filter_capability, False):
                continue

            result.append(
                ModelInfo(
                    id=model.name,
                    provider=provider_id,
                    capabilities=caps,
                )
            )

        return result

    async def switch_model(
        self,
        model_id: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> ModelInfo:
        """Switch to a specific model using ai-lib-python SDK.

        Args:
            model_id: Model identifier (e.g., "openai/gpt-4o")
            api_key: Optional explicit API key
            base_url: Optional custom base URL

        Returns:
            ModelInfo for the switched model

        Raises:
            InvalidModelError: If model_id format is invalid
            ModelNotFoundError: If model_id is not in available models
            ModelSwitcherError: If client creation fails
        """
        # Validate parameters
        try:
            DEFAULT_VALIDATOR.validate_model_id(model_id)
            DEFAULT_VALIDATOR.validate_api_key(api_key)
            DEFAULT_VALIDATOR.validate_base_url(base_url)
        except InvalidModelError as e:
            logger.error(f"Invalid model parameters: {e}")
            raise

        # Ensure initialization and get available models
        self._ensure_initialized()
        available_models = await self.list_models()
        model_map = {m.id: m for m in available_models}

        if model_id not in model_map:
            available = list(model_map.keys())
            logger.error(f"Model '{model_id}' not found. Available: {available}")
            raise ModelNotFoundError(
                f"Model '{model_id}' not found.",
                details={"available_models": available},
            )

        model_info = model_map[model_id]

        # Close existing client
        if self._current_client:
            try:
                await self._current_client.close()
            except Exception as e:
                logger.warning(f"Error closing previous client: {e}")

        # Create new client
        try:
            self._current_client = await AiClient.create(
                model=model_id,
                api_key=api_key,
                base_url=base_url,
            )
            self._current_model_info = model_info
            logger.info(f"Successfully switched to model: {model_id}")
        except Exception as e:
            self._current_client = None
            self._current_model_info = None
            logger.error(f"Failed to create client for model '{model_id}': {e}")
            raise ModelSwitcherError(
                f"Failed to create client for model '{model_id}'",
                details={"error": str(e)},
            ) from e

        return model_info

    async def get_current_model(self) -> ModelInfo | None:
        """Get information about the currently active model.

        Returns:
            ModelInfo if a model is configured, None otherwise
        """
        return self._current_model_info

    async def close(self) -> None:
        """Cleanup resources.
        
        Closes the current client and clears internal state.
        Any errors during cleanup are logged but not raised.
        关闭当前客户端并清理内部状态。清理过程中的错误会被记录但不会抛出。
        """
        cleanup_errors: list[str] = []

        # Close current client
        if self._current_client:
            try:
                await self._current_client.close()
                logger.info("Client closed successfully")
            except Exception as e:
                error_msg = f"Failed to close client: {e}"
                cleanup_errors.append(error_msg)
                logger.error(error_msg)
            finally:
                self._current_client = None

        # Clear internal state
        self._current_model_info = None
        self._is_initialized = False

        # Report any cleanup errors
        if cleanup_errors:
            logger.warning(
                f"Resource cleanup completed with {len(cleanup_errors)} error(s)"
            )


# Helper functions for MCP tool handlers


def extract_model_from_args(args: dict[str, object]) -> tuple[str, str | None, str | None]:
    """Extract and validate model parameters from MCP tool arguments.

    Args:
        args: Arguments dictionary from MCP tool call

    Returns:
        Tuple of (model_id, api_key, base_url)

    Raises:
        InvalidModelError: If validation fails
    """
    model = args.get("model")
    if not model or not isinstance(model, str):
        raise InvalidModelError(
            "Missing required parameter: 'model'",
        )

    api_key = args.get("api_key")
    base_url = args.get("base_url")

    # Use the validator
    return DEFAULT_VALIDATOR.validate_switch_arguments(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )


def format_model_info(info: ModelInfo) -> dict[str, object]:
    """Convert ModelInfo to MCP response format.

    Args:
        info: ModelInfo object to format

    Returns:
        Dictionary with model information
    """
    return {
        "id": info.id,
        "provider": info.provider,
        "capabilities": info.capabilities.to_list(),
    }


__all__ = ["PythonRuntime", "extract_model_from_args", "format_model_info"]
