# S.T.A.L.K.E.R. Anomaly Modding Guide

A practical, code-first reference for scripting and configuring mods for **S.T.A.L.K.E.R. Anomaly**.

Written for developers with programming experience who are new to Anomaly modding. No prior X-Ray engine or Lua knowledge assumed.

---

## What this guide covers

- **[Getting Started](getting-started/index.md)** — Environment setup, gamedata folder layout, writing your first mod
- **[Scripting](scripting/index.md)** — Lua in Anomaly, scope, the callback system, game_object, db.storage, object binders, save/load, debugging
- **[API Reference](api-reference/index.md)** — Engine-exposed globals: `db.actor`, `level`, `game`, `alife`, `xr_logic`, UI functions
- **[Config Formats](config-formats/index.md)** — LTX, XML, DXML, and DLTX: how game data is defined and patched
- **[Systems](systems/index.md)** — MCM, localization, items, NPCs, and UI scripting
- **[Callbacks Reference](callbacks-reference/index.md)** — Every known callback with signatures
- **[Examples](examples/index.md)** — Complete worked mods you can run and modify

---

## Where to start

=== "I want to write a script mod"
    1. [Environment Setup](getting-started/environment-setup.md) — editor, file associations, unpacking base scripts
    2. [Lua in Anomaly](scripting/lua-in-anomaly.md) — how Lua works in the X-Ray engine
    3. [Script Lifecycle](scripting/script-lifecycle.md) — when your code runs and what's available when
    4. [The Callback System](scripting/callbacks.md) — how to hook into engine events
    5. [Your First Mod](getting-started/first-mod.md) — build and test a working addon

=== "I want to edit configs or items"
    1. [Gamedata Structure](getting-started/gamedata-structure.md) — where configs live and how file priority works
    2. [LTX Format](config-formats/ltx.md) — the primary config format
    3. [DLTX (LTX Patching)](config-formats/dltx.md) — mod-compatible config overrides
    4. [Items & Inventory](systems/items.md) — item config structure and callbacks

=== "I want to modify the UI or dialogs"
    1. [XML Configs](config-formats/xml.md) — UI layout and dialog XML structure
    2. [DXML (XML Patching)](config-formats/dxml.md) — patching XML without replacing files
    3. [UI Scripting](systems/ui-scripting.md) — writing Lua-backed UI screens
    4. [Localization](systems/localization.md) — adding and translating text strings

---

## What is S.T.A.L.K.E.R. Anomaly?

Anomaly is a free standalone mod for *S.T.A.L.K.E.R.: Call of Pripyat* built on the **Open X-Ray engine** — an open-source continuation of GSC Game World's original engine. It ships with all the original game maps, a heavily reworked progression system, and an extensive Lua scripting layer that exposes most of the engine to modders.

Mods for Anomaly are called **addons**. An addon is a folder containing files that override or extend the base game's `gamedata/` directory. No compilation step is required for script mods — write Lua (saved as `.script` files), drop it in the right folder, and the engine loads it automatically.

---

## Why this guide exists

This guide was built out of a direct personal frustration: wanting to start modding Anomaly and not being able to find the information to do so in a form that suited my learning style.

The closest thing I could find was TheParaziT's [anomaly-modding-book](https://github.com/TheParaziT/anomaly-modding-book) — the most ambitious attempt at a comprehensive reference the community has produced, and worth reading. But many of its pages are incomplete, and after going through it the foundational picture still wasn't there: which systems exist, how they connect, what the actual API surface looks like, what callbacks fire and when. That information exists in the community, but it's scattered across forum posts, Discord threads, and mod source code with no single place that lays it out clearly.

This guide is an attempt to be that place. It's written by someone learning Anomaly modding alongside writing it, using the base game source and a systematic analysis of real mods as the ground truth rather than community hearsay.

I've been using mods in games for a long time — Anomaly in particular — and always wanted to give something back to the community. This felt like somewhere I could actually contribute. The other thing that made this feel possible now, when it wasn't before, is the AI and LLM tooling available today. The task of building a guide like this is exactly what these tools are well-suited for: aggregating large amounts of information scattered across hundreds of repositories, forum posts, and source files; finding the patterns and understanding the relationships between systems; and presenting it in a form that's digestible to someone encountering it for the first time. This guide was built with that tooling at the center of the process.

---

## How this guide was made

The API documentation and callback reference were derived by:

1. **Scanning GitHub** for public Anomaly addon repositories — 214 repos scored by relevance
2. **Analysing the top 50** — every `RegisterScriptCallback` call, engine API usage, and function signature extracted and counted across the dataset
3. **Cross-referencing against the base game** — all documented behaviour verified against a fully-unpacked copy of Anomaly 1.5.3 (the current release)

This means the guide reflects what real mods actually use, not just what the API theoretically exposes. The scanner and analyser tools live in `scanner/` and can be re-run to refresh the dataset as the mod ecosystem evolves.

**Scope and limitations:** This guide targets Anomaly 1.5.3. Some details may differ for derived modpacks (GAMMA, EFP, etc.). Engine-internal C++ behaviour is documented by observed effect, not by reading source — if something contradicts what you see in-game, the game wins.
