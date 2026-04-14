# Save & Load State

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- How Anomaly's save system works at a high level (marshal/unmarshal Lua tables to savegame)
- `save_state(m_data)` callback — `m_data` is a table you write your data into
- `load_state(m_data)` callback — `m_data` is the same table, restored from the savegame
- Canonical save/load pattern:

```lua
local data = {}

local function save_state(m_data)
    m_data.my_mod = data
end

local function load_state(m_data)
    data = m_data.my_mod or {}
end

function on_game_start()
    RegisterScriptCallback("save_state", save_state)
    RegisterScriptCallback("load_state", load_state)
end
```

- Namespacing your key in `m_data` to avoid collisions with other mods
- What types are serializable (strings, numbers, booleans, nested tables — not functions or userdata)
- What happens when a save was made with an older version of your mod (missing keys, default values)
- `actor_on_first_update` vs `load_state` for initialization: which to use when
