# Spiderswitch MCP Server - Usage Examples

This document provides practical examples for `list_models`, `switch_model`, `get_status`, and `exit_switcher`.

## list_models examples

### Example 1: list all models

```python
result = await mcp_client.call_tool("list_models", {})
payload = result["data"]
print(f"total models: {payload['count']}")
```

### Example 2: list only models with configured API keys

```python
result = await mcp_client.call_tool("list_models", {"require_api_key": True})
payload = result["data"]
print(f"ready models: {payload['count']}")
```

### Example 3: combined filtering

```python
result = await mcp_client.call_tool(
    "list_models",
    {
        "filter_provider": "openai",
        "filter_capability": "vision",
        "require_api_key": True,
    },
)
```

### Example response

```json
{
  "status": "success",
  "data": {
    "count": 3,
    "models": [
      {
        "id": "openai/gpt-4o",
        "provider": "openai",
        "capabilities": ["streaming", "tools", "vision"],
        "api_key_status": {
          "provider": "openai",
          "has_api_key": true,
          "expected_env_vars": ["OPENAI_API_KEY"],
          "configured_env_vars": ["OPENAI_API_KEY"]
        },
        "proxy_status": {
          "provider": "openai",
          "proxy_required_guess": true,
          "proxy_configured": false,
          "configured_proxy_env_vars": [],
          "hint": "This provider may require proxy access in your network region."
        }
      }
    ],
    "filtered": {
      "require_api_key": true,
      "provider": "openai",
      "capability": "vision"
    }
  }
}
```

## switch_model and status examples

```python
switch_result = await mcp_client.call_tool(
    "switch_model",
    {"model": "deepseek/deepseek-reasoner"},
)
print(switch_result["status"])  # success

status_result = await mcp_client.call_tool("get_status", {})
status = status_result["data"]
print(status["provider"], status["model"], status["connection_epoch"])
```

## exit_switcher example

```python
result = await mcp_client.call_tool("exit_switcher", {})
print(result["data"]["exited"])  # True
```

## Supported capabilities for filter_capability

- `streaming`
- `tools`
- `vision`
- `embeddings`
- `audio`

## Notes

- MCP responses are JSON text serialized as `{"status": "...", "data": ...}`.
- Prefer environment variables for API keys instead of passing `api_key` in tool arguments.
- `require_api_key=True` is useful when you want only immediately switchable models.
