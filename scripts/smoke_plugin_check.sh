#!/usr/bin/env bash
# Smoke checks for plugin-market packaging and CLI readiness.
# 插件市场封装与 CLI 可用性的冒烟检查脚本。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MANIFEST="$PROJECT_DIR/packaging/plugin-market/manifest.json"
TMP_CONFIG="$(mktemp)"

echo "[1/4] check manifest exists"
test -f "$MANIFEST"
echo "ok: $MANIFEST"

echo "[2/4] run doctor json (skip runtime probe for speed)"
python3 -m spiderswitch doctor --json --no-runtime-probe >/dev/null
echo "ok: doctor command available"

echo "[3/4] generate config template"
python3 -m spiderswitch init --client cursor --output "$TMP_CONFIG" --force >/dev/null
test -f "$TMP_CONFIG"
echo "ok: init command generated template"

echo "[4/4] validate manifest json parse"
python3 - <<'PY' "$MANIFEST"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
required = ["id", "name", "version", "entrypoint", "install", "healthcheck", "configuration"]
missing = [key for key in required if key not in payload]
if missing:
    raise SystemExit(f"missing manifest fields: {missing}")
print("ok: manifest fields valid")
PY

rm -f "$TMP_CONFIG"
echo ""
echo "[spiderswitch] smoke plugin checks passed."
