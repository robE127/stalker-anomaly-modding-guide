# game_object

`game_object` is the Lua class for every entity that exists in the game world as a client-side object — NPCs, mutants, items, weapons, anomaly zones, campfires, inventory boxes, and the actor. Every object you receive in a callback or retrieve with `level.object_by_id()` is a `game_object`.

!!! note "db.actor is a game_object"
    All methods on this page also work on `db.actor`. The [db.actor reference](actor.md) documents actor-specific usage and adds the actor-only methods not covered here.

---

## Identity & position

These methods work on any game_object regardless of type.

| Method | Returns | Description |
|--------|---------|-------------|
| `obj:id()` | `number` | Alife ID (unique, stable per session) |
| `obj:name()` | `string` | Internal name (e.g. `"esc_stalker_01"`) |
| `obj:section()` | `string` | Config section (e.g. `"stalker_novice"`) |
| `obj:clsid()` | `number` | Class ID constant — compare with `clsid.*` |
| `obj:position()` | `vector` | World position |
| `obj:level_vertex_id()` | `number` | Local navmesh vertex |
| `obj:game_vertex_id()` | `number` | Global graph node |
| `obj:direction()` | `number` | Facing direction in radians |
| `obj:parent()` | `game_object\|nil` | Owner if carried in inventory; `nil` otherwise |
| `obj:story_id()` | `number` | Story ID if assigned; `-1` otherwise |

```lua
local obj = level.object_by_id(some_id)
if obj then
    printf("[my_mod] %s at %s (section=%s)", obj:name(), tostring(obj:position()), obj:section())
end
```

---

## Type testing

Use these to check what kind of object you have before calling type-specific methods. The `is_*` functions return `true`/`false`.

| Method | True when… |
|--------|-----------|
| `obj:is_actor()` | Object is the player |
| `obj:is_stalker()` | Human NPC (not actor) |
| `obj:is_monster()` | Mutant creature |
| `obj:is_custom_monster()` | Both stalkers and monsters |
| `obj:is_trader()` | Trader NPC |
| `obj:is_entity_alive()` | Creature that can die (alive or dead) |
| `obj:is_weapon()` | Any weapon |
| `obj:is_weapon_magazined()` | Magazine-fed weapon |
| `obj:is_weapon_gl()` | Weapon with underbarrel launcher |
| `obj:is_outfit()` | Suit/armour |
| `obj:is_artefact()` | Artefact |
| `obj:is_ammo()` | Ammo box |
| `obj:is_scope()` | Scope attachment |
| `obj:is_silencer()` | Silencer attachment |
| `obj:is_grenade_launcher()` | Grenade launcher attachment |
| `obj:is_hud_item()` | Item that has a HUD model |
| `obj:is_space_restrictor()` | Zone/restrictor |
| `obj:is_anomaly()` | Anomaly zone |
| `obj:is_inventory_item()` | Can be held in inventory |
| `obj:is_inventory_owner()` | Has an inventory (NPC/actor) |
| `obj:is_inventory_box()` | Stash/inventory box |

!!! tip "Prefer `_g.script` helpers for simple checks"
    `IsStalker(obj)`, `IsMonster(obj)`, `IsWeapon(obj)` etc. wrap `clsid` comparisons and are safer (nil-check included). See [Type-checking helpers](index.md#type-checking-helpers-_gscript).

```lua
local function on_hit(obj, amount, local_dir, who, bone)
    if obj:is_stalker() or obj:is_monster() then
        printf("[my_mod] %s was hit for %f", obj:name(), amount)
    end
end
```

---

## Vitals

Properties on a `game_object` (read/write directly):

| Property | Range | Description |
|----------|-------|-------------|
| `obj.health` | 0–1 | Current health |
| `obj.power` | 0–1 | Current stamina |
| `obj.psy_health` | 0–1 | Psychic health |
| `obj.radiation` | 0–1 | Radiation level |
| `obj.bleeding` | 0–1 | Bleeding intensity |
| `obj.morale` | 0–1 | Morale (creatures) |

For incremental changes prefer the `change_*` methods:

| Method | Description |
|--------|-------------|
| `obj:change_health(delta)` | Add delta to health (negative to damage) |
| `obj:change_power(delta)` | Add delta to stamina |
| `obj:change_psy_health(delta)` | Add delta to psy health |
| `obj:change_radiation(delta)` | Add delta to radiation |
| `obj:change_bleeding(delta)` | Add delta to bleed rate — **NPCs/monsters only**; crashes with nil if called on `db.actor` |
| `obj:change_morale(delta)` | Add delta to morale |
| `obj:alive()` | Returns `true` if not dead |
| `obj:max_health()` | Maximum health value |
| `obj:wounded()` | Get/set wounded state (boolean) |
| `obj:critically_wounded()` | True if in critical wound state |
| `obj:mass()` | Physics mass |

---

## Info portions

Info portions work on any entity that can carry them (actors, NPCs).

| Method | Description |
|--------|-------------|
| `obj:has_info(id)` | `true` if entity has this info portion |
| `obj:dont_has_info(id)` | `true` if entity does NOT have it |
| `obj:give_info_portion(id)` | Set the info portion |
| `obj:disable_info_portion(id)` | Unset the info portion |

---

## Applying damage

To deal damage to any creature from script, create a `hit` object and call `obj:hit()`:

```lua
local function damage_npc(npc, amount)
    local h = hit()
    h.type        = hit.wound
    h.power       = amount
    h.direction   = vector():set(0, -1, 0)
    h.draftsman   = db.actor   -- who is credited with the hit
    h.impulse     = 1.0
    npc:hit(h)
end
```

See [hit](hit.md) for all hit type constants and properties.

---

## NPC / stalker methods

These apply when `obj:is_stalker()` or `obj:is_actor()` is true.

### Relations & goodwill

| Method | Description |
|--------|-------------|
| `obj:relation(other)` | Relation enum toward `other` (0=kill, 1=neutral, 2=friend) |
| `obj:goodwill(other)` | Personal goodwill toward `other` game_object |
| `obj:general_goodwill(other)` | Combined goodwill (personal + community) |
| `obj:community_goodwill(faction)` | NPC's community goodwill toward a faction string |
| `obj:set_relation(type, other)` | Override relation enum |
| `obj:set_goodwill(val, other)` | Set personal goodwill (−10000 to 10000) |
| `obj:force_set_goodwill(val, other)` | Force-set goodwill (bypasses clamping) |
| `obj:change_goodwill(delta, other)` | Adjust goodwill by delta |
| `obj:set_community_goodwill(faction, val)` | Set NPC's community goodwill |
| `obj:sympathy()` | Sympathy value (community affinity) |
| `obj:set_sympathy(val)` | Set sympathy |
| `obj:rank()` | Rank value |

### Combat

| Method | Description |
|--------|-------------|
| `obj:see(other)` | True if NPC can currently see `other` |
| `obj:see(section)` | True if NPC can see any object matching section |
| `obj:best_enemy()` | Current best enemy `game_object` |
| `obj:get_enemy()` | Active enemy target |
| `obj:set_enemy(obj)` | Force a new enemy target |
| `obj:best_danger()` | Most threatening danger source |
| `obj:mental_state()` | Current mental state (free/danger/panic) |
| `obj:set_mental_state(state)` | Set mental state |
| `obj:kill(who)` | Kill the NPC, crediting `who` |
| `obj:can_be_harmed()` | Whether NPC can take damage |
| `obj:set_can_be_harmed(bool)` | Toggle harm-ability |
| `obj:invulnerable()` | Get invulnerability |
| `obj:invulnerable(bool)` | Set invulnerability |
| `obj:register_in_combat()` | Mark as combat participant |
| `obj:unregister_in_combat()` | Remove from combat tracking |
| `obj:berserk()` | Force berserk state |

### Character info

| Method | Description |
|--------|-------------|
| `obj:character_name()` | Display name |
| `obj:character_icon()` | Portrait icon |
| `obj:character_community()` | Faction string |
| `obj:character_rank()` | Rank value |
| `obj:character_reputation()` | Reputation |
| `obj:set_character_rank(val)` | Set rank |
| `obj:set_character_community(faction, rank, rep)` | Change faction |
| `obj:set_character_icon(icon)` | Change portrait |
| `obj:change_character_reputation(delta)` | Adjust reputation |
| `obj:profile_name()` | Internal profile name |

### Economy

| Method | Description |
|--------|-------------|
| `obj:money()` | Current money in RU |
| `obj:give_money(amount)` | Add (or remove if negative) RU |
| `obj:transfer_money(amount, target)` | Move RU to another entity |

### Dialog & tasks

| Method | Description |
|--------|-------------|
| `obj:enable_talk()` | Allow player to start dialog |
| `obj:disable_talk()` | Prevent dialog |
| `obj:is_talk_enabled()` | Whether dialog is allowed |
| `obj:is_talking()` | Whether dialog is active |
| `obj:switch_to_talk()` | Open dialog with this NPC |
| `obj:stop_talk()` | End current dialog |
| `obj:allow_break_talk_dialog(bool)` | Whether player can close dialog early |
| `obj:run_talk_dialog(npc, bool)` | Force dialog with `npc` |
| `obj:give_talk_message(npc_id, dialog_id, icon)` | Show talk message |
| `obj:give_talk_message2(npc_id, dialog_id, icon, sound)` | Show talk message with sound |
| `obj:get_start_dialog()` | First dialog ID |
| `obj:set_start_dialog(id)` | Override start dialog |
| `obj:restore_default_start_dialog()` | Reset to config dialog |
| `obj:give_task(task, t1, bool, t2)` | Assign a task |
| `obj:set_active_task(task)` | Set active task |
| `obj:get_task_state(id)` | State of task by ID |

### Patrolling & movement

| Method | Description |
|--------|-------------|
| `obj:set_patrol_path(name, start_type, route_type, bool)` | Set patrol path |
| `obj:patrol()` | Current patrol object |
| `obj:path_completed()` | True if current path is done |
| `obj:set_dest_game_vertex_id(gvid)` | Set destination graph node |
| `obj:set_dest_level_vertex_id(lvid)` | Set destination navmesh node |
| `obj:set_path_type(type)` | Path type (game_path/level_path/etc.) |
| `obj:movement_type()` | Current movement type |
| `obj:set_movement_type(type)` | Override movement type |
| `obj:set_body_state(state)` | Stand/crouch state |
| `obj:set_fov(angle)` | Override field of view |
| `obj:fov()` | Current field of view |
| `obj:set_home(patrol, min, max, aggress, [point])` | Define home territory |
| `obj:remove_home()` | Remove home restriction |
| `obj:jump(pos, factor)` | Force a jump toward `pos` |
| `obj:set_npc_position(pos)` | Teleport NPC to position |
| `obj:set_desired_position([pos])` | Hint at preferred position |
| `obj:set_desired_direction([dir])` | Hint at preferred facing |
| `obj:movement_target_reached()` | True when movement goal reached |
| `obj:get_movement_speed()` | Current movement speed |
| `obj:allow_sprint(bool)` | Toggle sprinting |

### Memory / perception

| Method | Description |
|--------|-------------|
| `obj:memory_visible_objects()` | List of visible remembered objects |
| `obj:memory_sound_objects()` | List of recently heard objects |
| `obj:memory_hit_objects()` | List of recently hit objects |
| `obj:memory_time(other)` | Last time `other` was perceived |
| `obj:memory_position(other)` | Last known position of `other` |
| `obj:not_yet_visible_objects()` | Objects entering vision but not yet seen |
| `obj:enable_memory_object(other, bool)` | Force-track/untrack an object in memory |
| `obj:make_object_visible_somewhen(other)` | Schedule visibility of `other` |
| `obj:set_visual_memory_enabled(bool)` | Toggle visual memory system |
| `obj:enable_vision(bool)` | Toggle vision entirely |
| `obj:vision_enabled()` | Whether vision is on |
| `obj:who_hit_name()` | Name of last attacker |
| `obj:who_hit_section_name()` | Section of last attacker |
| `obj:get_monster_hit_info()` | `MonsterHitInfo` for last hit received |

### Script control (GOAP)

| Method | Description |
|--------|-------------|
| `obj:script(bool, name)` | Take (`true`) or release (`false`) scripted control |
| `obj:get_script()` | True if under script control |
| `obj:can_script_capture()` | True if script control is available |
| `obj:motivation_action_manager(obj)` | Access the GOAP planner |
| `obj:debug_planner(planner)` | Dump planner state to log |
| `obj:action()` | Current active script action |
| `obj:action_count()` | Number of queued actions |
| `obj:action_by_index(i)` | Action at index `i` |
| `obj:reset_action_queue()` | Clear pending actions |
| `obj:set_fastcall(fn, obj)` | Register a per-frame update function |

### Sounds

| Method | Description |
|--------|-------------|
| `obj:add_sound(path, count, type, delay, priority, freq, [anim])` | Register a script sound |
| `obj:add_combat_sound(path, count, type, delay, priority, freq, anim)` | Register combat sound |
| `obj:remove_sound(index)` | Remove a registered sound |
| `obj:play_sound(index, [delay, [priority, [freq, [vol, [pitch]]]]])` | Play a registered sound |
| `obj:active_sound_count([bool])` | Number of currently playing sounds |
| `obj:external_sound_start(name)` | Start an external named sound |
| `obj:external_sound_stop()` | Stop external sound |
| `obj:restore_sound_threshold()` | Reset sound threshold |
| `obj:set_sound_threshold(val)` | Set minimum audible threshold |
| `obj:set_sound_mask(mask)` | Bit-mask of permitted sound channels |
| `obj:sound_prefix()` | Current voice/sound prefix |
| `obj:sound_prefix(prefix)` | Override voice/sound prefix |
| `obj:sound_voice_prefix()` | Voice-specific prefix |

---

## Inventory owner methods

Available when `obj:is_inventory_owner()` is true (NPC or actor).

| Method | Description |
|--------|-------------|
| `obj:object(section)` | First item matching section; `nil` if not found |
| `obj:object(id)` | Item with given alife ID; `nil` if not held |
| `obj:iterate_inventory(fn, data)` | Iterate all items: `fn(data, item)` |
| `obj:iterate_ruck(fn, data)` | Iterate backpack items only |
| `obj:iterate_belt(fn, data)` | Iterate belt items only |
| `obj:inventory_for_each(fn)` | Iterate all items: `fn(item)` |
| `obj:active_item()` | Currently held item |
| `obj:item_in_slot(slot_id)` | Item in slot; `nil` if empty |
| `obj:item_on_belt(index)` | Belt item at 0-based index |
| `obj:belt_count()` | Number of belt items |
| `obj:is_on_belt(item)` | True if item is on the belt |
| `obj:active_slot()` | Active weapon slot index |
| `obj:activate_slot(slot_id)` | Switch active weapon slot |
| `obj:best_weapon()` | Best weapon in inventory |
| `obj:best_item()` | Best general item |
| `obj:get_artefact()` | Currently active artefact |
| `obj:active_detector()` | Active detector object |
| `obj:show_detector()` | Show detector |
| `obj:hide_detector()` | Hide detector |
| `obj:drop_item(item)` | Drop item to the ground |
| `obj:drop_item_and_teleport(item, pos)` | Drop and teleport item |
| `obj:take_items_enabled(bool)` | Toggle item pickup |
| `obj:take_items_enabled()` | Whether item pickup is enabled |
| `obj:is_there_items_to_pickup()` | Items nearby to pick up |
| `obj:transfer_item(item, target)` | Move item to another inventory |
| `obj:move_to_ruck(item)` | Move item to backpack |
| `obj:move_to_slot(item, slot_id)` | Move item to weapon slot |
| `obj:move_to_belt(item)` | Move item to belt |
| `obj:eat(item)` | Consume a food/medkit item |
| `obj:get_total_weight()` | Total carry weight |
| `obj:get_inv_weight()` | Backpack weight |
| `obj:get_inv_max_weight()` | Max backpack capacity |
| `obj:get_actor_max_weight()` | Absolute max carry weight |
| `obj:set_actor_max_weight(v)` | Override max carry weight |
| `obj:get_actor_max_walk_weight()` | Walk weight limit |
| `obj:set_actor_max_walk_weight(v)` | Override walk weight limit |
| `obj:can_select_weapon(bool)` | Toggle weapon auto-select |
| `obj:weapon_strapped()` | True if weapon is holstered |
| `obj:weapon_unstrapped()` | True if weapon is drawn |
| `obj:hide_weapon()` | Holster weapon |
| `obj:restore_weapon()` | Equip previous weapon |
| `obj:make_item_active(item)` | Force item into active slot |
| `obj:mark_item_dropped(item)` | Mark item as intentionally dropped |

---

## Trade methods

| Method | Description |
|--------|-------------|
| `obj:is_trade_enabled()` | Whether trade is available |
| `obj:enable_trade()` | Allow trading |
| `obj:disable_trade()` | Prevent trading |
| `obj:switch_to_trade()` | Open trade UI |
| `obj:item_allow_trade(item)` | Mark item as tradeable |
| `obj:item_deny_trade(item)` | Mark item as not tradeable |
| `obj:buy_condition(ini, section)` | Set buy condition from ini |
| `obj:sell_condition(ini, section)` | Set sell condition from ini |
| `obj:buy_supplies(ini, section)` | Load supply config |
| `obj:buy_item_condition_factor(v)` | Set item condition threshold for purchases |
| `obj:set_trader_global_anim(name)` | Set trader global animation |
| `obj:set_trader_head_anim(name)` | Set trader head animation |
| `obj:set_trader_sound(name, anim)` | Set trader sound |

---

## Item methods

Available when `obj:is_inventory_item()` is true.

| Method | Description |
|--------|-------------|
| `obj:condition()` | Durability (0–1) |
| `obj:set_condition(v)` | Set durability |
| `obj:weight()` | Item weight in kg |
| `obj:set_weight(v)` | Override weight |
| `obj:cost()` | Item value in RU |
| `obj:get_max_uses()` | Maximum use count |
| `obj:get_remaining_uses()` | Remaining uses |
| `obj:set_remaining_uses(n)` | Set remaining uses |
| `obj:install_upgrade(section)` | Apply an upgrade to the item |
| `obj:has_upgrade(section)` | True if upgrade is installed |
| `obj:iterate_installed_upgrades(fn)` | Iterate installed upgrades: `fn(section, item)`, return `true` to stop |

---

## Weapon methods

Available when `obj:is_weapon()` is true.

| Method | Description |
|--------|-------------|
| `obj:get_main_weapon_type()` | Main weapon type constant |
| `obj:set_main_weapon_type(n)` | Override main weapon type |
| `obj:get_weapon_type()` | Weapon category constant |
| `obj:set_weapon_type(n)` | Override weapon category |
| `obj:get_ammo_total()` | Total ammo across all magazines |
| `obj:get_ammo_in_magazine()` | Rounds currently in magazine |
| `obj:set_ammo_elapsed(n)` | Set magazine fill count |
| `obj:unload_magazine(retrieve)` | Unload — pass `true` to recover ammo |
| `obj:force_unload_magazine(retrieve)` | Unload even when jammed |
| `obj:get_ammo_type()` | Current ammo type index |
| `obj:set_ammo_type(n)` | Set ammo type |
| `obj:has_ammo_type(n)` | True if ammo type is compatible |
| `obj:get_state()` | Weapon state constant |
| `obj:get_weapon_substate()` | Sub-state constant |
| `obj:switch_state(n)` | Force weapon state transition |
| `obj:weapon_in_grenade_mode()` | True when in GL mode |
| `obj:weapon_is_scope()` | True if scope is installed |
| `obj:weapon_scope_status()` | Scope attachment status |
| `obj:weapon_is_silencer()` | True if silencer installed |
| `obj:weapon_silencer_status()` | Silencer attachment status |
| `obj:weapon_is_grenadelauncher()` | True if GL installed |
| `obj:weapon_grenadelauncher_status()` | GL attachment status |
| `obj:weapon_addon_attach(item)` | Attach an addon `game_object` |
| `obj:weapon_addon_detach(section)` | Detach addon by section name |
| `obj:set_queue_size(n)` | Override burst size |
| `obj:can_throw_grenades()` | Whether NPC can throw grenades |
| `obj:can_throw_grenades(bool)` | Toggle grenade throwing |

---

## Ammo methods

| Method | Description |
|--------|-------------|
| `obj:ammo_get_count()` | Rounds in this ammo box |
| `obj:ammo_set_count(n)` | Set round count |
| `obj:ammo_box_size()` | Maximum capacity of the box |

---

## Outfit / armour methods

| Method | Description |
|--------|-------------|
| `obj:get_current_outfit()` | Currently equipped outfit `game_object` |
| `obj:get_current_outfit_protection(hit_type)` | Protection value for a given hit type |
| `obj:get_additional_max_weight()` | Extra carry capacity from outfit |
| `obj:set_additional_max_weight(v)` | Override extra carry capacity |
| `obj:get_additional_max_walk_weight()` | Extra walk-weight capacity |
| `obj:set_additional_max_walk_weight(v)` | Override extra walk-weight capacity |

---

## Anomaly methods

| Method | Description |
|--------|-------------|
| `obj:get_anomaly_power()` | Current power/intensity |
| `obj:set_anomaly_power(v)` | Override power |
| `obj:get_anomaly_radius()` | Effect radius |
| `obj:set_anomaly_radius(v)` | Override radius |
| `obj:set_anomaly_position(x, y, z)` | Reposition anomaly |
| `obj:enable_anomaly()` | Enable anomaly |
| `obj:disable_anomaly()` | Disable anomaly |

---

## Particles

| Method | Description |
|--------|-------------|
| `obj:start_particles(effect, bone)` | Attach particle effect to a bone |
| `obj:stop_particles(effect, bone)` | Remove particle effect from a bone |

```lua
-- Attach a fire effect to an NPC's torso
npc:start_particles("anomaly\\electra_hit_01", "bip01_spine")
-- Remove it later
npc:stop_particles("anomaly\\electra_hit_01", "bip01_spine")
```

---

## Bones & geometry

| Method | Description |
|--------|-------------|
| `obj:bone_position(bone_name)` | World position of a named bone |
| `obj:get_bone_id(bone_name)` | Numeric bone ID |
| `obj:center()` | World position of the object's centre |
| `obj:inside(pos, radius)` | True if `pos` is within the zone |
| `obj:inside(pos)` | True if `pos` is within the zone (default radius) |
| `obj:mass()` | Physics mass |
| `obj:get_physics_shell()` | Physics shell if one exists |
| `obj:get_physics_object()` | Raw physics object |

---

## Object callbacks

`game_object` supports per-object per-callback registration (distinct from the global callback system). These bind directly to the object:

| Method | Description |
|--------|-------------|
| `obj:set_callback(type, fn)` | Register `fn` for callback `type` |
| `obj:set_callback(type, fn, obj)` | Register with extra `obj` context |
| `obj:set_callback(type)` | Clear callback for `type` |

Use `callback.*` constants for `type`. Example:

```lua
-- React to this specific NPC dying
npc:set_callback(callback.death, function(victim, killer)
    printf("[my_mod] %s was killed by %s", victim:name(), killer and killer:name() or "unknown")
end)
```

---

## Visual & HUD

| Method | Description |
|--------|-------------|
| `obj:get_visual_name()` | Path to current 3D model |
| `obj:set_visual_name(path)` | Change 3D model |
| `obj:set_invisible(bool)` | Toggle object visibility |
| `obj:force_visibility_state(n)` | Force a specific visibility state |
| `obj:get_visibility_state()` | Current visibility state |
| `obj:night_vision_enabled()` | True if NV is active |
| `obj:enable_night_vision(bool)` | Toggle NV on NPC |
| `obj:play_cycle(anim)` | Loop a named animation |
| `obj:play_cycle(anim, mix)` | Loop with blending |
| `obj:add_animation(anim, mix, bool)` | Queue a one-shot animation |
| `obj:clear_animations()` | Stop all queued animations |
| `obj:animation_count()` | Number of queued animations |
| `obj:animation_slot()` | Animation slot index |
| `obj:set_tip_text(text)` | Override use-hint text |
| `obj:set_tip_text_default()` | Reset use-hint to config default |
| `obj:set_nonscript_usable(bool)` | Whether the use key triggers a callback |
| `obj:info_add(text)` | Add debug text overlay |
| `obj:info_clear()` | Clear debug text overlay |

---

## Miscellaneous

| Method | Description |
|--------|-------------|
| `obj:bind_object(binder)` | Attach an object_binder instance |
| `obj:binded_object()` | Get the bound object_binder |
| `obj:spawn_ini()` | `ini_file` for the object's spawn config |
| `obj:get_script_name()` | Active scheme script name |
| `obj:accessible(pos)` | True if `pos` is reachable |
| `obj:accessible(lvid)` | True if navmesh node is reachable |
| `obj:accessible_nearest(pos, out)` | Nearest accessible position to `pos` |
| `obj:team()` | Team index |
| `obj:squad()` | Squad index |
| `obj:group()` | Group index |
| `obj:change_team(team, squad, group)` | Change team assignment |
| `obj:get_corpse()` | Carried corpse if any |
| `obj:get_enemy_strength()` | Threat level of current enemy |
| `obj:sight_params()` | Current `CSightParams` |
| `obj:set_sight(...)` | Override sight target (many overloads) |
| `obj:head_orientation()` | Current head rotation |
| `obj:add_restrictions(in_restr, out_restr)` | Add zone restrictions |
| `obj:remove_restrictions(in_restr, out_restr)` | Remove zone restrictions |
| `obj:in_restrictions()` | Current in-restriction list |
| `obj:out_restrictions()` | Current out-restriction list |
| `obj:remove_all_restrictions()` | Clear all restrictions |
| `obj:in_smart_cover()` | True if NPC is in smart cover |
| `obj:get_dest_smart_cover_name()` | Target smart cover name |
| `obj:get_smart_cover_description()` | Current smart cover description |
| `obj:get_dest_smart_cover()` | Target smart cover object |
| `obj:set_dest_smart_cover(name)` | Set target smart cover |
| `obj:is_body_turning()` | True while turning body |
| `obj:path_type()` | Current path type |
| `obj:detail_path_type()` | Detail path type |

---

## Class casting

Several engine classes extend `game_object` with extra methods. To access them, cast the object:

| Method | Gives access to… |
|--------|----------------|
| `obj:cast_Actor()` | `CActor` — player-specific methods |
| `obj:cast_Weapon()` | `CWeapon` — weapon methods |
| `obj:cast_WeaponMagazined()` | `CWeaponMagazined` |
| `obj:cast_WeaponMagazinedWGrenade()` | `CWeaponMagazinedWGrenade` |
| `obj:cast_CustomOutfit()` | `CCustomOutfit` |
| `obj:cast_Helmet()` | `CHelmet` |
| `obj:cast_Artefact()` | `CArtefact` |
| `obj:cast_Ammo()` | `CAmmo` |
| `obj:cast_EatableItem()` | `CEatableItem` |
| `obj:cast_Medkit()` | `CMedkit` |
| `obj:cast_Antirad()` | `CAntirad` |
| `obj:cast_FoodItem()` | `CFoodItem` |
| `obj:cast_BottleItem()` | `CBottleItem` |
| `obj:cast_InventoryOwner()` | `CInventoryOwner` |
| `obj:cast_InventoryBox()` | `CInventoryBox` |
| `obj:cast_CustomZone()` | `CCustomZone` |
| `obj:cast_TorridZone()` | `CTorridZone` |
| `obj:cast_MosquitoBald()` | `CMosquitoBald` |
| `obj:cast_ZoneCampfire()` | `CZoneCampfire` |
| `obj:cast_Car()` | `CCar` |
| `obj:cast_Heli()` | `CHelicopter` |

Returns the cast object on success, or `nil` if the object is not of that type.

```lua
local outfit = db.actor:get_current_outfit()
if outfit then
    local co = outfit:cast_CustomOutfit()
    if co then
        -- access CCustomOutfit-specific methods
    end
end
```

---

## See also

- [db.actor](actor.md) — actor-specific methods (satiety, psy, goodwill, etc.)
- [hit](hit.md) — hit object for applying damage
- [alife](alife.md) — server-side entity API (`se_abstract` and subclasses)
- [Scripting: What is a game_object?](../scripting/game-object.md) — conceptual overview
- [Object Binders](../scripting/object-binders.md) — per-object Lua state
