# Claude Code — Project Instructions

S.T.A.L.K.E.R. Anomaly Modding Guide. Goal: comprehensive modding reference covering Lua API, callbacks, config formats, and worked examples — in one place, verified against real sources. Guide in `docs/`, built with MkDocs Material, auto-deployed from `main` via GitHub Actions. Test mod in `test_mod/`.

---

## Working with the project owner

Software engineering background, not an Anomaly expert — questions are reasoning checks, not corrections. Hold your position if you wrote something for good reason; only concede if the discussion reveals you were actually wrong, and say so explicitly. Push back with evidence if the owner contradicts what sources show.

---

## Research sources (priority order)

1. **Base game scripts** — fully unpacked Anomaly installation under `data/clones/Anomaly-*-Full/tools/_unpacked/`. Highest authority. Grep here first.
2. **Community mod analysis** — `data/analysis/index.json` (cross-repo frequency), per-repo JSON, cloned mods in `data/clones/`.
3. **xray-monolith C++ source** — `data/clones/xray-monolith/src/`. Grep here first for engine-level questions.
4. **External** (forums, ModDB, web search) — last resort only; verify against base game scripts before publishing.

Full paths, key files, and notable clones: read `CLAUDE-SOURCES.md` when needed.

---

## Writing standards

- All code examples must exist in base game scripts. No invented API.
- No assumed facts — every claim needs a traceable source. "Verified in `X.script`" is the standard.
- Verify across all relevant layers (C++ and Lua) before writing.
- Ask the owner when a detail can't be confirmed — faster and more reliable than guessing.
- Accurate over complete. Short verified page > long speculative page.
- Update `docs/` in the same session whenever the test mod reveals new engine behaviour. Don't defer.
- If you use or confirm modding knowledge **not already represented in `docs/`** (unpacked game scripts, `xray-monolith`, runtime behaviour, verified external sources, etc.), **add or update `docs/` in the same session** so the guide improves with the work. Prefer extending existing pages; keep claims source-traceable.
- No WIP stubs. `!!! note "Work in progress"` must never appear in committed content.
- Use `local` for all module-level variables and callback functions.
- Show the full `on_game_start` / `on_game_end` registration pattern in every example that registers callbacks.
- Audience: programmers new to Anomaly. Explain engine-specific concepts; skip general programming basics.

---

## Operations

**Never start the dev server** — the user manages it manually. See `CLAUDE-WORKFLOW.md` for kill/start commands.

**Before committing any new or changed page:** run `python -m mkdocs build` to verify clean build. When adding a page, also add it to `nav:` in `mkdocs.yml`.

**Never commit without explicit user approval.** Propose the commit message and wait for confirmation. Format: short imperative subject, blank line, bullet details. Always include `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`. Never commit `site/` or `data/clones/`.

Known test-mod limitations and unresolved behavior should be tracked in `test_mod/KNOWN_ISSUES.md`. When a new issue is confirmed, add it there in the same session.

Todo list: `TODO.md`.
