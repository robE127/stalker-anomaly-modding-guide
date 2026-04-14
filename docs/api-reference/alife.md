# alife

!!! note "Work in progress"
    This page is being written. Content coming soon.

`alife()` returns the A-Life simulation manager — the server-side layer that manages all entities in the game world, whether loaded or not.

## Topics to cover

- The client/server split in X-Ray: online (loaded, has a `game_object`) vs offline (server-side only, `CSE_ALifeDynamicObject`)
- `alife():object(id)` — get a server-side object by ID
- `alife():create(section, pos, lv_id, gv_id [, parent_id])` — spawn an entity
- `alife():release(obj, true)` — destroy a server-side entity
- `alife():actor()` — server-side actor object
- `alife():level_name(gv_id)` — resolve a level name from a game vertex ID
- The difference between `alife():object(id)` and `level.object_by_id(id)` — server vs client
- `server_entity_on_unregister` callback — fires when an entity is removed from the simulation
- Common patterns: spawning loot on NPC death, spawning squads, teleporting objects
