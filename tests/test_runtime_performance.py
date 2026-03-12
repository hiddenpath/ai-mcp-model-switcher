# Runtime performance baseline tests
"""
Performance smoke tests for runtime initialization path.
运行时初始化路径的性能基线冒烟测试。
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
import yaml

from spiderswitch.runtime.python_runtime import PythonRuntime


@pytest.mark.asyncio
async def test_runtime_offline_initialization_latency_baseline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Offline init + first list_models should stay within lightweight baseline."""
    protocol_root = tmp_path / "ai-protocol"
    model_dir = protocol_root / "v1" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "openai.yaml").write_text(
        yaml.safe_dump(
            {
                "models": {
                    "gpt-4o": {
                        "provider": "openai",
                        "model_id": "gpt-4o",
                        "capabilities": ["streaming", "tools"],
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SPIDERSWITCH_SYNC_ON_INIT", "0")
    runtime = PythonRuntime(ai_protocol_path=str(protocol_root))

    start = time.perf_counter()
    models = await runtime.list_models()
    elapsed = time.perf_counter() - start

    assert models
    # Keep this threshold relaxed enough for CI variance.
    assert elapsed < 1.0
