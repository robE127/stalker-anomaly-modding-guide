# What is a game_object?

`game_object` is the most important type in Anomaly scripting. Almost every interaction with the game world — checking if an NPC is alive, reading an item's section name, getting the actor's position — goes through a `game_object`. It's the Lua-side handle to an entity that currently exists in the simulated world.

---

## Client vs server: two representations of the same entity

Every entity in Anomaly has **two representations** that exist for different purposes.

| | `game_object` | `se_abstract` |
|---|---|---|
| Also called | Client object, runtime object | Server entity, alife object |
| Exists when | The entity is **online** (loaded near the player) | Always — even when far away |
| Access | `level.object_by_id(id)`, `db.actor`, callback arguments | `alife_object(id)` |
| Has | Full methods: position, animation, physics, inventory, AI | Limited data: section, position, vertex IDs, group |
| Use for | Real-time behaviour, reading/writing state, combat | Persistence, spawning, teleporting, offline tracking |

```lua
local id = victim:id()

-- game_object — exists only while the NPC is loaded
local obj = level.object_by_id(id)   -- returns nil if offline

-- se_abstract — always available
local se_obj = alife_object(id)       -- returns nil only if dead/removed
```

When a script callback hands you an NPC or item directly (e.g. `npc_on_death_callback(victim, who)`), you already have the `game_object`. You don't need to look it up.

---

## Core methods

These methods exist on every `game_object` regardless of type.

### Identity

```lua
obj:id()          -- integer: unique object ID (stable for the save's lifetime)
obj:name()        -- string: engine-assigned instance name, e.g. "stalker_freedom_3"
obj:section()     -- string: config section, e.g. "wpn_ak74" or "medkit"
obj:clsid()       -- integer: class ID (use with clsid.* constants or type helpers)
```

`:section()` is what you use to look up config values — it's the `[section_name]` from the LTX files. `:name()` is the instance name assigned by the engine and is not useful for config lookups.

### Position

```lua
obj:position()              -- vector: world-space position {x, y, z}
obj:direction()             -- vector: facing direction
obj:level_vertex_id()       -- integer: AI navigation mesh node
obj:game_vertex_id()        -- integer: global graph vertex (for level transitions)
obj:distance_to(pos)        -- float: distance to a vector
obj:distance_to_sqr(pos)    -- float: squared distance (faster for comparisons)
```

```lua
-- Distance check without a square root
if npc:distance_to_sqr(db.actor:position()) < 100 then  -- < 10 metres
    -- close enough
end
```

### Liveness

```lua
obj:alive()   -- bool: true if the entity is alive
```

!!! warning "`:alive()` vs `alife_object():alive()`"
    For NPCs and monsters that could be going offline, prefer checking the server entity:
    ```lua
    local se_obj = alife_object(obj:id())
    if se_obj and se_obj:alive() then
        -- reliable even if the object is transitioning online/offline
    end
    ```
    Calling `:alive()` directly on a `game_object` is fine in most callback contexts where you know the object is currently online.

---

## Type-checking

`clsid()` returns a raw integer, which is awkward to work with directly. `_g.script` provides helper functions that map clsids to readable predicates. Pass an optional cached clsid as the second argument to avoid calling `:clsid()` twice:

```lua
local c = obj:clsid()

IsStalker(obj, c)     -- human NPC or the player actor
IsMonster(obj, c)     -- bloodsucker, boar, pseudodog, chimera, etc.
IsAnomaly(obj, c)     -- zone anomaly
IsTrader(obj, c)      -- trader NPC
IsWeapon(obj, c)      -- any weapon
IsPistol(obj, c)      -- handgun subtype
IsRifle(obj, c)       -- assault rifle subtype
IsShotgun(obj, c)     -- shotgun subtype
IsSniper(obj, c)      -- sniper rifle subtype
IsLauncher(obj, c)    -- rocket/grenade launcher subtype
IsMelee(obj, c)       -- knife
IsAmmo(obj, c)        -- ammo box
IsGrenade(obj, c)     -- throwable grenade
IsArtefact(obj, c)    -- artefact
IsOutfit(obj, c)      -- body armour
IsHeadgear(obj, c)    -- helmet
IsExplosive(obj, c)   -- placed explosive
IsInvbox(obj, c)      -- inventory box (stash, corpse container)
IsBolt(obj, c)        -- bolt
IsCar(obj, c)         -- vehicle
IsHelicopter(obj, c)  -- helicopter
```

For items with a known section name, `IsItem` does a config-table lookup:

```lua
-- Check if obj is a specific category of item by its section
IsItem("eatable", nil, obj)    -- consumable food/drug
IsItem("explosive", nil, obj)
```

### Typical pattern — iterating nearby objects

```lua
local function actor_on_update()
    level.iterate_nearest(db.actor:position(), 5, function(obj)
        local c = obj:clsid()
        if IsArtefact(obj, c) then
            -- found an artefact within 5 metres
        end
    end)
end
```

---

## Getting a game_object

There are several ways to obtain one:

```lua
-- The player actor (available from actor_on_first_update onward)
db.actor

-- Any online object by ID (returns nil if offline or doesn't exist)
local obj = level.object_by_id(id)

-- Online NPCs — db.storage maps id → {object = game_object, ...}
local obj = db.storage[id] and db.storage[id].object

-- Directly from callback arguments
local function npc_on_death_callback(victim, who)
    -- victim and who are both game_objects
end

-- Active item in a slot (db.actor only)
local active_weapon = db.actor:item_in_slot(2)   -- slot 2 = primary weapon

-- Find an item in actor's inventory by section
local medkit = db.actor:object("medkit")
```

---

## Stalker-specific methods

These methods only make sense on `game_object`s where `IsStalker()` returns true:

```lua
npc:character_community()   -- string: faction, e.g. "freedom", "duty", "stalker"
npc:alive()                 -- bool
npc:critically_wounded()    -- bool: in a severely wounded state
npc:in_smart_cover()        -- bool: using a cover node
npc:best_enemy()            -- game_object or nil: current combat target
npc:relation(other)         -- integer: game_object.friend / .neutral / .enemy
npc:is_talking()            -- bool: in an active dialog
npc:stop_talk()             -- end active dialog
```

```lua
-- Check faction and relation before doing something
local function npc_on_death_callback(victim, who)
    if not (who and who:id() == db.actor:id()) then return end
    if victim:character_community() == "monolith" then
        -- player killed a monolith NPC
    end
end
```

---

## Actor-specific methods

`db.actor` is a `game_object` with additional methods only available on the actor:

```lua
db.actor:has_info("info_id")             -- bool: actor has this info portion
db.actor:give_info_portion("info_id")    -- grant an info portion
db.actor:disable_info_portion("info_id") -- revoke an info portion
db.actor:give_money(amount)              -- add money
db.actor:give_game_news(...)             -- show an in-world notification
db.actor:iterate_inventory(fn, data)     -- walk every item in inventory
db.actor:item_in_slot(n)                 -- game_object in slot n, or nil
db.actor:object("section")              -- first matching item in inventory, or nil
```

---

## Safety patterns

### Always nil-check `level.object_by_id`

An object can go offline between the time you stored its ID and the time you use it:

```lua
local function do_something_with(id)
    local obj = level.object_by_id(id)
    if not obj then return end        -- object went offline or was removed
    if not obj:alive() then return end
    -- safe to proceed
end
```

### Cache the clsid when checking multiple types

```lua
local c = obj:clsid()
if IsStalker(obj, c) or IsMonster(obj, c) then
    -- creature of some kind
end
```

### Don't store `game_object` references across frames

`game_object` handles can become stale at any time. Store the **ID** and look up a fresh handle when you need it.

```lua
-- BAD: storing a game_object reference between frames
local tracked = some_npc   -- may become invalid

-- GOOD: store the ID, look up fresh each time
local tracked_id = some_npc:id()

local function actor_on_update()
    local obj = level.object_by_id(tracked_id)
    if obj and obj:alive() then
        -- fresh handle, safe to use
    end
end
```

??? info "Why references go stale — engine details (modded exes source)"
    Based on the [xray-monolith](https://github.com/themrdemonized/xray-monolith) C++ source (the community modded exes — vanilla engine internals cannot be verified): `game_object` in Lua is a wrapper (`CScriptGameObject`) that holds a pointer to the underlying C++ entity (`CGameObject`). When an object goes offline (because the player moved away, or the object was destroyed), the engine calls `net_Destroy()`, which:

    1. Calls the object binder's `net_destroy()` method (your Lua cleanup code runs here)
    2. **Deletes** the Lua wrapper object (`CScriptGameObject`)
    3. Sets `m_spawned = false` on the C++ object

    After this, any Lua reference you held to that `game_object` now points to freed memory. The modded exes provide a `game_object:is_valid()` method that checks whether the back-reference between the wrapper and the C++ object is still intact — but the safest pattern is to never store the reference at all.

### Checking validity with `is_valid()`

!!! note "Requires the modded exes"
    `is_valid()` is added by the [modded exes](https://github.com/themrdemonized/xray-monolith) and is not available in vanilla Anomaly.

If you must hold a `game_object` reference temporarily (e.g. within a single complex operation), you can check whether it's still valid:

```lua
if obj:is_valid() then
    -- safe to use
end
```

`is_valid()` returns `false` if the underlying C++ object has been destroyed or if the Lua wrapper has been detached. It is not a substitute for storing IDs — it's a safety net for edge cases where you're holding a reference briefly and need to guard against mid-operation destruction.

---

## See also

- [db.actor](../api-reference/actor.md) — the player's game_object in detail
- [alife()](../api-reference/alife.md) — working with `se_abstract` server entities
- [The Callback System](callbacks.md) — how game_objects arrive as callback arguments
- [NPCs & Factions](../systems/npcs.md) — NPC-specific patterns
