# Save & Load State

Anomaly uses a binary serialisation system (the Marshal library) to persist Lua data across saves. The `save_state` and `load_state` callbacks are how your mod participates in it.

---

## How it works

When the player saves the game, the engine fires `save_state` with a shared table (`m_data`). Every registered handler writes its data into that table. The engine then serialises the whole table to the save file.

When the player loads a save, the engine deserialises the table, then fires `load_state` with the restored data.

```
Save:   your save_state(m_data)  →  m_data written to disk
Load:   m_data read from disk    →  your load_state(m_data)
```

---

## The pattern

```lua
-- Module-level state your mod wants to persist
local data = {}

local function save_state(m_data)
    m_data.my_mod = data
end

local function load_state(m_data)
    data = m_data.my_mod or {}  -- 'or {}' handles first-ever load (key won't exist)
end

function on_game_start()
    RegisterScriptCallback("save_state", save_state)
    RegisterScriptCallback("load_state", load_state)
end

function on_game_end()
    UnregisterScriptCallback("save_state", save_state)
    UnregisterScriptCallback("load_state", load_state)
end
```

---

## Namespacing

`m_data` is shared by every mod. Use a unique key — your mod's name — to avoid collisions:

```lua
-- Good: namespaced under your mod
m_data.my_mod_name = { count = 5, last_seen = "cordon" }

-- Dangerous: generic key that another mod might also use
m_data.count = 5
m_data.settings = { ... }
```

If two mods write to the same key, the last one to run wins and the other's data is lost.

---

## What can be serialised

The Marshal library serialises Lua values to a compact binary format. Supported types:

| Type | Supported |
|------|-----------|
| `nil` | Yes |
| `boolean` | Yes |
| `number` (int and float) | Yes |
| `string` | Yes |
| `table` (nested) | Yes |
| `function` | **No** |
| `userdata` (game objects) | **No** |
| `thread` (coroutine) | **No** |

Don't try to save `game_object` references, `CTime` values, or functions. Convert them to primitive types first:

```lua
-- Wrong: game_object can't be serialised
m_data.my_mod = { target = some_game_object }

-- Right: save the ID (a number), look up the object on load
m_data.my_mod = { target_id = some_game_object:id() }

-- On load, retrieve the object:
local target = level.object_by_id(data.target_id)
```

---

## Providing defaults

Since `load_state` runs even on a brand new game (when the key doesn't exist yet), always provide defaults:

```lua
local function load_state(m_data)
    local saved = m_data.my_mod or {}
    data = {
        count      = saved.count      or 0,
        last_level = saved.last_level or "unknown",
        enabled    = saved.enabled    ~= nil and saved.enabled or true,
    }
end
```

The `enabled ~= nil and saved.enabled or true` pattern handles booleans correctly — `or` alone doesn't work for booleans because `false or default` returns `default`.

---

## Handling save version changes

If you add a new field to your data in a mod update, old saves won't have it. The `or default` pattern handles this automatically. If you rename or remove a field, old saves will just have the old key sitting unused in the table — harmless.

If you need to migrate data from an old format:

```lua
local function load_state(m_data)
    local saved = m_data.my_mod or {}

    -- Migrate from v1 format (single number) to v2 (table)
    if type(saved) == "number" then
        data = { count = saved }  -- wrap old value in new structure
    else
        data = saved
    end
end
```

---

## Storing per-NPC or per-object data

`m_data` is shared across all scripts, so it's also where per-object state can be stored. The convention is to index by object ID:

```lua
-- Saving per-NPC data (from a binder's save_state method)
function my_binder:save_state(m_data)
    local id = self.object:id()
    m_data.my_mod_npcs = m_data.my_mod_npcs or {}
    m_data.my_mod_npcs[id] = self.my_npc_data
end

function my_binder:load_state(m_data)
    local id = self.object:id()
    local saved = m_data.my_mod_npcs and m_data.my_mod_npcs[id]
    self.my_npc_data = saved or {}
end
```

---

## Timing: when is `load_state` safe to act on?

`load_state` fires **before** `on_game_load` and **before** the first simulation tick. `db.actor` is **not** available in `load_state`. Only restore data there — don't try to interact with game objects.

```lua
local function load_state(m_data)
    data = m_data.my_mod or {}       -- OK: just restoring data
    db.actor:give_money(100)         -- CRASH: db.actor is nil
end

local function on_game_load()
    -- data is already restored here, and we can read it
    if data.reward_pending then
        -- still can't use db.actor here either — wait for actor_on_first_update
    end
end

local function actor_on_first_update()
    -- db.actor exists, data is restored — safe to do everything
    if data.reward_pending then
        db.actor:give_money(100)
        data.reward_pending = false
    end
end
```
