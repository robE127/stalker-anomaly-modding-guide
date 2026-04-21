# Extraction Mod — Lessons Learned

This file captures every concrete finding from building the extraction mod that is
either missing from the current guide, contradicts it, or fills a gap that required
reading community mod source to resolve. Use this to drive guide improvements.

---

## 1. API gaps — functions not documented in the guide

### `exec_console_cmd(cmd)`
Fires any console command from Lua. Required for saving to a specific filename:
```lua
exec_console_cmd("save my_save_name")
```
Not documented anywhere in `docs/`. Found via Jabbers Soulslike source.
**Should be added to:** api-reference (level/game utilities section).

---

### `ui_load_dialog.delete_save_game(name)`
Deletes a save file by name. Takes the **lowercase** filename with **no extension**.
```lua
ui_load_dialog.delete_save_game("autosave")
ui_load_dialog.delete_save_game("my_save_name")
```
Not documented. Found via Jabbers Soulslike source.
**Should be added to:** a new "Save file management" section in the API reference.

---

### `db.actor:transfer_item(item, container)`
Moves an item from the actor's inventory directly into a container game object.
The container must be **online** (i.e. `level.object_by_id(id)` returns non-nil)
before this can be called. Do not use `drop_item` when you want items inside a
container — `drop_item` places them on the ground near the actor.
```lua
db.actor:transfer_item(item, stash_object)
```
Not documented. Found via Jabbers Soulslike source (`TransferItem` method).
**Should be added to:** api-reference/actor.md and api-reference/game-object.md.

---

### `db.actor:set_health_ex(value)`
Sets health to an **absolute** value (0.0–1.0). Requires modded exes.
Prefer this over `change_health` when you need to set a specific value, especially
after a cancelled death, because `change_health` is a delta that compounds with
whatever the current value is (which may be 0 or negative in edge cases).
Already noted in actor.md as modded-exes only but worth emphasising in context.

---

### `db.actor:wounded(false)`
Clears the "wounded" state set by the engine when health hits 0.
This state persists after health is restored and causes hurt sounds to keep
playing. Must be called explicitly after a death-cancel respawn.
```lua
db.actor:wounded(false)
```
The setter form is documented in `lua_help.script` (`function wounded(boolean)`)
but not called out in our guide. **Should be added to:** actor.md vitals section.

---

### Direct property setters on `db.actor`
Several actor stats can be set via direct assignment rather than `change_*` methods:
```lua
db.actor.power      = 1     -- set stamina to full
db.actor.radiation  = 0     -- clear radiation
db.actor.bleeding   = 0     -- stop bleeding (see change_bleeding note below)
db.actor.psy_health = 1     -- set psy health to full
db.actor.health     = 1     -- set health (prefer set_health_ex for absolute sets)
```
These are used by `bind_stalker_ext.script` internally and by Jabbers Soulslike's
`HealActor()`. Not mentioned in the guide as an alternative to `change_*`.
**Should be added to:** actor.md.

---

### `bind_stalker_ext.invulnerable_time`
A module-level variable (not `local`) in `bind_stalker_ext.script`. When set to a
future `time_global()` value, `actor_on_update` forces `health=1`, `bleeding=1`,
`psy_health=1`, `radiation=0` every frame, preventing re-death from residual damage.

```lua
bind_stalker_ext.invulnerable_time = time_global() + 30000  -- 30 seconds
```

**Critical side effect:** while active, `bleeding` is forced to `1` each frame,
which causes hurt sounds even after calling `heal_actor()`. Expire it immediately
after the actor is safely at the respawn point:
```lua
bind_stalker_ext.invulnerable_time = time_global() + 1
```
Pattern confirmed from Jabbers Soulslike `OnDeath()` / `OnRespawn()`.
Not documented anywhere in the guide.
**Should be added to:** a new "bind_stalker_ext integration" section or the
callbacks/lifecycle page.

---

### `ChangeLevel(pos, lvid, gvid, angle, anim)`
Teleports the actor by sending an `M_CHANGE_LEVEL` net packet.
```lua
ChangeLevel(pos, lvid, gvid, VEC_ZERO, false)
```
**Critical behaviour:** execution of the current Lua block stops immediately when
`ChangeLevel` fires (documented in `_g.script` line 407). Any save/message calls
must come **before** `ChangeLevel`, not after.

`anim=true` adds a `sleep_fade.ppe` effect and a 3-second deferred timer before
the actual level change. `anim=false` fires immediately.

**Same-level vs cross-level:** `ChangeLevel` on the same level causes a "ghost
camera" state — the level reloads but the actor binder does not reinitialise
correctly. The base game's `game_fast_travel.script` uses `set_actor_position` for
same-level travel and only `ChangeLevel` for cross-level. Follow the same split:
```lua
if data.last_base_level == level.name() then
    db.actor:set_actor_position(base_pos)
else
    ChangeLevel(base_pos, lvid, gvid, VEC_ZERO, false)
end
```
Not documented in the guide. `VEC_ZERO` is a global defined in `_g.script`.
**Should be added to:** api-reference (level utilities or a teleportation page).

---

### `db.actor_inside_zones`
A table tracking which zones the actor is currently inside. Not used in the final
mod (distance check was sufficient), but would enable precise zone-entry events
rather than polling. Found in Fair Fast Travel source.
**Should be added to:** api-reference.

---

## 2. Documentation errors — things the guide says that are wrong

### `change_bleeding()` listed as available on `db.actor`
**`db.actor:change_bleeding(delta)` does not exist and crashes with a nil error.**
The method is registered only for NPCs/monsters. It appears in `lua_help.script`
under the `-- NPCs` comment block (around line 5556).

Both `actor.md` and `game-object.md` were corrected during this session:
- `actor.md` — removed the call and added a `!!! warning` admonition
- `game-object.md` — annotated the table row as "NPCs/monsters only"

**Root cause:** the guide listed it based on `lua_help.script` without verifying
that the binding is present on the actor type.

---

## 3. Engine behaviour not documented

### `actor_on_before_death` timing and `g_Alive()`
When `actor_on_before_death` fires, health is **already 0**. `g_Alive()` in C++
is simply `GetfHealth() > 0` (`Entity.h:90`). This means `db.actor:alive()`
returns `false` inside and immediately after the death callback.

Consequence: any deferred function that calls `db.actor:alive()` as a guard will
bail out silently if health has not been restored before the defer fires.

Fix: restore health immediately in the death callback itself, before queuing any
`CreateTimeEvent`:
```lua
local function actor_on_before_death(who_id, flags)
    flags.ret_value = false
    db.actor:set_health_ex(1.0)  -- must happen HERE, not in the deferred fn
    CreateTimeEvent(...)
end
```
**Should be added to:** the `actor_on_before_death` entry in the callbacks reference.

---

### Death must be deferred with `CreateTimeEvent`
Setting `flags.ret_value = false` cancels the `kill()` call but the engine has
already started death-related state (camera, ragdoll) before the Lua callback fires.
Doing any teleport or state change in the same frame as the death callback results
in a broken "hovering outside body" camera state.

Defer all respawn logic by at least 1 second:
```lua
CreateTimeEvent("my_mod", "respawn", 1, my_respawn_fn)
```
**Should be added to:** `actor_on_before_death` docs and the death/respawn example.

---

### Same-map respawn after cancelled death — no movement / no mouse
Observed in `extraction_mod.script`: `black_infinite.ppe` + deferred `set_actor_position`
on the **same** level could leave input dead after `remove_pp_effector` alone.

**Fix:** after removing the PP id, call `level.enable_input()`, clear
`game.only_allow_movekeys(false)` when `game.only_movekeys_allowed()`, `level.show_weapon(true)`,
and schedule the same cleanup again with `CreateTimeEvent(..., 0, ...)`.

**Documented in the guide** under `actor_on_before_death` (callbacks reference) and
under cancel-death / same-map respawn (actor API page).
Implementation reference: `extraction_respawn_clear_death_fx_and_controls` in this mod.

---

### `ProcessEventQueue` is driven by `AddUniqueCall`, not `actor_on_update`
`CreateTimeEvent` events are processed by `ProcessEventQueue`, which is registered
via `AddUniqueCall(ProcessEventQueue)` in `bind_stalker_ext.actor_on_reinit`. This
means time events fire from the engine's main update loop, not from
`actor_on_update`, and will fire even when the actor is in unusual states.

---

### `printf` in Anomaly Lua only handles `%s` reliably
Anomaly's `printf` does not reliably substitute `%f`, `%d`, or other format
specifiers. Always pre-format with `string.format` and pass the result as `%s`:
```lua
local function dbg(fmt, ...)
    if not DEBUG then return end
    local ok, msg = pcall(string.format, fmt, ...)
    printf("[EM] %s", ok and msg or ("(fmt error) " .. tostring(fmt)))
end
```
**Should be added to:** the debugging / logging section of the guide.

---

### Level-transition autosaves bypass `on_console_execute`
The engine writes `<character_name> - autosave` on every level transition via an
internal path. `on_console_execute` **does** fire for this save, but as a
pre-notification — before the file is written to disk. Calling
`ui_load_dialog.delete_save_game` inside that callback attempts to delete a file
that does not yet exist; the engine then writes it after the callback returns.

Consequence: the player sees the "Cannot save outside a friendly base!" UI message
(from `is_engine_save` detection), but the file persists on disk.

Fix: in `actor_on_first_update`, delete the specific autosave name the engine
would have written, constructed using `user_name()`:
```lua
local autosave_name = string.lower(user_name()) .. " - autosave"
ui_load_dialog.delete_save_game(autosave_name)
```
`delete_save_game` on a non-existent file is a silent no-op.

**Source of the save name:** both the C++ engine (`alife_update_manager.cpp:219`:
`strconcat(buf, Core.UserName, " - ", "autosave")`) and base-game Lua scripts
(`itms_manager.script`: `exec_console_cmd("save " .. user_name() .. " - autosave")`)
use `Core.UserName` as the prefix. `user_name()` is the Lua binding to
`Core.UserName` (`script_engine_script.cpp`: `def("user_name", &user_name)`).

**`Core.UserName` is NOT reliably the OS username.** It is initialised from the
Windows `GetUserName()` API, but xray-monolith overrides it to the hardcoded
string `"Player"` when the `[string_table]` config section contains `no_native_input`
(see `x_ray.cpp` line 1071). Anomaly ships with this key for CIS/Asian locale
support, so on most installations `user_name()` returns `"Player"` regardless of
the actual Windows account.

The engine log file is named at startup BEFORE this override runs, which is why
the log is `xray_roced.log` (OS login = "roced") while `user_name()` returns
"Player" once the game is running. `character_name()` is unrelated — it returns the in-game
actor display name (faction archetype, e.g. "stalker"), not any OS or save-file
identity.

**`character_name()` is not the same as `user_name()`:** `character_name()` returns
the NPC/actor display name used in UI (settable via Options → Gameplay → Player
Name). `user_name()` returns the OS-level username used for save file naming.

**A glob scan (`*autosave*`) works but is unsafe** — it would delete autosave
files from other playthroughs or characters sharing the same Anomaly install.

**`user_name()` alone is also not safe** — it doesn't change between playthroughs,
so `user_name() .. " - autosave"` is the same filename for every playthrough on
the same machine. A pre-existing "player - autosave" from a different playthrough
would be deleted unconditionally on the first level transition with the mod.

**Recommended pattern: flag file + mod-specific save prefix.** Write a flag file
to the saves folder in `on_level_changing`; check for it in `actor_on_first_update`.
Only delete `user_name() .. " - autosave"` when the flag is present — meaning THIS
session triggered the transition. Name all mod-owned saves with a distinctive
prefix (e.g. `"em_"`) so they can be identified without relying on `user_name()`
or broad globs:
```lua
local TRANSITION_FLAG = "em_transition_flag"
local SAVE_FILENAME   = "em_extraction_save"

local function get_flag_path()
    return getFS():update_path("$game_saves$", "") .. TRANSITION_FLAG
end

local function on_level_changing()
    local f = io.open(get_flag_path(), "w")
    if f then f:write("1"); f:close() end
end

local function actor_on_first_update()
    local f = io.open(get_flag_path(), "r")
    if f then
        f:close()
        os.remove(get_flag_path())
        ui_load_dialog.delete_save_game(string.lower(user_name()) .. " - autosave")
    end
    -- ...
end
```
`io.open` is available in Anomaly's Lua (`alife_storage_manager.script` uses it).
**`os.remove` is NOT available** — it crashes with `attempt to call field 'remove'
(a nil value)`. The `os` library's file-system functions are not exposed in the
sandbox. To consume the flag file, overwrite it with `"0"` and check for `"1"` on
read rather than deleting it. `getFS():update_path` returns the absolute path to
the saves folder with a trailing separator. `on_level_changing` is a real callback
in `axr_main.script` line 53.
**Should be added to:** debugging guide (silent failure modes) — `os.remove` looks
like it should work but crashes immediately.
**Should be added to:** a save-file management API page.

---

### Stash objects are not immediately online after `alife_create`
`alife_create("inv_backpack", pos, lvid, gvid)` returns a server-side object
immediately, but the corresponding client-side object (accessible via
`level.object_by_id(id)`) may not exist yet. Calling `transfer_item` before the
object is online will fail silently.

Poll until online using a `CreateTimeEvent` that returns `false` to keep firing:
```lua
local function wait_for_stash(stash_id)
    local stash = level.object_by_id(stash_id)
    if not stash then return false end  -- poll again next tick
    -- stash is online, do work here
    return true
end
CreateTimeEvent("my_mod", "wait_stash", 0, wait_for_stash, se_stash.id)
```
Pattern confirmed from Jabbers Soulslike `HandleItemsAndRespawn`.
**Should be added to:** the alife_create API docs and an item transfer example.

---

## 4. Level name strings

All level name strings have been confirmed in-game and documented in
`docs/api-reference/level.md`. Several names we originally inferred from smart
terrain prefixes were wrong — the authoritative source is Fair Fast Travel
`travel_destinations.ltx` `[northern_maps]`, cross-checked against in-game
`level.name()` output.

Key corrections from the original inferred list:

| Was (wrong)      | Correct          | Location        |
|------------------|------------------|-----------------|
| `l03_bar`        | `l05_bar`        | Rostok          |
| `l04_agroprom`   | `l03_agroprom`   | Agroprom        |
| `l05_marsh`      | `k00_marsh`      | Great Swamp     |
| `l06_mil`        | `l07_military`   | Army Warehouses |
| `l09_limansk`    | `l10_limansk`    | Limansk         |
| `l12_darkvalley` | `l04_darkvalley` | Dark Valley     |
| `k00_marsh`      | `zaton`          | Zaton           |
| `k01_darkscape`  | `jupiter`        | Jupiter         |

Note: `k00_marsh` is Great Swamp (not Zaton). `k01_darkscape` is Darkscape
(a separate map — not Jupiter). The CoP maps use plain names: `zaton`,
`jupiter`, `pripyat`.

**See:** `docs/api-reference/level.md` for the full confirmed list.

---

## 5. Useful reference mods for this topic area

| Mod | What it demonstrates |
|-----|----------------------|
| [Jabbers Soulslike](https://github.com/fdsprod/Jabbers-Soulslike-Anomaly-Mod) | Full death/respawn cycle: cancel death, invulnerability window, stash creation, item transfer, `ChangeLevel` teleport, wound clearing |
| [Fair Fast Travel](https://www.moddb.com/mods/stalker-anomaly/addons/fair-fast-travel) | Safe zone detection via `db.actor_inside_zones`, travel zone coordinates |

---

## 6. Remaining known issues in the mod itself

- All level names have been confirmed in-game and corrected in `extraction_mod_zones.ltx`.
- Debug logging (`DEBUG = true` in the script) produces no output for unknown
  reasons even with the `string.format` pre-processing fix applied. Needs further
  investigation — may be a MO2 load order issue where an older version of the
  script overrides ours.
- Cross-level respawn (death on one level, base on another) is implemented but
  untested.
- Late-game levels (Pripyat, Red Forest, Dead City, Limansk continuation) have no
  safe zone data.
- Level-transition autosave bypass: **fixed** using flag file + `on_level_changing`.
  `on_level_changing` writes `em_transition_flag` to the saves folder before the
  level unloads. `actor_on_first_update` on the new level checks for the flag:
  if present, deletes `user_name() .. " - autosave"` (which is now on disk) and
  removes the flag; if absent, skips the delete (preserves pre-existing files from
  other playthroughs). All mod-owned saves use the `"em_"` prefix.
