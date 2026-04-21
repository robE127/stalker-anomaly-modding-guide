# db.actor

`db.actor` is the Lua representation of the player character — a `game_object` userdata value exposed by the engine. Nearly everything that affects the player goes through this object.

!!! warning "Availability"
    `db.actor` is `nil` until the first simulation tick. Never access it at script load time, in `load_state`, or in `on_game_load`. The first safe point is `actor_on_first_update`.

    ```lua
    -- Always guard before use in callbacks where timing is uncertain
    local function some_callback()
        if not db.actor then return end
        -- safe from here
    end
    ```

---

## Condition & status

These are **direct property accesses** — no parentheses. Values are normalised floats in the range `0`–`1`.

```lua
db.actor.health      -- current health (1.0 = full, 0.0 = dead)
db.actor.power       -- stamina
db.actor.radiation   -- radiation level
db.actor.psy_health  -- psychic health
db.actor.satiety     -- hunger (1.0 = full, 0.0 = starving)
db.actor.bleeding    -- bleeding rate
```

To **modify** these values, use the corresponding methods rather than direct assignment:

```lua
db.actor:change_health(0.2)          -- add 20% health
db.actor:change_health(-0.5)         -- remove 50% health
db.actor:change_power(delta)
db.actor:change_radiation(delta)
db.actor:change_satiety(delta)
db.actor:change_psy_health(delta)    -- modify psychic health by delta
db.actor:change_morale(delta)        -- modify morale by delta
db.actor:set_health_ex(1.0)          -- set health to exact value *(modded exes)*
```

!!! warning "`change_bleeding` is not available on the actor"
    `db.actor:change_bleeding(delta)` will crash with a nil method error at runtime. The method is only bound for NPC/monster game objects (it appears under the `-- NPCs` block in `lua_help.script`). To stop bleeding on the actor, use direct property assignment: `db.actor.bleeding = 0`.

!!! note
    `change_health` takes a **delta** (positive or negative). `set_health_ex` takes an **absolute** value and is added by the modded exes. Avoid reading `.health` and then writing back a computed value — prefer deltas to avoid race conditions with other mods.

### Clearing wounded state

When the actor's health reaches 0, the engine sets a `wounded` flag that persists even after health is restored — it causes hurt sounds to keep playing. Clear it explicitly after any death-cancel or respawn:

```lua
db.actor:wounded(false)   -- clear the wounded state
db.actor:wounded()        -- read the current state (returns boolean)
```

This must be called after health is restored, not before.

---

## Identity

```lua
db.actor:id()               -- unique numeric object ID
db.actor:name()             -- returns "actor"
db.actor:section()          -- character section (e.g. "actor_visual_stalker")
db.actor:alive()            -- true while the actor is alive
db.actor:character_name()   -- the player's character name string
```

---

## Position & movement

```lua
local pos = db.actor:position()      -- returns vector3 {x, y, z}
local dir = db.actor:direction()     -- facing direction (radians from north)

db.actor:level_vertex_id()           -- pathfinding vertex ID on the level mesh
db.actor:game_vertex_id()            -- game vertex (used for level-to-level transitions)

-- Bone position (e.g. for attaching effects)
local head_pos = db.actor:bone_position("bip01_head")
local bone_id  = db.actor:get_bone_id("bip01_head")  -- numeric bone ID for a named bone

-- Teleport the actor (use with caution)
db.actor:set_actor_position(new_position)
db.actor:set_actor_direction(angle_radians)  -- see angle convention below

-- Lighting (useful for stealth/visibility systems) *(modded exes)*
local light = db.actor:get_luminocity()       -- direct illumination level (0–1)
local hemi  = db.actor:get_luminocity_hemi()  -- ambient hemisphere illumination (0–1)
```

**`set_actor_direction` angle convention**

`set_actor_direction` takes a heading in radians, but the value returned by `direction():getH()` uses the opposite sign convention. Always negate it when copying a recorded heading back:

```lua
-- Record the player's current facing
local heading = -db.actor:direction():getH()   -- negate: converts engine heading to set_actor_direction angle

-- Apply it after a teleport
db.actor:set_actor_direction(heading)
```

The negation is confirmed from `sr_teleport.script` and `dialogs_warlab.script` in the base game. If you skip it, the player will face the wrong direction after the teleport.

To read your current heading from the console for use in config files:

```
run_string printf("heading=%s", -db.actor:direction():getH())
```

**Distance checks** are done on the returned vector:

```lua
local dist = db.actor:position():distance_to(other_object:position())
local dist_sq = db.actor:position():distance_to_sqr(other_object:position())
-- distance_to_sqr is cheaper when you only need to compare distances
if dist_sq < 4 then  -- within 2 metres
    -- ...
end
```

---

## Inventory

### Finding items

```lua
-- Get item by section name (first match)
local bandage = db.actor:object("bandage")

-- Get item in a specific equipment slot
local outfit   = db.actor:item_in_slot(7)   -- armour/suit slot
local helmet   = db.actor:item_in_slot(12)  -- helmet slot
local weapon1  = db.actor:item_in_slot(2)   -- primary weapon
local weapon2  = db.actor:item_in_slot(3)   -- secondary weapon

-- Currently active (held) item
local active = db.actor:active_item()
```

**Standard slot numbers:**

| Slot | Contents |
|------|----------|
| 2 | Primary weapon |
| 3 | Secondary weapon |
| 7 | Outfit / armour |
| 8 | PDA |
| 12 | Helmet |
| 13 | Backpack |

### Iterating inventory

```lua
-- iterate_inventory fires the callback for every item in the full inventory
db.actor:iterate_inventory(function(owner, obj)
    printf("item: %s", obj:section())
end, nil)  -- second arg is passed as first arg to callback

-- Collect all items of a given section
local function find_all(section)
    local found = {}
    db.actor:iterate_inventory(function(temp, obj)
        if obj:section() == section then
            found[#found + 1] = obj
        end
    end, nil)
    return found
end

-- Iterate only the ruck (backpack) or belt separately
db.actor:iterate_ruck(callback, arg)
db.actor:iterate_belt(callback, arg)
```

!!! note "Callback signature"
    The callback receives `(owner, item_object)`. `owner` is the actor itself. You cannot `break` out of an iteration early — if you need to stop early, use a flag and check it at the start of the callback.

### Moving and dropping items

```lua
db.actor:move_to_ruck(item)                    -- move item to backpack
db.actor:move_to_belt(item)                    -- move item to belt
db.actor:move_to_slot(item, slot_num)          -- equip item to a specific slot
db.actor:drop_item(item)                       -- drop item on the ground
db.actor:drop_item_and_teleport(item, pos)     -- drop item and teleport it to pos
db.actor:transfer_item(item, npc)              -- give item to an NPC game_object
db.actor:mark_item_dropped(item)               -- mark item as intentionally dropped *(modded exes)*
db.actor:make_item_active(item)                -- force an item into the active slot
```

### Belt

```lua
db.actor:belt_count()                          -- number of items on the belt
db.actor:item_on_belt(index)                   -- item at given belt index (0-based)
db.actor:is_on_belt(item)                      -- true if item is currently on the belt
db.actor:iterate_belt(callback, arg)           -- iterate belt items; callback(arg, item)
```

### Weight

```lua
db.actor:get_total_weight()           -- current carry weight (includes belt) *(modded exes)*
db.actor:get_inv_weight()             -- weight of items in the backpack only
db.actor:get_inv_max_weight()         -- maximum backpack capacity
db.actor:get_actor_max_weight()       -- absolute maximum carry weight (including belt)
db.actor:set_actor_max_weight(value)  -- override absolute max weight
db.actor:get_actor_max_walk_weight()  -- weight limit for normal movement speed
db.actor:set_actor_max_walk_weight(value)
```

---

## Money

```lua
local current = db.actor:money()         -- current ruble count

db.actor:give_money(500)                 -- add 500 roubles
db.actor:give_money(-200)                -- remove 200 roubles (take money)

db.actor:transfer_money(100, npc_object) -- transfer to an NPC
```

!!! warning "Taking money"
    `give_money(-amount)` can take money but won't go below zero — it clamps. Always check `db.actor:money() >= amount` before deducting.

---

## Info portions (quest flags)

Info portions are the engine's lightweight boolean flag system. They're used to track quest progress, world states, and one-time events. The IDs are defined in the `info_portions` config files.

```lua
-- Check
if db.actor:has_info("jup_b206_arrived_to_jupiter_with_old_faction_id") then
    -- ...
end

-- Grant
db.actor:give_info_portion("my_mod_quest_started")

-- Remove
db.actor:disable_info_portion("my_mod_quest_started")

-- Negation check (equivalent to not has_info)
if db.actor:dont_has_info("my_flag") then
    -- ...
end
```

Info portion IDs can be any string. For mod-owned flags, prefix with your mod name to avoid collisions with base game flags.

---

## Rank & reputation

```lua
-- Read
local rank    = db.actor:character_rank()         -- numeric rank value
local rep     = db.actor:character_reputation()   -- -4000 to 4000
local faction = db.actor:character_community()    -- e.g. "stalker", "freedom"

-- Modify by delta *(modded exes)*
db.actor:change_character_rank(50)
db.actor:change_character_reputation(100)

-- Set to exact value *(modded exes)*
db.actor:set_character_rank(500)
db.actor:set_character_reputation(2000)
db.actor:set_character_community("freedom")

-- Actor community goodwill
local goodwill = db.actor:community_goodwill("dolg")  -- -10000 to 10000
db.actor:set_community_goodwill("dolg", 1000)

-- Actor profile icon *(modded exes)*
db.actor:set_character_icon("ui_inGame2_Dolg_1")
```

---

## HUD notifications

```lua
-- News-style popup with icon
db.actor:give_game_news(
    "Title text",          -- header line
    "Body text",           -- message body
    "ui\\ui_iconsTotal",   -- texture path (ui section)
    0,                     -- delay before showing (ms)
    5000                   -- duration (ms)
)
```

For simpler in-world tips, most mods use `actor_menu.set_msg` (from `actor_menu.script`) which is lighter and doesn't require a texture:

```lua
-- actor_menu.set_msg(level, message, duration_seconds)
actor_menu.set_msg(1, "Something happened", 3)
```

---

## Outfit & equipment

```lua
local outfit = db.actor:get_current_outfit()  -- returns game_object or nil

-- Protection value for a given hit type *(modded exes)*
-- hit types: HIT_TYPE_BURN, HIT_TYPE_STRIKE, etc. (constants in _g.script)
local protection = db.actor:get_current_outfit_protection(HIT_TYPE_BURN)

-- Movement speed coefficients (all *(modded exes)*)
local jump   = db.actor:get_actor_jump_speed()       -- jump power
local sprint = db.actor:get_actor_sprint_koef()      -- sprint speed multiplier
local run    = db.actor:get_actor_run_coef()         -- run speed multiplier
local runbk  = db.actor:get_actor_runback_coef()     -- run-backward multiplier
db.actor:set_actor_jump_speed(value)
db.actor:set_actor_sprint_koef(value)
db.actor:set_actor_run_coef(value)
db.actor:set_actor_runback_coef(value)
```

---

## Weapon state

```lua
-- Weapon strap state
local strapped   = db.actor:weapon_strapped()    -- true if weapon is on back (not drawn)
local unstrapped = db.actor:weapon_unstrapped()  -- true if weapon is drawn
db.actor:hide_weapon()         -- holster the current weapon
db.actor:restore_weapon()      -- re-equip previously active weapon
db.actor:reload_weapon()       -- trigger a reload (call after unloading magazine)

-- Active slot
db.actor:active_slot()         -- index of the currently active equipment slot
db.actor:activate_slot(n)      -- switch to slot n
```

---

## Invulnerability

```lua
-- Check or set invulnerability (god mode)
local inv = db.actor:invulnerable()       -- returns bool
db.actor:invulnerable(true)               -- enable invulnerability
db.actor:invulnerable(false)              -- disable invulnerability
```

---

## Script control

```lua
-- Take/release scripted control of the actor
-- true = enable script control, string = script name for logging
db.actor:script(true, "my_mod_capture")
db.actor:script(false, "my_mod_capture")
local controlled = db.actor:get_script()  -- returns true if under script control
```

---

## Sight

```lua
-- Point the actor at a target or world position
-- Sight types defined in CSightParams constants (eSightTypeObject, eSightTypePosition, etc.)
db.actor:set_sight(target_game_object)
db.actor:set_sight(target_game_object, true)          -- with look-over flag
db.actor:set_sight(SightType, target_vector, bone_id) -- explicit direction
local sp = db.actor:sight_params()                    -- returns CSightParams object
```

---

## Particles

```lua
-- Attach a particle effect to a skeleton bone
db.actor:start_particles("anomaly\\electra_spell", "bip01_head")
db.actor:stop_particles("anomaly\\electra_spell", "bip01_head")
```

---

## Detector

```lua
local det = db.actor:active_detector()    -- currently held detector item (or nil) *(modded exes)*
db.actor:show_detector()                  -- show the detector HUD *(modded exes)*
db.actor:hide_detector()                  -- hide the detector HUD *(modded exes)*
db.actor:force_hide_detector()            -- force-hide (used during item animations) *(modded exes)*
```

---

## Perception & visibility

```lua
-- Can the actor see this object right now?
if db.actor:see(npc_object) then
    -- actor has line of sight to the NPC
end
```

---

## Dialog

```lua
if db.actor:is_talking() then
    -- in an active dialog
end

db.actor:run_talk_dialog(npc_object)  -- force-start dialog with NPC
db.actor:stop_talk()                  -- end current dialog
db.actor:allow_break_talk_dialog(true)
```

---

## Common patterns

### Safe access wrapper

Any callback that might fire before `actor_on_first_update` should guard against `nil`:

```lua
local function on_some_callback()
    if not db.actor then return end
    -- ... rest of handler
end
```

### Count items of a type

```lua
local function count_items(section)
    local count = 0
    db.actor:iterate_inventory(function(_, obj)
        if obj:section() == section then
            count = count + 1
        end
    end, nil)
    return count
end
```

### Check if player can afford something

```lua
local function can_afford(cost)
    return db.actor:money() >= cost
end

local function charge(cost)
    if not can_afford(cost) then return false end
    db.actor:give_money(-cost)
    return true
end
```

### One-time initialisation on load

```lua
local initialized = false

local function actor_on_first_update()
    if initialized then return end
    initialized = true

    -- db.actor is guaranteed available here
    local start_pos = db.actor:position()
    printf("[my_mod] actor at level: %s", level.name())
end
```

### Grant quest item and flag

```lua
local function start_my_quest()
    if db.actor:has_info("my_mod_quest_active") then return end

    -- Give the player an item and mark quest started
    alife_create_item("my_quest_item", db.actor)
    db.actor:give_info_portion("my_mod_quest_active")
    actor_menu.set_msg(1, "Quest started.", 3)
end
```

### Cancel death and respawn at a base

`actor_on_before_death` is a modded-exes callback that lets you intercept the death event before it completes.

```lua
local death_hour = nil

local function do_respawn()
    local hour = death_hour
    death_hour = nil

    -- night check, teleport, etc.
    -- ...

    -- Expire the invulnerability window now that the actor is safe.
    -- While this is active, actor_on_update forces bleeding=1 every frame,
    -- which overrides db.actor.bleeding=0 and causes hurt sounds.
    bind_stalker_ext.invulnerable_time = time_global() + 1
    return true
end

local function actor_on_before_death(who_id, flags)
    -- Cache any values needed by the deferred function now. Some queries
    -- (e.g. level.get_time_hours()) may return different values once
    -- deferred callbacks fire.
    death_hour = level.get_time_hours()

    flags.ret_value = false           -- cancel the death event (modded exes only)
    db.actor:set_health_ex(1.0)       -- health is 0 here; restore it before deferring
                                      -- or anything guarding on alive() will bail out

    -- Prevent re-death from residual damage during the respawn sequence.
    -- bind_stalker_ext.invulnerable_time is a non-local variable; while it is
    -- more than 7 seconds in the future, actor_on_update forces health=1 every frame.
    bind_stalker_ext.invulnerable_time = time_global() + 30000  -- 30 s window

    -- Do not teleport or change state here -- doing so in the same frame as the
    -- death event produces a floating camera bug. Defer by at least 1 second.
    CreateTimeEvent("my_mod", "respawn", 1, do_respawn)
end
```

### Same-map respawn: input and HUD after fade

If your deferred respawn uses a **cyclic blackout** (`level.add_pp_effector("black_infinite.ppe", id, true)`) and then **`set_actor_position`** on the **current** level (instead of `ChangeLevel`), test for a **post-respawn lock**: no movement, no mouse, sometimes with a normal-looking view.

After you **`level.remove_pp_effector`** on that fade ID, also:

1. **`level.enable_input()`** when available.
2. **`game.only_allow_movekeys(false)`** when **`game.only_movekeys_allowed()`** is true.
3. **`level.show_weapon(true)`** when you need the weapon mesh back.

Schedule the same cleanup again with **`CreateTimeEvent(..., 0, ...)`** so it runs on the **next** `ProcessEventQueue` tick; a single call is sometimes not enough depending on save / message ordering.

Put this cleanup in a small dedicated helper and call it once after teleport, then schedule the same helper on delay **0** for a second pass on the next tick.

See also: [Callbacks Reference — actor_on_before_death](../callbacks-reference/index.md#actor_on_before_death--critical-timing-notes).

---

## Notes

- `db.actor` is the same object every time you access it during a session — you don't need to cache it, but you do need to guard against `nil`.
- All `game_object` base methods (`id()`, `name()`, `section()`, `position()`, `alive()`, etc.) are available on `db.actor` since it is a `game_object`.
- Condition properties (`.health`, `.radiation`, `.power`, `.psy_health`) can be assigned directly as well as via `change_*` methods. Direct assignment bypasses some engine hooks, so prefer the `change_*` / `set_*_ex` methods for normal gameplay deltas. Direct assignment is the correct approach for bulk resets (e.g. after a respawn, when you want exact values immediately).
- **`.bleeding` must be set via direct assignment** (`db.actor.bleeding = 0`) — there is no `change_bleeding` method on the actor type.

---

## See also

- [game_object](../scripting/game-object.md) — base methods available on db.actor
- [alife](alife.md) — spawning items into the actor's inventory via alife_create_item
- [Callbacks Reference](../callbacks-reference/index.md) — actor_on_first_update, actor_on_item_take, and other actor callbacks
