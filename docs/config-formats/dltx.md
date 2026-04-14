# DLTX — LTX Patching

!!! note "Work in progress"
    This page is being written. Content coming soon.

DLTX lets you add, modify, or delete LTX section values without replacing the original file. Essential for addon compatibility.

## Topics to cover

- Why DLTX exists: same motivation as DXML — prevents file conflicts between addons
- File naming convention: `mod_<your_mod_name>.ltx` placed in the relevant config subfolder
- DLTX directives:
  - `!include <original_file>` — the base file this patch targets
  - `[section_name]` with only the keys you want to change (values are merged, not replaced)
  - `[section_name]:delete` — remove a section entirely
  - `![section_name]` — delete specific keys from a section
- How the engine processes DLTX files on startup
- Ordering: when multiple DLTX files target the same section, last-loaded wins
- Limitations: DLTX can't reorder multi-value lists, only append/replace scalar values
