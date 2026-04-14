# NPCs & Factions

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- NPC vs monster — different class hierarchies, different callbacks
- `npc_on_death_callback(victim, who)` — most common NPC callback (41 uses); `victim` and `who` are `game_object`
- `npc_on_before_hit(npc, hit, bone_id)` — intercept and modify incoming hits
- `monster_on_death_callback` — same pattern for mutants
- Squad system: `se_simulated_squad` server object, getting a squad from an NPC
- `db.storage[id]` — per-NPC Lua state table, where scripts store NPC-local data
- Faction relations: `game_relations.get_npcs_relation`, setting and getting goodwill
- Spawning an NPC squad: `alife():create_squad(section, smart_terrain_id)`
- `server_entity_on_unregister` — cleanup when any entity (including NPCs) is removed
- Dialog callbacks: triggered from XML dialog trees via `precondition` and `action` scripts
