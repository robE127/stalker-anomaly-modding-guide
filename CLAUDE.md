# Claude Code — Project Instructions

This is the S.T.A.L.K.E.R. Anomaly Modding Guide project. Before writing or editing any guide content, read this file in full.

---

## Working with the project owner

The project owner has a **software engineering background but is not an Anomaly modding expert** — quite the opposite; this guide is being built partly to fill their own knowledge gaps. When they question something, they are applying engineering reasoning to test whether your logic is sound, not correcting you from domain expertise.

**Do not immediately concede and make changes when questioned.** If you wrote something for a good reason, explain that reason and have a discussion. The owner's questions are prompts to verify your reasoning, not instructions to reverse course. Only change course if the discussion reveals your original reasoning was actually wrong — and say so explicitly when that happens.

This applies equally in reverse: if the owner suggests something that conflicts with what the base game source shows, push back with evidence.

---

## What this project is

This project has two distinct parts that work together toward one goal.

### The goal
Create the best resource for learning how to mod S.T.A.L.K.E.R. Anomaly — one that doesn't exist yet. No comprehensive guide covering the Lua scripting API, the callback system, config formats, engine bindings, and worked examples currently exists in one place. This project fills that gap.

### Part 1 — Data gathering tooling
The `scanner/` directory contains Python tools that were built specifically to gather reliable, ground-truth data for the guide:

- `scanner.py` — searches GitHub, scores repos by relevance to Anomaly modding, and records them in `data/repos.json`
- `analyze_repos.py` — clones the top-scoring repos and extracts callback names, API calls, function signatures, and usage patterns into `data/analysis/`
- `report.py` — produces human-readable summaries from the analysis

This tooling exists so that guide content is grounded in **what real mods actually do**, not in speculation or hearsay. The 214 repos scored, 50 analysed, and base game scripts cloned under `data/clones/` are the raw material. The scanner can be re-run at any time to refresh the data as the mod ecosystem evolves.

### Part 2 — The guide
The actual guide lives in `docs/` and is published via MkDocs Material to GitHub Pages (auto-deployed from `main` via GitHub Actions). It is written for developers with programming experience but no prior Anomaly modding knowledge. Every claim in the guide should be traceable back to a source in `data/` — either the base game scripts, or observed patterns across real mod repos.

---

## Research sources — use in this order

When writing or improving guide content, always prefer sources in this priority order:

### 1. Base game scripts (highest authority)
```
data/clones/Tosox__STALKER-Anomaly-gamedata/gamedata/scripts/
data/clones/Tosox__STALKER-Anomaly-gamedata/gamedata/configs/
```
This is a full shallow clone of the Anomaly 1.5.2 base game. It is the ground truth for all API signatures, callback names, config field names, and engine behaviour. When documenting any function or system, grep here first.

Key files to know:
- `_g.script` — global environment, helper functions, `alife_create`, `IsWeapon`, etc.
- `axr_main.script` — the complete callback registration table (authoritative callback list)
- `xr_logic.script` — condition list evaluator and NPC behaviour system
- `bind_stalker_ext.script` — actor binder, item callbacks
- `utils_item.script`, `utils_ui.script`, `utils_data.script` — utility modules

### 2. Community mod analysis
```
data/analysis/index.json          — cross-repo callback and API frequency counts
data/analysis/<repo>.json         — per-repo extracted callbacks, functions, API calls
data/repos.json                   — scored list of 214 scanned repos with metadata
```
Use `index.json` to find the most commonly used callbacks and API calls across 50 real mods. This tells you what's actually important to document. Use per-repo JSON files and the cloned repos to find real usage patterns.

Particularly useful clones for real-world patterns:
- `data/clones/nltp-ashes__Nanosuit/` — complex multi-system mod, good patterns
- `data/clones/nltp-ashes__Western-Goods/` — full quest and economy mod
- `data/clones/themrdemonized__STALKER-Anomaly-Mugging-Squads/` — NPC squad manipulation
- `data/clones/explorerbeer__tactical_compass/` — HUD and UI patterns
- `data/clones/Grokitach__Stalker_GAMMA/` — DLTX usage examples
- `data/clones/AlienProductGames__SCP-Faction-WIP/` — DXML usage examples
- `data/clones/TheParaziT__anomaly-modding-book/` — existing community documentation (credit this)

**If a clone is not available locally**, fall back in this order:
1. Check `data/repos.json` — every scanned repo has a `html_url` (GitHub link) and a relevance `score`. Use the highest-scored repos relevant to your topic.
2. Fetch the GitHub URL directly (raw file links, or the repo tree) to read source code.
3. Only after exhausting local clones and GitHub source should you fall back to web search or forum posts.

Always prefer higher-scored repos from `repos.json` when choosing which GitHub sources to consult.

### 3. xray-monolith (engine internals)
The modded exes are open-source C++: **https://github.com/themrdemonized/xray-monolith**

Use this when you need to understand how the engine actually works rather than just what it exposes to Lua. Particularly useful for:
- Verifying exactly which C++ functions are bound to the Lua API (`luabind` / `script_register` calls in the source)
- Understanding how DLTX and DXML are implemented — merge algorithm, load order, edge cases
- Understanding which callbacks are added by the modded exes vs present in vanilla Anomaly
- Engine behaviours (object lifetime, save serialisation, etc.) that are otherwise only documentable by observation

This repo is not cloned locally. Fetch files directly from GitHub using raw URLs:
`https://raw.githubusercontent.com/themrdemonized/xray-monolith/master/<path>`

Or browse the tree: `https://github.com/themrdemonized/xray-monolith/tree/master`

Key areas to look in:
- `src/xrScripts/` or similar — Lua binding registration
- Search for `luabind::` or `export_` prefix functions to find what's exposed to scripts
- DLTX implementation: search for `dltx` or `mod_` prefix handling
- DXML implementation: search for `on_xml_read` or `xml_document`

### 4. External sources (use only when local data is insufficient)
Web search and the Anomaly modding community (AP-PRO forums, ModDB, Discord) may fill gaps not covered by the local data. Always verify against the base game scripts before publishing.

---

## Writing standards

- **Code examples must be grounded.** Every function, method, or property shown in examples must exist in the base game scripts. Do not invent API.
- **Accurate over complete.** A shorter page with verified information is better than a long page with speculative content.
- **No WIP stubs.** Every page must be fully written before being committed. The admonition `!!! note "Work in progress"` must never appear in committed content.
- **Lua style.** Use `local` for all module-level variables and callback functions. Show the full `on_game_start` / `on_game_end` registration pattern in every example that registers callbacks.
- **Audience.** Readers have programming experience but are new to Anomaly. Explain X-Ray/Anomaly-specific concepts; don't explain general programming concepts at length.

---

## File structure

```
docs/                    — MkDocs source (Markdown)
  getting-started/       — Installation, gamedata layout, first mod
  scripting/             — Lua runtime, lifecycle, callbacks, save/load
  api-reference/         — db.actor, level, game, alife, xr_logic, UI
  config-formats/        — LTX, XML, DLTX, DXML
  systems/               — MCM, localization, items, NPCs, UI scripting
  callbacks-reference/   — Full callback list from axr_main.script
  examples/              — Complete worked addon examples
data/
  clones/                — Shallow-cloned repos (gitignored)
  analysis/              — Per-repo and cross-repo analysis JSON
  repos.json             — Scored repo list from scanner
scanner/                 — Python tools used to generate data/
  scanner.py             — GitHub search and scoring
  analyze_repos.py       — Clone and analyse scripts
  report.py              — Human-readable summary
mkdocs.yml               — Site config and nav
requirements-docs.txt    — Python deps for building the site
TODO.md                  — Current task list (keep updated)
```

---

## Dev server

**Hot reloading does not work on this setup.** Neither the watchdog Windows API observer nor the polling backend reliably detect file changes, regardless of how the server is launched. Do not expect the browser to auto-refresh when files change.

**The correct workflow for previewing changes:**

1. Kill the existing server process (use PowerShell):
```powershell
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force
```
2. Start a fresh server:
```powershell
cd C:\Users\roced\Documents\Projects\stalker-anomaly-modding-guide
python -m mkdocs serve
```
3. Hard-refresh the browser (Ctrl+Shift+R) after the server is up.

**Claude Code should never start the dev server** — running it as a background bash task (Git Bash on Windows) has the same broken file-watching behaviour and also accumulates stale processes. The user always starts and restarts the server manually from their own PowerShell terminal.

---

## Nav structure (mkdocs.yml)

The navigation is explicitly defined in `mkdocs.yml`. When adding a new page:
1. Create the `.md` file in the appropriate `docs/` subfolder
2. Add it to the `nav:` section of `mkdocs.yml` in the right place
3. Run `python -m mkdocs build` to verify it builds cleanly before committing

---

## Commit conventions

- **Always ask before committing.** Never run `git commit` or `git push` without explicit user approval. Propose the commit message and wait for confirmation.
- Commit after each logical chunk of work (a page, a fix, a feature)
- Commit message format: short imperative summary, then blank line, then bullet details
- Always include `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Never commit the `site/` directory (it's gitignored and built by CI)
- Never commit `data/clones/` (gitignored — too large)

---

## Todo list

The current task list lives in `TODO.md` at the repo root. Keep it updated as tasks are completed or added.
