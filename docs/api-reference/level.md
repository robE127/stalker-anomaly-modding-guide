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
level.name()       -- current map name, e.g. "l01_escape", "l05_bar", "zaton"
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

**Known level name strings** (Anomaly 1.5.x):

| `level.name()` | Location | Notes |
|----------------|----------|-------|
| `l01_escape` | Cordon | Confirmed |
| `l02_garbage` | Garbage | Confirmed |
| `l03_agroprom` | Agroprom | Confirmed |
| `l03u_agr_underground` | Agroprom Underground | Confirmed |
| `l04_darkvalley` | Dark Valley | Confirmed |
| `l04u_labx18` | Lab X-18 | Confirmed |
| `l05_bar` | Rostok | Confirmed |
| `l06_rostok` | Wild Territory | Confirmed |
| `l07_military` | Army Warehouses | Confirmed |
| `l08_yantar` | Yantar | Confirmed |
| `l08u_brainlab` | Brain Scorcher (Yantar underground) | Confirmed |
| `l09_deadcity` | Dead City | Confirmed |
| `l10_limansk` | Limansk | Confirmed |
| `l10_radar` | Radar / CNPP | Confirmed |
| `l10_red_forest` | Red Forest | Confirmed |
| `l10u_bunker` | Radar Bunker | Confirmed |
| `l11_hospital` | Limansk Hospital | Confirmed |
| `l11_pripyat` | Pripyat (CoP south) | Confirmed |
| `l12_stancia` | Chernobyl NPP | Confirmed |
| `l12_stancia_2` | Chernobyl NPP (Sarcophagus approach) | Confirmed |
| `l12u_control_monolith` | Monolith Control (X18 Lab) | Confirmed |
| `l12u_sarcofag` | Sarcophagus | Confirmed |
| `l13_generators` | Generators | Confirmed |
| `l13u_warlab` | War Lab | Confirmed |
| `l23_x9` | Lab X-9 | Confirmed |
| `labx8` | Lab X-8 | Confirmed |
| `k00_marsh` | Great Swamp | Confirmed |
| `k01_darkscape` | Darkscape | Confirmed |
| `k02_trucks_cemetery` | Truck Cemetery | Confirmed |
| `zaton` | Zaton | Confirmed |
| `jupiter` | Jupiter | Confirmed |
| `jupiter_underground` | Jupiter Underground | Confirmed |
| `pripyat` | Pripyat (CoP north) | Confirmed |
| `y04_pole` | Meadow | Confirmed |
| `fake_start` | Floating Test Level | Confirmed |

Level names partly sourced from Fair Fast Travel `travel_destinations.ltx` `[northern_maps]` section and confirmed against in-game testing. Use `printf("[test] level: %s", level.name())` to verify level in game.

---

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

### Zone membership — db.actor_inside_zones

`db.actor_inside_zones` is a table (defined in `db.script`) that tracks which space restrictor zones the actor is currently inside. Keys are zone names (strings), values are the zone `game_object`s. Updated automatically by `bind_restrictor.script`:

```lua
-- Check if the actor is inside a specific zone right now
if db.actor_inside_zones["my_safe_zone_name"] then
    -- actor is inside the zone
end

-- Iterate all zones the actor is currently in
for zone_name, zone_obj in pairs(db.actor_inside_zones) do
    printf("inside zone: %s", zone_name)
end
```

This is more precise than a distance check because it respects the zone's actual shape (which may not be spherical). Zone names come from the level's `space_restrictor` objects, typically defined in `gamedata/levels/<level>/level.game`.

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

Two variants exist, distinguished by the `_ser` suffix:

| Function | Persistence |
|----------|-------------|
| `level.map_add_object_spot(id, type, label)` | **Session only** — removed when the game exits or the save is reloaded. |
| `level.map_add_object_spot_ser(id, type, label)` | **Serialised** — written into the save file and restored on load. Use this whenever the marker should survive a save/reload cycle. |

`id` must be the **server object ID** (from `alife_create(...).id` or `obj:id()` on a server object). Both functions accept the same spot type strings.

```lua
-- Session-only marker (disappears on reload)
level.map_add_object_spot(obj_id, "secondary_object", "hint text")

-- Persistent marker (survives save/load)
level.map_add_object_spot_ser(obj_id, "secondary_task_location", "Death: 14.04.2012 21:33")

-- Check if a marker exists (returns 0 or 1 as a number, not a boolean)
if level.map_has_object_spot(obj_id, "secondary_task_location") ~= 0 then
    -- marker is present
end

-- Remove a marker
level.map_remove_object_spot(obj_id, "secondary_task_location")

-- Update the hint text of an existing marker in place
level.map_change_spot_hint(obj_id, "secondary_object", "New hint text")
```

**Common spot types:**

| Spot type | Description |
|-----------|-------------|
| `"primary_object"` | Primary quest marker (large icon) |
| `"secondary_object"` | Secondary marker (smaller icon) |
| `"secondary_task_location"` | Secondary task location marker — used for custom markers such as death stash locations. Confirmed from community mods (Jabbers Soulslike, extraction_mod). |
| `"treasure"` | Stash marker |
| `"fast_travel"` | Fast travel point |
| `"ui_pda2_mechanic_location"` | Mechanic location |

Spot type strings are defined in `configs/ui/map_spots.xml`. That file lists every icon and its display name — grep it when you need an icon that isn't in the table above.

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

## Teleportation

### Same-level — set_actor_position

To move the actor to a different position **on the same level**, use the actor method directly:

```lua
db.actor:set_actor_position(new_position)  -- moves actor without a level reload
```

### Cross-level — ChangeLevel

`ChangeLevel` is a global helper (defined in `_g.script`) that sends an `M_CHANGE_LEVEL` network packet, triggering a full level transition:

```lua
-- ChangeLevel(position, level_vertex_id, game_vertex_id, angle_vector, use_animation)
ChangeLevel(target_pos, target_lvid, target_gvid, VEC_ZERO, false)
```

`VEC_ZERO` is a global constant (`vector():set(0,0,0)`) defined in `_g.script`.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `position` | `vector` | World-space destination position |
| `level_vertex_id` | `number` | Nav mesh vertex ID at the destination |
| `game_vertex_id` | `number` | Game vertex identifying the destination level |
| `angle` | `vector` | Facing direction at arrival (`VEC_ZERO` = default) |
| `use_animation` | `boolean` | `true` = fade to black with `sleep_fade.ppe`, 3-second deferred travel; `false` = immediate |

!!! warning "Execution stops immediately"
    `ChangeLevel` sends a net packet that fires the level change right away. **Any Lua code after the `ChangeLevel` call in the same block will not execute.** Put saves, messages, and any other work *before* the call.

    ```lua
    -- WRONG — the save never runs
    ChangeLevel(pos, lvid, gvid, VEC_ZERO, false)
    exec_console_cmd("save my_save")   -- never reached

    -- Correct
    exec_console_cmd("save my_save")
    ChangeLevel(pos, lvid, gvid, VEC_ZERO, false)
    ```

!!! warning "Do not use ChangeLevel for same-level travel"
    `ChangeLevel` causes the level to reload. When the source and destination are the same level, the actor binder does not reinitialise correctly, leaving the player as a floating camera with no HUD, no shadow, and no input. Use `db.actor:set_actor_position(pos)` for same-level teleportation. This is the same split used by `game_fast_travel.script`.

    ```lua
    if destination_level == level.name() then
        db.actor:set_actor_position(target_pos)
    else
        ChangeLevel(target_pos, target_lvid, target_gvid, VEC_ZERO, false)
    end
    ```

---

## See also

- [game_object](../scripting/game-object.md) — the type returned by level.object_by_id
- [Engine Internals](../scripting/engine-internals.md) — the online/offline system that determines which objects level.object_by_id can find
