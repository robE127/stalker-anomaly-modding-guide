# S.T.A.L.K.E.R. Anomaly Modding Guide

**The comprehensive technical reference for modding S.T.A.L.K.E.R. Anomaly that doesn't exist anywhere else.**

📖 **[Read the guide →](https://robE127.github.io/stalker-anomaly-modding-guide/)**

---

## What this is

This repository produces the guide at the link above. The `docs/` folder is the guide source (Markdown), built with MkDocs and automatically published to GitHub Pages on every push to `main`. If you're here to read the guide, use the link — this repo is where it's written and maintained.

### Why this guide exists

S.T.A.L.K.E.R. Anomaly has a thriving mod scene but almost no technical documentation. The existing resources are scattered across forum posts, Discord messages, and mod source code — there's no single place that explains the Lua scripting API, the callback system, config formats, engine bindings, and how they all fit together.

This guide is that missing resource. It's written for developers with general programming experience who want to mod Anomaly but don't know where to start. It covers:

- **Scripting** — Lua in Anomaly, the callback system, object binders, save/load state, debugging
- **API reference** — `db.actor`, `level`, `game`, `alife`, `xr_logic`, UI functions
- **Config formats** — LTX syntax, XML, DLTX patching, DXML patching
- **Systems** — MCM (settings UI), localization, items & inventory, NPCs, UI scripting
- **Callbacks reference** — every callback from `axr_main.script` with signatures and examples
- **Examples** — complete worked mods you can build on

Everything is grounded in sources: the base game scripts, 50 real community mods analysed with automated tooling, and the [xray-monolith](https://github.com/themrdemonized/xray-monolith) C++ source for engine internals.

---

## Repository structure

```
docs/               The guide (MkDocs source, Markdown)
scanner/            Python tools for gathering ground-truth data from GitHub
data/
  repos.json        214 scored GitHub repos from the scanner
  analysis/         Per-repo and cross-repo API/callback frequency data
  clones/           Shallow-cloned repos (gitignored — too large to commit)
mkdocs.yml          Site config and navigation
TODO.md             Current task list
CLAUDE.md           Project instructions for Claude Code
```

---

## Contributing

Corrections and additions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit changes and how to re-run the scanner tooling to refresh the data.

---

## Tooling

The `scanner/` directory contains the Python tools used to gather data for the guide. You don't need to run these to use the guide — the outputs are already committed to `data/`. But you can re-run them if you want fresher data.

### Prerequisites

```bash
cd scanner
pip install -r requirements.txt
# Optional but recommended: set GITHUB_TOKEN in .env for better rate limits
```

### Phase 1 — Scan GitHub for mod repos

```bash
python scanner.py
```

Searches GitHub for Anomaly mod repos, scores each by relevance, saves results to `data/repos.json`. Runtime: ~5–10 minutes with a token.

### Phase 2 — Clone and analyze repos

```bash
python analyze_repos.py --top 50 --min-score 25
```

Shallow-clones the top repos and extracts callback usage, API call patterns, and function signatures into `data/analysis/`.

### View a summary

```bash
python report.py               # List repos by score
python report.py --analysis    # Include top callbacks and API calls
```
