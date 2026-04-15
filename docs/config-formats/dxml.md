# DXML — XML Patching

DXML (Dynamic XML) lets you modify XML files at runtime from a script, without replacing the original file. It's the correct way to patch UI layouts, dialogs, and other XML-defined content when compatibility with other mods matters.

---

## Why DXML exists

Without DXML, modifying an XML file means copying it and editing the copy. If two mods copy the same file, only one survives — the last one loaded wins. DXML solves this: multiple mods can each apply targeted changes to the same XML file and they all take effect.

DXML works through the `on_xml_read` callback, which fires each time the engine reads an XML file. Your handler receives the parsed document and can modify it in place before the engine uses it.

---

## The on_xml_read callback

```lua
local function on_xml_read(xml_file_name, xml_obj)
    -- xml_file_name: relative path to the file being read
    --                e.g. "ui\\ui_inventory.xml"
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

Note the double-backslash raw string literal (`[[...]]`) — on Windows these paths use backslashes.

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

---

## Inserting XML

`xml_obj:insertFromXMLString(xml_string, parent_element, position)` inserts raw XML into the document.

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

- `parent` is an element returned by `query` — or `nil` to insert at root level
- `position` is the index to insert at; `#parent.kids` appends after existing children
- The XML string can contain multiple elements or a single element

**Insert at root level** (no parent):

```lua
xml_obj:insertFromXMLString([[<my_element x="0" y="0"/>]])
```

---

## Modifying attributes

`xml_obj:setElementAttr(element, attribute_table)` changes attributes on an existing element.

```lua
local res = xml_obj:query("window[name=inventory_panel]")
if #res > 0 then
    -- Move the window and make it taller
    xml_obj:setElementAttr(res[1], {
        y      = 134,
        height = 560,
    })
end
```

Pass a table of `{attribute_name = value}` pairs. Only the attributes you specify are changed.

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

## Complete example

This snippet adds a new phrase option to an existing in-game dialog:

```lua
-- my_mod_dxml.script

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

## Tips and gotchas

**Backslash paths on Windows.** File paths use backslashes: `[[ui\ui_inventory.xml]]`. The double-bracket raw string avoids escaping.

**`#parent.kids` vs a fixed index.** Using `#parent.kids` always appends after existing children. A fixed index like `0` inserts before everything else.

**`query` returns a table, not a single element.** Always index with `[1]` and check `#res > 0` before using the result.

**Multiple mods, same file.** All registered `on_xml_read` handlers fire in registration order. If your mod and another both patch the same element, both patches apply — but the order they run in is determined by `on_game_start` registration order, which is alphabetical by filename. Name your file accordingly if order matters.

!!! warning "DXML requires the modded exes"
    DXML is **not** part of vanilla Anomaly. Like DLTX, it is included in the community **modded exes** maintained by themrdemonized ([xray-monolith](https://github.com/themrdemonized/xray-monolith)). The `on_xml_read` callback does not exist in vanilla Anomaly's script engine — it is added by the modded exes. List them as a hard dependency in your README if your mod uses DXML.
