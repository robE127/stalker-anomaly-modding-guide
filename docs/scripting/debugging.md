# Debugging & Logging

Anomaly's Lua environment gives you no interactive debugger. Diagnosing problems means reading log output, using `pcall` to catch errors before they crash a callback, and knowing which silent failure modes to watch for.

---

## The log file

All `printf` output goes to the engine log in the `appdata\logs\` subfolder of your Anomaly installation. The filename is `xray_<windows_username>.log`:

```
<Anomaly install folder>\appdata\logs\xray_roced.log   ← example
```

On each new launch the engine renames the previous session's log to `.bkp` before starting a fresh one:

```
xray_roced.log      ← current session (being written now)
xray_roced.log.bkp  ← previous session (complete, safe to read)
```

Open these in a text editor that handles large files (Notepad++, VS Code) and search for your mod's prefix. The log grows fast — tail the end, or search for `!` which the base game uses to prefix errors.

### Two requirements before printf writes anything

Getting output into the log requires satisfying two separate conditions, both of which trip up new modders:

**1. The game must be launched with `-dbg`.**
In release builds, `printf` routes through `vscript_log()` in `script_storage.cpp`, which returns immediately without writing unless `-dbg` is present in the launch arguments. Only `printe` calls (errors) bypass this gate. Add `-dbg` to your MO2 launch arguments or shortcut while developing.

**2. The log buffer must be flushed.**
Even with `-dbg`, the engine holds log writes in a memory buffer and only commits them to disk when the process exits. This means `printf` output does **not** appear in `xray_<user>.log` while the game is running — it only shows up in the `.bkp` file from the previous session on the next launch.

The `printf` implementation in `_g.script` has a `exec_console_cmd("flush")` call for exactly this purpose, but it is commented out for performance. The community norm is to accept the post-session workflow: play, close, read the `.bkp`. If you want output to appear in real-time while the game is running, you must call `flush()` yourself after each write.

**3. String literals must be plain ASCII.**
The X-Ray engine writes the log in Windows-1252. If your Lua source file is saved as UTF-8 (the default for every modern editor), any non-ASCII character in a string literal is stored as a multi-byte UTF-8 sequence but the log reader interprets each byte as a Windows-1252 codepoint. The result is garbled output:

```
-- Source file (UTF-8): "entered base zone — recording position"
-- Log output (Windows-1252 reader): "entered base zone â€" recording position"
```

The fix is simple: stick to ASCII in any string that ends up in the log. Use ` -- ` instead of `—`, `>=` instead of `≥`, and so on. This applies to `printf` strings, `printe` strings, and `abort` messages. HUD messages shown to the player via `actor_menu.set_msg` or `give_game_news` are rendered by the UI layer and are not affected.

---

## Logging functions

Four logging functions are available globally (defined in `_g.script`):

### `printf(fmt, ...)` — standard output

Formats a string and writes it to the log. Handles userdata (vectors, game objects) by converting them to readable strings automatically.

```lua
printf("player health: %s", db.actor.health)
printf("NPC %s killed by %s", victim:name(), who:name())
printf("position: %s", db.actor:position())   -- vector prints as {x, y, z}
```

Use `%s` for everything — Anomaly's `printf` implements its own `%s` substitution via `string_gsub` and does not support `%d`, `%f`, or any other specifier. Passing them produces no substitution and the literal `%d` text appears in the output.

```lua
-- WRONG: %d is not substituted, appears literally
printf("count: %d", count)

-- Correct
printf("count: %s", count)
printf("count: %s", tostring(count))
```

See [DEV_DEBUG mode](#dev_debug-mode) below for how to use `string.format` safely in a debug helper.

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

- **Enables `printf` output** — without `-dbg`, `printf` is silently discarded by the engine in release builds
- Enables `printdbg` output (which also calls `printf`)
- Activates the `printe` HUD overlay
- Unlocks debug console commands
- Enables additional validation checks in base game systems

### Recommended debug helper

Gate your own verbose logging behind `DEV_DEBUG` and use `string.format` for the interpolation — this lets you use `%d`, `%f`, and other specifiers that `printf` doesn't support natively:

**Standard version** — output appears in the `.bkp` log after the session closes (community norm):

```lua
local function dbg(fmt, ...)
    if not DEV_DEBUG then return end
    local ok, msg = pcall(string.format, fmt, ...)
    printf("[my_mod] %s", ok and msg or ("(fmt error) " .. tostring(fmt)))
end
```

**Real-time version** — output appears in the live log immediately, at the cost of a `flush()` call per message:

```lua
local function dbg(fmt, ...)
    if not DEV_DEBUG then return end
    local ok, msg = pcall(string.format, fmt, ...)
    printf("[my_mod] %s", ok and msg or ("(fmt error) " .. tostring(fmt)))
    flush()  -- force log buffer to disk immediately
end
```

`flush()` is a top-level engine function (bound in `lua_help.script`). It is equivalent to `exec_console_cmd("flush")` but avoids the overhead of console command parsing. The `printf` implementation in `_g.script` has this call commented out for performance — the community norm is to accept the post-session workflow and read the `.bkp`. Use the real-time version when you specifically need to watch the log while the game is running.

Both versions are safe to leave in a released mod — the `if not DEV_DEBUG then return end` guard means they are completely inert without `-dbg`.

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

## Testing in-game

### run_string — execute Lua from the console

The `run_string` console command evaluates an arbitrary Lua expression without modifying any script file. Open the console (`` ` `` by default) and type:

```
run_string <lua expression>
```

**Advance or rewind the game clock**

```
run_string level.change_game_time(0,3,0)
run_string level.change_game_time(0,-3,0)
```

Advances or rewinds the in-game clock by the given number of hours. Affects the actual game clock that `level.get_time_hours()` reads — unlike the weather editor, which only changes the visual sky appearance.

!!! warning "Avoid extreme `time_factor` for stability testing"
    Very high `time_factor` values can destabilize Anomaly's simulation (rapid spawn/destroy churn) and cause crashes unrelated to your script changes. For testing time-based mod logic, prefer direct clock jumps with `run_string level.change_game_time(0,h,0)`.

**Read the current hour**

```
run_string printf("hour=%s", level.get_time_hours())
```

Prints the current in-game hour to the log. Output appears in the live log immediately if `flush()` has been called; otherwise in the next session's `.bkp`.

**Restore actor health**

```
run_string db.actor:set_health_ex(1.0)
```

Sets the actor to full health instantly. Useful when testing death and respawn logic without having to reload. Requires modded exes.

**Teleport to a position**

```
run_string db.actor:set_actor_position(vector():set(-206.0193, -20.3856, -148.0225))
```

Moves the actor to the given world coordinates on the current level without a level reload. The actor snaps to the nearest navmesh vertex, so an imprecise Y value self-corrects on landing. This is the fastest way to reach a specific location to test zone detection, trigger logic, or reproduce a position-dependent bug.

!!! note "Weather editor vs. game time"
    The in-game weather editor changes the visual sky appearance but does **not** change the actual game clock that `level.get_time_hours()` reads. When testing time-based features, use `run_string level.change_game_time(0,h,0)` instead.

### Debug HUD and other debug settings

With `-dbg` active, the **Others** tab in the options menu exposes extra debug overlays:

- **Debug HUD** — shows a real-time overlay including the current in-game time. Essential for testing any time-based feature (night respawn, day/night event triggers, etc.) because it reflects the actual clock rather than the visual sky.
- **Debug map spots** — renders extra markers on the minimap for debug purposes.
- **Debug error notifications** — shows error popups in the HUD when Lua errors occur, in addition to the log entries.
- **Actor Inside Zone Info** — lists the names of `space_restrictor` zones the actor is currently inside. This mirrors `db.actor_inside_zones` (key = zone name, value = zone object), so entries like `esc_2_12_stalker_wolf_kill_zone` are level object names, not Lua variables.

Enable all three when actively developing and testing a mod. They have no effect when `-dbg` is not active.

#### Understanding zone names in Actor Inside Zone Info

Zone names in this overlay come from map data (`space_restrictor` object names in the level), so they often look editor-generated and verbose. A suffix like `_kill_zone` usually indicates a gameplay trigger/restrictor volume created by level logic.

You can inspect the same data directly from Lua:

```
run_string for name,_ in pairs(db.actor_inside_zones or {}) do printf("inside_zone=%s", name) end
```

Use this when you need to confirm that zone entry/exit logic matches what the debug HUD shows. For API details, see [`db.actor_inside_zones` in the `level` reference](../api-reference/level.md).

---

## See also

- [Lua Scope & Globals](lua-scope.md) — global namespace collisions
- [Script Lifecycle](script-lifecycle.md) — when db.actor becomes available
- [The Callback System](callbacks.md) — why pcall matters for callbacks
- [Save & Load State](save-load.md) — pcall patterns for save/load
