# alife

`alife()` returns the A-Life simulation manager — the server-side layer that tracks every entity in the game world, whether currently loaded or not.

---

## The client/server split

Anomaly (like all X-Ray games) runs two parallel representations of the game world:

| | Client side | Server side |
|--|--|--|
| Object type | `game_object` | `se_abstract` (server entity) |
| Access | `level.object_by_id(id)` | `alife():object(id)` |
| Availability | Only when entity is **online** (within spawn distance) | Always — every entity is always in alife |
| Lua global | `db.storage[id].object` | `alife():object(id)` |

**Online** means the entity is close enough to the player that the engine has loaded it into the game world — it has a `game_object` and can be interacted with physically. **Offline** means it exists only in the simulation, tracked by position and faction but not physically present.

Most mod code works with client-side `game_object`s. The alife API is needed for:

- Spawning or destroying entities
- Reading data about offline NPCs (position, faction, squad)
- Teleporting entities anywhere in the world
- Accessing entities regardless of whether they're currently online

---

## Helpers from _g.script

The base game provides wrapper functions in `_g.script` that are safer and more convenient than calling `alife()` directly. **Always prefer these over the raw API.**

### alife_object(id)

```lua
local se_obj = alife_object(id)  -- returns server entity or nil
```

Safe wrapper around `alife():object(id)`. Returns `nil` if `id` is nil or the invalid sentinel `65535`.

### alife_create(section, pos_or_obj, [lid, gid, parent_id])

```lua
-- Spawn at a world position
local se_obj = alife_create("wpn_ak74", spawn_pos, level_vertex_id, game_vertex_id)

-- Spawn at the same location as an existing object
local se_obj = alife_create("device_pda", db.actor)

-- Spawn as a child of another object (adds to their inventory)
local se_obj = alife_create("bandage", db.actor:id())
```

### alife_create_item(section, recipient, [properties])

Specialized for inventory items. Creates the item and places it in the recipient's inventory.

```lua
-- Give the player an item
local se_item = alife_create_item("bandage", db.actor)

-- Give with specific condition and uses
local se_item = alife_create_item("wpn_ak74", db.actor, {
    cond = 0.8,   -- 80% condition
    ammo = 30,    -- ammo count
})

-- Give to an NPC (game_object)
alife_create_item("stalker_outfit", npc_game_object)
```

### alife_release(se_obj_or_game_obj, [reason_string])

```lua
-- Destroy a server entity
alife_release(se_obj)

-- Destroy from a client game_object (auto-converts)
alife_release(game_obj)

-- With a debug reason string (logged)
alife_release(se_obj, "quest_complete_cleanup")
```

Handles NPCs in squads automatically — removes the NPC from their squad before releasing. Safe to call with `nil` (returns `false`).

### alife_release_id(id, [reason])

```lua
alife_release_id(object_id, "my_mod cleanup")
```

Convenience form: looks up the server entity by ID and releases it.

---

## Raw alife() methods

### Object lookup

```lua
local se_obj = alife():object(id)       -- nil if not found
local se_actor = alife():actor()        -- server-side player entity
local se_story = alife():story_object(story_id)  -- look up by story ID
```

### Spawning

```lua
-- alife():create(section, position, level_vertex_id, game_vertex_id [, parent_id])
local se_obj = alife():create(
    "stalker_helper",  -- config section
    position,          -- vector3
    level_vertex_id,   -- number
    game_vertex_id     -- number
)
```

Returns the new server entity object, or errors if the section is invalid.

### Destroying

```lua
alife():release(se_obj)        -- destroy the server entity
alife():release(se_obj, true)  -- force release
```

### Teleportation

```lua
-- Move an object anywhere in the world, including other levels
alife():teleport_object(id, new_position, new_level_vertex_id, new_game_vertex_id)
```

### Online/offline control

```lua
-- Force an entity to stay online (won't despawn when player moves away)
alife():set_switch_online(id, true)
alife():set_switch_offline(id, false)  -- disable despawning

-- Restore normal behavior
alife():set_switch_online(id, false)
alife():set_switch_offline(id, true)
```

Useful for containers or NPCs that must remain interactable.

### Spawn distance

```lua
local dist = alife():switch_distance()     -- current spawn radius
alife():set_switch_distance(200)           -- widen/narrow spawn zone
```

---

## Server entity (se_abstract)

Objects returned by `alife():object()` and `alife_object()` are server entities. They have a different (smaller) API than client `game_object`s.

### Common properties

```lua
se_obj.id                  -- numeric ID (same as client object's id())
se_obj.parent_id           -- owner ID (65535 = no owner / world)
se_obj.position            -- vector3 world position
se_obj.m_level_vertex_id   -- nav mesh vertex
se_obj.m_game_vertex_id    -- game vertex (identifies the level)
se_obj.group_id            -- squad ID (for NPCs)
se_obj.remaining_uses      -- for multi-use objects
```

### Common methods

```lua
se_obj:section_name()      -- config section (e.g. "stalker_bandit")
se_obj:name()              -- object name string
se_obj:clsid()             -- class ID (use clsid constants from _g.script)
se_obj:alive()             -- is entity alive? (NPCs/creatures)
se_obj:community()         -- faction string (NPCs)
se_obj:level_id()          -- which level this entity is on
se_obj:level_vertex_id()   -- nav vertex
se_obj:game_vertex_id()    -- game vertex
```

### Squad methods

Squads are also server entities. Methods specific to squad objects:

```lua
for member in se_squad:squad_members() do
    printf("member id: %d", member.id)
end

local leader_id = se_squad:commander_id()
local count     = se_squad:npc_count()
se_squad:remove_npc(npc_id)
se_squad:remove_squad()     -- disband the squad
```

---

## Common patterns

### Spawn loot on NPC death

```lua
local function npc_on_death_callback(victim, who)
    local se_vic = alife_object(victim:id())
    if not se_vic then return end

    alife_create_item("bandage",    victim)
    alife_create_item("conserva",   victim)
end
```

Note: items given to `victim` (the dying client object) before it goes offline end up on the ground at its position.

### Spawn a world object at a position

```lua
local function spawn_at_actor(section)
    local pos  = db.actor:position()
    local lvid = db.actor:level_vertex_id()
    local gvid = db.actor:game_vertex_id()
    return alife_create(section, pos, lvid, gvid)
end
```

### Check if entity is online right now

```lua
local function is_online(id)
    -- level.object_by_id only returns something if the entity is online
    return level.object_by_id(id) ~= nil
end
```

### Teleport an item to the player

```lua
local function pull_to_actor(id)
    local pos  = db.actor:position()
    local lvid = db.actor:level_vertex_id()
    local gvid = db.actor:game_vertex_id()
    alife():teleport_object(id, pos, lvid, gvid)
end
```

### Give an item only if the player doesn't already have one

```lua
local function ensure_has(section)
    if db.actor:object(section) then return end  -- already has it
    alife_create_item(section, db.actor)
end
```

---

## Key differences from client objects

| Task | Client (game_object) | Server (se_abstract) |
|------|---------------------|----------------------|
| Get by ID | `level.object_by_id(id)` | `alife_object(id)` |
| Position | `obj:position()` | `se_obj.position` |
| Section | `obj:section()` | `se_obj:section_name()` |
| Alive check | `obj:alive()` | `se_obj:alive()` |
| Availability | Online only | Always |
| Spawn | — | `alife_create(...)` |
| Destroy | — | `alife_release(...)` |

!!! warning "Never mix the two"
    `level.object_by_id` returns a `game_object` or `nil`. `alife():object()` returns an `se_abstract` or `nil`. They are different types — methods from one will not work on the other.
