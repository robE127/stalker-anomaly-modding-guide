# Items & Inventory

This page covers how to work with items and the inventory system from script — spawning items, reacting to inventory events, reading item properties, and checking item types.

---

## Item callbacks

Register these in `on_game_start` to react to inventory events.

### actor_on_item_take

Fires after the actor picks up an item.

```lua
local function actor_on_item_take(item)
    local sec = item:section()
    printf("[my_mod] picked up: %s", sec)

    if sec == "my_quest_item" then
        db.actor:give_info_portion("my_mod_got_quest_item")
    end
end

function on_game_start()
    RegisterScriptCallback("actor_on_item_take", actor_on_item_take)
end
```

### actor_on_item_drop

Fires after the actor drops an item.

```lua
local function actor_on_item_drop(item)
    printf("[my_mod] dropped: %s", item:section())
end
```

### actor_on_item_use

Fires after the actor uses (consumes) an item.

```lua
local function actor_on_item_use(item, section)
    -- 'section' is the item's config section name
    local boost_time = ini_sys:r_float_ex(section, "boost_time") or 0
    printf("[my_mod] used %s (boost time: %s)", section, boost_time)
end
```

### actor_on_item_before_use

Fires before consumption — returning `false` via `flags` cancels the use.

```lua
local function actor_on_item_before_use(item, flags)
    if item:section() == "vodka" and my_mod_data.no_alcohol then
        flags.ret_value = false  -- block the use
        actor_menu.set_msg(1, "Can't drink right now.", 3)
    end
end
```

### actor_on_item_before_pickup

Fires before pickup — set `flags.ret_value = false` to block it.

```lua
local function actor_on_item_before_pickup(item, flags)
    if IsArtefact(item) and my_mod_data.artefact_locked then
        flags.ret_value = false
    end
end
```

### actor_on_item_take_from_box

Fires when taking an item from a container (stash, dead body).

```lua
local function actor_on_item_take_from_box(box, item)
    printf("[my_mod] looted %s from container %s", item:section(), box:name())
end
```

### actor_item_to_ruck / actor_item_to_slot

Fires when an item moves between belt and backpack.

```lua
local function actor_item_to_ruck(item)
    -- item moved to backpack
end

local function actor_item_to_slot(item)
    -- item moved to belt/slot
end
```

---

## Inventory drag & drop

`ActorMenu_on_item_drag_drop` fires when the player drags an item in the inventory UI.

```lua
local function ActorMenu_on_item_drag_drop(item1, item2, from_slot, to_slot)
    -- item1 = dragged item, item2 = target item (may be nil)
    -- from_slot and to_slot are EDDListType values
    if to_slot == EDDListType.iActorSlot then
        -- item was equipped
    end
end
```

Slot type constants (`EDDListType`):

| Constant | Meaning |
|----------|---------|
| `iActorSlot` | Equipped slot |
| `iActorBag` | Backpack |
| `iActorBelt` | Belt |
| `iDeadBodyBag` | Dead body inventory |
| `iActorTrade` | Actor trade panel |
| `iPartnerTradeBag` | NPC's trade inventory |

---

## Spawning items

### Give an item to the player

```lua
-- Immediately adds to actor inventory
alife_create_item("bandage", db.actor)

-- With specific condition and uses
alife_create_item("vodka", db.actor, {cond = 0.9, uses = 2})
```

### Spawn at a world position

```lua
local pos  = db.actor:position()
local lvid = db.actor:level_vertex_id()
local gvid = db.actor:game_vertex_id()
alife_create_item("ammo_9x18_fmj", {pos, lvid, gvid})
```

### Give to an NPC

```lua
-- npc is a game_object
alife_create_item("wpn_pm", npc_game_object)
```

See the [alife](../api-reference/alife.md) page for the full `alife_create_item` signature.

---

## Checking item types

Use the global type-check functions from `_g.script`:

```lua
IsWeapon(obj)        -- is it a weapon?
IsAmmo(obj)          -- is it ammunition?
IsGrenade(obj)       -- is it a grenade?
IsArtefact(obj)      -- is it an artefact?
IsBolt(obj)          -- is it a crossbow bolt?
IsStalker(obj)       -- is it a humanoid NPC?
IsMonster(obj)       -- is it a creature?

-- IsItem with a type string
IsItem("eatable",   nil, obj)   -- food or drink
IsItem("weapon",    nil, obj)   -- weapon
IsItem("outfit",    nil, obj)   -- armour/suit
IsItem("helmet",    nil, obj)   -- helmet
IsItem("backpack",  nil, obj)   -- backpack
IsItem("artefact",  nil, obj)   -- artefact
IsItem("device",    nil, obj)   -- detector, torch, etc.
IsItem("tool",      nil, obj)   -- tools
IsItem("ammo",      nil, obj)   -- ammunition
IsItem("quest",     nil, obj)   -- quest item
```

You can also check by class ID directly:

```lua
local cls = obj:clsid()
if cls == clsid.wpn_ak74 then ... end
if cls == clsid.eatable_item then ... end
```

---

## Reading item properties from config

Every item's stats live in its `.ltx` config section. Access them via `ini_sys` (the merged system ini):

```lua
local sec = item:section()   -- e.g. "bandage", "vodka", "wpn_ak74"

-- Read config values
local name_key  = ini_sys:r_string_ex(sec, "inv_name")       -- inventory name key
local weight    = ini_sys:r_float_ex(sec, "inv_weight")      -- kg
local cost      = ini_sys:r_float_ex(sec, "cost")            -- roubles
local max_uses  = ini_sys:r_float_ex(sec, "max_uses")        -- multiuse count
local boost_t   = ini_sys:r_float_ex(sec, "boost_time")      -- effect duration (s)
local kind      = ini_sys:r_string_ex(sec, "kind")           -- e.g. "i_food", "i_drink"
local use_cond  = ini_sys:r_bool_ex(sec, "use_condition")    -- has durability?

-- Consumable effects
local eat_health   = ini_sys:r_float_ex(sec, "eat_health")
local eat_satiety  = ini_sys:r_float_ex(sec, "eat_satiety")
local eat_alcohol  = ini_sys:r_float_ex(sec, "eat_alcohol")
local eat_rad      = ini_sys:r_float_ex(sec, "boost_radiation_restore")
```

The `_ex` variants return `nil` instead of erroring when the field doesn't exist.

**Get the display name:**

```lua
local function get_item_name(section)
    local key = ini_sys:r_string_ex(section, "inv_name") or section
    return game.translate_string(key)
end

local name = get_item_name(item:section())
```

---

## Item condition and uses

```lua
local cond = item:condition()   -- 0.0 (broken) to 1.0 (perfect)

-- Remaining uses for multiuse items
local uses_left = item:get_remaining_uses and item:get_remaining_uses() or 1
```

---

## Weapon-specific utilities

`utils_item` provides helpers for weapon data:

```lua
-- Compatible ammo for a weapon
local ammo_list = utils_item.get_ammo("wpn_ak74", item:id())
for _, ammo_sec in ipairs(ammo_list) do
    printf("compatible: %s", ammo_sec)
end

-- Read a weapon stat (respects installed upgrades)
local dispersion = utils_item.get_param("wpn_ak74", item:id(), "fire_dispersion_base", "float", true)
local hit_power  = utils_item.get_param("wpn_ak74", item:id(), "hit_power", "float", true)

-- Check attached addons
if utils_item.addon_attached(weapon_obj, "sc") then
    -- scope attached
end
if utils_item.addon_attached(weapon_obj, "sl") then
    -- silencer attached
end
if utils_item.addon_attached(weapon_obj, "gl") then
    -- grenade launcher attached
end
```

---

## Common patterns

### Count items of a type in inventory

```lua
local function count_items(section)
    local n = 0
    db.actor:iterate_inventory(function(_, obj)
        if obj:section() == section then n = n + 1 end
    end, nil)
    return n
end
```

### Remove one item of a section

```lua
local function take_item(section)
    local found
    db.actor:iterate_inventory(function(_, obj)
        if not found and obj:section() == section then
            found = obj
        end
    end, nil)
    if found then
        alife_release(found)
        return true
    end
    return false
end
```

### React to using a specific item

```lua
local function actor_on_item_use(item, sec)
    if sec == "my_special_item" then
        do_special_effect()
        actor_menu.set_msg(1, game.translate_string("my_mod_item_used"), 4)
    end
end
```

### Give a quest item once

```lua
local function give_quest_item_once()
    if db.actor:has_info("my_mod_item_given") then return end
    alife_create_item("my_quest_item", db.actor)
    db.actor:give_info_portion("my_mod_item_given")
end
```
