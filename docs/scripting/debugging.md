# Debugging & Logging

Anomaly's Lua environment gives you no interactive debugger. Diagnosing problems means reading log output, using `pcall` to catch errors before they crash a callback, and knowing which silent failure modes to watch for.

---

## The log file

All `printf` output goes to the engine log at:

```
<game install folder>\logs\xray_x64.log
```

This file is overwritten each launch. Open it in a text editor that handles large files (Notepad++, VS Code) and search for your mod's prefix. The log grows fast — tail the end or search for `!` which the base game uses to prefix errors.

---

## Logging functions

Four logging functions are available globally (defined in `_g.script`):

### `printf(fmt, ...)` — standard output

The workhorse. Formats a string and writes it to the log. Handles userdata (vectors, game objects) by converting them to readable strings automatically.

```lua
printf("player health: %s", db.actor.health)
printf("NPC %s killed by %s", victim:name(), who:name())
printf("position: %s", db.actor:position())   -- vector prints as {x, y, z}
```

Use `%s` for everything — Anomaly's `printf` only supports `%s`, not `%d` or `%f`.

```lua
-- WRONG: %d is not supported, will produce garbled output
printf("count: %d", count)

-- Correct
printf("count: %s", count)
printf("count: %s", tostring(count))
```

### `printe(fmt, ...)` — error output

Identical to `printf` but also shows a red HUD overlay when `DEV_DEBUG` is active. Use it for conditions that should never happen in a working mod:

```lua
if not db.actor then
    printe("![my_mod] actor_on_update fired but db.actor is nil")
    return
end
```

The `!` prefix is a convention used throughout the base game — it makes errors easy to find with a text search in the log.

### `printdbg(fmt, ...)` — debug-only output

Only writes to the log when the game was launched with the `-dbg` flag. Use this for verbose tracing you want during development but don't want in a released mod:

```lua
printdbg("[my_mod] processing %s items in inventory", item_count)
```

### `abort(msg, ...)` — critical error

Logs the message and immediately prints a full callstack. Use when something is so wrong the current function cannot continue:

```lua
if not st then
    abort("![my_mod] storage entry missing for id %s", tostring(id))
    return
end
```

### `callstack()` — print a stack trace

Writes the current call stack to the log. Useful standalone when you want to know how execution reached a certain point:

```lua
-- Full stack trace
callstack()

-- Caller-only (less noise)
callstack(true)

-- Return as string instead of logging
local trace = callstack(true, true)
printf("![my_mod] unexpected state — %s", trace)
```

---

## DEV_DEBUG mode

Launch the game with `-dbg` in the command line to enable debug mode:

```
AnomalyDX11.exe -dbg
```

In `_g.script` this sets the global `DEV_DEBUG = true`, which:

- Enables `printdbg` output
- Activates the `printe` HUD overlay
- Unlocks debug console commands
- Enables additional validation checks in base game systems

You can gate your own verbose logging behind the same flag:

```lua
if DEV_DEBUG then
    printf("[my_mod] detailed state: active=%s, count=%s", tostring(active), count)
end
```

---

## pcall — catching errors

`pcall` (protected call) runs a function and catches any Lua error it throws, returning a status flag instead of crashing. The callback system does **not** wrap your callbacks in pcall — an unhandled error in a callback propagates up and can freeze the game or corrupt state.

### Basic form

```lua
local ok, err = pcall(function()
    some_risky_operation()
end)

if not ok then
    printe("![my_mod] error: %s", tostring(err))
end
```

### Passing arguments

```lua
local ok, result = pcall(dangerous_function, arg1, arg2)
if ok then
    -- result is the return value of dangerous_function
else
    -- result is the error message string
end
```

### Wrapping a whole callback

The most important use of pcall in Anomaly is protecting a callback that does complex work:

```lua
local function do_on_update(delta)
    -- all the real work here
    local npc = db.storage[tracked_id] and db.storage[tracked_id].object
    if not npc then return end
    -- ... processing
end

local function actor_on_update(delta)
    local ok, err = pcall(do_on_update, delta)
    if not ok then
        printe("![my_mod] actor_on_update error: %s", tostring(err))
    end
end
```

Splitting the work into an inner function keeps the pcall wrapper clean and makes the error message point to the right place.

### Nested pcall

When one protected block calls another, each pcall only catches errors within its own call. An error in an inner pcall does not propagate to the outer one unless you re-raise it:

```lua
local function risky_inner()
    error("something went wrong")
end

local function outer_work()
    local ok, err = pcall(risky_inner)
    if not ok then
        -- Handle or re-raise
        printe("![my_mod] inner failed: %s", err)
        -- To propagate: error(err)
    end
    -- Continues here even if risky_inner failed
    printf("outer_work continues")
end

local ok, err = pcall(outer_work)
-- outer_work never throws unless you re-raise, so ok is always true here
```

### Recovering gracefully

pcall is most useful when you can continue with a fallback rather than just logging and stopping:

```lua
local function get_npc_name(id)
    local ok, result = pcall(function()
        local obj = level.object_by_id(id)
        return obj and obj:name() or "unknown"
    end)
    return ok and result or "error"
end
```

---

## Common silent failure modes

These mistakes produce no error message — the code just doesn't do what you expect.

### Callback never fires

You registered a callback but it never runs. Check:

1. **Is the callback name correct?** A typo produces a `printf("![axr_main callback_set] callback %s doesn't exist!")` in the log — search for `!` lines.
2. **Did `on_game_start` run?** If your script file has a syntax error, `on_game_start` never executes and no callbacks are registered.
3. **Is the event actually firing?** Add a `printf` directly inside the callback to confirm it's being reached at all.

### db.actor is nil

`db.actor` is nil until `actor_on_first_update` fires. Accessing it in `on_game_start`, `on_game_load`, or at module load time silently returns nil and any method call on it crashes silently (or loudly, depending on context):

```lua
-- Crashes if called before actor_on_first_update
local pos = db.actor:position()

-- Safe
local function actor_on_first_update()
    local pos = db.actor:position()   -- guaranteed non-nil here
end
```

### level.object_by_id returns nil

An object you tracked by ID has gone offline. Any method call on nil crashes:

```lua
-- CRASH if NPC went offline
db.storage[id].object:position()

-- Safe
local obj = db.storage[id] and db.storage[id].object
if obj then obj:position() end
```

### Wrong section name in ini lookup

`ini_sys:r_string_ex(section, key)` returns nil if either the section or key doesn't exist — no error, just nil. This propagates silently until something tries to use the result:

```lua
local heal = ini_sys:r_float_ex("medkit", "eat_health")
-- If "eat_health" doesn't exist, heal is nil
-- Later: db.actor.health = db.actor.health + heal   → crash
```

Always nil-check ini results before using them:

```lua
local heal = ini_sys:r_float_ex("medkit", "eat_health") or 0
```

### Global collision

Two scripts define the same global name. The second overwrites the first silently. Symptoms: a variable has the wrong value, or a function that existed earlier is now a different function. Diagnose by printing `type(variable_name)` and its value at the start of your callback.

---

## Diagnosing callback errors

When a callback throws an uncaught error, the engine logs a Lua traceback. Search the log for `SCRIPT ERROR` or `LUA ERROR` to find it. The traceback shows the file, line number, and call chain.

Because the callback system (`make_callback` in `axr_main.script`) does not use pcall internally, an error in any registered callback propagates up and can affect other callbacks registered for the same event that haven't fired yet. If you see cascading errors from unrelated callbacks, look for the first error in the log — that's the real cause.

### Minimal diagnostic template

When something doesn't work and you don't know why, add this at the very top of the suspect callback:

```lua
local function my_callback(...)
    printf("[my_mod] my_callback fired, args: %s", tostring(select(1, ...)))
    local ok, err = pcall(function(...)
        -- all your real code moved here
    end, ...)
    if not ok then
        printe("![my_mod] my_callback error: %s", tostring(err))
        callstack()
    end
end
```

This confirms the callback fires at all, shows you the arguments it received, and catches any error with a stack trace.

---

## Checking for syntax errors

Syntax errors in a `.script` file prevent the entire file from loading. The game continues without that script — no error popup, just silently missing functionality. Check the log on startup for lines like:

```
[error][     LUA] ...scripts/my_mod.script:42: unexpected symbol near '='
```

This points to the file and line. Fix the syntax, restart.

---

## See also

- [Lua Scope & Globals](lua-scope.md) — global namespace collisions
- [Script Lifecycle](script-lifecycle.md) — when db.actor becomes available
- [The Callback System](callbacks.md) — why pcall matters for callbacks
- [Save & Load State](save-load.md) — pcall patterns for save/load
