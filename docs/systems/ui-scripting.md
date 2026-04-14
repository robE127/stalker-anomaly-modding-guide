# UI Scripting

Anomaly's UI system uses XML to define layout and Lua to drive logic. This page covers building custom windows — from a minimal dialog to a fully interactive menu.

For quick HUD messages and notifications without a custom window, see [UI Functions](../api-reference/ui.md).

---

## How the system works

```
XML file             Lua script
─────────────────    ──────────────────────────────────────
Defines layout   →   class inherits CUIScriptWnd
Button positions     __init() calls xml:ParseFile(...)
Control sizes        InitControls() creates controls
Font, colour         InitCallBacks() wires up events
                     OnKeyboard() handles key presses
```

The XML is loaded at runtime from `gamedata/configs/ui/`. Lua then instantiates controls from it and responds to events. The XML never changes at runtime — only Lua drives state.

---

## File locations

```
gamedata/
  configs/
    ui/
      my_mod_window.xml      ← XML layout
  scripts/
    my_mod_ui.script         ← Lua window class
    my_mod.script            ← main mod logic (opens/closes window)
```

---

## Minimal window example

### XML layout

```xml
<!-- gamedata/configs/ui/my_mod_window.xml -->
<w>
    <window name="background">
        <auto_static x="0" y="0" width="400" height="300"
                     texture="ui\ui_common_window" stretch="1"/>
    </window>

    <button name="btn_close" x="170" y="260" width="60" height="24">
        <text>Close</text>
    </button>

    <static name="lbl_info" x="20" y="20" width="360" height="200">
        <text font="letterica18" r="200" g="200" b="200"/>
    </static>
</w>
```

### Lua window class

```lua
-- my_mod_ui.script

class "my_mod_window" (CUIScriptWnd)

function my_mod_window:__init()
    super()
    self:InitControls()
    self:InitCallBacks()
end

function my_mod_window:__finalize()
end

function my_mod_window:InitControls()
    -- Set the window's position and size on screen
    self:SetWndRect(Frect():set(200, 150, 400, 300))

    -- Load and parse the XML file
    local xml = CScriptXmlInit()
    xml:ParseFile("my_mod_window.xml")

    -- Initialise controls from XML (they become children of self)
    xml:InitStatic("background", self)
    self.lbl_info = xml:InitTextWnd("lbl_info", self)
    self.btn_close = xml:Init3tButton("btn_close", self)

    -- Register controls so callbacks can fire
    self:Register(self.btn_close, "btn_close")
end

function my_mod_window:InitCallBacks()
    -- Wire a Lua function to the button click event
    self:AddCallback("btn_close", ui_events.BUTTON_CLICKED, self.OnClose, self)
end

function my_mod_window:OnClose()
    self:HideDialog()
    Unregister_UI("my_mod_window")
end

function my_mod_window:OnKeyboard(key, action)
    -- action 1 = key down, 2 = key up
    if action == ui_events.WINDOW_KEY_PRESSED then
        if key == DIK_keys.DIK_ESCAPE then
            self:OnClose()
            return true  -- consumed
        end
    end
    return false
end

function my_mod_window:SetText(msg)
    self.lbl_info:SetText(msg)
end
```

### Opening and closing the window

```lua
-- my_mod.script

local GUI = nil

local function open_window(message)
    if GUI then return end  -- already open

    GUI = my_mod_window()
    GUI:SetText(message)
    GUI:ShowDialog(true)

    Register_UI("my_mod_window", "my_mod_ui", "GUI")
end

local function on_key_press(key)
    if key == DIK_keys.DIK_F9 then
        open_window("Hello from my mod!")
    end
end

function on_game_start()
    RegisterScriptCallback("on_key_press", on_key_press)
end

function on_game_end()
    UnregisterScriptCallback("on_key_press", on_key_press)
    GUI = nil
end
```

---

## Control types and initialisation

All controls are initialised through `CScriptXmlInit` by calling a method named for the control type:

```lua
local xml = CScriptXmlInit()
xml:ParseFile("my_file.xml")

-- Controls are always: xml:InitXxx("xml_element_name", parent)
xml:InitStatic("my_bg",      self)              -- CUIStatic (image/background)
xml:InitTextWnd("my_label",  self)              -- CUITextWnd (text display)
xml:Init3tButton("my_btn",   self)              -- CUI3tButton (standard button)
xml:InitEditBox("my_input",  self)              -- CUIEditBox (text input)
xml:InitListBox("my_list",   self)              -- CUIListBox (scrollable list)
xml:InitComboBox("my_combo", self)              -- CUIComboBox (dropdown)
xml:InitProgressBar("my_bar", self)             -- CUIProgressBar
xml:InitFrame("my_frame",    self)              -- CUIFrame (border/panel)
xml:InitScrollView("my_scroll", self)           -- CUIScrollView
xml:InitWindow("my_wnd",     self)              -- generic CUIWindow
```

---

## Common control methods

### Text controls (CUITextWnd, labels)

```lua
lbl:SetText("Hello world")
lbl:SetTextST("localization_key")   -- translates automatically
local text = lbl:GetText()
lbl:SetTextColor(GetARGB(255, 255, 200, 0))
lbl:SetFont(GetFontLetterica18())   -- or GetFontSmall(), GetFontMedium()
lbl:Show(false)                     -- hide/show
```

### Buttons (CUI3tButton)

```lua
btn:Enable(false)    -- disable (greyed out, no clicks)
btn:Enable(true)
btn:Show(false)
btn:SetText("Click me")
```

### Edit boxes (CUIEditBox)

```lua
local text = edit:GetText()
edit:SetText("default")
edit:SetNumbersOnly(true)   -- restrict to numeric input
```

### List boxes (CUIListBox)

```lua
list:AddTextItem("item label")
list:RemoveAll()
local index = list:GetSelectedIndex()
local text  = list:GetSelectedText()
local count = list:GetSize()
list:SetSelectedIndex(0)
```

### Progress bar

```lua
bar:SetProgressPos(0.75)   -- 0.0 to 1.0
local pos = bar:GetProgressPos()
```

### Visibility and layout

```lua
control:Show(true)
control:IsShown()
control:Enable(true)
control:SetWndRect(Frect():set(x, y, width, height))
control:SetWndPos(vector2():set(x, y))
control:SetWndSize(vector2():set(w, h))
local w = control:GetWidth()
local h = control:GetHeight()
```

---

## Callback events

Register callbacks in `InitCallBacks` using `AddCallback`:

```lua
self:AddCallback("control_name", event_type, handler_function, context)
```

Common event types from `ui_events`:

| Event | Description |
|-------|-------------|
| `ui_events.BUTTON_CLICKED` | Button clicked |
| `ui_events.LIST_ITEM_SELECT` | List item selected |
| `ui_events.EDIT_TEXT_COMMIT` | Edit box text confirmed |
| `ui_events.WINDOW_KEY_PRESSED` | Key pressed inside window |
| `ui_events.WINDOW_KEY_RELEASED` | Key released |
| `ui_events.CHECKBOX_CHANGED` | Checkbox toggled |

```lua
function my_mod_window:InitCallBacks()
    self:AddCallback("btn_ok",      ui_events.BUTTON_CLICKED,   self.OnOK,    self)
    self:AddCallback("btn_cancel",  ui_events.BUTTON_CLICKED,   self.OnCancel, self)
    self:AddCallback("list_items",  ui_events.LIST_ITEM_SELECT, self.OnSelect, self)
end

function my_mod_window:OnOK()
    local input = self.edit_name:GetText()
    save_name(input)
    self:HideDialog()
    Unregister_UI("my_mod_window")
end

function my_mod_window:OnSelect()
    local idx = self.list_items:GetSelectedIndex()
    printf("selected index: %d", idx)
end
```

---

## Reacting to any UI opening or closing

The `GUI_on_show` and `GUI_on_hide` callbacks fire whenever any UI window is registered or unregistered:

```lua
local function GUI_on_show(name, path)
    printf("UI opened: %s (%s)", name, path)
end

local function GUI_on_hide(name, path)
    printf("UI closed: %s (%s)", name, path)
end

function on_game_start()
    RegisterScriptCallback("GUI_on_show", GUI_on_show)
    RegisterScriptCallback("GUI_on_hide", GUI_on_hide)
end
```

---

## Screen coordinates

The UI coordinate system in Anomaly uses a virtual 1024×768 space regardless of actual screen resolution. The engine scales automatically.

```lua
-- Centre a 400×300 window
self:SetWndRect(Frect():set(
    (1024 - 400) / 2,   -- x = 312
    (768  - 300) / 2,   -- y = 234
    400,                 -- width
    300                  -- height
))
```

---

## Tips and pitfalls

**Always unregister on close.** If you call `Register_UI` when opening, call `Unregister_UI` in your close handler. Leaving a UI registered blocks game input permanently.

**Nil-check your window.** If the player can open your window from a callback, guard against it being opened twice:

```lua
if GUI then return end
GUI = my_window()
GUI:ShowDialog(true)
Register_UI("MyWnd", "my_ui", "GUI")
```

**`ShowDialog(true)` vs `Show(true)`.** `ShowDialog` registers the window with the game's dialog system (enables input handling, proper z-ordering). `Show` just toggles visibility — use `ShowDialog` for top-level windows.

**Keyboard handling.** Override `OnKeyboard` in your window class to intercept keys. Return `true` to consume the event and prevent it propagating to the game. Always handle `DIK_ESCAPE` to let the player close your window.
