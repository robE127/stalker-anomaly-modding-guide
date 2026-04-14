# UI Functions

This page covers the practical scripted UI functions available to mod authors — showing messages, notifications, and reading settings. Full custom UI window development is covered in [Systems: UI Scripting](../systems/ui-scripting.md).

---

## HUD messages — actor_menu

`actor_menu` (from `actor_menu.script`) is the standard way to show in-game text messages.

### actor_menu.set_msg

The most common way to show a quick message on-screen:

```lua
-- actor_menu.set_msg(type, message, duration_seconds, color)
actor_menu.set_msg(1, "You found something.", 3)
actor_menu.set_msg(1, game.translate_string("my_mod_found_item"), 5)

-- With a custom color (GetARGB: alpha, red, green, blue, 0-255)
actor_menu.set_msg(1, "Warning!", 4, GetARGB(255, 255, 50, 50))
```

Message types:

| Type | Appearance |
|------|-----------|
| `1` | Standard gameplay notification (bottom-centre of screen) |
| `2` | Showcase notification style |
| `3` | Icon notification |

### actor_menu.set_fade_msg

A message that fades in and out:

```lua
-- actor_menu.set_fade_msg(message, duration_seconds, color_table, sound_path)
actor_menu.set_fade_msg("Task complete.", 4)
actor_menu.set_fade_msg("Danger!", 3, {R=255, G=50, B=50})
actor_menu.set_fade_msg("Objective updated.", 4, nil, "interface\\inv_ui_itm_pickup")
```

Multiple `set_fade_msg` calls stack — messages display in order by time.

### actor_menu.set_notification

Shows an icon notification on the HUD:

```lua
-- actor_menu.set_notification(type, texture, duration_seconds, sound)
actor_menu.set_notification(3, "ui\\hud_icon_sleep", 10)
```

### State checks

```lua
local free = actor_menu.is_hud_free()        -- true if no menu/inventory is open
local inv_open = actor_menu.inventory_opened() -- true if inventory or related UI is open
```

---

## Tip system — news_manager

`news_manager` (from `news_manager.script`) handles the PDA-style tip popups and news notifications that appear in the top-right of the screen.

### send_tip

```lua
-- news_manager.send_tip(actor, text_key, timeout_ms, sender, showtime_ms, sender_story_id)
news_manager.send_tip(db.actor, "my_mod_tip_text", 0, nil, 5000)

-- With an NPC as sender (shows their icon and name)
news_manager.send_tip(db.actor, "my_mod_npc_says", 0, npc_object, 7000)

-- Delayed by 2 seconds
news_manager.send_tip(db.actor, "my_mod_delayed_tip", 2000, nil, 5000)
```

`text_key` must be a translation key defined in your text XML files.

Returns `false` (and cancels the tip) if `sender_story_id` is given and that NPC is dead or heavily wounded.

### send_task

Display task status notifications:

```lua
-- type: 'new', 'complete', 'fail', 'updated', 'reversed'
news_manager.send_task(db.actor, "new", task_object)
news_manager.send_task(db.actor, "complete", task_object)
```

### relocate_item and relocate_money

Show item pickup/drop and money transaction notifications:

```lua
news_manager.relocate_item(db.actor, "in", "bandage")     -- received 1 bandage
news_manager.relocate_item(db.actor, "in", "bandage", 5)  -- received 5 bandages
news_manager.relocate_item(db.actor, "out", "wpn_ak74")   -- gave away AK74

news_manager.relocate_money(db.actor, "in", 500)   -- received 500 roubles
news_manager.relocate_money(db.actor, "out", 200)  -- spent 200 roubles
```

---

## HUD element access

The HUD object (`get_hud()`) provides access to the game's HUD layer:

```lua
local hud = get_hud()
```

### Custom statics

You can add transient custom elements defined in XML to the HUD:

```lua
-- Add an element defined in a UI XML file
hud:AddCustomStatic("my_element_name", true)   -- true = auto-delete on level change

-- Access the added element
local elem = hud:GetCustomStatic("my_element_name")
if elem then
    elem:wnd():TextControl():SetTextST("Hello")
end

-- Remove it
hud:RemoveCustomStatic("my_element_name")
```

### Menu visibility

```lua
hud:HideActorMenu()   -- close inventory
hud:HidePdaMenu()     -- close PDA

hud:show_messages()   -- restore HUD message display
hud:hide_messages()   -- hide HUD messages
```

---

## Settings — ui_mcm

`ui_mcm` is the Mod Configuration Menu — the community standard for mod settings. Full setup is covered in [Systems: MCM](../systems/mcm.md).

### Reading settings

```lua
-- ui_mcm.get("mod_id/setting_name")
local enabled = ui_mcm.get("my_mod/enabled")
local volume  = ui_mcm.get("my_mod/effect_volume")
local count   = ui_mcm.get("my_mod/max_count")
```

Keys follow the pattern `"mod_id/setting_key"` where `mod_id` matches what you registered in your MCM table. Always check for `nil` when reading settings — MCM may not be installed:

```lua
local function get_setting(key, default)
    if ui_mcm then
        return ui_mcm.get("my_mod/" .. key)
    end
    return default
end

local volume = get_setting("volume", 1.0)
```

---

## Settings — ui_options

`ui_options` provides access to the built-in engine settings (the Options menu in-game). It's more commonly read than MCM in the base game itself.

```lua
-- Read a setting
local val = ui_options.get("key_path")

-- Write a setting (changes take effect immediately)
ui_options.set("key_path", value)
```

Common read-only uses:

```lua
-- Check if a feature is enabled in engine options
local dyn_news = ui_options.get("gameplay/dynamic_news")
```

---

## UI window registration

When you open a custom UI window that should block game input, use `Register_UI` and `Unregister_UI` from `_g.script`:

```lua
-- Register an open UI (blocks keybinds while open)
Register_UI("MyModUI", "my_mod_ui", "GUI")

-- Unregister when closing
Unregister_UI("MyModUI")

-- Check if your UI is open
if Check_UI("MyModUI") then ... end

-- Check if ANY mod UI is open
if Check_UI() then ... end
```

---

## Colors

```lua
-- GetARGB(alpha, red, green, blue) — values 0–255
local white  = GetARGB(255, 255, 255, 255)
local red    = GetARGB(255, 220, 50, 50)
local yellow = GetARGB(255, 255, 215, 0)
local dim    = GetARGB(128, 255, 255, 255)  -- semi-transparent white
```

---

## Common patterns

### Show a message only when the HUD is visible

```lua
local function notify(msg)
    if actor_menu.is_hud_free() then
        actor_menu.set_msg(1, msg, 4)
    end
end
```

### Show a translated message

```lua
local function notify_translated(key)
    actor_menu.set_msg(1, game.translate_string(key), 4)
end
```

### Quest complete notification

```lua
local function on_quest_complete()
    news_manager.send_tip(db.actor, "my_mod_quest_done", 0, nil, 6000)
    actor_menu.set_msg(1, game.translate_string("my_mod_quest_done_short"), 5)
end
```

### Read an MCM setting with fallback

```lua
local defaults = {
    enabled = true,
    radius  = 5,
    volume  = 1.0,
}

local function cfg(key)
    if not ui_mcm then return defaults[key] end
    local v = ui_mcm.get("my_mod/" .. key)
    return v ~= nil and v or defaults[key]
end
```
