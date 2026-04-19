# Dev Workflow Reference

## Dev server

Hot reloading does not work — neither the watchdog nor polling backend reliably detects file changes on this setup.

**Claude Code should never start the dev server.** The user always manages it manually.

To restart the server manually (user's PowerShell terminal):
```powershell
# Find and kill the existing process
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force

# Start fresh
cd C:\Users\roced\Documents\Projects\stalker-anomaly-modding-guide
python -m mkdocs serve
```
Then hard-refresh the browser (Ctrl+Shift+R).

## Adding a new page

1. Create the `.md` file in the appropriate `docs/` subfolder
2. Add it to `nav:` in `mkdocs.yml`
3. Run `python -m mkdocs build` to verify clean build before committing

## Commit conventions

- Always propose the commit message and wait for explicit user approval before running `git commit` or `git push`
- Format: short imperative subject line, blank line, bullet details
- Always include: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Never commit `site/` (gitignored, built by CI)
- Never commit `data/clones/` (gitignored, too large)

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
.claude/                 — Project reference files (loaded on demand)
mkdocs.yml               — Site config and nav
requirements-docs.txt    — Python deps for building the site
TODO.md                  — Current task list
```
