# UI Functions

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

### ui_mcm — Mod Configuration Menu

- `ui_mcm.get(key)` — read a setting registered by your mod (323 uses in analyzed repos)
- How MCM keys are structured: `"mod_id/setting_name"`
- The relationship between `ui_mcm.get` and `on_option_change` callback
- Full MCM setup covered in [Systems: Mod Configuration Menu](../systems/mcm.md)

### ui_options — Engine Options

- `ui_options.get(key)` — read a built-in engine setting (549 uses — more common than MCM!)
- Common keys: video settings, gameplay toggles
- `ui_options.set(key, value)` — write a setting

### HUD messages

- `actor_menu.get_actor_menu()` — access the actor inventory UI
- News and tip notifications: `news_manager` module
- `ui_hud` — HUD element access
- `game_message` and message display utilities
