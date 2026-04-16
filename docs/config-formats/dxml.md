# DXML — XML Patching

DXML (Dynamic XML) lets you modify XML files at runtime from a script, without replacing the original file. It's the correct way to patch UI layouts, dialogs, and other XML-defined content when compatibility with other mods matters.

---

## Why DXML exists

Without DXML, modifying an XML file means copying it and editing the copy. If two mods copy the same file, only one survives — the last one loaded wins. DXML solves this: multiple mods can each apply targeted changes to the same XML file and they all take effect.

DXML works through the `on_xml_read` callback, which fires each time the engine reads an XML file. Your handler receives a DOM-like object representing the parsed document and can modify it in place before the engine uses it.

### How it works internally

!!! info "Source: modded exes"
    DXML itself is a modded exes feature — it does not exist in the vanilla Anomaly engine. The implementation details below are derived from the [xray-monolith](https://github.com/themrdemonized/xray-monolith) C++ source code and `dxml_core.script`.

The data flow from disk to engine:

1. **C++ loads the file** — `CXml::Load()` in `src/xrXMLParser/xrXMLParser.cpp` reads the XML file from disk and recursively processes all `#include` directives, producing a single assembled XML string.
2. **C++ does an initial parse** — The assembled string is parsed by TinyXML into a document tree.
3. **C++ calls into Lua** — `XMLLuaCallback()` (defined in `src/xrGame/ScriptXMLInit.cpp`) calls the Lua function `_G.COnXmlRead(filename, raw_xml_string)` with the filename and the fully-assembled XML string (with `#include`s already resolved, BOM stripped).
4. **Lua parses again** — `dxml_core.script` parses the raw string into a DOM-like table using SLAXML (a pure-Lua XML parser), wraps it in the `xml_object` API, and dispatches to all registered `on_xml_read` callbacks.
5. **Lua serializes back** — After all callbacks run, the modified DOM is serialized back to an XML string and returned to C++.
6. **C++ re-parses** — `CXml::LoadFromString()` clears the initial TinyXML tree and re-parses the returned string. The engine then uses this final tree.

This means every XML file load involves **three parses** when DXML is active (TinyXML, SLAXML, TinyXML again). The initial C++ parse is effectively wasted — it exists as a fallback if the Lua callback doesn't exist or returns the string unchanged.

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
    DXML will not process translation strings from folders other than `eng/` and `rus/` — other locales are skipped because the SLAXML parser has not been tested with their character encodings. The file `gameplay\character_desc_general.xml` is also skipped because it contains data for all generic NPCs and is too large for the pure-Lua parser to handle efficiently. Use the dedicated callbacks [`on_specific_character_init`](#patching-npc-character-data) and [`on_specific_character_dialog_list`](#patching-npc-dialog-lists) instead.

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

The file `gameplay\character_desc_general.xml` cannot be patched through `on_xml_read`. Instead, the modded exes provide two dedicated callbacks that fire from C++ (`CSpecificCharacter::load_shared()` in `src/xrServerEntities/specific_character.cpp`) when each individual character is loaded. These use the standard script callback system, not the DXML dispatch.

Use the `on_specific_character_init` callback to modify NPC properties:

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

## Caching

The `on_xml_read` callback receives an optional third argument — a `flags` table:

```lua
local function on_xml_read(xml_file_name, xml_obj, flags)
    if xml_file_name ~= [[ui\ui_inventory.xml]] then return end
    -- modify xml_obj...
    flags.cache = true  -- cache the result for this file
end
```

When any callback sets `flags.cache = true`, the final serialized XML string is cached in memory. On subsequent loads of the same file, **no callbacks fire** — the cached string is returned directly to C++.

!!! warning "Cache has no invalidation"
    Once cached, the result persists for the entire game session. There is no API to clear individual entries. Only use caching for files whose DXML modifications are deterministic and don't depend on game state.

By default, `flags.cache` is `false` — XML files are re-parsed and all callbacks re-fired on every load. This is correct for most mods.

---

## Execution order

All registered `on_xml_read` handlers fire in registration order. Each handler's modifications are visible to subsequent handlers.

**For `modxml_*.script` files**, `dxml_core.script` scans for all scripts matching the `modxml_*` prefix, sorts them alphabetically, and calls each script's `on_xml_read` registration function in that sorted order. This means `modxml_aaa_mod.script` runs before `modxml_zzz_mod.script`.

Callbacks registered from other scripts (e.g., in `on_game_start`) fire after all `modxml_*` callbacks.

The `on_xml_read` callback uses a **separate dispatch system** from normal script callbacks. `dxml_core.script` monkey-patches `RegisterScriptCallback` so that `"on_xml_read"` registrations go into a dedicated `xmlCallbacks` array rather than the standard `axr_main` intercepts table. Duplicate function references are silently ignored.

---

## Tips and gotchas

**Backslash paths on Windows.** File paths use backslashes: `[[ui\ui_inventory.xml]]`. The double-bracket raw string avoids escaping.

**`#include` is pre-processed.** By the time your callback fires, all `#include` directives in the original XML file have already been resolved by the C++ loader. You see the fully assembled document. However, `insertFromXMLString` also supports `#include` directives in the strings you insert.

**`#parent.kids` vs a fixed index.** Using `#parent.kids` always appends after existing children. A fixed index like `0` inserts before everything else.

**`query` returns a table, not a single element.** Always index with `[1]` and check `#res > 0` before using the result.

**Check for duplicates before inserting.** If two mods both insert the same element, you'll get duplicates. Check with `query` first:

```lua
-- Don't insert if it already exists
if is_not_empty(xml_obj:query("menu_main btn[name=btn_mcm]")) then return end
```

**Error handling is silent.** If SLAXML fails to parse the XML (e.g., the raw string is malformed), the original unmodified string is returned to C++ and your modifications are silently dropped. Check the log for parse errors if your changes aren't taking effect.

!!! warning "DXML requires the modded exes"
    DXML is **not** part of vanilla Anomaly. Like DLTX, it is included in the community **modded exes** maintained by themrdemonized ([xray-monolith](https://github.com/themrdemonized/xray-monolith)). The `on_xml_read` callback does not exist in vanilla Anomaly's script engine — it is added by the modded exes. List them as a hard dependency in your README if your mod uses DXML.

---

## See also

- [XML Configs](xml.md) — the base format DXML patches
