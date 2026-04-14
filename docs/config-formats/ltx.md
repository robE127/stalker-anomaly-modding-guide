# LTX Format

LTX is X-Ray's custom INI-like format. It's used for almost all game data definitions — items, weapons, creatures, AI behavior, physics properties, and more. Understanding it is essential for any mod that touches stats or config values.

---

## Basic syntax

```ltx
; This is a comment

[section_name]
key = value
another_key = 1.5
flag = true
list_value = item_a, item_b, item_c
```

- Sections are declared with `[section_name]`
- Keys and values are separated by `=`
- `;` begins a comment (rest of line is ignored)
- Values can be strings, numbers, booleans (`true`/`false`), or comma-separated lists
- Whitespace around `=` is ignored; trailing whitespace on values is also ignored

---

## Section inheritance

A section can inherit all properties from a parent section:

```ltx
[child_section]:parent_section
; Only override what differs
health = 500
speed = 2.0
```

The child gets every property defined in the parent. Any key defined in the child overwrites the parent's value for that key. This is how Anomaly builds its item hierarchy — most weapons inherit from a base weapon section, most food items from a consumable base, etc.

**Multiple inheritance** is supported:

```ltx
[my_item]:base_item,identity_immunities
```

The engine merges all ancestor properties, resolving conflicts left-to-right.

---

## Include directives

LTX files can include other LTX files. The included file's contents are merged in at that point.

```ltx
#include "weapons_base.ltx"
#include "upgrades\upgrade_presets.ltx"

; Wildcards load all matching files
#include "w_*.ltx"
#include "items_*.ltx"
```

This is how the engine's master config files work — `system.ltx` includes dozens of sub-files, and `configs/items/weapons/base.ltx` uses `#include "w_*.ltx"` to load all weapon definitions automatically.

**Paths** in includes are relative to the file containing the directive.

---

## Data types

| LTX value | Lua read method | Example |
|-----------|----------------|---------|
| String | `r_string` / `r_string_ex` | `"stalker"`, `"my_sound_file"` |
| Float | `r_float` / `r_float_ex` | `1.5`, `0.25`, `-10` |
| Integer (signed) | `r_s32` | `42`, `-1` |
| Integer (unsigned) | `r_u32` | `0`, `65535` |
| Boolean | `r_bool` / `r_bool_ex` | `true`, `false` |
| Comma list | `r_string` then split | `a, b, c` |

---

## Reading LTX from Lua

### The system ini

`system_ini()` returns the engine's merged view of all loaded LTX files. It's the main way scripts access item stats, creature properties, and global settings:

```lua
local ini = system_ini()   -- or use the global alias: ini_sys
```

`ini_sys` is a cached reference to `system_ini()` defined in `_g.script` — prefer it over calling `system_ini()` directly in hot paths.

### Read methods

```lua
local sec = "my_item_section"

-- Strings
local name   = ini_sys:r_string(sec, "inv_name")          -- errors if missing
local name   = ini_sys:r_string_ex(sec, "inv_name")       -- returns nil if missing

-- Numbers
local weight = ini_sys:r_float(sec, "inv_weight")
local weight = ini_sys:r_float_ex(sec, "inv_weight")      -- returns nil if missing
local cost   = ini_sys:r_u32(sec, "cost")                  -- unsigned int
local rank   = ini_sys:r_s32(sec, "min_rank")              -- signed int

-- Booleans
local usable = ini_sys:r_bool(sec, "use_condition")
local usable = ini_sys:r_bool_ex(sec, "use_condition")    -- returns nil if missing

-- Existence checks (always do this before r_string/r_float/r_bool to avoid errors)
if ini_sys:section_exist(sec) then
    -- section is present
end

if ini_sys:line_exist(sec, "special_field") then
    -- key exists in this section
end
```

The `_ex` variants return `nil` instead of throwing an error when the section or key is missing. **Always use `_ex` variants** unless you're certain the field must exist.

### Loading a custom ini file

```lua
-- Load an ini file directly (path relative to gamedata/)
local my_ini = ini_file("configs\\my_mod\\settings.ltx")

local value = my_ini:r_float_ex("settings", "some_value") or 1.0
```

### Safe read pattern

```lua
local function read_cfg(section, key, default)
    if not ini_sys:section_exist(section) then return default end
    if not ini_sys:line_exist(section, key) then return default end
    return ini_sys:r_string_ex(section, key) or default
end
```

---

## Common LTX structure patterns

### Item definition

```ltx
[my_item]:booster_multi    ; inherits from booster_multi base
$spawn          = "food and drugs\my_item"
inv_name        = st_my_item
inv_name_short  = st_my_item
description     = st_my_item_descr
inv_weight      = 0.5
cost            = 300
inv_grid_x      = 5
inv_grid_y      = 12
inv_grid_width  = 1
inv_grid_height = 1
eat_health      = 0.1
boost_time      = 30
```

### Weapon definition (abbreviated)

```ltx
[wpn_my_pistol]:wpn_pistol_base
inv_name        = st_wpn_my_pistol
hit_power       = 0.45, 0.45, 0.45, 0.45
fire_distance   = 60
ammo_class      = ammo_9x18_fmj, ammo_9x18_pbp
rpm             = 300
```

---

## Common files

| File | Contents |
|------|----------|
| `configs/system.ltx` | Master include file — loads everything else |
| `configs/items/items/items_*.ltx` | Consumables, artefacts, equipment |
| `configs/items/weapons/w_*.ltx` | Weapon definitions |
| `configs/creatures/m_*.ltx` | Creature / mutant definitions |
| `configs/creatures/monsters.ltx` | Includes all creature files |
| `configs/gameplay/character_desc_*.ltx` | NPC character definitions |
| `configs/misc/zone_*.ltx` | Anomaly zone definitions |

---

## Gotchas

**Case sensitivity.** Section names and keys are case-sensitive on some builds. Use lowercase consistently.

**No spaces in section names.** `[my section]` is invalid. Use underscores: `[my_section]`.

**Boolean values are strictly `true` or `false`.** `1`, `yes`, or `on` will not be parsed as booleans by `r_bool`.

**Comma-separated lists have no fixed length.** Read them as a string with `r_string_ex` then split on `,`:

```lua
local ammo_str = ini_sys:r_string_ex("wpn_ak74", "ammo_class") or ""
local ammo_list = {}
for sec in ammo_str:gmatch("[^,%s]+") do
    ammo_list[#ammo_list + 1] = sec
end
```

**Modding:** Don't edit base game LTX files directly — use [DLTX](dltx.md) to patch only the values you need to change.
