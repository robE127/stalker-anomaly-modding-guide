# DXML — XML Patching

DXML (Dynamic XML) lets you modify XML files at runtime from a script, without replacing the original file. It's the correct way to patch UI layouts, dialogs, and other XML-defined content when compatibility with other mods matters.

---

## Why DXML exists

Without DXML, modifying an XML file means copying it and editing the copy. If two mods copy the same file, only one survives — the last one loaded wins. DXML solves this: multiple mods can each apply targeted changes to the same XML file and they all take effect.

DXML works through the `on_xml_read` callback, which fires each time the engine reads an XML file. Your handler receives a DOM-like object representing the parsed document and can modify it in place before the engine uses it.

### How it works internally

When the engine loads an XML file, the C++ code calls a Lua function (`_G.COnXmlRead`) with the filename and the raw XML string. The DXML Lua library (`dxml_core.script`) parses this string into a DOM-like table structure, fires all registered `on_xml_read` callbacks so mods can modify it, then converts it back to an XML string and returns it to the engine. The engine parses the modified string as if it were the original file.

---

## File naming convention

DXML scripts should follow the naming convention:

```
modxml_<your_mod_name>.script
```

The `modxml_` prefix is the convention for DXML scripts (similar to how `mod_` is the prefix for DLTX files), though any script filename will work as long as it registers the callback.

---

## The on_xml_read callback

```lua
local function on_xml_read(xml_file_name, xml_obj)
    -- xml_file_name: relative path to the file being read
    --                e.g. "ui\ui_inventory.xml"
    -- xml_obj:       the parsed XML document (modifiable in place)
end

function on_game_start()
    RegisterScriptCallback("on_xml_read", on_xml_read)
end

function on_game_end()
    UnregisterScriptCallback("on_xml_read", on_xml_read)
end
```

**Always filter by filename.** The callback fires for every XML file the engine reads — dozens of them at startup. Only apply your changes when the path matches the file you care about:

```lua
local function on_xml_read(xml_file_name, xml_obj)
    if xml_file_name ~= [[ui\ui_inventory.xml]] then return end
    -- now safe to patch
end
```

Note the double-bracket raw string literal (`[[...]]`) — on Windows these paths use backslashes.

!!! warning "Translation and character_desc restrictions"
    DXML will not process translation strings from folders other than `eng/` and `rus/`. The file `gameplay\character_desc_general.xml` also cannot be patched through `on_xml_read` — use the special callbacks [`on_specific_character_init`](#patching-npc-character-data) and [`on_specific_character_dialog_list`](#patching-npc-dialog-lists) instead.

---

## Querying elements

`xml_obj:query(selector)` returns a table of matching elements using a CSS-like selector syntax.

```lua
-- Match by element name
local elements = xml_obj:query("button")

-- Match by attribute value
local elements = xml_obj:query("button[name=btn_ok]")

-- Match by id attribute
local elements = xml_obj:query("dialog[id=my_dialog_id]")

-- Navigate the tree (parent > direct child)
local phrases = xml_obj:query("dialog[id=my_dialog] > phrase_list > phrase[id=0]")

-- Check if anything was found
if #elements > 0 then
    local el = elements[1]
    -- use el
end
```

Returns an empty table (not nil) if nothing matches — safe to check with `#result > 0` or Anomaly's `is_not_empty(result)`.

### Selector syntax

| Selector | Meaning |
|----------|---------|
| `name` | Match element by tag name (any depth) |
| `parent > child` | Direct child only |
| `el + sibling` | First sibling after element |
| `el ~ sibling` | All siblings after element |
| `[attr=value]` | Match by attribute |
| `[attr1=val1][attr2=val2]` | Match by multiple attributes |

### Element structure

Each element returned by `query` is a table with:

- `el` — element type string: `<` prefix for node elements, `#` prefix for text nodes
- `parent` — reference to the parent element's table
- `kids` — table of child elements

---

## Inserting XML

### From a string

`xml_obj:insertFromXMLString(xml_string, parent, position, useRootNode)` inserts raw XML into the document.

```lua
local new_button = [[
    <button name="my_new_btn" x="10" y="10" width="80" height="24">
        <text>Click me</text>
    </button>
]]

local res = xml_obj:query("window[name=main_panel]")
if #res > 0 then
    local parent = res[1]
    -- Append to end of parent's children
    xml_obj:insertFromXMLString(new_button, parent, #parent.kids)
end
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `xml_string` | Yes | The XML to insert |
| `parent` | No | Element to insert into (default: root) |
| `position` | No | Index to insert at (default: end). `#parent.kids` appends; `0` prepends |
| `useRootNode` | No | If true, inserts the contents inside the root node rather than the whole string |

Returns the position of the first inserted element.

DXML supports `#include` directives inside the XML string — the `#include` must start at the beginning of a line:

```lua
xml_obj:insertFromXMLString([[
<my_element>
#include "gameplay\character_criticals.xml"
</my_element>
]])
```

**Insert at root level** (no parent):

```lua
xml_obj:insertFromXMLString([[<my_element x="0" y="0"/>]])
```

### From a file

`xml_obj:insertFromXMLFile(path, parent, position, useRootNode)` inserts XML from a file. The path is relative to `gamedata/configs/`:

```lua
-- Inserts contents of gamedata/configs/plugins/new_dialog.xml
xml_obj:insertFromXMLFile([[plugins\new_dialog.xml]])
```

Same parameters as `insertFromXMLString` except the first argument is a file path instead of an XML string. If the file cannot be read, the game will crash with an error message.

---

## Reading and modifying text

`xml_obj:getText(element)` returns the text content of an element. `xml_obj:setText(element, text)` replaces it.

```lua
local res = xml_obj:query("string[id=ui_st_game_version] > text")
if #res > 0 then
    local el = res[1]
    local current = xml_obj:getText(el)
    if current then
        xml_obj:setText(el, current .. " (Modded)")
    end
end
```

---

## Modifying attributes

`xml_obj:setElementAttr(element, attribute_table)` changes attributes on an existing element.

```lua
local res = xml_obj:query("window[name=inventory_panel]")
if #res > 0 then
    xml_obj:setElementAttr(res[1], {
        y      = 134,
        height = 560,
    })
end
```

Pass a table of `{attribute_name = value}` pairs. Only the attributes you specify are changed.

`xml_obj:getElementAttr(element)` returns a table of all attributes on an element:

```lua
local attrs = xml_obj:getElementAttr(res[1])
-- attrs = { x = "10", y = "20", width = "100", ... }
```

`xml_obj:removeElementAttr(element, attr_list)` removes specified attributes:

```lua
xml_obj:removeElementAttr(res[1], {"x", "y"})
```

---

## Adding to a dialog tree

A common use case is inserting a new phrase into an existing dialog:

```lua
local function on_xml_read(xml_file_name, xml_obj)
    if xml_file_name ~= [[gameplay\dialogs_jupiter.xml]] then return end

    -- Find phrase 6 in a specific dialog
    local res = xml_obj:query("dialog[id=jup_b4_monolith_main] > phrase_list > phrase[id=6]")
    if #res == 0 then return end

    local phrase = res[1]

    -- Add a <next> link pointing to our new phrase
    xml_obj:insertFromXMLString([[<next>100</next>]], phrase, #phrase.kids)

    -- Add the new phrase itself to the phrase_list
    local list = xml_obj:query("dialog[id=jup_b4_monolith_main] > phrase_list")
    if #list > 0 then
        xml_obj:insertFromXMLString([[
            <phrase id="100">
                <text>my_mod_new_dialog_line</text>
                <action>my_mod_dialog_action</action>
            </phrase>
        ]], list[1], #list[1].kids)
    end
end
```

---

## Patching a UI layout

Extend an existing inventory screen to add a custom button:

```lua
local function on_xml_read(xml_file_name, xml_obj)
    if xml_file_name ~= [[ui\ui_inventory.xml]] then return end

    local container = xml_obj:query("dragdrop_actorBag")
    if #container == 0 then return end

    xml_obj:insertFromXMLString([[
        <button name="my_mod_sort_btn" x="5" y="5" width="60" height="20">
            <text font="letterica16">Sort</text>
        </button>
    ]], container[1], #container[1].kids)
end
```

The button won't do anything yet — you also need to initialise it in the Lua class that owns `ui_inventory.xml`.

---

## Patching NPC character data

The file `gameplay\character_desc_general.xml` cannot be patched through `on_xml_read`. Instead, use the `on_specific_character_init` callback to modify NPC properties:

```lua
function on_game_start()
    RegisterScriptCallback("on_specific_character_init", function(character_id, data)
        if character_id == "sim_default_csky_0_default_0" then
            data.visual = [[actors\stalker_neutral\stalker_neutral_3_face_1]]
        end
    end)
end
```

The `data` table contains these fields:

| Field | Description |
|-------|-------------|
| `name` | Display name |
| `bio` | Biography text |
| `community` | Faction |
| `icon` | Portrait icon |
| `start_dialog` | Initial dialog |
| `panic_threshold` | Panic AI threshold |
| `hit_probability_factor` | Accuracy multiplier |
| `crouch_type` | Crouch behaviour |
| `mechanic_mode` | Mechanic repair capability |
| `critical_wound_weights` | Wound thresholds |
| `supplies` | Starting inventory |
| `visual` | 3D model path |
| `npc_config` | Config section override |
| `snd_config` | Sound config override |
| `terrain_sect` | Terrain navigation section |
| `rank_min`, `rank_max` | Rank range |
| `reputation_min`, `reputation_max` | Reputation range |
| `money_min`, `money_max` | Starting money range |
| `money_infinitive` | Unlimited money flag |

---

## Patching NPC dialog lists

Use `on_specific_character_dialog_list` to add or remove dialogs for specific NPCs:

```lua
function on_game_start()
    RegisterScriptCallback("on_specific_character_dialog_list", function(character_id, dialog_list)
        if character_id == "sim_default_csky_0_default_0" then
            dialog_list:add("my_mod_custom_dialog")
        end
    end)
end
```

The `dialog_list` object provides:

| Method | Description |
|--------|-------------|
| `find(regex)` | Find dialog by regex; returns last match and its position |
| `has(string)` | Check if dialog exists; returns position |
| `add(string, pos)` | Add dialog at position (default: before break dialog) |
| `add_first(string)` | Add dialog at the beginning |
| `add_last(string)` | Add dialog at the end |
| `remove(string)` | Remove dialog by name |
| `get_dialogs()` | Return the full dialog list |

---

## Complete example

This snippet adds a new phrase option to an existing in-game dialog:

```lua
-- modxml_my_mod.script

local NEW_PHRASE = [[
    <phrase id="999">
        <text>my_mod_extra_option</text>
        <precondition>my_mod_show_option</precondition>
        <action>my_mod_option_action</action>
    </phrase>
]]

local function on_xml_read(xml_file_name, xml_obj)
    if xml_file_name ~= [[gameplay\dialogs.xml]] then return end

    -- Add a <next>999</next> to phrase 0 of the target dialog
    local res = xml_obj:query("dialog[id=my_target_dialog] > phrase_list > phrase[id=0]")
    if #res == 0 then return end
    xml_obj:insertFromXMLString([[<next>999</next>]], res[1], #res[1].kids)

    -- Add the new phrase
    local list = xml_obj:query("dialog[id=my_target_dialog] > phrase_list")
    if #list == 0 then return end
    xml_obj:insertFromXMLString(NEW_PHRASE, list[1], #list[1].kids)
end

function on_game_start()
    RegisterScriptCallback("on_xml_read", on_xml_read)
end

function on_game_end()
    UnregisterScriptCallback("on_xml_read", on_xml_read)
end
```

And the Lua dialog functions referenced above:

```lua
function my_mod_show_option(first_speaker, second_speaker)
    return not db.actor:has_info("my_mod_option_used")
end

function my_mod_option_action(first_speaker, second_speaker)
    db.actor:give_info_portion("my_mod_option_used")
    db.actor:give_money(500)
end
```

---

## API reference

### xml_obj methods

| Method | Description |
|--------|-------------|
| `query(selector)` | Find elements by CSS-like selector; returns table |
| `insertFromXMLString(xml, [parent], [pos], [useRootNode])` | Insert XML string; returns position of first inserted element |
| `insertFromXMLFile(path, [parent], [pos], [useRootNode])` | Insert XML from file (relative to `gamedata/configs/`) |
| `getText(element)` | Get text content of an element |
| `setText(element, text)` | Set text content of an element |
| `setElementAttr(element, {attr = val, ...})` | Set attributes on an element |
| `getElementAttr(element)` | Get all attributes as a table |
| `removeElementAttr(element, {"attr1", "attr2"})` | Remove attributes from an element |

---

## Tips and gotchas

**Backslash paths on Windows.** File paths use backslashes: `[[ui\ui_inventory.xml]]`. The double-bracket raw string avoids escaping.

**`#parent.kids` vs a fixed index.** Using `#parent.kids` always appends after existing children. A fixed index like `0` inserts before everything else.

**`query` returns a table, not a single element.** Always index with `[1]` and check `#res > 0` before using the result.

**Check for duplicates before inserting.** If two mods both insert the same element, you'll get duplicates. Check with `query` first:

```lua
-- Don't insert if it already exists
if is_not_empty(xml_obj:query("menu_main btn[name=btn_mcm]")) then return end
```

**Multiple mods, same file.** All registered `on_xml_read` handlers fire in registration order. Each handler's modifications are visible to subsequent handlers. The order is determined by `on_game_start` registration order, which is alphabetical by script filename — hence the `modxml_` naming convention.

!!! warning "DXML requires the modded exes"
    DXML is **not** part of vanilla Anomaly. Like DLTX, it is included in the community **modded exes** maintained by themrdemonized ([xray-monolith](https://github.com/themrdemonized/xray-monolith)). The `on_xml_read` callback does not exist in vanilla Anomaly's script engine — it is added by the modded exes. List them as a hard dependency in your README if your mod uses DXML.
