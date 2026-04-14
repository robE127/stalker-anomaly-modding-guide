# xr_logic

!!! note "Work in progress"
    This page is being written. Content coming soon.

`xr_logic` is a script module (not an engine global) providing condition list evaluation and logic scheme utilities. It appears in 317 places across the analyzed repos, making it one of the most important utility modules to understand.

## Topics to cover

- What a condition list is: a mini-language in LTX config values that evaluates to a string result based on game state
  - Example: `on_info = {+info_portion_given} section_a, section_b`
- `xr_logic.pick_section_from_condlist(actor, obj, condlist)` — evaluate a parsed condlist
- `xr_logic.cfg_get_string(ini, section, field, obj, mandatory, default)` — safe INI value reader
- `xr_logic.parse_condlist(obj, section, field, str)` — parse a condlist string into a table
- How logic schemes work: `on_info`, `on_timer`, `on_signal` and their evaluation
- Common pattern: reading a config value that might be a condlist
