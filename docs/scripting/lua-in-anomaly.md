# Lua in Anomaly

Anomaly's scripting layer is **LuaJIT** — a fast just-in-time compiler for Lua 5.1. If you've written Python, JavaScript, or any other scripting language, Lua will feel familiar quickly. This page covers what's different about Lua specifically inside Anomaly.

---

## The `.script` extension

Anomaly scripts are plain Lua files saved with the `.script` extension instead of `.lua`. The extension is a convention from the X-Ray engine's early days and has no effect on how the files execute. Lua syntax, semantics, and standard libraries are unchanged.

Set your editor to treat `.script` as Lua (see [Environment Setup](../getting-started/environment-setup.md)).

---

## No `require` — scripts are global

Standard Lua modules use `require("module_name")` to import code from other files. **Anomaly does not use `require`.** Instead, the engine loads every `.script` file in `gamedata/scripts/` at startup and every function defined at module level is accessible from every other script as a global.

If `utils.script` defines:
```lua
function utils.clamp(val, min, max)
    return math.max(min, math.min(max, val))
end
```

Any other script can call `utils.clamp(...)` directly. There's no import step.

!!! warning "Name collisions"
    Because everything is global, two scripts that define the same function name will conflict — the last one loaded wins. Always prefix your functions and global variables with your mod's name:
    ```lua
    -- Bad:
    function helper() ... end

    -- Good:
    function my_mod_helper() ... end
    ```

---

## Standard library availability

Most of Lua's standard library is available. The commonly used ones:

| Library | Available | Notes |
|---------|-----------|-------|
| `math` | Yes | Full |
| `string` | Yes | Full |
| `table` | Yes | Full |
| `io` | Partial | File reading works; writing is restricted |
| `os` | Partial | `os.clock()`, `os.time()` work; `os.execute()` does not |
| `debug` | Partial | Some introspection available |
| `coroutine` | Yes | Full (LuaJIT) |
| `bit` | Yes | LuaJIT bitwise operations |
| `ffi` | No | FFI is disabled |

### Performance tip: cache standard library calls

The base game scripts cache frequently called functions as module-level locals. You should do the same in hot paths:

```lua
-- At the top of your script
local string_format = string.format
local math_floor = math.floor
local pairs = pairs
```

This avoids a global table lookup on every call, which matters in `actor_on_update` (runs every frame).

---

## Engine-injected globals

The engine makes these globals available to all scripts from startup:

```lua
-- Core game objects
db          -- Central storage: db.actor, db.storage[], db.add_actor, etc.
level       -- Current map: level.name(), level.object_by_id(), level.get_time_hours()
game        -- Game utilities: game.translate_string(), game.get_game_time()
alife()     -- A-Life simulation (function call, returns the sim manager)

-- Config access
system_ini()  -- Returns an ini_file for the merged system config

-- Key constants
DIK_keys      -- Table of DirectInput key codes: DIK_keys.DIK_W, DIK_keys.DIK_F6, etc.
key_bindings  -- Table of game action bindings: key_bindings.kFWD, etc.

-- Callback system
RegisterScriptCallback(name, fn)
UnregisterScriptCallback(name, fn)
AddScriptCallback(name)
SendScriptCallback(name, ...)

-- Utility
printf(fmt, ...)   -- Write formatted string to game log
log(msg)           -- Write string to game log
bind_to_dik(bind)  -- Convert a key_bindings constant to a DIK code

-- Version
GAME_VERSION  -- "1.5.2"
```

---

## The `class` keyword

LuaJIT in Anomaly is extended with a `class` keyword for object-oriented programming. This is not standard Lua — it's a custom addition by the engine.

```lua
class "my_class" (parent_class)  -- inherit from parent_class (optional)

function my_class:__init(arg1, arg2)
    super(self)  -- call parent constructor if inheriting
    self.value = arg1
end

function my_class:my_method()
    return self.value
end

-- Instantiate:
local obj = my_class("hello")
obj:my_method()  -- returns "hello"
```

You'll use this when building UI windows (which inherit from `CUIScriptWnd`) or object binders. For most script mods you won't need to define classes.

---

## Logging and debugging

```lua
-- Write to the log file (appdata/logs/xray_*.log)
printf("My value is: %s", tostring(my_var))
printf("Position: %f, %f, %f", pos.x, pos.y, pos.z)

-- Conditional debug logging (only when DEV_DEBUG is true in _g.script)
if DEV_DEBUG then
    printf("[my_mod] debug info: %s", msg)
end
```

`printf` uses standard C-style format strings: `%s` for strings, `%d` for integers, `%f` for floats.

There is no interactive debugger. Log-driven development is the norm.

---

## Error handling

Unhandled Lua errors in callbacks are caught by the engine and logged, but they silently abort that callback's execution. If something isn't working, the log file is the first place to look.

Use `pcall` to handle errors gracefully in your own code:

```lua
local ok, err = pcall(function()
    -- code that might error
    risky_operation()
end)

if not ok then
    printf("[my_mod] Error: %s", tostring(err))
end
```

---

## LuaJIT-specific features

```lua
-- Bitwise operations (via the 'bit' library)
local flags = bit.bor(0x01, 0x04)   -- OR
local masked = bit.band(flags, 0x01) -- AND
local shifted = bit.lshift(1, 3)    -- left shift

-- Anomaly also provides global bit helpers:
bit_and(a, b)
bit_or(a, b)

-- The Marshal library (binary serialisation, used by the save system)
-- You don't call this directly — the save/load callback system handles it.
-- USE_MARSHAL = true when available (set in _g.script)
```
