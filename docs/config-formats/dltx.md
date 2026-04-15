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

The `mod_` prefix is what tells DLTX to treat the file as a patch rather than a standalone definition.

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

---

## Deleting a section

Use `![section_name]` to remove an entire section:

```ltx
![my_old_item]      ; completely removes this section
```

---

## Adding new sections

You can define entirely new sections in a DLTX file — just write them without the `!` prefix. These follow normal LTX rules including inheritance:

```ltx
; New item that inherits from an existing base
[my_mod_special_vodka]:vodka
inv_name    = st_my_mod_special_vodka
cost        = 1500
eat_health  = 0.2
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

## Load order

DLTX files are loaded in alphabetical order within each folder. If two DLTX files patch the same key in the same section, the last one alphabetically wins.

To control load order, use a naming prefix:

```
mod_aaa_my_early_patch.ltx      ← loads first
mod_zzz_my_late_patch.ltx       ← loads last, overrides earlier patches
```

Some modpacks use a numeric prefix convention like `mod_system_zzzzzz_<name>.ltx` to force late loading.

---

## Limitations

- **Can't reorder list values.** If a field is `a, b, c` and you write `c, b, a`, you replace the whole list. You can't insert into the middle of a comma-separated list.
- **Can't merge multi-value fields.** Writing a new value for a list key replaces the entire list, not appends to it.
- **Inheritance is static.** You can change a child section's own values, but you can't change which parent it inherits from after the fact.
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
