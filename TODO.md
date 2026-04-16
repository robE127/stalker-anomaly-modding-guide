# TODO

Task list for the S.T.A.L.K.E.R. Anomaly Modding Guide. Kept in sync with the Claude Code session todo list.

---

## In progress

_Nothing currently in progress._

---

## Pending

### P1 — High value, relatively quick

_(all done)_

### P2 — Medium effort, meaningful impact

- [ ] **Basic vs advanced content tagging** — Add a visual system distinguishing beginner-essential content from deep-dive/advanced material. Could be MkDocs Material admonitions, section badges, or separate "advanced" callout boxes. Should work across all pages without requiring site-wide restructure.
- [ ] **Full API reference index page** — A single page listing every known Lua API callable (namespaces, classes, functions) with the most commonly used ones visually highlighted (based on `data/analysis/index.json` frequency data). Links to the relevant detailed pages.
- [ ] **Audit and fix all internal cross-links** — Many pages reference other pages without a proper Markdown link. Do a systematic pass and wire them all up.
- [ ] **Full Mini-Quest Example** — A complete worked example: NPC dialog → info portion flag → item delivery → save/load → reward. Demonstrates how real quest mods are structured.
- [ ] **Add See Also sections** — Structured "See Also" footers on pages with clear relationships (e.g. alife.md → npcs.md, mcm.md → examples/mcm-options.md).

### P3 — Larger projects

- [ ] **Sounds & Particles from Script** — `sound_object`, playing sounds at world positions, attaching sounds to objects, `start_particles` / `stop_particles`, common particle file paths.
- [ ] **Ray Casting** — How to fire a ray from script to detect line-of-sight, find objects in a direction, or check terrain intersection.
- [ ] **Improve navmesh explanation** — Expand the navmesh section in `docs/api-reference/level.md` with more context on what level vertices are, when to use `level_vertex_id` vs `game_vertex_id`, and practical pathfinding patterns.
- [ ] **API reference completeness audit** — Is the `game_object` member list exhaustive? Are all listed methods confirmed present in vanilla 1.5.2? Verify against `lua_help.script` and xray-monolith bindings catalog.
- [ ] **Validation mod** — Create a small but real mod using only this guide and the wiki as references. Store it in the repo (`examples/validation-mod/`) along with the AI conversation that produced it. Demonstrates guide reliability and surfaces gaps.

### P4 — Investigate / low priority

- [ ] **Move to Zensical?** — Evaluate whether Zensical is a better platform than MkDocs Material for this guide. Consider: search quality, navigation UX, hosting, contributor workflow, and migration cost.
- [ ] **Buy Me a Coffee link** — Add a sponsor/support link to the home page.
- [ ] **Add See Also sections** — Add structured "See Also" footers to pages with clear relationships.

---

## Fixes & quick wins (pending)

- [ ] **Audit and fix all internal cross-links** — Many pages reference other pages without a proper Markdown link.

---

## Completed

- [x] Add vanilla/modded exes Req column to callbacks reference
- [x] Glossary / jargon page — `docs/reference/glossary.md` with 20+ terms, added to nav
- [x] "What is a section?" — both senses covered in glossary
- [x] Improve binders page — analogy, 3 concrete scenarios, side-by-side comparison
- [x] Fix .sav → .scop in engine-internals.md (save files are `.scop`/`.scoc`, not `.sav`)
- [x] Update CLAUDE.md — xray-monolith is now cloned locally at `data/clones/xray-monolith/`
- [x] Rewrite README — leads with mission and live guide link; tooling is secondary
- [x] Add engine internals page (`docs/scripting/engine-internals.md`)
- [x] Document DLTX internals from C++ source
- [x] Document DXML internals from C++ source
- [x] Fetch and index xray-monolith Lua binding headers
- [x] Fix callback registration contradiction between callbacks.md and script-lifecycle.md
- [x] Enable next/prev page navigation
- [x] What is a game_object? (new page)
- [x] What is db.storage? (new section)
- [x] Lua Scope & Globals (new page)
- [x] Debugging & Logging (new page)
- [x] When are configs loaded? (config-formats section)
- [x] List base game scripts with load order
- [x] Object Binders (new page)
- [x] Scripts folder as workspace (getting-started)
- [x] Motivation and methodology
- [x] Credits and cross-links to anomaly-modding-book
- [x] Contribution guide
- [x] Packaging for MO2/BAIN
- [x] Polish home page
- [x] Commit CLAUDE.md
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
