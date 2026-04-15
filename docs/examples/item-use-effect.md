# Example: Item Use Effect

A complete mod that triggers a custom effect when the player uses a specific item. Demonstrates the item use callback, reading item config properties, applying effects, and blocking use under certain conditions.

!!! note "Requires the modded exes"
    This example uses `actor_on_item_before_use`, which is dispatched from an engine hook added by the [modded exes](https://github.com/themrdemonized/xray-monolith). The `actor_on_item_use` callback works without them.

---

## What this builds

- When the player uses a specific food or consumable, apply a custom secondary effect
- The effect is applied in addition to (not instead of) the normal item effect
- Optionally block item use if a condition isn't met
- All configurable via MCM

---

## Files

```
gamedata/
  scripts/
    my_item_effect.script
    my_item_effect_mcm.script
  configs/
    text/
      eng/
        ui_st_my_item_effect.xml
```

---

## my_item_effect_mcm.script

```lua
function on_mcm_load()
    return {
        id = "my_item_effect",
        sh = true,
        gr = {
            {
                id      = "banner",
                type    = "slide",
                text    = "ui_mcm_my_item_effect",
                link    = "ui_options_slider_player",
                size    = {512, 50},
                spacing = 20,
            },
            {
                id   = "enable",
                type = "check",
                val  = 1,
                def  = true,
                text = "ui_mcm_my_item_effect_enable",
            },
            {
                id   = "boost_mult",
                type = "track",
                val  = 2,
                min  = 0.5,
                max  = 3.0,
                step = 0.1,
                def  = 1.0,
                text = "ui_mcm_my_item_effect_boost",
            },
        }
    }
end
```

---

## my_item_effect.script

```lua
-- ─────────────────────────────────────────────────────────────
-- Config
-- ─────────────────────────────────────────────────────────────

local defaults = {
    enable     = true,
    boost_mult = 1.0,
}

local function cfg(key)
    if ui_mcm then
        local v = ui_mcm.get("my_item_effect/" .. key)
        return v ~= nil and v or defaults[key]
    end
    return defaults[key]
end

-- ─────────────────────────────────────────────────────────────
-- Which items trigger the effect
-- ─────────────────────────────────────────────────────────────

-- These sections get the extra effect when consumed
local TRIGGER_SECTIONS = {
    vodka             = true,
    vodka_fuel        = true,
    spirit            = true,
}

-- ─────────────────────────────────────────────────────────────
-- The effect
-- ─────────────────────────────────────────────────────────────

local EFFECT_ID = 47291   -- unique PP effector ID for this mod

local function apply_alcohol_effect(mult)
    -- Camera sway
    level.add_cam_effector("camera_effects\\alcohol.anm", EFFECT_ID, true, "", 0, false)

    -- Screen distortion
    level.add_pp_effector("alcohol.ppe", EFFECT_ID, true)
    level.set_pp_effector_factor(EFFECT_ID, math.min(mult, 1.0))

    -- Notification
    actor_menu.set_msg(1, game.translate_string("my_item_effect_drunk"), 4)

    -- Schedule removal after 30 in-game seconds
    clear_time = game.time() + 30000
end

local clear_time = nil

local function actor_on_update()
    if not clear_time then return end
    if game.time() < clear_time then return end

    clear_time = nil
    level.remove_cam_effector(EFFECT_ID)
    level.remove_pp_effector(EFFECT_ID)
end

-- ─────────────────────────────────────────────────────────────
-- Item use callbacks
-- ─────────────────────────────────────────────────────────────

local function actor_on_item_use(item, section)
    if not cfg("enable") then return end
    if not TRIGGER_SECTIONS[section] then return end

    local mult = cfg("boost_mult")
    apply_alcohol_effect(mult)
end

-- Block use if the player is already heavily drunk (effect active)
local function actor_on_item_before_use(item, flags)
    if not cfg("enable") then return end
    if not TRIGGER_SECTIONS[item:section()] then return end

    if clear_time and game.time() < clear_time then
        -- Already drunk — block another drink
        flags.ret_value = false
        actor_menu.set_msg(1, game.translate_string("my_item_effect_too_drunk"), 3)
    end
end

-- ─────────────────────────────────────────────────────────────
-- Save / load
-- ─────────────────────────────────────────────────────────────

local function save_state(m_data)
    m_data.my_item_effect = {
        clear_time = clear_time,
    }
end

local function load_state(m_data)
    local saved = m_data.my_item_effect or {}
    clear_time = saved.clear_time  -- may be nil (first load)

    -- Restore visual effects if still active after load
    if clear_time and game.time() < clear_time then
        local remaining_frac = (clear_time - game.time()) / 30000
        level.add_pp_effector("alcohol.ppe", EFFECT_ID, true)
        level.set_pp_effector_factor(EFFECT_ID, math.min(remaining_frac, 1.0))
    end
end

-- ─────────────────────────────────────────────────────────────
-- Lifecycle
-- ─────────────────────────────────────────────────────────────

function on_game_start()
    RegisterScriptCallback("actor_on_item_use",        actor_on_item_use)
    RegisterScriptCallback("actor_on_item_before_use", actor_on_item_before_use)
    RegisterScriptCallback("actor_on_update",          actor_on_update)
    RegisterScriptCallback("save_state",               save_state)
    RegisterScriptCallback("load_state",               load_state)
end

function on_game_end()
    UnregisterScriptCallback("actor_on_item_use",        actor_on_item_use)
    UnregisterScriptCallback("actor_on_item_before_use", actor_on_item_before_use)
    UnregisterScriptCallback("actor_on_update",          actor_on_update)
    UnregisterScriptCallback("save_state",               save_state)
    UnregisterScriptCallback("load_state",               load_state)
    clear_time = nil
end
```

---

## ui_st_my_item_effect.xml

```xml
<?xml version="1.0" encoding="windows-1251"?>
<string_table>
    <string id="ui_mcm_my_item_effect">
        <text>Item Effect Mod</text>
    </string>
    <string id="ui_mcm_my_item_effect_enable">
        <text>Enable enhanced alcohol effects</text>
    </string>
    <string id="ui_mcm_my_item_effect_boost">
        <text>Effect intensity multiplier</text>
    </string>
    <string id="my_item_effect_drunk">
        <text>The alcohol hits hard...</text>
    </string>
    <string id="my_item_effect_too_drunk">
        <text>You're already too drunk for another drink.</text>
    </string>
</string_table>
```

---

## How it works

**`actor_on_item_use(item, section)`.** The callback receives the item object and its config section name. The section is the key — it's faster and more reliable than checking `item:name()` (which is an instance name, not a type).

**`actor_on_item_before_use(item, flags)`.** This fires _before_ the item is consumed. Setting `flags.ret_value = false` cancels the use — the item stays in inventory. This is used here to implement a "too drunk" block.

**State persistence.** `clear_time` is a game-time timestamp. It's saved to `m_data` and restored on load. After a save/load, `load_state` checks whether the effect is still in-progress and restores the PP effector.

**`actor_on_update`.** Runs every frame. It checks whether `clear_time` has elapsed and cleans up the effectors. This is lightweight — the early returns mean the body rarely executes.

**PP effector ID.** `47291` is arbitrary but must be unique across the game session. Reusing an ID that the base game uses would cause your effector to be removed by base game code (or vice versa).

---

## Variation: read effect strength from item config

Instead of a flat multiplier, read the effect from the item's LTX:

```lua
local function actor_on_item_use(item, section)
    if not cfg("enable") then return end
    if not TRIGGER_SECTIONS[section] then return end

    -- Read the item's alcohol value directly from config
    local base_alcohol = ini_sys:r_float_ex(section, "eat_alcohol") or 0
    if base_alcohol <= 0 then return end

    local mult = base_alcohol * cfg("boost_mult") * 10
    apply_alcohol_effect(math.min(mult, 1.0))
end
```

## Variation: target all food items

Instead of a fixed list, use `IsItem`:

```lua
local function actor_on_item_use(item, section)
    if not cfg("enable") then return end
    if not IsItem("eatable", section) then return end

    -- applies to all food and drink
    apply_satiety_bonus()
end
```
