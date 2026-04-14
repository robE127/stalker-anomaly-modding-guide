# Script Lifecycle

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- When the engine loads scripts (at game startup, not per-level)
- Execution order: alphabetical by filename within `gamedata/scripts/`
- Top-level code runs at load time — what is and isn't safe to do at module level
- Why `actor_on_first_update` exists: the actor object isn't available until the first update tick
- The difference between `on_game_load` (fires after loading a save) and `actor_on_first_update` (fires when the world simulation is ready)
- Script reload: not possible at runtime without restarting — implications for development
- Depending on another script: calling functions across scripts, load-order risks
