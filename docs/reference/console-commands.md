# Console Commands Reference

The in-game console gives you direct access to engine variables and commands without modifying any files. Open it with the `` ` `` (backtick/tilde) key.

Type `help` to list every registered command. Type a command name alone (without arguments) to see its current value and accepted range.

---

## -dbg requirement

Several commands — including the most useful ones for modding — are only registered when the game is launched with `-dbg`. Commands in this category are marked **(dbg)** in the tables below. Without `-dbg` they simply do not exist and will produce "unknown command" if typed.

The confirmation comes directly from the source: xray-monolith registers `run_string`, `run_script`, `g_god`, `g_unlimitedammo`, and `jump_to_level` inside a `MASTER_GOLD + strstr(Core.Params, "-dbg")` block (`console_commands.cpp`), meaning they are absent in the shipped binary unless `-dbg` is present.

---

## Scripting & testing

These are the commands you will reach for most often when developing and testing a mod.

| Command | Syntax | Description |
|---------|--------|-------------|
| `run_string` | `run_string <lua expression>` | Execute an arbitrary Lua expression immediately. The most direct way to test a Lua call without touching a script file. **(dbg)** |
| `run_script` | `run_script <filename>` | Execute a `.script` file by name (without extension). **(dbg)** |
| `flush` | `flush` | Force the engine log buffer to disk so output appears in the live log file immediately. Equivalent to calling `flush()` from Lua. |

**`run_string` examples:**

**Advance the game clock**
```
run_string level.change_game_time(0,3,0)
```
Advances the in-game clock by 3 hours. Affects the actual game time — unlike the weather editor, which only changes the visual sky.

**Read the current hour**
```
run_string printf("hour=%s", level.get_time_hours())
```
Prints the current in-game hour to the log. Useful for verifying time-based logic.

**Restore actor health**
```
run_string db.actor:set_health_ex(1.0)
```
Sets the actor to full health instantly. Requires modded exes.

**Show a HUD message**
```
run_string db.actor:give_game_news("", "test message", "ui\\ui_iconsTotal", 0, 3000)
```
Displays a notification in the HUD for 3000 ms. Useful for verifying that a UI call works before wiring it into a callback.

**Teleport to a position**
```
run_string db.actor:set_actor_position(vector():set(-206.0193, -20.3856, -148.0225))
```
Moves the actor to the given world coordinates on the current level without a level reload. The actor snaps to the nearest navmesh vertex, so a slightly imprecise Y value self-corrects on landing. The coordinates above are Rookie Village on Cordon — useful for quickly reaching a safe zone to test zone detection or save logic.

---

## Save & load

| Command | Syntax | Description |
|---------|--------|-------------|
| `save` | `save [name]` | Save the current game. Name is optional; omitting it uses the current save slot. Writes `<name>.scop` to the saves folder. |
| `load` | `load <name>` | Load a save file by name (no extension). |
| `load_last_save` | `load_last_save` | Load the most recently written save file. |
| `flush` | `flush` | Flush the log buffer to disk (also listed above). |

---

## Game state

| Command | Syntax | Description |
|---------|--------|-------------|
| `g_god` | `g_god [0\|1]` | Toggle god mode. Actor takes no damage. **(dbg)** |
| `g_unlimitedammo` | `g_unlimitedammo [0\|1]` | Toggle unlimited ammo. **(dbg)** |
| `time_factor` | `time_factor <value>` | Set the global time scale. `1.0` is normal, `10.0` runs the clock ten times faster. Useful for skipping to night without waiting. Range: `0.001–1000.0`. Always available (no `-dbg` required). |
| `al_time_factor` | `al_time_factor <value>` | Set the A-Life simulation time scale independently of the visual time factor. |
| `freeze_time` | `freeze_time` | Toggle time freeze. |
| `jump_to_level` | `jump_to_level <level_name>` | Teleport to the named level. Level name must match the internal name (e.g. `l01_escape`). **(dbg)** |
| `g_game_difficulty` | `g_game_difficulty <token>` | Change difficulty. Tokens: `novice`, `stalker`, `veteran`, `master`. |

---

## Display & HUD

| Command | Syntax | Description |
|---------|--------|-------------|
| `hud_draw` | `hud_draw [0\|1]` | Show or hide the entire HUD. Useful for clean screenshots. |
| `hud_weapon` | `hud_weapon [0\|1]` | Show or hide the weapon model in the HUD. |
| `hud_info` | `hud_info [0\|1]` | Show or hide the info panel (health, stamina, etc.). |
| `hud_crosshair` | `hud_crosshair [0\|1]` | Show or hide the crosshair. |
| `hud_fov` | `hud_fov <value>` | HUD field of view scale. Range: `0.1–1.0`. Default `0.45`. |
| `fov` | `fov <degrees>` | Player field of view. Range: `5–180`. Default `67.5`. |
| `rs_cam_pos` | `rs_cam_pos [0\|1]` | Show the current camera world-space position on screen. |
| `rs_stats` | `rs_stats [0\|1]` | Show frame time and rendering statistics overlay. |
| `screenshot` | `screenshot` | Save a screenshot to the `screenshots\` folder. |

---

## Graphics & performance

| Command | Syntax | Description |
|---------|--------|-------------|
| `rs_vis_distance` | `rs_vis_distance <value>` | Visibility distance multiplier. Range: `0.4–1.5`. |
| `rs_v_sync` | `rs_v_sync [0\|1]` | Toggle vertical sync. |
| `r__framelimit` | `r__framelimit <fps>` | Cap the frame rate. `0` = uncapped. Range: `0–500`. |
| `texture_lod` | `texture_lod <0–4>` | Texture LOD level. `0` = highest quality. |
| `r__tf_aniso` | `r__tf_aniso <1–16>` | Anisotropic filtering level. |
| `r__geometry_lod` | `r__geometry_lod <value>` | Geometry LOD multiplier. Range: `0.1–1.5`. |
| `rs_c_gamma` | `rs_c_gamma <value>` | Gamma correction. Range: `0.5–1.5`. |

---

## Sound

| Command | Syntax | Description |
|---------|--------|-------------|
| `snd_volume_eff` | `snd_volume_eff <0.0–1.0>` | Effects volume. |
| `snd_volume_music` | `snd_volume_music <0.0–1.0>` | Music volume. |
| `snd_restart` | `snd_restart` | Restart the sound system. |

---

## System

| Command | Syntax | Description |
|---------|--------|-------------|
| `help` | `help` | List all registered commands. |
| `cfg_save` | `cfg_save` | Save current console settings to `user.ltx`. |
| `cfg_load` | `cfg_load` | Load settings from `user.ltx`. |
| `quit` | `quit` | Exit the game immediately. |

---

## Using commands from Lua

Any console command can be triggered from a script using `exec_console_cmd`:

```lua
exec_console_cmd("save my_save_name")
exec_console_cmd("hud_draw 0")
exec_console_cmd("time_factor 5")
exec_console_cmd("run_string level.change_game_time(0,3,0)")
```

`exec_console_cmd` is a global helper defined in `_g.script`. It calls `get_console():execute(cmd)` and also fires the `on_console_execute` callback, so other scripts can observe it. See [game — Console commands](../api-reference/game.md#console-commands) for details.

---

## See also

- [game — Console commands](../api-reference/game.md#console-commands) — calling commands from Lua, reading console variables
- [Debugging & Logging](../scripting/debugging.md) — `run_string` usage, Debug HUD settings, log workflow
- [level — Time](../api-reference/level.md) — `level.change_game_time`, `level.get_time_hours`
