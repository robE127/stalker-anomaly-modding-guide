# game

!!! note "Work in progress"
    This page is being written. Content coming soon.

The `game` global provides engine-wide utilities: localization, time, difficulty, and game flow control.

## Topics to cover

- `game.translate_string(key)` — the most-called function in all of Anomaly (3351 uses across analyzed repos); looks up a localization key from `configs/text/<lang>/`
- `game.get_game_time()` — returns a `CTime` userdata object representing in-game time
- `CTime` methods: `:timeToString(fmt)`, `:diffSec(other)`, individual field accessors
- `game.time()` — raw in-game time in seconds since game epoch
- `game.difficulty()` — current difficulty level
- `game.start_tutorial(name)` — trigger a tutorial/hint popup
- `game.only_allow_monster_attack` and other game state flags
- `game.ConsoleExecute(cmd)` — run a console command from script
