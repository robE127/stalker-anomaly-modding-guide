# XML Configs

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- Where XML is used vs LTX (UI layouts, localization, dialog trees, character/spawn profiles)
- `configs/ui/` — UI element definitions: positions, sizes, textures, font references
- `configs/text/<lang>/` — Localization string tables (`<string id="key"><text>Value</text></string>`)
- `configs/gameplay/` — Task definitions, dialog trees, character profiles
- Reading XML from Lua using `CScriptXmlInit`
- The `on_xml_read` callback — fired when the engine reads an XML file, used for DXML patching
