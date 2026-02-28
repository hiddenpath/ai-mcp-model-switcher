#!/bin/bash
# Installation script for ai-mcp-model-switcher
# ai-mcp-model-switcher 安装脚本

set -e

echo "========================================="
echo "Installing ai-mcp-model-switcher"
echo "========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Detected Python $PYTHON_VERSION"

if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 10 ]]; then
    echo "Error: Python 3.10 or higher is required"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install in editable mode
echo "Installing ai-mcp-model-switcher in editable mode..."
pip3 install -e .

# Check ai-lib-python is available
echo ""
echo "========================================="
echo "Verification"
echo "========================================="
python3 -c "import ai_lib_python; print(f'ai-lib-python version: {ai_lib_python.__version__}')"

# Check module can be imported
python3 -c "from ai_mcp_model_switcher import main; print('MCP server module imported successfully')"

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "To run the MCP server:"
echo "  python -m ai_mcp_model_switcher.server"
echo ""
echo "To run with mock server for testing:"
echo "  MOCK_HTTP_URL=http://localhost:4010 python -m ai_mcp_model_switcher.server"
echo ""
echo "Don't forget to set your API keys:"
echo "  export OPENAI_API_KEY='sk-...'"
echo "  export ANTHROPIC_API_KEY='sk-ant-...'"
echo ""
