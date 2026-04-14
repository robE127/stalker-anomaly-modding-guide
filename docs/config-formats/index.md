# Config Formats

Anomaly uses two text-based config formats — **LTX** and **XML** — for almost all non-script game data. Understanding them is essential because most mods touch config files, and even pure script mods often need to read config values at runtime.

## Formats at a glance

| Format | Extension | Used for | Patching system |
|--------|-----------|----------|-----------------|
| LTX | `.ltx` | Items, creatures, trader inventories, sound, weather | DLTX |
| XML | `.xml` | UI layouts, localization strings, dialog trees, spawn profiles | DXML |

## Pages in this section

- **[LTX Format](ltx.md)** — Syntax, sections, inheritance, and how the engine reads it
- **[XML Configs](xml.md)** — Structure of UI and content XML files
- **[DXML (XML Patching)](dxml.md)** — Modifying XML files at runtime without replacing them
- **[DLTX (LTX Patching)](dltx.md)** — Modifying LTX files without replacing them
