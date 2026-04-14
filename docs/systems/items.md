# Items & Inventory

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- Item definitions in LTX: required fields (`$spawn`, `class`, `description`, `inv_name`, etc.)
- Item class hierarchy: `CMedkit`, `CFood`, `CWeapon`, `CArtefact`, etc. — what each exposes
- Spawning items: `alife():create(section, pos, lv_id, gv_id, parent_id)` with actor as parent
- `actor_on_item_take` callback — fires when the actor picks up an item
- `actor_on_item_drop` callback — fires when the actor drops an item
- `actor_on_item_use` callback — fires when the actor uses a consumable
- `actor_item_to_ruck` / `actor_item_to_slot` — belt ↔ backpack movement callbacks
- `ActorMenu_on_item_drag_drop` — drag and drop in inventory
- `ActorMenu_on_item_focus_receive` — item hover/focus
- Reading item properties at runtime: `obj:section()`, `ini:r_string("section", "field")`
- The `ui_item` module: `ui_item.get_sec_name(section)` and other display helpers
