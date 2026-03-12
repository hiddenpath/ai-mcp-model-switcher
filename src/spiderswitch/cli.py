# spiderswitch CLI
"""
Command-line interface for server operations and plugin-market onboarding.
命令行入口：服务运行、初始化配置与健康检查。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Literal

from .runtime.python_runtime import PythonRuntime
from .validation import PROVIDER_API_KEY_ENV, PROXY_ENV_VARS

ClientType = Literal["cursor", "claude", "opencode"]


def _build_mcp_config(client: ClientType, ai_protocol_path: str | None) -> dict[str, Any]:
    """Build a default MCP config template for target clients."""
    env: dict[str, str] = {
        "AI_PROTOCOL_PATH": ai_protocol_path or "/path/to/ai-protocol",
        "OPENAI_API_KEY": "sk-...",
    }
    if client in {"cursor", "claude"}:
        return {
            "mcpServers": {
                "spiderswitch": {
                    "command": "spiderswitch",
                    "args": ["serve"],
                    "env": env,
                }
            }
        }
    return {
        "$schema": "https://opencode.ai/config.json",
        "mcp": {
            "spiderswitch": {
                "type": "local",
                "command": ["spiderswitch", "serve"],
                "enabled": True,
                "environment": env,
            }
        },
    }


def write_init_config(
    *,
    output: Path,
    client: ClientType,
    ai_protocol_path: str | None,
    force: bool,
) -> Path:
    """Write MCP config template to output file."""
    if output.exists() and not force:
        raise FileExistsError(f"Config file already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    config = _build_mcp_config(client=client, ai_protocol_path=ai_protocol_path)
    output.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


async def _runtime_probe(ai_protocol_path: str | None) -> dict[str, Any]:
    """Run a lightweight runtime list_models probe."""
    old_sync = os.getenv("SPIDERSWITCH_SYNC_ON_INIT")
    os.environ["SPIDERSWITCH_SYNC_ON_INIT"] = "0"
    runtime = PythonRuntime(ai_protocol_path=ai_protocol_path)
    try:
        models = await asyncio.wait_for(runtime.list_models(), timeout=5.0)
        return {
            "ok": True,
            "detail": f"runtime probe succeeded, discovered {len(models)} models",
        }
    except Exception as exc:
        return {
            "ok": False,
            "detail": f"runtime probe failed: {exc}",
            "hint": "Check AI_PROTOCOL_PATH and local ai-protocol manifests.",
        }
    finally:
        await runtime.close()
        if old_sync is None:
            os.environ.pop("SPIDERSWITCH_SYNC_ON_INIT", None)
        else:
            os.environ["SPIDERSWITCH_SYNC_ON_INIT"] = old_sync


def run_doctor_checks(*, include_runtime_probe: bool) -> dict[str, Any]:
    """Run structured health checks for installation readiness."""
    checks: list[dict[str, Any]] = []

    py_ok = sys.version_info >= (3, 10)
    checks.append(
        {
            "name": "python_version",
            "ok": py_ok,
            "detail": f"detected {sys.version.split()[0]} (require >= 3.10)",
        }
    )

    runtime = PythonRuntime()
    protocol_path = runtime._resolve_protocol_base()  # noqa: SLF001
    protocol_ok = protocol_path is not None
    checks.append(
        {
            "name": "ai_protocol_path",
            "ok": protocol_ok,
            "detail": str(protocol_path) if protocol_path else "not found",
            "hint": "Set AI_PROTOCOL_PATH or AI_PROTOCOL_DIR to ai-protocol root.",
        }
    )

    configured_keys: list[str] = []
    for env_names in PROVIDER_API_KEY_ENV.values():
        for env_name in env_names:
            if os.getenv(env_name):
                configured_keys.append(env_name)
    checks.append(
        {
            "name": "api_keys",
            "ok": bool(configured_keys),
            "detail": f"{len(configured_keys)} env var(s) configured",
            "configured_env_vars": sorted(set(configured_keys)),
            "hint": "Configure at least one provider API key.",
        }
    )

    unsupported_proxy_env = runtime._detect_unsupported_proxy_env()  # noqa: SLF001
    checks.append(
        {
            "name": "proxy_scheme",
            "ok": not bool(unsupported_proxy_env),
            "detail": (
                "unsupported proxy env vars: "
                f"{sorted(unsupported_proxy_env.keys())}"
                if unsupported_proxy_env
                else "proxy scheme looks compatible"
            ),
            "observed_proxy_env_vars": [key for key in PROXY_ENV_VARS if os.getenv(key)],
            "hint": "Use http://, https://, or socks5:// proxy scheme if needed.",
        }
    )

    if include_runtime_probe:
        probe = asyncio.run(_runtime_probe(str(protocol_path) if protocol_path else None))
        checks.append({"name": "runtime_probe", **probe})

    healthy = all(bool(item.get("ok", False)) for item in checks)
    return {"healthy": healthy, "checks": checks}


def _print_human_doctor_result(result: dict[str, Any]) -> None:
    """Print doctor output in human-readable format."""
    print("spiderswitch doctor")
    print("==================")
    for item in result.get("checks", []):
        status = "OK" if item.get("ok") else "FAIL"
        detail = item.get("detail", "")
        print(f"- [{status}] {item.get('name')}: {detail}")
        hint = item.get("hint")
        if hint and not item.get("ok"):
            print(f"  hint: {hint}")
    print("")
    print(f"overall: {'healthy' if result.get('healthy') else 'unhealthy'}")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for spiderswitch."""
    parser = argparse.ArgumentParser(prog="spiderswitch")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("serve", help="Run MCP stdio server")

    init_parser = subparsers.add_parser("init", help="Generate MCP config template")
    init_parser.add_argument(
        "--client",
        choices=["cursor", "claude", "opencode"],
        default="cursor",
        help="Target MCP client template",
    )
    init_parser.add_argument(
        "--output",
        default=".spiderswitch.mcp.json",
        help="Output config path",
    )
    init_parser.add_argument(
        "--ai-protocol-path",
        default=os.getenv("AI_PROTOCOL_PATH") or os.getenv("AI_PROTOCOL_DIR"),
        help="Optional ai-protocol root path",
    )
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing output file")

    doctor_parser = subparsers.add_parser("doctor", help="Run installation health checks")
    doctor_parser.add_argument("--json", action="store_true", help="Print JSON output")
    doctor_parser.add_argument(
        "--no-runtime-probe",
        action="store_true",
        help="Skip runtime list_models probe",
    )

    args = parser.parse_args(argv)
    command = args.command or "serve"

    if command == "serve":
        from .server import cli as server_cli

        server_cli()
        return 0

    if command == "init":
        client = args.client
        output = Path(args.output).expanduser()
        ai_protocol_path = args.ai_protocol_path
        try:
            write_init_config(
                output=output,
                client=client,
                ai_protocol_path=ai_protocol_path,
                force=bool(args.force),
            )
        except FileExistsError as exc:
            print(str(exc))
            print("Use --force to overwrite.")
            return 1
        print(f"Generated config template: {output}")
        return 0

    if command == "doctor":
        result = run_doctor_checks(include_runtime_probe=not bool(args.no_runtime_probe))
        if bool(args.json):
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_human_doctor_result(result)
        return 0 if result["healthy"] else 1

    parser.print_help()
    return 1


__all__ = ["main", "run_doctor_checks", "write_init_config"]
