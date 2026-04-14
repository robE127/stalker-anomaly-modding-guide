# S.T.A.L.K.E.R. Anomaly Modding Guide

A practical, code-first guide to scripting mods for **S.T.A.L.K.E.R. Anomaly**.

This guide is aimed at developers who have programming experience but have never modded Anomaly before. It documents the Lua scripting API, the callback system, config file formats, and common modding patterns — all derived from reading the base game's scripts and studying hundreds of community mods.

---

## What this guide covers

- **[Getting Started](getting-started/index.md)** — Setting up your environment, understanding the folder layout, writing your first mod
- **[Scripting](scripting/index.md)** — How Lua works in Anomaly, the module system, and the callback architecture
- **[API Reference](api-reference/index.md)** — The engine-exposed globals: `db.actor`, `level`, `game`, `alife`, `xr_logic`, and more
- **[Config Formats](config-formats/index.md)** — LTX, XML, DXML, and DLTX: how game data is defined and how mods override it
- **[Systems](systems/index.md)** — Deep dives into MCM, localization, items, NPCs, and UI scripting
- **[Callbacks Reference](callbacks-reference/index.md)** — Every known callback with signatures and usage examples
- **[Examples](examples/index.md)** — Complete worked mods you can run and modify

---

## What is S.T.A.L.K.E.R. Anomaly?

Anomaly is a standalone mod for *S.T.A.L.K.E.R.: Call of Pripyat* built on the **Open X-Ray engine** — an open-source continuation of GSC Game World's original engine. It ships with all the original game maps, a heavily reworked progression system, and an extensive Lua scripting layer that exposes most of the engine to modders.

Mods for Anomaly are called **addons**. An addon is a folder containing files that override or extend the base game's `gamedata/` directory. No compilation step is required for script mods — you write Lua (saved as `.script` files), drop them in the right folder, and the engine loads them automatically.

---

## How this guide was made

The API documentation and callback reference were derived by:

1. Scanning GitHub for public Anomaly addon repositories
2. Shallow-cloning the top 50 and extracting every `RegisterScriptCallback` call, function signature, and engine API usage pattern
3. Cross-referencing against the unpacked base game scripts (`Tosox/STALKER-Anomaly-gamedata`)

The scanner and analyzer tools are included in this repository under `scanner/` and can be re-run to expand the dataset.
