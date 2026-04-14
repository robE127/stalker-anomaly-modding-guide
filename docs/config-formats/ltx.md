# LTX Format

!!! note "Work in progress"
    This page is being written. Content coming soon.

LTX is a custom INI-like format used by the X-Ray engine for the majority of game data definitions.

## Topics to cover

- Basic syntax: `[section_name]` headers, `key = value` pairs, comments with `;`
- Section inheritance: `[child_section]:parent_section` — child inherits all parent values and can override them
- Multi-value fields: comma-separated lists
- Include directives: `#include "other_file.ltx"`
- Reading LTX from Lua:
  - `ini_file` userdata: `ini:r_string(section, key)`, `ini:r_float(section, key)`, `ini:r_u32`, `ini:r_bool`
  - `ini:line_exist(section, key)` — check key presence before reading
  - `ini:section_exist(section)` — check section presence
  - `system_ini()` — the global system config (all merged LTX files)
- Common LTX files: `system.ltx`, `items/weapons/*.ltx`, `creatures/*.ltx`
- Gotchas: case sensitivity, trailing whitespace, Windows line endings
