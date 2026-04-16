# level

The `level` global provides access to the currently loaded map — its objects, time, weather, navigation mesh, minimap, and visual effects. It is always available from `on_game_start` onward, but many of its functions only make sense when a level is actually loaded.

```lua
-- Check before calling level-specific functions in any context where a level might not be loaded
if level.present() then
    local name = level.name()
end
```

---

## Level information

```lua
level.name()       -- current map name, e.g. "l01_escape", "k00_marsh", "l08_yantar"
level.present()    -- true if a level is currently loaded (false on main menu)
level.game_id()    -- internal game ID
level.get_game_difficulty()           -- 0=novice, 1=stalker, 2=veteran, 3=master
level.set_game_difficulty(enum_val)   -- change difficulty; use game_difficulty constants
level.environment()                   -- returns the current environment manager object
level.get_bounding_volume()           -- returns Fbox defining the level's bounding box
```

The level name is how scripts distinguish which map the player is on. Level names match the folder names in `gamedata/levels/`:

```lua
local function is_in_zone(zone_levels)
    return zone_levels[level.name()] ~= nil
end

local dead_city_levels = { l10_radar = true, l10u_bunker = true }
if is_in_zone(dead_city_levels) then
    -- player is near the Brain Scorcher
end
```

---

## Object access

```lua
-- Retrieve any client-side game object by its numeric ID
local obj = level.object_by_id(id)  -- returns game_object or nil

-- Get the object the player is currently looking at (crosshair target)
local target = level.get_target_obj()
local dist   = level.get_target_dist()
local bone   = level.get_target_element()  -- bone ID under the crosshair

-- Find an object by name (debug/editor use)
level.debug_object("object_name")
level.debug_actor()             -- returns the actor game_object (do not use in production)
```

!!! warning "Do not use `level.actor()`"
    `level.actor()` logs an engine error message every call. Use `db.actor` instead.

`level.object_by_id` only works for **online** (client-side, currently simulated) objects. Use `alife():object(id)` for server-side (alife) entities.

---

## In-game time

The in-game clock runs independently of real time.

```lua
local hour   = level.get_time_hours()    -- 0–23
local minute = level.get_time_minutes()  -- 0–59
local day    = level.get_time_days()     -- current in-game day number

-- Time factor (how fast in-game time passes relative to real time)
local factor = level.get_time_factor()
level.set_time_factor(5)   -- 5× speed

-- Advance time by (days, hours, minutes)
level.change_game_time(0, 1, 0)   -- skip 1 game-hour forward
level.change_game_time(1, 0, 0)   -- skip 1 game-day forward

-- CTime object representing when the current level session started
local start = level.get_start_time()
```

For a full `CTime` timestamp, use `game.get_game_time()` instead (see the [game](game.md) page).

**Common time checks:**

```lua
local h = level.get_time_hours()
local is_night = (h >= 22 or h < 5)
local is_day   = (h >= 6 and h < 20)
```

---

## Weather

```lua
local current = level.get_weather()        -- e.g. "default", "cloudy", "rain"
level.set_weather("rain", true)            -- true = apply immediately, false = next cycle

-- Weather FX (special events: psi storms, blowouts, etc.)
level.set_weather_fx("fx_psi_storm_day")
level.stop_weather_fx()
local active = level.is_wfx_playing()      -- true while FX is running
local wfx_time = level.get_wfx_time()

level.start_weather_fx_from_time("fx_psi_storm_night", elapsed_time)

-- Rain intensity (0.0 = dry, 1.0 = heavy rain)
local rain = level.rain_factor()
local rain_vol = level.get_rain_volume()   -- rain audio volume (0.0–1.0)

-- Environment
local env_rads = level.get_env_rads()      -- environmental radiation (HUD sensor value)
```

---

## Post-processing effects

PP effectors are full-screen shader overlays loaded from `.ppe` files in `gamedata/anims/`.

```lua
-- Add an effect (id is an arbitrary integer you choose, used to remove it later)
level.add_pp_effector("radiation.ppe", 2020, true)   -- cyclic = true loops it

-- Adjust intensity while active (factor 0.0–1.0)
level.set_pp_effector_factor(2020, 0.5)

-- Remove it
level.remove_pp_effector(2020)

-- Some common base game PP IDs (avoid reusing these)
-- 2020 = radiation
-- 2012 = alcohol
-- 39568 = Yantar underground psi
```

Choose a unique numeric ID for your effects. Conflicts with other mods or the base game will cause unexpected effects to be removed prematurely.

---

## Camera effectors

Camera effectors play pre-built camera animation files (`.anm`), useful for recoil, impacts, or cinematic moments.

```lua
-- level.add_cam_effector(file, id, looped, sound, bone_tag, random_seed)
level.add_cam_effector("camera_effects\\headlamp\\headlamp.anm", 7539, false, "", 0, false)

level.remove_cam_effector(7539)

-- Complex effectors (predefined by name)
level.add_complex_effector("brighten", 1999)
level.remove_complex_effector(1999)
```

---

## Minimap markers

```lua
-- Add a marker to the minimap and full map
-- spot_type determines the icon (defined in map_spots.xml)
level.map_add_object_spot(obj_id, "secondary_object", "hint text")
level.map_add_object_spot_ser(obj_id, "treasure", "Stash text")  -- serialised (persists through save/load)

-- Check if a marker exists (returns 0 or 1 as a number, not boolean)
if level.map_has_object_spot(obj_id, "treasure") ~= 0 then
    -- marker is present
end

-- Remove a marker
level.map_remove_object_spot(obj_id, "treasure")

-- Update the hint text of an existing marker
level.map_change_spot_hint(obj_id, "secondary_object", "New hint text")
```

**Common spot types:**

| Spot type | Description |
|-----------|-------------|
| `"primary_object"` | Primary quest marker (large icon) |
| `"secondary_object"` | Secondary marker |
| `"treasure"` | Stash marker |
| `"fast_travel"` | Fast travel point |
| `"ui_pda2_mechanic_location"` | Mechanic location |

---

## Navigation mesh

```lua
-- Get the 3D world position of a nav mesh vertex
local pos = level.vertex_position(vertex_id)

-- Get the nearest nav mesh vertex to a world position
local vid = level.vertex_id(world_position)

-- Find a vertex in a given direction (for AI cover calculations)
local vid = level.vertex_in_direction(base_vertex_id, direction_vector, max_distance)

-- Cover height in a direction (0.0 = no cover, higher = more cover)
local hi = level.high_cover_in_direction(npc:level_vertex_id(), direction_vec)
local lo = level.low_cover_in_direction(npc:level_vertex_id(), direction_vec)

-- Check if a patrol path exists in the current level
if level.patrol_path_exists("esc_wolf_walk") then ... end

-- Client spawn manager (for deferred object spawns)
local mgr = level.client_spawn_manager()
-- mgr:add(id, version, callback, data)
-- mgr:remove(id, version)

-- Physics world (for applying impulses to physics objects)
local phys = level.physics_world()
```

---

## Nearby object iteration

```lua
-- Call func(obj) for every object within radius of position
level.iterate_nearest(position, radius, function(obj)
    printf("nearby: %s", obj:name())
end)
```

This is more efficient than iterating `db.storage` when you only care about a spatial region.

---

## Input & HUD control

```lua
-- Enable/disable all player input
level.enable_input()
level.disable_input()

-- Show/hide the HUD indicators (health, stamina bars, etc.)
level.show_indicators()
level.hide_indicators()
level.hide_indicators_safe()  -- safe version (won't crash if HUD not ready)

-- Show/hide the weapon model on-screen
level.show_weapon(true)

-- Simulate key press/release/hold
level.press_action(bind_to_dik(key_bindings.kWPN_ZOOM))
level.release_action(bind_to_dik(key_bindings.kWPN_ZOOM))
level.hold_action(bind_to_dik(key_bindings.kWPN_ZOOM))

-- Current actor movement state (returns a number, e.g. standing/crouching/sprinting)
local state = level.actor_moving_state()
```

---

## Sound

```lua
local vol = level.get_snd_volume()   -- current sound volume (0.0–1.0)
level.set_snd_volume(0.5)            -- set sound volume
local rain_vol = level.get_rain_volume()
```

---

## Deferred callbacks

```lua
-- level.add_call(check_fn, action_fn)
-- Registers check_fn to be called each tick; when it returns true, action_fn fires once
local function timer_done()
    return game.time() > end_time
end

local function on_timer_fired()
    printf("timer elapsed!")
end

level.add_call(timer_done, on_timer_fired)
```

This is a lightweight alternative to `actor_on_update` for one-shot deferred actions.

---

## Spawning

```lua
-- Spawn a client-side object immediately (online only, not tracked by alife)
-- level.spawn_item(section, position, level_vertex_id, game_vertex_id)
level.spawn_item("wpn_ak74", spawn_pos, lvid, gvid)

-- Spawn a phantom (internal engine entity, for visual effects)
level.spawn_phantom(position)

-- Preload sounds into memory before they are needed
level.prefetch_sound("weapons\\ak74\\ak74_shoot")

-- Iterate all sounds at a path (for distance-based mixing)
-- level.iterate_sounds(path, proximity, callback)
level.iterate_sounds("ambient\\zaton", 100, function(obj) ... end)
```

For spawning NPC and creature entities, prefer `alife_create` (see the [alife](alife.md) page).

---

## See also

- [game_object](../scripting/game-object.md) — the type returned by level.object_by_id
- [Engine Internals](../scripting/engine-internals.md) — the online/offline system that determines which objects level.object_by_id can find
