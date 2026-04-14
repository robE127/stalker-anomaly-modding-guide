# XML Configs

XML is used alongside LTX for a specific subset of game data: UI layouts, localization strings, dialog trees, character spawn profiles, and task definitions. The two formats serve different purposes and are never interchangeable.

---

## Where XML is used

| Folder | Contents |
|--------|----------|
| `configs/ui/` | UI element definitions — positions, sizes, textures, fonts |
| `configs/text/<lang>/` | Localization string tables |
| `configs/gameplay/` | Task definitions, dialog trees |
| `configs/gameplay/character_desc_*.xml` | NPC character profiles |
| `configs/gameplay/spawn_sections*.xml` | Spawn profiles |

---

## Syntax overview

Anomaly XML follows standard XML rules with a few conventions:

```xml
<?xml version="1.0" encoding="windows-1251"?>
<root_element>
    <!-- This is a comment -->
    <child_element name="my_name" x="10" y="20" width="100" height="50">
        <nested>content</nested>
    </child_element>
</root_element>
```

**Important:** Anomaly XML must be encoded as `windows-1251`, not UTF-8. Opening these files in a modern text editor set to UTF-8 may corrupt non-ASCII characters.

---

## UI layout files

UI XML files define control positions, sizes, textures, and fonts. The Lua script then loads these definitions using `CScriptXmlInit`.

```xml
<!-- configs/ui/my_mod_window.xml -->
<w>
    <background x="0" y="0" width="400" height="300" stretch="1">
        <texture>ui\ui_common_window</texture>
    </background>

    <button name="btn_ok" x="155" y="260" width="90" height="24">
        <text font="letterica16" r="200" g="200" b="200">OK</text>
    </button>

    <static name="lbl_title" x="20" y="15" width="360" height="30">
        <text font="letterica18" align="c" r="255" g="215" b="0"/>
    </static>

    <edit_box name="input_field" x="20" y="60" width="360" height="24"/>
</w>
```

**Common attributes:**

| Attribute | Description |
|-----------|-------------|
| `x`, `y` | Position in virtual 1024×768 screen space |
| `width`, `height` | Dimensions |
| `stretch="1"` | Scale texture to fill bounds |
| `align` | Text alignment: `"l"`, `"c"`, `"r"` |
| `font` | Font name: `"letterica16"`, `"letterica18"`, `"graffiti19"`, `"small"` |
| `r`, `g`, `b` | Text colour (0–255) |

**Loading in Lua:**

```lua
local xml = CScriptXmlInit()
xml:ParseFile("my_mod_window.xml")

self.btn_ok    = xml:Init3tButton("button[name=btn_ok]", self)
self.lbl_title = xml:InitTextWnd("static[name=lbl_title]", self)
self.input     = xml:InitEditBox("edit_box[name=input_field]", self)
```

See [UI Scripting](../systems/ui-scripting.md) for the full window building pattern.

---

## Localization string tables

String tables are simple key→value XML files. Every piece of visible text in the game goes through this system.

```xml
<?xml version="1.0" encoding="windows-1251"?>
<string_table>
    <string id="my_mod_quest_title">
        <text>The Lost Signal</text>
    </string>

    <string id="my_mod_reward_fmt">
        <text>You received %d roubles.</text>
    </string>

    <string id="my_mod_hint">
        <text>%c[d_green]Hint:%c[default] Check the stash near the bridge.</text>
    </string>
</string_table>
```

- Files go in `configs/text/eng/` (and optionally other language folders)
- Filename can be anything — all files in the folder are loaded
- Keys must be globally unique; prefix with your mod name
- Look up with `game.translate_string("my_mod_quest_title")`

See [Localization](../systems/localization.md) for the full system.

---

## Dialog trees

Dialog XML defines the conversation trees shown when the player talks to an NPC. Each `phrase` is a line of dialog; `next` links to the next phrase; `precondition` and `action` call Lua functions.

```xml
<dialog id="my_mod_quest_dialog">
    <phrase_list>
        <!-- Opening line (always phrase 0) -->
        <phrase id="0">
            <text>my_mod_dialog_greeting</text>
            <next>1</next>
            <next>2</next>
        </phrase>

        <!-- Option 1: start quest (only shown if quest not yet started) -->
        <phrase id="1">
            <text>my_mod_dialog_ask_quest</text>
            <precondition>my_mod_can_give_quest</precondition>
            <action>my_mod_give_quest</action>
            <next>10</next>
        </phrase>

        <!-- Option 2: goodbye -->
        <phrase id="2">
            <text>my_mod_dialog_goodbye</text>
        </phrase>

        <!-- NPC response after accepting quest -->
        <phrase id="10">
            <text>my_mod_dialog_quest_given</text>
        </phrase>
    </phrase_list>
</dialog>
```

`precondition` and `action` reference **global Lua function names**. The functions receive `(first_speaker, second_speaker)` where first_speaker is the NPC and second_speaker is the actor.

Dialogs must also be registered in the NPC's character description XML:

```xml
<specific_character id="my_npc_character">
    ...
    <actor_dialog>my_mod_quest_dialog</actor_dialog>
</specific_character>
```

---

## Task definitions

Tasks (quests) are defined in `configs/gameplay/` XML files:

```xml
<game_task id="my_mod_find_item_task">
    <title>my_mod_task_find_title</title>
    <descr>my_mod_task_find_descr</descr>
    <job_descr>my_mod_task_find_job</job_descr>
    <icon>ui_icon_default</icon>
    <article>article_my_mod</article>

    <objectives>
        <objective>
            <text>my_mod_task_objective_1</text>
            <infoportion_complete>my_mod_item_found</infoportion_complete>
            <on_complete>my_mod_on_task_complete</on_complete>
        </objective>
    </objectives>
</game_task>
```

All `<text>` values are localization keys. `infoportion_complete` is an info portion ID — the task objective completes automatically when the actor receives that info portion.

---

## NPC character profiles

Character profiles define an NPC's appearance, voice, faction, and dialog:

```xml
<specific_character id="my_npc_unique_stalker" team_default="1">
    <name>my_npc_name_key</name>
    <icon>ui_inGame2_Stalker_1</icon>
    <bio>my_npc_bio_key</bio>
    <class>stalker</class>
    <community>stalker</community>
    <rank>400</rank>
    <reputation>200</reputation>
    <money count="500" delay="0"/>
    <rank_insignia id="0"/>
    <visual>actors\stalker_soldier\stalker_soldier_1</visual>
    <actor_dialog>my_mod_quest_dialog</actor_dialog>
    <start_dialog>my_mod_greeting_dialog</start_dialog>
    <supplies>
        [wpn_ak74] count = 1
        [ammo_5.45x39_fmj] count = 2
    </supplies>
</specific_character>
```

---

## Reading XML from Lua

Beyond UI layouts, scripts can directly inspect XML using `CScriptXmlInit`:

```lua
local xml = CScriptXmlInit()
xml:ParseFile("gameplay\\my_task_file.xml")

-- Navigate to a specific element
local count = xml:GetNodesNum("game_task", 0)  -- number of <game_task> elements
```

For runtime XML modification, use [DXML](dxml.md).

---

## Modding XML files

**Don't replace files directly** when other mods might also modify them. Replacing `ui_inventory.xml` means your version wins and the other mod's changes are lost.

Use [DXML](dxml.md) to apply targeted patches instead — it lets multiple mods modify the same XML file without conflicts.

The exception is new files you create from scratch (new dialogs, new string tables, new UI windows). Those don't conflict with anything and can simply be placed in the appropriate folder.
