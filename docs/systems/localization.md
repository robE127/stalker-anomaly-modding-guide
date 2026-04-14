# Localization

!!! note "Work in progress"
    This page is being written. Content coming soon.

`game.translate_string` is the single most-called function across all analyzed Anomaly scripts (3,351 uses). Understanding the localization system is not optional.

## Topics to cover

- How string tables work: XML files in `configs/text/<lang>/`
- Language codes: `eng`, `rus`, and others
- String XML format: `<string id="key"><text>Value</text></string>`
- `game.translate_string(key)` — looks up a key in the current language, falls back to `eng`
- Naming conventions for mod string keys (prefix with your mod name to avoid collisions)
- Adding a new string table file for your mod
- The `on_localization_change` callback — fires when the player changes language in settings
- String formatting: Anomaly's `strformat` utility for inserting values into strings
- Multiline strings and special characters
