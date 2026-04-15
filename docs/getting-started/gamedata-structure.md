# Gamedata Structure

Everything in Anomaly that a script mod can touch lives under `gamedata/`. Understanding this folder is essential — every file you create as a modder goes somewhere in this tree.

---

## How file loading works

Anomaly loads game data from two places, in order of priority:

1. **`gamedata/`** (your addon files, highest priority)
2. **`db/`** archives (packed base game files, lower priority)

If a file exists in `gamedata/`, the engine uses it instead of the packed version. This is how mods work: you place your file at the same relative path as the base game file, and the engine picks yours up automatically.

!!! warning "Never edit base game files directly"
    If you modify files inside `db/` archives directly, your changes are fragile and will break on game updates. Always put your files in `gamedata/` (or in your addon folder that gets merged in). The only exception is using the unpacker to *read* base game files as reference.

---

## Top-level folders

```
gamedata/
├── ai/          AI behaviour data
├── anims/       Camera animations and post-processing effects
├── configs/     All configuration files (LTX and XML)
├── levels/      Level/map data
├── meshes/      3D models and animations
├── scripts/     Lua source files ← most modding happens here
├── shaders/     Renderer shader source
├── sounds/      Audio files
├── spawns/      NPC and object spawn data
└── textures/    DDS texture files
```

---

## scripts/

This is where all Lua code lives. Every `.script` file in this folder is loaded by the engine at startup, in alphabetical order by filename.

!!! note "File extension"
    Despite the `.script` extension, these are standard Lua files. VS Code will treat them as Lua if you set up the file association from [Environment Setup](environment-setup.md).

**Your scripts go here.** Name them with a unique prefix to avoid collisions with other mods:

```
gamedata/scripts/my_mod_main.script
gamedata/scripts/my_mod_utils.script
```

### Key base game scripts

A selection of the most important base game scripts and their roles. These are the files to read when you want to understand how a system works.

| Script | Role |
|--------|------|
| `_g.script` | Runs first. Sets up the global environment: `RegisterScriptCallback`, `printf`, `IsWeapon`, `alife_create`, and ~300 other globals used everywhere. |
| `axr_main.script` | The addon framework. Owns the `intercepts` callback table. All `RegisterScriptCallback` calls route through here. |
| `db.script` | The central object registry. Defines `db.actor`, `db.storage`, `db.OnlineStalkers`, and the `add_obj`/`del_obj` lifecycle helpers. |
| `bind_stalker.script` | The actor (player) binder. Drives `actor_on_first_update`, `actor_on_update`, save/load, and all actor-level callbacks. |
| `bind_stalker_ext.script` | Actor callback dispatchers for item pickup/drop/use, outfit changes, hit events. |
| `bind_monster.script` | The generic NPC and monster binder. Handles NPC spawn, death, hit, and AI scheme setup. |
| `xr_logic.script` | The condition-list evaluator. Parses `{+info}`, `=func`, `%effect%` condlist syntax and drives NPC behaviour switching. |
| `xr_conditions.script` | Built-in condlist conditions (`+info_portion`, `=actor_in_zone`, etc.). |
| `xr_effects.script` | Built-in condlist effects (`%give_item%`, `%teleport_actor%`, etc.). |
| `axr_task_manager.script` | Quest/task system — creating, updating, and completing tasks. |
| `ui_mcm.script` | Mod Configuration Menu. Handles `on_mcm_load`, option storage, `ui_mcm.get`. |
| `utils_item.script` | Item utility functions — spawn helpers, section lookups, inventory tools. |
| `utils_ui.script` | UI utility functions — HUD messages, screen coordinates, icon helpers. |
| `utils_data.script` | Data serialization helpers — reading/writing typed values for save files. |
| `game_relations.script` | Faction relation system — getting and setting NPC/faction goodwill. |
| `news_manager.script` | In-game notification system — tips, task updates, item relocation messages. |
| `class_registrator.script` | Wires binder classes to entity types. Edited only when adding entirely new entity types. |

For a deeper look at how scripts interact at startup, see [Script Lifecycle](../scripting/script-lifecycle.md).

---

## configs/

All game data that isn't code is here. Broken into subfolders by category:

```
configs/
├── ai_tweaks/       AI behaviour adjustments
├── creatures/       NPC and monster definitions (stats, immunities, visuals)
├── environment/     Weather, sky, and lighting definitions
├── gameplay/        Task definitions, dialog trees, character profiles, faction data
├── items/
│   ├── items/       Consumables, ammo, attachments, artefacts
│   ├── outfits/     Armour and suits
│   ├── settings/    Global item system settings
│   ├── trade/       Trader inventories
│   └── weapons/     Weapon definitions
├── misc/            Sound settings, anomaly zones, HUD elements, and more
├── models/          Model visual properties
├── scripts/         Per-script configuration files read at runtime
├── text/
│   ├── eng/         English localization strings (XML)
│   └── rus/         Russian localization strings (XML)
└── ui/              UI layout definitions (XML)
```

### configs/items/weapons/ — example

Each weapon is defined in a `.ltx` file that specifies its stats, sounds, model paths, and more:

```
configs/items/weapons/
├── w_pistols.ltx
├── w_rifles.ltx
├── w_shotguns.ltx
├── w_smgs.ltx
└── ...
```

### configs/text/eng/ — example

Localization strings are XML files containing key/value pairs:

```xml
<string_table>
    <string id="my_mod_message">
        <text>Hello from my mod!</text>
    </string>
</string_table>
```

Reference by key in code: `game.translate_string("my_mod_message")`

---

## Other folders (brief)

| Folder | What you'll touch as a script modder |
|--------|--------------------------------------|
| `anims/` | Post-processing effect definitions (`.ppe` files) referenced in `level.add_pp_effector` calls |
| `sounds/` | `.ogg` audio files, referenced by section name in script sound configs |
| `textures/` | Rarely touched for pure script mods; needed for custom UI icons or item textures |
| `meshes/` | Only for mods that add custom 3D models |
| `levels/` | Only for map mods; not relevant for script/config work |
| `spawns/` | The `all.spawn` file controls initial world population; advanced topic |

---

## Your addon's folder structure

A well-structured addon mirrors the `gamedata/` layout exactly:

```
my_addon/
└── gamedata/
    ├── scripts/
    │   └── my_addon_main.script
    ├── configs/
    │   ├── scripts/
    │   │   └── my_addon_settings.ltx
    │   └── text/
    │       └── eng/
    │           └── my_addon_strings.xml
    └── ...
```

When installing, the contents of your `gamedata/` folder are merged into the game's `gamedata/`. Files at the same path override the base game version.
