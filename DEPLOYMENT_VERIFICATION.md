# Spiderswitch Release Verification

## Scope

Release verification for version `0.4.0`.

## Verification checklist

- Version metadata updated in package files.
- Runtime changes validated by unit tests.
- MCP response examples aligned to JSON envelope format.
- Public documentation scrubbed of local paths and secrets.

## Commands

```bash
ruff check src tests
mypy src
pytest
pytest --cov=src/spiderswitch
```

## Expected outcomes

- All checks pass.
- No sensitive data appears in repository docs.
- Tool contract in docs matches runtime behavior:
  - `status` and `data` envelope
  - `list_models.filtered` metadata
  - capability filter includes `audio`

## Release artifacts

- Branch: `release/v0.4.0`
- Planned tag: `v0.4.0`
- Source of release notes: `CHANGELOG.md`
