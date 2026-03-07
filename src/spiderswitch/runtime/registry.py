# spiderswitch runtime registry and resolver
"""
Runtime registry/resolver execution layer for multi-runtime routing.
多运行时路由执行层：注册表与解析器。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import ModelSwitcherError
from .base import Runtime


@dataclass
class RuntimeResolution:
    """Resolved runtime selection result."""

    runtime_id: str
    source: str


class RuntimeRegistry:
    """Registry for runtime instances keyed by runtime_id."""

    def __init__(self, runtimes: dict[str, Runtime], default_runtime_id: str) -> None:
        if not runtimes:
            raise ValueError("RuntimeRegistry requires at least one runtime.")
        if default_runtime_id not in runtimes:
            raise ValueError(f"default_runtime_id '{default_runtime_id}' not found in runtimes.")
        self._runtimes = dict(runtimes)
        self._default_runtime_id = default_runtime_id

    @property
    def default_runtime_id(self) -> str:
        return self._default_runtime_id

    def get_runtime(self, runtime_id: str | None = None) -> tuple[str, Runtime]:
        target = runtime_id or self._default_runtime_id
        runtime = self._runtimes.get(target)
        if runtime is None:
            raise ModelSwitcherError(
                f"Unknown runtime_id '{target}'",
                details={
                    "runtime_id": target,
                    "available_runtime_ids": sorted(self._runtimes.keys()),
                    "default_runtime_id": self._default_runtime_id,
                },
            )
        return target, runtime

    def list_runtime_ids(self) -> list[str]:
        return sorted(self._runtimes.keys())

    async def close_runtime(self, runtime_id: str) -> None:
        _, runtime = self.get_runtime(runtime_id)
        await runtime.close()

    async def close_all(self) -> None:
        for runtime in self._runtimes.values():
            await runtime.close()


class RuntimeResolver:
    """Resolve requested runtime_id while keeping strategy outside spiderswitch."""

    def __init__(self, registry: RuntimeRegistry) -> None:
        self._registry = registry

    def resolve(self, requested_runtime_id: str | None, active_runtime_id: str | None = None) -> RuntimeResolution:
        if requested_runtime_id:
            self._registry.get_runtime(requested_runtime_id)
            return RuntimeResolution(runtime_id=requested_runtime_id, source="request")
        if active_runtime_id:
            self._registry.get_runtime(active_runtime_id)
            return RuntimeResolution(runtime_id=active_runtime_id, source="state")
        return RuntimeResolution(runtime_id=self._registry.default_runtime_id, source="default")


__all__ = ["RuntimeRegistry", "RuntimeResolver", "RuntimeResolution"]
