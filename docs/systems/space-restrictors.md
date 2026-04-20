# Space Restrictors

`space_restrictor` objects are named 3D volumes placed in a level. Scripts and AI use them as "areas with meaning": enter/leave triggers, safe zones, danger zones, and movement restrictions.

If you enabled debug overlays and saw names like `esc_2_12_stalker_wolf_kill_zone`, those are restrictor object names from level data.

---

## What they are used for

In practice, restrictors are used for four main jobs:

- **Actor area checks** - detect whether the player is inside specific zones.
- **Config-driven logic switches** - condlist fields like `on_actor_in_zone` transition logic sections when actor enters a named zone.
- **AI path constraints** - "in/out restrictions" limit where NPCs and monsters may path.
- **Map/mission trigger volumes** - fire scripted reactions when a level designer-defined area is entered.

---

## Adding your own restrictors

For most mods, this is the key distinction:

- You can **use** named restrictors from Lua at runtime.
- You generally cannot define a brand-new arbitrary 3D restrictor shape from Lua alone.
- The scripts expose `script_restr` / `script_zone` classes, but in base scripts and cloned mods there are no practical examples of spawning new restrictor volumes at runtime via `alife_create(...)`.

Creating new restrictor geometry is level-data work (SDK/editor pipeline), then scripts consume the final restrictor name.

### Practical workflow

1. **Create the restrictor in level data** (level editor / map pipeline) and give it a stable unique name like `my_mod_escape_safehouse_zone`.
2. **Ship that level data change** with your mod (or depend on a map add-on that provides it).
3. **Use the restrictor name in scripts/ltx**:
   - `db.actor_inside_zones["my_mod_escape_safehouse_zone"]`
   - `on_actor_in_zone = my_mod_escape_safehouse_zone | next_section`
4. **Verify in game** with `-dbg` and `Actor Inside Zone Info`.

### If you cannot edit level data

Use a script-defined spherical check as a fallback. You can still avoid per-frame work by throttling checks with a timer event:

```lua
local center = vector():set(-200.0, 0.0, 120.0)
local radius = 25.0

local was_inside = false

local function actor_in_fake_zone()
    if not db.actor then
        return false
    end
    return db.actor:position():distance_to_sqr(center) <= (radius * radius)
end

local function poll_fake_zone()
    local inside = actor_in_fake_zone()
    if inside and not was_inside then
        printf("[my_mod] entered fallback zone")
    elseif (not inside) and was_inside then
        printf("[my_mod] left fallback zone")
    end
    was_inside = inside
    return true
end

function on_game_start()
    -- Poll every 250 ms instead of every frame.
    CreateTimeEvent("my_mod", "poll_fake_zone", 250, poll_fake_zone)
end

function on_game_end()
    RemoveTimeEvent("my_mod", "poll_fake_zone")
end
```

This is useful for script-only distribution, but it is not the same as a true restrictor volume (no custom shape, no built-in restrictor name for condlist logic).

If you prefer the simpler per-frame style (acceptable for lightweight checks), use `actor_on_update` directly:

```lua
local center = vector():set(-200.0, 0.0, 120.0)
local radius = 25.0
local was_inside = false

local function actor_in_fake_zone()
    if not db.actor then
        return false
    end
    return db.actor:position():distance_to_sqr(center) <= (radius * radius)
end

local function actor_on_update()
    local inside = actor_in_fake_zone()
    if inside and not was_inside then
        printf("[my_mod] entered fallback zone")
    elseif (not inside) and was_inside then
        printf("[my_mod] left fallback zone")
    end
    was_inside = inside
end

function on_game_start()
    RegisterScriptCallback("actor_on_update", actor_on_update)
end

function on_game_end()
    UnregisterScriptCallback("actor_on_update", actor_on_update)
end
```

---

## Working with actor zone membership in Lua

The engine keeps a live table of restrictors the actor is currently inside:

- `db.actor_inside_zones[zone_name] = zone_game_object`

This table is updated by restrictor `zone_enter` / `zone_exit` callbacks in the base binder, so with real restrictors you are not doing geometric checks yourself each frame.

!!! tip "You do not need `actor_on_update` for true restrictors"
    `actor_on_update` polling is mainly a fallback for script-only fake zones (for example, distance-radius checks when you cannot ship map data). For actual `space_restrictor` objects, the engine callback path (`zone_enter` / `zone_exit` -> `db.actor_inside_zones`) already does the event tracking.

Use this for exact volume checks (better than distance checks, because restrictors are arbitrary shapes):

```lua
-- True while actor is inside this named restrictor
if db.actor_inside_zones["my_safe_zone"] then
    printf("actor is in my_safe_zone")
end
```

### Detect enter/leave events yourself

There is no universal "entered this specific zone" callback for every custom restrictor use case, so a common pattern is to diff membership over time:

```lua
local was_inside = false

local function actor_on_update()
    if not db.actor then
        return
    end

    local inside = db.actor_inside_zones and db.actor_inside_zones["my_safe_zone"] ~= nil

    if inside and not was_inside then
        printf("[my_mod] entered my_safe_zone")
    elseif (not inside) and was_inside then
        printf("[my_mod] left my_safe_zone")
    end

    was_inside = inside
end

function on_game_start()
    RegisterScriptCallback("actor_on_update", actor_on_update)
end

function on_game_end()
    UnregisterScriptCallback("actor_on_update", actor_on_update)
end
```

---

## Using restrictors in condlist logic (`.ltx`)

`xr_logic` supports zone-based section switching:

```ltx
[walker@guard]
path_walk = esc_guard_walk
path_look = esc_guard_look
on_actor_in_zone = esc_base_inner_zone | walker@warn

[walker@warn]
path_walk = esc_warn_walk
path_look = esc_warn_look
```

When the actor enters `esc_base_inner_zone`, logic switches to `walker@warn`.

Use this when you want map-driven behavior transitions without writing per-frame Lua checks.

---

## Restricting NPC movement (client object API)

For online NPC objects (`game_object`), you can add/remove movement restrictions directly:

```lua
-- Keep NPC inside one area and outside another
npc:add_restrictions("my_patrol_zone", "my_no_go_zone")

-- Later, clear those restrictions
npc:remove_restrictions("my_patrol_zone", "my_no_go_zone")
```

You can also inspect/reset current restriction sets:

```lua
local in_list = npc:in_restrictions()
local out_list = npc:out_restrictions()
npc:remove_all_restrictions()
```

---

## Restricting AI on server entities (ALife API)

For server-side entities (`se_*` objects), use `alife()` restriction functions:

```lua
local sim = alife()
local se_monster = sim:object(monster_id)
local restrictor_id = 12345

if se_monster then
    sim:add_in_restriction(se_monster, restrictor_id)
    sim:add_out_restriction(se_monster, restrictor_id)
end
```

And remove/clear later:

```lua
sim:remove_in_restriction(se_monster, restrictor_id)
sim:remove_out_restriction(se_monster, restrictor_id)
sim:remove_all_restrictions(monster_id, RestrictionSpace.eRestrictorTypeNone)
```

Use ALife restriction functions when you need behavior to persist/operate at the simulation layer (including objects that may be offline).

---

## Debugging restrictors quickly

- Enable **Debug HUD** + **Actor Inside Zone Info** with `-dbg` to see live zone names.
- Print current memberships:

```lua
for name, _ in pairs(db.actor_inside_zones or {}) do
    printf("inside_zone=%s", name)
end
```

- Verify a suspected restrictor object:

```lua
local obj = level.debug_object("esc_2_12_stalker_wolf_kill_zone")
if obj and obj:is_space_restrictor() then
    printf("found restrictor: %s id=%s", obj:name(), obj:id())
end
```

---

## Common pitfalls

- Restrictor names are level object names, not localized strings; they are often verbose/editor-generated.
- `db.actor_inside_zones` only tells you about the **actor**, not every NPC.
- Distance-to-point checks are not equivalent to restrictor membership for irregular volumes.
- Client-object restriction changes affect online objects; use ALife APIs when you need simulation-level persistence.

---

## See also

- [level](../api-reference/level.md)
- [game_object](../api-reference/game-object.md#type-testing)
- [alife](../api-reference/alife.md#restrictions-space-restrictors)
- [xr_logic](../api-reference/xr-logic.md#state-machine-switching-sections)
- [Debugging & Logging](../scripting/debugging.md#debug-hud-and-other-debug-settings)
