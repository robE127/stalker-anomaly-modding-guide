# Scripting

Everything about how Lua code runs inside Anomaly — from how files are loaded to how your code hooks into engine events.

## Pages in this section

- **[Lua in Anomaly](lua-in-anomaly.md)** — The Lua version, available standard libraries, globals injected by the engine, and the module system
- **[Script Lifecycle](script-lifecycle.md)** — When scripts load, execution order, and how to safely depend on other scripts
- **[The Callback System](callbacks.md)** — `RegisterScriptCallback` and `AddScriptCallback` in depth, with patterns for safe registration and cleanup
- **[Save & Load State](save-load.md)** — Persisting mod data across saves using the `save_state` / `load_state` callback pair
