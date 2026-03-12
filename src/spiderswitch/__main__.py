# spiderswitch module executable
"""
Module executable wrapper for spiderswitch CLI.
模块执行入口，委托到 spiderswitch CLI。
"""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
