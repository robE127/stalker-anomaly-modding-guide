# Examples

Complete, runnable addon examples. Each one is small enough to read in full but demonstrates a real, useful pattern.

## Examples in this section

- **[Keybind Action](keybind.md)** — Bind a key to trigger a script function. Covers `on_key_press`, DIK constants, and MCM key binding.
- **[Item Use Effect](item-use-effect.md)** — React when the player uses a specific item. Covers `actor_on_item_use` and reading item sections.
- **[NPC Death Reward](npc-death-reward.md)** — Spawn loot or give the player money when a specific NPC type dies. Covers `npc_on_death_callback` and `alife():create`.
- **[MCM Options](mcm-options.md)** — A mod with a full settings screen: checkbox, slider, and key bind options. Covers MCM registration and `ui_mcm.get`.
- **[Callback Logger](callback-logger.md)** — A development tool that logs every known callback in real time. Useful for learning when callbacks fire. Covers the LuaJIT upvalue limit, throttling high-frequency callbacks, and `flush()` for live log output.

!!! tip
    Each example is structured as a complete addon folder you can drop into `gamedata/`. The folder structure and all required files are shown.
