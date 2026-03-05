# Spiderswitch 用户指南

> **面向本地开发者** - 在本地环境中安装和配置 spiderswitch

> **注意**: 如果您没有本地环境，请查看 [PRODUCT_GUIDE.md](./PRODUCT_GUIDE.md)

---

## 前言

本文档面向希望在本地机器上安装和配置 spiderswitch 的开发者和技术用户。

**适合以下场景**:
- 您有自己的开发环境
- 您需要测试或开发 AI 应用
- 您希望完全控制 MCP 服务器的配置

**如果不符合以上条件**，请查看 [PRODUCT_GUIDE.md](./PRODUCT_GUIDE.md) 了解如何在产品环境中使用。

---

## 什么是 Spiderswitch？

**spiderswitch** 是一个 AI 模型切换工具，让您可以在不同的 AI 模型之间轻松切换（如从 GPT-4 切换到 Claude，或从 Claude 切换到 DeepSeek）。

它通过 **MCP (Model Context Protocol)** 协议工作，可以与 MCP-enabled 的应用（如 Claude Desktop、Cursor、OpenCode 等）集成。

---

## 前置条件

开始之前，请确保您有：

| 项目 | 说明 |
|------|------|
| Python 3.10+ | 运行环境 |
| API Keys | 至少一个 AI 服务的 API Key |
| MCP 客户端 | MCP-enabled 应用（如 Claude Desktop、Cursor 等） |
| ai-protocol | 可选，如果不指定则使用默认在线版本 |

---

## 安装步骤

### 方法 1: 从 GitHub 安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/hiddenpath/spiderswitch.git
cd spiderswitch

# 2. 安装
pip install -e .

# 3. 验证安装
python -c "import spiderswitch; print('✓ 安装成功！')"
```

### 方法 2: 从 PyPI 安装

```bash
pip install spiderswitch

# 验证安装
python -c "import spiderswitch; print('✓ 安装成功！')"
```

---

## 配置 API Keys

spiderswitch 需要您的 AI 服务 API Key 才能正常工作。

### 支持的 AI 服务

| AI 服务 | 环境变量 | 获取地址 |
|---------|----------|---------|
| OpenAI (GPT-4, etc.) | `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | [console.anthropic.com/](https://console.anthropic.com/) |
| Google (Gemini) | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| DeepSeek | `DEEPSEEK_API_KEY` | [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) |
| Cohere | `COHERE_API_KEY` | [dashboard.cohere.com/](https://dashboard.cohere.com/) |
| Mistral | `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/) |

### 配置方法

**Linux / macOS (bash/zsh)**

编辑 `~/.bashrc` 或 `~/.zshrc`，添加：

```bash
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
export DEEPSEEK_API_KEY="sk-your-deepseek-key"
```

然后运行：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

**Windows (PowerShell)**

```powershell
# 临时（仅当前会话）
$env:OPENAI_API_KEY = "sk-your-key"

# 永久（需要管理员权限）
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-key", "User")
```

### 安全提示

⚠️ **不要**：
- ❌ 在代码中硬编码 API Key
- ❌ 通过工具参数传递 API Key
- ❌ 将 API Key 提交到代码仓库

✅ **应该**：
- ✅ 使用环境变量
- ✅ 使用密钥管理工具
- ✅ 定期更换 API Key

---

## 配置 MCP 客户端

spiderswitch 是一个通用的 MCP 服务器，可与任何 MCP 兼容的客户端配合使用。

### 通用配置模板

所有 MCP 客户端都使用相同的配置格式：

```json
{
  "mcpServers": {
    "spiderswitch": {
      "command": "python",
      "args": ["-m", "spiderswitch.server"]
    }
  }
}
```

指定自定义 ai-protocol 路径：

```json
{
  "mcpServers": {
    "spiderswitch": {
      "command": "python",
      "args": ["-m", "spiderswitch.server"],
      "env": {
        "AI_PROTOCOL_PATH": "/path/to/ai-protocol"
      }
    }
  }
}
```

### 客户端特定配置

不同 MCP 客户端的配置文件位置不同：

#### Claude Desktop

| 系统 | 配置文件路径 |
|------|------------| 
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**配置步骤**:
1. 找到并编辑配置文件（如果不存在则创建）
2. 添加上述通用配置模板内容
3. 保存文件并重启 Claude Desktop

#### Cursor

| 系统 | 配置文件路径 |
|------|------------|
| macOS | `~/.cursor/mcp.json` |
| Windows | `%USERPROFILE%\\.cursor\\mcp.json` (recommended), fallback `%APPDATA%\\Cursor\\mcp.json` |
| Linux | `~/.config/cursor/mcp.json` |

**配置步骤**:
1. 打开 Cursor 设置 (`Ctrl/Cmd + ,`)
2. 搜索 "MCP" 确认 MCP 功能已启用
3. 编辑配置文件并添加上述通用配置模板内容
4. 重启 Cursor

**注**: Cursor 也支持项目级配置。可以在项目根目录创建 `.cursor/mcp.json`。
在 Windows 上如果两个用户级路径都存在，优先使用 `%USERPROFILE%\\.cursor\\mcp.json`。

#### OpenCode / OpenCode 兼容客户端

| 系统 | 配置文件路径 |
|------|------------|
| macOS/Linux | `~/.config/opencode/mcp.json` |
| Windows | `%APPDATA%\opencode\mcp.json` |

**配置步骤**:
1. 确认配置目录存在（如需要则创建）
2. 编辑或创建 `mcp.json` 文件
3. 添加上述通用配置模板内容
4. 重启客户端

#### Windsurf

| 系统 | 配置文件路径 |
|------|------------|
| macOS | `~/.windsurf/mcp.json` |
| Windows | `%APPDATA%\Windsurf/mcp.json` |
| Linux | `~/.config/windsurf/mcp.json` |

#### Zed

Zed 通过 `settings.json` 配置 MCP 服务器：

| 系统 | 配置文件路径 |
|------|------------|
| macOS/Linux | `~/.config/zed/settings.json` |
| Windows | `%APPDATA%\Zed\settings.json` |

**配置示例**:
```json
{
  "mcp_servers": {
    "spiderswitch": {
      "command": "python",
      "args": ["-m", "spiderswitch.server"]
    }
  }
}
```

### 配置验证

配置完成后，通过以下步骤验证：

1. 重启您的 MCP 客户端
2. 在客户端中调用 `list_models` 工具
3. 如果返回了可用模型列表，说明配置成功

### 常见问题

**Q: 配置文件不存在怎么办？**

手动创建目录和文件：

```bash
# macOS/Linux (Claude Desktop)
mkdir -p ~/.config/Claude
touch ~/.config/Claude/claude_desktop_config.json

# macOS/Linux (Cursor)
mkdir -p ~/.cursor
touch ~/.cursor/mcp.json

# macOS/Linux (OpenCode)
mkdir -p ~/.config/opencode
touch ~/.config/opencode/mcp.json
```

**Q: 环境变量不生效？**

MCP 服务器从客户端进程继承环境变量。确保：
1. 环境变量在**启动客户端之前**设置
2. 或在配置文件的 `env` 字段中设置

---

## 使用方法

### 可用的 MCP 工具

| 工具名称 | 功能 |
|---------|------|
| `list_models` | 查看所有可用的 AI 模型 |
| `switch_model` | 切换到指定的模型 |
| `get_status` | 查看当前使用的模型 |
| `exit_switcher` | 重置 switcher 状态 |

### 查看可用模型

在 MCP-enabled 应用中调用 `list_models`：

```bash
# 列出所有模型
```

**返回示例**:

```json
{
  "count": 188,
  "models": [
    {
      "id": "openai/gpt-4o",
      "provider": "openai",
      "capabilities": ["streaming", "tools", "vision"],
      "api_key_status": {
        "provider": "openai",
        "has_api_key": true,
        "configured_env_vars": ["OPENAI_API_KEY"]
      }
    }
  ]
}
```

### 只列出有 API Key 的模型

使用新增的 `require_api_key` 参数：

```json
{
  "name": "list_models",
  "arguments": {
    "require_api_key": true
  }
}
```

这将只返回您已配置 API Key 的模型，减少列表中的噪音。

### 按能力过滤模型

```json
{
  "name": "list_models",
  "arguments": {
    "filter_capability": "vision"
  }
}
```

支持的能力：
- `streaming` - 流式输出
- `tools` - 工具调用
- `vision` - 视觉输入
- `embeddings` - 向量嵌入
- `audio` - 语音输入/输出

### 切换模型

使用 `provider/model-name` 格式切换到指定模型：

```bash
# 切换到 Claude 3.5 Sonnet
```

**支持的主要模型标识符**:

| 模型 | 标识符 |
|------|--------|
| GPT-4o | `openai/gpt-4o` |
| GPT-4 Turbo | `openai/gpt-4-turbo` |
| Claude 3.5 Sonnet | `anthropic/claude-3-5-sonnet` |
| Claude 3 Opus | `anthropic/claude-3-opus` |
| Gemini Pro | `google/gemini-pro` |
| DeepSeek Chat | `deepseek/deepseek-chat` |

### 查看当前状态

```bash
# 查看当前模型状态
```

**返回示例**:

```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"],
  "is_configured": true,
  "connection_epoch": 3,
  "last_switched_at": "2026-03-05T04:00:00+00:00"
}
```

### 重置状态

如需重置 switcher：

```bash
# 退出模型 switcher
```

---

## 高级配置

### 禁用启动时的协议自动同步

默认情况下，spiderswitch 会在启动时尝试从官方 GitHub 仓库同步最新的 ai-protocol manifest 文件。如需禁用：

```bash
export SPIDERSWITCH_SYNC_DIST=0
```

### 使用自定义协议源

指定自定义的 ai-protocol manifest 源：

```bash
export AI_PROTOCOL_DIST_BASE_URL="https://your-mirror.com/dist"
export AI_PROTOCOL_DIST_API_BASE_URL="https://your-mirror.com/api"
```

### 日志级别控制

通过环境变量控制日志输出：

```bash
export PYTHONUNBUFFERED=1
export SPIDERSWITCH_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

---

## 故障排查

### 切换模型失败，提示"Missing API Key"

**原因**: 对应 AI 服务的 API Key 未配置。

**解决方法**:
1. 确认正确的环境变量已设置
2. 重启 MCP 客户端使环境变量生效
3. 重新尝试切换模型

**错误示例**:

```json
{
  "error": "Missing API key for provider: openai",
  "details": {
    "provider": "openai",
    "expected_env_vars": ["OPENAI_API_KEY"],
    "hint": "Set OPENAI_API_KEY environment variable in the MCP server process environment before calling switch_model."
  }
}
```

### 连接超时或无法访问

**原因**: 部分 AI 服务在您的网络区域可能需要代理访问。

**解决方法**:
设置代理环境变量：

```bash
export HTTPS_PROXY="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
```

### 如何验证配置是否正确？

1. 在 MCP 客户端中调用 `get_status`
2. 检查返回的 `is_configured` 字段
3. 如果为 `true`，说明至少有一个模型已配置

### 验证工具是否工作

创建测试脚本 `test_spiderswitch.py`:

```python
import asyncio
import sys
sys.path.insert(0, '/path/to/spiderswitch/src')

from spiderswitch.server import create_app

async def test():
    app = create_app()
    print("✓ Spiderswitch MCP 服务器创建成功")
    print("✓ 配置加载正常")

asyncio.run(test())
```

运行测试：

```bash
python test_spiderswitch.py
```

---

## 相关链接

### 项目

- **GitHub 仓库**: [spiderswitch](https://github.com/hiddenpath/spiderswitch)
- **问题反馈**: [GitHub Issues](https://github.com/hiddenpath/spiderswitch/issues)

### 生态项目

- [ai-lib-python](https://github.com/hiddenpath/ai-lib-python) - Python 运行时 SDK
- [ai-protocol](https://github.com/hiddenpath/ai-protocol) - 协议规范
- [ai-lib-rust](https://github.com/hiddenpath/ai-lib-rust) - Rust 运行时
- [ai-lib-ts](https://github.com/hiddenpath/ai-lib-ts) - TypeScript 运行时

### 文档

- [PRODUCT_GUIDE.md](./PRODUCT_GUIDE.md) - 产品使用指南（无本地环境）
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - 使用示例
- [README.md](./README.md) - 项目概览

---

## 许可证

本项目采用 MIT 或 Apache-2.0 双重许可，您可以选择其中之一。

---

**spiderswitch** — 在本地环境中自由模型切换 🤖🔀
