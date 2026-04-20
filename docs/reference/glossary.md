# Glossary

Anomaly modding uses a set of domain-specific terms that appear throughout the codebase. This page defines each one and links to more detailed coverage where it exists.

---

## alife

The **alife** ("artificial life") system is the offline simulation that manages all entities in the game world — squads, NPCs, anomalies, items — even when they are far from the player. When the player is nowhere near an entity, the alife simulator handles it: moving squads between [smart terrains](#smart-terrain), tracking deaths, running timed events.

In scripts, `alife()` returns the `CALifeSimulator` singleton — the central registry of all server entities.

See [Engine Internals → The alife simulator](../scripting/engine-internals.md#the-alife-simulator).

---

## binder

See [object binder](#object-binder).

---

## callback

A **callback** is a Lua function you register with the engine to be called when a specific event occurs — an NPC dies, the actor fires a weapon, a save is loaded. Anomaly's callback system is managed by `axr_main.script` via `RegisterScriptCallback` / `UnregisterScriptCallback`.

See [The Callback System](../scripting/callbacks.md) and the [Callbacks Reference](../callbacks-reference/index.md).

---

## clsid

A **clsid** (class ID) is an integer constant that identifies the C++ type of a game object or server entity. Type-checking in Lua is done by comparing `obj:clsid()` against constants in the global `clsid` table (e.g. `clsid.script_stalker`, `clsid.bloodsucker`). The `_g.script` helpers (`IsStalker()`, `IsMonster()`, etc.) wrap this pattern.

Server-side entities follow the naming convention `clsid.typename_s` (e.g. `clsid.bloodsucker_s`, `clsid.online_offline_group_s`). Online (client-side) objects use the bare name (e.g. `clsid.bloodsucker`).

```lua
local c = obj:clsid()
if c == clsid.script_stalker or c == clsid.script_actor then
    -- human NPC or actor
end

-- The helper functions in _g.script do this for you:
if IsStalker(obj, c) then ... end
```

---

## community

The **community** is the faction string used in scripts to identify which faction an NPC belongs to. Access it via `npc:character_community()`. Common values: `"stalker"`, `"freedom"`, `"duty"`, `"army"`, `"bandit"`, `"monolith"`, `"csky"`, `"ecolog"`, `"killer"`.

This is the internal identifier used in config files and [condition lists](#condition-list) — not the localised display name shown to the player.

---

## condition list

A **condition list** is a declarative mini-language embedded in LTX string fields. It lets AI logic, quest scripts, and NPC behaviour specify conditional transitions without writing Lua code.

The format is:

```
{+required_info -must_not_have =lua_check(arg)} target_section %+give_info =side_effect()%
```

- `{...}` — conditions evaluated to decide which entry matches
- The bare name after `}` — the value returned when conditions pass
- `%...%` — effects applied when this entry is chosen (optional)

Sigils inside `{...}` and `%...%`:

| Sigil | Meaning |
|-------|---------|
| `+info_id` | Actor must have this [info_portion](#info_portion) |
| `-info_id` | Actor must **not** have this info_portion |
| `=func(args)` | Call `xr_conditions.func()` — must return true |
| `!func(args)` | Call `xr_conditions.func()` — must return false |
| `~N` | Random: N% probability |
| `+info_id` in `%...%` | Give this info_portion as a side-effect |
| `-info_id` in `%...%` | Remove this info_portion |
| `=func(args)` in `%...%` | Call `xr_effects.func()` as a side-effect |

Multiple entries are chained with commas — the first entry whose conditions all pass is used:

```ini
; Switch to "sr_idle@timer" if both info_portions are set
on_info = {+base_defense_enemy_1_killed +base_defense_enemy_2_killed} sr_idle@timer

; Call a Lua function as a condition
on_info = {=surge_started} walker@surge, {=is_night} walker@sleep
```

Condition lists are parsed once at load by `xr_logic.parse_condlist()` and evaluated by `xr_logic.pick_section_from_condlist()`.

---

## db.actor

`db.actor` is the [`game_object`](#game_object) for the player's character. It is available from the `actor_on_first_update` callback onward and is `nil` before the first update tick.

See [db.actor reference](../api-reference/actor.md).

---

## db.storage

`db.storage` is a global Lua table that maps online object IDs to per-object state tables. [Object binders](#object-binder) populate it when entities come online and clean it up when they go offline.

See [What is db.storage?](../scripting/db-storage.md).

---

## gamedata

**gamedata** is the directory that holds all modifiable game assets — scripts, configs, textures, sounds, UI definitions. Anomaly loads files from `gamedata/` in preference to the base archives. Mods ship their files inside a `gamedata/` subfolder within their archive.

See [Gamedata Structure](../getting-started/gamedata-structure.md).

---

## game_object

A **game_object** is the Lua-side handle to an entity that is currently **online** (loaded near the player). It provides the full runtime API: position, animation, physics, AI state, and inventory. When an entity goes [offline](#online-offline), its `game_object` is destroyed — any stored reference becomes stale.

See [What is a game_object?](../scripting/game-object.md).

---

## game_vertex_id

A **game vertex** is a node in the global navigation graph that spans all levels. Unlike [level vertices](#level_vertex_id) (which are local to one map), game vertices allow the alife simulation to track entities across level boundaries. Access via `obj:game_vertex_id()` or `se_obj.m_game_vertex_id`.

---

## info_portion

An **info_portion** is a named boolean flag attached to the actor. It is either set or unset — there is no associated value. Info_portions are the primary mechanism for tracking quest state, dialog history, and one-time events.

```lua
db.actor:give_info_portion("my_quest_started")      -- set the flag
db.actor:has_info("my_quest_started")               -- check (returns bool)
db.actor:disable_info_portion("my_quest_started")   -- unset the flag
```

Info_portions are declared in XML files under `configs/gameplay/` (e.g. `info_portions.xml`). They appear as `+name` / `-name` sigils inside [condition list](#condition-list) blocks, and as `<has_info>` / `<dont_has_info>` / `<give_info>` tags in dialog XML files.

---

## level_vertex_id

A **level vertex** is a node in the AI navigation mesh (navmesh) for the current level. The navmesh is a graph of walkable positions — each vertex represents a point that AI can navigate to. `obj:level_vertex_id()` returns the ID of the navmesh node nearest to the object.

---

## modded exes

The **modded exes** are a community-maintained fork of the Anomaly engine by themrdemonized. They add Lua callbacks not present in vanilla Anomaly (`actor_on_weapon_fired`, `npc_shot_dispersion`, `bullet_on_hit`, `on_xml_read`, and several `actor_on_before_*` / `npc_on_before_*` variants), the `game_object:is_valid()` method, memory optimisations, and engine bug fixes.

Source: [xray-monolith on GitHub](https://github.com/themrdemonized/xray-monolith).

Features that require the modded exes are tagged **Exes** in the [Callbacks Reference](../callbacks-reference/index.md).

---

## object binder

An **object binder** is a Lua class (inheriting from `object_binder`) that attaches to a specific [`game_object`](#game_object) and receives per-object lifecycle callbacks: spawn, destroy, per-frame update, save, and load. The base game registers binders for all NPCs, monsters, the actor, helicopters, and anomaly zones.

See [Object Binders](../scripting/object-binders.md).

---

## online / offline

Every entity in Anomaly exists in one of two states:

- **Online** — the entity is within simulation distance of the player. A [`game_object`](#game_object) exists; the entity has physics, AI, and render presence.
- **Offline** — the entity is beyond the switch distance. Only the [server entity](#server-entity) exists; it is tracked by the alife simulator with no in-world representation.

The default switch distance is 750m, with a hysteresis gap (online at 675m, offline at 825m) to prevent rapid flickering at the boundary.

See [Engine Internals → Online and offline](../scripting/engine-internals.md#online-and-offline).

---

## section

"Section" has two distinct meanings in Anomaly, and both appear frequently in the codebase.

**Sense 1 — LTX block:** A `[section_name]` block in an LTX file. It is a named group of key-value pairs that defines something — an item, a weapon, a spawn template, AI logic. Example:

```ini
[medkit]
cost     = 850
inv_name = st_medkit
```

**Sense 2 — entity config type:** The config-section name of a specific object — the string returned by `obj:section()`. Every instance of a medkit returns `"medkit"` from `obj:section()`. This string is what you use to look up config data, check item type, or classify objects in script:

```lua
if obj:section() == "medkit" then
    -- this is a medkit
end
```

In both senses, a section is an identifier that maps to a block of config data. When reading code, "the object's section" usually means sense 2; "the LTX section" usually means sense 1.

See [LTX Format](../config-formats/ltx.md) for sense 1, and [What is a game_object?](../scripting/game-object.md) for sense 2.

---

## server entity

The **server entity** (Lua base type: `se_abstract`) is the permanent alife-side record for every entity. It exists from creation until the entity is released, regardless of [online/offline](#online-offline) state. Access it via `alife_object(id)`. It provides a limited API compared to [`game_object`](#game_object): section, position, vertex IDs, and spawn data — but no physics, animation, or inventory.

See [What is a game_object? → Client vs server](../scripting/game-object.md#client-vs-server-two-representations-of-the-same-entity).

---

## smart terrain

A **smart terrain** is a named alife zone that owns a set of **jobs** — scripted activities such as patrolling, sitting at a campfire, standing guard, or manning a post. NPCs do not pick destinations independently; the simulation board assigns [squads](#squad) to smart terrains, and the terrain assigns each NPC to one of its jobs.

From a modding perspective, smart terrains define where NPCs go and what they do when they get there. A terrain's LTX config specifies `max_population`, faction restrictions, job definitions (patrol paths, idle animations, etc.), and optional respawn behaviour.

Access from scripts: `db.smart_terrain_by_id[id]` returns the server entity.

See [Smart Terrains](../systems/smart-terrains.md) for the full system walkthrough.

---

## squad

A **squad** is the atomic unit of NPC grouping in the alife simulation. It is a server-side object (`sim_squad_scripted`) that owns one or more NPC server entities and moves as a unit between [smart terrains](#smart-terrain). Individual NPCs do not navigate the alife simulation independently — their squad does.

Squads have a faction, a current smart terrain, and a target smart terrain (evaluated as a [condition list](#condition-list)). Members are iterated with `for k in squad:squad_members() do` — `k.id` is the alife ID of each NPC server entity.

```lua
-- Find a named squad and iterate its members
local squad = get_story_squad("my_named_squad")
if squad then
    for k in squad:squad_members() do
        local npc = level.object_by_id(k.id)  -- nil if offline
        if npc then
            -- do something with the online NPC
        end
    end
end
```

---

## story_id

A **story_id** is a stable, human-readable string alias permanently bound to a specific alife entity — an NPC, squad, item, or smart terrain. Because numeric alife IDs are volatile (they can be reused across saves), story_ids are the correct way to reference specific named entities across save/load boundaries.

Story_ids are declared in spawn config LTX files:

```ini
[story_object]
story_id = bar_barman
```

Lookup functions in `_g.script`:

```lua
get_story_se_object("bar_barman")   -- server entity (always available)
get_story_object("bar_barman")      -- game_object (nil if offline)
get_story_object_id("bar_barman")   -- numeric alife ID
get_object_story_id(obj_id)         -- reverse lookup: numeric ID → story_id string
```

Story_ids must be globally unique across all mods. If two objects claim the same story_id, `story_objects.script` logs a warning and the second registration wins.
