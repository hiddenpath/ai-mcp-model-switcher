# spiderswitch 产品发布指南

## 概述

本指南说明如何将 spiderswitch MCP 服务器作为产品发布，让用户可以在 Cursor、Claude Desktop、Antigravity 等 agent 中使用。

## 发布状态（已完成）

- 已发布版本：`0.2.0`
- GitHub 仓库：https://github.com/hiddenpath/spiderswitch
- PyPI 页面：https://pypi.org/project/spiderswitch/
- PyPI 版本页：https://pypi.org/project/spiderswitch/0.2.0/

---

## 1. 产品定位

### 目标用户
- **开发者**: 想要在 AI agent 工作流中动态切换 AI 模型
- **企业**: 需要在多个 AI provider 之间灵活切换以优化成本
- **研究者**: 需要测试不同模型的性能

### 核心价值
- 🔀 **动态切换**: 无需重启即可在 OpenAI、Anthropic 等模型间切换
- 🚀 **协议驱动**: 新 provider 只需添加配置文件
- 🔒 **线程安全**: 支持并发请求
- 🎯 **易集成**: 标准 MCP 协议，兼容所有 MCP 客户端

---

## 2. 发布准备

### 2.1 版本管理

当前版本: `0.2.0` (Alpha)

版本策略遵循语义化版本 (SemVer):
- `MAJOR.MINOR.PATCH`
- 0.x.x: 开发版，可能有破坏性变更
- 1.0.0+: 稳定版，遵循 SemVer

### 2.2 依赖管理

更新 `pyproject.toml`，确保所有依赖版本固定：

```toml
[project]
name = "spiderswitch"
version = "0.2.0"
description = "MCP server for dynamic AI model switching in ai-lib ecosystem"

dependencies = [
    "ai-lib-python>=0.7.0,<1.0.0",
    "mcp>=1.0.0,<2.0.0",
    "pydantic>=2.0.0,<3.0.0",
    "pyyaml>=6.0.0,<7.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0,<8.0.0",
    "pytest-asyncio>=0.21.0,<1.0.0",
    "pytest-cov>=4.0.0,<5.0.0",
    "ruff>=0.1.0,<1.0.0",
    "mypy>=1.0.0,<2.0.0",
]
```

### 2.3 完善元数据

更新元数据：

```toml
authors = [
    {name = "ai-lib team", email = "maintainers@ai-lib.org"},
]
keywords = [
    "mcp", "model-context-protocol", "ai-lib", "model-switching",
    "llm", "cursor", "claude-desktop", "ai-agent",
]
```

---

## 3. 发布到 PyPI

### 3.1 创建 PyPI 账号

1. 访问 https://pypi.org/account/register/
2. 创建用户账号
3. 启用 2FA（推荐）

### 3.2 配置发布凭据

```bash
# 安装发布工具
pip install build twine

# 配置 ~/.pypirc
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-xxx...  # PyPI API token

[testpypi]
username = __token__
password = pypi-xxx...  # TestPyPI API token
EOF
```

### 3.3 构建和测试

```bash
# 清理旧的构建
rm -rf build dist src/*.egg-info

# 构建
python -m build

# 检查包内容
twine check dist/*

# 本地测试安装
pip install dist/spiderswitch-0.2.0-py3-none-any.whl --force-reinstall

# 测试导入
python -c "import spiderswitch; print(spiderswitch.__version__)"
```

### 3.4 发布到 TestPyPI（推荐）

```bash
# 发布到测试环境
twine upload --repository testpypi dist/*

# 从 TestPyPI 测试安装
pip install --index-url https://test.pypi.org/simple/ spiderswitch
```

### 3.5 发布到 PyPI

```bash
# 发布到正式环境
twine upload dist/*
```

---

## 4. 安装方式

### 4.1 标准安装（推荐）

```bash
# 从 PyPI 安装
pip install spiderswitch

# 或使用 pipx（推荐，避免依赖冲突）
pipx install spiderswitch
```

### 4.2 开发安装

```bash
git clone https://github.com/hiddenpath/spiderswitch.git
cd spiderswitch
pip install -e .
```

### 4.3 Docker 安装（可选）

创建 `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

# 复制源代码
COPY src/ ./src/

# 设置环境变量
ENV AI_PROTOCOL_PATH=/app/ai-protocol

CMD ["python", "-m", "spiderswitch.server"]
```

发布到 Docker Hub:

```bash
docker build -t spiderswitch:0.2.0 .
docker tag spiderswitch:0.2.0 spiderswitch:latest
docker push spiderswitch:0.2.0
```

---

## 5. 配置指南

### 5.1 Cursor 配置

在 Cursor 中配置 MCP 服务器：

```json
{
  "mcpServers": {
    "spiderswitch": {
      "command": "python",
      "args": ["-m", "spiderswitch.server"],
      "env": {
        "AI_PROTOCOL_PATH": "$HOME/ai-protocol",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "GOOGLE_API_KEY": "${GOOGLE_API_KEY}",
        "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}"
      }
    }
  }
}
```

配置文件位置：
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/mcp.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\mcp.json`

### 5.2 Claude Desktop 配置

```json
{
  "mcpServers": {
    "spiderswitch": {
      "command": "python",
      "args": ["-m", "spiderswitch.server"],
      "env": {
        "AI_PROTOCOL_PATH": "$HOME/ai-protocol",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

配置文件位置：
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 5.3 Antigravity 配置

```json
{
  "mcpServers": {
    "spiderswitch": {
      "command": "python",
      "args": ["-m", "spiderswitch.server"],
      "env": {
        "AI_PROTOCOL_PATH": "$HOME/ai-protocol"
      }
    }
  }
}
```

### 5.4 环境变量

在用户 shell 配置文件（`.bashrc`, `.zshrc`, `.config/fish/config.fish`）中配置：

```bash
# AI Protocol 路径
export AI_PROTOCOL_PATH="$HOME/ai-protocol"

# API Keys
export OPENAI_API_KEY="sk-..."   # 从 https://platform.openai.com/api-keys 获取
export ANTHROPIC_API_KEY="sk-ant-..."  # 从 https://console.anthropic.com/settings/keys 获取
export GOOGLE_API_KEY="..."      # 从 Google Cloud Console 获取
export DEEPSEEK_API_KEY="..."    # 从 DeepSeek 获取

# 日志级别（可选）
export AI_MCP_LOG_LEVEL="INFO"   # DEBUG, INFO, WARNING, ERROR
```

---

## 6. ai-protocol 设置

### 6.1 安装 ai-protocol

```bash
# 克隆 ai-protocol
git clone https://github.com/hiddenpath/ai-protocol.git ~/ai-protocol

# 或下载特定版本
wget https://github.com/hiddenpath/ai-protocol/archive/refs/tags/v1.0.0.tar.gz
tar xzf v1.0.0.tar.gz
mv ai-protocol-1.0.0 ~/ai-protocol
```

### 6.2 验证 ai-protocol

```bash
# 检查清单文件
ls ~/ai-protocol/manifests/
# 应该看到: openai.yaml, anthropic.yaml, google.yaml 等

# 测试加载
python -c "
from ai_lib_python.protocol import ProtocolLoader
loader = ProtocolLoader(ai_protocol_path='~/ai-protocol')
manager = loader.load_all_manifests()
print(f'Loaded {len(list(manager.list_models()))} models')
"
```

---

## 7. 使用示例

### 7.1 在 Cursor 中使用

1. **列出可用模型**:
   ```
   列出所有可用的 AI 模型
   ```

2. **切换到 Claude 3.5 Sonnet**:
   ```
   切换到 anthropic/claude-3-5-sonnet 模型
   ```

3. **按能力过滤模型**:
   ```
   列出所有支持 vision 能力的模型
   ```

4. **检查当前模型**:
   ```
   当前使用的是什么模型？
   ```

### 7.2 在 Claude Desktop 中使用

Claude Desktop 会自动识别 MCP 工具，用户可以请求：

```
请使用 list_models 工具查看所有可用模型
```

```
请使用 switch_model 工具切换到 openai/gpt-4o
```

### 7.3 编程使用（API）

```python
import asyncio
from spiderswitch.server import create_app
from spiderswitch.runtime import PythonRuntime

async def main():
    # 创建运行时
    runtime = PythonRuntime()
    
    # 列出模型
    models = await runtime.list_models()
    print(f"Available models: {len(models)}")
    
    # 切换模型
    model_info = await runtime.switch_model(
        model_id="openai/gpt-4o",
        api_key="sk-...",
    )
    print(f"Switched to: {model_info.id}")
    
    # 清理
    await runtime.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 8. 文档和教程

### 8.1 README.md 结构

```markdown
# spiderswitch

[![PyPI version](https://img.shields.io/pypi/v/spiderswitch.svg)](https://pypi.org/project/spiderswitch/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-green.svg)](LICENSE)

MCP (Model Context Protocol) server that enables agents to dynamically switch AI models.

## Quick Start

### Installation

```bash
pip install spiderswitch
```

### Configuration

#### Cursor
[ detailed config ]

#### Claude Desktop
[ detailed config ]

### Usage

[ usage examples ]

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)
```

### 8.2 创建文档目录

```bash
mkdir -p docs
touch docs/installation.md
touch docs/configuration.md
touch docs/api.md
touch docs/troubleshooting.md
touch docs/custom-providers.md
```

### 8.3 安装指南 (`docs/installation.md`)

```markdown
# Installation Guide

## Requirements

- Python 3.10 or higher
- AI provider API keys
- ai-protocol manifests

## Methods

### Method 1: pip install (Recommended)
[ ... ]

### Method 2: pipx install
[ ... ]

### Method 3: Docker
[ ... ]

### Method 4: Development install
[ ... ]

## Verification

[ ... ]
```

---

## 9. CI/CD 配置

### 9.1 GitHub Actions (`.github/workflows/publish.yml`)

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install build twine pytest pytest-asyncio
          pip install -e .
      - name: Run tests
        run: pytest

  build-and-publish:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

创建标签并触发发布：

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

---

## 10. 测试验证

### 10.1 功能测试清单

- [ ] 所有工具可正常调用
- [ ] 模型列表正确加载
- [ ] 模型切换成功
- [ ] 状态查询正确
- [ ] 错误处理正常
- [ ] 并发请求不冲突

### 10.2 兼容性测试

- [ ] Cursor 兼容
- [ ] Claude Desktop 兼容
- [ ] Antigravity 兼容
- [ ] Python 3.10, 3.11, 3.12

### 10.3 性能测试

```bash
# 安装 locust
pip install locust

# 创建性能测试
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class MCPUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def list_models(self):
        self.client.get("/tools/list")
EOF

# 运行性能测试
locust -f locustfile.py
```

---

## 11. 发布检查清单

### 发布前

- [ ] 版本号更新 (`pyproject.toml`)
- [ ] 更新日志 (`CHANGELOG.md`)
- [ ] 文档完整
- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 许可证文件完整
- [ ] README 更新

### 发布后

- [ ] 在 GitHub 创建 Release
- [ ] 发布公告
- [ ] 更新网站/博客
- [ ] 通知用户
- [ ] 收集反馈

---

## 12. 用户支持

### 12.1 问题报告

引导用户：
1. 查看 [Troubleshooting](docs/troubleshooting.md)
2. 搜索 [Issues](https://github.com/hiddenpath/spiderswitch/issues)
3. 创建新 Issue（使用模板）

### 12.2 Issue 模板

创建 `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
 - OS: [e.g. macOS, Linux, Windows]
 - Python version: [e.g. 3.10, 3.11, 3.12]
 - spiderswitch version: [e.g. 0.2.0]
 - MCP client: [e.g. Cursor, Claude Desktop]

**Additional context**
Add any other context about the problem here.
```

---

## 13. 营销和推广

### 13.1 社交媒体

- Twitter/X:
  ```text
  🚀 Just released spiderswitch v0.2.0!
  Dynamic AI model switching for Cursor & Claude Desktop.
  Switch between OpenAI, Anthropic, and more in seconds!
  #AI #MCP #ModelSwitching #OpenSource
  ```

- Reddit (r/MachineLearning, r/artificial):
  ```text
  [RELEASE] spiderswitch: Dynamic AI Model Switching MCP Server
  [ ... details ... ]
  ```

### 13.2 技术博客

撰写博客文章：
- 介绍 MCP 协议
- 演示动态模型切换
- 展示实际应用场景

---

## 14. 后续路线图

### v0.2.0 (短期)
- [ ] 添加 Rust 运行时支持
- [ ] 添加 TypeScript 运行时支持
- [ ] 改进性能（缓存、异步优化）
- [ ] 更多 provider（Groq、Together AI）

### v0.3.0 (中期)
- [ ] 指标和监控
- [ ] 配置 UI 工具
- [ ] 批量模型切换
- [ ] 成本估算

### v1.0.0 (稳定版)
- [ ] 完整的测试覆盖
- [ ] 产品级文档
- [ ] SLA 支持
- [ ] 企业功能

---

## 15. 维护和支持

### 毕业标准项目

- [ ] 文档完整（安装、配置、API、故障排除）
- [ ] 测试覆盖率 > 80%
- [ ] 积极维护（响应 issues < 48 小时）
- [ ] 定期发布（至少每季度）

---

## 总结

遵循此指南，你可以将 spiderswitch 成功发布为产品，让用户轻松地：

1. ✅ 通过 `pip install` 安装
2. ✅ 在 Cursor 中配置使用
3. ✅ 在 Claude Desktop 中配置使用
4. ✅ 在其他 MCP 兼容的 agent 中使用

关键成功因素：
- **易安装**: 一行命令安装
- **易配置**: 清晰的配置指南
- **易使用**: 直观的工作流
- **好文档**: 完整的教程和故障排除
- **持续支持**: 活跃维护和快速响应
