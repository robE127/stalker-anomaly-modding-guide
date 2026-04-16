# Callbacks Reference

Every callback registered in `axr_main.script` — the authoritative source. Signatures are taken directly from the source comments. Frequency counts are from analysis of 50 community mod repositories.

Register any callback with:
```lua
RegisterScriptCallback("callback_name", your_function)
```

Unregister in `on_game_end` (or when done):
```lua
UnregisterScriptCallback("callback_name", your_function)
```

**Req** column:

- *(blank)* — vanilla Anomaly, no extra dependencies
- **Exes** — requires the [modded exes](https://github.com/themrdemonized/xray-monolith) (dispatched from C++ hooks or modded-exes Lua; will never fire without them)

!!! note "Best-effort accuracy"
    **Exes** markings are based on author annotations in the game scripts and inspection of the modded exes source. Without access to a vanilla (pre-modded-exes) build to diff against, some markings may be incomplete or incorrect.

---

## Core game flow

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `actor_on_first_update` | | 187 | `(binder, ?)` | First simulation tick after loading. `db.actor` is guaranteed available. Use for one-time initialisation requiring the actor. |
| `actor_on_update` | | 147 | `(binder, ?)` | Every simulation tick while the actor is alive. Keep handlers fast — this runs every frame. |
| `actor_on_init` | | — | `(binder)` | Actor binder initialised. |
| `actor_on_reinit` | | — | `(binder)` | Actor binder re-initialised. |
| `actor_on_net_destroy` | | 29 | `(binder)` | Actor client-side object destroyed (level transition or death). |
| `on_game_load` | | 107 | `(binder)` | Save file fully loaded and deserialised. Fires after `load_state`. `db.actor` not yet available. |
| `on_before_level_changing` | | — | `()` | Player is about to transition to a new level. |
| `on_level_changing` | | — | `()` | Level transition in progress. |
| `save_state` | | 198 | `(m_data: table)` | Write your mod's persistent data into `m_data`. See [Save & Load State](../scripting/save-load.md). |
| `load_state` | | 181 | `(m_data: table)` | Restore your mod's persistent data from `m_data`. `db.actor` not available yet. |
| `on_pstor_save_all` | | — | `(game_object, ?)` | Per-object persistent storage save. |
| `on_pstor_load_all` | | — | `(game_object, ?)` | Per-object persistent storage load. |
| `se_actor_on_STATE_Write` | | — | `(server_object)` | Server-side actor state written. |
| `se_actor_on_STATE_Read` | | — | `(server_object)` | Server-side actor state read. |

---

## Input

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `on_key_press` | | 80 | `(key: number)` | A key was pressed. `key` is a `DIK_keys.*` constant. |
| `on_key_release` | | 64 | `(key: number)` | A key was released. |
| `on_key_hold` | | — | `(key: number)` | A key is being held. Fires repeatedly each tick while held. |
| `on_before_key_press` | **Exes** | 15 | `(key: number, bind: number, is_down: boolean, flags: table)` | Fires before `on_key_press`. Set `flags.ret_value = false` to suppress the keypress. |
| `on_before_key_release` | **Exes** | — | `(key: number, bind: number, is_down: boolean, flags: table)` | Fires before `on_key_release`. Set `flags.ret_value = false` to suppress. |
| `on_before_key_hold` | **Exes** | — | `(key: number, bind: number, is_down: boolean, flags: table)` | Fires before `on_key_hold`. Set `flags.ret_value = false` to suppress. |
| `on_console_execute` | | 20 | `(cmd: string, ...)` | A console command was executed. Additional arguments are the command parts. |
| `on_option_change` | | 121 | `()` | Player saved settings (MCM or engine options). Re-read your `ui_mcm.get` / `ui_options.get` values here. |
| `on_localization_change` | | 24 | `()` | Player changed language setting. Rebuild any cached translated strings. |
| `on_screen_resolution_changed` | | — | `()` | Screen resolution changed. Rebuild any UI that depends on screen dimensions. |
| `on_before_save_input` | | — | `(flags: table, number, string)` | Before a quicksave input. Set `flags.ret = true` to cancel. |
| `on_before_load_input` | | — | `(key: number, bind: number, flags: table)` | Before a quickload input. Set `flags.ret = true` to cancel. |

---

## Inventory & items

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `actor_on_item_take` | | 39 | `(obj: game_object)` | Player picked up an item. |
| `actor_on_item_take_from_box` | | — | `(item: game_object, box: game_object)` | Player took an item from a stash/box. |
| `actor_on_item_put_in_box` | | — | `(item: game_object, box: game_object)` | Player put an item into a stash/box. |
| `actor_on_item_drop` | | 34 | `(obj: game_object)` | Player dropped an item. |
| `actor_on_item_use` | | 58 | `(obj: game_object, section: string)` | Player used a consumable. `obj` is the item, `section` is its LTX section name. |
| `actor_on_item_before_use` | **Exes** | — | `(obj: game_object, flags: table)` | Before item use. Set `flags.ret_value = false` to cancel. |
| `actor_on_item_before_pickup` | **Exes** | — | `(obj: game_object, flags: table)` | Before picking up an item. Set `flags.ret_value = false` to cancel pickup. |
| `actor_item_to_belt` | | — | `(obj: game_object)` | Item moved to belt. |
| `actor_item_to_ruck` | | 27 | `(obj: game_object)` | Item moved to backpack. |
| `actor_item_to_slot` | | 25 | `(obj: game_object)` | Item moved to equipment slot. |
| `actor_on_trade` | | — | `(obj: game_object, sell: boolean, cost: number)` | Trade transaction completed. |

---

## Combat & damage

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `actor_on_before_hit` | **Exes** | 32 | `(shit: SHit, bone_id: number, flags: table)` | Actor is about to take damage. Modify `shit.power` to change damage. Set `flags.ret_value = false` to cancel the hit entirely. |
| `actor_on_hit_callback` | | — | `(obj: game_object, amount: number, direction: vector, attacker: game_object, bone_id: number)` | Actor took damage (after the hit resolved). |
| `actor_on_before_death` | **Exes** | 29 | `(who_id: number, flags: table)` | Actor is about to die. Set `flags.ret_value = false` to prevent death. |
| `actor_on_feeling_anomaly` | | — | `(anomaly: game_object, flags: table)` | Actor entered an anomaly field. |

---

## Weapons

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `actor_on_weapon_fired` | **Exes** | 22 | `(obj: game_object, wpn: game_object, ammo_elapsed: number, grenade: number, bone_id: number, direction: number)` | Player fired a weapon. |
| `actor_on_weapon_before_fire` | **Exes** | — | `(flags: table)` | Before a shot is fired. Set `flags.ret_value = false` to cancel. |
| `actor_on_weapon_jammed` | **Exes** | — | `(wpn: game_object)` | Weapon jammed. |
| `actor_on_weapon_no_ammo` | | — | `(wpn: game_object, ammo_type: number)` | Out of ammo. |
| `actor_on_weapon_reload` | | — | `(wpn: game_object, ammo_elapsed: number)` | Weapon reloaded. |
| `actor_on_weapon_lower` | **Exes** | — | `(wpn: game_object)` | Weapon lowered. |
| `actor_on_weapon_raise` | **Exes** | — | `(wpn: game_object)` | Weapon raised. |
| `actor_on_weapon_zoom_in` | | 23 | `(wpn: game_object)` | Aimed down sights. |
| `actor_on_weapon_zoom_out` | | 20 | `(wpn: game_object)` | Stopped aiming. |
| `actor_on_before_throwable_select` | **Exes** | — | `(t: table)` | Before the engine selects the next throwable (grenade/bolt). `t.item` is the selected `game_object`; replace it to override the selection. |
| `actor_on_hud_animation_play` | | — | `(anm_table: table, obj: game_object)` | HUD animation started. |
| `actor_on_hud_animation_end` | **Exes** | — | `(obj: game_object, name: string, ?, ?, num: number)` | HUD animation finished. |
| `actor_on_hud_animation_mark` | | — | `(mark: number, name: string)` | Animation mark reached (sync point in animation). |

---

## Movement & interaction

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `actor_on_sleep` | | 22 | `(hours: number)` | Player slept. `hours` is how long they slept. |
| `actor_on_foot_step` | **Exes** | — | `(obj: game_object, surface: number, ?, ?, ?)` | Footstep sound played. |
| `actor_on_footstep` | | — | `(surface: string, power: number, is_crouching: boolean, flags: table)` | Footstep event (newer version). |
| `actor_on_jump` | | — | `()` | Player jumped. |
| `actor_on_land` | | — | `(fall_speed: number)` | Player landed. |
| `actor_on_movement_changed` | | — | `(move_type: number)` | Player movement type changed (walking/running/crouching). |
| `actor_on_interaction` | | — | `(interaction_type: string, obj: game_object, section: string)` | Player interacted with something. |
| `actor_on_attach_vehicle` | | — | `(vehicle: game_object)` | Player entered a vehicle. |
| `actor_on_detach_vehicle` | | — | `(vehicle: game_object)` | Player exited a vehicle. |
| `actor_on_use_vehicle` | | — | `(vehicle: game_object)` | Player used a vehicle. |
| `actor_on_leave_dialog` | | — | `(dialog_id: number)` | Player exited a dialog. |
| `actor_on_stash_create` | | — | `(stash_data: table)` | A stash was created. |
| `actor_on_stash_remove` | | — | `(stash_data: table)` | A stash was removed. |
| `actor_on_frequency_change` | | — | `(old_freq: number, new_freq: number)` | Radio frequency changed. |
| `actor_on_achievement_earned` | | — | `(id: string, name: string)` | Achievement unlocked. |
| `actor_on_info_callback` | | — | `(obj: game_object, info_id: number)` | An info portion was received. |

---

## NPCs

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `npc_on_death_callback` | | 41 | `(victim: game_object, who: game_object)` | An NPC was killed. `who` may be `nil` if killed by environment. |
| `npc_on_before_hit` | **Exes** | 23 | `(npc: game_object, shit: SHit, bone_id: number, flags: table)` | NPC is about to be hit. Modify `shit.power` to change damage. Set `flags.ret_value = false` to cancel. |
| `npc_on_hit_callback` | | — | `(npc: game_object, amount: number, direction: vector, attacker: game_object, bone_id: number)` | NPC took damage. |
| `npc_on_net_spawn` | | — | `(npc: game_object, server_object)` | NPC entered the online zone (loaded into the scene). |
| `npc_on_net_destroy` | | — | `(npc: game_object)` | NPC left the online zone. |
| `npc_on_update` | | — | `(npc: game_object, state: table)` | NPC update tick. Expensive — avoid registering this for many NPCs. |
| `npc_on_use` | | — | `(npc: game_object, who: game_object)` | Player used/talked to an NPC. |
| `npc_on_item_take` | | — | `(npc: game_object, item: game_object)` | NPC picked up an item. |
| `npc_on_item_take_from_box` | | — | `(npc: game_object, item: game_object, box: game_object)` | NPC took from a box. |
| `npc_on_item_drop` | | — | `(npc: game_object, item: game_object)` | NPC dropped an item. |
| `npc_on_fighting_actor` | | — | `(npc: game_object)` | NPC became hostile to the player. |
| `npc_on_weapon_strapped` | | — | `(npc: game_object, wpn: game_object)` | NPC strapped a weapon. |
| `npc_on_weapon_unstrapped` | | — | `(npc: game_object, wpn: game_object)` | NPC unstrapped a weapon. |
| `npc_on_weapon_drop` | | — | `(npc: game_object, wpn: game_object)` | NPC dropped a weapon. |
| `npc_on_hear_callback` | | — | `(npc: game_object, who_id: number, ?, power: number, ?, position: vector)` | NPC heard a sound. |
| `npc_on_get_all_from_corpse` | | — | `(npc: game_object, corpse: game_object, item: game_object, is_all: boolean)` | NPC looted a corpse. |
| `npc_on_eval_danger` | | — | `(npc: game_object, flags: table)` | NPC evaluating danger level. |
| `npc_on_choose_weapon` | | — | `(npc: game_object, best_weapon: game_object, flags: table)` | NPC choosing which weapon to use. |
| `npc_shot_dispersion` | **Exes** | — | `(npc: game_object, wpn: game_object, body_state: number, move_type: number, t: table)` | NPC weapon accuracy calculation. Modify `t.dispersion` to change the shot spread. |
| `se_stalker_on_spawn` | | — | `(server_object)` | Stalker server entity spawned. |

---

## Monsters

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `monster_on_death_callback` | | — | `(victim: game_object, who: game_object)` | A monster was killed. |
| `monster_on_before_hit` | **Exes** | — | `(monster: game_object, shit: SHit, bone_id: number, flags: table)` | Monster about to take damage. Set `flags.ret_value = false` to cancel. |
| `monster_on_hit_callback` | | — | `(monster: game_object, amount: number, direction: vector, attacker: game_object, bone_id: number)` | Monster took damage. |
| `monster_on_net_spawn` | | — | `(monster: game_object, server_object)` | Monster loaded into scene. |
| `monster_on_net_destroy` | | — | `(monster: game_object)` | Monster unloaded. |
| `monster_on_update` | | — | `(monster: game_object, state: table)` | Monster update tick. |
| `monster_on_actor_use_callback` | | — | `(monster: game_object, who: game_object)` | Player interacted with a monster. |
| `monster_on_loot_init` | | — | `(monster: game_object, loot_table: table)` | Monster loot table being built. Modify the table to change drops. |
| `burer_on_before_weapon_drop` | | — | `(burer: game_object, wpn: game_object)` | Burer (telekinetic mutant) about to throw a weapon. |
| `anomaly_on_before_activate` | | — | `(anomaly: game_object, activator: game_object)` | Anomaly about to activate. |

---

## Squads & simulation

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `squad_on_npc_creation` | | — | `(squad: server_object, npc: server_object, smart: server_object)` | NPC added to a squad at creation. |
| `squad_on_npc_death` | | — | `(squad: server_object, npc: server_object, killer: server_object)` | NPC in squad died. |
| `squad_on_add_npc` | | — | `(squad: server_object, npc: server_object, section: string, pos: vector, lv_id: number, gv_id: number)` | NPC added to squad. |
| `squad_on_enter_smart` | | — | `(squad: server_object, smart: server_object)` | Squad entered a smart terrain. |
| `squad_on_leave_smart` | | — | `(squad: server_object, smart: server_object)` | Squad left a smart terrain. |
| `squad_on_update` | | — | `(squad: server_object)` | Squad simulation tick. |
| `squad_on_first_update` | | — | `(squad: server_object)` | First simulation tick for a squad. |
| `squad_on_after_game_vertex_change` | | — | `(squad: server_object, old_gv: number, new_gv: number, changed: boolean)` | Squad moved to a new game vertex. |
| `squad_on_after_level_change` | | — | `(squad: server_object, old_level: string, new_level: string)` | Squad moved to a different level. |
| `smart_terrain_on_update` | | — | `(smart: server_object)` | Smart terrain simulation tick. |
| `on_try_respawn` | | — | `(smart: server_object, flags: table)` | Smart terrain about to respawn a squad. Set `flags.disabled = true` to cancel. |
| `server_entity_on_register` | | — | `(obj: server_object, type: string)` | Any entity added to A-Life simulation. |
| `server_entity_on_unregister` | | 32 | `(obj: server_object, type: string)` | Any entity removed from A-Life simulation. |
| `fill_start_position` | | — | `()` | New game start positions are being filled. |

---

## UI & inventory screens

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `GUI_on_show` | | 31 | `(name: string, path: string)` | A UI window opened. `name` is the Lua class name, `path` is the XML source path. |
| `GUI_on_hide` | | 23 | `(name: string, path: string)` | A UI window closed. |
| `ActorMenu_on_mode_changed` | | — | `(old_mode: number, new_mode: number)` | Inventory screen tab changed. |
| `ActorMenu_on_before_init_mode` | | — | `(mode: string, flags: table, item: game_object)` | Before inventory mode initialised. |
| `ActorMenu_on_item_drag_drop` | | 26 | `(item: game_object, from: game_object, from_slot: number, to_slot: number)` | Item dragged and dropped in inventory. |
| `ActorMenu_on_item_focus_receive` | | 20 | `(item: game_object)` | Mouse hovered over an inventory item. |
| `ActorMenu_on_item_focus_lost` | | — | `(item: game_object)` | Mouse left an inventory item. |
| `ActorMenu_on_item_before_move` | | — | `(flags: table, mode: number, item: game_object, to: string, ?, slot: number)` | Before item moved in inventory. Set flag to cancel. |
| `ActorMenu_on_item_after_move` | | — | `(mode: number, item: game_object, to: string, ?, slot: number)` | After item moved in inventory. |
| `ActorMenu_on_trade_started` | | — | `()` | Trade window opened. |
| `ActorMenu_on_trade_closed` | | — | `()` | Trade window closed. |
| `map_spot_menu_add_property` | | — | `(wnd: CUIWindow, obj_id: number, section: string, ?)` | Map spot right-click menu being built. Add custom options here. |
| `map_spot_menu_property_clicked` | | — | `(wnd: CUIWindow, obj_id: number, section: string, ?)` | Map spot menu option was clicked. |

---

## Main menu

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `main_menu_on_init` | | — | `(wnd: CUIScriptWnd)` | Main menu initialised. |
| `main_menu_on_quit` | | — | `(wnd: CUIScriptWnd)` | Player clicked quit from main menu. |
| `main_menu_on_keyboard` | | — | `(key: number, action: number, wnd: CUIScriptWnd, is_down: boolean)` | Key pressed while main menu is open. |

---

## Physics, vehicles & misc

| Callback | Req | Freq | Params | Description |
|----------|-----|------|--------|-------------|
| `physic_object_on_hit_callback` | | — | `(obj: game_object, amount: number, direction: vector, attacker: game_object, bone_id: number)` | A physics object (barrel, crate, etc.) was hit. |
| `physic_object_on_use_callback` | | — | `(obj: game_object, who: game_object)` | A physics object was used/interacted with. |
| `heli_on_hit_callback` | | — | `(heli: game_object, amount: number, nil, attacker: game_object, nil)` | Helicopter was hit. |
| `vehicle_on_death_callback` | | — | `(id: number)` | Vehicle was destroyed. |
| `on_before_surge` | | — | `(flags: table)` | Emission/surge about to start. Set `flags.allow = false` to cancel. |
| `on_before_psi_storm` | | — | `(flags: table)` | Psi storm about to start. Set `flags.allow = false` to cancel. |
| `bullet_on_hit` | **Exes** | — | `(section: string, obj: game_object, pos: vector, dir: vector, material: string, speed: number, wpn_id: number)` | A bullet hit something. `section` is the ammo section, `obj` is the hit object, `wpn_id` is the weapon's object ID. |
| `on_enemy_eval` | | — | `(npc: game_object, enemy: game_object, flags: table)` | NPC evaluating whether an entity is an enemy. |
| `on_get_item_cost` | | — | See `utils_item.script` | Item cost being calculated for trading. |
| `on_xml_read` | **Exes** | 36 | `(path: string, xml_obj: CScriptXmlInit)` | Engine reading an XML file. Used for DXML patching. See [DXML](../config-formats/dxml.md). |
