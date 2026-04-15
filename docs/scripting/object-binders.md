# Object Binders

An object binder is a Lua class that attaches to a specific `game_object` and receives lifecycle callbacks for that object alone — spawn, destroy, update, save, load. Where global callbacks let you react to events across all objects of a type, a binder lets you maintain **per-object state** with clean lifecycle boundaries.

The base game uses binders for the actor (`bind_stalker.script`), all NPCs and monsters (`bind_monster.script`), crows, helicopters, and more.

---

## When to use a binder vs a global callback

| | Object Binder | Global Callback |
|---|---|---|
| State | Per-object (binder instance owns it) | Shared/centralised |
| Lifecycle | Hooks into spawn/destroy/update per object | Hooks into engine-wide events |
| Use for | Per-NPC timers, AI extensions, custom save data | Watching all objects of a type, cross-object logic |
| Overhead | Created per online object | One handler regardless of object count |

For most mods, global callbacks are sufficient. Reach for a binder when you need state that lives and dies with a specific object.

---

## Class declaration

Binders inherit from `object_binder`, a C++ base class provided by the engine:

```lua
class "my_binder" (object_binder)

function my_binder:__init(obj) super(obj)
    -- obj is the game_object this binder is attached to
    -- self.object is available from here onward
    self.my_timer = 0
end
```

`super(obj)` must be called to initialise the base class. `self.object` is set by the base class constructor and is available in every lifecycle method.

---

## Lifecycle methods

The engine calls these methods in order as an object moves through its lifecycle.

### `__init(obj)` — construction

Called once when the binder instance is created. `self.object` is already set by `super(obj)`. Use this for one-time variable initialisation.

```lua
function my_binder:__init(obj) super(obj)
    self.state = "idle"
    self.timer = 0
end
```

---

### `reinit()` — re-initialisation

Called after `__init` and also after level reloads. This is where you set up `db.storage`, register object-specific callbacks, and attach engine callbacks.

```lua
function my_binder:reinit()
    object_binder.reinit(self)                  -- always call this first
    db.storage[self.object:id()] = {}
    self.st = db.storage[self.object:id()]

    self.object:set_callback(callback.hit,   self.on_hit,   self)
    self.object:set_callback(callback.death, self.on_death, self)
end
```

---

### `net_spawn(se_abstract)` — object comes online

Called when the object transitions from offline (alife simulation) to online (loaded near the player). This is the right place to add the object to databases and finish AI setup.

**Must return `true` on success.** Returning `false` rejects the spawn.

```lua
function my_binder:net_spawn(se_abstract)
    if not object_binder.net_spawn(self, se_abstract) then
        return false
    end
    db.add_obj(self.object)
    -- object is fully online and db.storage entry exists
    return true
end
```

---

### `update(delta)` — per-frame

Called every frame while the object is online. `delta` is the elapsed time in milliseconds since the last call. Keep this fast — it runs every frame for every online object with a binder.

```lua
function my_binder:update(delta)
    object_binder.update(self, delta)   -- always call this first

    if not self.object:alive() then return end

    self.timer = self.timer + delta
    if self.timer > 5000 then           -- every 5 seconds
        self.timer = 0
        -- do something periodic
    end
end
```

---

### `net_destroy()` — object goes offline

Called when the object leaves the online zone or is permanently removed. Clean up callbacks and db.storage here. Call `object_binder.net_destroy(self)` **last** — after this call `self.object` is no longer valid.

```lua
function my_binder:net_destroy()
    self.object:set_callback(callback.hit,   nil)
    self.object:set_callback(callback.death, nil)

    db.del_obj(self.object)

    object_binder.net_destroy(self)     -- must be last
end
```

---

### `net_save_relevant()` — should this object be saved?

Return `true` to include this object's state in the save file. Return `false` for transient objects whose state doesn't need to survive a reload. Most binders return `true`.

```lua
function my_binder:net_save_relevant()
    return true
end
```

---

### `save_state(m_data)` and `load_state()` — saving and restoring state

Modern Anomaly uses marshal serialisation (`USE_MARSHAL = true`). Override these to persist your binder's data across saves.

```lua
function my_binder:save_state(m_data)
    local state = alife_storage_manager.get_game_object_state(self.object, true)
    state.my_mod = {
        timer = self.timer,
        custom_flag = self.st.custom_flag,
    }
end

function my_binder:load_state()
    local state = alife_storage_manager.get_game_object_state(self.object)
    if not (state and state.my_mod) then return end

    self.timer = state.my_mod.timer or 0
    self.st.custom_flag = state.my_mod.custom_flag
end
```

!!! note "save/load vs save_state/load_state"
    The `save(packet)` / `load(reader)` methods use legacy binary packet serialisation and are called when `USE_MARSHAL = false`. Anomaly 1.5.2 uses the marshal path (`USE_MARSHAL = true`), so `save_state` / `load_state` are what you override in practice. You only need `save` / `load` for compatibility with older code paths.

---

## Object-specific engine callbacks

Inside `reinit()` you can attach callbacks to `self.object` using `set_callback`. These fire on that object only, unlike the global `RegisterScriptCallback` which fires for all objects:

```lua
-- Available callback types (from the callback.* enum)
self.object:set_callback(callback.hit,                    self.on_hit,    self)
self.object:set_callback(callback.death,                  self.on_death,  self)
self.object:set_callback(callback.patrol_path_in_point,   self.on_waypoint, self)
self.object:set_callback(callback.sound,                  self.on_sound,  self)
self.object:set_callback(callback.use_object,             self.on_use,    self)

-- Clear a callback in net_destroy
self.object:set_callback(callback.hit, nil)
```

The third argument (`self`) is passed as the first argument to the handler, making them proper methods.

---

## Complete example — tracking an NPC that's been talked to

```lua
-- my_mod_binder.script

class "my_npc_binder" (object_binder)

function my_npc_binder:__init(obj) super(obj)
    self.greeted = false
end

function my_npc_binder:reinit()
    object_binder.reinit(self)
    db.storage[self.object:id()] = {}
    self.st = db.storage[self.object:id()]
end

function my_npc_binder:net_spawn(se_abstract)
    if not object_binder.net_spawn(self, se_abstract) then return false end
    db.add_obj(self.object)
    return true
end

function my_npc_binder:net_destroy()
    db.del_obj(self.object)
    object_binder.net_destroy(self)
end

function my_npc_binder:net_save_relevant()
    return true
end

function my_npc_binder:save_state(m_data)
    local state = alife_storage_manager.get_game_object_state(self.object, true)
    state.my_npc_binder = { greeted = self.greeted }
end

function my_npc_binder:load_state()
    local state = alife_storage_manager.get_game_object_state(self.object)
    if state and state.my_npc_binder then
        self.greeted = state.my_npc_binder.greeted or false
    end
end

function my_npc_binder:update(delta)
    object_binder.update(self, delta)
end

-- Attach the binder to all stalker NPCs
function bind(obj)
    obj:bind_object(my_npc_binder(obj))
end
```

!!! warning "Replacing vs extending base binders"
    Defining a `bind()` function replaces the existing binder for that object type. The base game's `bind_monster.script` already registers a binder for all stalkers. If you replace it your NPC AI will break. In practice, mods extend behaviour through [global callbacks](callbacks.md) rather than replacing base binders. Writing a custom binder is most useful for entirely new entity types you've added.

---

## How binders are registered with the engine

The engine associates binder classes with entity types in `class_registrator.script`:

```lua
cs_register(object_factory, "CAI_Stalker", "se_stalker.se_stalker", "AI_STL_S", "script_stalker")
cs_register(object_factory, "CActor",      "se_actor.se_actor",     "S_ACTOR",  "script_actor")
```

When an entity of a given type comes online, the engine calls the `bind(obj)` function in the script registered for that class. That function creates the binder and attaches it:

```lua
-- bind_monster.script
function bind(obj)
    obj:bind_object(generic_object_binder(obj))
end
```

You won't need to modify `class_registrator.script` unless you're creating a completely new entity type.

---

## See also

- [What is a game_object?](game-object.md) — `self.object` explained
- [What is db.storage?](db-storage.md) — the storage table binders populate
- [The Callback System](callbacks.md) — global callbacks vs per-object binder callbacks
- [Save & Load State](save-load.md) — the global save/load system binders integrate with
