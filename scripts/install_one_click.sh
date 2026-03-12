#!/usr/bin/env bash
# One-click installer for spiderswitch plugin-market usage.
# spiderswitch 一键安装脚本（插件市场场景）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SPIDERSWITCH_HOME="${SPIDERSWITCH_HOME:-$HOME/.spiderswitch}"
VENV_DIR="$SPIDERSWITCH_HOME/venv"
BIN_DIR="$HOME/.local/bin"
INSTALL_SOURCE="${SPIDERSWITCH_INSTALL_SOURCE:-$PROJECT_DIR}"

echo "[spiderswitch] home=$SPIDERSWITCH_HOME"
echo "[spiderswitch] creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "[spiderswitch] upgrading pip..."
"$VENV_DIR/bin/python" -m pip install -U pip

echo "[spiderswitch] installing from source: $INSTALL_SOURCE"
"$VENV_DIR/bin/pip" install "$INSTALL_SOURCE"

mkdir -p "$BIN_DIR"
ln -sf "$VENV_DIR/bin/spiderswitch" "$BIN_DIR/spiderswitch"

echo "[spiderswitch] installation complete."
echo "[spiderswitch] linked command: $BIN_DIR/spiderswitch"
echo "[spiderswitch] running basic doctor..."
"$VENV_DIR/bin/spiderswitch" doctor --json --no-runtime-probe || true

echo ""
echo "Next:"
echo "1) Add $BIN_DIR to PATH if needed."
echo "2) Run: spiderswitch init --client cursor --output ~/.cursor/mcp.spiderswitch.json --force"
echo "3) Configure AI_PROTOCOL_PATH and provider API keys."
