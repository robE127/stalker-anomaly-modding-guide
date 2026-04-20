# API Reference

The X-Ray engine exposes a set of global objects and functions to Lua scripts. This page is an index of everything documented here, with frequency counts from analysis of 50 community mod repositories.

!!! tip "How to read this reference"
    Function signatures use the format `object:method(param: type) -> return_type`.
    Parameters in `[brackets]` are optional. Frequency counts show how many repos in the analysis used a given call — use this as a rough guide to what's important to learn first.

**Req** column:

- *(blank)* — vanilla Anomaly, no extra dependencies
- **Exes** — requires the [modded exes](https://github.com/themrdemonized/xray-monolith); method does not exist without them

!!! note "Best-effort accuracy"
    **Exes** markings are based on author annotations in the game scripts and inspection of the modded exes source. Without access to a vanilla (pre-modded-exes) build to diff against, some markings may be incomplete or incorrect.

---

## Most-used calls at a glance

The 25 highest-frequency API calls across 50 analysed mods:

| Call | Req | Freq | Page |
|------|-----|-----:|------|
| `game.translate_string(key)` | | 3351 | [game](game.md) |
| `db.actor:object(section)` | | 861 | [db.actor](actor.md) |
| `level.object_by_id(id)` | | 768 | [level](level.md) |
| `game.get_game_time()` | | 629 | [game](game.md) |
| `ui_options.get(group, key)` | | 549 | [UI](ui.md) |
| `db.actor:position()` | | 489 | [db.actor](actor.md) |
| `db.actor:item_in_slot(slot_id)` | | 441 | [db.actor](actor.md) |
| `db.actor:iterate_inventory(fn, data)` | | 412 | [db.actor](actor.md) |
| `level.name()` | | 404 | [level](level.md) |
| `db.actor:give_info_portion(info_id)` | | 387 | [db.actor](actor.md) |
| `ui_mcm.get(mod, key)` | | 323 | [UI](ui.md) |
| `xr_logic.pick_section_from_condlist(obj, npc, cl)` | | 317 | [xr_logic](xr-logic.md) |
| `db.actor:active_item()` | | 263 | [db.actor](actor.md) |
| `level.add_cam_effector(...)` | | 251 | [level](level.md) |
| `level.add_pp_effector(...)` | | 230 | [level](level.md) |
| `db.actor:money()` | | 211 | [db.actor](actor.md) |
| `db.actor:has_info(info_id)` | | 195 | [db.actor](actor.md) |
| `level.get_time_hours()` | | 152 | [level](level.md) |
| `level.remove_pp_effector(id)` | | 136 | [level](level.md) |
| `xr_logic.parse_condlist(npc, sec, field, str)` | | 133 | [xr_logic](xr-logic.md) |
| `level.map_remove_object_spot(id, type)` | | 130 | [level](level.md) |
| `level.map_has_object_spot(id, type)` | | 129 | [level](level.md) |
| `db.actor:give_game_news(icon, text, tex, delay, time)` | | 123 | [db.actor](actor.md) |
| `db.actor:activate_slot(slot_id)` | | 114 | [db.actor](actor.md) |
| `db.actor:disable_info_portion(info_id)` | | 111 | [db.actor](actor.md) |

---

## db.actor

The player character's `game_object`. Available from `actor_on_first_update` onward.

**Full reference: [db.actor](actor.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `db.actor:activate_slot(slot_id)` | | Switch active slot |
| `db.actor:active_detector()` | **Exes** | Currently active detector |
| `db.actor:active_item()` | | Currently held item |
| `db.actor:active_slot()` | | Active slot index |
| `db.actor:alive()` | | Returns `true` if the actor is alive |
| `db.actor:allow_break_talk_dialog(bool)` | | Allow/prevent player ending dialog |
| `db.actor:belt_count()` | | Number of items on the belt |
| `db.actor:bone_position(bone_name)` | | World position of a named bone |
| `db.actor:change_bleeding(delta)` | | Modify bleeding rate by delta |
| `db.actor:change_health(delta)` | | Modify health by delta |
| `db.actor:change_morale(delta)` | | Modify morale by delta |
| `db.actor:change_power(delta)` | | Modify stamina by delta |
| `db.actor:change_psy_health(delta)` | | Modify psychic health by delta |
| `db.actor:change_radiation(delta)` | | Modify radiation by delta |
| `db.actor:change_satiety(delta)` | | Modify satiety by delta |
| `db.actor:character_community()` | | Faction string (always `"actor"`) |
| `db.actor:character_icon()` | | Current portrait icon name |
| `db.actor:character_name()` | | Display name |
| `db.actor:character_rank()` | | Current rank value |
| `db.actor:character_reputation()` | | Current reputation (-4000 to 4000) |
| `db.actor:community_goodwill(faction)` | | Goodwill with a faction (-10000 to 10000) |
| `db.actor:direction()` | | Facing direction in radians |
| `db.actor:disable_info_portion(info_id)` | | Unset a quest flag |
| `db.actor:dont_has_info(info_id)` | | True if flag is NOT set |
| `db.actor:drop_item(item)` | | Drop item to the ground |
| `db.actor:drop_item_and_teleport(item, pos)` | | Drop item and teleport it to pos |
| `db.actor:eat(item)` | | Consume a food/medkit item |
| `db.actor:force_hide_detector()` | **Exes** | Force-hide detector (during animations) |
| `db.actor:game_vertex_id()` | | Global navigation graph node |
| `db.actor:get_actor_jump_speed()` | **Exes** | Jump power |
| `db.actor:get_actor_max_walk_weight()` | | Weight limit for normal movement |
| `db.actor:get_actor_max_weight()` | | Absolute max carry weight |
| `db.actor:get_actor_run_coef()` | **Exes** | Run speed multiplier |
| `db.actor:get_actor_runback_coef()` | **Exes** | Backwards run multiplier |
| `db.actor:get_actor_sprint_koef()` | **Exes** | Sprint speed multiplier |
| `db.actor:get_bone_id(bone_name)` | | Numeric ID for a named bone |
| `db.actor:get_current_outfit()` | | Equipped outfit `game_object` or `nil` |
| `db.actor:get_current_outfit_protection(type)` | **Exes** | Protection for hit type |
| `db.actor:get_inv_max_weight()` | | Maximum backpack capacity |
| `db.actor:get_inv_weight()` | | Backpack weight only |
| `db.actor:get_luminocity()` | **Exes** | Direct illumination (0–1) |
| `db.actor:get_luminocity_hemi()` | **Exes** | Ambient illumination (0–1) |
| `db.actor:get_script()` | | True if under script control |
| `db.actor:get_total_weight()` | **Exes** | Total carry weight |
| `db.actor:give_game_news(title, body, tex, delay, dur)` | | HUD news notification |
| `db.actor:give_info_portion(info_id)` | | Set a quest flag |
| `db.actor:give_money(amount)` | | Add (or remove if negative) RU |
| `db.actor:give_talk_message2(npc_id, dialog_id, ...)` | | Show a talk message from NPC |
| `db.actor:has_info(info_id)` | | Check a quest flag |
| `db.actor:hide_detector()` | **Exes** | Hide detector HUD |
| `db.actor:hide_weapon()` | | Holster current weapon |
| `db.actor:hit(hit_obj)` | | Apply a `hit` to the actor |
| `db.actor:id()` | | Alife ID |
| `db.actor:inventory_for_each(fn)` | | Iterate all items; `fn(item)` |
| `db.actor:invulnerable()` | | Get invulnerability state |
| `db.actor:invulnerable(bool)` | | Set invulnerability state |
| `db.actor:is_on_belt(item)` | | True if item is on the belt |
| `db.actor:is_talking()` | | True if dialog is open |
| `db.actor:item_in_slot(slot_id)` | | Item equipped in given slot; `nil` if empty |
| `db.actor:item_on_belt(index)` | | Belt item at index (0-based) |
| `db.actor:iterate_belt(fn, data)` | | Iterate belt items only |
| `db.actor:iterate_inventory(fn, data)` | | Iterate all items; `fn(data, item)` |
| `db.actor:iterate_ruck(fn, data)` | | Iterate backpack items only |
| `db.actor:level_vertex_id()` | | Local navmesh node |
| `db.actor:make_item_active(item)` | | Force item into active slot |
| `db.actor:mark_item_dropped(item)` | **Exes** | Mark item as intentionally dropped |
| `db.actor:money()` | | Current RU balance |
| `db.actor:move_to_belt(item)` | | Move item to belt |
| `db.actor:move_to_ruck(item)` | | Move item to backpack |
| `db.actor:move_to_slot(item, slot_id)` | | Move item to a specific equip slot |
| `db.actor:name()` | | Returns `"actor"` |
| `db.actor:object(section)` | | First inventory item matching section; `nil` if none |
| `db.actor:object(id)` | | Inventory item with given alife ID; `nil` if not held |
| `db.actor:position()` | | World position (`vector`) |
| `db.actor:reload_weapon()` | | Trigger a weapon reload |
| `db.actor:restore_weapon()` | | Re-equip previously active weapon |
| `db.actor:run_talk_dialog(npc, bool)` | | Force-start dialog with NPC |
| `db.actor:script(bool, name)` | | Take/release scripted control |
| `db.actor:section()` | | Character section name |
| `db.actor:see(obj)` | | True if actor has line-of-sight to obj |
| `db.actor:set_actor_direction(angle)` | | Set facing direction (radians) |
| `db.actor:set_actor_jump_speed(v)` | **Exes** | Set jump power |
| `db.actor:set_actor_max_walk_weight(v)` | | Override walk weight limit |
| `db.actor:set_actor_max_weight(v)` | | Override absolute max weight |
| `db.actor:set_actor_position(pos)` | | Teleport actor to position |
| `db.actor:set_actor_run_coef(v)` | **Exes** | Set run speed multiplier |
| `db.actor:set_actor_runback_coef(v)` | **Exes** | Set backwards run multiplier |
| `db.actor:set_actor_sprint_koef(v)` | **Exes** | Set sprint multiplier |
| `db.actor:set_community_goodwill(faction, val)` | | Set faction goodwill |
| `db.actor:set_health_ex(value)` | **Exes** | Set health to exact value |
| `db.actor:set_sight(...)` | | Override sight target |
| `db.actor:show_detector()` | **Exes** | Show detector HUD |
| `db.actor:sight_params()` | | Returns current `CSightParams` |
| `db.actor:start_particles(effect, bone)` | | Attach particle effect to bone |
| `db.actor:stop_particles(effect, bone)` | | Remove attached particle effect |
| `db.actor:stop_talk()` | | End current dialog |
| `db.actor:transfer_item(item, to_obj)` | | Move item to another object's inventory |
| `db.actor:transfer_money(amount, npc)` | | Transfer RU to an NPC |
| `db.actor:weapon_strapped()` | | True if weapon is holstered |
| `db.actor:weapon_unstrapped()` | | True if weapon is drawn |

---

## level

The current map — object lookup, time, weather, effects, minimap.

**Full reference: [level](level.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `level.actor_moving_state()` | | Current actor movement state number |
| `level.add_call(check_fn, action_fn)` | | Register a deferred one-shot callback |
| `level.add_cam_effector(anm, id, cyclic, cb)` | | Play camera animation |
| `level.add_complex_effector(name, id)` | | Start a named complex camera effector |
| `level.add_pp_effector(name, id, cyclic)` | | Apply post-process effect |
| `level.change_game_time(days, hours, mins)` | | Advance game time by delta |
| `level.client_spawn_manager()` | | Client spawn manager object |
| `level.debug_object(name)` | | Find object by name (debug/editor use) |
| `level.disable_input()` | | Block player input |
| `level.enable_input()` | | Restore player input |
| `level.environment()` | | Current environment manager object |
| `level.game_id()` | | Internal game ID |
| `level.get_bounding_volume()` | | Level bounding box (`Fbox`) |
| `level.get_env_rads()` | | Environmental radiation (HUD sensor value) |
| `level.get_game_difficulty()` | | Difficulty constant (0=novice … 3=master) |
| `level.get_rain_volume()` | | Rain audio volume (0–1) |
| `level.get_snd_volume()` | | Master sound volume (0–1) |
| `level.get_start_time()` | | `CTime` when the current level load began |
| `level.get_target_dist()` | | Distance to crosshair target |
| `level.get_target_element()` | | Bone ID under the crosshair |
| `level.get_target_obj()` | | Object the crosshair is aimed at |
| `level.get_time_days()` | | Current in-game day number |
| `level.get_time_factor()` | | Time acceleration multiplier |
| `level.get_time_hours()` | | Current game hour (0–23) |
| `level.get_time_minutes()` | | Current game minutes (0–59) |
| `level.get_weather()` | | Current weather name string |
| `level.get_wfx_time()` | | Elapsed time of current weather effect |
| `level.hide_indicators()` | | Hide HUD indicators |
| `level.hide_indicators_safe()` | | Safe hide (won't crash before HUD ready) |
| `level.high_cover_in_direction(lvid, dir)` | | High-cover score in direction |
| `level.hold_action(key_bind)` | | Simulate key hold |
| `level.is_wfx_playing()` | | True while a weather effect is running |
| `level.iterate_nearest(pos, radius, fn)` | | Call `fn(obj)` for each online object within radius |
| `level.iterate_sounds(path, radius, fn)` | | Iterate sounds at a path within radius |
| `level.low_cover_in_direction(lvid, dir)` | | Low-cover score in direction |
| `level.map_add_object_spot(id, type, hint)` | | Add minimap marker |
| `level.map_add_object_spot_ser(id, type, hint)` | | Add minimap marker (serialised) |
| `level.map_change_spot_hint(id, type, hint)` | | Update marker tooltip |
| `level.map_has_object_spot(id, type)` | | Check for minimap marker |
| `level.map_remove_object_spot(id, type)` | | Remove minimap marker |
| `level.name()` | | Internal level name string (e.g. `"l01_escape"`) |
| `level.object_by_id(id)` | | Game object by alife ID; `nil` if offline |
| `level.patrol_path_exists(name)` | | Check if a patrol path exists |
| `level.physics_world()` | | Physics world object |
| `level.prefetch_sound(path)` | | Preload a sound file |
| `level.present()` | | Returns `true` if a level is loaded |
| `level.press_action(key_bind)` | | Simulate key press |
| `level.rain_factor()` | | Current rain intensity (0–1) |
| `level.release_action(key_bind)` | | Simulate key release |
| `level.remove_call(check_fn, action_fn)` | | Unregister a deferred callback |
| `level.remove_calls_for_object(obj)` | | Remove all deferred calls for an object |
| `level.remove_cam_effector(id)` | | Stop camera animation |
| `level.remove_complex_effector(id)` | | Stop complex effector |
| `level.remove_pp_effector(id)` | | Remove post-process effect |
| `level.set_game_difficulty(enum_val)` | | Change difficulty |
| `level.set_pp_effector_factor(id, factor)` | | Blend post-process intensity |
| `level.set_snd_volume(v)` | | Set master sound volume |
| `level.set_time_factor(n)` | | Set time acceleration multiplier |
| `level.set_weather(name, immediate)` | | Change weather |
| `level.set_weather_fx(name)` | | Start a weather effect (psi storm etc.) |
| `level.show_indicators()` | | Show HUD indicators |
| `level.show_weapon(bool)` | | Toggle weapon render |
| `level.spawn_item(sec, pos, lvid, gvid)` | | Spawn a client-side object (not tracked by alife) |
| `level.spawn_phantom(pos)` | | Spawn a phantom entity |
| `level.start_weather_fx_from_time(name, t)` | | Start weather effect at a given elapsed time |
| `level.stop_weather_fx()` | | Stop active weather effect |
| `level.vertex_id(pos)` | | Nearest navmesh vertex to a world position |
| `level.vertex_in_direction(lvid, dir, dist)` | | Navmesh vertex in a direction |
| `level.vertex_position(lvid)` | | World position of a navmesh vertex |

---

## game

Game-wide utilities — localisation, time, HUD animations.

**Full reference: [game](game.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `game.actor_lower_weapon()` | | Lower weapon to safe position |
| `game.actor_weapon_lowered()` | | True if weapon is currently lowered |
| `game.change_game_news_show_time(ms)` | | Override news notification display duration |
| `game.get_actor_alcohol()` | | Actor's current alcohol level (0–1) |
| `game.get_game_time()` | | Returns `CTime` for current in-game time |
| `game.get_motion_length(sec, name, speed)` | | Total duration of an animation in seconds |
| `game.get_resolutions()` | | String of all supported display resolutions |
| `game.has_active_tutorial()` | | True if a tutorial is currently displayed |
| `game.hud_motion_allowed()` | | True if HUD motion system is active |
| `game.only_allow_movekeys(bool)` | | Restrict input to movement keys |
| `game.only_movekeys_allowed()` | | Query movement-keys-only state |
| `game.play_hud_anm(name, part, speed, power, loop, no_restart)` | | Play a blended HUD animation |
| `game.play_hud_motion(hand, sec, anim, loop, speed)` | | Play a hand/motion animation |
| `game.prefetch_model(path)` | | Preload a model without extension |
| `game.prefetch_texture(path)` | | Preload a texture with extension |
| `game.reload_language()` | | Reload all language XML files |
| `game.reload_ui_xml()` | | Clear XML cache and reload all HUD XML |
| `game.set_actor_allow_ladder(bool)` | | Toggle ladder climbing |
| `game.set_hud_anm_time(name, t)` | | Set playback time; returns current time |
| `game.set_nv_lumfactor(v)` | | Adjust night vision luminance factor |
| `game.start_tutorial(name)` | | Show a named tutorial |
| `game.stop_all_hud_anms(force)` | | Stop all active HUD animations |
| `game.stop_hud_anm(name, force)` | | Stop a named HUD animation |
| `game.stop_hud_motion()` | | Stop current hand animation |
| `game.stop_tutorial()` | | Stop the active tutorial |
| `game.time()` | | Raw game time as ms since epoch |
| `game.translate_string(key)` | | Look up a localisation string by key |
| `game.world2ui(pos)` | | Convert world position to UI screen coordinates |

---

## alife()

The A-Life simulation — server-side entity management.

**Full reference: [alife](alife.md)**

Prefer the `_g.script` wrappers below over calling `alife()` directly.

### Global helpers (`_g.script`)

| Function | Req | Description |
|----------|-----|-------------|
| `alife_create(section, pos, lid, gid, [parent_id])` | | Spawn any entity in the world |
| `alife_create_item(section, recipient, [props])` | | Spawn an item directly into an inventory |
| `alife_object(id)` | | Server entity by ID; `nil` if not found |
| `alife_release(se_or_game_obj, [reason])` | | Destroy an entity permanently |
| `alife_release_id(id, [reason])` | | Destroy by alife ID |
| `disable_info(info_id)` | | Unset an actor quest flag |
| `get_object_story_id(obj_id)` | | Reverse lookup: ID → story_id string |
| `get_story_object(story_id)` | | Game object for a named entity (nil if offline) |
| `get_story_object_id(story_id)` | | Numeric alife ID for a named entity |
| `get_story_se_object(story_id)` | | Server entity for a named entity |
| `get_story_squad(story_id)` | | Squad server object for a named squad |
| `give_info(info_id)` | | Set an actor quest flag |
| `has_alife_info(info_id)` | | Check actor quest flag via alife simulator |

### Raw alife() methods

| Method | Req | Description |
|--------|-----|-------------|
| `alife():actor()` | | Server-side actor entity |
| `alife():add_in_restriction(se_obj, restr_id)` | | Add in-restriction to NPC/monster |
| `alife():add_out_restriction(se_obj, restr_id)` | | Add out-restriction to NPC/monster |
| `alife():create(sec, pos, lvid, gvid, [parent])` | | Spawn entity |
| `alife():create_ammo(sec, pos, lvid, gvid, parent, count)` | | Spawn an ammo stack |
| `alife():disable_info(entity_id, info_id)` | | Remove info portion from any entity |
| `alife():dont_has_info(entity_id, info_id)` | | True if entity does NOT have the info |
| `alife():get_children(se_obj)` | | Iterator over child entities (inventory) |
| `alife():give_info(entity_id, info_id)` | | Give info portion to any entity |
| `alife():has_info(entity_id, info_id)` | | Check quest flag on any entity |
| `alife():kill_entity(se_obj, [gvid])` | | Mark entity as dead in simulation |
| `alife():level_id()` | | Numeric ID of the level the actor is on |
| `alife():level_name(level_id)` | | Level name string for a numeric level ID |
| `alife():object(id)` | | Server entity by ID; `nil` if not found |
| `alife():release(se_obj, force)` | | Destroy entity |
| `alife():remove_all_restrictions(id, type)` | | Remove all restrictions of a type |
| `alife():remove_in_restriction(se_obj, restr_id)` | | Remove in-restriction |
| `alife():remove_out_restriction(se_obj, restr_id)` | | Remove out-restriction |
| `alife():set_interactive(id, bool)` | | Toggle whether NPCs can interact with object |
| `alife():set_switch_offline(id, bool)` | | Force offline transition |
| `alife():set_switch_online(id, bool)` | | Force online transition |
| `alife():spawn_id(spawn_story_id)` | | Spawn by spawn_story_id number |
| `alife():story_object(story_id)` | | Server entity for a story ID |
| `alife():switch_distance()` | | Get current spawn radius |
| `alife():switch_distance(n)` | | Set spawn radius |
| `alife():teleport_object(id, gvid, lvid, pos)` | | Move server entity to position |
| `alife():valid_object_id(id)` | | True if ID is valid (not 65535 and exists) |

---

## xr_logic

Condition list evaluation and NPC logic schemes.

**Full reference: [xr_logic](xr-logic.md)**

| Function | Req | Description |
|----------|-----|-------------|
| `xr_logic.assign_storage_and_bind(obj, ini, scheme, sec)` | | Bind a scheme to an object |
| `xr_logic.cfg_get_switch_conditions(ini, sec, obj)` | | Read all `on_info` fields from an LTX section |
| `xr_logic.is_active(obj, action)` | | Check if a scheme/action is active on an object |
| `xr_logic.issue_event(obj, st, event)` | | Fire an event on a subscribed action |
| `xr_logic.mob_capture(obj, bool)` | | Take/release scripted control of a creature |
| `xr_logic.parse_condlist(npc, sec, field, str)` | | Parse a condition list string into a table |
| `xr_logic.pick_section_from_condlist(obj, npc, cl)` | | Evaluate a parsed condlist; returns the matching section name or `nil` |
| `xr_logic.subscribe_action_for_events(obj, st, action)` | | Register a scheme action for event callbacks |
| `xr_logic.switch_to_section(obj, ini, section)` | | Force a section switch |
| `xr_logic.try_switch_to_another_section(obj, st, actor)` | | Evaluate and execute any pending section switch |

---

## UI & settings

HUD messages, notifications, and settings access.

**Full reference: [UI Functions](ui.md)**

| Function | Req | Description |
|----------|-----|-------------|
| `ui_mcm.get(mod, key)` | | Read an MCM setting value |
| `ui_options.get(group, key)` | | Read a game option value |
| `ui_mcm.get_mod_key(mod, key)` | | Get the MCM key path string |
| `news_manager.send_tip(actor, text, icon, delay, time, task)` | | Queue a tip/notification |
| `ui_mcm.set(mod, key, value)` | | Write an MCM setting value |
| `actor_menu.set_fade_msg(text, dur)` | | Show a fading centre message |
| `actor_menu.set_msg(side, text, dur)` | | Show a screen-edge HUD message |
| `actor_menu.set_notification(icon, header, body, sound, dur)` | | Show a notification popup |

---

## Type-checking helpers (`_g.script`)

These functions wrap `clsid` comparisons for common object types:

| Function | Req | Returns true if… |
|----------|-----|-----------------|
| `get_clsid(obj)` | | Returns `obj:clsid()` safely (nil-checks `obj`) |
| `IsArtefact(obj, [clsid])` | | Object is an artefact |
| `IsBackpack(obj, [clsid])` | | Object is a backpack |
| `IsFood(obj, [clsid])` | | Object is a consumable |
| `IsMonster(obj, [clsid])` | | Object is a mutant |
| `IsOutfit(obj, [clsid])` | | Object is a suit/outfit |
| `IsStalker(obj, [clsid])` | | Object is a human NPC or the actor |
| `IsWeapon(obj, [clsid])` | | Object is any weapon |

---

## db namespace

| Name | Req | Description |
|------|-----|-------------|
| `db.actor` | | The player's `game_object`. See [db.actor](actor.md). |
| `db.add_obj(game_obj)` | | Register an online object in db.storage |
| `db.del_obj(game_obj)` | | Remove an object from db.storage |
| `db.offline_objects` | | Table of currently offline entity IDs |
| `db.smart_terrain_by_id` | | Table mapping alife ID → smart terrain server entity |
| `db.storage` | | Per-object state table, keyed by alife ID. See [db.storage](../scripting/db-storage.md). |

---

## game_object (general)

All in-world entities — NPCs, items, weapons, anomalies, the actor — are `game_object` instances. This section covers methods available on **any** game object. Actor-specific methods are in [db.actor](actor.md).

**Full reference: [game_object](game-object.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `obj:alive()` | | True if not dead |
| `obj:bind_object(binder)` | | Attach object_binder instance |
| `obj:bone_position(name)` | | World position of a named bone |
| `obj:character_community()` | | Faction string |
| `obj:character_name()` | | Display name |
| `obj:clsid()` | | Class ID — compare with `clsid.*` constants |
| `obj:condition()` | | Item durability (0–1) |
| `obj:direction()` | | Facing direction (radians) |
| `obj:game_vertex_id()` | | Global graph node |
| `obj:get_ammo_in_magazine()` | | Rounds in magazine |
| `obj:get_ammo_total()` | | Total ammo count |
| `obj:give_money(n)` | | Add RU |
| `obj:hit(hit_obj)` | | Apply a `hit` object for damage |
| `obj:id()` | | Alife ID |
| `obj:invulnerable([bool])` | | Get/set invulnerability |
| `obj:iterate_inventory(fn, data)` | | Iterate inventory items |
| `obj:kill(who)` | | Kill the object |
| `obj:level_vertex_id()` | | Local navmesh node |
| `obj:max_health()` | | Maximum health |
| `obj:money()` | | Current RU balance |
| `obj:name()` | | Internal name string |
| `obj:object(section)` | | First matching inventory item |
| `obj:parent()` | | Owner object if in an inventory |
| `obj:position()` | | World position (`vector`) |
| `obj:relation(other)` | | Relation enum toward `other` |
| `obj:script(bool, name)` | | Take/release scripted control |
| `obj:section()` | | Config section name |
| `obj:see(other)` | | True if NPC has LOS to `other` |
| `obj:set_callback(type, fn)` | | Register per-object callback |
| `obj:set_condition(v)` | | Set item durability |
| `obj:spawn_ini()` | | Spawn config as `ini_file` |
| `obj:start_particles(effect, bone)` | | Attach particle effect |
| `obj:stop_particles(effect, bone)` | | Remove particle effect |
| `obj:story_id()` | | Story ID, or -1 |

Type-testing: `is_actor()`, `is_stalker()`, `is_monster()`, `is_weapon()`, `is_outfit()`, `is_artefact()`, `is_ammo()`, `is_anomaly()`, `is_inventory_box()`, `is_space_restrictor()`, and more — see [game_object](game-object.md#type-testing).

---

## ini_file

Runtime LTX config reader. Returned by `system_ini()`, `game_ini()`, `create_ini_file(path)`, and `obj:spawn_ini()`.

**Full reference: [ini_file](ini-file.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `ini:line_count(section)` | | Number of keys in section |
| `ini:line_exist(section, key)` | | True if key exists in section |
| `ini:r_bool(section, key)` | | Read boolean value |
| `ini:r_clsid(section, key)` | | Read class ID |
| `ini:r_float(section, key)` | | Read float value |
| `ini:r_line(ini, section, i, key_out, val_out)` | | Read key+value at 0-based index `i` |
| `ini:r_s32(section, key)` | | Read signed integer |
| `ini:r_string(section, key)` | | Read string value |
| `ini:r_u32(section, key)` | | Read unsigned integer |
| `ini:r_vector(section, key)` | | Read vector (`x, y, z`) |
| `ini:section_exist(section)` | | True if section exists |

---

## vector

3D vector — used for positions, directions, velocities.

**Full reference: [vector](vector.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `v:add(other)` | | Add component-wise (in place) |
| `v:average(a, b)` | | Midpoint |
| `v:crossproduct(a, b)` | | Cross product into `v` |
| `v:distance_to(other)` | | 3D distance |
| `v:distance_to_sqr(other)` | | Squared distance |
| `v:distance_to_xz(other)` | | 2D distance (ignoring Y) |
| `v:div(n)` | | Divide by scalar |
| `v:dotproduct(other)` | | Dot product |
| `v:getH()` | | Heading angle |
| `v:lerp(a, b, t)` | | Linear interpolate |
| `v:magnitude()` | | Length |
| `v:mul(n)` | | Multiply by scalar |
| `v:normalize()` | | Normalise to unit length |
| `v:normalize_safe()` | | Normalise or zero if zero-length |
| `v:set(x, y, z)` | | Set components |
| `v:setHP(heading, pitch)` | | Set from angles |
| `v:sub(other)` | | Subtract component-wise |
| `vector()` | | Construct `(0,0,0)` |

---

## hit

Damage event object — create, fill, and pass to `obj:hit()`.

**Full reference: [hit](hit.md)**

| Property / Method | Req | Description |
|----------|-----|-------------|
| `h:bone(name)` | | Target specific bone |
| `h.direction` | | Direction (`vector`) |
| `h.draftsman` | | Credit for the kill (`game_object`) |
| `hit()` | | Construct empty hit |
| `h.impulse` | | Physics impulse |
| `h.power` | | Damage amount (0–1+ fraction of max health) |
| `h.type` | | Damage type (`hit.wound`, `hit.burn`, etc.) |

Hit type constants: `hit.burn`, `hit.shock`, `hit.chemical_burn`, `hit.radiation`, `hit.telepatic`, `hit.wound`, `hit.strike`, `hit.explosion`, `hit.fire_wound`, `hit.light_burn`, `hit.dummy`.

---

## sound_object

Scripted sound playback — 3D positional or 2D non-positional.

**Full reference: [sound_object](sound-object.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `snd.frequency` | | Pitch multiplier |
| `snd:length()` | | Duration in seconds |
| `snd.max_distance` | | Inaudible distance |
| `snd.min_distance` | | Full-volume distance |
| `snd:play(obj)` | | Play at object's position |
| `snd:play(obj, delay, flags)` | | Play with delay / flags |
| `snd:play_at_pos(obj, pos)` | | Play at world position |
| `snd:playing()` | | True if currently playing |
| `sound_object(path)` | | Construct (path relative to `sounds/`, no extension) |
| `snd:stop()` | | Stop immediately |
| `snd:stop_deffered()` | | Stop after current loop |
| `snd.volume` | | Volume (0–1) |

Flags: `sound_object.s3d` (default), `sound_object.s2d`, `sound_object.looped`.

---

## CTime

In-game time object returned by `game.get_game_time()`.

**Full reference: [CTime](ctime.md)**

| Method | Req | Description |
|--------|-----|-------------|
| `t:add(other)` / `t:sub(other)` | | Add/subtract CTimes |
| `t:dateToString(fmt)` | | Format date as string |
| `t:diffSec(other)` | | Difference in game seconds |
| `t:get(...)` | | Returns year, month, day, h, m, s, ms |
| `t:set(y, mo, d, h, m, s, ms)` | | Set all components |
| `t:setHMS(h, m, s)` | | Set H:M:S |
| `t:timeToString(fmt)` | | Format time as string |

Global `CTime()` / `CTime(t)` constructors and the `CTime.*` format name constants are **often not registered** for mod scripts — use `game.get_game_time()` and numeric format codes (see [CTime](ctime.md#getting-a-ctime-userdata)).

---

## particles_object

Script-controlled particle effect object.

| Method | Req | Description |
|--------|-----|-------------|
| `po:load_path(path)` | | Load a movement path |
| `po:looped()` | | True if looped effect |
| `po:move_to(pos, dir)` | | Move to position |
| `particles_object(name)` | | Construct with effect name |
| `po:pause_path(bool)` | | Pause/resume path |
| `po:play()` | | Start playing |
| `po:play_at_pos(pos)` | | Play at world position |
| `po:playing()` | | True if active |
| `po:start_path(loop)` | | Start path-following |
| `po:stop()` | | Stop |
| `po:stop_deffered()` | | Stop after current loop |
| `po:stop_path()` | | Stop path-following |

For attaching effects to game objects, use `obj:start_particles(effect, bone)` instead.

---

## relation_registry namespace

Community (faction-to-faction) relation management.

| Function | Req | Description |
|----------|-----|-------------|
| `relation_registry.change_community_goodwill(faction, entity_id, delta)` | | Adjust goodwill by delta |
| `relation_registry.community_goodwill(faction, entity_id)` | | Get goodwill of an entity toward a faction |
| `relation_registry.community_relation(fac_a, fac_b)` | | Get relation between two faction strings |
| `relation_registry.set_community_goodwill(faction, entity_id, val)` | | Set absolute goodwill |
| `relation_registry.set_community_relation(fac_a, fac_b, val)` | | Set faction-to-faction relation |

---

## actor_stats namespace

Tracking and award statistics.

| Function | Req | Description |
|----------|-----|-------------|
| `actor_stats.add_points(stat, id, score, amount)` | | Add points to a stat |
| `actor_stats.add_points_str(stat, id, string)` | | Add string-keyed stat points |
| `actor_stats.get_points(stat)` | | Get current point value |

---

## weather namespace

Fine-grained weather parameter control (modded exes).

| Function | Req | Description |
|----------|-----|-------------|
| `weather.boost_reset()` | | Reset all boosts |
| `weather.boost_value(key, val)` | | Temporarily boost a parameter |
| `weather.get_value_numric(key)` | | Get a numeric weather parameter |
| `weather.get_value_string(key)` | | Get a string weather parameter |
| `weather.get_value_vector(key)` | | Get a vector weather parameter |
| `weather.is_paused()` | | True if paused |
| `weather.pause(bool)` | | Pause/resume weather cycling |
| `weather.reload()` | | Reload weather config |
| `weather.set_value_numric(key, val)` | | Set a numeric weather parameter |
| `weather.set_value_string(key, val)` | | Set a string weather parameter |
| `weather.set_value_vector(key, x, y, z, w)` | | Set a vector weather parameter |

---

## Global functions

Globally available functions that don't belong to a namespace:

| Function | Req | Description |
|----------|-----|-------------|
| `db.actor` | | The player `game_object` |
| `alife()` | | The `alife_simulator` singleton |
| `app_ready()` | | True once the engine is fully initialised |
| `bit_and(a, b)` | | Bitwise AND |
| `bit_not(a)` | | Bitwise NOT |
| `bit_or(a, b)` | | Bitwise OR |
| `bit_xor(a, b)` | | Bitwise XOR |
| `command_line()` | | Raw command line string |
| `create_ini_file(path)` | | Open any VFS file as `ini_file` |
| `device()` | | Render device object |
| `dik_to_bind(dik)` | | Convert `DIK_keys` constant to `key_bindings` |
| `error_log(msg)` | | Write `msg` to the error log |
| `flush()` | | Flush the log buffers |
| `game_graph()` | | Global navigation graph object |
| `game_ini()` | | Game config (includes AI files) |
| `get_console()` | | Console object |
| `get_hud()` | | HUD manager object |
| `GetARGB(a, r, g, b)` | | Pack colour channels into a single number |
| `GetFontDI()` | | DI font object |
| `GetFontMedium()` | | Medium UI font object |
| `GetFontSmall()` | | Small UI font object |
| `getFS()` | | File system object |
| `IsDynamicMusic()` | | True if dynamic music is active |
| `IsGameTypeSingle()` | | True in singleplayer mode |
| `log(msg)` | | Write `msg` to the script log |
| `reload_system_ini()` | | Reload `system_ini` in-game (Alundaio extension) |
| `render_get_dx_level()` | | Current DirectX renderer level (8/9) |
| `system_ini()` | | Global config `ini_file` |
| `time_continual()` | | Like `time_global()` but continues while paused |
| `time_global()` | | Real-time milliseconds since engine start |
| `user_name()` | | Current user name string |

---

## Constants

### clsid

`clsid` constants identify the class of a `game_object` or server entity. Compare with `obj:clsid()`.

Key values:

| Constant | Req | Meaning |
|----------|-----|---------|
| `clsid.actor` | | Player actor |
| `clsid.artefact` | | Artefact |
| `clsid.bloodsucker` … `clsid.zombie` | | Mutant creatures |
| `clsid.equ_stalker` / `clsid.equ_exo` | | Armour suits |
| `clsid.helmet` | | Helmet |
| `clsid.inventory_box` | | Stash |
| `clsid.obj_medkit` / `clsid.obj_food` / `clsid.obj_bandage` | | Consumables |
| `clsid.smart_terrain` | | Smart terrain |
| `clsid.space_restrictor` / `clsid.script_restr` | | Zone/restrictor |
| `clsid.stalker` / `clsid.script_stalker` | | NPC stalker |
| `clsid.trader` / `clsid.script_trader` | | Trader NPC |
| `clsid.wpn_ak74` … `clsid.wpn_walther` | | Specific weapon types |
| `clsid.wpn_ammo` | | Ammo box |

The full list (228+ values) is in `scripts/lua_help.script` in your unpacked Anomaly installation. Use `_g.script` type helpers (`IsStalker`, `IsMonster`, `IsWeapon`, etc.) instead of raw clsid comparisons where possible.

---

### callback

Per-object callback type constants, used with `obj:set_callback(type, fn)`:

| Constant | Req | When it fires |
|----------|-----|--------------|
| `callback.death` | | Object dies |
| `callback.hit` | | Object receives a hit |
| `callback.inventory_info` | | Info portion state changes |
| `callback.map_location_added` | | Map marker added |
| `callback.on_item_drop` | | Item dropped |
| `callback.on_item_take` | | Item picked up |
| `callback.patrol_path_in_point` | | Patrol reaches a waypoint |
| `callback.sound` | | Object hears a sound |
| `callback.take_item_from_box` | | Item taken from box |
| `callback.task_state` | | Task state changed |
| `callback.trade_sell_buy_item` | | Item bought/sold |
| `callback.trade_start` / `callback.trade_stop` | | Trade opened/closed |
| `callback.use_object` | | Player uses object |
| `callback.weapon_no_ammo` | | Weapon runs out of ammo |
| `callback.zone_enter` / `callback.zone_exit` | | Zone entry/exit |

The full list is in `scripts/lua_help.script` in your unpacked Anomaly installation.

---

### key_bindings

Logical key binding constants, used with `level.hold_action()`, `level.press_action()`, `level.release_action()`:

| Constant | Req | Action |
|----------|-----|--------|
| `key_bindings.kBACK` | | Move backward |
| `key_bindings.kCROUCH` | | Crouch |
| `key_bindings.kCUSTOM1` … `kCUSTOM25` | | Custom keybinds (MCM) |
| `key_bindings.kDROP` | | Drop item |
| `key_bindings.kFWD` | | Move forward |
| `key_bindings.kINVENTORY` | | Inventory screen |
| `key_bindings.kJUMP` | | Jump |
| `key_bindings.kLEFT` / `kRIGHT` | | Strafe |
| `key_bindings.kUSE` | | Use / interact |
| `key_bindings.kWPN_1` … `kWPN_6` | | Weapon slots |
| `key_bindings.kWPN_FIRE` | | Fire weapon |
| `key_bindings.kWPN_RELOAD` | | Reload |
| `key_bindings.kWPN_ZOOM` | | Aim / zoom |

---

### DIK_keys

Raw DirectInput keyboard constants. Used with MCM keybind settings. Convert to a logical bind with `dik_to_bind(dik)`.

Common values: `DIK_keys.DIK_F1` … `DIK_F12`, `DIK_keys.DIK_A` … `DIK_Z`, `DIK_keys.MOUSE_1` / `MOUSE_2` / `MOUSE_3`.

The full set is in `scripts/lua_help.script` in your unpacked Anomaly installation.

---

### game_difficulty

| Constant | Req | Value |
|----------|-----|-------|
| `game_difficulty.master` | | 3 |
| `game_difficulty.novice` | | 0 |
| `game_difficulty.stalker` | | 1 |
| `game_difficulty.veteran` | | 2 |

Read with `level.get_game_difficulty()`.

---

### snd_type

Sound category bitmasks. Used when registering sounds with `obj:add_sound()`.

Key values: `snd_type.no_sound`, `snd_type.idle`, `snd_type.attack`, `snd_type.die`, `snd_type.injure`, `snd_type.talk`, `snd_type.step`, `snd_type.weapon`, `snd_type.item`, `snd_type.monster`, `snd_type.world`, `snd_type.ambient`.

---

### ui_events

Event constants for UI element callbacks:

| Constant | Req | When |
|----------|-----|------|
| `ui_events.BUTTON_CLICKED` | | Button left-click |
| `ui_events.BUTTON_DOWN` | | Button pressed |
| `ui_events.CHECK_BUTTON_RESET` | | Checkbox unchecked |
| `ui_events.CHECK_BUTTON_SET` | | Checkbox checked |
| `ui_events.EDIT_TEXT_COMMIT` | | Edit box committed |
| `ui_events.LIST_ITEM_CLICKED` | | List item clicked |
| `ui_events.LIST_ITEM_SELECT` | | List item selected |
| `ui_events.MESSAGE_BOX_NO_CLICKED` | | Message box No |
| `ui_events.MESSAGE_BOX_OK_CLICKED` | | Message box OK |
| `ui_events.MESSAGE_BOX_YES_CLICKED` | | Message box Yes |
| `ui_events.SCROLLBAR_VSCROLL` | | Vertical scroll |
| `ui_events.TAB_CHANGED` | | Tab bar changed |
| `ui_events.WINDOW_KEY_PRESSED` | | Key pressed while window focused |

---

## Server entity classes (alife)

The server-side entity hierarchy (accessible via `alife():object(id)`). Full coverage is in the [alife](alife.md) reference.

| Class | Req | Description |
|-------|-----|-------------|
| `cse_abstract` | | Base class: `id`, `position`, `angle`, `parent_id`, `section_name()`, `name()`, `clsid()`, `spawn_ini()` |
| `cse_alife_creature_abstract` | | Adds `health`, `group_id`, `rank` |
| `cse_alife_creature_actor` | | Server-side actor |
| `cse_alife_dynamic_object` | | Adds `can_switch_online/offline`, `switch_online/offline` |
| `cse_alife_dynamic_object_visual` | | Adds visual/model data |
| `cse_alife_helicopter` | | Helicopter |
| `cse_alife_human_stalker` | | Human NPC — adds `community`, dialog, rank, reputation |
| `cse_alife_inventory_box` | | Stash/box |
| `cse_alife_item` | | Base inventory item — adds `condition` |
| `cse_alife_item_ammo` | | Ammo — adds `ammo_type`, `elapsed` |
| `cse_alife_item_artefact` | | Artefact |
| `cse_alife_item_custom_outfit` | | Armour suit |
| `cse_alife_item_detector` | | Detector device |
| `cse_alife_item_weapon` | | Weapon server entity — adds ammo, upgrades |
| `cse_alife_level_changer` | | Level transition trigger |
| `cse_alife_monster_abstract` | | Monster base — adds restrictions, kill helpers |
| `cse_alife_monster_base` | | Physics-enabled monster |
| `cse_alife_object` | | Adds `m_game_vertex_id`, `m_level_vertex_id`, `m_story_id`, `online` |
| `cse_alife_online_offline_group` | | NPC squad group |
| `cse_alife_smart_zone` | | Smart terrain zone |
| `cse_alife_space_restrictor` | | Zone restrictor |

---

## CScriptXmlInit

UI XML element initialiser. Instantiated in UI scripts to build HUD windows from XML definitions.

| Method | Req | Description |
|--------|-----|-------------|
| `xml:Init(path, ...)` | | Load an XML file |
| `xml:InitButton(section, parent)` | | Create a button |
| `xml:InitCheck(section, parent)` | | Create a checkbox |
| `xml:InitComboBox(section, parent)` | | Create a combo box |
| `xml:InitEditBox(section, parent)` | | Create an edit box |
| `xml:InitFont(section, parent)` | | Get a font from section |
| `xml:InitFrame(section, parent)` | | Create a frame |
| `xml:InitFrameLine(section, parent)` | | Create a frame line |
| `xml:InitListBox(section, parent)` | | Create a list box |
| `xml:InitScrollView(section, parent)` | | Create a scroll view |
| `xml:InitStatic(section, parent)` | | Create a static/label |
| `xml:InitTab(section, parent)` | | Create a tab control |
| `xml:InitTextWnd(section, parent)` | | Create a text window |
| `xml:InitTrackBar(section, parent)` | | Create a track bar |
| `xml:InitWindow(section, parent)` | | Create a basic window |

See [UI Scripting](../systems/ui-scripting.md) for worked UI examples. The `CUIWindow` base class (from which all UI elements inherit) has ~100 methods for positioning, visibility, events, and child management — beyond the scope of this index.

---

## GOAP / action planner classes

The engine's Goal-Oriented Action Planning system, used for advanced NPC AI scripting. Rarely needed unless you are writing custom NPC behaviour schemes.

| Class | Req | Description |
|-------|-----|-------------|
| `action_base` | | A single action in the planner |
| `action_planner` | | GOAP planner — manages actions and evaluators |
| `planner_action` | | Combined planner + action |
| `property_evaluator` | | Evaluates a world-state property (boolean) |
| `property_evaluator_const` | | Evaluator that always returns a constant |
| `world_property` | | Single property: condition ID + boolean value |
| `world_state` | | Set of world-state properties |

These classes are used in base game scripts like `xr_combat.script`, `xr_stalker.script`, and similar NPC behaviour scheme scripts.

---

## Not yet documented

The following modules are used in mods but not yet fully covered in this guide:

| Module | Req | Description |
|--------|-----|-------------|
| `axr_task_manager` | | Quest task creation and management |
| `bind_stalker_ext` | | Extended actor binder callbacks (see base game source) |
| `sim_board` | | Simulation board — squad/smart terrain matching |
| `story_objects` | | `story_id` registration and lookup internals |

---

## See also

- [The Callback System](../scripting/callbacks.md) — how to register for engine events
- [What is a game_object?](../scripting/game-object.md) — the object all methods operate on
- [Callbacks Reference](../callbacks-reference/index.md) — full list of available callbacks
- [Glossary](../reference/glossary.md) — definitions of Anomaly-specific terms
