# ai-lib生态系统的MCP模型切换器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-green.svg)](LICENSE)

MCP（Model Context Protocol）服务器，使Agent能够从[ai-lib生态系统](https://github.com/hiddenpath/ai-lib-python)动态切换AI模型。

## 功能特性

- **协议驱动**：所有模型配置从ai-protocol manifests加载（ARCH-001）
- **多Provider支持**：支持OpenAI、Anthropic、Google、DeepSeek等
- **运行时无关**：使用ai-lib-python SDK进行统一的模型交互
- **MCP兼容**：通过stdio传输实现标准MCP工具
- **能力发现**：查询可用模型及其能力

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourorg/ai-mcp-model-switcher.git
cd ai-mcp-model-switcher

# 安装依赖
pip install -e .
```

### 环境配置

设置你的API密钥：

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

### 配置

添加到你的MCP客户端配置（如Cursor、Claude Desktop）：

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

### 使用方法

在Agent中调用MCP工具：

```python
# 列出可用模型
models = await mcp_client.call_tool("list_models", {})

# 切换到Claude 3.5 Sonnet
await mcp_client.call_tool(
    "switch_model",
    {"model": "anthropic/claude-3-5-sonnet"}
)

# 检查当前状态
status = await mcp_client.call_tool("get_status", {})
```

## 可用的MCP工具

### 1. switch_model

切换到不同的AI模型/provider。

**参数：**
- `model`（字符串，必填）：模型标识符（如 `openai/gpt-4o`、`anthropic/claude-3-5-sonnet`）
- `api_key`（字符串，可选）：显式API密钥（覆盖环境变量）
- `base_url`（字符串，可选）：用于测试/mock的自定义基础URL

**返回：**
```json
{
  "status": "success",
  "current_provider": "anthropic",
  "current_model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"]
}
```

### 2. list_models

列出所有已注册provider的可用模型。

**参数：**
- `filter_provider`（字符串，可选）：按provider ID过滤
- `filter_capability`（字符串，可选）：按能力过滤（`streaming`、`tools`、`vision`、`embeddings`）

**返回：**
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

获取当前模型状态和配置。

**返回：**
```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"],
  "is_configured": true
}
```

## 架构

```
ai-mcp-model-switcher/
├── src/
│   ├── server.py           # MCP服务器主入口
│   ├── tools/              # MCP工具实现
│   │   ├── switch.py       # switch_model工具
│   │   ├── list.py         # list_models工具
│   │   └── status.py       # get_status工具
│   ├── runtime/            # 运行时抽象层
│   │   ├── base.py         # 基础运行时接口
│   │   ├── python_runtime.py  # ai-lib-python实现
│   │   └── loader.py       # ProtocolLoader封装
│   └── state.py            # 状态管理
├── tests/                  # 测试套件
└── pyproject.toml          # 项目配置
```

## 开发

### 运行测试

```bash
# 安装测试依赖
pip install -e ".[test]"

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src/ai_mcp_model_switcher
```

### 使用Mock服务器测试

使用[ai-protocol-mock](https://github.com/hiddenpath/ai-protocol-mock)：

```bash
# 启动mock服务器
docker-compose up -d ai-protocol-mock

# 使用mock运行
MOCK_HTTP_URL=http://localhost:4010 python -m ai_mcp_model_switcher.server
```

### 代码风格

```bash
# 格式化代码
ruff format src tests

# 代码检查
ruff check src tests

# 类型检查
mypy src
```

## 协议驱动设计（ARCH-001）

本服务器遵循ai-lib设计原则：

> **一切逻辑皆算子，一切配置皆协议**

所有provider配置从ai-protocol manifests加载。没有provider特定的硬编码逻辑。添加新provider只需在ai-protocol中添加manifest文件。

## 相关项目

- [ai-protocol](https://github.com/hiddenpath/ai-protocol) - 协议规范
- [ai-lib-python](https://github.com/hiddenpath/ai-lib-python) - Python运行时SDK
- [ai-lib-rust](https://github.com/hiddenpath/ai-lib-rust) - Rust运行时SDK
- [ai-lib-ts](https://github.com/hiddenpath/ai-lib-ts) - TypeScript运行时SDK

## 许可证

本项目采用以下任一许可证：
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) 或 http://www.apache.org/licenses/LICENSE-2.0)
- MIT License ([LICENSE-MIT](LICENSE-MIT) 或 http://opensource.org/licenses/MIT)

可选其一。

## 贡献

欢迎贡献！请确保：
1. 代码遵循PEP 8并通过`ruff check`
2. 类型提示通过`mypy --strict`
3. 包含新功能的测试
4. 更新文档

---

**ai-mcp-model-switcher** - Where MCP meets ai-lib. 🤖🔀
