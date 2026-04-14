# Callbacks Reference

A complete reference for every known callback in S.T.A.L.K.E.R. Anomaly, sorted by category. Frequencies shown are occurrence counts across 50 analyzed repositories including the base game scripts.

!!! note "Work in progress"
    Signatures and descriptions are being filled in. The callback names and frequencies are accurate.

---

## How to use this reference

Register any callback with:
```lua
RegisterScriptCallback("callback_name", your_function)
```

Unregister (do this in `on_game_end` or when cleaning up):
```lua
UnregisterScriptCallback("callback_name", your_function)
```

---

## Core game flow

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `actor_on_first_update` | 187 | `()` | Fires once on the first simulation tick. The earliest point where `db.actor` is guaranteed non-nil. Use for one-time initialization. |
| `on_game_load` | 107 | `()` | Fires after loading a save file. Fires after `load_state`. |
| `save_state` | 198 | `(m_data: table)` | Write your mod's persistent data into `m_data`. |
| `load_state` | 181 | `(m_data: table)` | Read your mod's persistent data from `m_data`. |
| `actor_on_update` | 147 | `()` | Fires every simulation tick while the actor is active. Keep this fast. |
| `on_option_change` | 121 | `()` | MCM settings were saved. Re-read your `ui_mcm.get` values here. |

---

## Input

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `on_key_press` | 80 | `(key: number)` | A key was pressed. `key` is a `DIK_*` constant. |
| `on_key_release` | 64 | `(key: number)` | A key was released. |
| `on_before_key_press` | 15 | `(key: number, bind: number, flags: table)` | Fires before `on_key_press`. Set `flags.ret = true` to suppress the keypress. |
| `on_console_execute` | 20 | `(cmd: string)` | A console command was executed. |

---

## Inventory & items

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `actor_on_item_use` | 58 | `(obj: game_object)` | Player used a consumable item. |
| `actor_on_item_take` | 39 | `(obj: game_object)` | Player picked up an item. |
| `actor_on_item_drop` | 34 | `(obj: game_object)` | Player dropped an item. |
| `actor_item_to_ruck` | 27 | `(obj: game_object)` | Item moved from belt/slot to backpack. |
| `actor_item_to_slot` | 25 | `(obj: game_object)` | Item moved from backpack to slot/belt. |
| `ActorMenu_on_item_drag_drop` | 26 | `(obj, from, to, from_slot, to_slot)` | Item dragged in inventory UI. |
| `ActorMenu_on_item_focus_receive` | 20 | `(obj: game_object)` | Mouse hovered over an inventory item. |

---

## Combat & health

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `actor_on_before_hit` | 32 | `(shit: hit, bone_id: number)` | Fires before the actor takes a hit. Modify `shit` to change damage. |
| `actor_on_before_death` | 29 | `(shit: hit, bone_id: number)` | Fires just before the actor dies. |
| `npc_on_death_callback` | 41 | `(victim: game_object, who: game_object)` | An NPC was killed. |
| `npc_on_before_hit` | 23 | `(npc, shit, bone_id)` | An NPC is about to be hit. |
| `actor_on_weapon_fired` | 22 | `(obj, wpn, ammo_elapsed, grenade, bone_id, direction, parent_id)` | Player fired a weapon. |
| `actor_on_weapon_zoom_in` | 23 | `(obj: game_object)` | Player aimed down sights. |
| `actor_on_weapon_zoom_out` | 20 | `(obj: game_object)` | Player stopped aiming. |

---

## World & simulation

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `server_entity_on_unregister` | 32 | `(obj, type)` | An entity was removed from the A-Life simulation. |
| `actor_on_net_destroy` | 29 | `(obj: game_object)` | The actor's client-side object was destroyed (level transition or death). |
| `actor_on_sleep` | 22 | `(hours: number)` | Player slept. `hours` is how many hours passed. |

---

## UI

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `GUI_on_show` | 31 | `(name: string, path: string)` | A UI window was opened. `name` is the class name, `path` is the XML path. |
| `GUI_on_hide` | 23 | `(name: string, path: string)` | A UI window was closed. |

---

## Config & XML

| Callback | Freq | Signature | Description |
|----------|------|-----------|-------------|
| `on_xml_read` | 36 | `(path: string, xml_obj: CScriptXmlInit)` | The engine is reading an XML file. Used for DXML patching. |
| `on_localization_change` | 24 | `()` | The player changed their language setting. |
