# Example: MCM Options

A reference implementation showing every common MCM option type, correct defaults handling, and the `on_option_change` pattern. Use this as a starting template for any mod that exposes settings.

---

## What this covers

- All standard MCM control types: checkbox, slider, dropdown, keybind, text input
- Organising options into collapsible sections
- Providing defaults that work when MCM is not installed
- Reacting to setting changes at runtime

---

## Files

```
gamedata/
  scripts/
    my_full_mod.script
    my_full_mod_mcm.script
  configs/
    text/
      eng/
        ui_st_my_full_mod.xml
```

---

## my_full_mod_mcm.script

```lua
function on_mcm_load()
    return {
        id = "my_full_mod",
        sh = true,
        gr = {
            -- ─── Header banner ────────────────────────────────────
            {
                id      = "banner",
                type    = "slide",
                text    = "ui_mcm_my_full_mod",
                link    = "ui_options_slider_player",
                size    = {512, 50},
                spacing = 20,
            },

            -- ─── General settings section ─────────────────────────
            {
                id = "general",
                sh = true,
                gr = {
                    {id = "title_general", type = "title", text = "ui_mcm_my_full_mod_general"},

                    -- Checkbox: simple boolean toggle
                    {
                        id   = "enable",
                        type = "check",
                        val  = 1,
                        def  = true,
                        text = "ui_mcm_my_full_mod_enable",
                    },

                    -- Slider: numeric value with min/max/step
                    {
                        id   = "intensity",
                        type = "track",
                        val  = 2,
                        min  = 0.0,
                        max  = 2.0,
                        step = 0.1,
                        def  = 1.0,
                        text = "ui_mcm_my_full_mod_intensity",
                    },

                    -- Dropdown list
                    {
                        id      = "mode",
                        type    = "list",
                        val     = 2,
                        def     = 0,
                        text    = "ui_mcm_my_full_mod_mode",
                        content = {
                            {0, "ui_mcm_my_full_mod_mode_off"},
                            {1, "ui_mcm_my_full_mod_mode_low"},
                            {2, "ui_mcm_my_full_mod_mode_medium"},
                            {3, "ui_mcm_my_full_mod_mode_high"},
                        },
                    },
                },
            },

            -- ─── Advanced settings section ────────────────────────
            {
                id = "advanced",
                sh = true,
                gr = {
                    {id = "title_advanced", type = "title", text = "ui_mcm_my_full_mod_advanced"},

                    -- Another checkbox
                    {
                        id   = "debug_log",
                        type = "check",
                        val  = 1,
                        def  = false,
                        text = "ui_mcm_my_full_mod_debug",
                    },

                    -- Text input
                    {
                        id   = "custom_label",
                        type = "input",
                        val  = 0,
                        def  = "Stalker",
                        text = "ui_mcm_my_full_mod_label",
                    },

                    {id = "divider", type = "line"},

                    -- Description block (non-interactive)
                    {
                        id   = "help_text",
                        type = "desc",
                        text = "ui_mcm_my_full_mod_help",
                        clr  = {255, 150, 150, 150},
                    },
                },
            },

            -- ─── Keybinds section ─────────────────────────────────
            {
                id = "keybinds",
                sh = true,
                gr = {
                    {id = "title_keys", type = "title", text = "ui_mcm_my_full_mod_keybinds"},

                    {
                        id   = "hotkey_main",
                        type = "key_bind",
                        val  = 2,
                        def  = DIK_keys.DIK_F7,
                        text = "ui_mcm_my_full_mod_hotkey_main",
                    },

                    {
                        id   = "hotkey_toggle",
                        type = "key_bind",
                        val  = 2,
                        def  = DIK_keys.DIK_F8,
                        text = "ui_mcm_my_full_mod_hotkey_toggle",
                    },
                },
            },
        }
    }
end
```

---

## my_full_mod.script

```lua
-- ─────────────────────────────────────────────────────────────
-- Defaults (used when MCM isn't installed)
-- ─────────────────────────────────────────────────────────────

local defaults = {
    enable        = true,
    intensity     = 1.0,
    mode          = 0,
    debug_log     = false,
    custom_label  = "Stalker",
    hotkey_main   = DIK_keys.DIK_F7,
    hotkey_toggle = DIK_keys.DIK_F8,
}

-- ─────────────────────────────────────────────────────────────
-- Settings accessor
-- ─────────────────────────────────────────────────────────────

local function cfg(key)
    if ui_mcm then
        local v = ui_mcm.get("my_full_mod/" .. key)
        return v ~= nil and v or defaults[key]
    end
    return defaults[key]
end

-- For nested paths (general/enable, keybinds/hotkey_main, etc.)
local function cfg_path(path)
    if ui_mcm then
        local v = ui_mcm.get("my_full_mod/" .. path)
        -- Extract the key after the last /
        local key = path:match("[^/]+$")
        return v ~= nil and v or defaults[key]
    end
    local key = path:match("[^/]+$")
    return defaults[key]
end

-- ─────────────────────────────────────────────────────────────
-- Runtime state updated from settings
-- ─────────────────────────────────────────────────────────────

local is_enabled   = true
local active_mode  = 0
local debug_mode   = false

local function apply_settings()
    is_enabled  = cfg_path("general/enable")
    active_mode = cfg_path("general/mode")
    debug_mode  = cfg_path("advanced/debug_log")

    if debug_mode then
        printf("[my_full_mod] settings applied: enable=%s mode=%s intensity=%.2f",
            tostring(is_enabled),
            tostring(active_mode),
            cfg_path("general/intensity")
        )
    end
end

-- ─────────────────────────────────────────────────────────────
-- Key handlers
-- ─────────────────────────────────────────────────────────────

local function on_key_press(key)
    if not is_enabled then return end
    if not actor_menu.is_hud_free() then return end

    if key == cfg_path("keybinds/hotkey_main") then
        do_main_action()
    elseif key == cfg_path("keybinds/hotkey_toggle") then
        toggle_feature()
    end
end

function do_main_action()
    local intensity = cfg_path("general/intensity")
    local label     = cfg_path("advanced/custom_label")
    local msg = string.format("Hello, %s! Intensity: %.1f", label, intensity)
    actor_menu.set_msg(1, msg, 4)
end

function toggle_feature()
    -- override local enable independently of MCM
    is_enabled = not is_enabled
    local key = is_enabled and "my_full_mod_on" or "my_full_mod_off"
    actor_menu.set_msg(1, game.translate_string(key), 3)
end

-- ─────────────────────────────────────────────────────────────
-- Option change callback
-- ─────────────────────────────────────────────────────────────

local function on_option_change()
    apply_settings()
end

-- ─────────────────────────────────────────────────────────────
-- Lifecycle
-- ─────────────────────────────────────────────────────────────

function on_game_start()
    RegisterScriptCallback("on_key_press",    on_key_press)
    RegisterScriptCallback("on_option_change", on_option_change)

    -- Apply settings immediately so defaults take effect without MCM
    apply_settings()
end

function on_game_end()
    UnregisterScriptCallback("on_key_press",    on_key_press)
    UnregisterScriptCallback("on_option_change", on_option_change)
end
```

---

## ui_st_my_full_mod.xml

```xml
<?xml version="1.0" encoding="windows-1251"?>
<string_table>
    <string id="ui_mcm_my_full_mod"><text>My Full Mod</text></string>

    <!-- General section -->
    <string id="ui_mcm_my_full_mod_general"><text>General</text></string>
    <string id="ui_mcm_my_full_mod_enable"><text>Enable mod</text></string>
    <string id="ui_mcm_my_full_mod_intensity"><text>Effect intensity</text></string>
    <string id="ui_mcm_my_full_mod_mode"><text>Operating mode</text></string>
    <string id="ui_mcm_my_full_mod_mode_off"><text>Off</text></string>
    <string id="ui_mcm_my_full_mod_mode_low"><text>Low</text></string>
    <string id="ui_mcm_my_full_mod_mode_medium"><text>Medium</text></string>
    <string id="ui_mcm_my_full_mod_mode_high"><text>High</text></string>

    <!-- Advanced section -->
    <string id="ui_mcm_my_full_mod_advanced"><text>Advanced</text></string>
    <string id="ui_mcm_my_full_mod_debug"><text>Enable debug logging</text></string>
    <string id="ui_mcm_my_full_mod_label"><text>Display name</text></string>
    <string id="ui_mcm_my_full_mod_help">
        <text>Changes take effect immediately after saving MCM settings.</text>
    </string>

    <!-- Keybinds section -->
    <string id="ui_mcm_my_full_mod_keybinds"><text>Keybinds</text></string>
    <string id="ui_mcm_my_full_mod_hotkey_main"><text>Main action key</text></string>
    <string id="ui_mcm_my_full_mod_hotkey_toggle"><text>Toggle key</text></string>

    <!-- Runtime strings -->
    <string id="my_full_mod_on"><text>Feature enabled.</text></string>
    <string id="my_full_mod_off"><text>Feature disabled.</text></string>
</string_table>
```

---

## Key decisions explained

**Nested MCM paths.** When you use nested `gr` sections with their own `id`, the MCM key path includes each level: `"my_full_mod/general/enable"`. The `cfg_path` helper in the script above handles this, but you can also use `cfg` with top-level keys if you keep all options flat.

**`apply_settings()` on startup.** Calling `apply_settings()` inside `on_game_start` means the mod reads its settings immediately — before the player ever opens the MCM menu. Without this, settings would only take effect after the first `on_option_change` fires.

**`defaults` table.** Every setting has a matching entry in `defaults`. The `cfg` / `cfg_path` function falls back to `defaults[key]` when MCM is nil or when the MCM value is nil (which happens for new keys on first load after an update).

**Boolean `nil` check in `cfg`.** The pattern `v ~= nil and v or defaults[key]` handles the case where `v` is `false` — a plain `v or default` would return the default for `false`, which is wrong for checkboxes.
