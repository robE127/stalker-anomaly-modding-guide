# S.T.A.L.K.E.R. Anomaly Modding Guide

A project to research and document the S.T.A.L.K.E.R. Anomaly modding API from the ground up — callbacks, engine bindings, tools, and worked examples — aimed at developers with coding experience but no prior exposure to the game's modding ecosystem.

No comprehensive guide like this currently exists.

---

## Repository structure

```
scanner/          Source code for the GitHub repo scanner and analyzer
data/
  repos.json      Scan results: 214 scored GitHub repos (produced by scanner.py)
  analysis/
    index.json    Cross-repo index of callbacks and API calls by frequency
    <repo>.json   Per-repo breakdown of scripts, callbacks, and API usage
guide/            (forthcoming) The modding guide itself
```

---

## How the research data was gathered

The `data/` folder is the output of a two-phase automated scan of public GitHub repositories. You can reproduce or extend it with the tools in `scanner/`.

### Prerequisites

- Python 3.10+
- Git (on PATH)
- A GitHub Personal Access Token (optional but strongly recommended)

### Setup

```bash
cd scanner
pip install -r requirements.txt

# Optional but recommended — without a token you get 10 req/min instead of 30
cp .env.example .env
# Edit .env and paste your token. No scopes needed — public repo access only.
# Create one at: https://github.com/settings/tokens?type=beta
```

### Phase 1 — Scan GitHub for mod repos

```bash
python scanner.py
```

Runs 13 search queries against the GitHub API covering topic tags, name/description keywords, and known modpack names. Each result is scored by relevance signals (keywords, topics, stars, presence of a `gamedata/` folder). Results are deduplicated and saved to `data/repos.json`.

Options:
```
--output PATH       Where to write results (default: data/repos.json)
--min-score N       Minimum relevance score to include (default: 20)
--no-details        Skip per-repo detail fetching (faster, less accurate scoring)
```

Expected runtime: ~5–10 minutes with a token.

### Phase 2 — Clone and analyze repos

```bash
python analyze_repos.py --top 50 --min-score 25
```

Takes the top N repos from `repos.json`, shallow-clones each one, then walks all `.script` and `.lua` files to extract:

- `RegisterScriptCallback` / `AddScriptCallback` calls → callback inventory
- Function definitions and signatures
- Engine API call patterns (`db.actor`, `level`, `game`, `xr_logic`, etc.)
- INI/config read method usage

Outputs a per-repo JSON to `data/analysis/<owner>__<repo>.json` and a merged frequency index to `data/analysis/index.json`.

Options:
```
--repos PATH        Path to repos.json (default: data/repos.json)
--cache-dir PATH    Where to store cloned repos (default: data/clones/)
--analysis-dir PATH Where to write analysis output (default: data/analysis/)
--top N             Analyze top N repos by score (default: 50)
--min-score N       Skip repos below this score (default: 30)
--skip-clone        Re-analyze already-cloned repos without fetching again
```

Note: `data/clones/` is gitignored (can be gigabytes). Re-running with `--skip-clone` is fast if clones are already present.

### View a summary

```bash
python report.py               # List repos by score
python report.py --analysis    # Include top callbacks and API calls
python report.py --top 100     # Show more repos
```

---

## Key findings from the initial scan

Across 50 repositories (including the unpacked base game scripts from `Tosox/STALKER-Anomaly-gamedata`):

### Most-used callbacks

| Callback | Uses | Purpose |
|---|---|---|
| `save_state` | 198 | Persist mod data to savegame |
| `actor_on_first_update` | 187 | One-time init after world loads |
| `load_state` | 181 | Restore mod data from savegame |
| `actor_on_update` | 147 | Per-frame tick |
| `on_option_change` | 121 | MCM settings changed |
| `on_game_load` | 107 | Post-load initialization |
| `on_key_press` | 80 | Keybind handling |
| `actor_on_item_use` | 58 | Player used an item |
| `npc_on_death_callback` | 41 | NPC killed |
| `on_xml_read` | 36 | DXML hook for XML patching |

### Most-used API calls

| Call | Uses | Purpose |
|---|---|---|
| `game.translate_string` | 3351 | Localization |
| `db.actor.object` | 861 | Get object reference from actor inventory |
| `level.object_by_id` | 768 | Look up any world object by ID |
| `game.get_game_time` | 629 | Current in-game time |
| `ui_options.get` | 549 | Read engine settings |
| `db.actor.position` | 489 | Player world position |
| `db.actor.item_in_slot` | 441 | Item in equipment slot |
| `db.actor.iterate_inventory` | 412 | Walk player inventory |
| `level.name` | 404 | Current map/level name |
| `ui_mcm.get` | 323 | Read MCM mod settings |
| `xr_logic.pick_section_from_condlist` | 317 | Evaluate condition lists |

---

## Background

S.T.A.L.K.E.R. Anomaly is a standalone mod for S.T.A.L.K.E.R.: Call of Pripyat built on the Open X-Ray engine. Mods for Anomaly are written in Lua (files use the `.script` extension) and live in `gamedata/scripts/`. Configuration uses a custom INI-like format (`.ltx`) and XML. The callback system (`RegisterScriptCallback` / `AddScriptCallback`) is the primary way scripts hook into engine events.
