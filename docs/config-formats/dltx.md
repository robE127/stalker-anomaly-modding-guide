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

!!! abstract "Advanced — skip on first read"
    This section covers how DLTX works internally. You don't need it to use DLTX — only read this if you're debugging merge conflicts or need to reason about load order.

This section describes how DLTX actually works inside the engine, based on the C++ source in `CInifile` ([xray-monolith](https://github.com/themrdemonized/xray-monolith) `src/xrCore/Xr_ini.cpp`).

!!! info "Source: modded exes"
    DLTX itself is a modded exes feature — it does not exist in the vanilla Anomaly engine. The implementation details below are derived from the xray-monolith C++ source code.

### Discovery

When the engine finishes reading a base LTX file, it scans the same directory for files matching `mod_<basename>_*.ltx`. For example, when loading `weapons.ltx`, it looks for `mod_weapons_*.ltx`.

**Disambiguation.** If the directory also contains a file like `weapons_upgrades.ltx`, a mod file named `mod_weapons_upgrades_fix.ltx` could match either base file. The engine resolves this by checking all `<basename>_*.ltx` files in the directory and skipping any mod file whose name also matches a longer base filename. In practice, this means `mod_weapons_upgrades_fix.ltx` is assigned to `weapons_upgrades.ltx`, not to `weapons.ltx`.

The matched mod files are returned from a sorted set (`FS_FileSet`), so they are iterated in **ascending alphabetical order by filename**.

### Depth priority

Each key-value pair (called an "item" internally) carries a **depth** value that determines its priority. Lower depth = higher priority.

| Source | Depth |
|--------|-------|
| Base file | `0` |
| File `#include`d by base | `+1`, `+2`, ... (incrementing per include level) |
| 1st mod file (alphabetically) | `-200` |
| 2nd mod file | `-400` |
| 3rd mod file | `-600` |
| File `#include`d by a mod | mod's depth `+1`, `+2`, ... |

The depth decreases by 200 for each subsequent mod file. This means **later alphabetical mod files have stronger priority** — `mod_zzz.ltx` always overrides `mod_aaa.ltx`.

Files `#include`d by a base file get depth `+1`, `+2`, etc. — always higher (weaker) than any mod file. Files included by a mod file get that mod's depth `+1`, which is still far more negative than base depth, so mod includes always beat base includes.

### Sort and merge

Within each section, items are sorted by:

1. Key name (alphabetical)
2. Depth (ascending — lower wins)
3. Insertion index (descending — later insertion wins at same depth)

A deduplication pass then keeps only the first item for each key — the one with the lowest depth. This is how mod values replace base values.

### Section operations at the C++ level

- **`[section]` (normal):** Items go into the `BaseData` map. If two base files define the same section name, the engine calls `Debug.fatal()` and crashes — you must use `![section]` for overrides.
- **`![section]` (override):** Items go into the `OverrideData` map. Multiple overrides for the same section are merged together. During the merge pass, override items replace base items with matching keys.
- **`@[section]` (safe override):** Same as `![section]`, but if no base section exists for this name, an empty base section is created automatically. Use this when your mod might load before the base file that defines the section.
- **`!![section]` (delete):** The section name is added to a `SectionsToDelete` set. After all merges complete, these sections are erased from the final resolved data.

### Key operations at the C++ level

- **`!key`:** The value is replaced with the literal string `"DLTX_DELETE"`. During merge, any key with this marker is added to a `DeletedItems` set and excluded from the output. If the deletion appears in a mod file merging against a base file, the key is removed. If it appears in a parent-inheritance merge, the parent's value is preserved instead.
- **`>key = items`:** The item is stored in a separate `OverrideModifyListData` map. During evaluation, the existing value is split by comma, the new items are appended, and the list is rejoined.
- **`<key = items`:** Same storage as `>`, but during evaluation, matching items are removed from the comma-separated list using `std::remove_if`.

List operations on a key that was deleted via `!key` are silently skipped — the key is not recreated.

### Inheritance resolution

Parent sections are resolved recursively. The engine detects cyclical inheritance (A inherits B which inherits A) and calls `Debug.fatal()` if found. The `[section]:!parent` syntax removes a parent from the inheritance chain during the merge pass.

!!! warning "Override inheriting from override"
    If a section inherits from a parent that was itself defined as an override (not a base section), the engine prints a warning and creates a fallback empty base section for backwards compatibility. This works but is not recommended.

### Controlling load order

To control which mod file wins, use naming prefixes:

```
mod_aaa_my_early_patch.ltx      ← loads first (depth -200)
mod_zzz_my_late_patch.ltx       ← loads last (depth -400), overrides earlier patches
```

Some modpacks use a naming convention like `mod_system_zzzzzz_<name>.ltx` to force late loading.

!!! note "Section names are case-insensitive"
    The engine converts all section names to lowercase during parsing. `[WPN_AK74]` and `[wpn_ak74]` are the same section.

---

## Caching

The engine caches the fully-resolved result of each LTX file (after all DLTX merges) in memory. On subsequent loads of the same file, the cached result is returned immediately — no file I/O or parsing occurs. Caching is enabled by default and is thread-safe.

The cache persists for the entire game session. If you modify a DLTX file while the game is running, the changes won't take effect until the cache is invalidated (see below) or the game is restarted.

Lua scripts can force a full reload of the config system at runtime via `reload_system_ini()`, which invalidates the cache for `system.ltx` and recreates the global `pSettings` object.

---

## Debugging DLTX

The modded exes provide console commands for diagnosing DLTX issues:

| Console command | Effect |
|-----------------|--------|
| `print_dltx_warnings 1` | Enables diagnostic logging: malformed lines, override sections without a matching base section, disambiguation decisions, section deletions. Off by default. |
| `dltx_use_cache 0` | Disables the DLTX parse cache and immediately clears all cached data. Useful if you suspect stale data during development. Re-enable for normal play (`dltx_use_cache 1`). |

### Lua debugging API

These methods are available on any `ini_file` object (including `system_ini()`):

```lua
local ini = system_ini()

-- Which file defined this specific key?
local source_file = ini:dltx_get_filename_of_line("wpn_ak74", "rpm")
-- Returns nil if the section or key doesn't exist

-- Is this key from a DLTX mod file or the base file?
local is_override = ini:dltx_is_override("wpn_ak74", "rpm")
-- Returns true if the source filename starts with "mod_"

-- Print all key-value pairs in a section with their source files
ini:dltx_print("wpn_ak74")
-- Output per line: "key = value -> filename"
-- Pass nil to print ALL sections (very verbose)

-- Get full introspection data for a section
local section_data = ini:dltx_get_section("wpn_ak74")
-- Returns a Lua table: { key_name = { name, value, filename }, ... }
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

---

## See also

- [LTX Format](ltx.md) — the base format DLTX patches
