# TODO

Task list for the S.T.A.L.K.E.R. Anomaly Modding Guide. Kept in sync with the Claude Code session todo list.

---

## In progress

_Nothing currently in progress._

---

## Pending

### Fixes & quick wins
- [x] Fix callback registration contradiction between `docs/scripting/callbacks.md` and `docs/scripting/script-lifecycle.md` — callbacks.md says registering the same function twice is harmless; script-lifecycle.md says it causes double-firing. Resolve against axr_main.script ground truth.
- [x] Enable next/prev page navigation — add `navigation.footer` to the `features` list in `mkdocs.yml` (one-line change).

### Core conceptual gaps (new pages / sections)
- [x] **What is a game_object?** — New page or prominent section. Fundamental type referenced everywhere; explain the client-side object, its base methods (`id()`, `name()`, `section()`, `position()`, `alive()`), and how it differs from a server entity.
- [x] **What is db.storage?** — Currently mentioned in NPCs page without explanation. Add a dedicated section covering its structure, lifecycle, and safe access patterns.
- [x] **Lua Scope & Globals** — New page. Explain `local` vs global, module scope, why globals are dangerous in Anomaly's shared namespace, upvalues and closures, and how to safely share state between scripts.
- [x] **Debugging & Logging** — New page. Reading the log file, `printf` vs `log`, `DEV_DEBUG`, `pcall` patterns, common silent failure modes, and how to diagnose callback errors.
- [x] **Expand pcall coverage** — Either in the Debugging page or back-linked from `lua-in-anomaly.md`. More depth on error handling patterns, nested pcall, and recovering gracefully.
- [x] **When are configs loaded?** — Add to `config-formats/` section. Explain that LTX is loaded at engine startup (merged into system.ltx), XML is loaded on demand per-file, and how DXML/DLTX timing works.
- [x] **List base game scripts with load order** — Expand `docs/getting-started/gamedata-structure.md` with a table of notable scripts and their roles; cross-reference load order in `docs/scripting/script-lifecycle.md`.
- [x] **Object Binders** — New page. How to subclass `object_binder`, the binder lifecycle (`net_spawn`, `net_destroy`, `update`, `save_state`, `load_state`), and when to use a binder vs a global callback.

### Getting started improvements
- [x] **Scripts folder as workspace** — Clarify in getting-started why mods are placed in `gamedata/scripts/` directly rather than a separate workspace folder, and how MO2 mod folder structure maps to this.

### Content & community
- [x] **Motivation and methodology** — Add an About or Methodology page (or expand home page) explaining why this guide exists, how content was derived (base game source + 50-repo analysis), and its scope and limitations.
- [x] **Credits and cross-links to anomaly-modding-book** — TheParaziT's anomaly-modding-book is the main existing community reference (`data/clones/TheParaziT__anomaly-modding-book/`). Add attribution, link to it, and note where the two guides complement each other.
- [ ] **Contribution guide** — Add `CONTRIBUTING.md` or a docs page explaining how to submit corrections, additions, and how the scanner tools can be re-run to refresh the data.
- [ ] **Packaging for MO2/BAIN** — New page in Getting Started. How to structure a mod folder for MO2 compatibility, what a BAIN-compatible archive looks like, and optionally a basic FOMOD installer.

### Advanced topics (new pages)
- [ ] **Sounds & Particles from Script** — `sound_object`, playing sounds at world positions, attaching sounds to objects, `start_particles` / `stop_particles`, common particle file paths.
- [ ] **Ray Casting** — How to fire a ray from script to detect line-of-sight, find objects in a direction, or check terrain intersection.
- [ ] **Improve navmesh explanation** — Expand the navmesh section in `docs/api-reference/level.md` with more context on what level vertices are, when to use `level_vertex_id` vs `game_vertex_id`, and practical pathfinding patterns.
- [ ] **Full Mini-Quest Example** — A complete worked example tying together: NPC dialog → info portion flag → item delivery → save/load → reward. Longer than the current examples but demonstrates how real quest mods are structured.

### Polish
- [ ] **API reference completeness audit** — Is the `game_object` member list exhaustive? Are all listed methods confirmed present in vanilla 1.5.2? Document what "character section" means. Verify against `lua_help.script`.
- [ ] **Buy Me a Coffee link** — Add a sponsor/support link to the home page.
- [x] **Polish home page** (`docs/index.md`) — Better orientation, scope statement, quick-start path for different reader types (scripter, config modder, etc.).
- [ ] **Audit and fix all internal cross-links** — Many pages reference other pages without a proper Markdown link. Do a pass and wire them all up.
- [ ] **Add See Also sections** — Add structured "See Also" footers to pages with clear relationships (e.g. alife.md → npcs.md, mcm.md → examples/mcm-options.md).

### Meta
- [ ] **Commit CLAUDE.md** — Rules file is written; commit it along with this TODO.

---

## Completed

- [x] Write Getting Started: Environment Setup
- [x] Write Getting Started: Gamedata Structure
- [x] Write Getting Started: Your First Mod
- [x] Write Scripting: Lua in Anomaly
- [x] Write Scripting: Script Lifecycle
- [x] Write Scripting: The Callback System
- [x] Write Scripting: Save & Load State
- [x] Write Callbacks Reference (full signature list from axr_main.script)
- [x] Write API Reference: db.actor
- [x] Write API Reference: level
- [x] Write API Reference: game
- [x] Write API Reference: alife
- [x] Write API Reference: xr_logic
- [x] Write API Reference: UI Functions
- [x] Write Config Formats: LTX
- [x] Write Config Formats: XML
- [x] Write Config Formats: DLTX
- [x] Write Config Formats: DXML
- [x] Write Systems: MCM
- [x] Write Systems: Localization
- [x] Write Systems: Items & Inventory
- [x] Write Systems: NPCs & Factions
- [x] Write Systems: UI Scripting
- [x] Write Example: Keybind Action
- [x] Write Example: Item Use Effect
- [x] Write Example: NPC Death Reward
- [x] Write Example: MCM Options
- [x] Set up MkDocs + Material theme
- [x] Set up GitHub Actions auto-deploy to GitHub Pages
- [x] Build GitHub scanner tooling (scanner.py, analyze_repos.py, report.py)
- [x] Run scanner — 214 repos scored, top 50 analysed
