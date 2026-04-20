# Smart Terrains

Smart terrains are the core scheduling system for NPC and mutant life in Anomaly's offline simulation.

At script level, a smart terrain is a server entity of class `se_smart_terrain` (defined in `smart_terrain.script`) that:

- registers itself in the simulation board (`SIMBOARD`)
- loads and owns a list of jobs
- tracks which NPC is assigned to which job
- evaluates respawn rules
- exposes itself as a simulation target for squads

---

## What a smart terrain actually is

A smart terrain is not "just a place marker." It is an active ALife object with logic.

In base scripts:

- `bind_smart_terrain.script` binds `clsid.smart_terrain` objects to `smart_terrain_binder`
- `smart_terrain_binder:update()` calls `self.se_smart_terrain:update()` every tick
- `se_smart_terrain:on_before_register()` and `:on_register()` register the terrain into:
  - `SIMBOARD` (`sim_board.script`)
  - `db.smart_terrain_by_id` (`db.script`)

This is why smart terrains participate directly in simulation decisions instead of being passive config entries.

---

## How squads use smart terrains

Squads (`sim_squad_scripted`) are assigned to smart terrains by the simulation board.

The main flow is:

1. `simulation_board:get_squad_target(squad)` picks candidate targets.
2. Smart terrains are filtered by `se_smart_terrain:target_precondition(squad)`.
3. `simulation_objects.evaluate_prior()` scores valid targets.
4. `simulation_board:assign_squad_to_smart(squad, smart_id)` moves the squad assignment.
5. On arrival, `se_smart_terrain:on_reach_target()` links the squad to that smart terrain.

Population caps are enforced with `max_population` (read from the terrain config and checked in target preconditions).

---

## Jobs: what NPCs do at a smart terrain

Each smart terrain owns job tables (stalker, monster, helicopter jobs).

`se_smart_terrain:load_jobs()`:

- calls `gulag_general.load_job(self)` to build a dynamic LTX with job sections
- inspects each job's `active` section
- resolves task anchors from logic fields like `path_walk`, `path_main`, `path_home`, `center_point`, or `path_move`
- builds `CALifeSmartTerrainTask` tasks for ALife routing

`se_smart_terrain:update_jobs()` and `:select_npc_job()` then:

- track arriving NPCs
- choose jobs based on availability and priority
- switch online NPC logic to the selected section via `xr_logic.configure_schemes()` / `xr_logic.activate_by_section()`

Important detail: job ownership is stored in `npc_by_job_section`, so one non-exclusive job section is owned by one NPC at a time.

---

## Config fields that matter most

`se_smart_terrain:read_params()` reads terrain behavior from the terrain's config (`smart_terrain` section).

Common high-impact fields:

- `max_population`, `min_population`
- `arrive_dist`
- `default_faction`, `faction_controlled`
- `respawn_idle`, `respawn_radius`
- `respawn_only_level`, `respawn_only_smart`
- `respawn_params` / `faction_respawn_num`
- `safe_restr`, `def_restr`, `spawn_point`

These values directly influence whether squads can target the terrain, when respawns happen, and how NPC jobs are initialized.

---

## Respawn behavior

Smart terrain respawn is handled in `se_smart_terrain:try_respawn()`.

A respawn only proceeds when key checks pass, including:

- terrain is enabled
- simulation availability allows it (`simulation_objects.available_by_id[self.id] ~= false`)
- actor is not too close (`respawn_radius` check on actor level)
- enough time has passed (`respawn_idle`)
- section limits in `respawn_params` have not been reached

When successful, the terrain typically spawns a squad through `SIMBOARD:create_squad(self, squad_section)` and tracks counts in `already_spawned`.

---

## Runtime access from your scripts

You can work with smart terrains as server entities:

```lua
local smart = db.smart_terrain_by_id[some_smart_id]
if smart then
    printf("smart: %s pop=%s/%s", smart:name(), SIMBOARD.smarts[smart.id].population, smart.max_population)
end
```

You can also identify smart terrain server objects by class:

```lua
local se_obj = alife_object(id)
if se_obj and se_obj:clsid() == clsid.smart_terrain then
    -- se_obj is a smart terrain
end
```

---

## Related simulation files worth reading

If you are modding smart terrain behavior, these are the core files:

- `scripts/smart_terrain.script` - terrain class, job assignment, respawn
- `scripts/sim_board.script` - smart/squad registry and assignment
- `scripts/sim_squad_scripted.script` - squad target logic and movement flow
- `scripts/simulation_objects.script` - target availability and priority scoring
- `scripts/bind_smart_terrain.script` - binder hookup and update bridge
- `scripts/db.script` - `db.smart_terrain_by_id` registration

For spawn presets, see `configs/misc/simulation.ltx` (smart section -> starting squad composition).

---

## Common modding pitfalls

- Do not treat smart terrains as online `game_object`s; they are primarily server entities in ALife logic.
- If a smart has missing/invalid job paths, `load_jobs()` can silently degrade behavior (NPCs fail to get useful tasks).
- `max_population` is enforced at simulation targeting time; adding squads elsewhere can still look "overcrowded" if you bypass normal assignment flow.
- `respawn_only_smart = true` prevents normal target selection for that terrain (`target_precondition()` returns `false`).

---

## See also

- [NPCs & Factions](npcs.md)
- [Engine Internals](../scripting/engine-internals.md)
- [What is db.storage?](../scripting/db-storage.md)
- [Glossary](../reference/glossary.md#smart-terrain)
