# Gamedata Structure

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- The `gamedata/` root and how the engine resolves file precedence (addon files override base game files)
- `gamedata/scripts/` — Lua source files (`.script` extension)
- `gamedata/configs/` — LTX and XML configuration files
  - `configs/items/` — weapon, armor, consumable definitions
  - `configs/creatures/` — NPC and monster definitions
  - `configs/gameplay/` — tasks, dialogs, character profiles
  - `configs/ui/` — UI layout XML
  - `configs/text/` — localization strings (one subfolder per language code)
  - `configs/misc/` — trader inventories, sound definitions, artefacts
- `gamedata/textures/` — DDS textures
- `gamedata/sounds/` — OGG audio
- `gamedata/meshes/` — 3D models (`.ogf`)
- `gamedata/anims/` — Animations
- `gamedata/shaders/` — Renderer shaders
- How Anomaly loads addons: the `db/` folder structure and archive precedence
- Why you should never edit base game files directly
