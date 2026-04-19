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

---

## Save file management

The sections above cover *data* serialization — what gets written inside a save file. This section covers the save files themselves: triggering saves from Lua, naming them, and deleting them.

### Triggering a save from Lua

```lua
exec_console_cmd("save my_save_name")
```

`exec_console_cmd` is a global helper defined in `_g.script`. It calls `get_console():execute(cmd)` and also fires the `on_console_execute` callback synchronously, so any registered handler sees the save before the function returns. See [Console Commands](../reference/console-commands.md) for the full reference.

### Save file names and `user_name()`

Every save is identified by a plain string name. The file on disk is `<name>.scop` in the saves folder (`appdata\savedgames\`), alongside a `.scoc` (Marshal state data) and `.dds` (screenshot thumbnail) with the same stem.

`user_name()` is a global function that returns `Core.UserName`. It is the authoritative source of the user-specific prefix used by the base game's autosave and quicksave naming:

| Save type | Name formula |
|-----------|--------------|
| Autosave (engine level-change) | `user_name() .. " - autosave"` |
| Autosave (new game, `itms_manager.script`) | `user_name() .. " - autosave"` |
| Quicksave (`level_input.script`) | `user_name() .. " - quicksave_" .. n` |
| Timer autosave (`game_autosave_new.script`) | `user_name() .. " - tempsave"` |

!!! warning "`user_name()` does not reliably return the OS username"
    `Core.UserName` is initialised from the Windows `GetUserName()` API (the OS login name). However, xray-monolith overrides it to the hardcoded string `"Player"` when the `[string_table]` config section contains a `no_native_input` key (`x_ray.cpp`). Anomaly ships with this key set for CIS/Asian locale support, so on most installations `user_name()` returns `"Player"` regardless of the actual OS account name.

    The engine log file is named before this override runs, which is why the log is named `xray_<OS-login>.log` (e.g. `xray_roced.log`) while `user_name()` at runtime returns `"Player"`.

    `character_name()` on `db.actor` returns the in-game character display name (settable in Options → Gameplay → Player Name, defaults to the stalker archetype). It is a reasonable choice for naming your own mod's save files when you want per-character save isolation across multiple playthroughs. Do not use it when you need to match or target the engine's own autosave files — those use `user_name()`, not `character_name()`.

### Deleting a save file

```lua
ui_load_dialog.delete_save_game(name)
```

`delete_save_game` is a function in the `ui_load_dialog` module. It removes the `.scop`, `.scoc`, and `.dds` files for the given save name. The name must be **lowercase** and must **not** include the `.scop` extension:

```lua
-- Delete a save named "my_save"
ui_load_dialog.delete_save_game("my_save")

-- Delete the standard autosave for the current user
ui_load_dialog.delete_save_game(string.lower(user_name()) .. " - autosave")
```

Calling `delete_save_game` on a name that does not exist is a silent no-op.

### Scanning save files

To scan the saves folder for existing `.scop` files, use `getFS():file_list_open_ex`:

```lua
local flist = getFS():file_list_open_ex(
    "$game_saves$",
    bit_or(FS.FS_ListFiles, FS.FS_RootOnly),
    "*.scop"                 -- glob pattern
)

for i = 0, flist:Size() - 1 do
    local file      = flist:GetAt(i)
    local fullname  = file:NameFull()   -- e.g. "player - quicksave.scop"
    local save_name = fullname:match("^(.+)%.scop$") or fullname
    -- save_name is now what delete_save_game expects (no extension)
    printf("found save: %s", save_name)
end
```

!!! warning "`GetAt` returns a file object, not a string"
    `flist:GetAt(i)` returns a **file object** (userdata), not a plain string. Calling string methods like `match` or `sub` directly on it throws a Lua error that fails silently inside a `CreateTimeEvent` callback, meaning no files get processed. Always call `:NameFull()` on the result first to get the filename string. This pattern is confirmed from `UILoadDialog:FillList` in `ui_load_dialog.script`, which does the same.

### Using `save_state` to detect all saves

`on_console_execute` only fires when saves are initiated through the Lua `exec_console_cmd` wrapper. It does **not** fire when the player types `save` directly in the C++ in-game console. `save_state`, on the other hand, is called by the C++ engine for every save regardless of how it was triggered — making it the reliable catch-all.

A common pattern for mods that restrict saving is to use `save_state` to detect external saves and schedule a deferred cleanup scan:

```lua
local save_in_progress = false  -- set true around our own exec_console_cmd("save ...")

local function cleanup_unauthorized_saves()
    local flist = getFS():file_list_open_ex(
        "$game_saves$",
        bit_or(FS.FS_ListFiles, FS.FS_RootOnly),
        "*.scop"
    )
    for i = 0, flist:Size() - 1 do
        local file      = flist:GetAt(i)
        local fullname  = file:NameFull()
        local save_name = fullname:match("^(.+)%.scop$") or fullname
        if save_name ~= MY_SAVE_FILENAME then
            ui_load_dialog.delete_save_game(save_name)
        end
    end
    return true  -- tell CreateTimeEvent not to repeat
end

local function save_state(m_data)
    -- ... write mod data to m_data ...
    if not save_in_progress then
        -- An external save we didn't initiate. The file may not be on disk yet
        -- (the engine writes it after all save_state callbacks return), so defer
        -- the scan by 1 second to give it time to appear.
        CreateTimeEvent("my_mod", "save_cleanup", 1, cleanup_unauthorized_saves)
    end
end
```

The 1-second delay is important: `save_state` fires before the `.scop` file is written, so scanning immediately would find nothing to delete.

### Level-transition autosaves

When the player crosses a level boundary, the engine automatically writes `user_name() .. " - autosave"` before unloading the old level. This save is generated by the C++ server (`alife_update_manager.cpp`) using `Core.UserName` directly, and the matching Lua path (`itms_manager.script`) uses `user_name()` for the same result.

If your mod restricts saves to certain locations, this autosave can bypass your restrictions. There are two layers to be aware of:

**`on_console_execute` does not fire for engine-generated saves.** The callback is only triggered by the Lua `exec_console_cmd` wrapper — the C++ engine never fires it directly. Engine autosaves (level transitions, `game_autosave_new.script` timers) and saves typed directly into the in-game console all bypass `on_console_execute` completely. Use `save_state` — called by C++ for every save — as the reliable catch-all instead.

**Even when `on_console_execute` does fire, it is a pre-notification.** For saves triggered via `exec_console_cmd`, the callback fires *before* the file is written to disk. Calling `delete_save_game` inside the callback attempts to delete a file that does not yet exist; the engine writes it after the callback returns and the file persists. This is why the deferred `CreateTimeEvent` pattern (described above) is necessary.

**The fix: write a flag file in `on_level_changing`, delete in `actor_on_first_update`.** `on_level_changing` fires before the level unloads, so write a small marker file to the saves folder there. On the new level, `actor_on_first_update` checks for the marker: if it exists, this session caused the transition and the autosave belongs to it; if it does not exist, the file (if any) came from somewhere else and should not be touched.

```lua
local TRANSITION_FLAG = "my_mod_transition_flag"

local function get_flag_path()
    return getFS():update_path("$game_saves$", "") .. TRANSITION_FLAG
end

local function on_level_changing()
    local f = io.open(get_flag_path(), "w")
    if f then f:write("1"); f:close() end
end

local function actor_on_first_update()
    local flag_path = get_flag_path()
    local f = io.open(flag_path, "r")
    local flag_val = f and f:read("*l") or "0"
    if f then f:close() end

    if flag_val == "1" then
        -- Consume the flag (os.remove is not available; overwrite instead).
        local fw = io.open(flag_path, "w")
        if fw then fw:write("0"); fw:close() end
        -- This session triggered the transition, so the autosave on disk is ours.
        local autosave_name = string.lower(user_name()) .. " - autosave"
        ui_load_dialog.delete_save_game(autosave_name)
    end
    -- ... rest of first-update logic
end
```

`getFS():update_path("$game_saves$", "")` returns the absolute path to the saves folder with a trailing separator. `io.open` is available in Anomaly's Lua environment (`alife_storage_manager.script` uses it), but `os.remove` is **not** — the `os` library's file-system functions are not exposed. Instead of deleting the flag file, overwrite it with `"0"` to consume it and check for `"1"` to distinguish a live flag from a previously-consumed one:

```lua
local f = io.open(flag_path, "r")
local flag_val = f and f:read("*l") or "0"
if f then f:close() end

if flag_val == "1" then
    -- Consume the flag
    local fw = io.open(flag_path, "w")
    if fw then fw:write("0"); fw:close() end
    -- ... delete autosave
end
```

!!! warning "Use a mod-specific prefix — `user_name()` alone is not sufficient"
    `user_name()` does not change between playthroughs. If two separate game sessions exist on the same machine (e.g. a vanilla playthrough and your modded one), both would write `user_name() .. " - autosave"` to the same filename. Deleting by that name would delete whichever file was written most recently, regardless of which session it belongs to.

    Scanning with `getFS():file_list_open_ex("$game_saves$", ..., "*autosave*")` is even more dangerous — it deletes every autosave in the folder unconditionally.

    The safe pattern is to give every save *your mod writes* a distinctive prefix so it can always be identified as yours:

    ```lua
    local SAVE_FILENAME = "em_extraction_save"  -- "em_" = extraction mod
    exec_console_cmd("save " .. SAVE_FILENAME)
    ```

    Your mod still needs `user_name()` to delete the engine's level-transition autosave (since the engine names it that way and you cannot change it). Guard the delete with the flag-file pattern above so that it only runs when *this session* triggered the transition — not when a pre-existing autosave from another playthrough happens to be sitting in the saves folder. Everything your mod writes uses your prefixed name, and any file management that targets your mod's saves can do so safely by matching `"em_*"` (or whatever prefix you choose) rather than relying on the OS username.

---

## See also

- [Engine Internals](engine-internals.md) — how the save file is structured and the marshal serialization system
- [Object Binders](object-binders.md) — the per-object save/load pattern used by binders
- [Console Commands](../reference/console-commands.md) — `save`, `load`, `flush` and other commands callable from Lua
