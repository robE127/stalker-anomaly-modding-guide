# Example: Keybind Action

A complete mod that triggers an action when the player presses a key — with an optional MCM-configurable hotkey. This is the pattern behind the majority of player-facing script features.

---

## What this builds

- Pressing a key (default `F7`) shows a HUD message and briefly dims the screen
- The key is configurable via MCM if MCM is installed
- Pressing the key is blocked during menus and conversations
- State is saved/loaded correctly across saves

---

## Files

```
gamedata/
  scripts/
    my_keybind_mod.script
    my_keybind_mod_mcm.script
  configs/
    text/
      eng/
        ui_st_my_keybind_mod.xml
```

---

## my_keybind_mod_mcm.script

```lua
function on_mcm_load()
    return {
        id = "my_keybind_mod",
        sh = true,
        gr = {
            {
                id      = "banner",
                type    = "slide",
                text    = "ui_mcm_my_keybind_mod",
                link    = "ui_options_slider_player",
                size    = {512, 50},
                spacing = 20,
            },
            {
                id   = "enable",
                type = "check",
                val  = 1,
                def  = true,
                text = "ui_mcm_my_keybind_mod_enable",
            },
            {
                id   = "hotkey",
                type = "key_bind",
                val  = 2,
                def  = DIK_keys.DIK_F7,
                text = "ui_mcm_my_keybind_mod_hotkey",
            },
        }
    }
end
```

---

## my_keybind_mod.script

```lua
-- ─────────────────────────────────────────────────────────────
-- Config
-- ─────────────────────────────────────────────────────────────

local defaults = {
    enable = true,
    hotkey = DIK_keys.DIK_F7,
}

local function cfg(key)
    if ui_mcm then
        local v = ui_mcm.get("my_keybind_mod/" .. key)
        return v ~= nil and v or defaults[key]
    end
    return defaults[key]
end

-- ─────────────────────────────────────────────────────────────
-- The action
-- ─────────────────────────────────────────────────────────────

local EFFECT_ID = 58391   -- arbitrary unique PP effector ID

local function do_pulse()
    -- Brief screen flash
    level.add_pp_effector("fade_out.ppe", EFFECT_ID, false)

    -- HUD notification
    actor_menu.set_msg(1, game.translate_string("my_keybind_mod_activated"), 3)

    printf("[my_keybind_mod] pulse activated")
end

-- ─────────────────────────────────────────────────────────────
-- Input handler
-- ─────────────────────────────────────────────────────────────

local function on_key_press(key)
    -- Bail out if disabled in settings
    if not cfg("enable") then return end

    -- Match the configured key
    if key ~= cfg("hotkey") then return end

    -- Don't fire during menus or conversations
    if not actor_menu.is_hud_free() then return end
    if db.actor and db.actor:is_talking() then return end

    do_pulse()
end

-- ─────────────────────────────────────────────────────────────
-- Lifecycle
-- ─────────────────────────────────────────────────────────────

function on_game_start()
    RegisterScriptCallback("on_key_press", on_key_press)
end

function on_game_end()
    UnregisterScriptCallback("on_key_press", on_key_press)
end
```

---

## ui_st_my_keybind_mod.xml

```xml
<?xml version="1.0" encoding="windows-1251"?>
<string_table>
    <string id="ui_mcm_my_keybind_mod">
        <text>My Keybind Mod</text>
    </string>
    <string id="ui_mcm_my_keybind_mod_enable">
        <text>Enable mod</text>
    </string>
    <string id="ui_mcm_my_keybind_mod_hotkey">
        <text>Activation key</text>
    </string>
    <string id="my_keybind_mod_activated">
        <text>Pulse activated.</text>
    </string>
</string_table>
```

---

## How it works

**Key detection.** `on_key_press` receives a DIK key code. Comparing it against `cfg("hotkey")` handles both the hardcoded default and any MCM override — because `cfg` returns the MCM value when available and the default otherwise.

**Guard conditions.** The check `actor_menu.is_hud_free()` returns `false` when any menu is open (inventory, PDA, trade). The `is_talking()` check prevents the action during dialogs. Both are good practice for any hotkey action.

**PP effector.** `level.add_pp_effector` takes a file from `gamedata/anims/`, a unique numeric ID, and a loop flag. `false` means play once and remove itself. The ID `58391` is arbitrary — pick a number you're unlikely to clash with (check base game IDs in `_g.script` for values to avoid).

**MCM fallback.** When MCM isn't installed, `ui_mcm` is `nil`, and `cfg` returns `defaults[key]`. The mod works identically with or without MCM.

---

## Common variations

### Toggle state on keypress

```lua
local active = false

local function on_key_press(key)
    if key ~= cfg("hotkey") then return end
    if not actor_menu.is_hud_free() then return end

    active = not active
    local msg = active and "my_mod_enabled" or "my_mod_disabled"
    actor_menu.set_msg(1, game.translate_string(msg), 3)
end
```

### Hold-to-activate

```lua
local held = false

local function on_key_press(key)
    if key == cfg("hotkey") then
        held = true
        begin_held_effect()
    end
end

local function on_key_release(key)
    if key == cfg("hotkey") and held then
        held = false
        end_held_effect()
    end
end

function on_game_start()
    RegisterScriptCallback("on_key_press",   on_key_press)
    RegisterScriptCallback("on_key_release", on_key_release)
end
```

### Cooldown

```lua
local last_used = 0
local COOLDOWN  = 5000  -- ms

local function on_key_press(key)
    if key ~= cfg("hotkey") then return end
    if not actor_menu.is_hud_free() then return end

    local now = game.time()
    if now - last_used < COOLDOWN then
        actor_menu.set_msg(1, "Not ready yet.", 2)
        return
    end

    last_used = now
    do_pulse()
end
```
