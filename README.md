# MCP Model Switcher for ai-lib Ecosystem

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-green.svg)](LICENSE)

MCP (Model Context Protocol) server that enables agents to dynamically switch AI models from the [ai-lib ecosystem](https://github.com/hiddenpath/ai-lib-python).

## Features

- **Protocol-Driven**: All model configurations loaded from ai-protocol manifests (ARCH-001)
- **Multi-Provider Support**: Switch between OpenAI, Anthropic, Google, DeepSeek, and more
- **Runtime-Agnostic**: Uses ai-lib-python SDK for unified model interaction
- **MCP-Compliant**: Implements standard MCP tools over stdio transport
- **Capability Discovery**: Query available models and their capabilities

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourorg/ai-mcp-model-switcher.git
cd ai-mcp-model-switcher

# Install dependencies
pip install -e .
```

### Environment Setup

Set up your API keys:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

### Configuration

Add to your MCP client configuration (e.g., Cursor, Claude Desktop):

```json
{
  "mcpServers": {
    "ai-model-switcher": {
      "command": "python",
      "args": ["-m", "ai_mcp_model_switcher.server"],
      "env": {
        "AI_PROTOCOL_PATH": "/path/to/ai-protocol"
      }
    }
  }
}
```

### Usage

In your agent, call MCP tools:

```python
# List available models
models = await mcp_client.call_tool("list_models", {})

# Switch to Claude 3.5 Sonnet
await mcp_client.call_tool(
    "switch_model",
    {"model": "anthropic/claude-3-5-sonnet"}
)

# Check current status
status = await mcp_client.call_tool("get_status", {})
```

## Available MCP Tools

### 1. switch_model

Switches to a different AI model/provider.

**Parameters:**
- `model` (string, required): Model identifier (e.g., `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`)
- `api_key` (string, optional): Explicit API key (overrides environment variable)
- `base_url` (string, optional): Custom base URL for testing/mock

**Returns:**
```json
{
  "status": "success",
  "current_provider": "anthropic",
  "current_model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"]
}
```

### 2. list_models

Lists all available models from registered providers.

**Parameters:**
- `filter_provider` (string, optional): Filter by provider ID
- `filter_capability` (string, optional): Filter by capability (`streaming`, `tools`, `vision`, `embeddings`)

**Returns:**
```json
{
  "models": [
    {
      "id": "openai/gpt-4o",
      "provider": "openai",
      "capabilities": ["streaming", "tools", "vision"]
    },
    {
      "id": "anthropic/claude-3-5-sonnet",
      "provider": "anthropic",
      "capabilities": ["streaming", "tools", "vision"]
    }
  ]
}
```

### 3. get_status

Gets current model status and configuration.

**Returns:**
```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"],
  "is_configured": true
}
```

## Architecture

```
ai-mcp-model-switcher/
├── src/
│   ├── server.py           # MCP server main entry point
│   ├── tools/              # MCP tool implementations
│   │   ├── switch.py       # switch_model tool
│   │   ├── list.py         # list_models tool
│   │   └── status.py       # get_status tool
│   ├── runtime/            # Runtime abstraction layer
│   │   ├── base.py         # Base runtime interface
│   │   ├── python_runtime.py  # ai-lib-python implementation
│   │   └── loader.py       # ProtocolLoader wrapper
│   └── state.py            # State management
├── tests/                  # Test suite
└── pyproject.toml          # Project configuration
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/ai_mcp_model_switcher
```

### Testing with Mock Server

Use [ai-protocol-mock](https://github.com/hiddenpath/ai-protocol-mock):

```bash
# Start mock server
docker-compose up -d ai-protocol-mock

# Run with mock
MOCK_HTTP_URL=http://localhost:4010 python -m ai_mcp_model_switcher.server
```

### Code Style

```bash
# Format code
ruff format src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## Protocol-Driven Design (ARCH-001)

This server follows the ai-lib design principle:

> **一切逻辑皆算子，一切配置皆协议**

All provider configurations are loaded from ai-protocol manifests. No provider-specific logic is hardcoded. Adding a new provider requires only a manifest file in ai-protocol.

## Related Projects

- [ai-protocol](https://github.com/hiddenpath/ai-protocol) - Protocol specification
- [ai-lib-python](https://github.com/hiddenpath/ai-lib-python) - Python runtime SDK
- [ai-lib-rust](https://github.com/hiddenpath/ai-lib-rust) - Rust runtime SDK
- [ai-lib-ts](https://github.com/hiddenpath/ai-lib-ts) - TypeScript runtime SDK

## License

This project is licensed under either of:
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT License ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

## Contributing

Contributions are welcome! Please ensure:
1. Code follows PEP 8 and passes `ruff check`
2. Type hints pass `mypy --strict`
3. Tests are included for new features
4. Documentation is updated

---

**ai-mcp-model-switcher** - Where MCP meets ai-lib. 🤖🔀
