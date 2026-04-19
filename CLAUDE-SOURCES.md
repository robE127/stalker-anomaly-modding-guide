# Research Sources — Full Reference

## 1. Base game scripts (highest authority)

**Primary — fully unpacked Anomaly installation:**
```
data/clones/Anomaly-<version>-Full/tools/_unpacked/scripts/
data/clones/Anomaly-<version>-Full/tools/_unpacked/configs/
```
Use the highest version present in `data/clones/`. No `gamedata/` prefix — scripts sit directly under `_unpacked/`.

**Fallback — Tosox Anomaly 1.5.2 (older, use only if no unpacked install present):**
```
data/clones/Tosox__STALKER-Anomaly-gamedata/gamedata/scripts/
data/clones/Tosox__STALKER-Anomaly-gamedata/gamedata/configs/
```

**Key files:**
- `_g.script` — global environment, helper functions, `alife_create`, `IsWeapon`, `exec_console_cmd`, etc.
- `axr_main.script` — complete callback registration table (authoritative callback list)
- `xr_logic.script` — condition list evaluator and NPC behaviour
- `bind_stalker_ext.script` — actor binder, item callbacks
- `utils_item.script`, `utils_ui.script`, `utils_data.script` — utility modules

## 2. Community mod analysis

```
data/analysis/index.json       — cross-repo callback and API frequency counts
data/analysis/<repo>.json      — per-repo extracted callbacks, functions, API calls
data/repos.json                — scored list of 214 scanned repos with metadata
```

Use `index.json` to find what's actually important to document. Use per-repo JSON and cloned repos for real usage patterns.

**Notable clones:**
- `data/clones/nltp-ashes__Nanosuit/` — complex multi-system mod
- `data/clones/nltp-ashes__Western-Goods/` — full quest and economy mod
- `data/clones/themrdemonized__STALKER-Anomaly-Mugging-Squads/` — NPC squad manipulation
- `data/clones/explorerbeer__tactical_compass/` — HUD and UI patterns
- `data/clones/Grokitach__Stalker_GAMMA/` — DLTX usage examples
- `data/clones/AlienProductGames__SCP-Faction-WIP/` — DXML usage examples
- `data/clones/TheParaziT__anomaly-modding-book/` — existing community docs (credit this)

**If a clone is missing:** check `data/repos.json` for the `html_url`, fetch from GitHub directly, then fall back to web search.

## 3. xray-monolith (engine internals)

```
data/clones/xray-monolith/src/
```

**Key subdirectories:**
- `src/xrGame/` — game logic, Lua bindings, callbacks, alife, save/load
- `src/xrCore/` — core engine, CInifile (DLTX), file system
- `src/xrXMLParser/` — XML loading (DXML hook)
- `src/xrServerEntities/` — server entity classes, script_ini_file Lua bindings, script loading (`script_storage.cpp`)
- `gamedata/scripts/` — Lua scripts shipped with the modded exes (dxml_core.script, etc.)

Use for: verifying Lua API bindings (`luabind`/`script_register`), DLTX/DXML implementation details, which callbacks are modded-exe additions, and engine behaviour not visible from Lua.

Fallback if file not found locally: `https://raw.githubusercontent.com/themrdemonized/xray-monolith/master/<path>`

## 4. External sources

Web search, AP-PRO forums, ModDB, Discord. Last resort only — always verify against base game scripts before publishing.
