# spiderswitch 用户指南

> 面向普通用户的安装和使用指南

---

## 这是什么？

**spiderswitch** 是一个 AI 模型切换工具，让你能在不同 AI 模型之间轻松切换——比如从 GPT-4 切换到 Claude，或从 Claude 切换到 DeepSeek。

它通过 **MCP（Model Context Protocol）** 协议工作，可以与支持 MCP 的 AI 应用（如 Claude Desktop、Cursor 等）配合使用。

---

## 准备工作

在开始之前，请确保你有：

| 项目 | 说明 |
|------|------|
| Python 3.10+ | 运行环境 |
| API 密钥 | 至少一个 AI 服务的 API Key |
| MCP 客户端 | 如 Claude Desktop、Cursor 等支持 MCP 的应用 |

---

## 第一步：安装

### 方法一：从 GitHub 安装（推荐）

打开终端，执行以下命令：

```bash
# 1. 克隆项目
git clone https://github.com/hiddenpath/spiderswitch.git

# 2. 进入项目目录
cd spiderswitch

# 3. 安装
pip install -e .
```

### 方法二：从 PyPI 安装

```bash
pip install spiderswitch
```

安装完成后，验证是否成功：

```bash
python -c "import spiderswitch; print('安装成功！')"
```

---

## 第二步：配置 API 密钥

spiderswitch 需要你的 AI 服务 API 密钥才能工作。

### 支持的 AI 服务

| AI 服务 | 环境变量名称 | 获取方式 |
|---------|-------------|---------|
| OpenAI (GPT-4 等) | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |
| Google (Gemini) | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| DeepSeek | `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| Cohere | `COHERE_API_KEY` | [dashboard.cohere.com](https://dashboard.cohere.com/) |
| Mistral | `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/) |

### 配置方法

**Linux / macOS（bash/zsh）**

编辑 `~/.bashrc` 或 `~/.zshrc`，添加：

```bash
export OPENAI_API_KEY="sk-你的密钥"
export ANTHROPIC_API_KEY="sk-ant-你的密钥"
```

然后执行：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

**Windows（PowerShell）**

```powershell
# 临时设置（仅当前会话有效）
$env:OPENAI_API_KEY = "sk-你的密钥"

# 永久设置（需要管理员权限）
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-你的密钥", "User")
```

### 安全提示

- **不要**在代码中硬编码 API 密钥
- **不要**通过工具参数传递密钥
- 生产环境请使用环境变量

---

## 第三步：配置 MCP 客户端

spiderswitch 是一个通用 MCP 服务器，可以与任何支持 MCP 协议的客户端配合使用。

### 通用配置模板

所有 MCP 客户端的配置格式相同：

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

如需指定 ai-protocol 路径：

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

---

### 各客户端配置方法

不同 MCP 客户端的配置文件位置不同，请根据你使用的工具选择：

#### Claude Desktop

| 系统 | 配置文件路径 |
|------|-------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\\Claude\\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**配置步骤**：
1. 找到并编辑配置文件（如不存在则创建）
2. 添加上述通用配置模板内容
3. 保存文件，重启 Claude Desktop

---

#### Cursor

| 系统 | 配置文件路径 |
|------|-------------|
| macOS | `~/.cursor/mcp.json` |
| Windows | `%USERPROFILE%\\.cursor\\mcp.json`（推荐），回退 `%APPDATA%\\Cursor\\mcp.json` |
| Linux | `~/.config/cursor/mcp.json` |

**配置步骤**：
1. 打开 Cursor 设置（`Ctrl/Cmd + ,`）
2. 搜索 "MCP" 确认 MCP 功能已启用
3. 编辑配置文件，添加通用配置模板内容
4. 重启 Cursor

**注意**：Cursor 也支持项目级配置，可在项目根目录创建 `.cursor/mcp.json`。在 Windows 上如果两个用户级路径都存在，优先使用 `%USERPROFILE%\\.cursor\\mcp.json`。

---

#### OpenCode / OpenCode-compatible Clients

| 系统 | 配置文件路径 |
|------|-------------|
| macOS/Linux | `~/.config/opencode/mcp.json` |
| Windows | `%APPDATA%\\opencode\\mcp.json` |

**配置步骤**：
1. 确认配置目录存在（如不存在则创建）
2. 编辑或创建 `mcp.json` 文件
3. 添加通用配置模板内容
4. 重启客户端

---

#### Windsurf

| 系统 | 配置文件路径 |
|------|-------------|
| macOS | `~/.windsurf/mcp.json` |
| Windows | `%APPDATA%\\Windsurf\\mcp.json` |
| Linux | `~/.config/windsurf/mcp.json` |

**配置步骤**：
1. 打开 Windsurf 设置
2. 找到 MCP 配置部分
3. 添加通用配置模板内容
4. 保存并重启

---

#### Zed

Zed 通过 `settings.json` 配置 MCP 服务器：

| 系统 | 配置文件路径 |
|------|-------------|
| macOS/Linux | `~/.config/zed/settings.json` |
| Windows | `%APPDATA%\\Zed\\settings.json` |

**配置示例**：
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

---

#### 其他 MCP 客户端

如果你使用的是其他支持 MCP 的客户端：

1. 查阅该客户端的文档，找到 MCP 服务器配置位置
2. 使用上述通用配置模板
3. 注意配置文件的 JSON 结构可能略有不同（如 `mcp_servers` vs `mcpServers`）

---

### 配置验证

配置完成后，可通过以下方式验证：

1. 重启 MCP 客户端
2. 在客户端中尝试调用 `list_models` 工具
3. 如返回可用模型列表，说明配置成功

### 常见问题

**Q: 配置文件不存在怎么办？**

手动创建目录和文件即可。例如：
```bash
# macOS/Linux (Claude Desktop)
mkdir -p ~/.config/Claude
touch ~/.config/Claude/claude_desktop_config.json

# macOS/Linux (Cursor)
mkdir -p ~/.cursor
touch ~/.cursor/mcp.json
```

**Q: 环境变量不生效？**

MCP 服务器继承客户端进程的环境变量。确保：
1. 环境变量在启动客户端**之前**设置
2. 或在配置文件的 `env` 字段中设置

---

## 第四步：使用

### 可用功能一览

| 工具名称 | 功能 |
|---------|------|
| `list_models` | 查看所有可用的 AI 模型 |
| `switch_model` | 切换到指定模型 |
| `get_status` | 查看当前使用的模型 |
| `exit_switcher` | 重置切换器状态 |

### 查看可用模型

在支持 MCP 的应用中，调用 `list_models`：

```
列出所有可用的模型
```

返回示例：

```json
{
  "models": [
    {
      "id": "openai/gpt-4o",
      "provider": "openai",
      "capabilities": ["streaming", "tools", "vision"],
      "api_key_status": {
        "has_api_key": true
      }
    },
    {
      "id": "anthropic/claude-3-5-sonnet",
      "provider": "anthropic",
      "capabilities": ["streaming", "tools", "vision"]
    }
  ]
}
```

### 切换模型

切换到特定模型，格式为 `提供者/模型名`：

```
切换到 Claude 3.5 Sonnet
```

或使用完整标识符：

```
switch_model: anthropic/claude-3-5-sonnet
```

支持的模型格式示例：

| 模型 | 标识符 |
|------|-------|
| GPT-4o | `openai/gpt-4o` |
| GPT-4 Turbo | `openai/gpt-4-turbo` |
| Claude 3.5 Sonnet | `anthropic/claude-3-5-sonnet` |
| Claude 3 Opus | `anthropic/claude-3-opus` |
| Gemini Pro | `google/gemini-pro` |
| DeepSeek Chat | `deepseek/deepseek-chat` |

### 查看当前状态

```
查看当前模型状态
```

返回示例：

```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"],
  "is_configured": true
}
```

### 重置状态

如果需要重置切换器：

```
退出模型切换器
```

---

## 常见问题

### Q: 切换模型失败，提示缺少 API Key

**原因**：未配置对应服务的 API 密钥。

**解决方法**：

1. 确认已设置正确的环境变量
2. 重启 MCP 客户端使环境变量生效
3. 再次尝试切换

错误返回示例：

```json
{
  "error": "Missing API key for provider: openai",
  "hint": "Set OPENAI_API_KEY environment variable"
}
```

### Q: 连接超时或无法访问

**原因**：某些 AI 服务可能需要代理访问。

**解决方法**：

设置代理环境变量：

```bash
export HTTPS_PROXY="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
```

### Q: 如何查看哪些模型已配置好 API Key？

调用 `list_models`，返回结果中的 `api_key_status` 字段会显示：

```json
{
  "api_key_status": {
    "has_api_key": true,
    "expected_env_vars": ["OPENAI_API_KEY"],
    "configured_env_vars": ["OPENAI_API_KEY"]
  }
}
```

### Q: 如何过滤特定能力的模型？

```
列出支持视觉功能的模型
```

或使用参数：

```json
{
  "filter_capability": "vision"
}
```

---

## 进阶配置

### 禁用自动同步

如需禁用启动时的协议文件同步：

```bash
export SPIDERSWITCH_SYNC_DIST=0
```

### 自定义协议源

```bash
export AI_PROTOCOL_DIST_BASE_URL="https://your-mirror.com/dist"
```

---

## 相关链接

- [ai-lib 生态](https://github.com/hiddenpath/ai-lib-python)
- [ai-protocol 协议规范](https://github.com/hiddenpath/ai-protocol)
- [问题反馈](https://github.com/hiddenpath/spiderswitch/issues)

---

## 许可证

本项目采用 MIT 或 Apache-2.0 双许可证，可任选其一。

---

**spiderswitch** — 让 AI 模型切换更简单 🤖🔀
