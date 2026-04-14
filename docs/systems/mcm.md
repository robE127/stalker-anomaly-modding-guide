# Mod Configuration Menu (MCM)

MCM is a community-standard settings system that gives mods a UI accessible from the ESC menu and main menu. Nearly every feature mod uses it — `ui_mcm.get` appears in 323 places across the analyzed repos, and `on_option_change` in 121.

MCM is distributed as a standalone mod. It ships with major modpacks (GAMMA, EFP, etc.) but is not bundled with base Anomaly. Your mod must handle the case where it isn't installed.

---

## How MCM works

MCM scans for files ending in `_mcm.script` at startup and calls `on_mcm_load()` in each. Your function returns a table describing your mod's options. MCM builds the UI from that table and persists the values.

When the player changes and saves settings, MCM fires the `on_option_change` callback in all scripts.

---

## File naming

MCM requires a dedicated file named `yourmod_mcm.script`. The `_mcm.script` suffix is what MCM uses to find registrations.

```
gamedata/
  scripts/
    my_mod.script          ← main logic
    my_mod_mcm.script      ← MCM registration (required name pattern)
```

---

## Minimal registration

```lua
-- my_mod_mcm.script

function on_mcm_load()
    return {
        id = "my_mod",   -- unique identifier for your mod
        sh = true,       -- true = collapsible section header
        gr = {
            {
                id      = "enable",
                type    = "check",
                val     = 1,
                def     = true,
                text    = "ui_mcm_my_mod_enable",
            },
        }
    }
end
```

---

## Reading settings

```lua
-- ui_mcm.get("mod_id/setting_id")
local enabled = ui_mcm.get("my_mod/enable")
```

Always guard against MCM not being installed, and provide defaults:

```lua
-- my_mod.script

local defaults = {
    enable    = true,
    intensity = 0.5,
    hotkey    = DIK_keys.DIK_F7,
}

local function cfg(key)
    if ui_mcm then
        local v = ui_mcm.get("my_mod/" .. key)
        return v ~= nil and v or defaults[key]
    end
    return defaults[key]
end

-- Usage
if cfg("enable") then
    -- feature is on
end
```

---

## Reacting to changes

Register `on_option_change` to react when the player saves new settings:

```lua
-- my_mod.script

local function on_option_change()
    -- Re-read settings and update runtime state
    local enabled = cfg("enable")
    if enabled then
        RegisterScriptCallback("actor_on_update", my_update)
    else
        UnregisterScriptCallback("actor_on_update", my_update)
    end
end

function on_game_start()
    RegisterScriptCallback("on_option_change", on_option_change)
    on_option_change()  -- Apply settings immediately on game start
end

function on_game_end()
    UnregisterScriptCallback("on_option_change", on_option_change)
end
```

Calling `on_option_change()` at startup ensures your mod initialises correctly even before the player touches the settings menu.

---

## Option types

### check — boolean toggle

```lua
{
    id   = "enable",
    type = "check",
    val  = 1,       -- 1 = boolean value type
    def  = true,    -- default value
    text = "ui_mcm_my_mod_enable",  -- localization key
}
```

Returns `true` or `false`.

### track — numeric slider

```lua
{
    id   = "intensity",
    type = "track",
    val  = 2,      -- 2 = numeric value type
    min  = 0,
    max  = 1,
    step = 0.05,
    def  = 0.5,
    text = "ui_mcm_my_mod_intensity",
}
```

Returns a number between `min` and `max`.

### list — dropdown

```lua
{
    id      = "mode",
    type    = "list",
    val     = 2,
    def     = 0,
    text    = "ui_mcm_my_mod_mode",
    content = {
        {0, "ui_mcm_my_mod_mode_off"},
        {1, "ui_mcm_my_mod_mode_low"},
        {2, "ui_mcm_my_mod_mode_high"},
    },
}
```

`content` is an array of `{value, localization_key}` pairs. Returns the numeric value of the selected entry.

### key_bind — hotkey

```lua
{
    id   = "hotkey",
    type = "key_bind",
    val  = 2,
    def  = DIK_keys.DIK_F7,
    text = "ui_mcm_my_mod_hotkey",
}
```

Returns a DIK key code. Use with `on_key_press`:

```lua
local function on_key_press(key)
    if key == cfg("hotkey") then
        -- trigger action
    end
end
```

### input — text field

```lua
{
    id   = "label",
    type = "input",
    val  = 0,      -- 0 = string value type
    def  = "default text",
    text = "ui_mcm_my_mod_label",
}
```

Returns a string.

---

## Layout controls

These items don't store values — they organise the settings UI visually.

### slide — section banner/header image

```lua
{
    id      = "banner",
    type    = "slide",
    text    = "ui_mcm_my_mod_title",
    link    = "ui_options_slider_player",  -- style reference
    size    = {512, 50},
    spacing = 20,
}
```

### title — plain text heading

```lua
{id = "section_title", type = "title", text = "ui_mcm_my_mod_section"}
```

### line — horizontal divider

```lua
{id = "divider", type = "line"}
```

### desc — descriptive text block

```lua
{
    id   = "help_text",
    type = "desc",
    text = "ui_mcm_my_mod_help",
    clr  = {255, 200, 200, 200},  -- ARGB color
}
```

---

## Grouping and nesting

Wrap related options in a sub-table with its own `gr` array. Set `sh = true` to make it collapsible:

```lua
function on_mcm_load()
    return {
        id = "my_mod",
        sh = true,
        gr = {
            -- Banner for the whole mod
            {id = "banner", type = "slide", text = "ui_mcm_my_mod", link = "ui_options_slider_player", size = {512, 50}, spacing = 20},

            -- General section
            {
                id = "general",
                sh = true,
                gr = {
                    {id = "general_title", type = "title", text = "ui_mcm_my_mod_general"},
                    {id = "enable",    type = "check", val = 1, def = true,  text = "ui_mcm_my_mod_enable"},
                    {id = "intensity", type = "track", val = 2, min = 0, max = 1, step = 0.05, def = 0.5, text = "ui_mcm_my_mod_intensity"},
                },
            },

            -- Keybinds section
            {
                id = "keys",
                sh = true,
                gr = {
                    {id = "keys_title", type = "title", text = "ui_mcm_my_mod_keybinds"},
                    {id = "hotkey",  type = "key_bind", val = 2, def = DIK_keys.DIK_F7, text = "ui_mcm_my_mod_hotkey"},
                },
            },
        }
    }
end
```

For nested settings, the path includes each level:

```lua
ui_mcm.get("my_mod/general/enable")
ui_mcm.get("my_mod/general/intensity")
ui_mcm.get("my_mod/keys/hotkey")
```

---

## Localization keys

All `text` values in MCM tables are localization keys. Define them in your mod's text XML:

```xml
<!-- gamedata/configs/text/eng/ui_st_my_mod.xml -->
<string_table>
    <string id="ui_mcm_my_mod_enable">
        <text>Enable My Mod</text>
    </string>
    <string id="ui_mcm_my_mod_intensity">
        <text>Effect Intensity</text>
    </string>
    <string id="ui_mcm_my_mod_hotkey">
        <text>Activation Key</text>
    </string>
</string_table>
```

---

## Complete example

Two files — the MCM registration and the main mod logic:

```lua
-- my_mod_mcm.script

function on_mcm_load()
    return {
        id = "my_mod",
        sh = true,
        gr = {
            {id = "banner",    type = "slide",  text = "ui_mcm_my_mod",           link = "ui_options_slider_player", size = {512, 50}, spacing = 20},
            {id = "enable",    type = "check",  val = 1, def = true,              text = "ui_mcm_my_mod_enable"},
            {id = "intensity", type = "track",  val = 2, min = 0, max = 1, step = 0.05, def = 0.5, text = "ui_mcm_my_mod_intensity"},
            {id = "hotkey",    type = "key_bind", val = 2, def = DIK_keys.DIK_F7, text = "ui_mcm_my_mod_hotkey"},
        }
    }
end
```

```lua
-- my_mod.script

local defaults = {
    enable    = true,
    intensity = 0.5,
    hotkey    = DIK_keys.DIK_F7,
}

local function cfg(key)
    if ui_mcm then
        local v = ui_mcm.get("my_mod/" .. key)
        return v ~= nil and v or defaults[key]
    end
    return defaults[key]
end

local function on_key_press(key)
    if not cfg("enable") then return end
    if key == cfg("hotkey") then
        do_the_thing(cfg("intensity"))
    end
end

local function on_option_change()
    -- Settings re-read lazily via cfg() — nothing to do here unless
    -- you need to immediately react (e.g. re-register a callback)
end

function on_game_start()
    RegisterScriptCallback("on_key_press",    on_key_press)
    RegisterScriptCallback("on_option_change", on_option_change)
end

function on_game_end()
    UnregisterScriptCallback("on_key_press",    on_key_press)
    UnregisterScriptCallback("on_option_change", on_option_change)
end
```
