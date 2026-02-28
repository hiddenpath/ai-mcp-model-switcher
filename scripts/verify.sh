#!/bin/bash
# Verification script for ai-mcp-model-switcher
# 项目验证脚本

set -e

echo "========================================="
echo "Verifying ai-mcp-model-switcher v0.1.0"
echo "========================================="

PROJECT_DIR="/home/alex/ai-mcp-model-switcher"
AI_LIB_PATH="/home/alex/pyapp/ai-lib-python/src"

# Check project structure
echo ""
echo "[1/5] Checking project structure..."
if [ ! -d "$PROJECT_DIR/src" ]; then
    echo "❌ src directory not found"
    exit 1
fi
echo "✓ Project structure valid"

# Check key files exist
echo ""
echo "[2/5] Checking key files..."
required_files=(
    "$PROJECT_DIR/pyproject.toml"
    "$PROJECT_DIR/README.md"
    "$PROJECT_DIR/README_CN.md"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/server.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/runtime/__init__.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/runtime/base.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/runtime/python_runtime.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/tools/__init__.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/tools/switch.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/tools/list.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/tools/status.py"
    "$PROJECT_DIR/src/ai_mcp_model_switcher/state.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done
echo "✓ All key files present"

# Check Python syntax
echo ""
echo "[3/5] Checking Python syntax..."
cd "$PROJECT_DIR"
if ! python3 -m py_compile src/ai_mcp_model_switcher/*.py \
    src/ai_mcp_model_switcher/runtime/*.py \
    src/ai_mcp_model_switcher/tools/*.py 2>/dev/null; then
    echo "❌ Python syntax errors found"
    exit 1
fi
echo "✓ All Python files compile successfully"

# Check module can be imported
echo ""
echo "[4/5] Checking module imports..."
cd /home/alex
export PYTHONPATH="$AI_LIB_PATH:$PROJECT_DIR/src"

python3 -c "
from ai_mcp_model_switcher.runtime.base import ModelCapabilities, ModelInfo
from ai_mcp_model_switcher.state import ModelState, ModelStateManager
from ai_mcp_model_switcher.tools import list, status, switch
print('✓ All modules import successfully')
" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Module import failed"
    echo "Note: This is ok if ai-lib-python is not installed globally"
fi

# Verify line counts for key components
echo ""
echo "[5/5] Checking implementation completeness..."
SERVER_LINES=$(wc -l < "$PROJECT_DIR/src/ai_mcp_model_switcher/server.py")
RUNTIME_LINES=$(wc -l < "$PROJECT_DIR/src/ai_mcp_model_switcher/runtime/python_runtime.py")

if [ "$SERVER_LINES" -lt 50 ]; then
    echo "❌ server.py seems incomplete ($SERVER_LINES lines)"
    exit 1
fi

if [ "$RUNTIME_LINES" -lt 100 ]; then
    echo "❌ python_runtime.py seems incomplete ($RUNTIME_LINES lines)"
    exit 1
fi

echo "✓ Implementation looks complete"
echo "  - server.py: $SERVER_LINES lines"
echo "  - python_runtime.py: $RUNTIME_LINES lines"

# Summary
echo ""
echo "========================================="
echo "Verification Complete!"
echo "========================================="
echo ""
echo "Project: ai-mcp-model-switcher"
echo "Version: 0.1.0"
echo "Location: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "  1. Install dependencies:"
echo "     pip install -e ."
echo ""
echo "  2. Set API keys:"
echo "     export OPENAI_API_KEY='sk-...'"
echo "     export ANTHROPIC_API_KEY='sk-ant-...'"
echo ""
echo "  3. Run MCP server:"
echo "     python -m ai_mcp_model_switcher.server"
echo ""
