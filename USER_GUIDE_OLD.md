# spiderswitch User Guide

> Installation and usage guide for end users

---

## What is This?

**spiderswitch** is an AI model switching tool that lets you easily switch between different AI models—like from GPT-4 to Claude, or from Claude to DeepSeek.

It works through the **MCP (Model Context Protocol)** and can be used with MCP-enabled AI applications (like Claude Desktop, Cursor, etc.).

---

## Prerequisites

Before you begin, make sure you have:

| Item | Description |
|------|-------------|
| Python 3.10+ | Runtime environment |
| API Keys | At least one AI service API key |
| MCP Client | An MCP-enabled application like Claude Desktop, Cursor, etc. |

---

## Step 1: Installation

### Method 1: Install from GitHub (Recommended)

Open a terminal and run:

```bash
# 1. Clone the repository
git clone https://github.com/hiddenpath/spiderswitch.git

# 2. Enter the project directory
cd spiderswitch

# 3. Install
pip install -e .
```

### Method 2: Install from PyPI

```bash
pip install spiderswitch
```

After installation, verify success:

```bash
python -c "import spiderswitch; print('Installation successful!')"
```

---

## Step 2: Configure API Keys

spiderswitch requires your AI service API keys to function.

### Supported AI Services

| AI Service | Environment Variable | How to Get |
|------------|---------------------|------------|
| OpenAI (GPT-4, etc.) | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |
| Google (Gemini) | `GOOGLE_API_KEY` or `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| DeepSeek | `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| Cohere | `COHERE_API_KEY` | [dashboard.cohere.com](https://dashboard.cohere.com/) |
| Mistral | `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/) |

### Configuration Method

**Linux / macOS (bash/zsh)**

Edit `~/.bashrc` or `~/.zshrc`, add:

```bash
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
```

Then run:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

**Windows (PowerShell)**

```powershell
# Temporary (current session only)
$env:OPENAI_API_KEY = "sk-your-key"

# Permanent (requires admin privileges)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-key", "User")
```

### Security Notes

- **Do not** hardcode API keys in code
- **Do not** pass keys through tool parameters
- Use environment variables in production

---

## Step 3: Configure MCP Client

spiderswitch is a universal MCP server that works with any MCP-compatible client.

### Universal Configuration Template

All MCP clients use the same configuration format:

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

To specify a custom ai-protocol path:

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

### Client-Specific Configuration

Different MCP clients have different configuration file locations. Choose based on your tool:

#### Claude Desktop

| System | Configuration File Path |
|--------|------------------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**Configuration Steps**:
1. Find and edit the configuration file (create if it doesn't exist)
2. Add the universal configuration template content above
3. Save the file and restart Claude Desktop

---

#### Cursor

| System | Configuration File Path |
|--------|------------------------|
| macOS | `~/.cursor/mcp.json` |
| Windows | `%APPDATA%\Cursor\mcp.json` |
| Linux | `~/.config/cursor/mcp.json` |

**Configuration Steps**:
1. Open Cursor settings (`Ctrl/Cmd + ,`)
2. Search for "MCP" to confirm MCP feature is enabled
3. Edit the configuration file and add the universal configuration template content
4. Restart Cursor

**Note**: Cursor also supports project-level configuration. You can create `.cursor/mcp.json` in your project root.

---

#### OpenCode / OpenCode-compatible Clients

| System | Configuration File Path |
|--------|------------------------|
| macOS/Linux | `~/.config/opencode/mcp.json` |
| Windows | `%APPDATA%\opencode\mcp.json` |

**Configuration Steps**:
1. Confirm the configuration directory exists (create if needed)
2. Edit or create the `mcp.json` file
3. Add the universal configuration template content
4. Restart the client

---

#### Windsurf

| System | Configuration File Path |
|--------|------------------------|
| macOS | `~/.windsurf/mcp.json` |
| Windows | `%APPDATA%\Windsurf\mcp.json` |
| Linux | `~/.config/windsurf/mcp.json` |

**Configuration Steps**:
1. Open Windsurf settings
2. Find the MCP configuration section
3. Add the universal configuration template content
4. Save and restart

---

#### Zed

Zed configures MCP servers through `settings.json`:

| System | Configuration File Path |
|--------|------------------------|
| macOS/Linux | `~/.config/zed/settings.json` |
| Windows | `%APPDATA%\Zed\settings.json` |

**Configuration Example**:
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

#### Other MCP Clients

If you're using another MCP-compatible client:

1. Check the client's documentation to find the MCP server configuration location
2. Use the universal configuration template above
3. Note that the JSON structure might differ slightly (e.g., `mcp_servers` vs `mcpServers`)

---

### Configuration Verification

After configuration, verify by:

1. Restart your MCP client
2. Try calling the `list_models` tool in the client
3. If a list of available models is returned, configuration was successful

### Common Issues

**Q: What if the configuration file doesn't exist?**

Create the directory and file manually:
```bash
# macOS/Linux (Claude Desktop)
mkdir -p ~/.config/Claude
touch ~/.config/Claude/claude_desktop_config.json

# macOS/Linux (Cursor)
mkdir -p ~/.cursor
touch ~/.cursor/mcp.json
```

**Q: Environment variables not working?**

MCP servers inherit environment variables from the client process. Ensure:
1. Environment variables are set **before** starting the client
2. Or set them in the configuration file's `env` field

---

## Step 4: Usage

### Available Tools

| Tool Name | Function |
|-----------|----------|
| `list_models` | View all available AI models |
| `switch_model` | Switch to a specific model |
| `get_status` | View current model in use |
| `exit_switcher` | Reset switcher state |

### View Available Models

In an MCP-enabled application, call `list_models`:

```
List all available models
```

Example response:

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

### Switch Model

Switch to a specific model using the format `provider/model-name`:

```
Switch to Claude 3.5 Sonnet
```

Or use the full identifier:

```
switch_model: anthropic/claude-3-5-sonnet
```

Supported model format examples:

| Model | Identifier |
|-------|------------|
| GPT-4o | `openai/gpt-4o` |
| GPT-4 Turbo | `openai/gpt-4-turbo` |
| Claude 3.5 Sonnet | `anthropic/claude-3-5-sonnet` |
| Claude 3 Opus | `anthropic/claude-3-opus` |
| Gemini Pro | `google/gemini-pro` |
| DeepSeek Chat | `deepseek/deepseek-chat` |

### Check Current Status

```
Check current model status
```

Example response:

```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet",
  "capabilities": ["streaming", "tools", "vision"],
  "is_configured": true
}
```

### Reset State

If you need to reset the switcher:

```
Exit model switcher
```

---

## FAQ

### Q: Switch model fails, missing API Key error

**Cause**: API key for the corresponding service is not configured.

**Solution**:

1. Confirm the correct environment variable is set
2. Restart the MCP client for environment variables to take effect
3. Try switching again

Example error response:

```json
{
  "error": "Missing API key for provider: openai",
  "hint": "Set OPENAI_API_KEY environment variable"
}
```

### Q: Connection timeout or inaccessible

**Cause**: Some AI services may require proxy access.

**Solution**:

Set proxy environment variables:

```bash
export HTTPS_PROXY="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
```

### Q: How to see which models have API keys configured?

Call `list_models`, the `api_key_status` field in the response shows:

```json
{
  "api_key_status": {
    "has_api_key": true,
    "expected_env_vars": ["OPENAI_API_KEY"],
    "configured_env_vars": ["OPENAI_API_KEY"]
  }
}
```

### Q: How to filter models by specific capability?

```
List models that support vision
```

Or use parameters:

```json
{
  "filter_capability": "vision"
}
```

---

## Advanced Configuration

### Disable Auto Sync

To disable protocol file sync at startup:

```bash
export SPIDERSWITCH_SYNC_DIST=0
```

### Custom Protocol Source

```bash
export AI_PROTOCOL_DIST_BASE_URL="https://your-mirror.com/dist"
```

---

## Related Links

- [ai-lib Ecosystem](https://github.com/hiddenpath/ai-lib-python)
- [ai-protocol Specification](https://github.com/hiddenpath/ai-protocol)
- [Issue Tracker](https://github.com/hiddenpath/spiderswitch/issues)

---

## License

This project is dual-licensed under MIT or Apache-2.0, at your option.

---

**spiderswitch** — Making AI model switching simple 🤖🔀
