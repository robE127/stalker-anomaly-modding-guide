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
-- Play a HUD animation file
-- game.play_hud_anm(anm_section, start_frame, speed, accel, looped)
game.play_hud_anm("anm_eat_bread", 0, 0.25, 1, false)

-- Stop all active HUD animations
game.stop_all_hud_anms()

-- Set playback time of a running animation
local length = game.set_hud_anm_time("anm_eat_bread", elapsed_seconds)

-- Play a hand/motion animation (for items that have anm_ bones)
-- game.play_hud_motion(hand_id, section, bone, looped, speed)
game.play_hud_motion(1, "torch_section", "anm_switch", true, 0.75)

game.stop_hud_motion()

-- Get the total duration of an animation at a given speed
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
