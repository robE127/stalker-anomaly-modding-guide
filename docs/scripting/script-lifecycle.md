# Script Lifecycle

Understanding when your code runs — and what's available at each point — prevents an entire class of bugs.

---

## The loading sequence

When Anomaly starts, scripts are loaded in this order:

```
1. Engine initialises
2. _g.script executes                    ← global environment, printf defined
3. axr_main.script executes              ← callback table created, RegisterScriptCallback defined
4. Scripts referenced by startup scripts ← load on demand as other scripts reference them
5. Player loads a save (or starts new game)
6. on_game_start() called on every script that defines it  ← mod scripts typically load here
7. load_state callback fires
8. on_game_load callback fires
9. First simulation tick
10. actor_on_first_update fires           ← db.actor is available from here
11. actor_on_update fires every tick thereafter
```

### When does a script actually load?

Scripts are **not** all loaded at application startup. A script file is loaded the first time another loaded script references it (lazy loading), or when the engine calls `on_game_start()` at game session start.

This has a practical consequence: **module-level code in a mod script does not run at application open** — it runs at game session start (step 6 above), which is when the player loads a save or starts a new game. If you need code to run earlier (for example to catch `main_menu_on_init`), your script must be explicitly referenced from a script that loads at startup, such as `ui_main_menu.script`. In practice, only scripts shipped by other mods (like MCM) are wired in this way, and editing those files risks breakage on updates.

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

## Detecting which scenario you are in

Several scenarios all involve the actor being destroyed or reinitialised, making it easy to confuse them. These are the distinguishing signals:

### Level transition

`on_before_level_changing` fires only during a player-triggered level transition (walking through a level changer). It does not fire on exit to main menu or save load.

After `on_before_level_changing`, the sequence continues with `on_level_changing`, `save_state`, then `actor_on_net_destroy` as the old level tears down. The new level then loads exactly like a save load: `load_state` fires, then `on_game_load`, then `actor_on_first_update`.

!!! warning "New game startup is different"
    When a new game starts, the engine performs an immediate automatic level transition to move the actor from the spawn point to the starting level. This transition fires `on_level_changing` and `save_state`/`load_state`, but does **not** fire `on_before_level_changing`. If you use a `transitioning` flag set by `on_before_level_changing`, it will be `false` during this automatic transition.

```lua
local transitioning = false

local function on_before_level_changing()
    transitioning = true
end

local function actor_on_net_destroy()
    if transitioning then
        -- player-triggered level transition — actor will come back on the other side
    else
        -- exiting to main menu, or automatic new-game startup transition
    end
    transitioning = false
end
```

### Exit to main menu

`actor_on_net_destroy` fires for both level transitions and exit to main menu, so it alone is not enough. The distinguishing signals for exit to main menu, in order:

1. `on_console_execute | disconnect` — fires first, before the actor is destroyed
2. `actor_on_net_destroy` — actor client object is destroyed
3. `server_entity_on_unregister | se_actor` — actor's server entity removed from A-Life
4. `main_menu_on_init` — main menu is shown

None of these fire during a level transition (except `actor_on_net_destroy`, which fires in both cases).

### Tracking main menu state

Combining the above: `in_main_menu` starts `true` because the script only ever loads when `on_game_start` fires — meaning the player was in the main menu immediately before. `actor_on_first_update` clears the flag once the player is in a live game. `disconnect` sets it again on exit.

`disconnect` also fires when loading a save from the main menu, which would briefly set `in_main_menu = true` during loading — but `actor_on_first_update` fires shortly after and resets it, so the false positive is self-correcting.

The initial main menu at application open cannot be observed (scripts do not load until game session start), but starting as `true` covers this correctly: the player was in the main menu before the first `on_game_start`.

```lua
local in_main_menu = true  -- true until actor_on_first_update confirms we are in a live game

local function on_console_execute(cmd)
    if cmd == "disconnect" then
        in_main_menu = true
    end
end

local function actor_on_first_update()
    in_main_menu = false
end

function on_game_start()
    RegisterScriptCallback("on_console_execute",    on_console_execute)
    RegisterScriptCallback("actor_on_first_update", actor_on_first_update)
end

function on_game_end()
    UnregisterScriptCallback("on_console_execute",    on_console_execute)
    UnregisterScriptCallback("actor_on_first_update", actor_on_first_update)
end
```

### New game vs. loading a save

A new game is a two-phase process. In phase 1, the actor spawns at an initial position: `fill_start_position` fires, then `actor_on_init`, then `on_game_load` (with no prior `load_state`), then `actor_on_first_update`. The engine then immediately transitions to the actual starting level (phase 2), which fires `on_level_changing`, `save_state`, `actor_on_net_destroy`, `load_state`, `on_game_load`, and `actor_on_first_update` again.

The cleanest signals:

- **`fill_start_position`** fires only on a new game, not on any kind of save load or level transition.
- **The first `on_game_load`** fires without a preceding `load_state` on a new game. On a save load (from main menu or level transition), `load_state` always fires first.

```lua
local save_was_loaded = false

local function load_state(m_data)
    save_was_loaded = true
    -- restore data from m_data
end

local function on_game_load()
    if not save_was_loaded then
        -- new game (phase 1) — no save data exists yet
        -- note: on_game_load will fire again after the automatic level transition (phase 2),
        -- at which point save_was_loaded will be true
    end
end
```

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
