# UI Scripting

!!! note "Work in progress"
    This page is being written. Content coming soon.

## Topics to cover

- How the X-Ray UI system works: XML defines layout, Lua drives logic
- `CUIScriptWnd` — base class for script-controlled windows
- Creating a simple window: inherit from `CUIScriptWnd`, define `__init`, `InitControls`, `OnKeyboard`
- XML-defined controls: `static`, `button`, `edit`, `list`, `scrollview`, `3tButton`
- Binding Lua functions to button click events
- `GUI_on_show(name, path)` / `GUI_on_hide(name, path)` callbacks — fires when any UI window opens/closes
- Opening and closing windows from script
- Reading control values: text fields, checkboxes, list selection
- The `actor_menu` module and the inventory screen
- HUD notifications: `news_manager.send_tip`, `actor_menu.set_msg`
- Modal dialogs vs non-modal overlays
