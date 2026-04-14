# The Callback System

The callback system is how Anomaly scripts communicate with the engine and with each other. Almost everything you'll ever do in a mod is triggered by a callback.

---

## The three functions

```lua
RegisterScriptCallback(name, fn)    -- Subscribe to an event
UnregisterScriptCallback(name, fn)  -- Unsubscribe
AddScriptCallback(name)             -- Declare a new event (for mod authors)
SendScriptCallback(name, ...)       -- Fire an event (for mod authors)
```

---

## How registration works

Internally, callbacks are stored in a table where the **function itself is the key**:

```lua
-- Conceptually (from axr_main.script):
intercepts["on_game_load"][your_function] = true
```

This means:
- Registering the same function twice is harmless (it's just setting a key to `true` again)
- You must pass the **exact same function reference** to unregister
- Order of execution among registered functions is not guaranteed

---

## The canonical pattern

Every mod that registers callbacks should follow this structure:

```lua
-- Declare local functions — the same references are used to register AND unregister
local function on_game_load()
    -- ...
end

local function on_key_press(key)
    -- ...
end

-- Register in on_game_start
function on_game_start()
    RegisterScriptCallback("on_game_load", on_game_load)
    RegisterScriptCallback("on_key_press", on_key_press)
end

-- Unregister in on_game_end
function on_game_end()
    UnregisterScriptCallback("on_game_load", on_game_load)
    UnregisterScriptCallback("on_key_press", on_key_press)
end
```

!!! danger "Anonymous functions break unregistration"
    This is a common mistake:
    ```lua
    -- WRONG: each call creates a new function object; you can never unregister it
    RegisterScriptCallback("on_game_load", function()
        printf("loaded")
    end)
    ```
    Always assign your callback to a named local variable first.

---

## Callback arguments

Callbacks receive arguments depending on the event. Always check what arguments a callback provides before writing your handler.

```lua
-- on_key_press provides the key code
local function on_key_press(key)
    if key == DIK_keys.DIK_F5 then
        -- ...
    end
end

-- npc_on_death_callback provides victim and killer
local function npc_on_death_callback(victim, who)
    printf("NPC %s killed by %s", victim:name(), who and who:name() or "unknown")
end

-- actor_on_before_hit provides a hit object and bone id
local function actor_on_before_hit(shit, bone_id)
    shit.power = shit.power * 0.5  -- halve incoming damage
end
```

See the [Callbacks Reference](../callbacks-reference/index.md) for the full list with signatures.

---

## Registering objects (not just functions)

The callback system also supports registering a **table/object** with a matching method name. This is used by object binders:

```lua
-- RegisterScriptCallback("save_state", self) will call self:save_state(m_data)
class "my_binder" (object_binder)

function my_binder:save_state(m_data)
    m_data[self.object:id()] = self.my_data
end

function my_binder:net_spawn(se_abstract)
    RegisterScriptCallback("save_state", self)
end

function my_binder:net_destroy()
    UnregisterScriptCallback("save_state", self)
end
```

For most mods you won't need this — function registration is sufficient.

---

## Defining your own callbacks

If you're writing a mod that other mods should be able to hook into, you can create your own callbacks:

```lua
-- Declare the callback (do this at top level, before any registrations)
AddScriptCallback("my_mod_on_something_happened")

-- Fire it when the event occurs
local function do_something()
    -- ... do the thing ...
    SendScriptCallback("my_mod_on_something_happened", some_data)
end
```

Other mods can then:
```lua
local function on_my_mod_event(data)
    -- react to your event
end

function on_game_start()
    RegisterScriptCallback("my_mod_on_something_happened", on_my_mod_event)
end
```

This is how Anomaly's major systems (MCM, the body health system, etc.) expose their events to other mods.

---

## Suppressing default behaviour

Some callbacks pass a `flags` table that you can modify to cancel the default engine action:

```lua
-- on_before_key_press: set flags.ret = true to swallow the keypress
local function on_before_key_press(key, bind, flags)
    if key == DIK_keys.DIK_TAB and some_condition then
        flags.ret = true  -- prevent default TAB behaviour
    end
end
```

Not all callbacks support this. The [Callbacks Reference](../callbacks-reference/index.md) notes which ones do.
