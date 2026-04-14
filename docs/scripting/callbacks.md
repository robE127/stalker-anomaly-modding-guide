# The Callback System

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- What callbacks are and why Anomaly uses them (decoupled event system between scripts)
- `RegisterScriptCallback(name, fn)` — registers `fn` to be called when event `name` fires
- `AddScriptCallback(name)` — declares a new callback name (done by the script that owns the event)
- `SendScriptCallback(name, ...)` — fires a callback with optional arguments
- Canonical registration pattern used in virtually every mod:

```lua
-- At module level, run when the script loads
local function on_game_load()
    -- safe to initialize here
end

function on_game_start()
    RegisterScriptCallback("on_game_load", on_game_load)
end

function on_game_end()
    UnregisterScriptCallback("on_game_load", on_game_load)
end
```

- Why `on_game_start` / `on_game_end` wrap registration (prevents duplicate registration on save reload)
- `UnregisterScriptCallback` — cleanup and why it matters
- Callbacks with parameters: how arguments are passed and what types to expect
- The full callback reference is in [Callbacks Reference](../callbacks-reference/index.md)
