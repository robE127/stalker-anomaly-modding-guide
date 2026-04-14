# DXML — XML Patching

!!! note "Work in progress"
    This page is being written. Content coming soon.

DXML (Dynamic XML) lets you modify XML files at runtime from a script, without replacing the original file. This is the correct way to patch XML when multiple mods need to modify the same file.

## Topics to cover

- Why DXML exists: multiple mods replacing the same XML file causes conflicts; DXML applies patches in sequence
- The `on_xml_read` callback: fires when the engine reads any XML file
  - Signature: `function on_xml_read(path, xml_obj)`
  - `path` is the relative path, e.g. `"ui\\ui_inventory.xml"`
  - `xml_obj` is a `CScriptXmlInit` that you can modify in place
- Common DXML operations:
  - `xml_obj:insertFromXmlFile(file, path)` — insert elements from another file
  - `xml_obj:setAttributeValue(path, attr, value)` — modify an attribute
  - Finding elements by path/index
- Pattern: only apply your patch when `path` matches the file you care about

```lua
local function on_xml_read(path, xml_obj)
    if path == "ui\\ui_inventory.xml" then
        -- apply your changes to xml_obj
    end
end

function on_game_start()
    RegisterScriptCallback("on_xml_read", on_xml_read)
end
```
