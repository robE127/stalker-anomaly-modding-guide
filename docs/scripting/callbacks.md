# The Callback System

The callback system is how Anomaly scripts communicate with the engine and with each other. Almost everything you'll ever do in a mod is triggered by a callback.

---

## The callback API

```lua
RegisterScriptCallback(name, fn)    -- Subscribe to an event
UnregisterScriptCallback(name, fn)  -- Unsubscribe
AddScriptCallback(name)             -- Declare a new event (for mod authors)
SendScriptCallback(name, ...)       -- Fire an event (for mod authors)
```

---

## How registration works

Internally, callbacks are stored in a table where the **function itself is the key** (from `axr_main.script`):

```lua
intercepts["on_game_load"][your_function] = true
```

This means:
- Registering the same function twice is harmless — the second call just sets the same key to `true` again, no duplicate entry is created
- You must pass the **exact same function reference** to unregister — this is why anonymous functions can never be unregistered
- Order of execution among registered functions is not guaranteed

**The intercepts table persists for the entire process lifetime** — it is never automatically reset between game sessions. If you load a save, return to main menu, and load another save without quitting, the table from the first session is still in memory. This is why `on_game_end` unregistration matters: not because double-registration causes double-firing (it doesn't), but because callbacks that aren't unregistered remain active across session boundaries and can fire while your module's state is in an indeterminate condition — reset local variables, a nil `db.actor`, or stale flags from the previous session.

Unregistering in `on_game_end` is also used in advanced mods to **replace or intercept base game callbacks**: unregister the original function, then re-register a patched version that adds behaviour before or after the original call.

---

## Two callback systems

Anomaly actually has **two separate callback systems** that serve different purposes. Understanding this distinction helps you pick the right one.

### Script callbacks (Lua-side dispatch)

`RegisterScriptCallback` / `SendScriptCallback` is a **purely Lua-side** system, implemented in `axr_main.script` and `dynamic_callbacks.lua`. The engine doesn't know about it. Base game scripts and mods manually call `SendScriptCallback(...)` at the right moments, and all registered handlers are invoked.

This is the system you use for most modding: `on_game_load`, `on_key_press`, `npc_on_death_callback`, etc. These are the callbacks listed in the [Callbacks Reference](../callbacks-reference/index.md).

### Object callbacks (engine-side dispatch)

`game_object:set_callback(type, fn)` is an **engine-side** callback system. You register a Lua function on a specific `game_object`, and the C++ engine calls it directly when the event fires on that object. These are per-object, not global.

**In practice, `set_callback` is used exclusively inside [object binders](object-binders.md).** The binder's `net_spawn` registers callbacks on `self.object`, and `net_destroy` clears them. Across the entire base game and all community mods we analysed, no mod uses `set_callback` outside of a binder context. If you need to react to events like death, hit, or item pickup, use `RegisterScriptCallback` — the base game's binders already relay these engine events into the script callback system via `callbacks_gameobject.script`.

```lua
-- Typical usage: inside an object binder
function my_binder:net_spawn(se_abstract)
    object_binder.net_spawn(self, se_abstract)
    self.object:set_callback(callback.hit, self.hit_callback, self)
    return true
end

function my_binder:hit_callback(obj, amount, direction, who, bone_id)
    -- handle hit on this specific object
end

function my_binder:net_destroy()
    self.object:set_callback(callback.hit, nil)  -- clear
    object_binder.net_destroy(self)
end
```

The `callback.*` enum values are defined in the engine. Some are vanilla, some were added by the modded exes:

| Callback type | Vanilla | Description |
|--------------|---------|-------------|
| `callback.trade_start` | Yes | Trade session opened |
| `callback.trade_stop` | Yes | Trade session closed |
| `callback.trade_sell_buy_item` | Yes | Item bought/sold |
| `callback.zone_enter` | Yes | Object entered a zone |
| `callback.zone_exit` | Yes | Object left a zone |
| `callback.death` | Yes | Entity died |
| `callback.hit` | Yes | Entity took damage |
| `callback.sound` | Yes | Sound event |
| `callback.use_object` | Yes | Object used/interacted |
| `callback.on_item_take` | Yes | Item picked up |
| `callback.on_item_drop` | Yes | Item dropped |
| `callback.patrol_path_in_point` | Yes | NPC reached patrol point |
| `callback.script_animation` | Yes | Script animation completed |
| `callback.helicopter_on_point` | Yes | Heli reached point |
| `callback.helicopter_on_hit` | Yes | Heli took damage |
| `callback.weapon_no_ammo` | Yes | No ammo available |
| `callback.key_press` | **Modded** | Key pressed (actor only) |
| `callback.key_release` | **Modded** | Key released (actor only) |
| `callback.key_hold` | **Modded** | Key held (actor only) |
| `callback.mouse_move` | **Modded** | Mouse moved |
| `callback.mouse_wheel` | **Modded** | Mouse scrolled |
| `callback.item_to_belt` | **Modded** | Item moved to belt |
| `callback.item_to_slot` | **Modded** | Item moved to slot |
| `callback.item_to_ruck` | **Modded** | Item moved to backpack |
| `callback.weapon_zoom_in` | **Modded** | Weapon aimed down sights |
| `callback.weapon_zoom_out` | **Modded** | Weapon lowered from aim |
| `callback.weapon_jammed` | **Modded** | Weapon jammed |
| `callback.weapon_fired` | **Modded** | Weapon fired |
| `callback.weapon_magazine_empty` | **Modded** | Magazine emptied |
| `callback.actor_before_death` | **Modded** | Before actor death (can be intercepted) |
| `callback.on_foot_step` | **Modded** | Footstep sound |
| `callback.weapon_lowered` | **Modded** | Weapon lowered stance |
| `callback.weapon_raised` | **Modded** | Weapon raised stance |
| `callback.hud_animation_end` | **Modded** | HUD animation completed |

For mod work, use `RegisterScriptCallback`. The only reason to use `set_callback` directly is if you're writing a custom object binder and need to handle engine events on that specific object — and even then, most events you'd care about already have corresponding script callbacks that the base game binders relay for you.

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
