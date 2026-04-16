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
db.actor:set_health_ex(1.0)          -- set health to exact value
```

!!! note
    `change_health` takes a **delta** (positive or negative). `set_health_ex` takes an **absolute** value. Avoid reading `.health` and then writing back a computed value — prefer deltas to avoid race conditions with other mods.

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

-- Teleport the actor (use with caution)
db.actor:set_actor_position(new_position)
db.actor:set_actor_direction(angle_radians)
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
db.actor:move_to_ruck(item)           -- move item to backpack
db.actor:move_to_belt(item)           -- move item to belt
db.actor:move_to_slot(item, slot_num) -- equip item to a specific slot
db.actor:drop_item(item)              -- drop item on the ground
db.actor:transfer_item(item, npc)     -- give item to an NPC game_object
```

### Weight

```lua
db.actor:get_total_weight()           -- current carry weight
db.actor:get_actor_max_weight()       -- maximum carry weight
db.actor:set_actor_max_weight(value)  -- override max weight
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

-- Modify by delta
db.actor:change_character_rank(50)
db.actor:change_character_reputation(100)

-- Set to exact value
db.actor:set_character_rank(500)
db.actor:set_character_reputation(2000)
db.actor:set_character_community("freedom")

-- Faction goodwill
local goodwill = db.actor:community_goodwill("dolg")  -- -10000 to 10000
db.actor:set_community_goodwill("dolg", 1000)
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

-- Protection value for a given hit type
-- hit types: HIT_TYPE_BURN, HIT_TYPE_STRIKE, etc. (constants in _g.script)
local protection = db.actor:get_current_outfit_protection(HIT_TYPE_BURN)
```

---

## Particles

```lua
-- Attach a particle effect to a skeleton bone
db.actor:start_particles("anomaly\\electra_spell", "bip01_head")
db.actor:stop_particles("anomaly\\electra_spell", "bip01_head")
```

---

## Perception & visibility

```lua
-- Can the actor see this object right now?
if db.actor:see(npc_object) then
    -- actor has line of sight to the NPC
end

-- Ambient light level (useful for stealth systems)
local light = db.actor:get_luminocity()
local hemi  = db.actor:get_luminocity_hemi()
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

---

## Notes

- `db.actor` is the same object every time you access it during a session — you don't need to cache it, but you do need to guard against `nil`.
- All `game_object` base methods (`id()`, `name()`, `section()`, `position()`, `alive()`, etc.) are available on `db.actor` since it is a `game_object`.
- Condition properties (`.health`, `.radiation`, etc.) can technically be assigned directly, but this bypasses engine hooks. Prefer the `change_*` and `set_*_ex` methods.

---

## See also

- [game_object](../scripting/game-object.md) — base methods available on db.actor
- [alife](alife.md) — spawning items into the actor's inventory via alife_create_item
- [Callbacks Reference](../callbacks-reference/index.md) — actor_on_first_update, actor_on_item_take, and other actor callbacks
