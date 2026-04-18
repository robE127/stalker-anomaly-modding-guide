# Extraction Mod — Test Plan

Tests for `extraction_mod.script` as currently implemented. Run in order —
each section builds on the previous one. All tests require modded exes
(xray-monolith) and `-dbg` launch flag to verify log output.

**Test character:** start a new game or use an existing save on Cordon
(`l01_escape`) — the only level whose safe zone coordinates are confirmed.

---

## Setup checklist

Before starting any tests:

- [ ] Mod is enabled in MO2 and has the correct priority
- [ ] Game launched with `-dbg` (for real-time log output)
- [ ] Log file open in Notepad++ / VS Code: `appdata\logs\xray_<username>.log`
- [ ] Saves folder open in Explorer: `appdata\savedgames\`
- [ ] No existing `extraction_save.scop` file (delete it to start clean)
- [ ] **Debug HUD enabled** (Options → Others → Debug HUD) — shows the actual in-game clock, essential for Features 8 and 9

**Changing in-game time:** use `run_string level.change_game_time(0,h,0)` in the console to advance time by `h` hours. Do **not** use the weather editor — it changes the visual sky but not the game clock that the mod reads. `time_factor` also works but requires waiting; `run_string` is instant.

---

## Feature 1 — Base zone detection and initial save

**Goal:** verify the mod detects Rookie Village as a safe zone on first entry
and writes the correct save file.

| # | Steps | Expected result |
|---|-------|-----------------|
| 1.1 | Load into Cordon. Walk to Rookie Village (the stalker starting camp). | HUD toast: **"Base reached — game saved."** |
| 1.2 | Check the saves folder. | `extraction_save.scop` exists. No other `.scop` files written at this point. |
| 1.3 | Check the log for `[EM] actor_on_update: entered base zone`. | Line present. `level=l01_escape`. |
| 1.4 | Walk out of Rookie Village to the open field. Wait ~10 seconds. Walk back in. | Toast fires again on re-entry. Save file timestamp updates. |
| 1.5 | Walk to the Northern Farm safe zone (north of the level). | Toast fires. Save updates. Confirms second zone on the same level works. |

---

## Feature 2 — Save restriction: quicksave blocked outside base

**Goal:** verify the quicksave key does nothing outside a safe zone and redirects
correctly inside one.

| # | Steps | Expected result |
|---|-------|-----------------|
| 2.1 | Walk to an area with no safe zone (middle of Cordon). Press quicksave (default: F6). | HUD toast: **"Cannot save — not at a friendly base!"** No new `.scop` file written. |
| 2.2 | Check the log. | `[EM] on_before_save_input: BLOCKED` present. |
| 2.3 | Walk back into Rookie Village. Press quicksave. | No "Cannot save" message. Save file timestamp updates (redirected to `extraction_save`). |
| 2.4 | Check the log. | `[EM] on_before_save_input: redirecting quicksave` present. |

---

## Feature 3 — Save restriction: menu save blocked outside base

**Goal:** verify saves from the pause menu are intercepted and deleted when
outside a safe zone.

| # | Steps | Expected result |
|---|-------|-----------------|
| 3.1 | Walk outside any safe zone. Open the pause menu → Save → type any name → confirm. | HUD toast: **"Cannot save outside a friendly base! Save deleted."** |
| 3.2 | Check the saves folder. | No new `.scop` file with the name you typed. `extraction_save.scop` is unchanged. |
| 3.3 | Check the log. | `[EM] on_console_execute: NOT in safe zone — deleting` present with the name you typed. |
| 3.4 | Go into Rookie Village. Open pause menu → Save → type any name → confirm. | No "Cannot save" message. `extraction_save.scop` timestamp updates. The wrong-named file does not persist. |
| 3.5 | Check the log. | `[EM] on_console_execute: in safe zone but external save ... redirecting` present. |

---

## Feature 4 — Save restriction: autosave silently discarded outside base

**Goal:** verify engine autosaves outside a safe zone are deleted without
showing the player a warning message (since autosaves are not player-initiated).

| # | Steps | Expected result |
|---|-------|-----------------|
| 4.1 | Walk outside any safe zone. Trigger an autosave by sleeping at a campfire or using a debug console command: `save roced - autosave`. | No HUD toast shown to the player. |
| 4.2 | Check the saves folder. | The autosave file does not persist. `extraction_save.scop` unchanged. |
| 4.3 | Check the log. | `on_console_execute: NOT in safe zone — deleting` is logged but no `show_msg` call (because `is_engine_save` was true). |
| 4.4 | Travel to a level transition (e.g. Cordon → Garbage or any other level change). Allow the loading screen to complete. | No HUD toast for the transition. |
| 4.5 | Check the saves folder immediately after the new level loads. | The transition autosave (e.g. `player - autosave.scop`) does **not** exist. Only `extraction_save.scop` is present (if one was written before the transition). |
| 4.6 | Check the log on the new level. | `[EM] actor_on_first_update: deleting transition autosave '<user_name> - autosave' if present` present. No autosave file remains. |

**Note on 4.4–4.6:** the engine writes `<user_name> - autosave` as part of every level transition (C++ `Core.UserName + " - autosave"`). `on_console_execute` fires as a pre-notification before the file is written, so the delete there is a no-op. The fix uses two callbacks:
- `on_level_changing` (fires before the level unloads): writes `em_transition_flag` to the saves folder.
- `actor_on_first_update` (fires after the new level loads): checks for the flag. If present — this session caused the transition — deletes `user_name() .. " - autosave"` and removes the flag. If absent — no transition was triggered by this session (e.g. fresh game start or load from menu) — skips the delete to preserve any pre-existing autosave from another playthrough.

**`Core.UserName` is not reliably the OS username** — xray-monolith overrides it to the hardcoded string `"Player"` when `[string_table]` contains `no_native_input` (Anomaly ships with this set). On most installs `user_name()` returns `"Player"` regardless of the actual Windows account. The log file is named before this override runs, so it uses the real OS login name.

---

## Feature 5 — Single save file: only one slot exists

**Goal:** verify that at no point are more than one `.scop` file present,
regardless of how saves are triggered.

| # | Steps | Expected result |
|---|-------|-----------------|
| 5.1 | From inside Rookie Village, trigger saves three different ways in sequence: quicksave, menu save (any name), console command `save some_other_name`. | Only `extraction_save.scop` exists in the saves folder at all times. |
| 5.2 | Note the timestamp of `extraction_save.scop` after each save action. | Timestamp advances each time. |

---

## Feature 6 — Death: stash spawns at death location

**Goal:** verify the inventory backpack stash appears at the correct position
when the player dies.

| # | Steps | Expected result |
|---|-------|-----------------|
| 6.1 | Pick up several distinct items (different weapons, items) so the inventory is non-empty. Note the items and your position. | — |
| 6.2 | Die (walk into an anomaly field or use console `g_god off` then let an NPC kill you). | Screen fades to black. No game-over screen. |
| 6.3 | After respawn, travel back to the death location. | A backpack item (`inv_backpack`) is present at or near the death site. |
| 6.4 | Open the backpack. | All items from your inventory at time of death are inside it. |
| 6.5 | Check the log. | `actor_on_before_death: stash created`, `wait_for_stash_and_respawn: stash id=... is ONLINE`, `transferring N items` all present. |
| 6.6 | Drop all items so the inventory is empty. Die. | No backpack appears at the death site. |
| 6.7 | Check the log for the empty-inventory case. | `inventory count=0` and `inventory empty -- skipping stash` present. No `stash created` line. |

---

## Feature 7 — Death: same-level respawn

**Goal:** verify the player respawns at the last recorded base position on
the same level.

| # | Steps | Expected result |
|---|-------|-----------------|
| 7.1 | Enter Rookie Village (saves and records position). Note the exact position. | Toast: "Base reached — game saved." |
| 7.2 | Walk far from Rookie Village. Die. | Fade to black, then fade back in. |
| 7.3 | Observe spawn location. | Player is at or very close to the Rookie Village position recorded in step 7.1. |
| 7.4 | Verify the player is fully functional: can move, open inventory, fire weapons, interact with NPCs. | No "ghost camera" state, full HUD visible, shadow present. |
| 7.5 | Verify player stats. | Full health, no bleeding, no radiation, no hurt sounds. |
| 7.6 | Check the saves folder. | `extraction_save.scop` timestamp updated (post-respawn save written by `actor_on_update` when the player arrives in the safe zone). |

---

## Feature 8 — Death: night respawn time advance

**Goal:** verify that dying at night (20:00–08:00) advances the clock to 08:00
before respawning.

| # | Steps | Expected result |
|---|-------|-----------------|
| 8.1 | Open the console and run `run_string level.change_game_time(0,2,0)` repeatedly until the Debug HUD shows a time between 20:00 and 23:59. | Debug HUD clock updates immediately to confirm the actual game time. |
| 8.2 | Die. | — |
| 8.3 | After respawn, check the Debug HUD clock. | Time reads 08:00 (or very close). |
| 8.4 | Repeat with the clock set past midnight (e.g. run enough `change_game_time` calls to reach 03:00). | Same result: clock reads 08:00 after respawn. |
| 8.5 | Set time to daytime (e.g. `run_string level.change_game_time(0,6,0)` from 08:00 to reach 14:00). Die. | Clock is **not** advanced. Time after respawn is still ~14:00. |

---

## Feature 9 — Death: invulnerability window and no hurt sounds

**Goal:** verify the player does not immediately re-die from residual damage
after respawn, and that hurt sounds stop.

| # | Steps | Expected result |
|---|-------|-----------------|
| 9.1 | Die in a location with ongoing damage (anomaly, heavy radiation, fire). Respawn. | Player does not immediately die again despite still being in a damage zone. |
| 9.2 | Immediately after respawn, listen for hurt/injury sounds. | No hurt sounds or gasping after respawn. (This verifies `wounded(false)` and `invulnerable_time` expiry both work.) |
| 9.3 | Wait 5–10 seconds after respawn. | Player can be damaged normally again (invulnerability window has expired). |

---

## Feature 10 — No-base edge case

**Goal:** verify the mod degrades gracefully when the player dies before ever
reaching a base.

| # | Steps | Expected result |
|---|-------|-----------------|
| 10.1 | Start a completely fresh save (no base recorded). Die immediately. | HUD toast: **"WARNING: No base on record — you wake where you fell! Visit a base first."** |
| 10.2 | Verify player position after respawn. | Player wakes at the death location (no teleport attempted). |
| 10.3 | Verify no save was written during this respawn. | `extraction_save.scop` does not exist (or its timestamp is unchanged if it existed from before). The save will be written once the player reaches a base. |

---

## Feature 11 — Save/load round-trip

**Goal:** verify the base position persists correctly across a save and reload.

| # | Steps | Expected result |
|---|-------|-----------------|
| 11.1 | Enter Rookie Village. Confirm save written. | Toast: "Base reached — game saved." |
| 11.2 | Walk to Northern Farm. Confirm save updates (new base recorded). | Toast fires. |
| 11.3 | Quit to main menu. Load `extraction_save`. | Game loads successfully. |
| 11.4 | Die anywhere on Cordon. | Respawn at Northern Farm (the most recently recorded base). |
| 11.5 | Check the log. | `load_state: level=l01_escape pos=(...)` with Northern Farm coordinates. |

---

## Feature 12 — PDA stash marker

**Goal:** verify the death stash appears on the PDA map, can be toggled via MCM,
and the marker disappears when the stash is looted.

**Requires MCM to be installed.**

| # | Steps | Expected result |
|---|-------|-----------------|
| 12.1 | Open MCM → Extraction Mod. Confirm the "Show death stash location on PDA" checkbox is present and defaults to enabled. | Checkbox visible and ticked. |
| 12.2 | With the option enabled, die with items in your inventory. After respawn, open the PDA map. | A secondary task marker appears at the death location, labelled **"Death: DD.MM.YYYY HH:MM"** using the in-game date and time of death. |
| 12.3 | Travel to the stash. Take any one item from it. Open the PDA map. | The marker is removed immediately after taking the first item. |
| 12.4 | Check the log. | `added PDA marker for stash id=...` on death, `removed stash marker for id=...` on loot. |
| 12.5 | Save and reload. Check the PDA map before visiting the stash. | Marker is still present after reload (persisted by `map_add_object_spot_ser`). |
| 12.6 | In MCM, disable "Show death stash location on PDA". Die with items. | No marker appears on the PDA map after respawn. |
| 12.7 | Die with no items (empty inventory). | No marker appears regardless of MCM setting (no stash was created). |

---

## Feature 13 — Faction-aware safe zones

**Goal:** verify the mod only accepts a zone as safe when the player's faction is
friendly with the zone's owner, and that neutral (ownerless) zones are always
accessible.

**Test character faction:** check with console `get_actor_true_community` or look
at the character info screen. Default new-game faction is `stalker`.

| # | Steps | Expected result |
|---|-------|-----------------|
| 13.1 | As a loner (`stalker`), enter Rookie Village. | Toast: **"Base reached — game saved."** (stalker zone, player is stalker — friendly). |
| 13.2 | As a loner, walk to the Army Checkpoint on Cordon. | **No** toast. Save is NOT triggered. Log: `is_in_safe_zone` returns false because `stalker` is not friends with `army`. |
| 13.3 | As a loner, walk to the Garbage Stalker Hangar (ownerless zone). | Toast fires. Confirms neutral zones work regardless of faction. |
| 13.4 | Check the log for a faction-gated rejection (step 13.2). | `safe zone state changed -> false` or no `entered base zone` line for the army checkpoint visit. |
| 13.5 | Reload as a different faction (use MCM or a save where you play as Army). Enter the Army Checkpoint. | Toast fires. Confirms faction check is symmetric. |

**Note:** changing faction mid-game (via `set_actor_true_community`) should take effect
immediately on the next `actor_on_update` poll cycle (within 5 seconds).

---

## Known limitations — not tested here

These are out of scope for the current implementation and tracked as known issues:

| Limitation | Reason not tested |
|------------|-------------------|
| Cross-level respawn (die on Level A, base on Level B) | Implemented but untested — requires playing through to a level transition |
| Limansk (`l10_limansk`) zone coordinates | Level name confirmed; coordinates for `limansk_radio` and `limansk_construction` are inferred and have not been verified in-game. |
| Late-game levels (Pripyat, Red Forest, Dead City, Limansk continuation) | No safe zone data; player would respawn at last known valid base from a different level |
| Autosave trigger verification | Tested via manual console command; full campfire/blowout autosave cycle not exercised |
