# game

The `game` global provides engine-wide utilities: localisation, time, HUD animations, and game flow control. Unlike `level`, these functions are available even when no level is loaded.

---

## Localisation

`game.translate_string` is the most-used function in Anomaly modding — it looks up a text key and returns the localised string for the current language.

```lua
local text = game.translate_string("st_psy_zombification_scene")
-- Returns the value from configs/text/<lang>/ui_st_psy.xml (or whichever file defines it)
```

Text keys are defined in XML files under `gamedata/configs/text/<lang>/`. The `eng/` subfolder is standard English. A file can contain many keys:

```xml
<string id="my_mod_greeting">
    <text>Hello, Stalker.</text>
</string>
```

```lua
local greeting = game.translate_string("my_mod_greeting")
-- Returns "Hello, Stalker."
```

If a key is not found, `translate_string` returns the key itself as a fallback string.

**Common pattern — build a displayed string from data:**

```lua
local level_display = game.translate_string(level.name())  -- levels often have translation keys
local header = game.translate_string("my_mod_quest_title")
local body   = string.format(game.translate_string("my_mod_quest_body_fmt"), npc_name, reward)
```

---

## Time

### CTime object

`game.get_game_time()` returns a `CTime` userdata object representing the current in-game timestamp.

```lua
local t = game.get_game_time()
```

`CTime` has methods for reading and comparing time:

```lua
-- Format as a string
-- Format codes: %H=hour(24), %M=minute, %S=second, %d=day, %m=month, %Y=year
local time_str = t:timeToString(0)  -- 0 = short format

-- Time difference in seconds
local elapsed = t:diffSec(earlier_ctime)  -- positive if t is later

-- The game epoch is 00:00 on April 12, 2012
```

### Raw time

```lua
local raw = game.time()  -- in-game time as a raw number (milliseconds since game epoch)
```

`game.time()` is cheaper than `game.get_game_time()` when you just need a relative timestamp for timers:

```lua
-- Simple timer pattern
local end_time = game.time() + 5000  -- 5 game-seconds from now

local function check()
    return game.time() >= end_time
end
```

!!! note "game.time() vs os.clock() vs level.get_time_hours()"
    - `os.clock()` — real CPU time, useful for performance measurement
    - `game.time()` — in-game time in ms, affected by time factor, paused when game is paused
    - `level.get_time_hours()` — integer hour of the in-game day (0–23), for day/night logic

---

## HUD animations

Anomaly's weapon and hand animations can be driven from script using the HUD animation system.

```lua
-- Play a blended HUD animation
-- game.play_hud_anm(name, part, speed, power, looped, no_restart)
game.play_hud_anm("anm_eat_bread", 0, 0.25, 1.0, false, false)

-- Stop a specific HUD animation
game.stop_hud_anm("anm_eat_bread", false)  -- false = let it finish; true = force stop

-- Stop all active HUD animations
game.stop_all_hud_anms(false)

-- Set the playback time of a running animation; returns current time as float
local t = game.set_hud_anm_time("anm_eat_bread", elapsed_seconds)

-- Check if HUD motion system is currently playing
local allowed = game.hud_motion_allowed()

-- Play a hand/motion animation (for items that have anm_ bones)
-- game.play_hud_motion(hand_id, section, animation_name, looped, speed)
game.play_hud_motion(1, "torch_section", "anm_switch", true, 0.75)

game.stop_hud_motion()

-- Get the total duration of an animation at a given speed (returns float seconds)
local duration_ms = game.get_motion_length("torch_section", "anm_switch", 1.0)
```

These are primarily used by item-use systems (eating, drinking, repairing) and the torch system. Most mods won't need to call them directly.

---

## Input restrictions

```lua
-- Restrict input to movement keys only (blocks fire, interact, etc.)
game.only_allow_movekeys(true)

-- Restore full input
game.only_allow_movekeys(false)

-- Query current state
local restricted = game.only_movekeys_allowed()

-- Allow/disallow climbing ladders
game.set_actor_allow_ladder(true)

-- Lower/restore weapon
game.actor_lower_weapon()
local lowered = game.actor_weapon_lowered()
```

---

## Tutorials

Tutorials are predefined UI hints defined in `configs/gameplay/tutorial.xml`. They can be triggered from script:

```lua
-- Start a named tutorial
game.start_tutorial("tutorial_campfire_extinguish")

-- Stop the currently active tutorial
game.stop_tutorial()

-- Check if any tutorial is currently running
if game.has_active_tutorial() then
    -- don't interrupt with other UI
end
```

---

## Night vision

```lua
-- Adjust the luminance factor for the night vision shader
game.set_nv_lumfactor(1.2)
```

---

## Preloading

```lua
-- Preload a model into memory to avoid hitching on first use
game.prefetch_model("actors\\stalker_dolg\\stalker_dolg")
```

---

## Language

```lua
-- Reload the current language XML files (useful after adding new text keys mid-session)
game.reload_language()
```

---

## UI utilities

```lua
-- Force a full reload of all HUD XML definitions (clears XML cache)
game.reload_ui_xml()

-- Convert a world-space position to 2D screen/UI coordinates
-- Returns: x, y (0.0–1.0 normalized screen coordinates), depth
local x, y, depth = game.world2ui(world_position)
local x, y, depth = game.world2ui_with_depth(world_position)

-- Convert UI coordinates back to world space
-- game.ui2world(screen_pos_vec, world_pos_out, vertex_id_out)
-- game.ui2world_offscreen(screen_pos_vec, world_pos_out, vertex_id_out)

-- Get a string of all supported display resolutions
local resolutions = game.get_resolutions()

-- Change how long game news messages (give_game_news) are visible on screen
-- value is in milliseconds
game.change_game_news_show_time(8000)
```

---

## Actor alcohol level

```lua
-- Returns the actor's current alcohol level (0.0–1.0)
local alcohol = game.get_actor_alcohol()
```

---

## Console commands

Any engine console command can be executed from Lua:

```lua
exec_console_cmd("save my_save_name")        -- trigger a named save
exec_console_cmd("hud_draw 0")               -- hide the HUD
exec_console_cmd("g_game_difficulty stalker") -- change difficulty
```

`exec_console_cmd` is a global helper defined in `_g.script`. It calls `get_console():execute(name)` and then fires the `on_console_execute` callback so other scripts can observe the command.

To **read** a console variable:

```lua
-- get_console_cmd(type, name)
-- type: 0=string, 1=bool, 2=float, other=token
local snd_vol = get_console_cmd(2, "snd_volume_eff")   -- returns float
local god_mode = get_console_cmd(1, "g_god")            -- returns bool
```

---

## Save file management

### Triggering a save

The engine does not expose a direct Lua save function. Use `exec_console_cmd` to trigger saves via the console:

```lua
exec_console_cmd("save my_save_name")    -- writes <saves folder>/my_save_name.scop
exec_console_cmd("save")                 -- quicksave (uses the current save name)
```

The save folder is typically `<game root>/appdata/savedgames/`. The filename is lowercase; do not include an extension.

!!! note "Autosaves"
    The base game's autosave system (`game_autosave_new.script`) uses this same pattern: `exec_console_cmd("save " .. (user_name() or "") .. " - tempsave")`. `user_name()` returns the Windows username.

### Deleting a save file

```lua
-- ui_load_dialog.delete_save_game(filename)
-- filename: lowercase, no extension (the .scop and .dds files are both removed)
ui_load_dialog.delete_save_game("my_save_name")
ui_load_dialog.delete_save_game("autosave")
```

Defined in `ui_load_dialog.script`. Deletes both the `.scop` save file and the associated `.dds` screenshot thumbnail.

**Single-slot save pattern** (used by ironman-style or other single-save-slot challenge modes):

```lua
local SAVE_NAME = "my_mod_save"

-- Flag set for the duration of our own exec_console_cmd call so that
-- on_console_execute can tell the difference between our save and an
-- external one that happens to use the same filename.
local save_in_progress = false

local function do_save()
    save_in_progress = true
    exec_console_cmd("save " .. SAVE_NAME)
    -- exec_console_cmd fires on_console_execute synchronously via
    -- SendScriptCallback, so save_in_progress is still true inside the
    -- handler and is reset to false only after it returns.
    save_in_progress = false
end

-- Intercept all saves and redirect to the single slot.
-- on_console_execute receives ("save", name_part1, name_part2, ...).
-- The save has already been written to disk when this fires.
local function on_console_execute(cmd, ...)
    if cmd ~= "save" then return end

    -- Skip saves we triggered ourselves (recursion guard).
    if save_in_progress then return end

    local save_name = string.lower(table.concat({ ... }, " "))

    -- Don't show UI warnings for engine/mod-generated autosaves or quicksaves.
    -- Use substring matching to handle name variations from different mods
    -- (e.g. "roced - autosave", "my_mod_autosave_slot1", etc.).
    local is_silent = save_name:find("autosave", 1, true)
                   or save_name:find("quicksave", 1, true)

    -- At this point you can check a zone condition, and either:
    --   (a) delete the save and warn the player, or
    --   (b) delete the wrong-name save and replace it with yours
    if not my_zone_check() then
        ui_load_dialog.delete_save_game(save_name)
        if not is_silent then
            actor_menu.set_msg(1, "Cannot save here!", 3)
        end
        return
    end

    ui_load_dialog.delete_save_game(save_name)
    do_save()
end
```

!!! warning "Use a flag, not a filename check, as the recursion guard"
    `exec_console_cmd` fires `on_console_execute` synchronously for every command it executes. If your handler calls `exec_console_cmd("save ...")`, the callback fires again immediately. **Do not guard against this by checking the save filename** — that would silently accept any external save that happens to use your slot name without checking your zone condition. Use a boolean flag set around the `exec_console_cmd` call instead, as shown above.

---

## Common patterns

### Translate a format string with values

```lua
-- Assuming the XML has: <text>Reward: %d roubles</text>
local msg = string.format(game.translate_string("my_mod_reward_fmt"), reward_amount)
db.actor:give_game_news("", msg, "ui\\ui_iconsTotal", 0, 5000)
```

### Game-time timer with callback

```lua
local finish_time = nil

local function actor_on_update()
    if finish_time and game.time() >= finish_time then
        finish_time = nil
        on_effect_expired()
    end
end

local function start_effect(duration_ms)
    finish_time = game.time() + duration_ms
end
```

### Check if it's a specific time of day

```lua
local function get_time_of_day()
    local h = level.get_time_hours()
    if h >= 6 and h < 12 then return "morning"
    elseif h >= 12 and h < 18 then return "afternoon"
    elseif h >= 18 and h < 22 then return "evening"
    else return "night"
    end
end
```

---

## See also

- [The Callback System](../scripting/callbacks.md) — timer patterns using game.time() inside callbacks
