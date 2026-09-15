---
name: python-mcp-standards
description: Conventions for drunk Python MCP/gateway services (drunk-mcp-proxy, entraid-mcp-server) — FastAPI/Starlette provider pattern, config-driven composition, src-layout with relative imports, security-safe error logging, singleton providers, and pytest conventions. Use when writing or reviewing Python MCP-server or FastAPI code in baoduy repos.
---

# Python MCP / FastAPI Standards (drunk MCP services)

Derived from `github.com/baoduy/drunk-mcp-proxy` (Python 3.10+ FastAPI/Starlette MCP gateway) and
`entraid-mcp-server`. Every rule carries a stable `rule-id`.

## Project layout & imports

- `MCP-STR-001` **Not src-layout.** Code lives under `src/` (`src/app/`, `src/auth_providers/`, `src/proxies/`, `src/tools/`, with `tests/` alongside). New modules go in matching package.
- `MCP-STR-002` **`src.`-prefixed import.** Use relative-from-`src`-root imports (`from app.config_provider import ConfigProvider`, `from tools.env import SERVER_NAME`) — NOT `from src.app...`. Tests run via `python -m pytest` with `conftest.py` putting `src/` on `sys.path`.
- `MCP-STR-003` **Test patch path mismatch.** `@patch(...)` must target import path as used by code under test (e.g. `@patch("src.proxies.llm_proxies_provider.AppConfigProvider.get_instance")`), not where symbol is defined.

## Configuration

- `MCP-CFG-001` **Config read from JSON / scattered os.getenv.** Composition is config-driven from `data/config.yaml` (root sections `auth`, `llm`, `mcp`), loaded once via `AppConfigProvider.get_instance()` and read through typed `.get_*_config()` accessors. Don't parse YAML ad hoc at call sites.
- `MCP-CFG-002` **camelCase YAML key.** Config fields are `snake_case` (`default_provider`, `mcp_servers`).
- `MCP-CFG-003` **Env var read outside `tools/env.py`.** OS-env overrides (`FASTMCP_AUTH_ENABLED`, `MCP_OAUTH_STORAGE_TYPE`, …) are centralized in `src/tools/env.py`; reference those, don't sprinkle `os.environ` reads.

## Provider pattern

- `MCP-PRV-001` **Endpoint not mounted as a provider sub-app.** Each capability (LLM, MCP, Static, OpenAPI, Swagger) is a provider that builds an internal FastAPI app and mounts it via `provider.mount(app, route_prefix)`; register routes with `app.add_api_route(...)`. Don't hang routes directly off root app.
- `MCP-PRV-002` **Auth dependency added when auth is None.** Inject auth via `dependencies=[Depends(FastAuthMiddleware(auth_provider))]` at FastAPI construction — but only when `auth is not None`, else FastAPI rejects invalid dependency.
- `MCP-PRV-003` **Singleton re-instantiated.** Shared providers/stores (`AppConfigProvider.get_instance()`, `CacheProvider.get_oauth_store()`) are singletons; fetch instance, don't `new` a second one.

## Error handling & security

- `MCP-SEC-001` **Full exception message logged.** Log exception TYPE only: `logger.error("%s: %s", context, type(e).__name__)` — message may carry API keys or paths. Logging `str(e)` / `%s % e` is a finding.
- `MCP-SEC-002` **Raw error returned to client.** Sanitize outbound errors (`_sanitize_error_message()`); return generic "An error occurred" unless error is explicitly user-actionable.
- `MCP-SEC-003` **Secret storage unencrypted.** OAuth/token stores are backend-driven (memory/sqlite/redis) with automatic encryption when a key is set — don't add a bespoke plaintext store.

## Style & tests

- `MCP-STY-001` **Missing type hints / docstrings.** All function signatures are fully type-hinted (args + return); public functions/classes/modules carry Google-style docstrings. Double quotes for strings.
- `MCP-TEST-001` **Module-level global mocked wrong.** Override module-level vars with `monkeypatch.setattr()`; mock async and sync functions appropriately; use Starlette's `TestClient` and `Mock()` request objects with `.headers`/`.json()`/`.form()`.
- `MCP-TEST-002` **Publish/CI shape broken.** These ship as packages/images via repo workflows (`.github/workflows/publish-*.yml`, `docker.yml`); keep a clean build and don't call removed private methods in tests.

