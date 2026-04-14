# Localization

`game.translate_string` is the most-called function across all Anomaly scripts (3,351 uses in the analyzed repos). The localization system is how every piece of visible text reaches the player — understanding it is not optional.

---

## How it works

Text is stored in XML files under `gamedata/configs/text/<lang>/`. When `game.translate_string("key")` is called, the engine looks up `key` in the loaded string tables for the current language and returns the value.

```
gamedata/
  configs/
    text/
      eng/           ← English (primary fallback)
        ui_st_items.xml
        ui_st_my_mod.xml    ← your mod adds files here
      rus/           ← Russian (if providing Russian localisation)
        ui_st_my_mod.xml
```

If a key isn't found in the current language, the engine falls back to `eng`. If it's not found there either, `translate_string` returns the key itself as a literal string.

---

## XML file format

```xml
<?xml version="1.0" encoding="windows-1251"?>
<string_table>
    <string id="my_mod_quest_title">
        <text>The Lost Signal</text>
    </string>

    <string id="my_mod_quest_body">
        <text>Track down the source of the anomalous transmission in Yantar.</text>
    </string>

    <string id="my_mod_reward_roubles">
        <text>You received %d roubles.</text>
    </string>
</string_table>
```

- The filename can be anything — the engine loads every XML in the `text/<lang>/` folder
- Use a filename prefix matching your mod name to keep things organised
- Encoding must be `windows-1251` (not UTF-8) — this is an X-Ray limitation

---

## Using translate_string

```lua
-- Basic lookup
local title = game.translate_string("my_mod_quest_title")

-- Common pattern: translate and display
actor_menu.set_msg(1, game.translate_string("my_mod_quest_title"), 4)

-- Unknown key falls back to the key itself (useful for detecting missing strings)
local text = game.translate_string("nonexistent_key")
-- text == "nonexistent_key"
```

---

## Naming conventions

All keys in `m_data` are shared globally across every mod. Collisions silently overwrite each other. Always prefix keys with your mod name:

```lua
-- Dangerous: generic keys that will clash
game.translate_string("quest_title")
game.translate_string("error_msg")

-- Safe: namespaced keys
game.translate_string("my_mod_quest_title")
game.translate_string("my_mod_error_msg")
```

---

## String formatting

For strings that contain dynamic values, use Lua's `string.format` after translating:

```xml
<string id="my_mod_reward_fmt">
    <text>You received %d roubles.</text>
</string>
```

```lua
local msg = string.format(game.translate_string("my_mod_reward_fmt"), 500)
-- msg == "You received 500 roubles."
```

The `%` format codes are standard C-style: `%d` integer, `%s` string, `%f` float, `%.1f` one decimal place.

---

## Multiline text

Use `\n` in the XML value for line breaks:

```xml
<string id="my_mod_long_desc">
    <text>First line of the description.\nSecond line.\nThird line.</text>
</string>
```

---

## Colour tags

Anomaly's UI supports inline colour tags in displayed text:

```xml
<string id="my_mod_colored_msg">
    <text>%c[d_green]Success:%c[default] operation complete.</text>
</string>
```

Common colour tags: `%c[d_green]`, `%c[d_red]`, `%c[d_orange]`, `%c[d_cyan]`, `%c[default]` (reset).

These only render in UI elements that support rich text — plain HUD messages from `actor_menu.set_msg` may not interpret them.

---

## Reacting to language changes

The `on_localization_change` callback fires when the player changes language in the options menu:

```lua
local function on_localization_change()
    -- Re-read any cached translated strings
    cached_title = game.translate_string("my_mod_quest_title")
end

function on_game_start()
    RegisterScriptCallback("on_localization_change", on_localization_change)
end

function on_game_end()
    UnregisterScriptCallback("on_localization_change", on_localization_change)
end
```

Most mods don't need this — if you call `translate_string` at the point of use (not at startup), the language change is automatically reflected.

---

## Adding a new language

To add Russian (or any other language) support, create the same filename in the `rus/` folder with translated values:

```
configs/text/eng/ui_st_my_mod.xml    ← English
configs/text/rus/ui_st_my_mod.xml    ← Russian (optional)
```

Players using Russian will see your Russian text; players using any other language see the English fallback.

---

## Common patterns

### Translating level names

Level names (as returned by `level.name()`) often have matching translation keys:

```lua
local level_display = game.translate_string(level.name())
-- "l01_escape" → "Cordon" (if the key exists in the string tables)
```

### Building a translated message from parts

```lua
local function describe_item(section)
    local name = game.translate_string(
        ini_sys:r_string_ex(section, "inv_name") or section
    )
    local desc = game.translate_string(
        ini_sys:r_string_ex(section, "description") or ""
    )
    return name .. ": " .. desc
end
```

### Tip notification with translated text

```lua
news_manager.send_tip(db.actor, "my_mod_tip_key", 0, nil, 5000)
-- the key "my_mod_tip_key" must exist in your string XML
```

`send_tip` takes the key directly and translates it internally — do not pre-translate before passing it.
