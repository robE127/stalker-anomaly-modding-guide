# API Reference

The X-Ray engine exposes a set of global objects and functions to Lua scripts. This page is an index of everything documented here, with frequency counts from analysis of 50 community mod repositories.

!!! tip "How to read this reference"
    Function signatures use the format `object:method(param: type) -> return_type`.
    Parameters in `[brackets]` are optional. Frequency counts show how many repos in the analysis used a given call — use this as a rough guide to what's important to learn first.

---

## Most-used calls at a glance

The 25 highest-frequency API calls across 50 analysed mods:

| Call | Freq | Page |
|------|-----:|------|
| `game.translate_string(key)` | 3351 | [game](game.md) |
| `db.actor:object(section)` | 861 | [db.actor](actor.md) |
| `level.object_by_id(id)` | 768 | [level](level.md) |
| `game.get_game_time()` | 629 | [game](game.md) |
| `ui_options.get(group, key)` | 549 | [UI](ui.md) |
| `db.actor:position()` | 489 | [db.actor](actor.md) |
| `db.actor:item_in_slot(slot_id)` | 441 | [db.actor](actor.md) |
| `db.actor:iterate_inventory(fn, data)` | 412 | [db.actor](actor.md) |
| `level.name()` | 404 | [level](level.md) |
| `db.actor:give_info_portion(info_id)` | 387 | [db.actor](actor.md) |
| `ui_mcm.get(mod, key)` | 323 | [UI](ui.md) |
| `xr_logic.pick_section_from_condlist(obj, npc, cl)` | 317 | [xr_logic](xr-logic.md) |
| `db.actor:active_item()` | 263 | [db.actor](actor.md) |
| `level.add_cam_effector(...)` | 251 | [level](level.md) |
| `level.add_pp_effector(...)` | 230 | [level](level.md) |
| `db.actor:money()` | 211 | [db.actor](actor.md) |
| `db.actor:has_info(info_id)` | 195 | [db.actor](actor.md) |
| `level.get_time_hours()` | 152 | [level](level.md) |
| `level.remove_pp_effector(id)` | 136 | [level](level.md) |
| `xr_logic.parse_condlist(npc, sec, field, str)` | 133 | [xr_logic](xr-logic.md) |
| `level.map_remove_object_spot(id, type)` | 130 | [level](level.md) |
| `level.map_has_object_spot(id, type)` | 129 | [level](level.md) |
| `db.actor:give_game_news(icon, text, tex, delay, time)` | 123 | [db.actor](actor.md) |
| `db.actor:activate_slot(slot_id)` | 114 | [db.actor](actor.md) |
| `db.actor:disable_info_portion(info_id)` | 111 | [db.actor](actor.md) |

---

## db.actor

The player character's `game_object`. Available from `actor_on_first_update` onward.

**Full reference: [db.actor](actor.md)**

| Method | Description |
|--------|-------------|
| `db.actor:activate_slot(slot_id)` | Switch active slot |
| `db.actor:active_detector()` | Currently active detector *(modded exes)* |
| `db.actor:active_item()` | Currently held item |
| `db.actor:active_slot()` | Active slot index |
| `db.actor:alive()` | Returns `true` if the actor is alive |
| `db.actor:allow_break_talk_dialog(bool)` | Allow/prevent player ending dialog |
| `db.actor:belt_count()` | Number of items on the belt |
| `db.actor:bone_position(bone_name)` | World position of a named bone |
| `db.actor:change_bleeding(delta)` | Modify bleeding rate by delta |
| `db.actor:change_health(delta)` | Modify health by delta |
| `db.actor:change_morale(delta)` | Modify morale by delta |
| `db.actor:change_power(delta)` | Modify stamina by delta |
| `db.actor:change_psy_health(delta)` | Modify psychic health by delta |
| `db.actor:change_radiation(delta)` | Modify radiation by delta |
| `db.actor:change_satiety(delta)` | Modify satiety by delta |
| `db.actor:character_community()` | Faction string (always `"actor"`) |
| `db.actor:character_icon()` | Current portrait icon name |
| `db.actor:character_name()` | Display name |
| `db.actor:character_rank()` | Current rank value |
| `db.actor:character_reputation()` | Current reputation (-4000 to 4000) |
| `db.actor:community_goodwill(faction)` | Goodwill with a faction (-10000 to 10000) |
| `db.actor:direction()` | Facing direction in radians |
| `db.actor:disable_info_portion(info_id)` | Unset a quest flag |
| `db.actor:dont_has_info(info_id)` | True if flag is NOT set |
| `db.actor:drop_item(item)` | Drop item to the ground |
| `db.actor:drop_item_and_teleport(item, pos)` | Drop item and teleport it to pos |
| `db.actor:eat(item)` | Consume a food/medkit item |
| `db.actor:force_hide_detector()` | Force-hide detector (during animations) *(modded exes)* |
| `db.actor:game_vertex_id()` | Global navigation graph node |
| `db.actor:get_actor_jump_speed()` | Jump power *(modded exes)* |
| `db.actor:get_actor_max_walk_weight()` | Weight limit for normal movement |
| `db.actor:get_actor_max_weight()` | Absolute max carry weight |
| `db.actor:get_actor_run_coef()` | Run speed multiplier *(modded exes)* |
| `db.actor:get_actor_runback_coef()` | Backwards run multiplier *(modded exes)* |
| `db.actor:get_actor_sprint_koef()` | Sprint speed multiplier *(modded exes)* |
| `db.actor:get_bone_id(bone_name)` | Numeric ID for a named bone |
| `db.actor:get_current_outfit()` | Equipped outfit `game_object` or `nil` |
| `db.actor:get_current_outfit_protection(type)` | Protection for hit type *(modded exes)* |
| `db.actor:get_inv_max_weight()` | Maximum backpack capacity |
| `db.actor:get_inv_weight()` | Backpack weight only |
| `db.actor:get_luminocity()` | Direct illumination (0–1) *(modded exes)* |
| `db.actor:get_luminocity_hemi()` | Ambient illumination (0–1) *(modded exes)* |
| `db.actor:get_script()` | True if under script control |
| `db.actor:get_total_weight()` | Total carry weight *(modded exes)* |
| `db.actor:give_game_news(title, body, tex, delay, dur)` | HUD news notification |
| `db.actor:give_info_portion(info_id)` | Set a quest flag |
| `db.actor:give_money(amount)` | Add (or remove if negative) RU |
| `db.actor:give_talk_message2(npc_id, dialog_id, ...)` | Show a talk message from NPC |
| `db.actor:has_info(info_id)` | Check a quest flag |
| `db.actor:hide_detector()` | Hide detector HUD *(modded exes)* |
| `db.actor:hide_weapon()` | Holster current weapon |
| `db.actor:hit(hit_obj)` | Apply a `hit` to the actor |
| `db.actor:id()` | Alife ID |
| `db.actor:inventory_for_each(fn)` | Iterate all items; `fn(item)` |
| `db.actor:invulnerable()` | Get invulnerability state |
| `db.actor:invulnerable(bool)` | Set invulnerability state |
| `db.actor:is_on_belt(item)` | True if item is on the belt |
| `db.actor:is_talking()` | True if dialog is open |
| `db.actor:item_in_slot(slot_id)` | Item equipped in given slot; `nil` if empty |
| `db.actor:item_on_belt(index)` | Belt item at index (0-based) |
| `db.actor:iterate_belt(fn, data)` | Iterate belt items only |
| `db.actor:iterate_inventory(fn, data)` | Iterate all items; `fn(data, item)` |
| `db.actor:iterate_ruck(fn, data)` | Iterate backpack items only |
| `db.actor:level_vertex_id()` | Local navmesh node |
| `db.actor:make_item_active(item)` | Force item into active slot |
| `db.actor:mark_item_dropped(item)` | Mark item as intentionally dropped *(modded exes)* |
| `db.actor:money()` | Current RU balance |
| `db.actor:move_to_belt(item)` | Move item to belt |
| `db.actor:move_to_ruck(item)` | Move item to backpack |
| `db.actor:move_to_slot(item, slot_id)` | Move item to a specific equip slot |
| `db.actor:name()` | Returns `"actor"` |
| `db.actor:object(section)` | First inventory item matching section; `nil` if none |
| `db.actor:object(id)` | Inventory item with given alife ID; `nil` if not held |
| `db.actor:position()` | World position (`vector`) |
| `db.actor:reload_weapon()` | Trigger a weapon reload |
| `db.actor:restore_weapon()` | Re-equip previously active weapon |
| `db.actor:run_talk_dialog(npc, bool)` | Force-start dialog with NPC |
| `db.actor:script(bool, name)` | Take/release scripted control |
| `db.actor:section()` | Character section name |
| `db.actor:see(obj)` | True if actor has line-of-sight to obj |
| `db.actor:set_actor_direction(angle)` | Set facing direction (radians) |
| `db.actor:set_actor_jump_speed(v)` | Set jump power *(modded exes)* |
| `db.actor:set_actor_max_walk_weight(v)` | Override walk weight limit |
| `db.actor:set_actor_max_weight(v)` | Override absolute max weight |
| `db.actor:set_actor_position(pos)` | Teleport actor to position |
| `db.actor:set_actor_run_coef(v)` | Set run speed multiplier *(modded exes)* |
| `db.actor:set_actor_runback_coef(v)` | Set backwards run multiplier *(modded exes)* |
| `db.actor:set_actor_sprint_koef(v)` | Set sprint multiplier *(modded exes)* |
| `db.actor:set_community_goodwill(faction, val)` | Set faction goodwill |
| `db.actor:set_health_ex(value)` | Set health to exact value *(modded exes)* |
| `db.actor:set_sight(...)` | Override sight target |
| `db.actor:show_detector()` | Show detector HUD *(modded exes)* |
| `db.actor:sight_params()` | Returns current `CSightParams` |
| `db.actor:start_particles(effect, bone)` | Attach particle effect to bone |
| `db.actor:stop_particles(effect, bone)` | Remove attached particle effect |
| `db.actor:stop_talk()` | End current dialog |
| `db.actor:transfer_item(item, to_obj)` | Move item to another object's inventory |
| `db.actor:transfer_money(amount, npc)` | Transfer RU to an NPC |
| `db.actor:weapon_strapped()` | True if weapon is holstered |
| `db.actor:weapon_unstrapped()` | True if weapon is drawn |

---

## level

The current map — object lookup, time, weather, effects, minimap.

**Full reference: [level](level.md)**

| Method | Description |
|--------|-------------|
| `level.actor_moving_state()` | Current actor movement state number |
| `level.add_call(check_fn, action_fn)` | Register a deferred one-shot callback |
| `level.add_cam_effector(anm, id, cyclic, cb)` | Play camera animation |
| `level.add_complex_effector(name, id)` | Start a named complex camera effector |
| `level.add_pp_effector(name, id, cyclic)` | Apply post-process effect |
| `level.change_game_time(days, hours, mins)` | Advance game time by delta |
| `level.client_spawn_manager()` | Client spawn manager object |
| `level.debug_object(name)` | Find object by name (debug/editor use) |
| `level.disable_input()` | Block player input |
| `level.enable_input()` | Restore player input |
| `level.environment()` | Current environment manager object |
| `level.game_id()` | Internal game ID |
| `level.get_bounding_volume()` | Level bounding box (`Fbox`) |
| `level.get_env_rads()` | Environmental radiation (HUD sensor value) |
| `level.get_game_difficulty()` | Difficulty constant (0=novice … 3=master) |
| `level.get_rain_volume()` | Rain audio volume (0–1) |
| `level.get_snd_volume()` | Master sound volume (0–1) |
| `level.get_start_time()` | `CTime` when the current level load began |
| `level.get_target_dist()` | Distance to crosshair target |
| `level.get_target_element()` | Bone ID under the crosshair |
| `level.get_target_obj()` | Object the crosshair is aimed at |
| `level.get_time_days()` | Current in-game day number |
| `level.get_time_factor()` | Time acceleration multiplier |
| `level.get_time_hours()` | Current game hour (0–23) |
| `level.get_time_minutes()` | Current game minutes (0–59) |
| `level.get_weather()` | Current weather name string |
| `level.get_wfx_time()` | Elapsed time of current weather effect |
| `level.hide_indicators()` | Hide HUD indicators |
| `level.hide_indicators_safe()` | Safe hide (won't crash before HUD ready) |
| `level.high_cover_in_direction(lvid, dir)` | High-cover score in direction |
| `level.hold_action(key_bind)` | Simulate key hold |
| `level.is_wfx_playing()` | True while a weather effect is running |
| `level.iterate_nearest(pos, radius, fn)` | Call `fn(obj)` for each online object within radius |
| `level.iterate_sounds(path, radius, fn)` | Iterate sounds at a path within radius |
| `level.low_cover_in_direction(lvid, dir)` | Low-cover score in direction |
| `level.map_add_object_spot(id, type, hint)` | Add minimap marker |
| `level.map_add_object_spot_ser(id, type, hint)` | Add minimap marker (serialised) |
| `level.map_change_spot_hint(id, type, hint)` | Update marker tooltip |
| `level.map_has_object_spot(id, type)` | Check for minimap marker |
| `level.map_remove_object_spot(id, type)` | Remove minimap marker |
| `level.name()` | Internal level name string (e.g. `"l01_escape"`) |
| `level.object_by_id(id)` | Game object by alife ID; `nil` if offline |
| `level.patrol_path_exists(name)` | Check if a patrol path exists |
| `level.physics_world()` | Physics world object |
| `level.prefetch_sound(path)` | Preload a sound file |
| `level.present()` | Returns `true` if a level is loaded |
| `level.press_action(key_bind)` | Simulate key press |
| `level.rain_factor()` | Current rain intensity (0–1) |
| `level.release_action(key_bind)` | Simulate key release |
| `level.remove_call(check_fn, action_fn)` | Unregister a deferred callback |
| `level.remove_calls_for_object(obj)` | Remove all deferred calls for an object |
| `level.remove_cam_effector(id)` | Stop camera animation |
| `level.remove_complex_effector(id)` | Stop complex effector |
| `level.remove_pp_effector(id)` | Remove post-process effect |
| `level.set_game_difficulty(enum_val)` | Change difficulty |
| `level.set_pp_effector_factor(id, factor)` | Blend post-process intensity |
| `level.set_snd_volume(v)` | Set master sound volume |
| `level.set_time_factor(n)` | Set time acceleration multiplier |
| `level.set_weather(name, immediate)` | Change weather |
| `level.set_weather_fx(name)` | Start a weather effect (psi storm etc.) |
| `level.show_indicators()` | Show HUD indicators |
| `level.show_weapon(bool)` | Toggle weapon render |
| `level.spawn_item(sec, pos, lvid, gvid)` | Spawn a client-side object (not tracked by alife) |
| `level.spawn_phantom(pos)` | Spawn a phantom entity |
| `level.start_weather_fx_from_time(name, t)` | Start weather effect at a given elapsed time |
| `level.stop_weather_fx()` | Stop active weather effect |
| `level.vertex_id(pos)` | Nearest navmesh vertex to a world position |
| `level.vertex_in_direction(lvid, dir, dist)` | Navmesh vertex in a direction |
| `level.vertex_position(lvid)` | World position of a navmesh vertex |

---

## game

Game-wide utilities — localisation, time, HUD animations.

**Full reference: [game](game.md)**

| Method | Description |
|--------|-------------|
| `game.actor_lower_weapon()` | Lower weapon to safe position |
| `game.actor_weapon_lowered()` | True if weapon is currently lowered |
| `game.change_game_news_show_time(ms)` | Override news notification display duration |
| `game.get_actor_alcohol()` | Actor's current alcohol level (0–1) |
| `game.get_game_time()` | Returns `CTime` for current in-game time |
| `game.get_motion_length(sec, name, speed)` | Total duration of an animation in seconds |
| `game.get_resolutions()` | String of all supported display resolutions |
| `game.has_active_tutorial()` | True if a tutorial is currently displayed |
| `game.hud_motion_allowed()` | True if HUD motion system is active |
| `game.only_allow_movekeys(bool)` | Restrict input to movement keys |
| `game.only_movekeys_allowed()` | Query movement-keys-only state |
| `game.play_hud_anm(name, part, speed, power, loop, no_restart)` | Play a blended HUD animation |
| `game.play_hud_motion(hand, sec, anim, loop, speed)` | Play a hand/motion animation |
| `game.prefetch_model(path)` | Preload a model without extension |
| `game.prefetch_texture(path)` | Preload a texture with extension |
| `game.reload_language()` | Reload all language XML files |
| `game.reload_ui_xml()` | Clear XML cache and reload all HUD XML |
| `game.set_actor_allow_ladder(bool)` | Toggle ladder climbing |
| `game.set_hud_anm_time(name, t)` | Set playback time; returns current time |
| `game.set_nv_lumfactor(v)` | Adjust night vision luminance factor |
| `game.start_tutorial(name)` | Show a named tutorial |
| `game.stop_all_hud_anms(force)` | Stop all active HUD animations |
| `game.stop_hud_anm(name, force)` | Stop a named HUD animation |
| `game.stop_hud_motion()` | Stop current hand animation |
| `game.stop_tutorial()` | Stop the active tutorial |
| `game.time()` | Raw game time as ms since epoch |
| `game.translate_string(key)` | Look up a localisation string by key |
| `game.world2ui(pos)` | Convert world position to UI screen coordinates |

---

## alife()

The A-Life simulation — server-side entity management.

**Full reference: [alife](alife.md)**

Prefer the `_g.script` wrappers below over calling `alife()` directly.

### Global helpers (`_g.script`)

| Function | Description |
|----------|-------------|
| `alife_create(section, pos, lid, gid, [parent_id])` | Spawn any entity in the world |
| `alife_create_item(section, recipient, [props])` | Spawn an item directly into an inventory |
| `alife_object(id)` | Server entity by ID; `nil` if not found |
| `alife_release(se_or_game_obj, [reason])` | Destroy an entity permanently |
| `alife_release_id(id, [reason])` | Destroy by alife ID |
| `disable_info(info_id)` | Unset an actor quest flag |
| `get_object_story_id(obj_id)` | Reverse lookup: ID → story_id string |
| `get_story_object(story_id)` | Game object for a named entity (nil if offline) |
| `get_story_object_id(story_id)` | Numeric alife ID for a named entity |
| `get_story_se_object(story_id)` | Server entity for a named entity |
| `get_story_squad(story_id)` | Squad server object for a named squad |
| `give_info(info_id)` | Set an actor quest flag |
| `has_alife_info(info_id)` | Check actor quest flag via alife simulator |

### Raw alife() methods

| Method | Description |
|--------|-------------|
| `alife():actor()` | Server-side actor entity |
| `alife():add_in_restriction(se_obj, restr_id)` | Add in-restriction to NPC/monster |
| `alife():add_out_restriction(se_obj, restr_id)` | Add out-restriction to NPC/monster |
| `alife():create(sec, pos, lvid, gvid, [parent])` | Spawn entity |
| `alife():create_ammo(sec, pos, lvid, gvid, parent, count)` | Spawn an ammo stack |
| `alife():disable_info(entity_id, info_id)` | Remove info portion from any entity |
| `alife():dont_has_info(entity_id, info_id)` | True if entity does NOT have the info |
| `alife():get_children(se_obj)` | Iterator over child entities (inventory) |
| `alife():give_info(entity_id, info_id)` | Give info portion to any entity |
| `alife():has_info(entity_id, info_id)` | Check quest flag on any entity |
| `alife():kill_entity(se_obj, [gvid])` | Mark entity as dead in simulation |
| `alife():level_id()` | Numeric ID of the level the actor is on |
| `alife():level_name(level_id)` | Level name string for a numeric level ID |
| `alife():object(id)` | Server entity by ID; `nil` if not found |
| `alife():release(se_obj, force)` | Destroy entity |
| `alife():remove_all_restrictions(id, type)` | Remove all restrictions of a type |
| `alife():remove_in_restriction(se_obj, restr_id)` | Remove in-restriction |
| `alife():remove_out_restriction(se_obj, restr_id)` | Remove out-restriction |
| `alife():set_interactive(id, bool)` | Toggle whether NPCs can interact with object |
| `alife():set_switch_offline(id, bool)` | Force offline transition |
| `alife():set_switch_online(id, bool)` | Force online transition |
| `alife():spawn_id(spawn_story_id)` | Spawn by spawn_story_id number |
| `alife():story_object(story_id)` | Server entity for a story ID |
| `alife():switch_distance()` | Get current spawn radius |
| `alife():switch_distance(n)` | Set spawn radius |
| `alife():teleport_object(id, gvid, lvid, pos)` | Move server entity to position |
| `alife():valid_object_id(id)` | True if ID is valid (not 65535 and exists) |

---

## xr_logic

Condition list evaluation and NPC logic schemes.

**Full reference: [xr_logic](xr-logic.md)**

| Function | Description |
|----------|-------------|
| `xr_logic.assign_storage_and_bind(obj, ini, scheme, sec)` | Bind a scheme to an object |
| `xr_logic.cfg_get_switch_conditions(ini, sec, obj)` | Read all `on_info` fields from an LTX section |
| `xr_logic.is_active(obj, action)` | Check if a scheme/action is active on an object |
| `xr_logic.issue_event(obj, st, event)` | Fire an event on a subscribed action |
| `xr_logic.mob_capture(obj, bool)` | Take/release scripted control of a creature |
| `xr_logic.parse_condlist(npc, sec, field, str)` | Parse a condition list string into a table |
| `xr_logic.pick_section_from_condlist(obj, npc, cl)` | Evaluate a parsed condlist; returns the matching section name or `nil` |
| `xr_logic.subscribe_action_for_events(obj, st, action)` | Register a scheme action for event callbacks |
| `xr_logic.switch_to_section(obj, ini, section)` | Force a section switch |
| `xr_logic.try_switch_to_another_section(obj, st, actor)` | Evaluate and execute any pending section switch |

---

## UI & settings

HUD messages, notifications, and settings access.

**Full reference: [UI Functions](ui.md)**

| Function | Description |
|----------|-------------|
| `ui_mcm.get(mod, key)` | Read an MCM setting value |
| `ui_options.get(group, key)` | Read a game option value |
| `ui_mcm.get_mod_key(mod, key)` | Get the MCM key path string |
| `news_manager.send_tip(actor, text, icon, delay, time, task)` | Queue a tip/notification |
| `ui_mcm.set(mod, key, value)` | Write an MCM setting value |
| `actor_menu.set_fade_msg(text, dur)` | Show a fading centre message |
| `actor_menu.set_msg(side, text, dur)` | Show a screen-edge HUD message |
| `actor_menu.set_notification(icon, header, body, sound, dur)` | Show a notification popup |

---

## Type-checking helpers (`_g.script`)

These functions wrap `clsid` comparisons for common object types:

| Function | Returns true if… |
|----------|-----------------|
| `get_clsid(obj)` | Returns `obj:clsid()` safely (nil-checks `obj`) |
| `IsArtefact(obj, [clsid])` | Object is an artefact |
| `IsBackpack(obj, [clsid])` | Object is a backpack |
| `IsFood(obj, [clsid])` | Object is a consumable |
| `IsMonster(obj, [clsid])` | Object is a mutant |
| `IsOutfit(obj, [clsid])` | Object is a suit/outfit |
| `IsStalker(obj, [clsid])` | Object is a human NPC or the actor |
| `IsWeapon(obj, [clsid])` | Object is any weapon |

---

## db namespace

| Name | Description |
|------|-------------|
| `db.actor` | The player's `game_object`. See [db.actor](actor.md). |
| `db.add_obj(game_obj)` | Register an online object in db.storage |
| `db.del_obj(game_obj)` | Remove an object from db.storage |
| `db.offline_objects` | Table of currently offline entity IDs |
| `db.smart_terrain_by_id` | Table mapping alife ID → smart terrain server entity |
| `db.storage` | Per-object state table, keyed by alife ID. See [db.storage](../scripting/db-storage.md). |

---

## Not yet documented

The following commonly used modules have partial or no documentation in this guide:

| Module | Description |
|--------|-------------|
| `axr_task_manager` | Quest task creation and management |
| `bind_stalker_ext` | Extended actor binder callbacks |
| `CScriptXmlInit` | UI XML loading and element initialisation |
| `particles_object` | Particle effect attachment |
| `sim_board` | Simulation board — squad/smart terrain matching |
| `sound_object` | Positional and attached sound playback |
| `story_objects` | story_id registration and lookup internals |

---

## See also

- [The Callback System](../scripting/callbacks.md) — how to register for engine events
- [What is a game_object?](../scripting/game-object.md) — the object all methods operate on
- [Callbacks Reference](../callbacks-reference/index.md) — full list of available callbacks
- [Glossary](../reference/glossary.md) — definitions of Anomaly-specific terms
