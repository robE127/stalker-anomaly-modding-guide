# What is db.storage?

`db.storage` is a Lua table that holds the runtime state for every entity currently **online** (loaded in the game world). It maps object IDs to state tables, giving you a fast way to retrieve any online NPC's `game_object`, its current AI scheme, and any custom data your mod has attached to it.

```lua
-- The pattern you'll see everywhere:
local obj = db.storage[npc_id] and db.storage[npc_id].object
```

---

## Structure

`db.storage` is a plain Lua table keyed by integer object ID. Each entry is a state table (`st`) created when the object comes online:

```lua
db.storage[id] = {
    object        = <game_object>,  -- the live runtime handle
    pstor         = {},             -- persistent variables (survives save/load)
    pstor_ctime   = {},             -- persistent game-time variables
    active_scheme = "walk",         -- current AI scheme name
    active_section = "walker@base", -- current scheme section
    state_mgr     = <state_mgr>,    -- AI behaviour state machine
    move_mgr      = <move_mgr>,     -- movement manager
    -- ... plus per-scheme subtables added by each active scheme
}
```

The most important field by far is `.object` — the live `game_object` handle. Everything else is internal AI state you generally read but don't write unless you're building a scheme.

---

## Lifecycle

Entries are created and destroyed by the object binder system, not by your mod.

```
Object comes online (enters simulation radius)
  └─ binder:reinit() fires
       └─ db.storage[obj:id()] = {}   ← entry created

Object goes offline or is permanently removed
  └─ binder:net_destroy() fires
       └─ db.storage[obj:id()] = nil  ← entry removed
```

**Consequence:** an entry in `db.storage` means the object is currently online and its `game_object` handle is valid. No entry means the object is either offline or doesn't exist.

---

## Safe access pattern

Always double-check before dereferencing:

```lua
-- Step 1: check the storage entry exists
-- Step 2: check .object is non-nil
local obj = db.storage[id] and db.storage[id].object
if obj then
    -- obj is a valid, online game_object
end
```

This two-step check is necessary because:

- The storage entry may not exist (object is offline or was removed)
- The entry can exist briefly while `.object` is still being initialised

!!! danger "Never skip the nil check"
    ```lua
    -- CRASH if the NPC has gone offline
    db.storage[npc_id].object:position()

    -- Safe
    local obj = db.storage[npc_id] and db.storage[npc_id].object
    if obj then obj:position() end
    ```

---

## Common use cases

### Get an NPC's game_object by ID

The most frequent use of `db.storage` is converting a known ID to a live handle:

```lua
local function get_online_object(id)
    return db.storage[id] and db.storage[id].object
end

local npc = get_online_object(some_id)
if npc and npc:alive() then
    -- do something with the NPC
end
```

### Iterate all online stalkers

`db.OnlineStalkers` is a companion table that lists IDs of all currently online NPC stalkers:

```lua
for _, id in pairs(db.OnlineStalkers) do
    local npc = db.storage[id] and db.storage[id].object
    if npc and npc:alive() then
        printf("Online NPC: %s", npc:name())
    end
end
```

### Walk a squad's online members

```lua
local squad = get_object_squad(npc)  -- returns se_squad server object
if squad then
    for k in squad:squad_members() do
        local member = db.storage[k.id] and db.storage[k.id].object
        if member and member:alive() then
            -- member is online and alive
        end
    end
end
```

---

## Persistent per-NPC storage (pstor)

The `.pstor` table survives save and load. Use the `save_var` / `load_var` helpers from `_g.script` rather than writing to `.pstor` directly — they handle nil safety and type coercion:

```lua
-- Store a value on an NPC (persists through save/load)
save_var(npc, "my_mod_flag", true)

-- Read it back (returns nil if not set)
local flag = load_var(npc, "my_mod_flag")
if flag then
    -- NPC has been flagged
end
```

Under the hood these read and write `db.storage[npc:id()].pstor["my_mod_flag"]`. Accessing `.pstor` directly is fine but you must nil-check the storage entry first.

---

## Other tables on the `db` module

`db` is a module, not just storage. Other fields you'll encounter:

```lua
db.actor              -- the player's game_object (nil until actor_on_first_update)
db.storage            -- all online entities indexed by id
db.OnlineStalkers     -- array of online NPC IDs (stalkers only)
db.offline_objects    -- objects that are offline but tracked
db.smart_terrain_by_id  -- smart terrain objects by ID
db.zone_by_name       -- dynamic zones by name
db.anomaly_by_name    -- anomalies by name
```

`db.actor` is the most important — it's the same object as the return of `level.object_by_id(0)`, but cached for fast access.

---

## Online vs offline — when db.storage isn't enough

`db.storage` only covers online objects. For objects that may be offline, fall back to `alife_object()` for the server-side representation:

```lua
local id = some_npc_id

-- Try online first
local obj = db.storage[id] and db.storage[id].object
if obj then
    -- Full game_object available
    local pos = obj:position()
else
    -- Fall back to server entity (always available if alive)
    local se_obj = alife_object(id)
    if se_obj and se_obj:alive() then
        -- Limited info only: se_obj.position, se_obj:section_name()
        local pos = se_obj.position
    end
end
```

See [alife()](../api-reference/alife.md) for the full server-entity API.

---

## See also

- [What is a game_object?](game-object.md) — the `.object` field explained in depth
- [Object Binders](object-binders.md) — how db.storage entries are created (binder lifecycle)
- [alife()](../api-reference/alife.md) — accessing offline entities via server objects
- [NPCs & Factions](../systems/npcs.md) — practical NPC patterns using db.storage
