# Spiderswitch 0.4.0 Modification Summary

## Code changes

- Runtime model mapping now keeps public switch IDs stable while passing provider-qualified IDs to the runtime client.
- Runtime client creation now temporarily unsets unsupported SOCKS4 proxy env vars and restores them after client creation.
- Added regression tests for both behaviors in `tests/test_runtime.py`.

## Versioning

- `pyproject.toml`: `0.3.0 -> 0.4.0`
- `src/spiderswitch/__init__.py`: `0.3.0 -> 0.4.0`
- Runtime download `User-Agent` updated to `spiderswitch/0.4.0`.

## Documentation alignment

- Updated README and guides to use unified MCP response envelope:
  - `{"status":"success","data":{...}}`
- Synchronized tool parameter docs with implementation:
  - `filter_capability` includes `audio`
  - documented `filtered` metadata from `list_models`
- Replaced internal environment-specific examples with neutral placeholders.

## Release notes source

See `CHANGELOG.md` for end-user release notes and upgrade history.
