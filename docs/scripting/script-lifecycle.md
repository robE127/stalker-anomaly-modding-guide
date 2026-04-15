# Script Lifecycle

Understanding when your code runs — and what's available at each point — prevents an entire class of bugs.

---

## The loading sequence

When Anomaly starts, scripts are loaded in this order:

```
1. Engine initialises
2. _g.script executes          ← global environment, RegisterScriptCallback defined
3. axr_main.script executes    ← callback table created
4. All other *.script files execute (alphabetical order)
5. on_game_start() called on every loaded script that defines it
6. Player loads a save (or starts new game)
7. load_state callback fires
8. on_game_load callback fires
9. First simulation tick
10. actor_on_first_update fires  ← db.actor is available from here
11. actor_on_update fires every tick thereafter
```

---

## Top-level code

Code written at the top level of a script (outside any function) runs **when the file is loaded**, during step 4 above. This is before `on_game_start`, before any save is loaded, and before `db.actor` exists.

**Safe at top level:** variable declarations, table creation, local function definitions, `AddScriptCallback`

**Not safe at top level:** anything that accesses `db.actor`, `level`, or game state

```lua
-- SAFE: define module state
local is_enabled = true
local cache = {}

-- SAFE: declare a callback name your mod owns
AddScriptCallback("my_mod_on_event")

-- NOT SAFE: db.actor doesn't exist yet
local actor_pos = db.actor:position()  -- ERROR: db.actor is nil
```

---

## `on_game_start()` — the registration point

The engine calls `on_game_start()` on every script that defines it, after all scripts are loaded. This is the correct place to register callbacks.

```lua
function on_game_start()
    RegisterScriptCallback("on_game_load", on_game_load)
    RegisterScriptCallback("actor_on_first_update", actor_on_first_update)
    RegisterScriptCallback("save_state", save_state)
    RegisterScriptCallback("load_state", load_state)
end
```

`on_game_start` fires **once per game session** (i.e. once per launch), not once per save load. Callbacks registered here persist for the entire session.

---

## `on_game_end()` — cleanup

The symmetrical function called when the game session ends (player quits to main menu or exits). Use it to unregister callbacks:

```lua
function on_game_end()
    UnregisterScriptCallback("on_game_load", on_game_load)
    UnregisterScriptCallback("actor_on_first_update", actor_on_first_update)
    UnregisterScriptCallback("save_state", save_state)
    UnregisterScriptCallback("load_state", load_state)
end
```

!!! tip "Why unregister?"
    Registering the same function twice does **not** cause double-firing — the callback system stores functions as table keys, so a duplicate registration just sets the same key to `true` again. The real reason to unregister is **session state hygiene**.

    The intercepts table is never automatically cleared between game sessions. If you don't unregister in `on_game_end`, your callbacks remain active across the main menu and into subsequent sessions — firing while your module's local variables may have been reset, `db.actor` may be nil, or the `initialized` flag below may be stale from the previous session. Explicit unregistration defines a clean boundary: your mod is active between `on_game_start` and `on_game_end`, nothing more.

---

## `on_game_load` vs `actor_on_first_update`

These fire close together when loading a save, but they're different:

| | `on_game_load` | `actor_on_first_update` |
|--|--|--|
| When | After save data is deserialised | On the first simulation tick |
| `db.actor` available | No | Yes |
| `load_state` has fired | Yes | Yes |
| Use for | Reading restored save data, triggering story events | Anything requiring the actor object |

```lua
-- Reading a saved value — use on_game_load
local function on_game_load()
    if my_data.quest_completed then
        -- update some UI or state
    end
end

-- Initialising something that needs the actor — use actor_on_first_update
local initialized = false
local function actor_on_first_update()
    if initialized then return end
    initialized = true

    local pos = db.actor:position()  -- safe here
    printf("Actor spawned at: %f, %f", pos.x, pos.z)
end
```

---

## Script load order

Scripts load alphabetically by filename. This matters in one narrow case: if script `b_thing.script` calls a function from `a_utils.script` at the **top level** (outside functions), `a_utils` will already be loaded because `a` comes before `b`.

In practice this rarely matters because:
- Most inter-script calls happen inside functions, not at top level
- By the time `on_game_start` runs, all scripts are loaded

If you do have a top-level dependency, name your files so the dependency sorts earlier:

```
my_mod_core.script      ← loads first (c before m)
my_mod_main.script      ← safe to call my_mod_core functions at top level? Only if c < m alphabetically
```

When in doubt, put inter-script calls inside functions and call them after `on_game_start`.

---

## The complete pattern

This template covers the full lifecycle correctly:

```lua
-- my_mod.script

-------------------------------
-- Module state
-------------------------------
local data = {}          -- restored from save
local initialized = false

-------------------------------
-- Callback implementations
-------------------------------
local function save_state(m_data)
    m_data.my_mod = data
end

local function load_state(m_data)
    data = m_data.my_mod or {}
end

local function on_game_load()
    -- data is restored, but db.actor may not exist yet
    printf("[my_mod] loaded. count = %s", tostring(data.count))
end

local function actor_on_first_update()
    if initialized then return end
    initialized = true
    -- db.actor is guaranteed available here
    printf("[my_mod] actor ready at level: %s", level.name())
end

local function actor_on_update()
    -- runs every frame — keep this fast
end

-------------------------------
-- Registration
-------------------------------
function on_game_start()
    RegisterScriptCallback("save_state",            save_state)
    RegisterScriptCallback("load_state",            load_state)
    RegisterScriptCallback("on_game_load",          on_game_load)
    RegisterScriptCallback("actor_on_first_update", actor_on_first_update)
    RegisterScriptCallback("actor_on_update",       actor_on_update)
end

function on_game_end()
    UnregisterScriptCallback("save_state",            save_state)
    UnregisterScriptCallback("load_state",            load_state)
    UnregisterScriptCallback("on_game_load",          on_game_load)
    UnregisterScriptCallback("actor_on_first_update", actor_on_first_update)
    UnregisterScriptCallback("actor_on_update",       actor_on_update)
    initialized = false
end
```
