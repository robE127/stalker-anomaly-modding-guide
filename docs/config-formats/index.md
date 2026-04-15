# Config Formats

Anomaly uses two text-based config formats — **LTX** and **XML** — for almost all non-script game data. Understanding them is essential because most mods touch config files, and even pure script mods often need to read config values at runtime.

## Formats at a glance

| Format | Extension | Used for | Patching system |
|--------|-----------|----------|-----------------|
| LTX | `.ltx` | Items, creatures, trader inventories, sound, weather | DLTX |
| XML | `.xml` | UI layouts, localization strings, dialog trees, spawn profiles | DXML |

## When configs are loaded

LTX and XML have very different loading models, and knowing this prevents a whole class of subtle bugs.

### LTX — loaded once at engine startup

All `.ltx` files under `configs/` are parsed and merged into one large in-memory config database (`system.ltx`) when the engine starts. By the time your first script runs, every LTX value is already in memory.

DLTX patches are applied during this same merge pass — before any script sees the data. This means DLTX changes are indistinguishable from base game values once the engine is running.

**Consequence:** If you change an LTX file (or a DLTX patch) while the game is running, nothing updates. You must restart the game for LTX changes to take effect.

### XML — loaded on demand, per file

XML files are **not** pre-loaded at startup. The engine reads each XML file the first time something requests it — a UI screen opening, a dialog starting, a localization string being looked up. The parsed result may be cached, but the initial read is deferred.

DXML patches are applied at read time via the `on_xml_read` callback, which fires each time an XML file is loaded. This means DXML runs inside an active game session and can be triggered multiple times across a session.

**Consequence:** XML (and DXML) changes take effect the next time the relevant file is loaded, which may not require a full restart — opening and closing an affected UI screen is sometimes sufficient during development.

### Summary

| | LTX / DLTX | XML / DXML |
|---|---|---|
| When loaded | Engine startup — once | On demand — each time the file is needed |
| When patches apply | During startup merge | When the XML file is read (`on_xml_read`) |
| See changes without restart | No | Sometimes (re-open the UI that uses the file) |
| Read from script | `ini_sys:r_string_ex(...)` etc. | N/A — use DXML to modify; read via UI classes |

---

## Pages in this section

- **[LTX Format](ltx.md)** — Syntax, sections, inheritance, and how the engine reads it
- **[XML Configs](xml.md)** — Structure of UI and content XML files
- **[DXML (XML Patching)](dxml.md)** — Modifying XML files at runtime without replacing them
- **[DLTX (LTX Patching)](dltx.md)** — Modifying LTX files without replacing them
