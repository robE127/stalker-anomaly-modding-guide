# Lua in Anomaly

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- Lua version used (LuaJIT 2.x)
- Standard library availability (`math`, `table`, `string`, `io` — which are present and which are restricted)
- File extension: `.script` not `.lua` — why and what it means
- How modules work: scripts as flat globals, not `require`-based modules
- Engine-injected globals: `db`, `level`, `game`, `alife`, `xr_logic`, `ui_mcm`, etc.
- The `_G` global table and how scripts share state
- `printf` and `log` for debug output
- Error handling: `pcall` patterns, what happens when a script errors
- Differences from standard Lua to watch out for (no `require`, limited `io`, LuaJIT-specific behaviour)
