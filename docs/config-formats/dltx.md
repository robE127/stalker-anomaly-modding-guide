# DLTX — LTX Patching

DLTX lets you add, modify, or delete values in existing LTX sections without replacing the original file. It's the correct way to change item stats, weapon properties, or any other LTX-defined value when compatibility with other mods matters.

---

## Why DLTX exists

Without DLTX, modifying an LTX value means copying the entire file and editing it. If two mods both copy the same file, only one survives — the last one loaded wins and the other's changes are silently discarded.

DLTX files are **patches**, not replacements. The engine merges them on top of the base files at startup. Multiple DLTX patches targeting the same section all apply in sequence.

---

## File naming

DLTX patch files follow the convention:

```
mod_<your_mod_name>.ltx
```

Place the file in the same folder as the file you're patching:

```
gamedata/
  configs/
    items/
      weapons/
        mod_my_mod_weapons.ltx     ← patches weapon LTX values
    items/
      items/
        mod_my_mod_food.ltx        ← patches food item values
    creatures/
      mod_my_mod_creatures.ltx     ← patches creature values
```

The `mod_` prefix is what tells DLTX to treat the file as a patch rather than a standalone definition. Internally, the engine scans for files matching `mod_<basename>_*.ltx` in the same folder as the base file and loads them as patches.

---

## Modifying values

To change a value in an existing section, write a block with only the keys you want to change:

```ltx
; Change the weight and cost of vodka
[vodka]
inv_weight = 0.8
cost = 500
```

You don't need to copy the entire `[vodka]` section — only the keys you include are updated. All other keys retain their original values.

---

## Deleting a key

Prefix the key name with `!` to remove it from the section:

```ltx
[wpn_ak74]
!snd_empty          ; remove the empty-mag sound
!fire_distance      ; remove the fire distance override (reverts to parent)
```

Internally, the engine replaces the value with a `DLTX_DELETE` marker. During merge, any key marked for deletion is excluded from the final output.

---

## Deleting a section

Use `!![section_name]` to remove an entire section:

```ltx
!![my_old_item]      ; completely removes this section
```

---

## Overriding a section

The `![section]` prefix replaces the entire section from the base file with the content you provide. Unlike a normal patch (which merges individual keys), an override discards all base values and starts fresh:

```ltx
; Replace the entire section — base values are discarded
![my_item]
key1 = new_value
key2 = new_value
```

If you want override behaviour but need the section to be created when it doesn't already exist, use `@[section]` (safe override):

```ltx
; Override if exists, create if it doesn't
@[my_item]
key1 = new_value
key2 = new_value
```

A normal `![section]` on a section that doesn't exist in the base file is a no-op — the engine logs a warning. `@[section]` avoids that problem.

---

## Adding new sections

You can define entirely new sections in a DLTX file — just write them without a prefix. These follow normal LTX rules including inheritance:

```ltx
; New item that inherits from an existing base
[my_mod_special_vodka]:vodka
inv_name    = st_my_mod_special_vodka
cost        = 1500
eat_health  = 0.2
```

---

## Modifying comma-separated lists

Many LTX values are comma-separated lists (e.g. loot tables, immunities, weapon modes). DLTX supports appending to and removing from these lists without replacing the entire value.

### Append items to a list

Prefix the key with `>` to append items:

```ltx
[stalker_immunities]
>burn_immunity = my_mod_burn_resist
```

If the base value is `item1, item2`, the result is `item1, item2, my_mod_burn_resist`.

You can append multiple items at once:

```ltx
[my_loot_table]
>supplies = medkit, bandage, vodka
```

### Remove items from a list

Prefix the key with `<` to remove items:

```ltx
[my_loot_table]
<supplies = vodka, cigarettes
```

If the base value is `medkit, bandage, vodka, cigarettes`, the result is `medkit, bandage`.

### Combining list operations

Multiple `>` and `<` operations on the same key apply in file order:

```ltx
[my_loot_table]
<supplies = old_item         ; remove old_item first
>supplies = new_item         ; then append new_item
```

!!! note
    List modification is order-sensitive. Removals and additions are applied sequentially in the order they appear across all DLTX files (alphabetical by filename).

---

## Removing a parent from inheritance

If a section inherits from multiple parents and you want to remove one, use `!parent_name` in the inheritance list:

```ltx
; If [my_weapon]:base_weapon, rifle_base originally
; Remove rifle_base from the parent list
[my_weapon]:!rifle_base
```

---

## Real examples

### Buff a weapon's fire rate

```ltx
; mod_my_mod_weapons.ltx
[wpn_ak74]
rpm = 650
fire_dispersion_base = 0.18
```

### Replace a sound on multiple weapons

```ltx
; mod_my_mod_sounds.ltx
[wpn_ak74]
snd_shoot = my_mod\ak74_shoot

[wpn_ak74u]
snd_shoot = my_mod\ak74u_shoot

[wpn_akm]
snd_shoot = my_mod\akm_shoot
```

### Remove a property and change another

```ltx
; mod_my_mod_food.ltx — make food weightless and cheaper
[conserva]
!inv_weight             ; removes the weight field (engine uses 0 or base)
cost = 50
```

### Add items to a loot table

```ltx
; mod_my_mod_loot.ltx — add custom items to existing loot lists
[stalker_outfit_loot]
>items = my_mod_patches, my_mod_toolkit
```

### New item inheriting from existing base

```ltx
; mod_my_mod_items.ltx
[my_mod_energy_drink]:booster_multi
$spawn          = "food and drugs\my_mod_energy_drink"
inv_name        = st_my_mod_energy_drink
inv_name_short  = st_my_mod_energy_drink
description     = st_my_mod_energy_drink_descr
inv_weight      = 0.3
cost            = 800
eat_power       = 0.5
boost_time      = 60
inv_grid_x      = 3
inv_grid_y      = 22
inv_grid_width  = 1
inv_grid_height = 1
```

---

## Load order and merge algorithm

DLTX files are loaded in alphabetical order within each folder. The merge algorithm works in stages:

1. **Discovery.** The engine scans for `mod_<basename>_*.ltx` files in the same directory as each base LTX file.
2. **Parsing.** Each DLTX file is parsed. Mod files are assigned a negative depth value (-200), making them higher priority than the base file (depth 0).
3. **Sort and filter.** Items are sorted by key name (alphabetical), then by depth (ascending), then by insertion index (descending). For duplicate keys at the same depth, the last-loaded file wins.
4. **Merge.** Override items replace base items with matching keys. `DLTX_DELETE` markers remove keys. New keys from overrides are added.
5. **Inheritance.** Parent sections are resolved with recursion detection.
6. **List modification.** `>` and `<` operations are applied in insertion order.

To control load order, use a naming prefix:

```
mod_aaa_my_early_patch.ltx      ← loads first
mod_zzz_my_late_patch.ltx       ← loads last, overrides earlier patches
```

Some modpacks use a naming convention like `mod_system_zzzzzz_<name>.ltx` to force late loading.

!!! note "Section names are case-insensitive"
    The engine converts all section names to lowercase during parsing. `[WPN_AK74]` and `[wpn_ak74]` are the same section.

---

## Debugging DLTX

The modded exes provide console variables for diagnosing DLTX issues:

| Console variable | Effect |
|-----------------|--------|
| `print_dltx_warnings 1` | Logs warnings for: cache hits, malformed lines, override sections without a matching base section, and duplicate sections |
| `dltx_use_cache 0` | Disables the DLTX parse cache (useful if you suspect stale data; re-enable for normal play) |

You can also use these Lua functions on any `ini_file` object to trace where a config value came from:

```lua
local ini = system_ini()
-- Which file defined this specific line?
local source_file = ini:dltx_get_filename_of_line("wpn_ak74", "rpm")
-- Is this line from a DLTX override or the base file?
local is_override = ini:dltx_is_override("wpn_ak74", "rpm")
-- Print all override info for a section
ini:dltx_print("wpn_ak74")
```

---

## Syntax summary

| Syntax | Effect |
|--------|--------|
| `[section]` | Patch section — merge keys into existing section, or create new |
| `![section]` | Override section — discard base values, replace with these |
| `@[section]` | Safe override — like `![]` but creates the section if it doesn't exist |
| `!![section]` | Delete section entirely |
| `key = value` | Set or replace a key |
| `!key` | Delete a key |
| `>key = item1, item2` | Append items to a comma-separated list |
| `<key = item1, item2` | Remove items from a comma-separated list |
| `[child]:!parent` | Remove a parent from the inheritance chain |

---

## Limitations

- **Can't reorder list values.** If a field is `a, b, c` and you want `c, b, a`, you must replace the whole value. The `>` and `<` operators only append and remove — they don't reorder.
- **Inheritance is static.** You can change a child section's own values and remove parents with `!parent`, but you can't add new parents after the fact.
- **No conditionals.** DLTX has no if/else logic — all patches are always applied.

---

## DLTX vs editing files directly

| | Edit file directly | DLTX patch |
|--|--|--|
| Other mods sharing the file | Conflict — one mod wins | All mods apply their patches |
| Patch scope | Entire file | Only specified keys |
| Update resilience | Must re-diff on game updates | Only patched keys affected |
| Works without DLTX installed | Yes | No (DLTX must be present) |

!!! warning "DLTX requires the modded exes"
    DLTX is **not** part of vanilla Anomaly. It is included in the community **modded exes** maintained by themrdemonized ([xray-monolith](https://github.com/themrdemonized/xray-monolith)), which replace the vanilla engine binaries. Most active mods and all major modpacks (GAMMA, EFP, etc.) require these exes — if you're targeting a general audience, list them as a hard dependency in your README.
