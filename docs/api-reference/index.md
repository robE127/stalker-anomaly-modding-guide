# API Reference

The X-Ray engine exposes a set of global objects and functions to Lua scripts. This section documents the most commonly used ones, derived from analysis of the base game scripts and community addons.

!!! tip "How to read this reference"
    Function signatures use the format `object:method(param: type) -> return_type`.
    Parameters in `[brackets]` are optional.

## Global objects

| Object | Description |
|--------|-------------|
| [`db.actor`](actor.md) | The player character — inventory, position, health, status effects |
| [`level`](level.md) | The current map — object lookup, time, camera effects, weather |
| [`game`](game.md) | Game-wide utilities — time formatting, localization, difficulty |
| [`alife()`](alife.md) | The A-Life simulation — creating, finding, and destroying server-side entities |
| [`xr_logic`](xr-logic.md) | Condition list evaluation, logic schemes |
| [UI Functions](ui.md) | `ui_mcm`, `ui_options`, HUD messaging |

## Pages in this section

- **[db.actor](actor.md)** — Player object: inventory iteration, slot access, stats, info portions
- **[level](level.md)** — Map and world functions: object lookup, time, post-processing effects
- **[game](game.md)** — Localization, game time formatting, difficulty queries
- **[alife](alife.md)** — Server-side entity management
- **[xr_logic](xr-logic.md)** — Condition lists and logic evaluation
- **[UI Functions](ui.md)** — HUD notifications, MCM settings access, options
