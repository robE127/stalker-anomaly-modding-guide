# db.actor

!!! note "Work in progress"
    This page is being written. Content coming soon.

`db.actor` is the Lua representation of the player character. It is a `game_object` userdata value exposed by the engine.

!!! warning "Availability"
    `db.actor` is `nil` until the first update tick. Never access it at script load time or in `on_game_load`. Use `actor_on_first_update` to safely initialize anything that depends on it.

## Topics to cover

- Checking `db.actor` is not nil before use
- Inventory access: `db.actor:object(section)`, `db.actor:item_in_slot(slot_id)`, `db.actor:iterate_inventory(fn, arg)`
- Position and movement: `db.actor:position()`, `db.actor:direction()`
- Health and condition: `db.actor:health`, radiation, bleeding, psy
- Info portions (quest flags): `db.actor:give_info_portion(id)`, `db.actor:has_info(id)`, `db.actor:disable_info_portion(id)`
- Money: `db.actor:money()`, `db.actor:give_money(amount)`, `db.actor:give_money(-amount)` to take
- Active weapon: `db.actor:active_item()`
- Rank and reputation
- Relation to NPC factions
- The `game_object` base methods available on all objects (`id()`, `name()`, `section()`, `position()`, etc.)

## Common patterns

```lua
-- Safe actor access pattern
local function do_something_with_actor()
    if not db.actor then return end
    -- ... safe to use db.actor here
end

-- Iterate inventory to find all items of a section
local function find_all(section)
    local found = {}
    db.actor:iterate_inventory(function(temp, obj)
        if obj:section() == section then
            found[#found + 1] = obj
        end
    end, nil)
    return found
end
```
