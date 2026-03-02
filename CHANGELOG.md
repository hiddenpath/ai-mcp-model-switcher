# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [0.2.0] - 2026-03-02

### Added
- Added API key configuration diagnostics with provider-specific environment variable hints.
- Added connection coordination metadata in status responses: `connection_epoch` and `last_switched_at`.
- Added concurrency protection for model switching in runtime implementation.
- Added validation tests for API key configuration behavior.
- Published package under new distribution name `spiderswitch` on PyPI.

### Changed
- Improved API key setup and troubleshooting guidance in `README.md` and `README_CN.md`.
- Updated package version to `0.2.0` in runtime and packaging metadata.
- Updated console entrypoint to invoke package CLI correctly.
- Improved model inventory loading to use ai-protocol model manifests dynamically.
- Renamed project/package identity from `ai-mcp-model-switcher` to `spiderswitch`.

### Fixed
- Fixed unknown-tool error path that previously referenced invalid response helpers.
- Fixed duplicate class/function definitions causing runtime instability.
- Fixed sensitive argument logging by applying redaction for secret-like keys.
- Fixed state manager thread-safety issues and state copy behavior.
- Fixed strict typing and lint issues across runtime, tools, and server modules.

