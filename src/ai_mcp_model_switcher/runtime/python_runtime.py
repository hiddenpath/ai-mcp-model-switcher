# ai-mcp-model-switcher Python runtime implementation
"""
ai-lib-python runtime implementation using ProtocolLoader and AiClient.
使用ai-lib-python SDK的实现，通过ProtocolLoader和AiClient进行模型交互。
"""

from __future__ import annotations

import os
from typing import Any

from ai_lib_python import AiClient
from ai_lib_python.protocol import ProtocolLoader
from ai_lib_python.routing import create_openai_models, create_anthropic_models

from .base import ModelCapabilities, ModelInfo, Runtime


class PythonRuntime(Runtime):
    """ai-lib-python runtime implementation.

    This implementation uses the ai-lib-python SDK to interact with AI models.
    It follows the protocol-driven design principle (ARCH-001): all provider
    behavior is loaded from ai-protocol manifests, with no hardcoded provider logic.
    """

    def __init__(self) -> None:
        """Initialize the Python runtime."""
        self._loader = ProtocolLoader(
            fallback_to_github=True,
            cache_enabled=True,
        )
        self._current_client: AiClient | None = None
        self._current_model_info: ModelInfo | None = None

        # Model manager for runtime capabilities
        self._model_manager = create_openai_models()
        try:
            self._model_manager.merge(create_anthropic_models())
        except Exception:
            # Anthropic models may not be available
            pass

    async def list_models(
        self,
        filter_provider: str | None = None,
        filter_capability: str | None = None,
    ) -> list[ModelInfo]:
        """List available models from ai-protocol manifests.

        Uses ModelManager to get available models and their capabilities.
        """
        models = self._model_manager.list_models()

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

        Creates a new AiClient instance for the requested model.
        """
        # Validate model exists
        available_models = await self.list_models()
        model_map = {m.id: m for m in available_models}

        if model_id not in model_map:
            raise RuntimeError(
                f"Model '{model_id}' not found. "
                f"Available: {list(model_map.keys())}"
            )

        model_info = model_map[model_id]

        # Close existing client
        if self._current_client:
            try:
                await self._current_client.close()
            except Exception:
                pass

        # Create new client
        try:
            self._current_client = await AiClient.create(
                model=model_id,
                api_key=api_key,
                base_url=base_url,
            )
            self._current_model_info = model_info
        except Exception as e:
            self._current_client = None
            self._current_model_info = None
            raise RuntimeError(f"Failed to create client for model '{model_id}': {e}") from e

        return model_info

    async def get_current_model(self) -> ModelInfo | None:
        """Get information about the currently active model."""
        return self._current_model_info

    async def close(self) -> None:
        """Cleanup resources."""
        if self._current_client:
            try:
                await self._current_client.close()
            except Exception:
                pass
            self._current_client = None
        self._current_model_info = None


# Helper functions for MCP tool handlers

def extract_model_from_args(args: dict[str, Any]) -> tuple[str, str | None, str | None]:
    """Extract model parameters from MCP tool arguments."""
    model = args.get("model")
    if not model or not isinstance(model, str):
        raise ValueError("Missing required parameter: 'model'")

    # Validate format: provider/model
    if "/" not in model:
        raise ValueError(
            f"Invalid model format: '{model}'. Expected format: 'provider/model'"
        )

    api_key = args.get("api_key")
    base_url = args.get("base_url")

    return model, api_key, base_url


def format_model_info(info: ModelInfo) -> dict[str, Any]:
    """Convert ModelInfo to MCP response format."""
    return {
        "id": info.id,
        "provider": info.provider,
        "capabilities": info.capabilities.to_list(),
    }


__all__ = ["PythonRuntime", "extract_model_from_args", "format_model_info"]
