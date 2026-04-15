# Contributing to the S.T.A.L.K.E.R. Anomaly Modding Guide

Corrections, additions, and improvements are welcome. This document explains how the project is structured, what kinds of contributions are most useful, and how to submit them.

---

## What this guide is

The guide has two parts:

1. **Data gathering tooling** (`scanner/`) — Python scripts that scan GitHub for Anomaly addon repos, clone and analyse the top results, and produce structured data about real-world callback and API usage.
2. **The guide itself** (`docs/`) — MkDocs Markdown pages published to GitHub Pages, written for developers with programming experience who are new to Anomaly modding.

Every claim in the guide should be traceable back to either the base game scripts or observed patterns across real mod repositories. Speculation is not accepted.

---

## Kinds of contributions

### Corrections

If something in the guide is factually wrong — a method signature is incorrect, a callback name is misspelled, a behaviour is described inaccurately — open an issue with:

- The page and section where the error appears
- What the guide currently says
- What the correct information is
- A source (base game script file, mod repo, or engine source) that confirms the correction

Small corrections (typos, broken links, obviously wrong information) can come in as a pull request directly without an issue first.

### New content

Before writing a new page or section, open an issue to discuss scope. The guide prioritises accuracy over completeness — a section that can't be verified against ground-truth sources shouldn't be added.

New content should follow the writing standards below.

### Scanner data refresh

The dataset used to write the guide (214 repos scored, top 50 analysed) was generated at a point in time. As the mod ecosystem evolves, the scanner can be re-run to refresh it. See [Re-running the scanner](#re-running-the-scanner) below.

---

## Writing standards

- **Every function, method, or property in a code example must exist in the base game scripts.** Check `data/clones/Tosox__STALKER-Anomaly-gamedata/gamedata/scripts/` first. Do not invent API.
- **Accurate over complete.** A shorter section with verified information is better than a longer one with speculative content.
- **No WIP stubs.** Every page or section must be fully written before being submitted. `!!! note "Work in progress"` blocks should not appear in submitted content.
- **Lua style.** Use `local` for all module-level variables and callback functions. Show the full `on_game_start` / `on_game_end` registration pattern in every example that registers callbacks.
- **Audience.** Readers have programming experience but are new to Anomaly. Explain X-Ray/Anomaly-specific concepts; don't explain general programming concepts at length.

---

## Development setup

### Prerequisites

- Python 3.9+
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

### Install docs dependencies

```bash
pip install -r requirements-docs.txt
```

### Build and preview the site

```bash
python -m mkdocs build       # build to site/
python -m mkdocs serve       # serve at http://localhost:8000
```

> **Note:** Live reload does not work reliably on Windows. Kill the server process and restart it manually to pick up changes (`Ctrl+C` or `Stop-Process` in PowerShell, then `python -m mkdocs serve` again).

### Adding a new page

1. Create the `.md` file in the appropriate `docs/` subfolder.
2. Add it to the `nav:` section of `mkdocs.yml`.
3. Run `python -m mkdocs build` to verify it builds without errors.

---

## Re-running the scanner

The scanner tooling lives in `scanner/`. It requires a GitHub personal access token for reasonable rate limits.

### Setup

```bash
cd scanner
pip install -r requirements.txt
cp .env.example .env          # then edit .env and add your GITHUB_TOKEN
```

If `.env.example` does not exist, create `.env` manually:

```
GITHUB_TOKEN=ghp_your_token_here
```

### Step 1 — Scan GitHub for repos

```bash
python scanner.py
```

This searches GitHub for public Anomaly addon repositories, scores them by relevance, and writes results to `data/repos.json`. The run takes a few minutes depending on rate limits.

Options:
```
--output PATH     Write repos.json to a custom path (default: data/repos.json)
--min-score N     Only save repos scoring at least N (default: 0)
--no-details      Skip fetching per-repo detail (faster, less data)
```

### Step 2 — Analyse the top repos

```bash
python analyze_repos.py
```

This reads `data/repos.json`, shallow-clones the top-scoring repos into `data/clones/`, and extracts callback registrations, API calls, and function signatures. Output goes to `data/analysis/`.

Options:
```
--top N           Analyse top N repos by score (default: 50)
--skip-clone      Skip cloning; analyse whatever is already in data/clones/
--repos PATH      Read repos from a custom repos.json path
```

### Step 3 — View a summary

```bash
python report.py              # summary of scored repos
python report.py --analysis   # include callback and API frequency counts
python report.py --top 100    # show top 100 repos
```

### Adding a repo manually

`scanner/manual_repos.json` lists repos that are always included in `repos.json` with a perfect relevance score (9999), regardless of what keyword search finds. This is for high-value sources that wouldn't be discovered by Anomaly-mod keyword search — engine source repos, reference implementations, etc.

To add a repo, append an entry to the `repos` array:

```json
{
  "full_name": "owner/repo-name",
  "note": "Why this repo is valuable to the guide"
}
```

The scanner fetches GitHub metadata automatically on the next run. No other changes are needed.

### Notes on data/clones/

`data/clones/` is gitignored — it contains full repo clones and can be several gigabytes. Do not commit it. The base game scripts at `data/clones/Tosox__STALKER-Anomaly-gamedata/` are the single most important clone; if you re-run the analyser, make sure that repo is still present.

---

## Pull request guidelines

- One logical change per PR.
- If adding or changing guide content, cite the source (script file, line number, or repo) in the PR description.
- Run `python -m mkdocs build` before submitting and confirm it exits without errors.
- Keep commit messages short and imperative: `Fix actor method signature in db-actor.md`, `Add See Also section to callbacks.md`.

---

## Questions

Open an issue. The project is maintained by a single person learning Anomaly modding alongside writing this guide, so response time may vary.
